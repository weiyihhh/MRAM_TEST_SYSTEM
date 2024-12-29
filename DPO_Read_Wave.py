import pyvisa
import pylab as pl
import struct
import math
import gc

DPO_Addr = 'USB0::0xF4EC::0x1013::SDS62DDX800034::INSTR'
CHANNEL = 'C1'
HORI_NUM = 10
"""HORI_NUM 的值为 10，这意味着屏幕上水平轴的单位数被分成了 10 个分度。在代码中，HORI_NUM 主要用于计算 时间轴 上的每个数据点对应的时间值。
结合 tdiv（时间基准，单位通常是 sec/div）、interval（采样间隔）和 delay（延迟），HORI_NUM 帮助确定每个波形点的时间位置。
"""
#指定时间轴缩放比例
tdiv_enum = [200e-12,500e-12, 1e-9,\
 2e-9, 5e-9, 10e-9, 20e-9, 50e-9, 100e-9, 200e-9, 500e-9, \
 1e-6, 2e-6, 5e-6, 10e-6, 20e-6, 50e-6, 100e-6, 200e-6, 500e-6, \
 1e-3, 2e-3, 5e-3, 10e-3, 20e-3, 50e-3, 100e-3, 200e-3, 500e-3, \
 1, 2, 5, 10, 20, 50, 100, 200, 500, 1000]


#DPO波形数据处理
def main_desc(recv):       #recv；从示波器获取的原始字节数据
    param_addr_type = {    #包含了示波器数据块中每个参数的偏移地址和数据类型。
        "data_bytes": [0x3c, "i"],
        "point_num": [0x74, 'i'],
        "fp": [0x84, 'i'],
        "sp": [0x88, 'i'],
        "vdiv": [0x9c, 'f'],
        "offset": [0xa0, 'f'],
        "code": [0xa4, 'f'],
        'adc_bit': [0xac, 'h'],
        "interval": [0xb0, 'f'],
        "delay": [0xb4, 'd'],
        "tdiv": [0x144, 'h'],
        "probe": [0x148, 'f']
    }
    data_byte = {"i": 4, "f": 4, "h": 2, "d": 8}
    param_val = {}               #存储从 recv 中提取的各种参数值。
    for key, addr_type in param_addr_type.items():
        addr_start = addr_type[0]  #地址
        format = addr_type[1]      #数据格式
        bytes = recv[addr_start:addr_start + data_byte[format]] #列表的切片遍历
        param_val[key] = struct.unpack(format, bytes)[0]  #将解码后的值存储到字典 param_val 中
        """#这一行代码的作用是将从 recv 中提取出来的字节数据解码为相应的数据类型，并将解码后的结果存入字典 param_val 中。是元组
        [0]的作用是从unpack返回的元组中获取解码后的实际值（比如整数、浮点数等），而不是将其作为一个元组保留下来。"""
    param_val["tdiv"] = tdiv_enum[param_val["tdiv"]]
    param_val["vdiv"] = param_val["vdiv"] * param_val["probe"] #示波器的电压尺度会受到探头倍率的影响
    param_val["offset"] = param_val["offset"] * param_val["probe"] #offset（电压偏移）也乘以 probe（探头倍数），得到实际的偏移值。
    return param_val

def main_wf_data():
    rm = pyvisa.ResourceManager()
    DPO = rm.open_resource(DPO_Addr)
    DPO.timeout = 5000    #设置连接超时时间
    DPO.chunk_size = 20 * 1024 * 1024      #设置数据块大小
    DPO.write(":WAVeform:STARt 0")    #设置或查询波形数据的起始点。
    DPO.write(f"WAV:SOUR {CHANNEL}")  #设置或查询传输波形数据的源。
    DPO.write("WAV:PREamble?")  #获取波形参数
    recv_all = DPO.read_raw()
    recv = recv_all[recv_all.find(b'#') + 11:]#查找字节串中第一次出现字符 # 的位置，第 11 个字节位置开始，到数据的结尾，截取一个子字节串 recv，它包含了有效的波形数据部分。
    print(len(recv))
    param_dic = main_desc(recv)
    print(param_dic)

    # Get the waveform points and confirm the number of waveform slice reads
    points = param_dic["point_num"]
    one_piece_num = float(DPO.query(":WAVeform:MAXPoint?").strip()) #查询每次最大可以读取的波形数据点数。
    read_times = math.ceil(points/one_piece_num) #计算需要读取多少次数据块才能获取完整的波形数据。
    #特别是当波形数据量非常大时，分批次读取数据可以有效避免一次性读取过多数据导致的内存和性能问题。

    # Set the number of read points per slice, if the waveform points is greater than the maximum number of slice reads
    if points > one_piece_num:
        DPO.write(f":WAVeform:POINt {one_piece_num}")
    DPO.write(":WAVeform:WIDTh BYTE")#表示将数据的宽度设置为字节（8 位）
    if param_dic["adc_bit"] > 8:
        DPO.write(":WAVeform:WIDTh WORD") #做确保示波器返回的数据格式符合每个数据点的实际位宽，便于后续正确解析数据。
    #这段代码的目的是确保每次读取的数据不会超过示波器最大支持的读取量。通过调整每次读取的点数，可以避免内存溢出或通信带宽超限。

    # Get the waveform data for each slice
    recv_byte = b''
    for i in range(0, read_times):
        start = i * one_piece_num
        # Set the starting point of each slice
        DPO.write(f":WAVeform:STARt {start}")
        # Get the waveform data of each slice
        DPO.write("WAV:DATA?") #向示波器发送查询命令，要求返回波形数据
        recv_rtn = DPO.read_raw()
        # Splice each waveform data based on data block information
        block_start = recv_rtn.find(b'#')
        data_digit = int(recv_rtn[block_start + 1:block_start + 2])
        data_start = block_start + 2 + data_digit
        data_len = int(recv_rtn[block_start + 2:data_start])
        recv_byte += recv_rtn[data_start:data_start + data_len]

    #解析从示波器或其他设备接收到的波形数据，按照特定格式提取并拼接数据块
    #Unpack signed byte data.
    if param_dic["adc_bit"] > 8:
        convert_data = struct.unpack("%dh"%points, recv_byte)
        convert_data = [float(i) for i in convert_data]
        #如果 points = 1000，则 "%dh"%points 会生成一个字符串 1000h，表示将 recv_byte 解包为 1000 个 2 字节的短整数。
    else:
        convert_data = struct.unpack("%db"%points, recv_byte)
        convert_data = [float(i) for i in convert_data]
    del recv_byte
    gc.collect()
    #通过调用 gc.collect()，我们确保及时回收被删除的变量（如 recv_byte）占用的内存，防止内存泄漏
    '''这段代码的主要目的是对接收到的波形数据进行解包（unpack），并根据 ADC 位数 (adc_bit) 选择适当的数据格式进行解码。
        最后，代码清理不再需要的 recv_byte 变量并调用垃圾回收'''
    #Calculate the voltage value and time value
    time_value = []
    volt_value = []
    for idx in range(0, len(convert_data)):
        volt_value.append(convert_data[idx]/param_dic["code"]*param_dic["vdiv"]- param_dic["offset"])
        time_data = - (param_dic["tdiv"] * HORI_NUM / 2) + idx * param_dic["interval"] + param_dic["delay"]
        time_value.append(time_data)
    print(len(volt_value))
    #Draw Waveform
    pl.figure(figsize=(7, 5))
    pl.plot(time_value, volt_value, markersize=2, label=u"Y-T")
    pl.legend()
    pl.grid()
    pl.show()
    print("Time values:", time_value[:10])  # 打印前10个时间点
    print("Voltage values:", volt_value[:10])  # 打印前10个电压值

    # 如果数据量比较大，可以检查最大和最小值
    print(f"Min time: {min(time_value)}, Max time: {max(time_value)}")
    print(f"Min voltage: {min(volt_value)}, Max voltage: {max(volt_value)}")


if __name__ == '__main__':
 main_wf_data()

