#############################################
# Curso de Internet de las Cosas
# Profesor: Diego Dujovne
# Alumno: Gabriel Petracca
#
# Fecha: 03-11-2016
#
#
#############################################


from __future__ import print_function
import os
import sys
here = sys.path[0]
#print here
sys.path.insert(0,os.path.join(here,'..','..','..','coap'))
from coap import coap
import signal
import argparse
from influxdb import InfluxDBClient
from influxdb.client import InfluxDBClientError
import datetime
import random
import time


# Creo arreglo con MOTE IPs
MOTE_IP = []
MOTE_2 = 'bbbb::1415:92cc:0:2'
MOTE_IP.insert(len(MOTE_IP), MOTE_2)
MOTE_3 = 'bbbb::1415:92cc:0:3'
MOTE_IP.insert(len(MOTE_IP), MOTE_3)


c = coap.coap()

# Variables de InfluxDB
USER = 'root'
PASSWORD = 'root'
DBNAME = 'openwsn'
host='localhost'
port=8086
client = InfluxDBClient(host, port, USER, PASSWORD, DBNAME)


############################################

# Se crea la DB InfluxDB
print("Creando base de datos: " + DBNAME)
try:
	client.create_database(DBNAME)
	print ("Base de datos " + DBNAME + " creada correctamente\n")
except InfluxDBClientError:
	# Drop and create
	client.drop_database(DBNAME)
	client.create_database(DBNAME)

############################################# 
# Leer datos de MOTEs
while True:
   # Inicializo
   serie_Temp = []
   serie_Humedad = []
   for i in range(0,len(MOTE_IP)):
      try:
	   timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
	   p = c.GET('coap://[{0}]/i'.format(MOTE_IP[i]))
	   print ('Mediciones de MOTE IP: {0}'.format(MOTE_IP[i]))
	   print ('  - Fecha: {0}'.format(timestamp)) 
	   print ('  - Temperatura: {0}'.format(p[0])) 
	   print ('  - Humedad: {0}\n'.format(p[1]))

	   # Genero la info de Temperatura para insertar en DB
	   Medicion_Temp = {
		 "time": timestamp,
		 "measurement": "Temperatura de MOTE: {0}".format(MOTE_IP[i]),
		 'fields':  { 'value': p[0], },
		 }
#	   Temp = p[0]
	   serie_Temp.append(Medicion_Temp)
#	   print (Temp)
	   
	   # Genero la info de humedad para insertar en DB
	   Medicion_Humedad = {
		 "time": timestamp,
		 "measurement": "Humedad de MOTE: {0}".format(MOTE_IP[i]),
		 'fields':  { 'value': p[1], },
		 }
	   serie_Humedad.append(Medicion_Humedad)

      except Exception:
	   continue

   # Grabo mediciones en la base de datos
#   print ('#####  debug - Temp: {0}'.format(serie_Temp))
   client.write_points(serie_Temp, time_precision='ms')
   client.write_points(serie_Humedad, time_precision='ms')
      
   t = 10
   print ('\nLa Proxima medicion se hara dentro de ' + str(t) + ' segundos.\n')
   time.sleep(t)
	


############################################# 

c.close()


############################################# 
#while True:
#        input = raw_input("Done. Press q to close. ")
#        if input=='q':
#            print 'bye bye.'
#            #c.close()
#            os.kill(os.getpid(), signal.SIGTERM)
