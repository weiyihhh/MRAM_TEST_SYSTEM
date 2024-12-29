import pyvisa
import struct
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
# 提取字节 136 到 139
interval_bytes = recv[136:140]

# 打印提取的字节数据
print(f"interval 字节数据：{interval_bytes}")

# 使用 struct 模块解析为浮动数值 (大端字节序)
interval_value = struct.unpack('>f', interval_bytes)[0]

# 打印解析后的 interval 值
print(f"interval 值：{interval_value}")
