#! /usr/bin/env python
#   Gter Copyleft 2017
#   Roberto Marzocchi
#
#
#   Modified by an priginal project of Mark Williams (2016)
#	This library is free software; you can redistribute it and/or
#	modify it under the terms of the GNU Library General Public
#	License as published by the Free Software Foundation; either
#	version 2 of the License, or (at your option) any later version.
#	This library is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
#	Library General Public License for more details.
#	You should have received a copy of the GNU Library General Public
#	License along with this library; if not, write to the Free
#	Software Foundation, Inc., 59 Temple Place - Suite 330, Boston,
#	MA 02111-1307, USA



import smbus
from LSM9DS0 import *
import time
bus = smbus.SMBus(1)

#library added by GTER
import os,sys,shutil,re,glob
import socket
#import time
from datetime import datetime, date



#socket data
#TCP_IP is the address of the control center server (TBM)
#TCP_IP = '192.168.2.126'
# in questo modo gli faccio leggere i dati da terminale (IP address e ID apparato)
#print(sys.argv)
#TCP_IP = sys.argv[1]
# qua specifico l'ID dell'apparato

#in questo modo leggo invece i messaggi da file 
nomefile1="/home/pi/NARVALO/DATI/CONF/narvalo_conf.dat"
print "\n\nReading the %s file " %nomefile1

# legge dal file coordinate 
parametri=[]

i=0
cc=0
for riga in file(nomefile1): # lettura file 
	#print riga
	#line = riga
	parametri.append(riga.strip('\n'))
	i+=1

id_apparato=parametri[0]
TCP_IP=parametri[2].replace("\\\"","")


print "#######################################"
print "Id apparato:", id_apparato
print "IP CC Anticollisione:", TCP_IP
print "#######################################"


################
# fissi 
TCP_PORT = 8081
BUFFER_SIZE = 1024
check_connection=0





def writeACC(register,value):
		bus.write_byte_data(ACC_ADDRESS , register, value)
		return -1




def readACCx():
	acc_l = bus.read_byte_data(ACC_ADDRESS, OUT_X_L_A)
	acc_h = bus.read_byte_data(ACC_ADDRESS, OUT_X_H_A)
	acc_combined = (acc_l | acc_h <<8)

	return acc_combined  if acc_combined < 32768 else acc_combined - 65536


def readACCy():
	acc_l = bus.read_byte_data(ACC_ADDRESS, OUT_Y_L_A)
	acc_h = bus.read_byte_data(ACC_ADDRESS, OUT_Y_H_A)
	acc_combined = (acc_l | acc_h <<8)

	return acc_combined  if acc_combined < 32768 else acc_combined - 65536


def readACCz():
	acc_l = bus.read_byte_data(ACC_ADDRESS, OUT_Z_L_A)
	acc_h = bus.read_byte_data(ACC_ADDRESS, OUT_Z_H_A)
	acc_combined = (acc_l | acc_h <<8)

	return acc_combined  if acc_combined < 32768 else acc_combined - 65536




	
#initialise the accelerometer
writeACC(CTRL_REG1_XM, 0b01100111) #z,y,x axis enabled, continuos update,  100Hz data rate
writeACC(CTRL_REG2_XM, 0b00011000) #+/- 8G full scale



while True:
	
	
	#Read the accelerometer,gyroscope and magnetometer values
	ACCx = readACCx()
	ACCy = readACCy()
	ACCz = readACCz()

	#print("##### X = %f G  #####" % ((ACCx * 0.224)/1000)),
	#print(" Y =   %fG  #####" % ((ACCy * 0.224)/1000)),
	#print(" Z =  %fG  #####" % ((ACCz * 0.224)/1000))

	dt=datetime.utcnow()
	# Formatting datetime
	day_time=dt.strftime("%Y/%m/%d|%H:%M:%S.%f")
	MESSAGE = "IMU|%s|%0.3f|%0.3f|%0.3f" % (day_time, (ACCx * 9.81* 0.224)/1000.0, (ACCy * 9.81* 0.224)/1000.0, (ACCz * 9.81* 0.224)/1000.0)
	print MESSAGE

	#print "Acc:", "{:+7.3f}".format(m9a[0]), "{:+7.3f}".format(m9a[1]), "{:+7.3f}".format(m9a[2]),
	#print " Gyr:", "{:+8.3f}".format(m9g[0]), "{:+8.3f}".format(m9g[1]), "{:+8.3f}".format(m9g[2]),
	#print " Mag:", "{:+7.3f}".format(m9m[0]), "{:+7.3f}".format(m9m[1]), "{:+7.3f}".format(m9m[2])

	try:
		if (check_connection==0):
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.connect((TCP_IP, TCP_PORT))
		s.send(MESSAGE)
		print "Message sent!"
		data = s.recv(BUFFER_SIZE)
		#s.close()
		check_connection=1
		print "received data:", data
	except:
		print "Socket connection failed!"
		print "TCP_IP=", TCP_IP
		check_connection=0


	# this is the frequency of the msg in seconds 
	time.sleep(0.5)




	#slow program down a bit, makes the output more readable
	#time.sleep(0.03)


