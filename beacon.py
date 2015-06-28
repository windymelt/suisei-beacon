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
from accl import ACCL
from contextlib import closing
#import numpy as np
#from filterpy.kalman import KalmanFilter

ADDR_MAGN = 0x1e
ADDR_ACCL = 0x18

CHANNEL = 1 # I2C bus channel no.


argvs = sys.argv
argc = len(argvs)

if argc <= 1:
  print('csv: quiet mode')
  output_file_name = '/dev/null'
else:
  print('csv: output is ' + argvs[1])
  output_file_name = argvs[1]

f = open(output_file_name, 'ab') # If the file doesn't exist, create it
csvWriter = csv.writer(f)

#kf = KalmanFilter(dim_x=3, dim_z=3)
#kf.x = np.array([0., 0., 0.])
#kf.F = np.array([[1.,0.,0.],[0.,1.,0.],[0.,0.,1.]])
#kf.H = np.array([[1., 1., 1.]])
#kf.P *= 1000.
#kf.R = 5
#from filterpy.common import Q_discrete_white_noise
#kf.Q = Q_discrete_white_noise(dim=3, dt=0.1, var=0.13)

def conn_handler(clientsock, addr, gyro, baro, accl):
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
      accx = accl.readXAxisValue()
      accy = accl.readYAxisValue()
      accz = accl.readZAxisValue()

      #kf.predict()
      #kf.update(np.array([[msgx], [msgy], [msgz]]))
      #print(kf.x)

      csvWriter.writerow([time.time(), msgx, msgy, msgz, msgbaro, msgtemp, accx, accy, accz])

      if msgx != None:
        clientsock.send(str(msgx * 0.01)) # msgx, degree per 0.01 sec.
        clientsock.send('*')
        clientsock.send(str(msgy * 0.01)) # msgy
        clientsock.send('*')
        clientsock.send(str(msgz * 0.01)) # msgz
        clientsock.send('*')
        clientsock.send(str(msgbaro / 100.0)) # msgbaro
        clientsock.send('*')
        clientsock.send(str(msgtemp / 10.0)) # msgtemp
        clientsock.send('*')
        clientsock.send(str(accx))
        clientsock.send('*')
        clientsock.send(str(accy))
        clientsock.send('*')
        clientsock.send(str(accz))
        clientsock.send('\n')
        time.sleep(0.01)

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

  accl = ACCL(CHANNEL)
  accl.startMeasuring()
  print('ACCL measuring started')

  baro = BARO(CHANNEL)

  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  sock.bind((host, port))
  sock.listen(backlog)

  while True:
    conn, addr = sock.accept()
    print('Connected by ' , addr)
    thread.start_new_thread(conn_handler, (conn, addr, gyro, baro, accl))
  conn.close()

def at_exit():
  f.close()

if __name__ == '__main__':
  main()
