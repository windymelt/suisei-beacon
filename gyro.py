# coding: utf-8
import smbus
import subprocess

class GYRO:
  def __init__(self, chnl):
    self.address = 0x6b
    self.channel = chnl
    print('GYRO ADDR: ' + hex(self.address) + ' CHNL: ' + hex(self.channel))

  def startMeasuring(self):
    try:
      print('GYRO measuring beginning')
      # degree per sec.
      smbus.SMBus(self.channel).write_byte_data(self.address, 0x20, 0x7f) # 0x7f = 01111111b: 800 Hz ODR, 100 Hz cutoff, power on, x on, y on, z on.
      smbus.SMBus(self.channel).write_byte_data(self.address, 0x23, 0x20) # 0x20 : 2000 dps

    except IOError as e:
      print('I/O error:')
      diag = subprocess.call(['i2cdetect', '-y', '1'])
      print(diag)

    except Exception as e:
      print('Error: ' + str(e))

  def readXAxisValue(self):
    try:
      print('GYRO X-axis value reading')
      dataLow = smbus.SMBus(self.channel).read_byte_data(self.address, 0x28)
      dataHigh = smbus.SMBus(self.channel).read_byte_data(self.address, 0x29)
      if dataHigh & 0x80 == 0x80: # If MSB is 1
        data = - ((dataHigh << 8 | dataLow - 1) ^ 0xffff)
      else:
        data = (dataHigh << 8) | dataLow
      return data + 16.9136331192006 # adjustment

    except Exception as e:
      print('Error: ' + str(e))

  def readYAxisValue(self):
    try:
      print('GYRO Y-axis value reading')
      dataLow = smbus.SMBus(self.channel).read_byte_data(self.address, 0x2a)
      dataHigh = smbus.SMBus(self.channel).read_byte_data(self.address, 0x2b)
      if dataHigh & 0x80 == 0x80: # If MSB is 1
        data = - ((dataHigh << 8 | dataLow - 1) ^ 0xffff)
      else:
        data = (dataHigh << 8) | dataLow
      return data + -9.22698072805139 # adjustment

    except Exception as e:
      print('Error: ' + str(e))

  def readZAxisValue(self):
    try:
      print('GYRO Z-axis value reading')
      dataLow = smbus.SMBus(self.channel).read_byte_data(self.address, 0x2c)
      dataHigh = smbus.SMBus(self.channel).read_byte_data(self.address, 0x2d)
      if dataHigh & 0x80 == 0x80: # If MSB is 1
        data = - ((dataHigh << 8 | dataLow - 1) ^ 0xffff)
      else:
        data = (dataHigh << 8) | dataLow
      return data + 11.123483226267 # adjustment

    except Exception as e:
      print('Error: ' + str(e))
