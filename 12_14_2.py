"""
 2024年 12月 14日 子任务二：控制DPO发送及接收指令
 通过python输出”*idn?”
 得到DPO正确返回的指令

"""
import pyvisa
rm = pyvisa.ResourceManager()
DPO_address = 'USB0::0xF4EC::0x1013::SDS62DDX800034::INSTR'
device = rm.open_resource(DPO_address)
response = device.query("*IDN?")
print(f"\nDPO设备信息：{response}")
device.close()
