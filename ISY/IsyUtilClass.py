# from xml.dom.minidom import parse, parseString
#from StringIO import StringIO
import xml.etree.ElementTree as ET
# import base64
import urllib2 as URL
# import re
from pprint import pprint

#from IsyClass import Isy

# import ISY.IsyClass 

__all__ = ['IsyUtil', 'IsySubClass' ]

#
# Simple Base class for ISY Class
#
class IsyUtil(object):
    def __init__(self) :
        self.debug = 0
        # self.pp = pprint.PrettyPrinter(indent=4)


    def _printXML(self, xml):
        """ Pretty Print XML """
        print "_printXML start"
        ET.dump(xml)

    def _getXMLetree(self, xmlpath, noquote=0):
        """ take a URL path, download XLM and return parsed Etree """
	if ( noquote ) :
	    xurl = self.baseurl + xmlpath
	else :
	    xurl = self.baseurl + URL.quote(xmlpath)
        if self.debug & 0x02:
            print "_getXMLetree : " + xurl
        # print "_getXMLetree : URL.Request"
        req = URL.Request(xurl)
        # print "_getXMLetree : self.opener.open "
        res = self.opener.open(req)
        data = res.read()
        res.close()
        return ET.fromstring(data)

    def _printdict(self, d):
        """ Pretty Print dictionary """
        try:
            self.pp
        except AttributeError:
            self.pp = pprint.PrettyPrinter(indent=3)
        finally:
	    print "===START==="
            self.pp.pprint(d)
	    print "===END==="

    def _printinfo(self, uobj, ulabel="\t"):
	""" Debug util """
        print "%s: tag=%s text=%s attr=%s : atype=%s : type=%s" % (ulabel, uobj.tag, uobj.text, uobj.attrib, type(uobj.attrib), type(uobj))

# Var : '1:1': {  'id': '1:1', 'init': '0', 'name': 'enter_light',
#	   'ts': '20130114 14:33:35', 'type': '1', 'val': '0'}
#
# Node: '15 4B 53 1': {  'ELK_ID': 'A01', 'address': '15 4B 53 1', 'flag': '128',
#	    'enabled': 'true', 'name': 'Front Light 2', 'pnode': '15 4B 53 1',
#	    'property': {  'ST': {  'formatted': 'Off', 'id': 'ST',
#				'uom': '%/on/off', 'value': '0'}}
#
# Scene:  '20326': { 'ELK_ID': 'C11', 'address': '20326', 'deviceGroup': '25',
#		     'flag': '132', 'name': 'Garage Lights'
#		     'members': {  '16 3F E5 1': '32', '16 D3 73 1': '32' }, },
#
# NodeFolder: '12743': {  'address': '12743', 'name': 'Garage Scenes'},
#
# Prog '0003': {  'enabled': 'true', 'folder': 'false', 'id': '0003',
#	    'name': 'AM Off', 'parentId': '0001', 'runAtStartup': 'false',
#	    'running': 'idle', 'status': 'false',
#	    'lastFinishTime': '2013/03/27 09:41:28',
#	    'lastRunTime': '2013/03/27 09:41:28',
#	    'nextScheduledRunTime': '2013/03/27 10:05:00', },
#
# Prog '000A': {  'folder': 'true', 'id': '000A', 'lastFinishTime': None,
#		'lastRunTime': None, 'name': 'garage',
#		'parentId': '0001', 'status': 'true'},



class IsySubClass(IsyUtil):
    """ Sub Class for ISY
    This is a Sub Class for Node, Scene, Folder, Var, and Program Objects

	This Class is not intended for direct use

	attributes/properties :
	    type :	object dependent flag
	    value :	current value
	    id/address :	unique for object used by ISY
	    name :	name of object

	funtions:
	    no public funtions

    """

    getlist = [ "name", "id", "value", "address", "type" ]
    setlist = [ ]
    propalias = { }

    def __init__(self, isy, objdict) :
	""" INIT """
        if isinstance(objdict, dict):
            self._mydict = objdict
        else :
            print "error : class IsySubClass called without objdict"
            raise IsyValueError("IsySubClass: called without objdict")

        if isinstance(isy, IsyUtil):
            self.isy = isy
            self.debug = isy.debug
        else :
            print "error : class " + self.__class__.__name__ + " called without Isy"
            raise TypeError("IsySubClass: isy is wrong class")

        if self.debug & 0x04 :
	    print "IsySubClass: ",
	    self._printdict(self._mydict)


    def _get_prop(self, prop):
	if prop in self.propalias :    
	    prop = self.propalias[prop]

	if prop in self.getlist : 
	    if prop in self._mydict :
		return(self._mydict[prop])
	return(None)

    def _set_prop(self, prop, val):

	if prop in self.propalias :    
	    prop = self.propalias[prop]

	if not prop in self.setlist :
	    raise IsyPropertyError("_set_prop : "
		"no property Attribute " + prop)
	pass


    def on(self, *args) :
        self.isy._node_comm(self._mydict["address"], "DON", *args)
	#if "property" in self._mydict :
        #    self._mydict["property"]["time"] = 0
        # self.update()

    def off(self) :
        self.isy._node_comm(self._mydict["address"], "DOF")
	if "property" in self._mydict :
            self._mydict["property"]["time"] = 0
	    if "ST" in  self._mydict["property"] :
		self._mydict["property"]["ST"]["value"] = 0
		self._mydict["property"]["ST"]["formatted"] = "off"

    def beep(self) :
        self.isy._node_comm(self._mydict["address"], "BEEP")

    def _getaddr(self):
	"""  Address or ID of Node (readonly) """
        return self._get_prop("address")
    address = property(_getaddr)

    def _getname(self):
	"""  Name of Node (readonly) """
        return self._get_prop("name")
    name = property(_getname)

    def __getitem__(self, prop):
	return self._get_prop(prop)

    def __setitem__(self, prop):
	return self._set_prop(prop)

    def __delitem__(self, prop):
        raise IsyProperyError("__delitem__ : can't delete propery :  " + str(prop) )

    def __get__(self, instance, owner):
	return self._get_prop("value")
    def __set__(self,  val):
	self._set_prop("value", val)

    def __iter__(self):
	print "IsyUtil __iter__"
	for p in self.getlist :
	    if p in self._mydict :
		yield (p , self._get_prop(p))
	    else :
		yield (p , None)

    def __repr__(self):
	return "<%s %s @ %s at 0x%x>" % ( self.__class__.__name__,
		self._get_prop("id"), self.isy.addr, id(self))



#    def __hash__(self):
#        #print "_hash__ called"
#        return str.__hash__(self._get_prop("id]").myval)
 
#    def __compare__(self,other):
#        print "__compare__ called"
#	if isinstance(other, str) :
#        if not hasattr(other, "myval") :
#            return -1
#        return ( str.__cmp__(self.myval ,other.myval) )

    def __getattr__(self,attr):
	attr_v = self._get_prop(attr)
	if attr_v :
	    return attr_v
	else :
	    print "attr =",attr
	    raise AttributeError, attr


    # check if obj _contains_  attib
    def __contains__(self, other):
	if isinstance(other, str)  :
	    return other in self.getlist
	else :
	    return False

    # This allows for 
    def __eq__(self,other):
	print "IsyUtil __eq__"
	print "self", self
	print "other", other
	if isinstance(other, str) :
	    return self._get_prop("id") == other
	if type(self) != type(other) :
	    return false
	    # NotImplemented 
	if not hasattr(other._mydict, "id") :
	    return object.__eq__(self,other)
	return self._get_prop("id") == other._get_prop("id")

#
# Do nothing
# (syntax check)
#
if __name__ == "__main__":
    import __main__
    print __main__.__file__
    print("syntax ok")
    exit(0)
