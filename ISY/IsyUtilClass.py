# from xml.dom.minidom import parse, parseString
#from StringIO import StringIO
import xml.etree.ElementTree as ET
from IsyExceptionClass import *
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
        # print "_getXMLetree : self._opener.open "
        res = self._opener.open(req)
        data = res.read()
	# print "res.getcode() ", res.getcode(), len(data)
        res.close()
	if len(data) :
	    return ET.fromstring(data)
	else :
	    return None

    def _printdict(self, d):
        """ Pretty Print dictionary """
	print "===START==="
	pprint(d)
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

    _getlist = [ "name", "id", "value", "address", "type" ]
    _setlist = [ ]
    _propalias = { }

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
	""" Internal funtion call """
	if prop in self._propalias :    
	    prop = self._propalias[prop]

	if prop in self._getlist : 
	    if prop in self._mydict :
		return(self._mydict[prop])
	return(None)

#    def _set_prop(self, prop, val):
#	""" Internal funtion call """
#	if prop in self._propalias :    
#	    prop = self._propalias[prop]
#
#	if not prop in self._setlist :
#	    raise IsyPropertyError("_set_prop : "
#		"no property Attribute " + prop)
#	pass


    def get_prop_list(self, l):
	""" Get a list of properties

	    args:
		prop_list : a list of property names

	    returns
		a list of property values

	    if I property does not exist a value of None is used instead
	    of raising a Attribute error

	"""
	pass

    def on(self, *args) :
	""" Send On command to a node

	    args: 
		take optional value for on level

	"""
        self.isy._node_comm(self._mydict["address"], "DON", *args)
	#if "property" in self._mydict :
        #    self._mydict["property"]["time"] = 0
        # self.update()

    def off(self) :
	""" Send Off command to a node

	    args: None

	"""
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
	""" Internal method 

	    allows Objects properties to be accessed in  a dict style

	"""
	return self._get_prop(prop)

    def __setitem__(self, prop):
	""" Internal method 

	    allows Objects properties to be accessed/set in a dict style

	"""
	return self._set_prop(prop)

    def __delitem__(self, prop):
        raise IsyProperyError("__delitem__ : can't delete propery :  " + str(prop) )

    def __get__(self, instance, owner):
	""" Internal method 

	    allows Object status to be access as the value of the obj

	"""
	return self._get_prop("value")
#    def __set__(self,  val):
#	""" Internal method 
#
#	    allows Object status to be set as the value of the obj
#
#	"""
#	self._set_prop("value", val)

    def __iter__(self):
	""" Internal method 

	    allows Objects properties to be access through iteration

	"""
	print "IsyUtil __iter__"
	for p in self._getlist :
	    if p in self._mydict :
		yield (p , self._get_prop(p))
	    else :
		yield (p , None)

    def member_iter(self):
	return self.members_list()

    def member_list(self):
    
	if 'members' in self._mydict :
	    # print "mydict['members'] : ", type(self._mydict['members']) 
	    if type(self._mydict['members']) == 'dict' :
		return self._mydict['members'].keys()
	    # if type(self._mydict['members']) == 'list' :
	    return self._mydict['members'][:]
	return [ ]

    def __repr__(self):
	return "<%s %s @ %s at 0x%x>" % ( self.__class__.__name__,
		self._get_prop("id"), self.isy.addr, id(self))



#    def __hash__(self):
#        #print "_hash__ called"
#        return str.__hash__(self._get_prop("id]").myval)
 
#    def __compare__(self, other):
#        print "__compare__ called"
#	if isinstance(other, str) :
#        if not hasattr(other, "myval") :
#            return -1
#        return ( str.__cmp__(self.myval, other.myval) )

    def __getattr__(self, attr):
	attr_v = self._get_prop(attr)
	if attr_v :
	    return attr_v
	else :
	    print "attr =", attr
	    raise AttributeError, attr

    def is_member(self, obj) :
	if "members" in self._mydict :
	    if isinstance(obj, str)  :
		return obj in self._mydict["members"]
	    elif isinstance(obj, IsySubClass)  :
		return obj._get_prop("address") in self._mydict["members"]
	return False

    # check if scene _contains_ node
    def __contains__(self, other):
	    return self.is_member(other)

    # check if obj _contains_  attib
#    def __contains__(self, other):
#	if isinstance(other, str)  :
#	    return other in self._getlist
#	else :
#	    return False

    # This allows for 
    def __eq__(self, other):
	print "IsyUtil __eq__"
	print "self", self
	print "other", other
	if isinstance(other, str) :
	    return self._get_prop("id") == other
	if type(self) != type(other) :
	    return False
	    # NotImplemented 
	if hasattr(other._mydict, "id") :
	    return self._get_prop("id") == other._get_prop("id")
	return False


#
# Do nothing
# (syntax check)
#
if __name__ == "__main__":
    import __main__
    print __main__.__file__
    print("syntax ok")
    exit(0)
