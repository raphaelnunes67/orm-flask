from pymodbus.client.sync import ModbusTcpClient as ModbusClient

client = ModbusClient('192.168.0.22', port=502)
client.connect()

rr = client.read_holding_registers(0, 4)
d = rr.registers[3]**2
client.write_registers(4,d)
print (rr.registers)

client.close()