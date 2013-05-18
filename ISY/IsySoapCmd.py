# import sys
# import os
# import traceback
#import warnings
import socket

from ISY.IsyExceptionClass import IsySUDSError

import base64

# import collections 
                 
try: 
    import fcntl 
except ImportError:
    fcntl = None

""" Support for making simple SOAP calls 

Very simple, with out Soap Library dependencies

Classes
-------

SendSoapCmd()
    Constructs and Handles call operations 
    args:
	addr : ISY addr
    named args:
	userp : ISY login
	userp : ISY pass
	keepalive : keep connection open for sequental calls



Functions
---------

sendcomm("command", arg1, arg2, arg3, ....)
    Generates SOAP command call

closesock():
    close network connection (for use with keep alive)
"""

__all__ = [ 'SendSoapCmd' ]

class SendSoapCmd(object):

    def __init__(self, addr, **kwargs) :
        self.soap_rf = None
        self.soap_wf = None
        self.soap_sock = None
        self.error = 0
        self.debug = 0x03
	userp = kwargs.get("userp", "admin")# isy.userp 
	userl = kwargs.get("userl", "admin")# isy.userl 
        self.isyaddr = addr # isy.addr
	self.keepalive = kwargs.get("keepalive", False)
	self.authbasic = base64.encodestring('{!s}:{!s}'.format(userl, userp))[:-1]

    def fileno(self):
        """ Interface required by select().  """
        return self.soap_sock.fileno()


    def closesock(self) :
	if self.debug & 0x01 :
	    print("soap_sock.close ")

	if self.soap_wf :
	    self.soap_wf.close()
	    self.soap_wf = None

	if self.soap_rf :
	    self.soap_rf.close()
	    self.soap_rf = None

	if self.soap_sock :
	    self.soap_sock.close()
	    self.soap_sock = None

    def opensock(self):

        if self.debug & 0x01 :
            print("_opensock ", self.isyaddr)

        # self.soap_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        server_address = (self.isyaddr, 80)
	try :
	    self.soap_sock = socket.create_connection(server_address, 10)
	except OSError as msg:
	    print "Failed to connect : {0}".format(str(msg))
	    raise RuntimeError(msg)

        #sn =  sock.getsockname()
        #self.myip = sn[0]
        #print "P ", self.myip

        #self.myurl = "http://{0}:{1}/".format(sn[0], self.server_address[1])
        #print "myurl ", self.myurl

        if self.keepalive and fcntl is not None and hasattr(fcntl, 'FD_CLOEXEC'):
            flags = fcntl.fcntl(self.soap_sock.fileno(), fcntl.F_GETFD)
            flags |= fcntl.FD_CLOEXEC
            fcntl.fcntl(self.soap_sock.fileno(), fcntl.F_SETFD, flags)

        self.soap_rf = self.soap_sock.makefile("rb")
        self.soap_wf = self.soap_sock.makefile("wb")

        return self.soap_sock

    def _gensoap(self, cmd, **kwargs) :

	if len(kwargs) == -1 :
	    cmdsoap = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>" \
		+ "<e:Envelope><s:Body>" \
		+ "<u:{0!s}/>".format(cmd) \
		+ "</s:Body></e:Envelope>"
	else :
	    cmdsoap =  "<?xml version=\"1.0\" encoding=\"UTF-8\"?>" \
		+ "<s:Envelope><s:Body>" \
		+ "<u:{0!s} ".format(cmd) \
		+ "xmlns:u=\"urn:udi-com:service:X_Insteon_Lighting_Service:1\">"

	    for k, v in kwargs.items() :
		cmdsoap += "<{0}>{1!s}</{0}>".format(k, v)
	 
	    cmdsoap += "</u:{0!s}>".format(cmd) \
		    + "</s:Body></s:Envelope>"

	# print "cmdsoap = \n", cmdsoap
	return cmdsoap

    def sendcomm(self, cmd, **kwargs):

        if self.debug & 0x01 :
            print "sendcomm : ", self.__class__.__name__

	soap_cmd = self._gensoap(cmd, **kwargs)

        post_head = "POST /services HTTP/1.1\r\n" \
            + "Host: {!s}:80\r\n".format(self.isyaddr) \
            + "Authorization: Basic {!s}\r\n".format(self.authbasic) \
            + "Content-Length: {!s}\r\n".format(len(soap_cmd)) \
            + "Content-Type: text/xml; charset=\"utf-8\"\r\n" 

	if self.keepalive :
	    post_head += "Connection: Keep-Alive\r\n" \

	post_head += "\r\n\r\n"

        # post_add = post_head.format(self.isyaddr, self.authbasic, len(soap_cmd)) \
        post_add = post_head + soap_cmd

	if self.debug & 0x20 :
	    print "post_add = ", post_add, "\n\n"

	#-# return

	if ( self.soap_sock == None ) :
	    self.opensock()

        self.soap_wf.write(post_add)
        self.soap_wf.flush()

        l = self.soap_rf.readline()
	if self.debug & 0x20 : print "++ ", l,
        if (l[:5] != 'HTTP/') :
	    print "l = ", l
            raise IsySUDSError(l)

	hresponse = l.split(' ')[1]
        #if (l.split(' ')[1] != "200") :
        #    raise IsySUDSError(l)

        while 1 :
            l = self.soap_rf.readline()
	    if self.debug & 0x20 : print "++ ", l,
            if len(l) == 2 :
                break
            if l[:15] == "Content-Length:" :
                l.rstrip('\r\n')
                data_len = int(l.split(':')[1])


        reply = self.soap_rf.read(data_len)

        if self.debug & 0x02 :
            print "Soap reply = '", reply, "'", "\n\n\n\n"


	if not self.keepalive :
	    self.closesock()


        if (hresponse != "200") :
            raise ValueError(l)

	return reply




#
# Do nothing
# (syntax check)
#
if __name__ == "__main__":
    import __main__
    print(__main__.__file__)

    print("syntax ok")


    #sp = SendSoapCmd("10.1.1.36", keepalive=True)

    #  MoveNode SetParent RemoveFromGroup
    #sp.sendcomm("MoveNode", node="18 A1 28 1", group="33444", flag="65519")
    #sp.sendcomm("RemoveFromGroup", node="18 A1 28 1", group="33444")
    #sp.sendcomm("MoveNode", node="18 A1 28 1", group="33444", flag=16)
    ##sp._gensoap("MoveNode", node="18 A1 28 1", group="33444", flag="65519")
    #sp.sendcomm("RenameNode", id="18 A1 28 1", name="18A12801")

    ##sp.sendcomm("SetParent", "18 A1 28 1", 1, 12743, 3)
    #sp.sendcomm("SetParent", node="18 A1 28 1", nodeType=1, parent=12743, parentType=3)
    ##sp._gensoap("SetParent", node="18 A1 28 1", nodeType=1, parent=12743, parentType=3)
    ##sp._gensoap("Reboot")
    #sp.sendcomm("SetParent", node="18 A1 28 1", nodeType=1)
    #sp.sendcomm("RemoveFromGroup", node="18 A1 28 1", group="33444")
    #sp.sendcomm("GetSystemTime")
    #sp.sendcomm("GetSystemStatus")



    exit(0)
