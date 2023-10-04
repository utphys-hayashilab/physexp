import pyvisa
import numpy as np
import sys
sys.path.append("../")
from lib import rsa306b_spec
import time
import datetime
import os
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from ctypes import *


#Fittingに使うガウシアンを定義
def gaussian(x, a=1, mu=0, sigma=1):
    return a * np.exp(-(x - mu)**2 / (2*sigma**2))

#保存場所の指定
savepath = os.path.join('RSA/', datetime.datetime.now().strftime('%Y-%m-%d %H%M%S')+'_vtune.txt')

#GPIBによって通信するデバイスのアドレス一覧
_addr = {1:'GPIB0::1::INSTR', 2: 'GPIB0::2::INSTR', 3:'GPIB0::3::INSTR'}

#GPIB通信の初期化
rm = pyvisa.ResourceManager()   #通信用のクラスのインスタンス作成
visa_list = rm.list_resources() #接続されているデバイスのアドレス一覧を取得
devices = dict()
for addr in visa_list:          #取得したアドレス一覧のそれぞれについて
    inst = rm.open_resource(addr)   #指定したアドレスのデバイスを取得
    devices[addr] = inst            #辞書型のdevicesに入れてアドレスで呼び出せるように
    
#addrで指定
v_source1 = devices[_addr[1]]   #GPIB0::1::INSTRで指定される6240B
v_measure3 = devices[_addr[3]]  #GPIB0::3::INSTRで指定される34401A

rl=-10 #スペアナのrefLevelを設定


def measure():
    print("-----measure()-----")
    freq, trace , peakPower , peakFreq = rsa306b_spec.getPeakSpectrum(startFreq= 4800e6, endFreq = 6000e6, refLevel=rl) #startからendまでの周波数範囲でスペクトルを取得
    trace = np.power(10, trace/10)  #dBmからWに単位変換
    Pp = np.power(10,peakPower/10)  #dBmからWに単位変換
    p0 = [Pp, peakFreq,1 ]          #Fittingの初期値を設定 param=[a, mu, sigma]
    print(peakFreq)
    print(Pp)
    # rsa306b_spec.plot(freq, trace)  #スペクトルを描画(optional)
    
    param, cov = curve_fit(gaussian, freq, trace, p0=p0)    #gaussianでfitting    param=[a, mu, sigma]
    # rsa306b_spec.end()
    return param[0], param[1]
    



#初期化
init_cmd_1 = """*RST
MD0
VF
F2
R0
SVR5
SOV 0
E
"""

v_source1.write(init_cmd_1) #6240Aの初期設定
v_tune = np.linspace(0, 7, 11)   #掃引する電圧の配列を用意

result = []

for v in v_tune:
    v_source1.write("SOV "+str(v))  #v (V)印加
    time.sleep(1)                   #一秒待つ
    print("V_tune: "+ str(v))       #
    # measure()
    r, f = measure()                #measure()を呼び出し、 ピークの高さ、周波数を返す
    
    result.append([v,r,f])
    print(r)
    print(f)
    
savepath = "RSA/v_cc.txt"
np.savetxt(savepath,result,delimiter=',')

    
#close
v_source1.write("H")                #6240Aの出力をOFFに
for device in devices.values():     #全ての接続されたデバイスについて
    device.close()                  #切断処理
rm.close()                          
rsa306b_spec.end()                  #スペアナも停止、切断
