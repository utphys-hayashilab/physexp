import ctypes
from ctypes import *
from pylab import *
import numpy as np
import matplotlib.animation as animation
import time
from matplotlib.widgets import Button
import matplotlib.pyplot as plt
import pprint

rsa300 = ctypes.WinDLL("C:\Tektronix\RSA_API\lib\\x64\RSA_API.dll")

center_freq = 5370e6
ref_level=0.0


intArray = c_int * 10
searchIDs = intArray()
deviceserial = c_wchar_p()
numFound = c_int()
iqSampleRate = c_double(0)

ret = rsa300.Search(searchIDs, byref(deviceserial), byref(numFound))

if ret != 0:
	print ("Run error: " + str(ret))
else:
	rsa300.Connect(searchIDs[0])
	
aLen = 1280
length = c_int(aLen)
rsa300.SetIQRecordLength(length)

cf = c_double(center_freq)
rsa300.SetCenterFreq(cf)

rl = c_double(ref_level)
rsa300.SetReferenceLevel(rl)

iqLen = aLen * 2
floatArray = c_float * iqLen

#triggerMode = c_int(True)
#rsa300.SetTriggerMode(triggerMode)
trigPos = c_double(25.0)
rsa300.SetTriggerPositionPercent(trigPos)

rsa300.GetIQSampleRate(byref(iqSampleRate))
print('Sample rate: ' + str(iqSampleRate.value) + 'Samples/sec')


iqBW = c_double(80e6)
rsa300.SetIQBandwidth(iqBW)

rsa300.GetIQSampleRate(byref(iqSampleRate))

print('Bandwidth: ' + str(iqBW.value) + 'Hz')
print('Sample rate: ' + str(iqSampleRate.value) + 'Samples/sec')


def getIQData():
	ready = c_bool(False)
	
	ret = rsa300.Run()
	if ret != 0:
			print( "Run error: " + str(ret))
	ret = rsa300.WaitForIQDataReady(10000, byref(ready))
	if ret != 0:
		print( "WaitForIQDataReady error: " + str(ret))
	iqData = floatArray()
	startIndex = c_int(0)
	if ready:
		ret = rsa300.GetIQData(iqData, startIndex, length)
		if ret != 0:
			print( "GetIQData error: " + str(ret))
		iData = list(range(0,aLen))
		qData = list(range(0,aLen))
		for i in range(0,aLen):
			iData[i] = iqData[i*2]
			qData[i] = iqData[i*2+1]
	
	z = [(x + 1j*y) for x, y in zip(iData,qData)]
	
	cf = c_double(0)
	rsa300.GetCenterFreq(byref(cf))
	spec2 = mlab.specgram(z, NFFT=aLen, Fs=int(iqSampleRate.value))
	f = [(x + cf)/1e6 for x in spec2[1]]
	# print("spec2[0]")
 
	#close()
 
	spec = np.fft.fft(z, aLen)
	r = [x * 1 for x in abs(spec)]
	r = np.fft.fftshift(r)
	return [iData, qData, z, r, f]

	
def end():
	rsa300.Stop()
	rsa300.Disconnect()

##########################################
_,_,_,r,f = getIQData()
print(f)
plt.plot(f,r)
plt.show()
end()
