# encoding: utf-8

import smbus
import subprocess
import time

class BARO:
  def __init__(self, chnl):
    self.address = 0x77
    self.channel = chnl
    print('BARO ADDR: ' + hex(self.address) + ' CHNL: ' + hex(self.channel))
    self.bus = smbus.SMBus(chnl)
    self.oss = 1

    print('self check..')
    testb5 = self.calcb5(27898, 32757, 23153, -8711, 2868)
    if testb5 != 2399:
      print('self check failed: b5')
      print('b5 should be 2399 but ', testb5)
    if self.calcTrueTemp(2399) != 150:
      print('self check failed: ttemp')
    if self.calcTruePressure(408, -72, -14383, 32741, 23843, 6190, 4, 2399, 0) != 69964:
      print('self check failed: tpressure')

    # Read calibration data from the EEPROM of the module
    # ac1, ac2, ac3, b1, b2, mb, mc, md can be two's complement
    self.ac1 = (self.read_byte_i2c(0xaa) << 8) | self.read_byte_i2c(0xab)
    if self.ac1 & 0x8000:
      self.ac1 = -(self.ac1 - 1 ^ 0xffff)

    self.ac2 = (self.read_byte_i2c(0xac) << 8) | self.read_byte_i2c(0xad)
    if self.ac2 & 0x8000:
      self.ac2 = -(self.ac2 - 1 ^ 0xffff)

    self.ac3 = (self.read_byte_i2c(0xae) << 8) | self.read_byte_i2c(0xaf)
    if self.ac3 & 0x8000:
      self.ac3 = -(self.ac3 - 1 ^ 0xffff)

    self.ac4 = (self.read_byte_i2c(0xb0) << 8) | self.read_byte_i2c(0xb1)
    self.ac5 = (self.read_byte_i2c(0xb2) << 8) | self.read_byte_i2c(0xb3)
    self.ac6 = (self.read_byte_i2c(0xb4) << 8) | self.read_byte_i2c(0xb5)

    self.b1 = (self.read_byte_i2c(0xb6) << 8) | self.read_byte_i2c(0xb7)
    if self.b1 & 0x8000:
      self.b1 = -(self.b1 - 1 ^ 0xffff)

    self.b2 = (self.read_byte_i2c(0xb8) << 8) | self.read_byte_i2c(0xb9)
    if self.b2 & 0x8000:
      self.b2 = -(self.b2 - 1 ^ 0xffff)

    self.mb = (self.read_byte_i2c(0xba) << 8) | self.read_byte_i2c(0xbb)
    if self.mb & 0x8000:
      self.mb = -(self.mb - 1 ^ 0xffff)

    self.mc = (self.read_byte_i2c(0xbc) << 8) | self.read_byte_i2c(0xbd)
    if self.mc & 0x8000:
      self.mc = -(self.mc - 1 ^ 0xffff)

    self.md = (self.read_byte_i2c(0xbe) << 8) | self.read_byte_i2c(0xbf)
    if self.md & 0x8000:
      self.md = -(self.md - 1 ^ 0xffff)

  def read_byte_i2c(self, reg):
    return self.bus.read_byte_data(self.address, reg)

  def calcb5(self, ut, ac5, ac6, mc, md):
    print('b5: ut, ac5, ac6, mc, md  ', ut, ac5, ac6, mc, md)
    t_x1 = (ut - ac6) * ac5 / (2 << 14) # 2 << 14 is equal to pow(2, 15)
    print('b5: t_x1 ', t_x1)
    t_x2 = mc * (2 << 10) / (t_x1 + md) # 2 << 10 is equal to pow(2, 11)
    print('b5: t_x2 ', t_x2)
    b5 = t_x1 + t_x2
    print('b5: b5 ', b5)
    return b5

  def calcTrueTemp(self, b5):
    print('tt: b5 ', b5)
    true_temp = (b5 + 8) / (2 << 3) # 2 << 3 is equal to pow(2, 4)
    print('tt: true_temp ', true_temp)
    return true_temp

  def calcTruePressure(self, ac1, ac2, ac3, ac4, up, b1, b2, b5, oss):
    print('tp: ac1,2,3,4, up, b1,2,5, oss  ', ac1, ac2, ac3, ac4, up, b1, b2, b5, oss)
    b6 = b5 - 4000
    print('tp: b6 ', b6)
    p_x1 = (b2 * (b6 * b6 / (2 << 11))) / (2 << 10)
    print('tp: p_x1 ', p_x1)
    p_x2 = ac2 * b6 / (2 << 10)
    print('tp: p_x2 ', p_x2)
    p_x3 = p_x1 + p_x2
    print('tp: p_x3 ', p_x3)
    b3 = (((ac1 * 4 + p_x3) << oss) + 2) / 4
    print('tp: b3 ', b3)
    p_x1 = ac3 * b6 / (2 << 12)
    print('tp: p_x1 ', p_x1)
    p_x2 = (b1 * (b6 * b6 / (2 << 11))) / (2 << 15)
    print('tp: p_x2 ', p_x2)
    p_x3 = ((p_x1 + p_x2) + 2) / (4)
    print('tp: p_x3 ', p_x3)
    b4 = ac4 * ((p_x3 + 32768) ) / (2 << 14) # convert to unsigned long
    print('tp: b4 ', b4)
    b7 = ((up - b3) * (50000 >> oss))
    print('tp: b7 ', b7)

    if b7 < 0x80000000:
      p = (b7 * 2) / b4
    else:
      p = (b7 / b4) * 2

    print('tp: p ', p)
    p_x1 = (p / 256) * (p / 256)
    print('tp: p_x1 ', p_x1)
    p_x1 = (p_x1 * 3038) / (2 << 15)
    print('tp: p_x1 again ', p_x1)
    p_x2 = (-7357 * p) / (2 << 15)
    print('tp: p_x2 ', p_x2)
    p = p + (p_x1 + p_x2 + 3791) / (2 << 3)
    print('tp: true_pressure ', p)
    true_pressure = p
    return true_pressure

  def getUt(self):
    milli = 0.001
    self.bus.write_byte_data(self.address, 0xf4, 0x2e)
    time.sleep(4.5 * milli)
    temp_msb = self.read_byte_i2c(0xf6)
    temp_lsb = self.read_byte_i2c(0xf7)
    ut = (temp_msb << 8) | temp_lsb
    return ut
      

  def getTemperature(self):
    try:
      print('BARO temperature measuring beginning')
      print('reading temperature')
      ut = self.getUt()
      print('UT ', ut)
      b5 = self.calcb5(ut, self.ac5, self.ac6, self.mc, self.md)
      print('b5', b5)

      print('calculating true temp')
      true_temp = self.calcTrueTemp(b5)
      print('truetemp ', true_temp / 10.0 , ' degree')
      return true_temp

    except IOError as e:
      print('I/O error:')
      diag = subprocess.call(['i2cdetect', '-y', '1'])
      print(diag)

    except Exception as e:
      print('Error: ' + str(e))

  def getPressure(self):
    milli = 0.001
    oss = 3 # 0: ultra low power, 1: standard, 2: high resolution, 3: ultra high resolution c.f. datasheet 
    ossWaitTime = [4.5, 7.5, 13.5, 23.5]
    try:
      print('BARO pressure measuring beginning')
      print('reading pressure')
      self.bus.write_byte_data(self.address, 0xf4, 0x34 + (oss << 6))
      time.sleep(ossWaitTime[oss] * milli)
      msb = self.read_byte_i2c(0xf6)
      print('msb ', hex(msb))
      lsb = self.read_byte_i2c(0xf7)
      print('lsb ', hex(lsb))
      xlsb = self.read_byte_i2c(0xf8)
      print('xlsb ', hex(xlsb))
      print('bitshifted ', ((((msb << 8) | lsb) << 8)  | xlsb) >> (8 - oss))
      up = ((((msb << 8) | lsb) << 8) | xlsb) >> (8 - oss)
      print('UP ' ,up)

      ut = self.getUt()
      b5 = self.calcb5(ut, self.ac5, self.ac6, self.mc, self.md)
      print('b5', b5)
      print('calculating true pressure')
      true_pressure = self.calcTruePressure(self.ac1, self.ac2, self.ac3, self.ac4, up, self.b1, self.b2, b5, oss)
      print('true pressure ', true_pressure)

      return true_pressure

    except IOError as e:
      print('I/O error:')
      diag = subprocess.call(['i2cdetect', '-y', '1'])
      print(diag)

    except Exception as e:
      print('Error: ' + str(e))
