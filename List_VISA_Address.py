import pyvisa
#创建VISA资源管理器
rm = pyvisa.ResourceManager()

#列出所有可用设备的VISA地址
resources = rm.list_resources()

#打印可用设备
print(f"可用的设备地址：{resources}")