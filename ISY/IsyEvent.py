
"""
        Ugly...

        work in progress, meant as proof of concept

        needs rewrite or cleanup
"""
from __future__ import print_function

__author__ = 'Peter Shipley <peter.shipley@gmail.com>'
__copyright__ = "Copyright (C) 2017 Peter Shipley"
__license__ = "BSD"

import time
import sys
# import os
# import traceback
import warnings
# import re
import base64
import socket
import select


import xml.etree.ElementTree as ET

from .IsyEventData import EVENT_CTRL
from ._isy_printevent import _print_event
import collections

try:
    import fcntl
except ImportError:
    fcntl = None

__all__ = ['ISYEvent']


class ISYEvent(object):


    def __init__(self, addr=None, **kwargs):
        # print( "ISYEvent ", self.__class__.__name__)

        self.debug = kwargs.get("debug", 0)
        self.connect_list = []
        self._shut_down = 0
        self.connected = False
        self.isy = kwargs.get("isy", None)
        self.level = kwargs.get("level", "1")

        self.process_func = kwargs.get("process_func", _print_event)
        self.process_func_arg = kwargs.get("process_func_arg", None)

        # print("_print_event", _print_event)
        if self.process_func:
            assert isinstance(self.process_func, collections.Callable), \
                    "process_func Arg must me callable"

        addr = kwargs.get("addr", None)

        if addr:
            userl = kwargs.get("userl", "admin")
            userp = kwargs.get("userp", "admin")
            authtuple = (  addr, userl, userp)
            self.connect_list.append(ISYEventConnection(self, authtuple))


    def set_process_func(self, func, arg):

        if func:
            # if self.debug & 0x01:
            if self.debug & 0x01:
                print("set_process_func", func)
            self.process_func = func
            assert isinstance(self.process_func, collections.Callable), \
                    "process_func Arg must me callable"
        else:
            self.process_func = _print_event

        if arg:
            self.process_func_arg = arg



    def _finish(self):
        # print("Finishing... ", self.__class__.__name__)
        for s in self.connect_list:
            s.disconnect()

        del self.connect_list[:]
        if self.isy:
            self.isy._isy_event = None
        # print("Finished... ", self.__class__.__name__)

#    def __del__(self):
#       print("\n\n\n>>>>>>>>>__del__ ", \
#          self.__class__.__name__, "<<<<<<<<<<<<<\n\n\n")

    def _stop_event_loop(self):
        # print(self.__class__.__name__)
        self._shut_down = 1

    # <?xml version="1.0" encoding="UTF-8"?><s:Envelope><s:Body>
    # <u:SetDebugLevel xmlns:u="urn:udi-com:service:X_Insteon_Lighting_Service:1">
    #<option>3</option></u:SetDebugLevel></s:Body></s:Envelope>
    def subscribe(self, **kwargs):
        """ subscribe to Isy device event stream

            this function adds an ISY device to the list of devices to
            receive events from

            named args:
                addr = IP address or hostname of isydevice
                userl = isy admin login
                userp = isy admin password
                level = debug level
        """

        addr = kwargs.get("addr", None)

        if self.debug & 0x01:
            print("subscribe ", addr)

        if addr in self.connect_list:
            # print("addr :", addr)
            if self.debug & 0x01:
                print("connect_list :", self.connect_list)
            warnstr = str("Duplicate addr : {0}").format(addr)
            warnings.warn(warnstr, RuntimeWarning)
            return

        userl = kwargs.get("userl", "admin")
        userp = kwargs.get("userp", "admin")

        authtuple = (  addr, userl, userp)

        new_conn = ISYEventConnection(self, authtuple)

        # see if the other connections are connected
        # if so connect to avoid an error in select()
        if self.connected:
            new_conn.connect()

        self.connect_list.append(new_conn)

    def unsubscribe(self, addr):
        """ unsubscribe to Isy device event stream

            this function removes an ISY device to the list of devices to
            receive events from

            arg: IP address or hostname of isydevice
        """
        remote_ip = socket.gethostbyname(addr)
        if not addr in self.connect_list:
            warnings.warn(
                "address {0}/{1} not subscribed".format(addr, remote_ip),
                RuntimeWarning)
            return
        isyconn = self.connect_list[self.connect_list.index(addr)]
        isyconn.disconnect()
        self.connect_list.remove(isyconn)
        del(isyconn)

    def _process_event(self, conn_obj):
        """

            _process_event : takes XML from the events stream
                coverts to a dict and passed to process_func provided
        """
        #print("-")

        l = conn_obj.event_rf.readline()
        if len(l) == 0:
            raise IOError("bad read form socket")
            # conn_obj._opensock(self.authtuple[0])
            # conn_obj._subscribe()
        # print("_process_event = ", l)
        if (l[:5] != 'POST '):
            print("Stream Sync Error")
            for x in range(10):
                print(x, " ")
                l = conn_obj.event_rf.readline()
                if (l[:5] == 'POST '):
                    break
            else:
                raise IOError("can not resync event stream")

        while 1:
            l = conn_obj.event_rf.readline()
            if len(l) == 2:
                break
            # print("HEADER : ", l)
            if l[:15].upper() == "CONTENT-LENGTH:":
                l.rstrip('\r\n')
                data_len = int(l.split(':')[1])

        # print("HEADER data_len ", data_len)

        # data = conn_obj.event_rf.readread(data_len)
        data_remaining = data_len
        L = []
        while data_remaining:
            chunk = conn_obj.event_rf.read(data_remaining)
            if not chunk:
                break
            L.append(chunk)
            data_remaining -= len(chunk)
        data = ''.join(L)

        ddat = dict()

        # work around for encoding bugs
        # in eventinfo field
        if data.find('-->') >= 0:
            data = data.replace('-->', '--&gt;')

        if data.find('<=') >= 0:
            data = data.replace('<=', '&lt;=')

        if data.find('< ') >= 0:
            # print("< HACK")
            data = data.replace('< ', '&lt; ')

        if data.find('<NULL>'):
            data = data.replace('<NULL>', '&lt;NULL&gt;')

        # ev = ET.fromstring(data)
        try:
            ev = ET.fromstring(data)
        except ET.ParseError as e:
            print("Etree ParseError ")
            print("data = ", data,)
            print("e.message = ", e.message)
            raise

        #print("_process_event ", data, "\n\n")


        ddat = self.et2d(ev)

        # print(ddat)
        #if ddat[control][0] == "_":
        #       return
        # print(ddat)
        return(ddat, data)
        #return(ddat)

    def et2d(self, et):
        """ Etree to Dict

            converts an ETree to a Dict Tree
            lists are created for duplicate tag

            if there are multiple XML of the same name
            an list array is used
            attrib tags are converted to "tag_name" + "attrib_name"

            if an invalid arg is passed a empty dict is retrurned


            arg: ETree Element obj

            returns: a dict obj
        """
        d = dict()
        if not isinstance(et, ET.Element):
            return d
        children = list(et)
        if et.attrib:
            for k, v in list(et.items()):
                d[et.tag + "-" + k] = v
            if et.text is not None:
                #d[et.tag + "_val"] = et.text
                d["#val"] = et.text
        if children:
            for child in children:
                if child.tag in d:
                    if type(d[child.tag]) != list:
                        t = d[child.tag]
                        d[child.tag] = [t]
                if list(child) or child.attrib:
                    if child.tag in d:
                        d[child.tag].append(self.et2d(child))
                    else:
                        d[child.tag] = self.et2d(child)
                else:
                    if child.tag in d:
                        d[child.tag].append(child.text)
                    else:
                        d[child.tag] = child.text
        return d

    def _et2d(self, et):
        """ Etree to Dict

            converts an ETree to a Dict Tree
            lists are created for duplicate tag

            arg: a ETree obj
            returns: a dict() obj

        """
        d = dict()
        children = list(et)
        if et.attrib:
            for k, v in list(et.items()):
                d[et.tag + "-" + k] = v
        if children:
            for child in children:
                if child.tag in d:
                    if type(d[child.tag]) != list:
                        t = d[child.tag]
                        d[child.tag] = [t]
                if list(child) or child.attrib:
                    if child.tag in d:
                        d[child.tag].append(self.et2d(child))
                    else:
                        d[child.tag] = self.et2d(child)
                else:
                    if child.tag in d:
                        d[child.tag].append(child.text)
                    else:
                        d[child.tag] = child.text
        return d





    def event_iter(self, ignorelist=None, poll_interval=0.5):
        """Loop thought events

            reads events packets and passes them to processor

        """

        self.connected = True
        for s in self.connect_list:
            s.connect()

        while not self._shut_down:
            if len(self.connect_list) == 0:
                break
            try:
                r, _, e = select.select(self.connect_list, [], [], poll_interval)
                for rl in r:
                    d, _ = self._process_event(rl)
                    if ignorelist:
                        if d["control"] in ignorelist:
                            continue
                    yield d
            except socket.error:
                print("socket error({0}): {1}".format(e.errno, e.strerror))
                self.reconnect()
            except IOError as e:
                print("I/O error({0}): {1}".format(e.errno, e.strerror))
                self.reconnect()
            except KeyboardInterrupt:
                return
            #except Exception:
                #print("Unexpected Error:", sys.exc_info()[0])
                #traceback.print_stack()
                #print(repr(traceback.extract_stack())
                #print(repr(traceback.format_stack())
            finally:
                pass

        if self._shut_down:
            self._finish()


    def reconnect(self):
        self.connected = True
        for isy_conn in self.connect_list:
            isy_conn.reconnect()

    def events_loop(self, **kargs):
        """Loop thought events

            reads events packets and passes them to processor

        """
        ignorelist = kargs.get("ignorelist", None)
        poll_interval = kargs.get("poll_interval", 0.5)

        if self.debug & 0x01:
            print("events_loop ", self.__class__.__name__)

        self.connected = True
        for isystream in self.connect_list:
            isystream.connect()


        while not self._shut_down:
            try:
                r, _, e = select.select(self.connect_list, [], [], poll_interval)
                for rs in r:
                    d, x = self._process_event(rs)
                    # print("d :", type(d)
                    if self.debug & 0x0400:
                        print("---------")
                        print("event_loop= ", x)
                        print("event_loop= ", d)
                        sys.stdout.flush()
                    if ignorelist:
                        if d["control"] in ignorelist:
                            continue
                    self.process_func(d, self.process_func_arg, x)
                    # self.process_func(d, x)
            except socket.error as e:
                print("socket error({0}): {1}".format(e.errno, e.strerror))
                self.reconnect()
            except IOError as e:
                print("I/O error({0}): {1}".format(e.errno, e.strerror))
                self.reconnect()
#           except Exception:
#               print("Unexpected error:", sys.exc_info()[0])
            finally:
                pass

        if self._shut_down:
            self._finish()

class ISYEventConnection(object):

    def __init__(self, isyevent, authtuple):
        self.event_rf = None
        self.event_wf = None
        self.event_sock = None
        self.parent = isyevent
        self.error = 0
        self.debug = isyevent.debug

        # print("authtuple : ", type(authtuple), authtuple)
        self.authtuple = authtuple

    def __hash__(self):
        return str.__hash__(self.authtuple[0])

    def __repr__(self):
        return "<ISYEventConnection %s at 0x%x>" % (self.authtuple[0], id(self))

    def __str__(self):
        return self.authtuple[0]

    def __del__(self):
        self.disconnect()
        #print("\n\n\n>>>>>>>>>__del__ ", self.__class__.__name__, "<<<<<<<<<<<<<\n\n\n")

    def __eq__(self, other):
        if isinstance(other, str):
            return self.authtuple[0] == other
        if not hasattr(other, "authtuple"):
            return False
        return self.authtuple == other.authtuple

    def fileno(self):
        """ Interface required by select().  """
        return self.event_sock.fileno()

    def reconnect(self):
        # print("--reconnect to self.authtuple[0]--")
        self.error += 1

        retry = True
        while retry:
            try:
                self.disconnect()
                self.connect()
                retry = False
            except socket.error as e:
                if self.debug & 0x01:
                    print("socket error - reconnecting({0}): {1}".format(e.errno, e.strerror))
                time.sleep(1)
                retry = True

    def disconnect(self):
        try:
            if self.event_rf:
                self.event_rf.close()
                self.event_rf = False
        except IOError:
            pass

        try:
            if self.event_wf:
                self.event_wf.close()
                self.event_wf = False
        except IOError:
            pass

        try:
            if self.event_sock:
                self.event_sock.close()
                self.event_sock = False
        except IOError:
            pass

    def connect(self):
        if self.debug & 0x01:
            print("connect ", self.__class__.__name__)
        self._opensock()
        self._subscribe()

    def _opensock(self):

        if self.debug & 0x01:
            print("_opensock ", self.authtuple[0])

        # self.event_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        host_port = 80

        addr_l = self.authtuple[0].split(":")
        host_addr=addr_l[0]
        if len(addr_l) > 1:
            host_port=addr_l[1]
        server_address = (host_addr, host_port)

        self.event_sock = socket.create_connection(server_address, 10)
        self.event_sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)

        if hasattr(socket, 'TCP_KEEPINTVL'):
           self.event_sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 1)
        if hasattr(socket, 'TCP_KEEPCNT'):
           self.event_sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 5)
        if hasattr(socket, 'TCP_KEEPIDLE'):
           self.event_sock.setsockopt(socket.SOL_TCP, socket.TCP_KEEPIDLE, 10)

        #sn = sock.getsockname()
        #self.myip = sn[0]
        #print("P ", self.myip)

        #self.myurl = "http://{0}:{1}/".format(sn[0], self.server_address[1])
        #print("myurl ", self.myurl)

        if fcntl is not None and hasattr(fcntl, 'FD_CLOEXEC'):
            flags = fcntl.fcntl(self.event_sock.fileno(), fcntl.F_GETFD)
            flags |= fcntl.FD_CLOEXEC
            fcntl.fcntl(self.event_sock.fileno(), fcntl.F_SETFD, flags)

        self.event_rf = self.event_sock.makefile("rb")
        self.event_wf = self.event_sock.makefile("wb")

        return self.event_sock

    def _subscribe(self):

        if self.debug & 0x01:
            print("_subscribe : ", self.__class__.__name__)

#        if ( not isinstance(self.event_wf, socket)
#                or not isinstance(self.event_rf, socket)):
#            raise RuntimeError(
#                   "{!s} called with invalid socket".format(self.__class__.__name__))

        # <ns0:Unsubscribe><SID>uuid:168</SID><flag></flag></ns0:Unsubscribe>
        post_body = "<s:Envelope><s:Body>" \
            "<u:Subscribe xmlns:u=\"urn:udicom:service:X_Insteon_Lighting_Service:1\">" \
            + "<reportURL>REUSE_SOCKET</reportURL>" \
            + "<duration>infinite</duration>" \
            "</u:Subscribe></s:Body></s:Envelope>"
            # "\r\n\r\n"

        base64pass = base64.encodestring('%s:%s' % (self.authtuple[1], self.authtuple[2]))[:-1]
        post_head = "POST /services HTTP/1.1\r\n" \
            + "Host: {0}:80\r\n".format(self.authtuple[0]) \
            + "Authorization: Basic {0}\r\n".format(base64pass) \
            + "Content-Length: {0}\r\n".format(len(post_body)) \
            + "Content-Type: text/xml; charset=\"utf-8\"\r\n" \
            + "\r\n\r\n"


        post = post_head + post_body

        self.event_wf.write(post)
        self.event_wf.flush()

        l = self.event_rf.readline()
        if (l[:5] != 'HTTP/'):
            raise ValueError(l)

        if (l.split(' ')[1] != "200"):
            raise ValueError(l)

        while 1:
            l = self.event_rf.readline()
            if len(l) == 2:
                break
            if l[:15] == "Content-Length:":
                l.rstrip('\r\n')
                data_len = int(l.split(':')[1])


        reply = self.event_rf.read(data_len)
        if self.debug & 0x01:
            print("_subscribe reply = '", reply, "'")


#
# Do nothing
# (syntax check)
#
if __name__ == "__main__":
    import __main__
    print(__main__.__file__)

    print("syntax ok")
    exit(0)
