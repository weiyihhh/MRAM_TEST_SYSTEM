# -*- coding: utf-8 -*-
import pyvisa

class AWG_Set:
    pass

def AWG_Init(Device_Model):
    if 'SDG6000X' == Device_Model:
        Device_TCPIP_Index = 'USB0::0xF4EC::0x1101::SDG6XBAC3R0014::INSTR'
        Device_USB_Index = 'USB0::0xF4EC::0x1101::SDG6XBAC3R0014::INSTR'
    elif 'SDG7000A' == Device_Model:
        # Device_TCPIP_Index = 'TCPIP0::192.168.1.56::inst0::INSTR'
        Device_TCPIP_Index = 'TCPIP0::192.168.2.134::inst0::INSTR'
        # Device_TCPIP_Index = 'USB0::0xF4EC::0x1102::SDG7ABAQ7R0051::INSTR'
        Device_USB_Index = 'USB0::0xF4EC::0x1102::SDG7ABAQ7R0051::INSTR'

    AWG_Set.Model_SDG7000A = 'SDG7000A'
    AWG_Set.Model_SDG6000X = 'SDG6000X'
    AWG_Set.CH = ('C1', 'C2')
    AWG_Set.Load_R50 = '50'
    AWG_Set.Load_R1M = '1000000'
    try:
        Visa_Device = pyvisa.ResourceManager()
        try:
            AWG = Visa_Device.open_resource(Device_TCPIP_Index)
        except:
            AWG = Visa_Device.open_resource(Device_USB_Index)

        AWG.timeout = 10000  # default value is 2000(2s)
        AWG.chunk_size = 40 * 2048 * 2048  # default value is 20*1024(20k bytes)

        AWG_Set.declare = 'AWG连接成功'
        # print('AWG连接成功')
        return AWG, AWG_Set
    except:
        AWG_Set.declare = 'AWG连接失败'
        # print('AWG连接失败')
        return 0, AWG_Set

