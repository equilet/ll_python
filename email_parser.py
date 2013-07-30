#!/usr/bin/env python
#http://docs.python.org/library/imaplib.html#imap4-objects
#http://en.wikipedia.org/wiki/Host_%28network%29
#http://docs.python.org/library/imaplib.html

import imaplib, re, sys, time, threading, os, liblo, ConfigParser
from optparse import OptionParser


#parse input
CONFIG_FILENAME = 'default.cfg'
config = ConfigParser.ConfigParser()
config.read(CONFIG_FILENAME)

parser = OptionParser()
parser.add_option("-u", "--username", 
	help="set user's email address", 
	default=config.get("Localization", "username"))
parser.add_option("-p", "--password", 
	help="set user's password", 
	default=config.get("Localization", "password"))
(options, args) = parser.parse_args()

iparg = 'localhost' #iparg = '127.0.0.1'
oportarg = 9000
kill_program = False
length_limit = 1024

print 'ip given: ', iparg
print 'outport given: ', oportarg
#print 'inport given: ', iportarg
print 'usr given: ', options.username
    
email_interval = 2.0

#send all msgs to port on local machine
try:
    target = liblo.Address(oportarg)
except liblo.AddressError, err:
    print str(err)
    sys.exit()

def init():
    login()
    flush_inbox()

def login():
    global server
    server = imaplib.IMAP4_SSL('imap.googlemail.com', 993)
    server.login(options.username, options.password)

def logout_handle(addr, tags, stuff, source):
    print 'received kill call'
    global kill_program
    kill_program = True

def flush_inbox():
    global server
    server.select('INBOX')
    server.store('1:*', '+X-GM-LABELS', '\\Trash')
    server.expunge()

#this is the signature that gmail appends to SMS messages; it may change over time.
#living lenses can alter this function if need be, and will periodically check in to see what the SMS reads as.

#example msg:  /email_content ['Dkd-- using SMS-to-email. Reply to this email to text the sender back and  /']
def filter_signature(s):
    try:
	a_sig = re.sub(r'Sent|--Sent|-- Sent', '', s)
	b_sig = re.sub(r'using SMS-to-email.  Reply to this email to text the sender back and', '', a_sig)
	c_sig = re.sub(r'save on SMS fees.', '', b_sig)
	d_sig = re.sub(r'https://www.google.com/voice', '', c_sig)
	no_lines = re.sub(r'\n|=|\r?', '', d_sig) #add weird characters to this as needed
    except:
	nolines = s
    return no_lines

def parse_email():
    global server
    server.select('INBOX')
    status, ids = server.search(None, 'UnSeen')
    print 'status is: ', status
    
    if not ids or ids[0] is '':
	print 'no new messages'
    else:
	print 'found a message; attempting to parse...'
	latest_id = ids[0]
	status, msg_data = server.fetch(latest_id, '(UID BODY[TEXT])')
	raw_data = msg_data[0][1]
	raw_filter = filter_signature(raw_data)
	char_array = list(raw_filter)
	char_string = ''.join(char_array)
	length = len(char_string)
	#raw_filter = raw_data
	if(length < length_limit):
	    liblo.send(target, '/email_content', (char_string))
	    print 'message result: ', char_string
	    print 'message length: ', length, ' characters'
	else:
	    print 'message found, but too long; discarding.'
    flush_inbox()

#execute main block
def main():
    while(True):
	global server
	login()
	parse_email()
	server.close()
	time.sleep(email_interval)

init()
main()
