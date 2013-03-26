import os
import inspect

from  ISY.IsyEvent import ISYEvent

server = ISYEvent(process_func=ISYEvent.print_event, process_func_arg="")

# you can subscribe to multiple devices
# server.subscribe('10.1.1.25')

server.subscribe('10.1.1.36')

try:
    print 'Use Control-C to exit'
    server.events_loop()
#    for d in  server.event_iter( ignorelist=["_0", "_11"] ):
#	server.print_event(d, "")
except KeyboardInterrupt:
    print 'Exiting'
