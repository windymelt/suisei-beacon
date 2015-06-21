from __future__ import print_function
import socket
import thread
import smbus
import subprocess
import time
import csv
import atexit
import sys
from gyro import GYRO
from baro import BARO
from contextlib import closing

ADDR_MAGN = 0x1e
ADDR_ACCL = 0x18

CHANNEL = 1 # I2C bus channel no.


argvs = sys.argv
argc = len(argvs)

if argc == 0 or (argc == 1 and argvs[0] == 'beacon.py'):
  print('csv: quiet mode')
  output_file_name = '/dev/null'
else:
  print('csv: output is ' + argvs[0])
  output_file_name = argvs[0]

f = open(output_file_name, 'ab') # If the file doesn't exist, create it
csvWriter = csv.writer(f)

def conn_handler(clientsock, addr, gyro, baro):
  while True:
    msg = clientsock.recv(1)
    if not msg:
      break
    print(msg)
    if msg == '\n':
      msgx = gyro.readXAxisValue()
      msgy = gyro.readYAxisValue()
      msgz = gyro.readZAxisValue()
      msgbaro = baro.getPressure()
      msgtemp = baro.getTemperature()

      csvWriter.writerow([time.time(), msgx, msgy, msgz, msgbaro, msgtemp])

      if msgx != None:
        clientsock.send(str(msgx / 2000.0))
        clientsock.send('*')
        clientsock.send(str(msgy / 2000.0))
        clientsock.send('*')
        clientsock.send(str(msgz / 2000.0))
        clientsock.send('*')
        clientsock.send(str(msgbaro / 100.0))
        clientsock.send('*')
        clientsock.send(str(msgtemp / 10.0))
        clientsock.send('\n')
        #time.sleep(0.1)

def main():
  print('- Beacon -')
  atexit.register(at_exit)
  host = '127.0.0.1'
  port = 10001
  backlog = 10
  bufsize = 4096

  gyro = GYRO(CHANNEL)
  gyro.startMeasuring()
  print('GYRO measuring started')

  baro = BARO(CHANNEL)

  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  sock.bind((host, port))
  sock.listen(backlog)

  while True:
    conn, addr = sock.accept()
    print('Connected by ' , addr)
    thread.start_new_thread(conn_handler, (conn, addr, gyro, baro))
  conn.close()

def at_exit():
  f.close()

if __name__ == '__main__':
  main()
