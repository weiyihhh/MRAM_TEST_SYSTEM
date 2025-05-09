import pyvisa

# 创建资源管理器
rm = pyvisa.ResourceManager()

# 连接到示波器（使用设备的地址）
DPO_address = 'USB0::0xF4EC::0x1013::SDS62DDX800034::INSTR'
device = rm.open_resource(DPO_address)

# 发送命令获取波形预置信息
device.write("WAV:PREamble?")

# 使用 read_raw() 获取原始字节数据（不进行任何解码）
recv_all = device.read_raw()
recv = recv_all[recv_all.find(b'#') + 11:]

# 打印返回的原始字节数据
print(f"原始字节数据：{recv}")


