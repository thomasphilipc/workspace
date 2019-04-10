#!/usr/bin/python
import minimalmodbus
import pyserial
import sys
sys.path.insert(0, u'/…/…/…/python2.7/site-packages')
import serial.tools.list_ports




def connect_device():
  comlist = serial.tools.list_ports.comports()
  connected = []
  for element in comlist:
      connected.append(element.device)
  print("Connected COM ports: " + str(connected))

def read_meter():
  # establish connection by passing the port and the slave id
  sdm630 = minimalmodbus.Instrument("COM7", 5)
  sdm630.serial.baudrate = 9600

  sdm630.read_Re
  print("First Two regissters are")
  print(sdm630.read_registers(0x0000, 2, 4))
  print("First Register - ")
  print(sdm630.read_register(0x0000, 0, 4, False))
  print("First register in Hex")
  print(hex(sdm630.read_register(0x0000, 0, 4, False)))
  print("Second Register - ")
  print(sdm630.read_register(0x0001, 0, 4, False))
  print("Second Register in Hex")
  print(hex(sdm630.read_register(0x0001, 0, 4, False)))
  print("Voltage Value on Line 1")
  print(sdm630.read_float(0x0000, 4, 2))
  print(sdm630.read_float(0x0002, 4, 2))
  print(sdm630.read_float(0x0004, 4, 2))
  print(sdm630.read_float(0x0006, 4, 2))
  print(sdm630.read_float(0x0008, 4, 2))
  print(sdm630.read_float(0x000A, 4, 2))
  print(sdm630.read_float(0x000C, 4, 2))
  print(sdm630.read_float(0x000E, 4, 2))
  print(sdm630.read_float(0x0010, 4, 2))
  print(sdm630.read_float(0x0012, 4, 2))
  print(sdm630.read_float(0x0014, 4, 2))
  print(sdm630.read_float(0x0016, 4, 2))
  print(sdm630.read_float(0x002E, 4, 2))



def read_socomec():
  # establish connection by passing the port and the slave id
  dirisa40 = minimalmodbus.Instrument("COM7", 5)
  dirisa40.serial.baudrate = 9600


  print("First Two regissters are")
  print(dirisa40.read_registers(0x0000, 2, 4))
  print("First Register - ")
  print(dirisa40.read_register(0x0000, 0, 4, False))
  print("First register in Hex")
  print(hex(dirisa40.read_register(0x0000, 0, 4, False)))
  print("Second Register - ")
  print(dirisa40.read_register(0x0001, 0, 4, False))
  print("Second Register in Hex")
  print(hex(dirisa40.read_register(0x0001, 0, 4, False)))
  print("Voltage Value on Line 1")
  print(dirisa40.read_float(0x0000, 4, 2))


def main():
  try:
    connect_device()
    read_socomec()
  except ValueError:
    print("Retry")
  except IOError:
    print("No device connected")

if __name__ == "__main__":
  main()
