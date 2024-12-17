"""
 2024年 12月 14日 子任务一：控制AWG发送及接收指令
"""
#PyVISA ： 是一个 Python 库，它通过 VISA (Virtual Instrument Software Architecture) 协议与仪器设备进行通信
"""PyVISA 并不是 SCPI 命令的生成器或解释器，而是用来与硬件设备
   （例如仪器）进行通信的工具。SCPI 命令本身是由仪器厂商定义的命令语言，
   PyVISA 通过 VISA 接口（例如 USB、GPIB、VXI、TCP/IP 等）
    将这些 SCPI 命令发送到设备，并可以接收设备的响应。"""

#任务：通过python输出”*idn?”得到AWG正确返回的指令
import pyvisa
rm = pyvisa.ResourceManager()
AWG_address = ''
#打开与AWG的连接，并发送SCPI命令
device = rm.open_resource(AWG_address)
response = device.query("*IDN?")
print(f"AWG设备信息：{response}")
device.close()

