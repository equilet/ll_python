#!/usr/bin/env python

import serial, time, sys, os, psycopg2, xmlrpclib, heapq, OSC
from xml.dom import minidom

#osc vars
iparg = 'localhost'
portarg = 9000
oclient = OSC.OSCClient()

#xml
XML_SETTINGS_FILE = "stormforce-xr/sxrserver-settings.xml"
#psql vars
POSTGRESQL_DATABASE = POSTGRESQL_PASSWORD = POSTGRESQL_SERVER = POSTGRESQL_USERNAME = ''

#program vars
intensity = ''
threshold = 250.0;
noiselevel = 0.0;
population = 100;
periodicity = 1.0;

def main():
    result = 1
    print '------------------------psql query code------------------------'
    print 'starting time: ' , time.ctime()
    print 'threshold is set to: ', threshold
    read_XML()
    connect()
    time.sleep(periodicity);
    get_data_distances(True)

def connect():
    global cur, conn
    conn = psycopg2.connect(database = POSTGRESQL_DATABASE, host = POSTGRESQL_SERVER, user = POSTGRESQL_USERNAME, password = POSTGRESQL_PASSWORD)
    #conn.autocommit = True 
    #conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    cur.execute("TRUNCATE TABLE tblstrikes;")
    conn.commit()  #have to commit
    oclient.connect((iparg, portarg))

def get_data_distances(status):
    while(status):

	#have to order by ID here, because we want the newest data
	cur.execute("SELECT correctedstrikedistance FROM tblstrikes ORDER BY id ASC LIMIT 1000;")
	distances = cur.fetchall()
	cur.execute("TRUNCATE TABLE tblstrikes;")
	conn.commit()  #have to commit

	#find smallest N
	nsmallest = float(min(distances)[0])
	print 'smallest distance from antenna: ', nsmallest, ' miles'
	#if lightning that struck was close...
	if nsmallest and nsmallest < threshold:
	    print 'threshold detected...'
	    print '----------------------------------------------------------------'
	    msg = OSC.OSCMessage()
	    msg.setAddress('/lightning_interruption')
	    msg.append('bang')
	    oclient.send(msg)

	time.sleep(periodicity);

def read_XML():
	global POSTGRESQL_DATABASE, POSTGRESQL_PASSWORD, POSTGRESQL_SERVER, POSTGRESQL_USERNAME, SERVER_PORT
	
	if os.path.exists(XML_SETTINGS_FILE):
		print 'success reading file...'
		xmldoc = minidom.parse(XML_SETTINGS_FILE)
		myvars = xmldoc.getElementsByTagName("Setting")
		
		for var in myvars:
			for key in var.attributes.keys():
				val = str(var.attributes[key].value)
				
				if key == "PostgreSQLDatabase":
					POSTGRESQL_DATABASE = val
				elif key == "PostgreSQLPassword":
					POSTGRESQL_PASSWORD = val
				elif key == "PostgreSQLServer":
					POSTGRESQL_SERVER = val
				elif key == "PostgreSQLUsername":
					POSTGRESQL_USERNAME = val

main()
