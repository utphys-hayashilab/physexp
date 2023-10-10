import pyvisa
import numpy as np
import time

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
v_measure3 = devices[_addr[3]]  #GPIB0::3::INSTRで指定される6240B

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
v_measure3.write("TRIG:SOUR BUS")   #34401Aの初期設定

def measure():
    v_measure3.write("INIT")        #34401Aを初期化
    v_measure3.write("*TRG")        #測定実行の命令を送る
    time.sleep(0.1)
    r = v_measure3.query("FETC?")   #34401Aの信号読み出し
    r=r.strip()                     #返ってくる文字列に含まれる改行を削除
    return float(r)

v_tune = np.linspace(0, 7, 8)       #掃引する電圧の配列を用意 
#高周波発生装置に入れる時は0~7V
#電磁石を操作する時は0~10V(→電磁石に流れる電流が0~10Aに対応)


result = []
for v in v_tune:
    v_source1.write("SOV "+str(v))  #v(単位 V)印加
    time.sleep(1)                   #1秒待つ
    r= measure()                    #測定実行 返り値34401Aの電圧
    print([v,r])                    
    result.append([v,r])            
    
np.savetxt(savepath,result,delimiter=',')   #savepathにresultを区切り文字","で保存

    
#close
v_source1.write("SOV 0")            #6240Aの出力を0Vに
v_source1.write("H")                #6240Aの出力をOFFに
for device in devices.values():     #全ての接続されたデバイスについて
    device.close()                  #切断処理
rm.close()                          #PyVisa停止処理