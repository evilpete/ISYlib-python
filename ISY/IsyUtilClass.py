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

class IsySubClass(IsyUtil):
    getlist = [ "name", "id", "value", "address" ]
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



    def __getitem__(self, prop):
	return self._get_prop(prop)

    def __setitem__(self, prop):
	return self._set_prop(prop)

    def __delitem__(self, prop):
        raise IsyProperyError("__delitem__ : can't delete propery :  " + str(prop) )
	pass

    def __get__(self, instance, owner):
	return self._get_prop("val")
    def __set__(self,  val):
	self._set_prop("value", val)

    def __iter__(self):
	for p in self.getlist :
	    if p in self._mydict :
		yield (p , self._mydict[p])
	    else :
		yield (p , None)

    def __repr__(self):
	return "<%s %s @ %s at 0x%x>" % ( self.__class__.__name__,
		self._get_prop("id"), self.isy.addr, id(self))


#
# Do nothing
# (syntax check)
#
if __name__ == "__main__":
    import __main__
    print __main__.__file__
    print("syntax ok")
    exit(0)
