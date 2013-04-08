"""Simple Python lib for the ISY home automation netapp

 This is a Python interface to the ISY rest interface
 providomg simple commands to query and control registared Nodes and Scenes
 and well as a method of setting or querying vars
 
"""

from ISY.IsyExceptionClass import *

#from xml.dom.minidom import parse, parseString
# from StringIO import StringIO
# import xml.etree.ElementTree as # ET
# import base64
import re
import os
from pprint import pprint
import sys
import string
import pprint
import time
from warnings import warn

"""
/rest/batch
    Returns the Batch mode:
    <batch><status>[0|1]</status></batch>

/rest/batch/on
    Turns on Batch mode. Does not write changes to device. Only internal
    configuration files are updated

/rest/batch/Off
    Turns off Batch mode. Writes all pending changes to devices and no longer
    buffers changes
"""

"""
/rest/batteryPoweredWrites
    Returns the status of Battery Powered device operations
    <batteryPoweredWrites> <status>[0|1]</status> </batteryPoweredWrites>

/rest/batteryPoweredWrites/on
    Writes all pending changes to battery powered devices when Batch mode is off

/rest/batteryPoweredWrites/off
    Does not write changes to battery powered devices when batch is off

"""


# /rest/time
#	Returns system time

#/rest/network
#    Returns network configuration



if sys.hexversion < 0x3000000 :
    import urllib2 as URL
    # HTTPPasswordMgrWithDefaultRealm = URL.HTTPPasswordMgrWithDefaultRealm
else :
    import urllib as URL
    from urllib.request import HTTPPasswordMgrWithDefaultRealm

from ISY.IsyUtilClass import IsyUtil, IsySubClass
from ISY.IsyNodeClass import IsyNode, IsyScene, IsyNodeFolder, _IsyNodeBase
from ISY.IsyProgramClass import *
from ISY.IsyVarClass import IsyVar
from ISY.IsyExceptionClass import *
from ISY.IsyEvent import ISYEvent

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

# EventUpdate Mask:
# 0x00 = update all
# 0x01 = Ignore Node events
# 0x02 = Ignore Var events
# 0x04 = Ignore Program events
# 0x08 = 
# 0x10 = Ignore Climate events
# 0x20 =
# 0x40 =
# 0x80 =
#
__all__ = ['Isy']



# if hasattr(instance, 'tags') and isinstance(instance.tags, dict):
#     for tag in instance.tags:

# def batch .write


# _nodedict     dictionary of node data indexed by node ID
# node2addr     dictionary mapping node names to node ID
# nodeCdict     dictionary cache or node objects indexed by node ID


class Isy(IsyUtil):
    """ Obj class the represents the ISY device

	Keyword Args :
	    addr :	IP address of ISY
	    userl/userp : User Login / Password

	    debug :	Debug flags (default 0)
	    cachetime :	cache experation time [NOT USED] (default 0)
	    faststart : ( ignored if eventupdate is used )
		    0=preload cache as startup
		    1=load cache on demand
	    eventupdates: run a sub-thread and stream  events updates from ISY
			same effect as calling  Isy().start_event_thread()



    """

    from _isywol import load_wol, wol, _get_wol_id, wol_names, wol_iter
    from _isyclimate import load_clim, clim_get_val, clim_query, clim_iter
    from _isyvar  import load_vars, var_set_value, _var_set_value, var_get_value, var_addrs, get_var, _var_get_id, var_get_type, var_iter


##    set_var_value, _set_var_value, var_names


    if sys.hexversion < 0x3000000 :
        _password_mgr = URL.HTTPPasswordMgrWithDefaultRealm()
        _handler = URL.HTTPBasicAuthHandler(_password_mgr)
        _opener = URL.build_opener(_handler)
    else:
        _password_mgr = URL.request.HTTPPasswordMgrWithDefaultRealm()
        _handler = URL.request.HTTPBasicAuthHandler(_password_mgr)
        _opener = URL.request.build_opener(_handler)

    def __init__(self, userl="admin", userp="admin", **kwargs):
        #
        # Keyword args
        #
        self.debug = kwargs.get("debug", 0)
        self.cachetime = kwargs.get("cachetime", 0)
        self.faststart = kwargs.get("faststart", 1)
        self.eventupdates = kwargs.get("eventupdates", 0)
        self.addr = kwargs.get("addr", os.getenv('ISY_ADDR', None))
	self._isy_event = None

        if self.addr == None :
            from ISY.IsyDiscover import isy_discover

            units = isy_discover(count=1) 
            for device in units.values() :
                self.addr = device['URLBase'][7:]
                self.baseurl = device['URLBase']
        else :
            self.baseurl = "http://" + self.addr

        if self.addr == None :
            raise Exception("No ISY address given or found")

        if self.debug & 0x01 :
            print("class Isy __init__")
            print("debug ", self.debug)
            print("cachetime ", self.cachetime)
            print("faststart ", self.faststart)

        # parse   ISY_AUTH as   LOGIN:PASS

        #
        # general setup logic
        #
        Isy._handler.add_password(None, self.addr, userl, userp)
        # self._opener = URL.build_opener(Isy._handler, URL.HTTPHandler(debuglevel=1))
        # self._opener = URL.build_opener(Isy._handler)
        if self.debug & 0x02:
            print("baseurl: " + self.baseurl + " : " + userl + " : " + userp)

        if not self.faststart :
            self.load_conf()

        # There for id's to Node/Var/Prog objects
        self.nodeCdict = dict ()
        self.varCdict = dict ()
        self.progCdict = dict ()
        self.folderCdict = dict ()

        if self.eventupdates :
            self.start_event_thread()

    #
    # Event Subscription Code
    # Allows for treaded realtime node status updating
    #
    def start_event_thread(self, mask=0):
        """  starts event stream update thread


        """
        from threading import Thread

	# if thread already runing we should update mask
	if hasattr(self, 'event_thread') and isinstance(self.event_thread, Thread) :
	    if self.event_thread.is_alive() :
		print "Thread already running ?"
		return

	#st = time.time()
        #print("start preload")

        self._preload(reload=0)

	#sp = time.time()
        #print("start complete")
	#print "load in ", ( sp - st )

        self._isy_event = ISYEvent()
        self._isy_event.subscribe(self.addr)
        self._isy_event.set_process_func(self._read_event, self)
        
        self.event_thread = Thread(target=self._isy_event.events_loop, name="event_looper" )
        self.event_thread.daemon = True
        self.event_thread.start()

        print(self.event_thread)

    def stop_event_tread(self) :
	""" Stop update thread """
	if hasattr(self._isy_event, "_shut_down") :
	    self._isy_event._shut_down = 1

    # @staticmethod
    def _read_event(self, evnt_dat, *arg) :
        """ read event stream data and copy into internal state cache

            internal function call

        """
        # print("_read_event")
        skip_default = ["_0", "_2", "_4", "_5", "_6", "_7", "_8",
                "_9", "_10", "_11", "_12", "_13", "_14",
                "_15", "_16", "_17", "_18", "_19", "_20",
                "DON", "DOF",
                ]

	skip = skip_default

        
        ar = arg[1]

        # print "ar", type( arg)

        assert isinstance(evnt_dat, dict), "_read_event Arg must me dict"

        if evnt_dat["control"] in skip :
            return

        if evnt_dat["control"] in ["ST", "RR", "OL"] :
            if evnt_dat["node"] in self._nodedict :
		# ADD LOCK ON NODE DATA
                # print("===evnt_dat :", evnt_dat)
                # print("===a :", ar)
                #print(self._nodedict[evnt_dat["node"]])
                target_node =  self._nodedict[evnt_dat["node"]]

                # create property if we do not have it yet
                if not evnt_dat["control"] in target_node["property"] :
                    target_node["property"][evnt_dat["control"]] = dict ( )

                target_node["property"][evnt_dat["control"]]["value"] \
                        = evnt_dat["action"]
                target_node["property"][evnt_dat["control"]]["formatted"] \
                        = self._format_val( evnt_dat["action"] )

                if ( self.debug & 0x10 ) :
		    print("_read_event :", evnt_dat["node"], evnt_dat["control"], evnt_dat["action"])
		    print(">>>", self._nodedict[evnt_dat["node"]]["property"])
            else :
                warn("Event for Unknown node : {0}".format(evnt_dat["node"]), \
                        RuntimeWarning)

        elif evnt_dat["control"] == "_3" : # Node Change/Updated Event
                print("Node Change/Updated Event :  {0}".format(evnt_dat["node"]))
                print("evnt_dat : ", evnt_dat)

        # handle VAR value change
        elif evnt_dat["control"] == "_1" :
            # Var Status / Initialized
            if evnt_dat["action"] == "6" or  evnt_dat["action"] == "7" :
                var_eventInfo =  evnt_dat['eventInfo']['var']
                vid = var_eventInfo['var-type'] + ":" + var_eventInfo['var-id']
                # check if the event var exists in out world
                if vid in self._vardict :
		    # ADD LOCK ON VAR DATA
                    # copy var properties from event

		    self._vardict[vid].update(var_eventInfo)

                    #for prop in ['init', 'val', 'ts'] :
                    #    if prop in var_eventInfo :
                    #        self._vardict[vid][prop] = var_eventInfo[prop]
                else :
                    warn("Event for Unknown Var : {0}".format(vid), RuntimeWarning)

        else:
            print("evnt_dat :", evnt_dat)
            print("Event fall though : '{0}'".format(evnt_dat["node"]))



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


    #
    #  Util Funtions
    #
    def _preload(self, mask=0, reload=0):
	if reload or  not hasattr(self, "controls") :
	    self.load_conf()

	if reload or not hasattr(self, "_nodedict") :
	    self.load_nodes()

        # self._gen_member_list()
	# if reload or  not hasattr(self, "climateinfo") :
	    # self.load_clim()

	if reload or  not hasattr(self, "_vardict") :
	    self.load_vars()

	if reload or  not hasattr(self, "_progdict") :
	    self.load_prog()

	# if reload or  not hasattr(self, "wolinfo") :
	    #self.load_wol()

	if reload or  not hasattr(self, "nodeCategory") :
	    self.load_node_types()

    def _savedict(self) :

        self._preload()

        # self._writedict(self.wolinfo, "wolinfo.txt")

        self._writedict(self._nodedict, "nodedict.txt")

        self._writedict(self._nodegroups, "nodegroups.txt")

        self._writedict(self._folderlist, "folderlist.txt")

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
            print("load_conf pre _getXMLetree")
        self.configinfo = self._getXMLetree("/rest/config")
        # Isy._printXML(self.configinfo)

        self.name2control = dict ( )
        self.controls = dict ( )
        for ctl in self.configinfo.iter('control') :
            # self._printXML(ctl)
            # self._printinfo(ctl, "configinfo : ")
            cprop = dict ( )

            for child in list(ctl):
                # print("child.tag " + str(child.tag) + "\t=" + str(child.text))
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

            # print("cprop ", cprop)
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

        # print("self.controls : ", self.controls)
        #self._printdict(self.controls)
        #print("self.name2control : ", self.name2control)

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
	if not hasattr(self, '_nodedict') or not isinstance(self._nodedict, dict):
	     self._nodedict = dict ()

	if not hasattr(self, '_nodegroups') or not isinstance(self._nodegroups, dict):
	    self._nodegroups  = dict ()

	if not hasattr(self, 'folderlist') or not isinstance(self._folderlist, dict):
	    self._folderlist  = dict ()

        # self.nodeCdict = dict ()
	# self.node2addr = dict ()
        if self.debug & 0x01 :
            print("load_nodes pre _getXML")
        nodeinfo = self._getXMLetree("/rest/nodes")
        self._gen_nodedict(nodeinfo)
        self._gen_folder_list(nodeinfo)
        self._gen_nodegroups(nodeinfo)
        # self._printdict(self._nodedict)
        # print("load_nodes self.node2addr : ", len(self.node2addr))
        self._gen_member_list()

    def _gen_member_list(self) :
        """ganerates node connecton lists

            internal function call

        """
        try:
            self._nodedict
        except AttributeError:
            return
        else :

            # Folders can only belong to Folders
            for faddr in self._folderlist :
                # make code easier to read
                foldr = self._folderlist[faddr]
                # add members list if needed
                if 'members' not in foldr :
                    foldr['members'] = list()
                # check if folder obj has a parent
                if 'parent' in foldr :
                    # this should always be true
                    if foldr['parent-type'] == '3' and \
                            foldr['parent'] in self._folderlist :
                        if 'members' not in self._folderlist[foldr['parent']] :
                            self._folderlist[foldr['parent']]['members'] = list()
                        self._folderlist[foldr['parent']]['members'].append( foldr['address'])  
                    else:
                        print("warn bad parenting foldr =", foldr)
			warn("Bad Parent : Folder  (0)  (1) : (2)".format( \
				foldr["name"], faddr, foldr['parent']), RuntimeWarning)

            # Scenes can only belong to Folders
            for sa in self._nodegroups :
                s = self._nodegroups[sa]
                if "parent" in s :
                    if s['parent-type'] == '3' and  s['parent'] in self._folderlist :
                        self._folderlist[s['parent']]['members'].append( s['address'])
                    else:
                        print("warn bad parenting s = ", s)
			warn("Bad Parent : Scene  (0)  (1) : (2)".format( \
				s["name"], sa, s['parent']), RuntimeWarning)

            # A Node can belong only to ONE and only ONE Folder or another Node
            for naddr in self._nodedict :
                n = self._nodedict[naddr]
                # print("n = ", n)
                if 'pnode' in n and n['pnode'] != n['address'] :
                    if 'members' not in self._nodedict[n['pnode']] :
                        self._nodedict[n['pnode']]['members'] = list ()
                    self._nodedict[n['pnode']]['members'].append( n['address'] )

                if 'parent' in n :
                    if 'pnode' not in n or n['parent'] != n['pnode'] :
                        if n['parent-type'] == 3 :
                            if n['parent'] in self._folderlist :
                                self._folderlist[n['parent']]['members'].append( n['address'])
                        elif  n['parent-type'] == 1 :
                            if n['parent'] in self._nodegroups :
                                self._nodegroups[n['parent']]['members'].add( n['address'])
                # 'parent': '16 6C D2 1', 'parent-type': '1',
                # 'parent': '12743', 'parent-type': '3',
                # if n.pnode == n.parent and n.pnode == n.address
                    next



    def _gen_folder_list(self, nodeinfo) :
        """ generate folder dictionary for load_node """
        # self._folderlist = dict ()
        self.folder2addr = dict ()
        for fold in nodeinfo.iter('folder'):

	    xelm = fold.find('address')
	    if hasattr(xelm, 'text') :
		if xelm.text in self._nodegroups :
		    fprop = self._folderlist[xelm.text]
		else :
		    fprop = self._folderlist[xelm.text] = dict()
	    else :
		warn("Error : no address in folder", RuntimeWarning)
		continue


            for k, v in fold.items() :
                fprop[fold.tag + "-" + k] = v
            for child in list(fold):
                fprop[child.tag] = child.text
                if child.attrib :
                    for k, v in child.items() :
                        fprop[child.tag + "-" + k] =  v
            # self._folderlist[fprop["address"]] = fprop
            self.folder2addr[fprop["name"]] = fprop["address"]
        #self._printdict(self._folderlist)
        #self._printdict(self.folder2addr)

    def _gen_nodegroups(self, nodeinfo) :
        """ generate scene / group dictionary for load_node """
        # self._nodegroups = dict ()
        self.groups2addr = dict ()
        for grp in nodeinfo.iter('group'):

	    xelm = grp.find('address')
	    if hasattr(xelm, 'text') :
		if xelm.text in self._nodegroups :
		    gprop = self._nodegroups[xelm.text]
		else :
		    gprop = self._nodegroups[xelm.text] = dict()
	    else :
		warn("Error : no address in scene", RuntimeWarning)
		continue


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
                # self._nodegroups[gprop["address"]] = gprop
                if "name" in gprop :
                    if gprop["name"] in self.groups2addr :
			warn("Duplicate group name (0) : (1) (2)".format(gprop["name"], \
				str(gprop["address"]), self.groups2addr[gprop["name"]]), RuntimeWarning)
                    else :
                        self.groups2addr[gprop["name"]] = str(gprop["address"])
            else :
                # should raise an exception ?
                self._printinfo(grp, "Error : no address in group :")


    def _gen_nodedict(self, nodeinfo) :
        """ generate node dictionary for load_node """
	self.node2addr = dict()
        for inode in nodeinfo.iter('node'):
            # self._printinfo(inode, "\n\n inode")

	    xelm = inode.find('address')
	    if hasattr(xelm, 'text') :
		if xelm.text in self._nodedict :
		    idict = self._nodedict[xelm.text]
		else :
		    idict = self._nodedict[xelm.text] = dict()
	    else :
		warn("Error : no address in node", RuntimeWarning)
		continue


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
		    if child.tag not in idict :
			idict[child.tag] = dict ()
                    nprop = dict ()
                    for k, v in child.items() :
                        # print("child.items", k, v)
                        nprop[k] = v
                    if "id" in nprop :
                        idict[child.tag][nprop["id"]] = nprop
                else :
                    idict[child.tag] = child.text

            if "address" in idict :
                # self._nodedict[idict["address"]] = idict
                if "name" in idict :
                    if idict["name"] in self.node2addr :
			warn_mess = "Duplicate Node name (0) : (1) (2)".format(idict["name"], \
				idict["address"], self.node2addr[idict["name"]])
			warn(warn_mess, RuntimeWarning)
                    else :
                        self.node2addr[idict["name"]] = idict["address"]

            else :
                # should raise an exception
                # self._printinfo(inode, "Error : no address in node :")
                warn("Error : no address in node", RuntimeWarning)
        #print("\n>>>>\t", self._nodedict, "\n<<<<<\n")



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
        return self.node2addr[:]

    def scene_names(self) :
        """ access method for scene names
            returns a dict of ( Node names : Node address )
        """
        try:
            self.groups2addr
        except AttributeError:
            self.load_nodes()
        return self.groups2addr[:]

    def node_addrs(self) :
        """ access method for node addresses
            returns a iist scene/group addresses
        """
        try:
            self._nodedict
        except AttributeError:
            self.load_nodes()
        return self._nodedict.viewkeys()

    def scene_addrs(self) :
        """ access method for scene addresses
            returns a iist scene/group addresses
        """
        try:
            self._nodegroups
        except AttributeError:
            self.load_nodes()
        return self._nodegroups.viewkeys()


    def get_node(self, node_id) :
        """ Get a Node object for given node or scene name or ID

            args:
                node : node name of id

            return:
                An IsyNode object representing the requested Scene or Node

        """
        if self.debug & 0x01 :
            print("get_node")

        nodeid = self._get_node_id(node_id)
        if nodeid in self._nodedict :
            if not nodeid in self.nodeCdict :
                self.nodeCdict[nodeid] = IsyNode(self, self._nodedict[nodeid])
            return self.nodeCdict[nodeid]

        elif nodeid in self._nodegroups:
            if not nodeid in self.nodeCdict :
                self.nodeCdict[nodeid] = IsyScene(self, self._nodegroups[nodeid])
            return self.nodeCdict[nodeid]

        elif nodeid in self._nodegroups:
            if not nodeid in self.nodeCdict :
                self.nodeCdict[nodeid] = IsyScene(self, self._nodegroups[nodeid])
            return self.nodeCdict[nodeid]

        else :
            print("Isy get_node no node : \"%s\"" % nodeid)
            raise LookupError("no node such Node : " + str(nodeid) )


    def _get_node_id(self, nid):
        """ node/scene/Folder name to node/scene/folder ID """

	try:
	    self._nodedict
	except AttributeError:
	    self.load_nodes()

        if isinstance(nid, IsySubClass) :
             return nid["addr"]
        else :
            n = str(nid)
        if string.upper(n) in self._nodedict :
            # print("_get_node_id : " + n + " nodedict " + string.upper(n))
            return string.upper(n)

        if n in self.node2addr :
            # print("_get_node_id : " + n + " node2addr " + self.node2addr[n])
            return self.node2addr[n]

        if n in self.groups2addr :
            # print("_get_node_id : " + n + " groups2addr " + self.groups2addr[n])
            return self.groups2addr[n]

        if n in self._nodegroups :
            # print("_get_node_id : " + n + " nodegroups " + n)
            return n

        if n in self.folder2addr :
            # print("_get_node_id : " + n + " folder2addr " + self.folder2addr[n])
            return self.folder2addr[n]

        if n in self._folderdict :
            # print("_get_node_id : " + n + " folderdict " + n)
            return n


	    # Fail #
        print("_get_node_id : " + n + " None")
        return None

    def _get_control_id(self, comm):
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
    # Get property for a node
    #
    def node_get_prop(self, naddr, prop) :
	#<isQueryAble>true</isQueryAble>
	pass

    # Set property for a node
    #
    def node_set_prop(self, naddr, prop, val) :
        """ calls /rest/nodes/<node-id>/set/<property>/<value> """
        if self.debug & 0x01 :
            print("node_set_prop")

        node_id = self._get_node_id(naddr)

	prop_id = _get_control_id(prop);

        if not node_id :
            raise LookupError("node_set_prop: unknown node : " + str(naddr) )

        if not prop_id :
            raise TypeError("node_comm: unknown prop : " + str(cmd) )

	if "readOnly" in self.controls[prop_id] and \
		    self.controls["prop_id"]["readOnly"] == "true" :
	    IsyPropertyError("readOnly property " + prop_id)

	    # <isNumeric>true</isNumeric>

#        if not prop in ['ST', 'OL', 'RR'] :
#            raise TypeError("node_set_prop: unknown propery : " + str(prop) )

        # if val :
        #       pass
        self._node_send(naddr, "set", prop, val)

    def _node_send(self, naddr, action,  prop, val) :
        """ node_set_prop after argument validation """
        #print("_node_set_prop : node=%s prop=%s val=%s" % str(naddr), prop, val)
        print ("_node_set_prop : node=" + str(naddr) + " prop=" + prop +
                    " val=" + val )
        xurl = "/rest/nodes/" + naddr + "/" + action + "/" + prop + "/" + val
        resp = self._getXMLetree(xurl)
        self._printXML(resp)
        if resp.attrib["succeeded"] != 'true' :
            raise IsyResponseError("Node Property Set error : node=%s prop=%s val=%s" %
                    naddr, prop, val )

    def _node_set_prop(self, naddr, prop, val) :
        """ node_set_prop without argument validation """
        #print("_node_set_prop : node=%s prop=%s val=%s" % str(naddr), prop, val)
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
            print("node_comm", naddr, cmd)
        node_id = self._get_node_id(naddr)
        cmd_id = self._get_control_id(cmd)

        #print("self.controls :", self.controls)
        #print("self.name2control :", self.name2control)

        if not node_id :
            raise LookupError("node_comm: unknown node : " + str(naddr) )
        print("naddr : ", naddr, " : ", node_id)

        if not cmd_id :
            raise TypeError("node_comm: unknown command : " + str(cmd) )

        #self._node_comm(node_id, cmd_id, args)
        self._node_send(node_id, "cmd", cmd_id, args)

    #
    # Send command to Node without all the arg checking
    #
    def _node_comm(self, node_id, cmd_id, *args) :
        """ send command to a node or scene without name to ID overhead """
        if self.debug & 0x04 :
            print("_node_comm", node_id, cmd_id)
        # rest/nodes/<nodeid>/cmd/<command_name>/<param1>/<param2>/.../<param5>
        xurl = ("/rest/nodes/" + node_id + "/cmd/" + cmd_id +
            "/" + "/".join(str(x) for x in args) )

        if self.debug & 0x02 :
                print("xurl = " + xurl)
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
            print("_updatenode pre _getXML")
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
            print("load_node_types called")
        typeinfo = self._getXMLetree("/WEB/cat.xml")
	if not hasattr(self, 'nodeCategory') or not isinstance(self.nodeCategory, dict):
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
                # print("ID : ", ncat.attrib["id"], " : ", subcat.attrib["id"])
                # print("ID  name: ", subcat.attrib["name"])
                self.nodeCategory[ncat.attrib["id"]][subcat.attrib["id"]] = subcat.attrib["name"]
                #self._printinfo(subcat, "subcat :")
        # print("nodeCategory : ", self.nodeCategory)
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
    ## ISY Programs Code
    ##
    def load_prog(self):
        """ Load Program status and Info

            args : none

            internal function call

        """
        if self.debug & 0x01 :
            print("load_prog called")
        prog_tree = self._getXMLetree("/rest/programs?subfolders=true", 1)
	if not hasattr(self, '_progdict') or not isinstance(self._progdict, dict):
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
                    print("Dup name : \"" + n + "\" ", pdict["id"])
                    print("name2prog ", self.name2prog[n])
                else :
                    self.name2prog[n] = pdict["id"]
        #self._printdict(self._progdict)
        #self._printdict(self.name2prog)



    def get_prog(self, pname) :
        """ get prog class obj """
        if self.debug & 0x01 :
            print("get_prog :" + pname)
        try:
            self._progdict
        except AttributeError:
            self.load_prog()
#       except:
#           print("Unexpected error:", sys.exc_info()[0])
#           return None
        finally:
            progid = self._prog_get_id(pname)
            # print("\tprogid : " + progid)
            if progid in self._progdict :
                if not progid in self.progCdict :
                    # print("not progid in self.progCdict:")
                    # self._printdict(self._progdict[progid])
                    self.progCdict[progid] = IsyProgram(self, self._progdict[progid])
                #self._printdict(self._progdict)
                # print("return : ",)
                #self._printdict(self.progCdict[progid])
                return self.progCdict[progid]
            else :
                if self.debug & 0x01 :
                    print("Isy get_prog no prog : \"%s\"" % progid)
                raise LookupError("no prog : " + str(progid) )

    def _prog_get_id(self, pname):
        """ Lookup prog value by name or ID
        returns ISY Id  or None
        """
        if isinstance(pname, IsyProgram) :
             return pname["id"]
        else :
            p = str(pname)
        if string.upper(p) in self._progdict :
            # print("_get_prog_id : " + p + " progdict " + string.upper(p))
            return string.upper(p)
        if p in self.name2prog :
            # print("_prog_get_id : " + p + " name2prog " + self.name2prog[p])
            return self.name2prog[p]

        # print("_prog_get_id : " + n + " None")
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
#           print("Unexpected error:", sys.exc_info()[0])

        k = self._progdict.keys()
        for v in k :
            yield self.get_prog(v)

    def prog_comm(self, paddr, cmd) :
        valid_comm = ['run', 'runThen', 'runElse', 'stop',
                        'enable', 'disable',
                        'enableRunAtStartup', 'disableRunAtStartup']
        prog_id = self._get_prog_id(paddr)

        #print("self.controls :", self.controls)
        #print("self.name2control :", self.name2control)

        if not prog_id :
            raise IsyInvalidCmdError("prog_comm: unknown node : " +
                str(paddr) )

        if not cmd in valid_comm :
            raise IsyInvalidCmdError("prog_comm: unknown command : " +
                str(cmd) )

        self._prog_comm(prog_id, cmd)

    def _prog_comm(self, prog_id, cmd) :
        """ send command to a program without name to ID overhead """
        # /rest/programs/<pgm-id>/<pgm-cmd>
        xurl = "/rest/programs/" + prog_id + cmd 

        if self.debug & 0x02 :
            print("xurl = " + xurl)

        resp = self._getXMLetree(xurl)
        self._printXML(resp)
        if resp.attrib["succeeded"] != 'true' :
            raise IsyResponseError("ISY command error : prog_id=" +
                str(prog_id) + " cmd=" + str(cmd))


    # redundant
    def _updatenode(self, naddr) :
        """ update a node's property from ISY device """
        xurl = "/rest/nodes/" + self._nodedict[naddr]["address"]
        if self.debug & 0x01 :
            print("_updatenode pre _getXML")
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
    def load_log_type(self):
        pass

    def load_log_id(self):
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
            print("xurl = " + xurl)
        req = URL.Request(xurl)
        res = self._opener.open(req)
        data = res.read()
        res.close()
        return data.splitlines()

    def log_format_line(self, line) :
        """ format a ISY log line into a more human readable form """
        pass


    ##
    ## X10 Code
    ##
    _x10re = re.compile('([a-pA-P]\d{,2)')
    _x10comm = { 'alllightsoff' : 1,
        'status off' : 2,
        'on' : 3,
        'Preset dim' : 4,
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
        if comm in self._x10comm :
            return self._x10comm[comm]
        else :
            raise IsyValueError("unknown x10 command : " + comm)


    def x10_comm(self, unit, cmd) :
        """ direct send x10 command """
        xcmd = self._get_x10_comm_id(str(cmd))
        unit = unit.upper()

        if not re.match("[A-P]\d{,2}", unit) :
            raise IsyValueError("bad x10 unit name : " + unit)

        print("X10 sent : " + str(unit) + " : " + str(xcmd))
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
        print("\n\n" + ulabel + " : ")
        for attr in dir(uobj) :
            print("   obj.%s = %s" % (attr, getattr(uobj, attr)))
        print("\n\n")


    ##
    ## Special Methods
    ##

    # Design question :
    # should __get/setitem__  return a node obj or a node's current value ?
    def __getitem__(self, nodeaddr):
        """ access node obj line a dictionary entery """
        if nodeaddr in self.nodeCdict :
            return self.nodeCdict[str(nodeaddr).upper()]
        else :
            return self.get_node(nodeaddr)

    def __setitem__(self, nodeaddr, val):
        """ This allows you to set the status of a Node by
	addressing it as dictionary entery """
        # print("__setitem__ : ", nodeaddr, " : ", val)
        self.node_set_prop(nodeaddr, val, "ST")

    def __delitem__(self, nodeaddr):
        raise IsyProperyError("__delitem__ : can't delete nodes :  " + str(prop) )

    def __iter__(self):
        """ iterate though Node Obj (see: node_iter() ) """
        return self.node_iter()

    def __del__(self):
        #if isinstance(self._isy_event, ISYEvent) :
	#    #ISYEvent._stop_event_loop()
	if hasattr(self._isy_event, "_shut_down") :
	    self._isy_event._shut_down = 1


    def __repr__(self):
        return "<Isy %s at 0x%x>" % (self.addr, id(self))

#    def debugerror(self) :
#       print("debugerror")
#        raise IsyProperyError("debugerror : test IsyProperyError  ")

    def _printdict(self, dic):
        """ Pretty Print dictionary """
        print("===START===")
        pprint.pprint(dic)
        print("===END===")

    def _writedict(self, d, filen):
        """ Pretty Print dict to file  """
        fi = open(filen, 'w')
        pprint(d)
        fi.close()



def log_time_offset() :
    lc_time = time.localtime()
    gm_time = time.gmtime()
    return ((lc_time[3] ) - (gm_time[3] - gm_time[8])) * 60 * 60
    # index 3 represent the hours
    # index 8 represent isdst (daylight saving time boolean (0/1))

#
# Do nothing
# (syntax check)
#
if __name__ == "__main__":
    import __main__
    print(__main__.__file__)

    print("syntax ok")
    exit(0)
