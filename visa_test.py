import pyvisa


rm = pyvisa.ResourceManager()
print(rm)
visa_list = rm.list_resources()
print(visa_list)
usb_1 = visa_list[2]
print(usb_1)
inst_1 = rm.open_resource(usb_1)
print(inst_1)

# inst_1.write('*IDN?')
# out = inst_1.read()

# queryを用いてももちろんOK
out = inst_1.query('*IDN?')

print(out)#(計測器の情報


inst_1.close()
rm.close()