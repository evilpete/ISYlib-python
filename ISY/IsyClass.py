"""Simple Python lib for the ISY home automation netapp

 This is a Python interface to the ISY rest interface
 providomg simple commands to query and control registared Nodes and Scenes
 and well as a method of setting or querying vars
 
"""

from IsyExceptionClass import *

#from xml.dom.minidom import parse, parseString
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

from IsyUtilClass import *
from IsyNodeClass import *
from IsyProgramClass import *
from IsyVarClass import *
from IsyExceptionClass import *
from IsyEvent import ISYEvent

# Debug Flags:
# 0x01 = report loads
# 0x02 = report urls used
# 0x04 = report func call
# 0x08 = Dump loaded data
# 0x10 = report changes to nodes
# 0x20 =
# 0x40 =
# 0x80 =
#

__all__ = ['Isy']



# if hasattr(instance, 'tags') and isinstance(instance.tags, dict):
#     for tag in instance.tags:

# def batch .write


# _nodedict	dictionary of node data indexed by node ID
# node2addr	dictionary mapping node names to node ID
# nodeCdict	dictionary cache or node objects indexed by node ID


class Isy(IsyUtil):
    """ Obj class the represents the ISY device """
    password_mgr = URL.HTTPPasswordMgrWithDefaultRealm()
    handler = URL.HTTPBasicAuthHandler(password_mgr)
    opener = URL.build_opener(handler)

    def __init__(self, userl="admin", userp="admin", **kwargs):
        #
        # Keyword args
        #
	self.debug = kwargs.get("debug", 0)
	self.cachetime = kwargs.get("cachetime", 0)
	self.faststart = kwargs.get("faststart", 1)
	self.eventupdates = kwargs.get("eventupdates", 0)
        self.addr = kwargs.get("addr", os.getenv('ISY_ADDR', '10.1.1.36'))

        if self.debug & 0x01 :
            print "class Isy __init__"
            print "debug ", self.debug
            print "cachetime ", self.cachetime
            print "faststart ", self.faststart

	# parse   ISY_AUTH as   LOGIN:PASS

        #
        # general setup logic
        #
        self.baseurl = "http://" + self.addr
        Isy.handler.add_password(None, self.addr, userl, userp)
        # self.opener = URL.build_opener(Isy.handler, URL.HTTPHandler(debuglevel=1))
        # self.opener = URL.build_opener(Isy.handler)
        if self.debug & 0x02:
	    print "baseurl: " + self.baseurl + " : " + userl + " : " + userp

        if not self.faststart :
            self.load_conf()

        # There for id's to Node/Var/Prog objects
        self.nodeCdict = dict ()
        self.varCdict = dict ()
        self.progCdict = dict ()
        self.folderCdict = dict ()

	if self.eventupdates :
	    self.start_event_thread()

    def start_event_thread(self):
	from threading import Thread

	print "start preload"
	self._preload()
	print "start complete"

	self.isy_event = ISYEvent()
	self.isy_event.subscribe(self.addr)
	self.isy_event.set_process_func(self._read_event, self)
	
	self.event_thread = Thread(target=self.isy_event.events_loop, name="event_looper" )
	self.event_thread.daemon = True
	self.event_thread.start()

	print self.event_thread

    # @staticmethod
    def _read_event(self, d, *arg) :
	# print "_read_event"
	skip = ["_0", "_2", "_4", "_5", "_6", "_7", "_8",
		"_9", "_10", "_11", "_12", "_13", "_14",
		"_15", "_16", "_17", "_18", "_19", "_20",]

	# isy = arg[0]

	# print "d",type(d)

	assert isinstance(d, dict), "_read_event Arg must me dict"

	if d["control"] in skip :
	    return

	if d["control"] in ["ST", "RR", "OL"] :
	    if d["node"] in self._nodedict :
		# print "d :",d
		#print self._nodedict[d["node"]]

		# create property if we do not have it yet
		if not d["control"] in self._nodedict[d["node"]]["property"] :
		    self._nodedict[d["node"]]["property"][d["control"]] = dict ( )

		self._nodedict[d["node"]]["property"][d["control"]]["value"] \
			= d["action"]
		self._nodedict[d["node"]]["property"][d["control"]]["formatted"] \
			= self._format_val( d["action"] )

		if ( self.debug & 0x10 ) :
		    print "_read_event :", d["node"],d["control"],d["action"]
		    print self._nodedict[d["node"]]["property"]
	    else :
		warning.warn("Event for Unknown node : {0}".format(d["node"]), \
			RuntimeWarning)


	elif d["control"] == "_3" : # Node Change/Updated Event
		print "Node Change/Updated Event :  {0}".format(d["node"])
		print "d : ", d

	# handle VAR value change
	elif d["control"] == "_1" :
	    if d["action"] == "6" or  d["action"] == "7" : # Var Status / Initialized
		vid = d['eventInfo']['var']['var-type'] + ":" + d['eventInfo']['var']['var-id']
		if vid in self._vardict :
		    for p in ['init', 'val', 'ts'] :
			if p in d['eventInfo']['var'] :
			    self._vardict[vid][p] = d['eventInfo']['var'][p]
		else :
		    warning.warn("Event for Unknown Var : {0}".format(vid), \
			    RuntimeWarning)

	else:
	    print "d :",d
	    print "Event for Unknown Node : '{0}'".format(d["node"])
	    print self



    def _format_val(self, v) :
	try:
	    v = int(v)
	except ValueError :
	    return "0"
	else :
	    if ( v == 0 ) :
		return "off"
	    elif  v == 255 :
		return "on"
	    else :
		return str ( (int(v)*100) // 255)


    def _preload(self):
        self.load_conf()
        self.load_nodes()
	# self._gen_member_list()
        # self.load_clim()
        self.load_vars()
        self.load_prog()
        #self.load_wol()
	self.load_node_types()

    def _savedict(self) :

	self._preload()

	# self._writedict(self.wolinfo, "wolinfo.txt")

	self._writedict(self._nodedict, "nodedict.txt")

	self._writedict(self._nodegroups, "nodegroups.txt")

	self._writedict(self.folderlist, "folderlist.txt")

	self._writedict(self._vardict, "vardict.txt")

	# self._writedict(self.climateinfo, "climateinfo.txt")

	self._writedict(self.controls, "controls.txt")

	self._writedict(self._progdict, "progdict.txt")



    ##
    ## Load System config / info and command information
    ##
    def load_conf(self) :
        """ Load configuration of the system with permissible commands 

	    args : none

	    internal function call

	"""
        if self.debug & 0x01 :
            print "load_conf pre _getXMLetree"
        self.configinfo = self._getXMLetree("/rest/config")
        # Isy._printXML(self.configinfo)

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
	    n = self.configinfo.find(v)
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
        """ Load node list scene list and folder info

	    args : none

	    internal function call

	"""
        self._nodedict = dict ()
        # self.nodeCdict = dict ()
        self.node2addr = dict ()
        if self.debug & 0x01 :
            print "load_nodes pre _getXML"
        nodeinfo = self._getXMLetree("/rest/nodes")
        self._gen_nodedict(nodeinfo)
        self._gen_folder_list(nodeinfo)
        self._gen_nodegroups(nodeinfo)
        # self._printdict(self._nodedict)
	print "load_nodes self.node2addr : ", len(self.node2addr)
	self._gen_member_list()

    def _gen_member_list(self) :
	try:
	    self._nodedict
        except AttributeError:
	    return
	else :

	    # Folders can only belong to Folders
	    for fa in self.folderlist :
		# make code easier to read
		f = self.folderlist[fa]
		# add members list if needed
		if 'members' not in f :
		    f['members'] = list()
		# check if folder obj has a parent
		if 'parent' in f :
		    # this should always be true
		    if f['parent-type'] == '3' and  f['parent'] in self.folderlist :
			if 'members' not in self.folderlist[f['parent']] :
			    self.folderlist[f['parent']]['members'] = list()
			self.folderlist[f['parent']]['members'].append( f['address'])  
		    else:
			print "warn bad parenting f =", f

	    # Scenes can only belong to Folders
	    for sa in self._nodegroups :
		s = self._nodegroups[sa]
		if "parent" in s :
		    if s['parent-type']== '3' and  s['parent'] in self.folderlist :
			self.folderlist[s['parent']]['members'].append( s['address'])
		    else:
			print "warn bad parenting s = ", s

	    # A Node can belong only to ONE and only ONE Folder or another Node
	    for na in self._nodedict :
		n = self._nodedict[na]
		# print "n = ", n
		if 'pnode' in n and n['pnode'] != n['address'] :
		    if 'members' not in self._nodedict[n['pnode']] :
			self._nodedict[n['pnode']]['members'] = list ()
		    self._nodedict[n['pnode']]['members'].append( n['pnode'] )

		if 'parent' in n :
		    if 'pnode' not in n or n['pnode'] != n['pnode'] :
			if n['parent-type'] == 3 :
			    if n['parent'] in self.folderlist :
				self.folderlist[n['parent']]['members'].append( n['address'])
			elif  n['parent-type'] == 1 :
			    if n['parent'] in self._nodegroups :
				self._nodegroups[n['parent']]['members'].add( n['address'])
		# 'parent': '16 6C D2 1', 'parent-type': '1',
		# 'parent': '12743', 'parent-type': '3',
		# if n.pnode == n.parent and n.pnode == n.address
		    next
		pass



    def _gen_folder_list(self, nodeinfo) :
        """ generate folder dictionary for load_node """
        self.folderlist = dict ()
        self.folder2addr = dict ()
        for fold in nodeinfo.iter('folder'):
            fprop = dict ()
            for k, v in fold.items() :
                fprop[fold.tag + "-" + k] = v
            for child in list(fold):
                fprop[child.tag] = child.text
		if child.attrib :
		    for k, v in child.items() :
			fprop[child.tag + "-" + k] =  v
            self.folderlist[fprop["address"]] = fprop
	    self.folder2addr[fprop["name"]] = fprop["address"]
	#self._printdict(self.folderlist)
	#self._printdict(self.folder2addr)

    def _gen_nodegroups(self, nodeinfo) :
        """ generate scene / group dictionary for load_node """
        self._nodegroups = dict ()
        self.groups2addr = dict ()
        for grp in nodeinfo.iter('group'):
            gprop = dict ()
            for k, v in grp.items() :
                gprop[grp.tag + "-" + k] = v
            for child in list(grp) :
		if child.tag == "parent" :
                    gprop[child.tag] = child.text
		    for k, v in child.items() :
			gprop[child.tag + "-" + k] =  v
                elif child.tag == "members" :
                    glist = dict ()
                    for lnk in child.iter('link'):
			glist[lnk.text] = lnk.attrib['type']
                    gprop[child.tag] = glist
                else :
                    gprop[child.tag] = child.text
		    if child.attrib :
			for k, v in child.items() :
			    gprop[child.tag + "-" + k] =  v

            if "address" in gprop :
                self._nodegroups[gprop["address"]] = gprop
                if "name" in gprop :
		    if gprop["name"] in self.groups2addr :
			print "Dup group name", gprop["name"], str(gprop["address"])
		    else :
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
                idict[inode.tag + "-" + k] = v
            for child in list(inode) :
                # self._printinfo(child, "\tchild")

                if child.tag == "parent" :
                    idict[child.tag] = child.text
                    for k, v in child.items() :
                        idict[child.tag + "-" + k] = v
		# special case where ST, OL, and RR
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
		    if idict["name"] in self.node2addr :
			warning.warn("Duplicate Node Name", RuntimeWarning)
		    else :
			self.node2addr[idict["name"]] = idict["address"]

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
            self.node2addr
        except AttributeError:
            self.load_nodes()
        finally:
            return self.node2addr[:]

    def scene_names(self) :
        """ access method for scene names
            returns a dict of ( Node names : Node address ) """
        try:
            self.groups2addr
        except AttributeError:
            self.load_nodes()
        finally:
            return self.groups2addr[:]

    def node_addrs(self) :
        """ access method for node addresses
            returns a iist scene/group addresses """
        try:
            self._nodedict
        except AttributeError:
            self.load_nodes()
        finally:
            return self._nodedict.viewkeys()

    def scene_addrs(self) :
        """ access method for scene addresses
            returns a iist scene/group addresses """
        try:
            self._nodegroups
        except AttributeError:
            self.load_nodes()
        finally:
            return self._nodegroups.viewkeys()


    def get_node(self, node_id) :
        """ Get a Node object for given node or scene name or ID

	    args:
		nodee : node name of id

	    return:
		An IsyNode object representing the requested Scene or Node

	"""
        if self.debug & 0x01 :
            print "get_node"

	nodeid = self._get_node_id(node_id)
	if nodeid in self._nodedict :
	    if not nodeid in self.nodeCdict :
		self.nodeCdict[nodeid] = IsyNode(self, self._nodedict[nodeid])
	    return self.nodeCdict[nodeid]
	elif nodeid in self._nodegroups:
	    if not nodeid in self.nodeCdict :
		self.nodeCdict[nodeid] = IsyScene(self, self._nodegroups[nodeid])
	    return self.nodeCdict[nodeid]
	else :
	    print "Isy get_node no node : \"%s\"" % nodeid
	    raise LookupError("no node such Node : " + str(nodeid) )


    def _get_node_id(self, nid):
        """ node/scene name to node/scene ID """

        try:
            self._nodedict
        except AttributeError:
            self.load_nodes()
#       except:
#           print "Unexpected error:", sys.exc_info()[0]
#           return None


	if isinstance(nid, IsySubClass) :
	     return nid["addr"]
	else :
	    n = str(nid)
        if string.upper(n) in self._nodedict :
            # print "_get_node_id : " + n + " nodedict " + string.upper(n)
            return string.upper(n)
        if n in self.node2addr :
            # print "_get_node_id : " + n + " node2addr " + self.node2addr[n]
            return self.node2addr[n]
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
        try:
            self.controls
        except AttributeError:
            self.load_conf()

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
        if self.debug & 0x01 :
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
        self._printXML(resp)
        if resp.attrib["succeeded"] != 'true' :
            raise IsyResponseError("Node Property Set error : node=%s prop=%s val=%s" %
		    naddr, prop, val )


    #
    # Send command to Node/Scene
    #
    def node_comm(self, naddr, cmd, *args) :
        """ send command to a node or scene """
        if self.debug & 0x04 :
	    print "node_comm",naddr, cmd
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
        if self.debug & 0x04 :
	    print "_node_comm",node_id, cmd_id
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
        if self.debug & (0x01 & 0x10) :
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
        """ Load node type info into a multi dimentional dictionary

	    args : none

	    internal function call

	"""
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
		## FIX
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


    def node_iter(self, nodetype=""):
	""" Iterate though nodes

	    args: 
		nodetype : type of node to return

	    returns :
		Return an iterator over the Node Obj
	"""
        try:
            self._nodedict
        except AttributeError:
            self.load_nodes()
	if nodetype == "node" :
	    k = self._nodedict.keys()
	elif nodetype == "scene" :
	    k = self._nodegroups.keys()
	else :
	    k = self._nodedict.keys()
	    k.extend(self._nodegroups.keys())
	for n in k :
	    yield self.get_node(n)

    ##
    ## variable funtions
    ##
    def load_vars(self) :
        """ Load variable names and values

	    args : none

	    internal function call

	"""
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
		vid = t + ":" + v.attrib["id"]
                self._vardict[vid]['name'] = v.attrib['name']
                self._vardict[vid]["id"] = vid
                self._vardict[vid]["type"] = t
		if v.attrib['name'] in self.name2var :
		    print "warning Dum var name :", v.attrib['name'], \
			    vid, self.name2var[v.attrib['name']]
		else :
		    self.name2var[v.attrib['name']] = vid

        # self._printdict(self._vardict)


    def var_set_value(self, var, val, prop="val") :
        """ Set var value by name or ID

	    args:
		var = var name or Id
		val = new value
		prop = property to addign value to (default = val)

	    raise:
		LookupError :  if var name or Id is invalid
		TypeError :  if property is not 'val or 'init'

	"""
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

    def var_get_value(self, var, prop="var") :
        """ Get var value by name or ID
	    args:
		var = var name or Id
		prop = property to addign value to (default = val)

	    raise:
		LookupError :  if var name or Id is invalid
		TypeError :  if property is not 'val or 'init'
	"""
	varid = self._var_get_id(vname)
        if not varid :
            raise LookupError("var_set_value: unknown var : " + str(var) )
        if not prop in ['init', 'val'] :
	    raise TypeError("var_set_value: unknown propery : " + str(prop) )
	if varid in self._vardict :
	    return(self._vardict[val])


#    def var_names(self) :
#        pass


    def var_addrs(self)  :
        """ access method for var addresses

	    args: None

            returns :  a iist view of var ids
	"""
        try:
            self._vardict
        except AttributeError:
            self.load_vars()
#       except:
#           print "Unexpected error:", sys.exc_info()[0]
#           return None
        return self.name2var.viewkeys()


    def get_var(self, vname) :
        """ get var class obj 

	    args : var name or Id

	    returns : a IsyVar obj

	    raise:
		LookupError :  if var name or Id is invalid

	"""
        if self.debug & 0x01 :
	    print "get_var :" + vname

	varid = self._var_get_id(vname)
	# print "\tvarid : " + varid
	if varid in self._vardict :
	    if not varid in self.varCdict :
		# print "not varid in self.varCdict:"
		# self._printdict(self._vardict[varid])
		self.varCdict[varid] = IsyVar(self, self._vardict[varid])
	    #self._printdict(self._vardict)
	    # print "return : ",
	    #self._printdict(self.varCdict[varid])
	    return self.varCdict[varid]
	else :
	    if self.debug & 0x01 :
		print "Isy get_var no var : \"%s\"" % varid
	    raise LookupError("no var : " + str(varid) )


    def _var_get_id(self, vname):
        """ Lookup var value by name or ID
	returns ISY Id  or None
	"""
        try:
            self._vardict
        except AttributeError:
            self.load_vars()
#       except:
#           print "Unexpected error:", sys.exc_info()[0]
#           return None
        
	if isinstance(vname, IsyVar) :
	     return vname["id"]
	else :
	    v = str(vname)
        if string.upper(v) in self._vardict :
            # print "_get_var_id : " + v + " vardict " + string.upper(v)
            return string.upper(v)
        if v in self.name2var :
            # print "_var_get_id : " + v + " name2var " + self.name2var[v]
            return self.name2var[v]

        # print "_var_get_id : " + n + " None"
        return None

    def var_get_type(self, var) :
        try:
            self._vardict
        except AttributeError:
            self.load_vars()
#       except:
#           print "Unexpected error:", sys.exc_info()[0]
	return "VART"

	v = self._var_get_id(var)
	if v in self._vardict :
	    return self._vardict[v]["type"] 
	return None



    def var_iter(self, vartype=0):
	""" Iterate though vars objects

	    args: 
		nodetype : type of var to return

	    returns :
		Return an iterator over the Var Obj
	"""
        try:
            self._vardict
        except AttributeError:
            self.load_vars()
#       except:
#           print "Unexpected error:", sys.exc_info()[0]

	k = self._vardict.keys()
	for v in k :
	    if vartype :
		vartype = str(vartype)
		if self._vardict[v]["type"] == vartype :
		    yield self.get_var(v)
	    else :
		yield self.get_var(v)

    def set_var_value(self, varname, val, init=0):
        if self.debug & 0x01 :
	    print "set_var :" + vname

	varid = self._var_get_id(vname)
	if varid in self._vardict :
	    self._set_var_value(varid, val, init)
	else :
	    raise LookupError("var_set_value: unknown var : " + str(var) )


    def _set_var_value(self, varid, val, init=0):
	vid = varid.split(':')
	if init :
	    xurl = "/rest/vars/init/" + a[0] + "/" + a[1] + "/" + val
	else :
	    xurl = "/rest/vars/set/" + a[0] + "/" + a[1] + "/" + val

        if self.debug & 0x02 :
            print "xurl = " + xurl

        resp = self._getXMLetree(xurl)
        self._printXML(resp)
        if resp.attrib["succeeded"] != 'true' :
            raise IsyResponseError("ISY command error : varid=" +
		str(varid) + " cmd=" + str(cmd_id))


    ##
    ## Climate funtions
    ##
    def load_clim(self) :
        """ Load climate data from ISY device

	    args : none

	    internal function call

	"""
        if self.debug & 0x01 :
            print "load_clim called"
        clim_tree = self._getXMLetree("/rest/climate")
        self.climateinfo = dict ()
	if clim_tree == None :
	    return 
        # Isy._printXML(self.climateinfo)

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

    def clim_iter():
	""" Iterate though climate values

	    args:  
		None

	    returns :
		Return an iterator over the climate values
	"""
        try:
            self.climateinfo
        except AttributeError:
            self.load_clim()
	k = self.climateinfo.keys()
	for p in k :
	    yield self.climateinfo[p]

    ##
    ## WOL (Wake on LAN) funtions
    ##
    def load_wol(self) :
        """ Load Wake On LAN IDs 

	    args : none

	    internal function call

	"""
        if self.debug & 0x01 :
            print "load_wol called"
        wol_tree = self._getXMLetree("/rest/networking/wol")
        self.wolinfo = dict ()
        self.name2wol = dict ()
        for wl in wol_tree.iter("NetRule") :
            wdict = dict ()
            for k, v in wl.items() :
                wdict[k] = v
            for we in list(wl):
                wdict[we.tag] = we.text
            if "id" in wdict :
                self.wolinfo[str(wdict["id"])] = wdict
                self.name2wol[wdict["name"].upper()] = wdict["id"]
        # self._printdict(self.wolinfo)
        # self._printdict(self.name2wol)

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
	if name in self.wolinfo :
	    return name

	if name in self.self.name2wol :
	    return self.name2wol[name]

	return None


    def wol_names(self, vname) :
	"""
	method to retrieve a list of WOL names
	:type wolname: string
	:param wolname: the WOL name or ISY Id
	:rtype: list
        :return: List of WOL names and IDs or None
	"""
	return self.name2wol.keys()


    def wol_iter():
	""" Iterate though Wol Ids values

	    args:  
		None

	    returns :
		Return an iterator over the "Wake on Lan" Ids
	"""
        try:
            self.self.wolinfo
        except AttributeError:
            self.load_wol()
	k = self.wolinfo.keys()
	for p in k :
	    yield p

    ##
    ## ISY Programs Code
    ##
    def load_prog(self):
        """ Load Program status and Info

	    args : none

	    internal function call

	"""
        if self.debug & 0x01 :
            print "load_prog called"
        prog_tree = self._getXMLetree("/rest/programs?subfolders=true", 1)
        self._progdict = dict ()
        self.name2prog = dict ()
        for pg in prog_tree.iter("program") :
            pdict = dict ()
            for k, v in pg.items() :
                pdict[k] = v
            for pe in list(pg):
                pdict[pe.tag] = pe.text
            if "id" in pdict :
                self._progdict[str(pdict["id"])] = pdict
		n = pdict["name"].upper()
		if n in self.name2prog :
		    print "Dup name : \"" + n + "\" ", pdict["id"]
		    print "name2prog ", self.name2prog[n]
		else :
		    self.name2prog[n] = pdict["id"]
        #self._printdict(self._progdict)
        #self._printdict(self.name2prog)



    def get_prog(self, pname) :
        """ get prog class obj """
        if self.debug & 0x01 :
	    print "get_prog :" + pname
        try:
            self._progdict
        except AttributeError:
            self.load_progs()
#       except:
#           print "Unexpected error:", sys.exc_info()[0]
#           return None
        finally:
            progid = self._prog_get_id(pname)
	    # print "\tprogid : " + progid
            if progid in self._progdict :
                if not progid in self.progCdict :
		    # print "not progid in self.progCdict:"
		    # self._printdict(self._progdict[progid])
                    self.progCdict[progid] = IsyProgram(self, self._progdict[progid])
		#self._printdict(self._progdict)
		# print "return : ",
		#self._printdict(self.progCdict[progid])
                return self.progCdict[progid]
            else :
		if self.debug & 0x01 :
		    print "Isy get_prog no prog : \"%s\"" % progid
                raise LookupError("no prog : " + str(progid) )

    def _prog_get_id(self, pname):
        """ Lookup prog value by name or ID
	returns ISY Id  or None
	"""
	if isinstance(pname, IsyProgram) :
	     return vname["id"]
	else :
	    p = str(pname)
        if string.upper(p) in self._progdict :
            # print "_get_prog_id : " + p + " progdict " + string.upper(p)
            return string.upper(p)
        if p in self.name2prog :
            # print "_prog_get_id : " + p + " name2prog " + self.name2prog[p]
            return self.name2prog[p]

        # print "_prog_get_id : " + n + " None"
        return None


    def prog_iter(self):
	""" Iterate though program objects

	    args:  
		None

	    returns :
		Return an iterator over Program Objects types
	"""
        try:
            self._progdict
        except AttributeError:
            self.load_prog()
#       except:
#           print "Unexpected error:", sys.exc_info()[0]

	k = self._progdict.keys()
	for v in k :
	    yield self.get_prog(v)

    def prog_comm(self, paddr, cmd, *args) :
	valid_comm = ['run', 'runThen', 'runElse', 'stop',
			'enable', 'disable',
			'enableRunAtStartup', 'disableRunAtStartup']
        prog_id = self._get_prog_id(paddr)

        #print "self.controls :", self.controls
        #print "self.name2control :", self.name2control

        if not prog_id :
            raise IsyInvalidCmdError("prog_comm: unknown node : " +
		str(paddr) )

        if not cmd in valid_comm :
            raise IsyInvalidCmdError("prog_comm: unknown command : " +
		str(cmd) )

	self._prog_comm(prog_id, cmd, *args)

    def _prog_comm(self, prog_id, cmd, *args) :
        """ send command to a program without name to ID overhead """
        # /rest/programs/<pgm-id>/<pgm-cmd>
        xurl = "/rest/programs/" + prog_id + cmd 

        if self.debug & 0x02 :
            print "xurl = " + xurl

        resp = self._getXMLetree(xurl)
        self._printXML(resp)
        if resp.attrib["succeeded"] != 'true' :
            raise IsyResponseError("ISY command error : prog_id=" +
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
    ## Logs
    ##
    def load_log_type():
	pass

    def load_log_id():
	pass

    def log_reset(self, errorlog = 0 ):
	""" clear log lines in ISY """ 
	self.log_query(errorlog, 1)

    def log_iter(self, error = 0 ):
	""" iterate though log lines 

	    args:  
		error : return error logs or now

	    returns :
		Return an iterator log enteries 
	"""
	for l in self.log_query(error) :
	    yield l

    def log_query(self, errorlog = 0, resetlog = 0 ):
	""" get log from ISY """
	xurl = self.baseurl + "/rest/log"
	if errorlog :
	    xurl += "/error"
	if resetlog :
	    xurl += "?reset=true"
        if self.debug & 0x02 :
	    print "xurl = " + xurl
	req = URL.Request(xurl)
        res = self.opener.open(req)
        data = res.read()
        res.close()
        return data.splitlines()

    def log_format_line(self, line) :
	""" format a ISY log line into a more human readable form """
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
	""" iterate though Node Obj

	    see : node_iter()

	"""
	return self.node_iter()

#    def __repr__(self):
#        return "<Isy %s at 0x%x>" % (self.addr, id(self))

    def debugerror(self) :
	print "debugerror"
        raise IsyProperyError("debugerror : test IsyProperyError  ")

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

    def _writedict(self, d, filen):
	""" Pretty Print dict to file  """
	fi = open(filen, 'w')
	mypp = pprint.PrettyPrinter(indent=3, stream=fi)
	mypp.pprint(d)
	fi.close()


#
# Do nothing
# (syntax check)
#
if __name__ == "__main__":
    import __main__
    print __main__.__file__

    print("syntax ok")
    exit(0)
