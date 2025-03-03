#!/usr/bin/env python3.6.5
# -*- coding: utf-8 -*-
import pyvisa
import time
import binascii
#USB resource of Device
device_resource = 'USB0::0xF4EC::0x1102::SDG7ABAQ5R0010::INSTR'
#Little endian, 16-bit2's complement
wave_points = [0x0080, 0x0070, 0x0060, 0x0040, 0x0050, 0x0060, 0x0070, 0xff7f,0x0050]
def create_wave_file():
    """create a file"""
    f = open("wave1.bin", "wb")
    for a in wave_points:
        b = hex(a)
        b = b[2:]
        len_b = len(b)
        if (0 == len_b):
            b = '0000'
        elif (1 == len_b):
            b = '000' + b
        elif (2 == len_b):
            b = '00' + b
        elif (3 == len_b):
            b = '0' + b
        c = binascii.a2b_hex(b) #Hexadecimal integer to ASCii encoded string
        f.write(c)
    f.close()
def send_wawe_data(dev):
    """send wave1.bin to the device"""
    f = open("wave1.bin", "rb") #wave1.bin is the waveform to be sent
    data = f.read()
    print ('write bytes:%s'%len(data))
    dev.write("C1:WVDTWVNM,wave1,FREQ,2000.0,AMPL,4.0,OFST,0.0,PHASE,0.0,WAVEDATA,%s" % (data)) #"X"series (SDG1000X/SDG2000X/SDG6000X/X-E)
    dev.write("C1:ARWV NAME,wave1")
    f.close()
def get_wave_data(dev):
    """get wave from the devide"""
    f = open("wave2.bin", "wb") #save the waveform as wave2.bin
    dev.write("WVDT? user,wave1") #"X" series(SDG1000X/SDG2000X/SDG6000X/X-E)
    time.sleep(1)
    data = dev.read()
    data_pos = data.find("WAVEDATA,") + len("WAVEDATA,")
    print (data[0:data_pos])
    wave_data = data[data_pos:]
    print ('read bytes:%s'%len(wave_data))
    f.write(wave_data)
    f.close()
if __name__ == '__main__':
    """"""
    rm=pyvisa.ResourceManager()
    device =rm.open_resource(device_resource, timeout=50000, chunk_size = 24*1024*1024)
    create_wave_file()
    send_wawe_data(device)
    #get_wave_data(device)