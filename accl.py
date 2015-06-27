# coding: utf-8
import smbus
import subprocess

class ACCL:
  def __init__(self, chnl):
    self.address = 0x18
    self.channel = chnl
    print('ACCL ADDR: ' + hex(self.address) + ' CHNL: ' + hex(self.channel))

  def startMeasuring(self):
    try:
      print('ACCL measuring beginning')
      smbus.SMBus(self.channel).write_byte_data(self.address, 0x20, 0x27) # 0b00100111: On normal power, 50Hz ODR, 37 Hz cutoff, x on, y on, z on.

    except IOError as e:
      print('I/O error:')
      diag = subprocess.call(['i2cdetect', '-y', '1'])
      print(diag)

    except Exception as e:
      print('Error: ' + str(e))

  def readAxisValue(self, offset):
    try:
      dataLow = smbus.SMBus(self.channel).read_byte_data(self.address, 0x28 + offset * 2)
      dataHigh = smbus.SMBus(self.channel).read_byte_data(self.address, 0x29 + offset * 2)
      print(dataLow)
      if dataHigh & 0x80 == 0x80: # If MSB is 1
        data = - ((dataHigh << 8 | dataLow - 1) ^ 0xffff)
      else:
        data = (dataHigh << 8) | dataLow
      return data >> 5 # adjustment

    except Exception as e:
      print('Error: ' + str(e))

  def readXAxisValue(self):
    return self.readAxisValue(0)

  def readYAxisValue(self):
    return self.readAxisValue(1)

  def readZAxisValue(self):
    return self.readAxisValue(2)
