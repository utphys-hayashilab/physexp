import pyvisa
import numpy as np
import time
import datetime
import os



_addr = {1:'GPIB0::1::INSTR', 2: 'GPIB0::2::INSTR', 3:'GPIB0::3::INSTR',10:'GPIB0::10::INSTR'}

savepath = os.path.join('RSA/', datetime.datetime.now().strftime('%Y-%m-%d %H%M%S')+'_SHE.txt')


rm = pyvisa.ResourceManager()
visa_list = rm.list_resources()
devices = dict()
for addr in visa_list:
    inst = rm.open_resource(addr)
    devices[addr] = inst
    


#addrで指定
v_source1 = devices[_addr[1]]
v_measure3 = devices[_addr[3]]
lock_in_amp = devices[_addr[10]]

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

v_source1.write(init_cmd_1)
v_measure3.write("TRIG:SOUR BUS")

def measure():
    v_measure3.write("INIT")
    v_measure3.write("*TRG")
    time.sleep(0.1)
    power = v_measure3.query("FETC?")
    
    ret = lock_in_amp.query("FETC?")
    v_lia_x, v_lia_y = ret.split(",")
    
    
    return power , float(v_lia_x), float(v_lia_y)

v_apply = np.linspace(0, 10, 11)

result = []
for B in v_apply:
    v_source1.write("SOV "+str(B))
    time.sleep(1)
    p, vx, vy= measure()
    
    result.append([p, vx, vy])
    
    
np.savetxt(savepath,result,delimiter=',')

    
#close
for device in devices.values():
    device.close()
rm.close()