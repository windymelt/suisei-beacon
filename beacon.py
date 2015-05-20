from __future__ import print_function
import socket
import thread
import smbus
import subprocess
import time
from contextlib import closing

ADDR_BARO = 0x77
ADDR_MAGN = 0x1e
ADDR_ACCL = 0x18
ADDR_GYRO = 0x6b

CHANNEL = 1 # I2C bus channel no.

class GYRO:
  def __init__(self, addr, chnl):
    print('GYRO ADDR: ' + hex(addr) + ' CHNL: ' + hex(chnl))
    self.address = addr
    self.channel = chnl

  def startMeasuring(self):
    try:
      print('GYRO measuring beginning')
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
      return data

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
      return data

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
      return data

    except Exception as e:
      print('Error: ' + str(e))

def conn_handler(clientsock, addr):
  gyro = GYRO(ADDR_GYRO, CHANNEL)
  gyro.startMeasuring()
  print('GYRO measuring started')

  while True:
    msg = clientsock.recv(1)
    if not msg:
      break
    print(msg)
    if msg == '\n':
      msgx = gyro.readXAxisValue()
      msgy = gyro.readYAxisValue()
      msgz = gyro.readZAxisValue()

      if msgx != None:
        clientsock.send(str(msgx / 2000.0))
        clientsock.send('*')
        clientsock.send(str(msgy / 2000.0))
        clientsock.send('*')
        clientsock.send(str(msgz / 2000.0))
        clientsock.send('\n')
        #time.sleep(0.1)

def main():
  print('- Beacon -')
  host = '127.0.0.1'
  port = 10001
  backlog = 10
  bufsize = 4096

  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  sock.bind((host, port))
  sock.listen(backlog)

  while True:
    conn, addr = sock.accept()
    print('Connected by ' , addr)
    thread.start_new_thread(conn_handler, (conn, addr))
  conn.close()

if __name__ == '__main__':
  main()
