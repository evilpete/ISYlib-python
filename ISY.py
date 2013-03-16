
"""Simple Python lib for the ISY home automation netapp

 This is a Python interface to the ISY rest interface
 providomg simple commands to query and control registared Nodes and Scenes
 and well as a method of setting or querying vars
 
"""

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
import time
import warnings

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


#
# The Following was lifted from other modules used as examples
#
class IsyError(Exception):
    """Base exception."""
    def __init__(self, msg, exception=None):
        """Creates an exception. The message is required, but the exception
        is optional."""
        self._msg = msg
        self._exception = exception
        Exception.__init__(self, msg)

    def getMessage(self):
        "Return a message for this exception."
        return self._msg

    def getException(self):
        "Return the embedded exception, or None if there was none."
        return self._exception

    def __str__(self):
        "Create a string representation of the exception."
        return self._msg

    def __getitem__(self, ix):
        """Avoids weird error messages if someone does exception[ix] by
        mistake, since Exception has __getitem__ defined."""
        raise AttributeError("__getitem__")


class IsyCommandError(IsyError):
    """General exception for command errors."""
    pass

class IsyNodeError(IsyError):
    """General exception for Node errors."""
    pass

class IsyResponseError(IsyError):
    """General exception for Node errors."""
    pass

class IsyPropertyError(IsyError):
    """General exception for Node errors."""
    pass

class IsyValueError(IsyError):
    """General exception for Node errors."""
    pass

#
# Simple Base class for ISY Class
#
class IsyBaseClass(object):
    def __init__(self) :
        self.debug = 0
        # self.pp = pprint.PrettyPrinter(indent=4)


    def _printXML(self, xml):
        """ Pretty Print XML """
        print "_printXML start"
        ET.dump(xml)

    def _getXMLetree(self, xmlpath):
        """ take a URL path, download XLM and return parsed Etree """
        xurl = self.baseurl + URL.quote(xmlpath)
        if self.debug & 0x02:
            print "_getXMLetree : " + xurl
        # print "_getXMLetree : URL.Request"
        req = URL.Request(xurl)
        # print "_getXMLetree : self.opener.open "
        res = IsyClass.opener.open(req)
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
            self.pp.pprint(d)

    def _printinfo(self, uobj, ulabel="\t"):
        print "%s: tag=%s text=%s attr=%s : atype=%s : type=%s" % (ulabel, uobj.tag, uobj.text, uobj.attrib, type(uobj.attrib), type(uobj))



# if hasattr(instance, 'tags') and isinstance(instance.tags, dict):
#     for tag in instance.tags:

# def batch .write

class IsyClass(IsyBaseClass):
    """ Obj class the represents the ISY device """
    password_mgr = URL.HTTPPasswordMgrWithDefaultRealm()
    handler = URL.HTTPBasicAuthHandler(password_mgr)
    opener = URL.build_opener(handler)

    def __init__(self, isyaddr='', userl="admin", userp="admin", **kwargs):
        #
        # Keyword args
        #
	self.debug = kwargs.get("debug", 0)
	self.cachetime = kwargs.get("cachetime", 0)
	self.faststart = kwargs.get("faststart", 1)

        if self.debug & 0x01 :
            print "class IsyClass __init__"
            print "debug ", self.debug
            print "cachetime ", self.cachetime
            print "faststart ", self.faststart

	# parse   ISY_AUTH as   LOGIN:PASS

        #
        # general setup logic
        #
        self.addr = isyaddr or os.getenv('ISY_ADDR', '10.1.1.36')
        self.baseurl = "http://" + self.addr
        IsyClass.handler.add_password(None, self.addr, userl, userp)
        # self.opener = URL.build_opener(IsyClass.handler, URL.HTTPHandler(debuglevel=1))
        # self.opener = URL.build_opener(IsyClass.handler)
        if self.debug & 0x02:
	    print "baseurl: " + self.baseurl + " : " + userl + " : " + userp
        if not self.faststart :
            self.load_conf()
        #
        self.nodeCdict = dict ()
        self.varCdict = dict ()

    def _preload_all(self):
        self.load_nodes()
        self.load_clim()
        self.load_conf()

    ##
    ## Load System config / info and command information
    ##
    def load_conf(self) :
        """ configuration of the system with permissible commands """
        if self.debug & 0x01 :
            print "load_conf pre _getXMLetree"
        self.configinfo = self._getXMLetree("/rest/config")
        # IsyClass._printXML(self.configinfo)

        self.name2control = dict ( )
        self.controls = dict ( )
        for ctl in self.configinfo.iter('control') :
            # self._printXML(ctl)
            # self._printinfo(ctl, "configinfo : ")
            cprop = dict ( )

            for child in list(ctl):
                # print "child.tag " + str(child.tag) + "\t=" + str(child.text)
                if child.tag == "actions" :
                    adict = dict ()
                    for act in child.iter('action') :
                        n = act.find('label').text
                        v = act.find('name').text
                        adict[n] = v
                    cprop[child.tag] = adict
                else :
                    # self._printinfo(child, "child")
                    cprop[child.tag] = child.text
            for n, v in child.items() :
                cprop[n] = v

            # print "cprop ", cprop
            if "name" in cprop :
                self.controls[cprop["name"].upper()] = cprop
                if "label" in cprop :
                    self.name2control[cprop["label"].upper()] \
			= cprop["name"].upper()

	self.config = dict ()
	for v in ( "platform", "app_version" ):
	    n = configinfo.find(v)
	    if not n is None:
		if isinstance(n.text, str):
		    self.config[v] = n.text

        # print "self.controls : ", self.controls
        #self._printdict(self.controls)
        #print "self.name2control : ", self.name2control

    ##
    ## property
    ##
    def _get_platform(self) :
	""" name of ISY platform (readonly) """
 	return self.config["platform"]
    platform = property(_get_platform)

    def _get_app_version(self) :
	""" name of ISY app_version (readonly) """
	return self.config["app_version"]
    app_version = property(_get_app_version)

    ##
    ## Node funtions
    ##
    def load_nodes(self) :
        """ Load node list scene list and folder info """
        self._nodedict = dict ()
        # self.nodeCdict = dict ()
        self.name2addr = dict ()
        if self.debug & 0x01 :
            print "load_nodes pre _getXML"
        nodeinfo = self._getXMLetree("/rest/nodes")
        self._gen_nodedict(nodeinfo)
        # self._gen_folder_list(nodeinfo)
        self._gen_nodegroups(nodeinfo)
        # self._printdict(self._nodedict)

    def _gen_folder_list(self, nodeinfo) :
        """ generate folder dictionary for load_node """
        self.folderlist = dict ()
        for fold in nodeinfo.iter('folder'):
            fprop = dict ()
            for child in list(fold):
                fprop[child.tag] = child.text
            self.folderlist[fprop["address"]] = fprop["name"]

    def _gen_nodegroups(self, nodeinfo) :
        """ generate scene / group dictionary for load_node """
        self._nodegroups = dict ()
        self.groups2addr = dict ()
        for grp in nodeinfo.iter('group'):
            gprop = dict ()
            for k, v in grp.items() :
                gprop[k] = v
            for child in list(grp) :
                if child.tag != "members" :
                    gprop[child.tag] = child.text
                else :
                    glist = [ ]
                    for lnk in child.iter('link'):
                        glist.append(lnk.text)
                    gprop[child.tag] = glist

            if "address" in gprop :
                self._nodegroups[gprop["address"]] = gprop
                if "name" in gprop :
                    self.groups2addr[gprop["name"]] = str(gprop["address"])
            else :
		# should raise an exception ?
                self._printinfo(grp, "Error : no address in group :")

    def _gen_nodedict(self, nodeinfo) :
        """ generate node dictionary for load_node """
        self._nodedict = dict ()
        for inode in nodeinfo.iter('node'):
            # self._printinfo(inode, "\n\n inode")
            idict = dict ()
            for k, v in inode.items() :
                idict[k] = v
            for child in list(inode) :
                # self._printinfo(child, "\tchild")

                if child.tag == "parent" :
                    idict[child.tag] = child.text
                    for k, v in child.items() :
                        idict[child.tag + "_" + k] = v
                elif child.tag == "property" :
                    nprop = dict ()
                    for k, v in child.items() :
                        # print "child.items",k,v
                        nprop[k] = v
                    if "id" in nprop :
                        idict[child.tag] = dict ()
                        idict[child.tag][nprop["id"]] = nprop
                else :
                    idict[child.tag] = child.text

            if "address" in idict :
                self._nodedict[idict["address"]] = idict
                if "name" in idict :
		    if idict["name"] in self.name2addr :
			warning.warn("Duplicate Node Name", RuntimeWarning)
		    else :
			self.name2addr[idict["name"]] = idict["address"]

            else :
		# should raise an exception
                # self._printinfo(inode, "Error : no address in node :")
		warning.warn("Error : no address in node", RuntimeWarning)
        #print "\n>>>>\t", self._nodedict, "\n<<<<<\n"

# if hasattr(instance, 'tags') and isinstance(instance.tags, dict):
#     for tag in instance.tags:


    #
    # access methods to Node data
    #
    def node_names(self) :
        """  access method for node names
            returns a dict of ( Node names : Node address )
	"""
        try:
            self.name2addr
        except AttributeError:
            self.load_nodes()
        finally:
            return self.name2addr

    def scene_names(self) :
        """ access method for scene names
            returns a dict of ( Node names : Node address ) """
        try:
            self.groups2addr
        except AttributeError:
            self.load_nodes()
        finally:
            return self.groups2addr

    def node_addrs(self) :
        """ access method for node addresses
            returns a iist scene/group addresses """
        try:
            self._nodedict
        except AttributeError:
            self.load_nodes()
        finally:
            return self._nodedict.keys()

    def scene_addrs(self) :
        """ access method for scene addresses
            returns a iist scene/group addresses """
        try:
            self._nodegroups
        except AttributeError:
            self.load_nodes()
        finally:
            return self._nodegroups.keys()


    def get_node(self, node_id) :
        """
	Get a Node object for given node or scene name or ID

        :type node_id: str
	:param owners: unique name or ID of request node or scene
		
	:rtype: :class:`IsyNode`
	:return: An IsyNode object representing the requested Scene or Node
	"""
        if self.debug & 0x01 :
            print "get_node"
        try:
            self._nodedict
        except AttributeError:
            self.load_nodes()
#       except:
#           print "Unexpected error:", sys.exc_info()[0]
#           return None
        finally:
            nodeid = self._get_node_id(node_id)
            if nodeid in self._nodedict :
                if not nodeid in self.nodeCdict :
                    self.nodeCdict[nodeid] = IsyNode(self, self._nodedict[nodeid])
                return self.nodeCdict[nodeid]
            elif nodeid in self._nodegroups:
                if not nodeid in self.nodeCdict :
                    self.nodeCdict[nodeid] = IsyNode(self, self._nodegroups[nodeid])
                return self.nodeCdict[nodeid]
            else :
                print "IsyClass get_node no node : \"%s\"" % nodeid
                raise LookupError("no node such Node : " + str(nodeid) )


    def _get_node_id(self, nid):
        """ node/scene name to node/scene ID """
        n = str(nid)
        if string.upper(n) in self._nodedict :
            # print "_get_node_id : " + n + " nodedict " + string.upper(n)
            return string.upper(n)
        if n in self.name2addr :
            # print "_get_node_id : " + n + " name2addr " + self.name2addr[n]
            return self.name2addr[n]
        if n in self.groups2addr :
            # print "_get_node_id : " + n + " groups2addr " + self.groups2addr[n]
            return self.groups2addr[n]
        if n in self._nodegroups :
            # print "_get_node_id : " + n + " nodegroups " + n
            return n
        print "_get_node_id : " + n + " None"
        return None

    def _get_command_id(self, comm):
        """ command name to command ID """
        c = comm.upper()
        if c in self.controls :
            return c
        if c in self.name2control :
            return self.name2control[c]
        return None


    #
    # Set 'ST', 'OL', 'RR' property for a node
    #
    def node_set_prop(self, naddr, prop, val) :
        """ calls /rest/nodes/<node-id>/set/<property>/<value> """
        #if self.debug & 0x01 :
        print "node_set_prop"
        node_id = self._get_node_id(naddr)
        if not node_id :
            raise LookupError("node_set_prop: unknown node : " + str(naddr) )
        if not prop in ['ST', 'OL', 'RR'] :
            raise TypeError("node_set_prop: unknown propery : " + str(prop) )
        # if val :
        #       pass
        self._node_set_prop(naddr, prop, val)

    def _node_set_prop(self, naddr, prop, val) :
        """ node_set_prop without argument validation """
        #print "_node_set_prop : node=%s prop=%s val=%s" % str(naddr), prop, val
        print ("_node_set_prop : node=" + str(naddr) + " prop=" + prop +
		    " val=" + val )
        xurl = "/rest/nodes/" + naddr + "/set/" + prop + "/" + val
        resp = self._getXMLetree(xurl)
        if resp.attrib["succeeded"] != 'true' :
            raise IsyResponseError("Node Property Set error : node=%s prop=%s val=%s" %
		    naddr, prop, val )


    #
    # Send command to Node/Scene
    #
    def node_comm(self, naddr, cmd, *args) :
        """ send command to a node or scene """
        if self.debug & 0x04 :
            print "node_comm"
        node_id = self._get_node_id(naddr)
        cmd_id = self._get_command_id(cmd)

        #print "self.controls :", self.controls
        #print "self.name2control :", self.name2control

        if not node_id :
            raise LookupError("node_comm: unknown node : " + str(naddr) )
        print "naddr : ", naddr, " : ", node_id

        if not cmd_id :
            raise TypeError("node_comm: unknown command : " + str(cmd) )

        self._node_comm(node_id, cmd_id, args)

    #
    # Send command to Node without all the arg checking
    #
    def _node_comm(self, node_id, cmd_id, *args) :
        """ send command to a node or scene without name to ID overhead """
        # rest/nodes/<nodeid>/cmd/<command_name>/<param1>/<param2>/.../<param5>
        xurl = ("/rest/nodes/" + node_id + "/cmd/" + cmd_id +
	    "/" + "/".join(str(x) for x in args) )

        if self.debug & 0x02 :
            print "xurl = " + xurl
        resp = self._getXMLetree(xurl)
        self._printXML(resp)
        if resp.attrib["succeeded"] != 'true' :
            raise IsyResponseError("ISY command error : node_id=" +
		str(node_id) + " cmd=" + str(cmd_id))


    # redundant
    def _updatenode(self, naddr) :
        """ update a node's property from ISY device """
        xurl = "/rest/nodes/" + self._nodedict[naddr]["address"]
        if self.debug & 0x01 :
            print "_updatenode pre _getXML"
        _nodestat = self._getXMLetree(xurl)
        # del self._nodedict[naddr]["property"]["ST"]
        for prop in _nodestat.iter('property'):
            tprop = dict ( )
            for k, v in prop.items() :
                tprop[k] = v
            if "id" in tprop :
                self._nodedict[naddr]["property"][tprop["id"]] = tprop
        self._nodedict[naddr]["property"]["time"] = time.gmtime()



    ##
    ##  Node Type
    ##
    def load_node_types(self) :
        """ Load node type info into a multi dimentional dictionary """
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
		# print "ID : ", ncat.attrib["id"], " : ", subcat.attrib["id"]
		# print "ID  name: ", subcat.attrib["name"]
		self.nodeCategory[ncat.attrib["id"]][subcat.attrib["id"]] = subcat.attrib["name"]
                #self._printinfo(subcat, "subcat :")
        # print "nodeCategory : ", self.nodeCategory
        # self._printdict(self.nodeCategory)

    def node_get_type(self, typid) :
        """ Take a node's type value and returns a string idnentifying the device """
        try:
            self.nodeCategory
        except :
            self.load_node_types()
        #
        # devcat = "UNKNOWN"
        # subcat = "UNKNOWN"
        #
        a = typid.split('.')
        #
        if len(a) >= 2 :
            devcat = a[0]
            subcat = a[1]
            if self.nodeCategory[a[0]] :
                devcat = self.nodeCategory[a[0]]["name"]
                if self.nodeCategory[a[0]][a[1]] :
                    subcat = self.nodeCategory[a[0]][a[1]].replace('DEV_CAT_', '')
        else :
            devcat = typid
            subcat = ""
        #
        return (devcat, subcat)

    ##
    ## variable funtions
    ##
    def load_vars(self) :
        """ Load variable names and values """
        self._vardict = dict ()
        self.name2var = dict ()
        for t in [ '1', '2' ] :
            vinfo = self._getXMLetree("/rest/vars/get/" + t)
            for v in vinfo.iter("var") :
                vdat = dict ()
                for vd in list(v) :
                    if vd.tag != "var" :
                        vdat[vd.tag] = vd.text
                self._vardict[t + ":" + v.attrib["id"]] = vdat
	    # self._printdict(self._vardict)

            vinfo = self._getXMLetree("/rest/vars/definitions/" + t)
            for v in vinfo.iter("e") :
                # self._printinfo(v, "e :")
		id = t + ":" + v.attrib["id"]
                self._vardict[id]['name'] = v.attrib['name']
                self._vardict[id]["id"] = id
                self.name2var[v.attrib['name']] = id

        # self._printdict(self._vardict)


    def var_set_value(self, var, val, prop="val") :
        """ Set var value by name or ID """
        if self.debug & 0x04 :
            print "var_set_value ", val, " : ", prop
	varid = self._var_get_id(var)
        if not varid :
            raise LookupError("var_set_value: unknown var : " + str(var) )
        if not prop in ['init', 'val'] :
	    raise TypeError("var_set_value: unknown propery : " + str(prop) )
	_var_set_value(self, varid, val, prop)

    def _var_set_value(self, varid, val, prop) :
        """ Set var value by name or ID """
        if self.debug & 0x04 :
            print "_var_set_value ", val, " : ", prop
	a = varid.split(':')
	if prop == "init" :
	    xurl = "/vars/init/" + a[0] + "/" + a[1] + "/" + val
	else :
	    xurl = "/vars/set/" + a[0] + "/" + a[1] + "/" + val
        resp = self._getXMLetree(xurl)
        if resp.attrib["succeeded"] != 'true' :
            raise IsyResponseError("Var Value Set error : var=%s prop=%s val=%s" %
		    varid, prop, val )
        self._printdict(self._vardict[varid])
	self._vardict[varid][prop] = val
        self._printdict(self._vardict[varid])
	return

    def var_get_value(self, var, prop) :
        """ Get var value by name or ID """
        pass


#    def var_names(self) :
#        pass


    def var_addrs(self)  :
        """ access method for var addresses
            returns a iist scene/group addresses """
        return self.name2var


    def get_var(self, vname) :
        """ get var class obj """
	print "get_var :" + vname
        if self.debug & 0x01 :
            print "get_var"
        try:
            self._vardict
        except AttributeError:
            self.load_vars()
#       except:
#           print "Unexpected error:", sys.exc_info()[0]
#           return None
        finally:
            varid = self._var_get_id(vname)
	    print "\tvarid : " + varid
            if varid in self._vardict :
                if not varid in self.varCdict :
		    print "not varid in self.varCdict:"
		    self._printdict(self._vardict[varid])
                    self.varCdict[varid] = IsyVar(self, self._vardict[varid])
		#self._printdict(self._vardict)
		print "return : ",
		#self._printdict(self.varCdict[varid])
                return self.varCdict[varid]
            else :
                print "IsyClass get_var no var : \"%s\"" % varid
                raise LookupError("no var : " + str(varid) )


    def _var_get_id(self, vname):
        """ Lookup var value by name or ID
	returns ISY Id  or None
	"""
        v = str(vname)
        if string.upper(v) in self._vardict :
            print "_get_var_id : " + v + " vardict " + string.upper(v)
            return string.upper(v)
        if v in self.name2var :
            print "_var_get_id : " + v + " name2var " + self.name2var[v]
            return self.name2var[v]

        print "_var_get_id : " + n + " None"
        return None

    def var_get_type(self, vtype) :
	return "VART"


    ##
    ## Climate funtions
    ##
    def load_clim(self) :
        """ Load climate data from ISY device """
        if self.debug & 0x01 :
            print "load_clim called"
        clim_tree = self._getXMLetree("/rest/climate")
        # IsyClass._printXML(self.climateinfo)
        self.climateinfo = dict ()
        for cl in clim_tree.iter("climate") :
            for k, v in cl.items() :
                self.climateinfo[k] = v
            for ce in list(cl):
                self.climateinfo[ce.tag] = ce.text
        self.climateinfo["time"] = time.gmtime()

    def clim_get_val(self, prop):
	pass

    def clim_query(self):
        """ returns dictionary of climate info """
        try:
            self.climateinfo
        except AttributeError:
            self.load_clim()

        #
        # ADD CODE to check self.cachetime
        #
        return self.climateinfo

    ##
    ## WOL (Wake on LAN) funtions
    ##
    def load_wol(self) :
        """ Load Wake On LAN IDs """
        if self.debug & 0x01 :
            print "load_wol called"
        wol_tree = self._getXMLetree("/rest/networking/wol")
        self.wolinfo = dict ()
        self.name2wol = dict ()
        for wl in wol_tree.iter("NetRule") :
            wdict = dict ()
            for k, v in cl.items() :
                wdict[k] = v
            for ce in list(cl):
                wdict[ce.tag] = ce.text
            if "id" in wdict :
                self.wolinfo[str(wdict["id"])] = wdict
                self.name2wol[wdict["name"].upper()] = wdict["id"]
        self._printdict(self.wolinfo)
        self._printdict(self.name2wol)

    def wol(self, wid) :
        """ Send Wake On LAN to registared wol ID """
        wid = str(wid).upper()
        if wid in self.wolinfo :
            wol_id = wid
        elif wid in self.name2wol :
            wol_id = self.name2wol[wid]
        else :
            raise IsyValueError("bad wol ID : " + wid)

	xurl = "/rest/networking/wol/" + wid_id

        if self.debug & 0x02 :
            print "wol : xurl = " + xurl
        resp = self._getXMLetree(xurl)
        self._printXML(resp)
        if resp.attrib["succeeded"] != 'true' :
            raise IsyResponseError("ISY command error : cmd=wol wol_id=" \
		+ str(wol_id))

    def name2wol(self, name) :
	pass

    def wol_names(self, vname) :
	"""
	method to retrieve a list of WOL names
	:type wolname: string
	:param wolname: the WOL name or ISY Id
	:rtype: list
        :return: List of WOL names and IDs or None
	"""
	pass

    ##
    ## X10 Code
    ##
    x10re = re.compile('([a-pA-P]\d{,2)')
    x10comm = { 'alllightsoff' : 1,
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
        'extended data' : 16 }

    def _get_x10_comm_id(self, comm) :
        """ X10 command name to id """
        comm = str(comm).lower()
        if comm.isdigit() :
            if int(comm) >= 1 and int(comm) <= 16 :
                return comm
            else :
                raise IsyValueError("bad x10 command digit : " + comm)
        if comm in self.x10comm :
            return self.x10comm[comm]
        else :
            raise IsyValueError("unknown x10 command : " + comm)


    def x10_comm(self, unit, cmd) :
        """ direct send x10 command """
        xcmd = self._get_x10_comm_id(str(cmd))
        unit = unit.upper()

        if not re.match("[A-P]\d{,2}", unit) :
            raise IsyValueError("bad x10 unit name : " + unit)

        print "X10 sent : " + str(unit) + " : " + str(xcmd)
        xurl = "/rest/X10/" + str(unit) + "/" + str(xcmd)
        resp = self._getXMLetree(xurl)
        #self._printXML(resp)
        #self._printinfo(resp)
        if resp.attrib["succeeded"] != 'true' :
            raise IsyResponseError("X10 command error : unit=" + str(unit) + " cmd=" + str(cmd))


    ##
    ## support funtions
    ##
    def _printinfolist(self, uobj, ulabel="_printinfo"):
        print "\n\n" + ulabel + " : "
        for attr in dir(uobj) :
            print "   obj.%s = %s" % (attr, getattr(uobj, attr))
        print "\n\n"


    ##
    ## Special Methods
    ##

    # Design question :
    # should __get/setitem__  return a node obj or a node's current value ?
    def __getitem__(self, nodeaddr):
        """ access a node as dictionary entery """
        if nodeaddr in self.nodeCdict :
            return self.nodeCdict[str(nodeaddr).upper()]
        else :
            return self.get_node(nodeaddr)

    def __setitem__(self, nodeaddr, val):
        # print "__setitem__ : ", nodeaddr, " : ", val
	self.node_set_prop(nodeaddr, val, "ST")

    def __delitem__(self, nodeaddr):
        raise IsyProperyError("__delitem__ : can't delete nodes :  " + str(prop) )
        pass

    def __iter__(self):
        try:
            self._nodedict
        except AttributeError:
            self.load_nodes()
	k = self._nodedict.keys()
	k.extend(self._nodegroups.keys())
	for n in k :
	    yield self.get_node(n)

    def __repr__(self):
        return "<IsyClass %s at 0x%x>" % (self.addr, id(self))



    # def rate
    # def onlevel
class IsyNode(IsyBaseClass):
    """ Node Class for ISY
	attributes :
	ramprate onlevel status address name type members
    """

    def __init__(self, isy, ndict) :
        if isinstance(ndict, dict):
            self._nodedict = ndict
        else :
            print "error : class IsyNode called without ndict"
            raise TypeError("IsyNode: called without ndict")

        if isinstance(isy, IsyBaseClass):
            self.isy = isy
            self.debug = isy.debug
        else :
            print "error : class IsyNode called without isyBaseClass"
            raise TypeError("IsyNode: isy is wrong class")
        # only update if not a scene
        if not (int(self._nodedict["flag"]) & 0x04) :
            self.update()

        if self.debug & 0x01 :
	    print "Init Node : \"" + self._nodedict["address"] + \
		"\" : \"" + self._nodedict["name"] + "\""
        #self._printdict(self._nodedict)


    def _get_node_prop(self, prop):
        """  generic property get """
        # print "----get_status call"

	if prop == "formatted" :
	    prop = "ST"
	    value = "formatted"
	else :
	    value = "value"

        # Scene's do not have property values
        if int(self._nodedict["flag"]) & 0x04 :
            return None

        # check if we have a property
        try:
            self._nodedict["property"][prop]
        except:
            # print "_get_node_prop AttributeError"
            raise IsyPropertyError("no property Attribute " + prop)
        finally:
	    pass
#            if self._nodedict["property"]["time"] == 0 :
#                    self.update()
#            elif self.isy.cachetime :
#                if time.gmtime() < ( self.cachetime + self._nodedict["property"]["time"] ) :
#                    self.update()
            return self._nodedict["property"][prop][value]

    def _set_node_prop(self, prop, new_value):
        """  generic property set """
        if self.debug & 0x04 :
            print "_set_node_prop ", prop, " : ", new_value

        if not str(new_value).isdigit :
            TypeError("Set Property : Bad Value : node=%s prop=%s val=%s" %
				    self._nodedict["address"], prop, str(val))

        self.isy._node_set_prop(self._nodedict["address"], prop, str(new_value))

        self._nodedict["property"]["time"] = 0

        try:
            self._nodedict["property"][prop]
        except:
            pass
            #print "_set_node_prop AttributeError"
            #raise AttributeError("no Attribute " + prop)
        else:
            if isinstance(new_value, (long, int, float))  :
                self._nodedict["property"][prop]["value"] = new_value

        # exception TypeError
        # print "set_status NOT VALID: ", new_value
        # raise NameError('New Val not a number')


    # ramprate property
    # obj mathod for getting/setting a Node's value
    # sets how fast a light fades on.
    def get_node_rr(self):
	"""
	Get RampRate property of Node
	:rtype: str
        :return: RampRate value
	"""
        return self._get_node_prop("RR")

    def set_node_rr(self, new_value):
	"""
	set_node_rr : Get/Set RampRate property of Node
	"""
        return self._set_node_prop("RR", new_value)

    ramprate = property(get_node_rr, set_node_rr)
    """
    ramprate Get/Set RampRate property of Node
    """

    # On Level property
    # obj mathod for getting/setting a Node's value
    # where in most cases light is how bright the light is
    # when turned on
    def get_node_ol(self):
	""" property On Level Value of Node """
        return self._get_node_prop("OL")

    def set_node_ol(self, new_value):
        return self._set_node_prop("OL", new_value)
    onlevel = property(get_node_ol, set_node_ol)


    def get_node_fm(self):
	""" property On Level Value of Node """
        return self._get_node_prop("formatted")
    formatted = property(get_node_fm)

    # status property
    # obj mathod for getting/setting a Node's value
    # where in most cases light is how bright the light is
    def get_node_status(self):
	""" property status value of Node """
        return self._get_node_prop("ST")

    def set_node_status(self, new_value):
        return self._set_node_prop("ST", new_value)

    status = property(get_node_status, set_node_status)
    """  returns status of Node """


    #
    # readonly to node attribute
    #
    def _getaddr(self):
        return self._nodedict["address"]
    address = property(_getaddr)

    def _getname(self):
	""" property : Name of Node (readonly) """
        return self._nodedict["name"]
    name = property(_getname)

    def _gettype(self):
        if "type" in self._nodedict :
            return self._nodedict["type"]
        elif int(self._nodedict["flag"]) & 0x04 :
            return "scene"
        else :
            return "_gettype : ERROR"
    type = property(_gettype)

    def _getmembers(self) :
	""" property : List members of a scene or group """
        if "members" in self._nodedict :
            return self._nodedict["members"]
        else :
            return None
    members = property(_getmembers)
    """
    Get members list for Scene
    :rtype: list
    :return: list of Nodes
    """

    def scene_nodes(self) :
        pass

    def pdict(self):
        self._printdict(self._nodedict)


    #
    #
    # direct (non obj) call to get value
    #
    def value(self) :
        try:
            return self._nodedict["property"]["ST"]["value"]
        except:
            return None
        #else:
        #    return self._nodedict["property"]["ST"]["value"]

    # direct (non obj) call to set value
    def svalue(self, v) :
        try:
            self._nodedict["property"]["ST"]["value"]
        except:
            return None
        else:
            self._nodedict["property"]["ST"]["value"] = v


    def on(self) :
        self.isy._node_comm(self._nodedict["address"], "DON")
        try :
            self._nodedict["property"]["time"] = 0
        except :
            pass
        # self.update()

    def off(self) :
        self.isy._node_comm(self._nodedict["address"], "DOF")

        try :
            self._nodedict["property"]["ST"]["value"] = 0
            self._nodedict["property"]["time"] = 0
        except:
            pass


    def beep(self) :
        self.isy._node_comm(self._nodedict["address"], "BEEP")
        pass

    #
    #
    #
    def update(self) :
        xurl = "/rest/nodes/" + self._nodedict["address"]
        if self.debug & 0x01 :
            print "_updatenode pre _getXML"
        _nodestat = self.isy._getXMLetree(xurl)
        # del self._nodedict["property"]["ST"]
        for prop in _nodestat.iter('property'):
            tprop = dict ( )
            for k, v in prop.items() :
                tprop[k] = v
            if "id" in tprop :
                self._nodedict["property"][tprop["id"]] = tprop
        # self._nodedict["property"]["time"] = time.gmtime()

    def __getitem__(self, prop):
	return self._get_node_prop(prop)

    def __setitem__(self, prop, val):
        if not prop in ['ST', 'OL', 'RR'] :
            raise IsyProperyError("__setitem__: unknown propery : " + str(prop) )
        self._set_prop(prop, val)
        # self._nodedict["property"]["time"] = 0

    def __delitem__(self, prop):
        raise IsyProperyError("__delitem__ : can't delete propery :  " + str(prop) )

    # The following is experimental

    def __nonzero__(self) :
        #print "__nonzero__ call", self._nodedict["property"]["ST"]["value"], \
        #        " :: ", int(self._nodedict["property"]["ST"]["value"])
        return ( int(self._nodedict["property"]["ST"]["value"]) > 0 )

    def __get__(self, instance, owner):
        print "__get__ call"
        return self.value()

    def __set__(self, instance, value):
        print "__set__ call"
        self._set_prop("ST", val)


#    def __str__(self):
#       print "__str__ call"
#       return ( "my str : " + self._nodedict["name"] )

    def __repr__(self):
        return "<IsyNode %s @ %s at 0x%x>" % (self._nodedict["address"], self.isy.addr, id(self))

    def __float__(self):
        # print "__float__ call"
        return float ( int(self._nodedict["property"]["ST"]["value"]) / float(255) )


class IsyVar(IsyBaseClass):
    """ VAR Class for ISY
	attributes : status name init ts id
    """

    def __init__(self, isy, vdict) :
	""" INIT IsyVar """

        if isinstance(vdict, dict):
            self._mydict = vdict
        else :
            print "error : class IsyVar called without vdict"
            raise IsyValueError("IsyVar: called without vdict")

        if isinstance(isy, IsyClass):
            self.isy = isy
            self.debug = isy.debug
        else :
            print "error : class IsyNode called without IsyClass"
            raise TypeError("IsyNode: isy is wrong class")
	print "IsyVar: ",
        self._printdict(self._mydict)


    def _get_var_prop(self, prop):
	pass
    def _set_var_prop(self, prop):
	pass

    def get_var_ts(self):
	""" returns var timestamp
	this is also avalible via the property : ts
	"""
	return(self._mydict["ts"])
    ts = property(get_var_ts)

    def get_var_type(self):
	""" returns var timestamp
	this is also avalible via the property : type
	"""
	a = self._mydict["id"].split(':')
	return(a[1])
    type = property(get_var_type)

    def get_var_init(self):
	""" returns var init value
	this is also avalible via the property : init
	"""
	return(self._mydict["init"])
    def set_var_init(self, new_value):
	""" sets var init value
	this can also be set via the property : init
	"""
	pass
    init = property(get_var_init, set_var_init)
    """ init property
    this value can also be read or set
    """

    def get_var_value(self):
	""" returns var value
	this is also avalible via the property : value
	"""
	return(self._mydict["val"])
    def set_var_value(self, new_value):
	""" sets var value
	this can also be set via the property : value
	"""
	pass
    value = property(get_var_value, set_var_value)
    """ value property
    this can also be read or set
    """

    def get_var_id(self):
	return(self._mydict["id"])
    id = property(get_var_id)

    def get_var_name(self):
	return(self._mydict["name"])
    name = property(get_var_name)

    def __getitem__(self, prop):
	pass
    def __setitem__(self, prop):
	pass
    def __delitem__(self, prop):
	pass

    def __get__(self, instance, owner):
	pass
    def __set__(self, instance, owner):
	pass

#    def __repr__(self):
#	pass

#
# Do nothing
# (syntax check)
#
if __name__ == "__main__":
    print("ISY.py syntax ok")
    exit(0)
