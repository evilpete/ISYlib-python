
from __future__ import print_function
# from xml.dom.minidom import parse, parseString
# from StringIO import StringIO
import xml.etree.ElementTree as ET
# from xml.etree.ElementTree import  iselement
from pprint import pprint
# import base64
# import sys
import requests
# if sys.hexversion < 0x3000000:
#     import urllib2 as URL
#     from urllib2 import URLError, HTTPError
# else:
#     import urllib as URL
# import re
#from .IsyExceptionClass import IsyPropertyError, IsyValueError, IsySoapError
import ISY.IsyExceptionClass as IsyE

__author__ = 'Peter Shipley <peter.shipley@gmail.com>'
__copyright__ = "Copyright (C) 2017 Peter Shipley"
__license__ = "BSD"

#__all__ = ['IsyUtil', 'IsySubClass' ]
__all__ = ['format_node_addr']

# pylint: disable=superfluous-parens,unsubscriptable-object
# disable=unsubscriptable-object,unsupported-membership-test,unused-argument


def val2bool(en):
    if isinstance(en, str):
        rval = (str(en).strip().lower() in ("yes", "y", "true", "t", "1"))
    else:  # if isinstance(en, (long, int, float)):
        # Punt
        rval = bool(en)
    return rval


def et2d(et):
    """ Etree to Dict

        converts an ETree to a Dict Tree
        lists are created for duplicate tag

        if there are multiple XML of the same name
        an list array is used
        attrib tags are converted to "tag_name" + "attrib_name"

        if an invalid arg is passed a empty dict is retrurned


        arg: ETree Element  obj

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
            # d[et.tag + "_val"] = et.text
            d["#val"] = et.text
    if children:
        for child in children:
            if child.tag in d:
                # if type(d[child.tag]) != list:
                if not isinstance(d[child.tag], list):
                    t = d[child.tag]
                    d[child.tag] = [t]
            if list(child) or child.attrib:
                if child.tag in d:
                    d[child.tag].append(et2d(child))
                else:
                    d[child.tag] = et2d(child)
            else:
                if child.tag in d:
                    d[child.tag].append(child.text)
                else:
                    d[child.tag] = child.text
    return d


def format_node_addr(naddr):
    if not isinstance(naddr, str):
        raise IsyE.IsyValueError("{0} arg not string".format(__name__))
    addr_el = naddr.upper().split()
    a = "{0:0>2}' '{1:0>2}' '{2:0>2}' ".format(*addr_el)
    return a


def print_url(r): #, *args, **kwargs):
    # print("r=", type(r), dir(r))
    # print("r.request=", type(r.request), dir(r.request), "\n\n")

    print(r.request.method, r.request.url)
    print("\t", r.status_code, r.reason, r.url)
    print("\t", "encoding:", r.encoding, "/", "apparent_encoding:", r.apparent_encoding)
    print("\t", "elapsed time", r.elapsed)

    # print("content", r.content)
    # print("links", r.links)



#
# Simple Base class for ISY Class
#
class IsyUtil(object):
    def __init__(self):
        self.debug = 0
        self.baseurl = "" # never used
        self.error_str = ""
        self._req_session = None
        # self.pp = pprint.PrettyPrinter(indent=4)

    def _initReqSession(self):
        self._req_session = requests.Session()
        # if debug
        if self.debug & 0x02:
            hook = dict(response=print_url)
            self._req_session.hooks = hook


    def _printXML(self, xml):
        """ Pretty Print XML, for internal debug"""
        print("_printXML start")
        ET.dump(xml)

    def _set_prop(self, *arg):
        pass


    def _geturl(self, url, timeout=15):
        self.error_str = ""
        try:
            res = self._req_session.get(url, timeout=timeout)
            data = res.text # res.content
            res.close()
            return data
        except requests.exceptions.RequestException as rex:
            self.error_str = str("Response Code : {0} : {1} : {2}").format(
                rex.response.status_code, url, str(rex))
            return None

    def _getXMLetree(self, xmlpath, noquote=0, timeout=10):
        """ take a URL path, download XLM and return parsed Etree """

        if (noquote):
            xurl = self.baseurl + xmlpath
        else:
            xurl = self.baseurl + requests.compat.quote(xmlpath)
            # xurl = self.baseurl + URL.quote(xmlpath)
        # if self.debug & 0x02:
        #     print("_getXMLetree: " + xurl)

        # print("_getXMLetree : URL.Request")
        # req = URL.Request(xurl)
        # HTTPError
        try:
            res = self._req_session.get(xurl, timeout=timeout)

            data = res.text # res.content
            res.close()
            # print("res.getcode() ", res.getcode(), len(data))
        except IOError as ioex:
            self.error_str = str("Error Code : {0} : {1}").format(
                xurl, str(ioex))
            return None
        except requests.exceptions.RequestException as rex:
            self.error_str = str("Response Code : {0} : {1} : {2}").format(
                rex.response.status_code, xurl, str(rex))
            return None

        # len(self.error_str)
        if self.error_str:
            self.error_str = ""
        if self.debug & 0x200:
            print("requests.response=", res)
            print("requests.response.text=", data)
        et = None
        # len(data)
        if data:
            try:
                et = ET.fromstring(data)
            except ET.ParseError as e:
                print("Etree ParseError ")
                print("data = ", data, end='')
                print("e.message = ", e.message)
                # raise
            else:
                return et

        else:
            return None

    def _gensoap(self, cmd, **kwargs):

        if self.debug & 0x200:
            print("len kwargs = ", len(kwargs), kwargs)
        # len(kwargs) == 0
        if not kwargs:
            cmdsoap = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>" \
                + "<e:Envelope><s:Body>" \
                + "<u:{0!s} ".format(cmd) \
                + "xmlns:u=\"urn:udi-com:service:X_Insteon_Lighting_Service:1\" />" \
                + "</s:Body></e:Envelope>"
        else:
            cmdsoap = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>" \
                + "<s:Envelope><s:Body>" \
                + "<u:{0!s} ".format(cmd) \
                + "xmlns:u=\"urn:udi-com:service:X_Insteon_Lighting_Service:1\">"

            for k, v in kwargs.items():
                cmdsoap += "<{0}>{1!s}</{0}>".format(k, v)

            cmdsoap += "</u:{0!s}>".format(cmd) \
                    + "</s:Body></s:Envelope>"

        # print("cmdsoap = \n", cmdsoap)
        return cmdsoap

    # http://wiki.universal-devices.com/index.php?title=ISY-99i/ISY-26_INSTEON:Errors_And_Error_Messages
    def soapcomm(self, cmd, **kwargs):
        """
        takes a command name and a list of keyword arguments.
        each keyword is converted into a xml element
        """

        if not isinstance(cmd, str) or not cmd:
            raise IsyE.IsyValueError("SOAP Method name missing")

        # if self.debug & 0x02:
        #     print("sendcomm : ", cmd)

        soap_cmd = self._gensoap(cmd, **kwargs)

        xurl = self.baseurl + "/services"
        if self.debug & 0x02:
            # print("xurl = ", xurl)
            print("soap_cmd = ", soap_cmd)

        # req_headers = {'content-type': 'application/soap+xml'}
        # req_headers = {'content-type': 'text/xml'}
        req_headers = {'Content-Type': 'application/xml; charset="utf-8"'}

        # req = URL.Request(xurl, soap_cmd, {'Content-Type': 'application/xml; charset="utf-8"'})

        data = ""
        try:

            res = self._req_session.post(xurl, data=soap_cmd, headers=req_headers)
            data = res.text # res.content
            if self.debug & 0x200:
                print("res.status_code ", res.status_code, len(data))
                print("data ", data)
            res.close()

        # except URL.HTTPError as e:
        except requests.exceptions.RequestException as rex:

            status_code = rex.response.status_code
            self.error_str = str("Reponse Code : {0} : {1} {2}").format(status_code, xurl, cmd)
            if ((cmd == "DiscoverNodes" and rex.response.status_code == 803)
                    or (cmd == "CancelNodesDiscovery" and status_code == 501)
                    # or (cmd == "RemoveNode" and status_code == 501)
               ):


                if self.debug & 0x02:
                    print("spacial case : {0} : {1}".format(cmd, status_code))
                    print("status_code = ", status_code)
                    print("response.reason = ", rex.response.reason)
                    print("response.headers = ", rex.response.headers)
                    # print("e.filename = ", e.filename)
                    print("\n")

                return rex.response.text

            if self.debug & 0x202:
                print("status_code = ", status_code)
                # print("e.read = ", e.read())
                print("RequestException = ", rex)
                print("data = ", data)

            mess = "{!s} : {!s} : {!s}".format(cmd, kwargs, status_code)
            # This a messy and should change
            raise IsyE.IsySoapError(mess, httperr=rex)
        else:
            if self.error_str: # len
                self.error_str = ""
            if self.debug & 0x200:
                print(data)
            return data



    def sendDeviceSpecific(self, command, s1, s2, s3, s4, stringbuffer):
        pass
#
#   public Object sendDeviceSpecific(String s, String s1, String s2, String s3, String s4, StringBuffer stringbuffer)
#    {
#        UDHTTPResponse udhttpresponse = null;
#        StringBuffer stringbuffer1 = new StringBuffer();
#        stringbuffer1.append("<command>").append(s != null ? s : "").append("</command>");
#        stringbuffer1.append("<node>").append(s1 != null ? s1 : "").append("</node>");
#        stringbuffer1.append("<p1>").append(s2 != null ? s2 : "").append("</p1>");
#        stringbuffer1.append("<p2>").append(s3 != null ? s3 : "").append("</p2>");
#        stringbuffer1.append("<p3>").append(s4 != null ? s4 : "").append("</p3>");
#        stringbuffer1.append("<flag>0</flag>");
#        stringbuffer1.append("<CDATA>").append(((CharSequence) \
#                             (stringbuffer != null ? ((CharSequence) (stringbuffer)) : ""))).append("</CDATA>");
#        udhttpresponse = submitSOAPRequest("DeviceSpecific", stringbuffer1, (short)2, false, false);
#        if(udhttpresponse == null)
#            return null;
#        if(!udhttpresponse.opStat)
#            return null;
#        else
#            return udhttpresponse.body;
#    }
#

    def sendfile(self, src=None, filename="", data=None):
        """
            upload file

            args:
                data            content for fine to upload
                src             file to load upload content ( if data is None )
                filename        name for remote file
        """

        if self.debug & 0x01:
            print("sendfile : ", self.__class__.__name__)

        if filename[0] != '/':
            filename = "/USER/WEB/" + filename
        elif not str(filename).upper().startswith("/USER/WEB/"):
            raise IsyE.IsyValueError("sendfile: invalid dst filename : {!s}".format(filename))

        # not len(data)
        if not data:
            if not src:
                src = filename

            if self.debug & 0x20:
                print("using file {!s} as data src".format(src))

            with open(src, 'r') as content_file:
                data = content_file.read()
        else:
            if self.debug & 0x20:
                print("using provided data as data src")

        return self._sendfile(filename=filename, data=data, load="n")


    def _sendfile(self, filename="", data="", load="n"):

        if (filename.startswith('/')):
            xurl = self.baseurl + "/file/upload" + filename + "?load=" + load
        else:
            xurl = self.baseurl + "/file/upload/" + filename + "?load=" + load

        if self.debug & 0x02:
            print("{0} xurl : {1}".format(__name__, xurl))
        # req = URL.Request(xurl, data, {'Content-Type': 'application/xml; charset="utf-8"'})
        req_headers = {'Content-Type': 'application/xml; charset="utf-8"'}

        try:
            res = self._req_session.post(xurl, data=data, headers=req_headers)
            responce = res.text
            res.close()
            # print("responce:", res.status_code, len(responce))
        except requests.exceptions.RequestException as rex:
            mess = "{!s} : {!s} : {!s}".format("/file/upload", filename, rex.response.status_code)
            raise IsyE.IsySoapError(mess, httperr=rex)
        else:
            return responce



    def _printdict(self, d):
        """ Pretty Print dictionary, for internal debug"""
        print("===START===")
        pprint(d)
        print("===END===")

    def _printinfo(self, uobj, ulabel="\t"):
        """ Debug util """
        print("%s: tag=%s text=%s attr=%s : atype=%s : type=%s" % (ulabel, uobj.tag, uobj.text, uobj.attrib, type(uobj.attrib), type(uobj)))

# Var : '1:1': {  'id': '1:1', 'init': '0', 'name': 'enter_light',
#          'ts': '20130114 14:33:35', 'type': '1', 'val': '0'}
#
# Node: '15 4B 53 1': {  'ELK_ID': 'A01', 'address': '15 4B 53 1', 'flag': '128',
#           'enabled': 'true', 'name': 'Front Light 2', 'pnode': '15 4B 53 1',
#           'property': {  'ST': {  'formatted': 'Off', 'id': 'ST',
#                               'uom': '%/on/off', 'value': '0'}}
#
# Scene:  '20326': { 'ELK_ID': 'C11', 'address': '20326', 'deviceGroup': '25',
#                    'flag': '132', 'name': 'Garage Lights'
#                    'members': {  '16 3F E5 1': '32', '16 D3 73 1': '32' }, },
#
# NodeFolder: '12743': {  'address': '12743', 'name': 'Garage Scenes'},
#
# Prog '0003': {  'enabled': 'true', 'folder': 'false', 'id': '0003',
#           'name': 'AM Off', 'parentId': '0001', 'runAtStartup': 'false',
#           'running': 'idle', 'status': 'false',
#           'lastFinishTime': '2013/03/27 09:41:28',
#           'lastRunTime': '2013/03/27 09:41:28',
#           'nextScheduledRunTime': '2013/03/27 10:05:00', },
#
# Prog '000A': {  'folder': 'true', 'id': '000A', 'lastFinishTime': None,
#               'lastRunTime': None, 'name': 'garage',
#               'parentId': '0001', 'status': 'true'},



class IsySubClass(IsyUtil):
    """ Sub Class for ISY
    This is a Sub Class for Node, Scene, Folder, Var, and Program Objects

        This Class is not intended for direct use

        attributes/properties:
            type :      object dependent flag
            value :     current value
            id/address :        unique for object used by ISY
            name :      name of object

        funtions:
            no public funtions

    """

    _getlist = ["name", "id", "value", "address", "type", "enabled"]
    _setlist = []
    _propalias = {}
    _boollist = ["enabled"]

    def __init__(self, isy, objdict):
        """ INIT """

        self.error_str = ""

        if isinstance(objdict, dict):
            self._mydict = objdict
        else:
            raise IsyE.IsyValueError("{!s}: called without objdict".format(self.__class__.__name__))

        if isinstance(isy, IsyUtil):
            self.isy = isy
            self.debug = isy.debug
        else:
            # print("error : class " + self.__class__.__name__ + " called without Isy")
            raise TypeError("IsySubClass: isy arg is not a ISY family class")

        if self.debug & 0x04:
            print("IsySubClass: ", end='')
            self._printdict(self._mydict)

    #_objtype = (0, "unknown")
    _objtype = "unknown"

    def objType(self):
        return self._objtype
        # return self._objtype[0]

    def _get_prop(self, prop):
        """ Internal funtion call """
        # print("U _get_prop =", prop)
        if prop in self._propalias:
            prop = self._propalias[prop]

        if prop in self._getlist:
            if prop in self._mydict:
                if prop in self._boollist:
                    return val2bool(self._mydict[prop])
            return self._mydict[prop]
        return None

#    def _set_prop(self, prop, val):
#       """ Internal funtion call """
#       if prop in self._propalias:
#           prop = self._propalias[prop]
#
#       if not prop in self._setlist:
#           raise IsyE.IsyPropertyError("_set_prop : "
#               "no property Attribute " + prop)
#       pass


#    def get_prop_list(self, l):
#        """ Get a list of properties
#
#            args:
#                prop_list : a list of property names
#
#            returns
#                a list of property values
#
#            if a property does not exist a value of None is used
#          ( instead of raising a Attribute error)
#
#        """
#        pass
#

    def _getaddr(self):
        """  Address or ID of Node (readonly) """
        return self._get_prop("address")
    address = property(_getaddr)

    def _getname(self):
        """  Name of Node (readonly) """
        return self._get_prop("name")
    name = property(_getname)

    def _gettype(self):
        """  Type of Node (readonly) """
        # self._get_prop("type")
        # return self._objtype[1]
        return self._objtype
    objtype = property(_gettype)

    def __getitem__(self, prop):
        """ Internal method

            allows Objects properties to be accessed in  a dict style

        """
        return self._get_prop(prop)

    def __setitem__(self, prop, val):
        """ Internal method

            allows Objects properties to be accessed/set in a dict style

        """
        return self._set_prop(prop, val)

    def __delitem__(self, prop):
        raise IsyE.IsyPropertyError("__delitem__ : can't delete propery :  " + str(prop))


    def __del__(self):
        if self.debug & 0x80:
            print("__del__ ", self.__repr__())
        if hasattr(self, "_mydict"):
            self._mydict.clear()

    def __iter__(self):
        """ Internal method

            allows Objects properties to be access through iteration

        """
        if self.debug & 0x80:
            print("IsyUtil __iter__")
        for p in self._getlist:
            if p in self._mydict:
                yield (p, self._get_prop(p))
            else:
                yield (p, None)


    def __repr__(self):

        # return "<%s %s @ %s at 0x%x>" %
        return "<{} {} @ {} at 0x{:x}>".format(
            self.__class__.__name__,
            self._get_prop("id"),
            self.isy.addr, id(self))



#    def __hash__(self):
#        # print("_hash__ called")
#        return str.__hash__(self._get_prop("id]").myval)

#    def __compare__(self, other):
#        print("__compare__ called")
#       if isinstance(other, str):
#        if not hasattr(other, "myval"):
#            return -1
#        return str.__cmp__(self.myval, other.myval)

    def __getattr__(self, attr):
        # print("U attr =", attr)
        attr_v = self._get_prop(attr)
        if attr_v is not None:
            return attr_v
        else:
#            print("attr =", attr, self.address)
#           print("self type = ", type(self))
#           pprint(self._mydict)
            raise AttributeError("bad attr = {}".format(attr))


    # This allows for
    def __eq__(self, other):
        """ smarter test for compairing Obj value """
        # print("IsyUtil __eq__")
        # print("self", self)
        # print("other", other)
        if isinstance(other, str):
            return self._get_prop("id") == other

        # if type(self) != type(other):
        if not isinstance(other, type(self)):
            return False
            # NotImplemented
        if hasattr(other._mydict, "id"):
            return(self._get_prop("id") == other._get_prop("id"))
        return False



#
# Do nothing
# (syntax check)
#
if __name__ == "__main__":
    print(__main__.__file__)
    print("syntax ok")
    exit(0)
