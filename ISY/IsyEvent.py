
import SocketServer
import BaseHTTPServer
import sys
import os
import traceback
import re
import socket

import xml.etree.ElementTree as ET

try:
    import fcntl
except ImportError:
    fcntl = None


# taken partly from   SimpleXMLRPCServer
class ISYRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    encode_threshold = None # 1400
    default_request_version = "HTTP/0.9"
    # Set this to HTTP/1.1 to enable automatic keepalive
    #protocol_version = "HTTP/1.0" 
    protocol_version = "HTTP/1.1" 



    wbufsize = -1    
    disable_nagle_algorithm = True

    def do_POST(self):
	# print  "do_POST"
	# print "IRH ", self.__class__.__name__

	try:

	    # data = self.rfile.read()
	    max_chunk_size = 10*1024*1024
	    size_remaining = int(self.headers["content-length"])
	    # print "content-length = ", size_remaining
            L = []
            while size_remaining:
                chunk_size = min(size_remaining, max_chunk_size)
                chunk = self.rfile.read(chunk_size)
                if not chunk:
                    break
                L.append(chunk)
                size_remaining -= len(L[-1])
		# print "size_remaining = ", size_remaining
            data = ''.join(L)


	    # print data,"\n\n\n"



	except Exception, e: 
	    self.send_response(500)

	    if hasattr(self.server, '_send_traceback_header') and \
		    self.server._send_traceback_header:
		self.send_header("X-exception", str(e))
		print "X-exception", str(e)
		self.send_header("X-traceback", traceback.format_exc())
		print "X-traceback", traceback.format_exc()

		self.send_header("Content-length", "0")
		self.end_headers()
	else :
	    process_event(data)

	    self.send_response(200)
	    self.send_header("Content-length", "0")
	    self.end_headers()


    def report_404 (self):
	print  "report_404"
	print  self.__class__.__name__
	# Report a 404 error
	self.send_response(404)
	response = 'No such page'
	self.send_header("Content-type", "text/plain")
	self.send_header("Content-length", str(len(response)))
	self.end_headers()
	self.wfile.write(response)

    def log_request(self, code='-', size='-'):
	"""Selectively log an accepted request."""
	# print  "log_request"
	# print  self.__class__.__name__
	     
	#if self.server.logRequests:
	# BaseHTTPServer.BaseHTTPRequestHandler.log_request(self, code, size)
	pass

# from pprint import pprint
def process_event(data) :

    ddat = dict ( )
    ev = ET.fromstring(data)
    #print "process_event ", data,"\n\n"

    for e in ev.iter() :
	ddat[e.tag] = e.text
	if e.attrib :
	    for k, v in e.attrib.iteritems() :
		ddat[k] = v

    # print ddat
    #if ddat[control][0] == "_" :
#	return

    print "%-4s\t%-12s\t%s\t%s" % (ddat["control"], ddat["node"], ddat["action"], ddat["eventInfo"] )








class SimpleISYDispatcher( ) :


    def __init__(self, allow_none=False, encoding=None):
	print  "SimpleISYDispatcher __init"
	print  self.__class__.__name__
	self.funcs = {} 
	self.instance = None
	self.allow_none = allow_none 
	self.encoding = encoding 

    def _dispatch(self) :
	print  "SimpleISYDispatcher _dispatch"
	print  self.__class__.__name__

class SimpleISYServer(SocketServer.TCPServer,SimpleISYDispatcher) :

    allow_reuse_address = True
    timeout = 300

    _send_traceback_header = False

    def __init__(self, addr, requestHandler=ISYRequestHandler,
		 logRequests=True, allow_none=False, encoding=None,
		 bind_and_activate=True):
	print  "SimpleISYServer__init__"
	print  "SIS ", self.__class__.__name__
	SocketServer.TCPServer.__init__(self, addr, requestHandler, bind_and_activate)
	SimpleISYDispatcher.__init__(self, allow_none, encoding)
	if fcntl is not None and hasattr(fcntl, 'FD_CLOEXEC'):
	    flags = fcntl.fcntl(self.fileno(), fcntl.F_GETFD)
	    flags |= fcntl.FD_CLOEXEC
	    fcntl.fcntl(self.fileno(), fcntl.F_SETFD, flags)



    def subscribe(self, isyaddr):
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	server_address = (isyaddr, 80)
	sock.connect(server_address)
	sn =  sock.getsockname()   
	self.myip = sn[0]
	print "P ", self.myip

	self.myurl = "http://{0}:{1}/".format( sn[0], self.server_address[1] )
	print "myurl ", self.myurl



	post_body = "<s:Envelope><s:Body>" \
		"<u:Subscribe xmlns:u=\"urn:udicom:service:X_Insteon_Lighting_Service:1\">" \
		+ "<reportURL>{0}</reportURL>".format(self.myurl) \
		+ "<duration>infinite</duration>" \
		"</u:Subscribe></s:Body></s:Envelope>" 
		# "\r\n\r\n" 

	post_head = "POST /services HTTP/1.1\r\n" \
		+ "Host: {0}:80\r\n".format(isyaddr) \
		+ "Authorization: Basic YWRtaW46YWRtaW4=\r\n" \
		+ "Content-Length: {0}\r\n".format( len(post_body) ) \
		+ "Content-Type: text/xml; charset=\"utf-8\"\r\n" \
		+ "\r\n\r\n"

	post = post_head + post_body
	print post

	msglen = len(post)
	totalsent = 0
	while totalsent < msglen:
	    sent = sock.send(post[totalsent:])
	    if sent == 0:
		raise RuntimeError("socket connection broken")
	    totalsent = totalsent + sent

	rf = sock.makefile("rb")

	l = rf.readline()
	if ( l[:5] != 'HTTP/' ) :
	    raise ValueError( l )

	l.split(' ', 1)[1]
	if ( l.split(' ')[1] != "200") :
	    raise ValueError( l )

	while 1 :
	    l = rf.readline()
	    if len(l) == 2 :
		break
	    if l[:15] == "Content-Length:" :
		l.rstrip('\r\n')
		data_len = int(l.split(':')[1])


	reply = rf.read(data_len) 
	print "reply = '", reply, "'"

	sock.shutdown(1)
	rf.close()




    def _dispatch(self):
	print  "server _dispatch"
	print  self.__class__.__name__



