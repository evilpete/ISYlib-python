
from xml.dom.minidom import parse, parseString
from StringIO import StringIO
import xml.etree.ElementTree as ET
import base64
import urllib2 as URL
import re
import os
from pprint import pprint
import sys
import string
import re
import pprint


# Debug Flags:
# 0x01 = report loads
# 0x02 = report urls used
# 0x04 = report func call
# 0x08 = Dump loaded data
# 0x10 = Dump loaded data
# 0x20 =
# 0x40 =
# 0x80 =
#


class IsyError(Exception):
    """Base exception."""
    pass
class IsyCommandError(IsyError):
    """General exception for command errors."""
    pass
class IsyNodeError(IsyError):
    """General exception for Node errors."""
    pass
class IsyResponseError(IsyError):
    """General exception for Node errors."""
    pass

class IsyBaseClass(object):
    def __init__(self) :
	self.debug=0
	# self.pp = pprint.PrettyPrinter(indent=4)

    def _printXML(self, xml):
	print "_printXML start"
	ET.dump(xml)

    def _getXMLetree(self, xmlpath):
	xurl = self.baseurl + URL.quote(xmlpath)
	if self.debug & 0x02 :
	    print "_getXMLetree : " + xurl 
	# print "_getXMLetree : URL.Request"
	req = URL.Request(xurl)
	# print "_getXMLetree : self.opener.open "
	res = IsyClass.opener.open(req)
	data = res.read()
	res.close()
	return  ET.fromstring(data)

    def _node_set_prop(self, naddr, prop, val) :
	""" node_set_prop without argument validation """
	#print "_node_set_prop : node=%s prop=%s val=%s" % str(naddr), prop, val
	print "_node_set_prop : node=" + str(naddr) + " prop=" + prop + " val=" + val
	xurl = "/rest/nodes/" + naddr + "/set/" + prop + "/" + val
	resp = self._getXMLetree(xurl)
	if resp.attrib["succeeded"] != 'true' :
	    raise IsyResponseError("Node Property Set error : node=%s prop=%s val=%s" % \
		naddr, prop, val )


    def _printdict(self, d):
	try:
	    self.pp
	except AttributeError:
	    self.pp = pprint.PrettyPrinter(indent=3)
	finally:
	    self.pp.pprint(d)


    def _printinfo(self, uobj, ulabel="\t"):
	print "%s: tag=%s text=%s attr=%s : atype=%s : type=%s" % (ulabel, uobj.tag, uobj.text, uobj.attrib, type(uobj.attrib), type(uobj))


# if hasattr(instance, 'tags') and isinstance(instance.tags, dict):
#     for tag in instance.tags:

# def batch .write

class IsyClass(IsyBaseClass):
    password_mgr = URL.HTTPPasswordMgrWithDefaultRealm()
    handler = URL.HTTPBasicAuthHandler(password_mgr)
    opener = URL.build_opener(handler)
    def __init__(self, isyaddr='', userl="admin", userp="admin", debug=0):
	self.debug = debug
	self.addr = isyaddr or os.getenv('ISY_ADDR', '10.1.1.36')
	self.baseurl = "http://" + self.addr 
	IsyClass.handler.add_password(None, self.addr, userl, userp)
	# self.opener = URL.build_opener(IsyClass.handler, URL.HTTPHandler(debuglevel=1))
	# self.opener = URL.build_opener(IsyClass.handler)
	print "baseurl: " + self.baseurl + " : " + userl + " : " + userp
	self.load_conf();
	print "__init__ end"


    def _preload_all(self):
	self.load_nodes()
	self.load_clim()
	self.load_conf()

    #
    # load_nodes
    #
    def load_nodes(self) :
	self.nodedict = dict ()
	self.nodeCdict = dict ()
	self.name2addr = dict ()
	if self.debug & 0x01 :
	    print "load_nodes pre _getXML"
	nodeinfo = self._getXMLetree("/rest/nodes")
	if self.debug & 0x04 :
	    self._printinfo(nodeinfo, "\nnodeinfo")
	self._gen_nodedict(nodeinfo)
	# self._gen_folder_list(nodeinfo)
	self._gen_nodegroups(nodeinfo)
	# self._printdict(self.nodedict)

    def _gen_folder_list(self, nodeinfo) :
	self.folderlist = dict () 
	for fold in nodeinfo.iter('folder'):
	    fprop = dict ()
	    for child in fold.iter() :
		fprop[child.tag] = child.text
	    self.folderlist[fprop["address"]] = fprop["name"]

    def _gen_nodegroups(self, nodeinfo) :
	self.nodegroups = dict () 
	self.groups2addr = dict ()
	for grp in nodeinfo.iter('group'):
	    gprop = dict ()
	    if hasattr(grp, 'attrib') and isinstance(grp.attrib, dict):
		for k, v in grp.attrib.items() :
		    gprop[k] = v
	    for child in grp.iter() :
		if child.tag != "members" :
		    gprop[child.tag] = child.text
		else :
		    glist = [ ]
		    for lnk in child.iter('link'):
			glist.append(lnk.text)
		    gprop[child.tag] = glist

	    if "address" in gprop :
		self.nodegroups[gprop["address"]] = gprop
		if "name" in gprop :
		    self.groups2addr[gprop["name"]] = str(gprop["address"])
	    else :
		self._printinfo(grp, "Error : no address in group :")

    def _gen_nodedict(self, nodeinfo) :
	self.nodedict = dict () 
	for inode in nodeinfo.iter('node'):
	    # self._printinfo(inode, "\n\n inode")
	    idict = dict ()
	    if hasattr(inode, 'attrib') and isinstance(inode.attrib, dict):
		for k, v in inode.attrib.items() :
		    idict[k] = v
	    for child in inode.iter() :
		#self._printinfo(child, "\tchild")
		
		if child.tag != "property" :
		    # print "child.tag = " + child.tag
		    idict[child.tag] = child.text
		else :
		    nprop = dict ()
		    for k, v in child.items() :
			# print "child.items",k,v
			nprop[k] = v
		    if "id" in nprop :
			idict[child.tag] = dict ()
			idict[child.tag][nprop["id"]] = nprop

	    if "address" in idict :
		self.nodedict[idict["address"]] = idict
		if "name" in idict :
		    self.name2addr[idict["name"]] = idict["address"]
	    else :
		self._printinfo(inode, "Error : no address in node :")
	#print "\n>>>>\t", self.nodedict, "\n<<<<<\n"

# if hasattr(instance, 'tags') and isinstance(instance.tags, dict):
#     for tag in instance.tags:


    def node_names(self) :
	""" returns a dict of ( Node names : Node address ) """
	try:
	    self.name2addr
	except AttributeError:
	    self.load_nodes()
	finally:
	    return self.name2addr

    def scene_names(self) :
	""" returns a dict of ( Node names : Node address ) """
	try:
	    self.groups2addr
	except AttributeError:
	    self.load_nodes()
	finally:
	    return self.groups2addr

    def node_addrs(self) :
	""" returns a iist scene/group addresses """
	try:
	    self.nodedict
	except AttributeError:
	    self.load_nodes()
	finally:
	    return self.nodedict.keys()

    def scene_addrs(self) :
	""" returns a iist scene/group addresses """
	try:
	    self.nodegroups
	except AttributeError:
	    self.load_nodes()
	finally:
	    return self.nodegroups.keys()


    def get_node(self, node_id) :
	""" Rerurns a IsyNode Class Obj of a scene or node """
	if self.debug & 0x01 :
	    print "get_node"
	try:
	    self.nodedict
	except AttributeError:
	    self.load_nodes()
#	except:
#	    print "Unexpected error:", sys.exc_info()[0]
#	    return None
	finally:
	    nodeid = self._get_node_id(node_id)
	    if nodeid in self.nodedict :
		if not nodeid in self.nodeCdict :
		    self.nodeCdict[nodeid] = IsyNode(self, self.nodedict[nodeid]);
		return self.nodeCdict[nodeid]
	    elif  nodeid in self.nodegroups:
		if not nodeid in self.nodeCdict :
		    self.nodeCdict[nodeid] = IsyNode(self, self.nodegroups[nodeid]);
		return self.nodeCdict[nodeid]
	    else :
		print "IsyClass get_node no node : \"%s\"" % nodeid
		raise LookupError("no node such Node : " + str(nodeid) )


    def _get_node_id(self, nid):
	n = str(nid)
	if string.upper(n) in self.nodedict :
	    print "_get_node_id : " + n + " nodedict " + string.upper(n) 
	    return string.upper(n)
	if n in self.name2addr :
	    print "_get_node_id : " + n + " name2addr " + self.name2addr[n]
	    return self.name2addr[n]
	if n in self.groups2addr :
	    print "_get_node_id : " + n + " groups2addr " + self.groups2addr[n]
	    return self.groups2addr[n]
	if n in self.nodegroups :
	    print "_get_node_id : " + n + " nodegroups " + n
	    return n
	print "_get_node_id : " + n + " None"
	return None

    def _get_command_id(self, comm):
	c = comm.upper()
	if c in self.controls :
	    return c
	if c in self.name2control :
	    return self.name2control[c]
	return None


    def node_set_prop(self, naddr, prop, val) :
	""" calls /rest/nodes/<node-id>/set/<property>/<value> """
	#if self.debug & 0x01 :
	print "node_set_prop"
	node_id = self._get_node_id(naddr)
	if not node_id :
	    raise LookupError("node_set_prop: unknown node : " + str(naddr) );
	if not prop in ['ST', 'OL', 'RR'] :
	    raise TypeError("node_set_prop: unknown propery : " + str(prop) );
	# if val :
	#	pass
	self._node_set_prop(naddr, prop, val)



    def node_comm(self, naddr, cmd, *args) :
	""" rest/nodes/<nodeid>/cmd/<command_name>/<param1>/<param2>/.../<param5>"""
	if self.debug & 0x04 :
	    print "node_comm"
	node_id = self._get_node_id(naddr)
	cmd_id = self._get_command_id(cmd)

	#print "self.controls :", self.controls
	#print "self.name2control :", self.name2control


	if not node_id :
	    raise LookupError("node_comm: unknown node : " + str(naddr) );
	print "naddr : ",  naddr , " : " , node_id

	if not cmd_id :
	    raise TypeError("node_comm: unknown command : " + str(cmd) );

	xurl = "/rest/nodes/" + node_id + "/cmd/" + cmd_id + "/" + "/".join(str(x) for x in args)

	if self.debug & 0x02 :
	    print "xurl = " + xurl

	resp = self._getXMLetree(xurl)

	if resp.attrib["succeeded"] != 'true' :
	    raise IsyResponseError("X10 command error : unit=" + str(unit) + " cmd=" +str(cmd))


    def _updatenode(self, naddr) :
	xurl = "/rest/nodes/" + self.nodedict[naddr]["address"]
	if self.debug & 0x01 :
	    print "_updatenode pre _getXML"
	_nodestat = self._getXMLetree(xurl)
	# del self.nodedict[naddr]["property"]["ST"]
	for prop in _nodestat.iter('property'):
	    tprop = dict ( )
	    for k, v in prop.items() :
		tprop[k] = v
	    if "id" in tprop :
		self.nodedict[naddr]["property"][tprop["id"]] = tprop


    # something is really broken with ETree 
    def load_conf(self) :
	""" configuration of the system with permissible commands """
	if self.debug & 0x01 :
	    print "load_conf pre _getXMLetree"
	self.configinfo = self._getXMLetree("/rest/config")
	# IsyClass._printXML(self.configinfo)
	# temp = self.configinfo.find('app_version').text
	# self.app_version = temp
	# print "app_version : " +  self.app_version

	self.name2control = dict ( ) 
	self.controls = dict ( ) 
	for ctl in self.configinfo.iter('control') :
	    # self._printXML(ctl)
	    # self._printinfo(ctl, "configinfo : ")
	    cprop = dict ( )

	    for child in ctl.iter():
		# print "child.tag " + str(child.tag) + "\t=" + str(child.text)
		if child.tag == "control" :
		    continue
		elif child.tag == "actions" :
		    #adict = ()
		    for act in child.iter('action') :
			pass
			# adict[act.tag] = act.text
			# self._printinfo(act, "action")
		    # cprop["actions"] = adict
		    continue
		else :
		    # self._printinfo(child, "child")
		    cprop[child.tag] = child.text

	    # print "cprop ", cprop
	    if "name" in cprop :
		self.controls[cprop["name"].upper()] = cprop
		if "label" in cprop :
		    self.name2control[cprop["label"].upper()] = cprop["name"].upper()

	# print "self.controls : ", self.controls
	self._printdict(self.controls)
	print "self.name2control : ", self.name2control

    def load_node_types(self) :
	if self.debug & 0x01 :
	    print "load_node_types called"
	typeinfo = self._getXMLetree("/WEB/cat.xml")
	self.nodeCategory = dict ()
	for ncat in typeinfo.iter('nodeCategory'):
	    if not ncat.attrib["id"] in self.nodeCategory :
		self.nodeCategory[ncat.attrib["id"]] = dict ()
	    self.nodeCategory[ncat.attrib["id"]]["name"] = ncat.attrib["name"]
	typeinfo = self._getXMLetree("/WEB/1_fam.xml")
	for ncat in typeinfo.iter('nodeCategory'):
	    for subcat in ncat.iter('nodeSubCategory'):
		if not ncat.attrib["id"] in self.nodeCategory :
		    self.nodeCategory[ncat.attrib["id"]] = dict ()
		self.nodeCategory[ncat.attrib["id"]][subcat.attrib["id"]] \
			    = subcat.attrib["name"]
		#self._printinfo(subcat, "subcat :")
	# print "nodeCategory : ", self.nodeCategory
	# self._printdict(self.nodeCategory)

	
    #
    # Climate Code
    #
    def load_vars(self) :
	self.vardict = dict ()
	self.name2var = dict ()
	for t in [ '1', '2' ] :
	    vinfo = self._getXMLetree("/rest/vars/get/" + t)
	    for v in vinfo.iter("var") :
		vdat = dict ()
		for vd in v.iter() :
		    if vd.tag != "var" :
			vdat[vd.tag] = vd.text
		self.vardict[t + ":" + v.attrib["id"]] = vdat 

	    vinfo = self._getXMLetree("/rest/vars/definitions/" + t)
	    for v in vinfo.iter("e") :
		# self._printinfo(v, "e :")
		self.vardict[t + ":" + v.attrib["id"]]['name'] = v.attrib['name']
		self.name2var[v.attrib['name']] = t + ":" + v.attrib["id"]

	# self._printdict(vdict)





    #
    # Climate Code
    #
    def load_clim(self) :
	if self.debug & 0x01 :
	    print "load_clim called"
	self.climateinfo = self._getXMLetree("/rest/climate")
	# IsyClass._printXML(self.climateinfo)

    def clim_query(self):
	try:
	    self.climateinfo
	except AttributeError:
	    self.load_clim()
	except:
	    print "Unexpected error:", sys.exc_info()[0]
	    return None

	try:
	    self.attribs
	except AttributeError:
	    self.attribs = { }
	    for child in self.climateinfo :
		#print(child.tag, child.text)
		self.attribs[child.tag] = child.text
	except:
	    print "Unexpected error:", sys.exc_info()[0]
	    return None
	finally:
	    return self.attribs

    #
    # X10 Code
    #
    x10re = re.compile('([a-pA-P]\d{,2)')
    x10comm={ 'alllightsoff' : 1,
	'status off' : 2,
	'on' : 3,
	'preset dim' : 4,
	'alllightson' : 5,
	'hail ack' : 6,
	'bright' : 7,
	'status on'  : 8,
	'extended code' : 9,
	'status request' : 10,
	'off' : 11,
	'preset dim' : 12,
	'alloff' : 13,
	'Hail Req' : 14,
	'dim' : 15,
	'extended data' : 16
    }
 
    def _get_x10_comm_id(self, comm) :
	comm = str(comm).lower()
	if comm.isdigit() :
	    if int(comm) >= 1 and int(comm) <= 16 : 
		return comm
	    else :
		raise ValueError("bad x10 command digit : "  + comm) ;
	if comm in self.x10comm :
	    return self.x10comm[comm]
	else :
	    raise ValueError("unknown x10 command : " + comm );
	

    def x10_comm(self, unit, cmd) :
        xcmd = self._get_x10_comm_id(str(cmd))
	unit = unit.upper()

	if not re.match("[A-P]\d{,2}", unit) :
	    raise ValueError("bad x10 unit name : "  + unit) ;

	print "X10 sent : " + str(unit) +  " : " + str(xcmd)
	xurl = "/rest/X10/" + str(unit) + "/" + str(xcmd)
	resp = self._getXMLetree(xurl)
	#self._printXML(resp)
	#self._printinfo(resp)
	if resp.attrib["succeeded"] != 'true' :
	    raise IsyResponseError("X10 command error : unit=" + str(unit) + " cmd=" +str(cmd))



    def _printinfolist(self, uobj, ulabel="_printinfo"):
	print "\n\n" + ulabel + " : "
	for attr in dir(uobj) :
	    print "   obj.%s = %s" % (attr, getattr(uobj, attr))
	print "\n\n";
	


# def rate
# def onlevel
class IsyNode(IsyBaseClass):

    def __init__(self, isy, ndict) :
	if isinstance(ndict, dict):
	    self.nodedict = ndict
	else :
	    print "error : class IsyNode called without ndict"
	    raise TypeError("IsyNode: called without ndict");

	if isinstance(isy, IsyBaseClass):
	    self.isy = isy
	    self.debug = isy.debug
	else :
	    print "error : class IsyNode called without isyBaseClass"
	    raise TypeError("IsyNode: isy is wrong class");

	self.update()
	print "Init Node : " + self.nodedict["address"] + \
	    " : " + self.nodedict["name"]
	self._printdict(self.nodedict)


    # generic property get / set
    def _get_prop(self, prop):
	# print "----get_status call"
	try:
	    self.nodedict["property"][prop]
	except:
	    # AttributeError
	    print "_get_prop AttributeError"
	    raise AttributeError("no Attribute " + prop)
	finally:
	    return self.nodedict["property"][prop]["value"]

    def _set_prop(self, prop, new_value):
	if self.debug & 0x04 :
	    print "_set_prop " , prop , " : " , new_value

	if not str(new_value).isdigit :
	    TypeError("Set Property : Bad Value : node=%s prop=%s val=%s" % \
		self.nodedict["address"], prop, str(val))

	self.isy._node_set_prop(self.nodedict["address"], prop, str(new_value))

	try:
	    self.nodedict["property"][prop]
	except:
	    pass
	    #print "_set_prop AttributeError"
	    #raise AttributeError("no Attribute " + prop)
	else:
	    if isinstance(new_value, (long, int, float))  :
		self.nodedict["property"][prop]["value"] = new_value

	# exception TypeError
	# print "set_status NOT VALID: ", new_value
	# raise NameError('New Val not a number')


    # ramprate property
    # obj mathod for getting/setting a Node's value 
    # sets how fast a light fades on.
    def get_rr(self):
	return self._get_prop("RR");
    def set_rr(self, new_value):
	return self._set_prop("RR", new_value);
    ramprate = property(get_rr, set_rr)

    # On Level property
    # obj mathod for getting/setting a Node's value 
    # where in most cases light is how bright the light is
    # when turned on
    def get_ol(self):
	return self._get_prop("OL");
    def set_ol(self, new_value):
	return self._set_prop("OL", new_value);
    onlevel = property(get_ol, set_ol)

    # status property
    # obj mathod for getting/setting a Node's value 
    # where in most cases light is how bright the light is
    def get_status(self):
	return self._get_prop("ST");
    def set_status(self, new_value):
	return self._set_prop("ST", new_value);
    status = property(get_status, set_status)


    # all read to node attribute
    # but not write
    def _getaddr(self):
	return self.nodedict["address"]
    address = property(_getaddr)

    def _getname(self):
	return self.nodedict["name"]
    name = property(_getname)

    #
    #
    # direct (non obj) call to get value
    #
    def value(self) :
	try:
	    self.nodedict["property"]["ST"]["value"]
	except:
	    return None
	else:
	    return self.nodedict["property"]["ST"]["value"]

    # direct (non obj) call to set value
    def svalue(self, v) :
	try:
	    self.nodedict["property"]["ST"]["value"]
	except:
	    return None
	else:
	    self.nodedict["property"]["ST"]["value"] = v


    #
    #
    #

    def update(self) :
	xurl = "/rest/nodes/" + self.nodedict["address"]
	if self.debug & 0x01 :
	    print "_updatenode pre _getXML"
	_nodestat = self.isy._getXMLetree(xurl)
	# del self.nodedict["property"]["ST"]
	for prop in _nodestat.iter('property'):
	    tprop = dict ( )
	    for k, v in prop.items() :
		tprop[k] = v
	    if "id" in tprop :
		self.nodedict["property"][tprop["id"]] = tprop


    # The following is experimental

    def __nonzero__(self) :
	print "__nonzero__ call" , self.nodedict["property"]["ST"]["value"], \
		 " :: ",  int(self.nodedict["property"]["ST"]["value"])
	return  ( int(self.nodedict["property"]["ST"]["value"]) > 0 )

#    def __get__(self, instance, owner):
#	print "__get__ call"
#	return self.nodedict["property"]["ST"]["value"]

#    def __set__(self, instance, value):
#	print "__set__ call"

#    def __str__(self):
#	print "__str__ call"
#	return  ( "my str : " + self.nodedict["name"] )


    def __float__(self):
	# print "__float__ call"
	return   float ( int(self.nodedict["property"]["ST"]["value"]) / float(255) )


# __invert__(self)





if __name__ == "__main__":
    print("ISY.py syntax ok")
