"""
    2024年 12 月 28 日 子任务一：读取DPO信号参数及波形数据
    通过python控制示波器DPO得到波形参数及波形数据
"""
""":WAVeform 命令子系统用于读取波形数据及其相关设置。波形记录实际上包含在两个部分中：波形
    参数和波形数据，上位机必须使用两个单独的命令:WAVeform:PREamble 和:WAVeform:DATA 从示波
    器读取。波形数据是针对指定源中的每个点读取的实际数据。波形参数包含用于解释波形数据的信息，
    该信息包括所读取点的数量、所读取的数据的格式和所读取数据的类型。波形参数还包含档位、偏移等
    信息，因此字和字节数据可以转换为时间值和电压值。
"""

import pyvisa
def main_desc(recv):
    param_addr_type = {
        "data_bytes": [0x3c, "i"],
        "point_num": [0x74, 'i'],
        "fp": [0x84, 'i'],
        "sp": [0x88, 'i'],
        "vdiv": [0x9c, 'f'],
        "offset": [0xa0, 'f'],
        "code": [0xa4, 'f'],
        "adc_bit": [0xac, 'h'],
        "interval": [0xb0, 'f'],
        "delay": [0xb4, 'd'],
        "tdiv": [0x144, 'h'],
        "probe": [0x148, 'f'],
    }
    data_byte = {"i": 4, "f": 4, "h": 2, "d": 8}
    param_val = {}
    for key, addr_type in param_addr_type.items():
        addr_start = addr_type[0]
        format = addr_type[1]
        bytes = recv[addr_start:addr_start + data_byte[format]]
        param_val[key] = struct.unpack(format, bytes)[0]

    param_val["tdiv"] = tdiv_enum[param_val["tdiv"]]
    param_val["vdiv"] = param_val["vdiv"] * param_val["probe"]
    param_val["offset"] = param_val["offset"] * param_val["probe"]
    return param_val

def DPO_READ_WAVE(Address, Channel):
    rm = pyvisa.ResourceManager()
    DPO_address = Address
    Device = rm.open_resource(DPO_address)
    Device.timeout = 2000
    Device.chunk_size = 20 * 1024 * 1024
    Device.write(":WAVeform:STARt 0")
    Device.write(f"WAV:SOUR {Channel}")
    DE
