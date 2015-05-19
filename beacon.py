from __future__ import print_function
import socket
import smbus
import time
from contextlib import closing

ADDR_BARO = 0x77
ADDR_MAGN = 0x1e
ADDR_ACCR = 0x18
ADDR_GYRO = 0x6b

CHANNEL = 1 # I2C bus channel no.

class BARO:
  def __init(addr, chnl):
    self.address = addr
    self.channel = chnl

    def startmeasuring(self, resolution):
      # temp: 0x2e, pressure1: 0x34, pressure2: 0x74, pressure3: 0xb4, pressure4: 0xf4
      try:
        smbus.SMBus(self.channel).write_i2c_block_data(self.address, 0xf4, [resolution])
    def readPressureValue(self):
      try:
        data = smbus.SMBus(self.channel).read_i2c_block_data(self.address, 0xf7)


def main():
  baro = BARO(ADDR_BARO, CHANNEL)
  baro.startmeasuring(0x74)

  host = '127.0.0.1'
  port = 1001
  backlog = 10
  bufsize = 4096

  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  with closing(sock):
    sock.bind((host, port))
    sock.listen(backlog)
    while True:
      conn, address = sock.accept()
      with closing(conn):
#       msg = conn.recv(bufsize)
#       print(msg)
        msg = baro.readPressureValue()
        conn.send(msg)
        baro.startMeasuring(0x74)
        time.sleep(1)
  return

if __name__ == '__main__':
  main()
