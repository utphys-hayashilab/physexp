import pyvisa
import numpy as np
import sys
sys.path.append("../")
import rsa306b_spec
import time
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit


#Fittingに使うガウシアンを定義
def gaussian(x, a=1, mu=0, sigma=1):
    return a * np.exp(-(x - mu)**2 / (2*sigma**2))

#GPIBによって通信するデバイスのアドレス一覧
_addr = {1:'GPIB0::1::INSTR', 2: 'GPIB0::2::INSTR', 3:'GPIB0::3::INSTR'}

#GPIB通信の初期化
rm = pyvisa.ResourceManager()   #通信用のクラスのインスタンス作成
v_source1 = rm.open_resource('GPIB0::1::INSTR')  #GPIB0::1::INSTRで指定される6240B

def measure():
    freq, trace , peakPower , peakFreq = rsa306b_spec.getPeakSpectrum(startFreq= 4800e6, endFreq = 6000e6) #startからendまでの周波数範囲でスペクトルを取得
    trace = np.power(10, trace/10)  #dBmからmWに単位変換
    Pp = np.power(10,peakPower/10)  #dBmからmWに単位変換
    p0 = [Pp, peakFreq,1 ]          #Fittingの初期値を設定 param=[a, mu, sigma]
    # rsa306b_spec.plot(freq, trace)  #スペクトルを描画(optional)
    
    param, cov = curve_fit(gaussian, freq, trace, p0=p0)    #gaussianでfitting    param=[a, mu, sigma]
    
    return param[0], param[1]
    



#6240Aを初期設定するコマンド
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
    v_source1.write("SOV "+str(v))  #v(単位 V)印加
    time.sleep(0.05)                #0.05秒待つ
    r, f = measure()                #measure()を呼び出し、 ピークの高さ、周波数を返す
    
    result.append([v,r,f])
    print([v,r,f])
    
savepath = "v_cc.txt"
np.savetxt(savepath,result,delimiter=',')   #savepathにresultを区切り文字","で保存

    
#close
v_source1.write("SOV 0")            #6240Aの出力を0Vに
v_source1.write("H")                #6240Aの出力をOFFに
v_source1.close()                  #切断処理
rm.close()                          #PyVisa停止処理
rsa306b_spec.end()                  #スペアナも停止、切断
