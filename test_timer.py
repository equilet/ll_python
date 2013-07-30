#!/usr/bin/env python

import time, sys

def print_something(status):
    while(status):
	print 'the time: ' , time.ctime()
	time.sleep(1);

def main():
    result = 1
    print 'starting time: ' , time.ctime()

    result = raw_input('press g to start timer, s to stop.\n')
    while(result is 'g'):
	print_something(True)
	result = ''

    result = None
    time.stop()

main()
