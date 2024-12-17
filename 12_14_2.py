"""
 2024年 12月 14日 子任务二：控制DPO发送及接收指令
 通过python输出”*idn?”
 得到DPO正确返回的指令

"""
import pyvisa
rm = pyvisa.ResourceManager()
DPO_address = ''
device = rm.open_resource(DPO_address)
response = device.query("*IDN?")
print(f"DPO设备信息：{response}")
device.close()
