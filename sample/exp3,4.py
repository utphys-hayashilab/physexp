import pyvisa
import numpy as np
import time
import datetime
import os

savepath = os.path.join('RSA/', datetime.datetime.now().strftime('%Y-%m-%d %H%M%S')+'_FMR.txt')


_addr = {1:'GPIB0::1::INSTR', 2: 'GPIB0::2::INSTR', 3:'GPIB0::3::INSTR'}

rm = pyvisa.ResourceManager()
visa_list = rm.list_resources()
devices = dict()
for addr in visa_list:
    inst = rm.open_resource(addr)
    devices[addr] = inst
    


#addrで指定
v_source1 = devices[_addr[1]]
v_measure3 = devices[_addr[3]]

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
v_measure3.write("TRIG:SOUR BUS")   #34401Aの初期設定

def measure():
    #initialize 34401A
    v_measure3.write("INIT")
    v_measure3.write("*TRG")
    time.sleep(0.1)
    r = v_measure3.query("FETC?") #信号読み出し
    r=r.strip()
    # v_measure3.write("FETC?")
    # time.sleep(0.1)
    # r = v_measure3.read()
    return float(r)

v_tune = np.linspace(0, 7, 8)


result = []
for v in v_tune:
    v_source1.write("SOV "+str(v))
    time.sleep(1)
    r= measure()
    print([v,r])
    result.append([v,r])
    
np.savetxt(savepath,result,delimiter=',')

    
#close
for device in devices.values():
    device.close()
rm.close()