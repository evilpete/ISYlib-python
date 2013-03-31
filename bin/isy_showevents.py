#!/usr/local/bin/python2.7

import os
import inspect

from  ISY.IsyEvent import ISYEvent

server = ISYEvent()

# you can subscribe to multiple devices
# server.subscribe('10.1.1.25')

server.subscribe( os.getenv('ISY_ADDR', '10.1.1.36'))
server.set_process_func(ISYEvent.print_event, "")

try:
    print 'Use Control-C to exit'
    server.events_loop()   #no return
#    for d in  server.event_iter( ignorelist=["_0", "_11"] ):
#	server.print_event(d, "")
except KeyboardInterrupt:
    print 'Exiting'
