# from xml.dom.minidom import parse, parseString
from StringIO import StringIO
import xml.etree.ElementTree as ET
# import base64
import urllib2 as URL
# import re
from pprint import pprint

#from IsyClass import Isy

# import ISY.IsyClass 

__all__ = ['IsyUtil']

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

#
# Do nothing
# (syntax check)
#
if __name__ == "__main__":
    import __main__
    print __main__.__file__
    print("syntax ok")
    exit(0)
