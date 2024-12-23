"""
Peak Power Detect using API for RSA306
Windows 7 64-bit
Python 3.5.2 64-bit (Anaconda 4.2.0)
NumPy 1.11.1, MatPlotLib 1.5.3
"""


#周波数幅(span)が40MHz以下しか指定できない（本来の最大値はもっと大きいはずなので原因不明）_getSpectrum
#そのため、ピークを探すために中心周波数を掃引すればよい(getSpectrum)、がエッジにピークが来たとき問題
#ピーク周波数付近で再度走らせてその結果を出力→getPeakSpectrum

from ctypes import *
import numpy as np
import matplotlib.pyplot as plt
from os import chdir
import sys

"""
################################################################
C:\Tektronix\RSA306 API\lib\x64 needs to be added to the
PATH system environment variable
################################################################
"""

rsa = cdll.LoadLibrary("C:\Tektronix\RSA_API\lib\\x64\RSA_API.dll")

#create Spectrum_Settings data structure
class Spectrum_Settings(Structure):
   _fields_ = [('span', c_double), ('rbw', c_double),
   ('enableVBW', c_bool), ('vbw', c_double),
   ('traceLength', c_int), ('window', c_int),
   ('verticalUnit', c_int), ('actualStartFreq', c_double), ('actualStopFreq', c_double),
   ('actualFreqStepSize', c_double), ('actualRBW', c_double),
   ('actualVBW', c_double), ('actualNumIQSamples', c_double)]
   
#initialize variables
specSet = Spectrum_Settings()   #structure to store spectrum settings
longArray = c_long*10           #array to store deviceID
deviceIDs = longArray()         #ID of device
deviceSerial = c_wchar_p('')    #Serial of device
numFound = c_int(0)             #number of connected devices
enable = c_bool(True)         #spectrum enable
ready = c_bool(False)         #ready
timeoutMsec = c_int(1000)      #timeout
trace = c_int(0)              #select Trace 1
detector = c_int(1)           #set detector type to max
span = 40e6                     #max span 
rl = 0                        #reference level(dBm)


#Added to set an external trigger. 
trigMode = c_int(2)             #Set 1 for external trigger 2 for free
trigSource = c_int(0)           #Set the trigger source 0 for external 1 for power
trigTrans = c_int(1)            #Set the transition for the trigger 1 for rising edge 2 for falling edge


#search the USB 3.0 bus for an RSA306
ret = rsa.Search(deviceIDs, byref(deviceSerial), byref(numFound))
if ret != 0:
   print('Error in Search: ' + str(ret))
if numFound.value < 1:
   print('No instruments found.')
   sys.exit()
elif numFound.value == 1:
   print('One device found.')
   print('Device Serial Number: ' + deviceSerial.value)
else:
   print('2 or more instruments found.')
    #note: the API can only currently access one at a time

#connect to the first RSA306
ret = rsa.Connect(deviceIDs[0])
if ret != 0:
   print('Error in Connect: ' + str(ret))
   
   
#function to get spectrum 
#freq range = [centerFreq - span/2 , centerFreq + span/2]
#refLevel 
def _getSpectrum(centerFreq = 5370e6, refLevel = c_double(0)):
    cf = c_double(centerFreq)       #center freq
    refLevel = c_double(refLevel)        #ref level    
    
    #preset the RSA306 and configure spectrum settings
    rsa.Preset()
    rsa.SPECTRUM_SetEnable(enable)              #Change mode to spectrum
    rsa.SPECTRUM_SetDefault()                   #Set settings to default
    rsa.SPECTRUM_GetSettings(byref(specSet))    #get settings from RSA306
    
    #Configure for an external trigger  
    rsa.TRIG_SetTriggerMode(trigMode)           
    rsa.TRIG_SetTriggerTransition(trigTrans)
    rsa.TRIG_SetTriggerSource(trigSource)
    
    
    rsa.SetCenterFreq(cf)                       #Set center freq.
    rsa.SetReferenceLevel(refLevel)             #Set Reference level

    #store spectrum settings
    specSet.span = c_double(span)               #Span of Freq.
    specSet.rbw = c_double(100e3)               #Resolution BandWidth
    specSet.enableVBW =c_bool(True)             #Set VBW mode enable
    specSet.vbw =c_double(100)                  #Video BandWidth
    specSet.traceLength = c_int(10401)            #num of datapoint


    
    freqScaler = specSet.span/2
    specSet.actualStartFreq = c_double(cf.value - freqScaler)           #Start freq.
    specSet.actualFreqStepSize = specSet.span/specSet.traceLength       #Step size of freq  
    ret = rsa.SPECTRUM_SetSettings(specSet)                             #send settings to RSA
    
    #initialize variables for GetTrace
    traceArray = c_float * specSet.traceLength #
    traceData = traceArray()
    outTracePoints = c_int()

    #generate frequency array for plotting the spectrum
    freq = np.arange(specSet.actualStartFreq,
    specSet.actualStartFreq + specSet.actualFreqStepSize*specSet.traceLength,
    specSet.actualFreqStepSize)

    #start acquisition
    rsa.Run()
    while ready.value == False:
        rsa.SPECTRUM_WaitForTraceReady(timeoutMsec, byref(ready))
        # print(ready)
    # print('Trace Data is Ready')
    ready.value = False 

    rsa.SPECTRUM_GetTrace(c_int(0), specSet.traceLength,
    byref(traceData), byref(outTracePoints))
    # print('Got trace data.')
    rsa.Stop()

    #convert trace data from a ctypes array to a numpy array
    trace = np.ctypeslib.as_array(traceData)
    # print(trace)

    #Peak power and frequency calculations
    peakPower = np.amax(trace)
    peakPowerFreq = freq[np.argmax(trace)]
    # print('Peak power in spectrum: %4.3f dBm @ %d Hz' % (peakPower, peakPowerFreq))
    return  freq,trace,  peakPower, peakPowerFreq

def end():
	rsa.Stop()
	rsa.Disconnect()

def plot(freq, trace):
    #plot the spectrum trace (optional)
    plt.plot(freq, trace)
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Amplitude (dBm)')

    #BONUS clean up plot axes
    xmin = np.amin(freq)
    xmax = np.amax(freq)
    plt.xlim(xmin,xmax)
    ymin = np.amin(trace)
    ymax = np.amax(trace)
    dy = ymax - ymin
    ymin -= dy*0.1
    ymax += dy*0.1
    plt.ylim(ymin,ymax)

    plt.show()


# Sweep center freq from startFreq to endFreq
# stack all the trace and freq result in one array
# store each peak data per centerFreq
# return stacked freq, trace array and max peak
def getSpectrum(startFreq, endFreq, refLevel):
    steps = int((endFreq - startFreq)/span) +1
    freq = np.asarray([])
    trace = np.asarray([])
    peakPower = np.asarray([])
    peakFreq = np.asarray([])
    for i in range(steps):
        cf = startFreq + i*span
        if cf > (6.2e9-span/2):
            break
        # print("cf: "+str(cf))
        f, t, Pp,Fp =_getSpectrum(centerFreq=cf, refLevel=refLevel)
        freq = np.append(freq,f)
        trace = np.append(trace,t)
        peakPower = np.append(peakPower,Pp)
        peakFreq = np.append(peakFreq,Fp)
    # print(peakPower)
    # print(peakFreq)
    pmax = np.amax(peakPower)
    pmaxF = peakFreq[np.argmax(peakPower)]
    return freq, trace, pmax, pmaxF


#
def getPeakSpectrum(startFreq, endFreq):
    _,_,_,peakFreq = getSpectrum(startFreq, endFreq, rl)
    f, t, Pp,Fp =_getSpectrum(centerFreq=peakFreq, refLevel=rl)
    return f, t, Pp, Fp
    
    
# f,t, Pp, Fp = getSpectrum(5230e6, 5400e6, 0)
# end()
# plot(f,t)
    


# freq, trace ,*_= _getSpectrum(5370e6, 0)
# end()
# plot(freq, trace)