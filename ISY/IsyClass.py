"""Simple Python lib for the ISY home automation netapp

 This is a Python interface to the ISY rest interface
 providomg simple commands to query and control registared Nodes and Scenes
 and well as a method of setting or querying vars
 
"""
__author__ = 'Peter Shipley <peter.shipley@gmail.com>'
__copyright__ = "Copyright (C) 2013 Peter Shipley"
__license__ = "BSD"



#from xml.dom.minidom import parse, parseString
# from StringIO import StringIO
# import xml.etree.ElementTree as # ET
# import base64
import re
import os
import sys
#import string
import pprint
import time
from warnings import warn
import logging
import xml.etree.ElementTree as ET


#logging.basicConfig(level=logging.INFO)


import collections



#try:
#    from suds.client import Client
#    suds_import = 1
#except ImportError :
#    suds_import = 0




if sys.hexversion < 0x3000000 :
    import urllib2 as URL
    # HTTPPasswordMgrWithDefaultRealm = URL.HTTPPasswordMgrWithDefaultRealm
    # Request, build_opener, request, HTTPBasicAuthHandler, HTTPPasswordMgrWithDefaultRealm, URLError, HTTPError

else :
    import urllib as URL
    from urllib.request import HTTPPasswordMgrWithDefaultRealm

from ISY.IsyUtilClass import IsyUtil, IsySubClass, et2d
# from ISY.IsyNodeClass import IsyNode, IsyScene, IsyNodeFolder, _IsyNodeBase
from ISY.IsyProgramClass import *
#from ISY.IsyVarClass import IsyVar
from ISY.IsyExceptionClass import  *
from ISY.IsyEvent import ISYEvent

# import netrc

# Debug Flags:
# 0x01 = report loads
# 0x02 = report urls used
# 0x04 = report func call
# 0x08 = Dump loaded data
# 0x10 = report changes to nodes
# 0x20 = report soap web
# 0x40 =
# 0x80 = print __del__()
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

_pro_models = [ 1100, 1110, 1040, 1050 ]

__all__ = ['Isy', 'IsyGetArg']



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

    from ISY._isyclimate import load_clim, clim_get_val, clim_query, clim_iter
    from ISY._isyvar  import load_vars, var_set_value, _var_set_value, \
		var_get_value, var_addrs, get_var, _var_get_id, \
		var_get_type, var_iter
    from ISY._isyprog import load_prog, get_prog, _prog_get_id, \
		prog_iter, prog_comm, _prog_comm
    from ISY._isynode import load_nodes, _gen_member_list, _gen_folder_list, \
		_gen_nodegroups, _gen_nodedict, node_names, scene_names, \
		node_addrs, scene_addrs, get_node, _node_get_id, node_get_prop, \
		node_set_prop, _node_send, node_comm, _updatenode, \
		load_node_types, node_get_type, node_iter, _updatenode
    from ISY._isynet_resources import _load_networking, load_net_resource, \
		_net_resource_get_id, net_resource_run, \
		net_resource_names, net_resource_iter, \
		load_net_wol, net_wol, _net_wol_get_id, net_wol_names, net_wol_iter



##    set_var_value, _set_var_value, var_names


    if sys.hexversion < 0x3000000 :
        _password_mgr = URL.HTTPPasswordMgrWithDefaultRealm()
        _handler = URL.HTTPBasicAuthHandler(_password_mgr)
        _opener = URL.build_opener(_handler)

	# URL.HTTPHandler(debuglevel=1) 
    else:
        _password_mgr = URL.request.HTTPPasswordMgrWithDefaultRealm()
        _handler = URL.request.HTTPBasicAuthHandler(_password_mgr)
        _opener = URL.request.build_opener(_handler)

    def __init__(self, **kwargs):
        #
        # Keyword args
        #
	self.userl = kwargs.get("userl", os.getenv('ISY_USER', "admin"))
	self.userp = kwargs.get("userp", os.getenv('ISY_PASS', "admin"))
        self.addr = kwargs.get("addr", os.getenv('ISY_ADDR', None))

	# print "AUTH: ", self.addr, self.userl, self.userp

        self.debug = kwargs.get("debug", 0)
        self.cachetime = kwargs.get("cachetime", 0)
        self.faststart = kwargs.get("faststart", 1)
        self.eventupdates = kwargs.get("eventupdates", 0)
	self._isy_event = None
	self.error_str = ""
	self.callbacks = dict ()
        self._is_pro = True


	# data dictionaries for ISY state
	self.controls = None
	self.name2control = None
	self._folderlist = None
	self._progdict = None      
	self._nodedict = None
	self._nodegroups = None
	self.groups2addr = None
	self.node2addr = None
	self.nodeCategory = None
	self._vardict = None        
	self.wolinfo = None
	self.net_resource = None
	self.climateinfo  = None

        if self.addr == None :
            from ISY.IsyDiscover import isy_discover

            units = isy_discover(count=1) 
            for device in units.values() :
                self.addr = device['URLBase'][7:]
                self.baseurl = device['URLBase']
        else :
            self.baseurl = "http://" + self.addr

        if self.addr == None :
	    warn("No ISY address : guessing \"isy\"")
	    self.addr = "isy"

#	print "\n\taddr", "=>", self.addr, "\n\n"


#	if ( not self.userl or not self.userp ) :
#	    netrc_info = netrc.netrc()
#	    login, account, password = netrc_info.authenticators(self.addr)
#	    print "login", "=>", repr(login)
#	    print "account", "=>", repr(account)
#	    print "password", "=>", repr(password)
#	    self.userl = "admin"
#	    self.userp = "admin"

        if self.debug & 0x01 :
            print("class Isy __init__")
            print("debug ", self.debug)
            print("cachetime ", self.cachetime)
            print("faststart ", self.faststart)

        # parse   ISY_AUTH as   LOGIN:PASS

        #
        # general setup logic
        #
        Isy._handler.add_password(None, self.addr, self.userl, self.userp)
        # self._opener = URL.build_opener(Isy._handler, URL.HTTPHandler(debuglevel=1))
        # self._opener = URL.build_opener(Isy._handler)
        if self.debug & 0x02:
            print("baseurl: " + self.baseurl + " : " + self.userl + " : " + self.userp)

	if self.faststart < 2 :
	    try:
		self.load_conf()
	    except URL.URLError as e:
		print("Unexpected error:", sys.exc_info()[0])
		print 'Problem connecting with ISY device :', self.addr
		print e
		raise IsyCommunicationError(e)


        if not self.faststart :
            self.load_nodes()

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

	mask will eventually be used to "masking" events


        """
        from threading import Thread

	# if thread already runing we should update mask
	if hasattr(self, 'event_thread') and isinstance(self.event_thread, Thread) :
	    if self.event_thread.is_alive() :
		print "Thread already running ?"
		return

	#st = time.time()
        #print("start preload")

        self._preload(rload=0)

	#sp = time.time()
        #print("start complete")
	#print "load in ", ( sp - st )

        self._isy_event = ISYEvent()
        self._isy_event.subscribe(self.addr)
        self._isy_event.set_process_func(self._read_event, self)
        
        self.event_thread = Thread(target=self._isy_event.events_loop, name="event_looper" )
        self.event_thread.daemon = True
        self.event_thread.start()

        self.eventupdates = True
        # print(self.event_thread)

    def stop_event_tread(self) :
	""" Stop update thread """
	if hasattr(self._isy_event, "_shut_down") :
	    self._isy_event._shut_down = 1
        self.eventupdates = False

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

        assert isinstance(evnt_dat, dict), "_read_event Arg must me dict"

	event_targ = None
        if evnt_dat["control"] in skip :
            return

	#
	# Status/property changed
	#
        if evnt_dat["control"] in ["ST", "RR", "OL"] :
            if evnt_dat["node"] in self._nodedict :
		# ADD LOCK ON NODE DATA
                # print("===evnt_dat :", evnt_dat)
                # print("===a :", ar)
                #print(self._nodedict[evnt_dat["node"]])
                target_node =  self._nodedict[evnt_dat["node"]]

		event_targ = evnt_dat["node"]

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

	#
        # handle VAR value change
	#
        elif evnt_dat["control"] == "_1" :
            # Var Status / Initialized
            if evnt_dat["action"] == "6" or  evnt_dat["action"] == "7" :
                var_eventInfo =  evnt_dat['eventInfo']['var']
                vid = var_eventInfo['var-type'] + ":" + var_eventInfo['var-id']

                # check if the event var exists in out world
                if vid in self._vardict :
		    # ADD LOCK ON VAR DATA
                    # copy var properties from event

		    event_targ = vid

		    self._vardict[vid].update(var_eventInfo)
		    self._vardict[vid]["val"]  = int(self._vardict[vid]["val"])
		    self._vardict[vid]["init"] = int(self._vardict[vid]["init"])

                else :
                    warn("Event for Unknown Var : {0}".format(vid), RuntimeWarning)

        else:
            print("evnt_dat :", evnt_dat)
            print("Event fall though : '{0}'".format(evnt_dat["node"]))

	if event_targ in self.callbacks :
	    cb = self.callbacks[event_targ]
	    if isinstance(cb[0], collections.Callable) :
		cb[0](evnt_dat, *cb[1])
	    else :
		warn("callback for {0} not callable, deleting callback".format(event_targ),
                        RuntimeWarning)
		del self.callbacks[event_targ]

	return



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



    def node_rename(self, nid, nname) :
	""" rename Node

		args: 
		    id = Node ID
		    name = new Node name

	    calls SOAP RenameNode()
	"""
	nid = self._node_get_id(nid)
	return self.soapcomm("RenameNode", id=nid, name=nname)


#    def node_new(self, id, nname) :
#	""" create new Folder """
#	return  self.soapcomm("AddNode", id=1234, name=nname, type="T", flag="Y")

    ## scene

    def scene_rename(self, fid, fname) :
	""" rename Scene/Group

		args: 
		    id = a Scene/Group id
		    name = new name 


	    calls SOAP RenameGroup()
	"""
	fid = self._node_get_id(fid)
	return self.soapcomm("RenameGroup", id=fid, name=fname)

    def scene_del(self, sid=None ) :
	""" delete Scene/Group 

		args: 
		    id : Scene address, name or Folder Obj

	    calls SOAP RemoveGroup()
	"""
	sceneid = self._node_get_id(sid)
	if sceneid == None :
	    raise IsyValueError("no such Scene : " + str(sid) )
	#
	# add code to update self._nodegroups
	#
	return  self.soapcomm("RemoveGroup", id=sceneid)

    def scene_new(self, nid=0, sname=None) :
	""" new Scene/Group

		args: 
		    id = a unique (unused) Group ID
		    name = name for new Scene/Group

	    ***No error is given if Scene/Group ID is already in use***

	    calls SOAP AddGroup()
	"""
	if not isinstance(sname, str) or not len(sname) :
	    raise IsyValueError("scene name must be non zero length string")

	if nid == 0 :
	    iid = 30001
	    nid = str(iid)
	    while nid in self._folderlist or nid in self._nodegroups :
		iid += 1
		nid=str(iid)
	self.soapcomm("AddGroup", id=nid, name=sname)
	#
	# add code to update self._nodegroups
	#
	return nid

    def scene_add_node(self, groupid, nid, nflag=0x10) :
	""" add node to Scene/Group

		args: 
		    group = a unique (unused) scene_id ID
		    node = id, name or Node Obj
		    flag = set to 0x10 if node it a controler for Scene/Group

	    Add new Node to Scene/Group 


	    calls SOAP MoveNode()
	"""
	nodeid = self._node_get_id(nid)
	if nodeid == None :
	    raise IsyValueError("no such Node : " + str(nid) )
	r = self.soapcomm("MoveNode", group=groupid, node=nodeid, flag=nflag)
	return r

    def scene_del_node(self, groupid, nid) :
	""" Remove Node from Scene/Group

		args:
		    group = address, name or Scene Obj
		    id = address, name or Node Obj

	    calls SOAP RemoveFromGroup()
	"""
	nodeid = self._node_get_id(nid)
	if nodeid == None :
	    raise IsyValueError("no such Node : " + str(nid) )
	r = self.soapcomm("RemoveFromGroup", group=groupid, id=nodeid)
	return r

    ## folder

    def folder_rename(self, fid, fname) :
	""" rename Folder

		args: 
		    id = folder ID
		    name = new folder name

	    calls SOAP RenameFolder()
	"""
	fid = self._node_get_id(fid)
	r = self.soapcomm("RenameFolder", id=fid, name=fname)
	return r

    def folder_new(self, fid, fname) :
	""" create new Folder

		args: 
		    folder_id = a unique (unused) folder ID
		    folder name = name for new folder


	    returns error if folder ID is already in use

	    calls SOAP AddFolder()
	"""
	if fid == 0 :
	    iid = 50001
	    fid = str(iid)
	    while fid in self._folderlist or fid in self._nodegroups :
		iid += 1
		fid = str(iid)
	r = self.soapcomm("AddFolder", fid=1234, name=fname)
	if  isinstance(r, tuple) and r[0] == '200' :
	    self._folderlist[fid] = dict()
	    self._folderlist[fid]['address'] = fid
	    self._folderlist[fid]['folder-flag'] = '0'
	    self._folderlist[fid]['name'] = 'fname'

	return r

    def folder_del(self,fid) :
	""" delete folder
		args: 
		    fid : folder address, name or Folder Obj

	    calls SOAP RemoveFolder()
	"""
	fid = self._node_get_id(fid)
	if fid == None :
	    raise IsyValueError("Unknown Folder : " + str(fid) )
	r = self.soapcomm("RemoveFolder", id=fid)
	if  isinstance(r, tuple) and r[0] == '200' :
	    self._folderlist[fid] = dict()

    # SetParent(node, nodeType, parent, parentType )
    def folder_add_node(self, nid, nodeType=1, parent="", parentType=3) :
	""" move node/scene from folder 

	    Named args:
		node
		nodeType
		parent
		parentType

	    sets Parent for node/scene 

	    calls SOAP SetParent()
	"""
	nodeid = self._node_get_id(nid)
	if nodeid == None :
	    raise IsyValueError("no such Node/Scene : " + str(nid) )

	if parent != "" :
	    fldid = self._node_get_id(parent)
	    if fldid == None :
		raise IsyValueError("no such Folder : " + str(parent) )
	    parentid = fldid
	else :
	    parentid = parent

	r = self.soapcomm("SetParent", node=nodeid, nodeType=nodeType, parent=parentid, parentType=parentType)
	return r

    def folder_del_node(self, nid, nodeType=1) :
	""" remove node from folder

	    Named args:
		node
		nodeType

	    remove node/scene from folder ( moves to default/main folder )

	    calls SOAP SetParent()
	"""
	return self.folder_add_node(nid, nodeType=nodeType, \
		parent="", parentType=3)

    def reboot(self) :
	""" Reboot ISY Device
		args: none

	    calls SOAP Reboot() 
	"""
	return self.soapcomm("Reboot")

    #
    # User web  commands
    #
    def user_fsstat(self) :
	""" ISY Filesystem Status

	    calls SOAP GetFSStat()
	"""
	r = self.soapcomm("GetFSStat")
	return et2d( ET.fromstring(r))
     

    def user_dir(self, name="", pattern="") :
	""" Get User Folder/Directory Listing

	    Named args:
		name
		pattern

	    call SOAP GetUserDirectory()
	"""
	r = self.soapcomm("GetUserDirectory", name=name, pattern=pattern)
	# print "GetUserDirectory : ", r
	return et2d( ET.fromstring(r))

    def user_mkdir(self, name=None) :
	""" Make new User Folder/Directory

	    Named args:
		name

	    call SOAP MakeUserDirectory()
	"""
	if name == None :
	    raise IsyValueError("user_mkdir : invalid dir name")
	if name[0] != "/" :
	    name = "/USER/WEB/" + name
	r = self.soapcomm("MakeUserDirectory", name=name)
	return et2d( ET.fromstring(r))

    def user_rmdir(self, name=None) :
	""" Remove User Folder/Directory

	    Named args:
		name

	    call SOAP RemoveUserDirectory()
	"""
	if name == None :
	    raise IsyValueError("user_rmdir : invalid dir name")
	name = name.rstrip('/')
	if name[0] != "/" :
	    name = "/USER/WEB/" + name
	r = self.soapcomm("RemoveUserDirectory", name=name)
	return et2d( ET.fromstring(r))


    def user_mv(self, name=None, newName=None) :
	""" Move/Rename User Object (File or Directory)

	    Named args:
		oldn
		newn

	    call SOAP MoveUserObject()
	"""
	if name == None or newName == None :
	    raise IsyValueError("user_mv : invalid name")
	if name[0] != "/" :
	    name = "/USER/WEB/" + name
	if newName[0] != "/" :
	    newName = "/USER/WEB/" + newName
	r = self.soapcomm("MoveUserObject", name=name, newName=newName)
	return r

    def user_rm(self, name=None) :
	""" Remove User File

	    Named args:
		name

	    call SOAP RemoveUserFile()
	"""
	if name == None :
	    raise IsyValueError("user_mkdir : invalid name")
	if name[0] != "/" :
	    name = "/USER/WEB/" + name
	r = self.soapcomm("RemoveUserFile", name=name)
	return(r)

    def user_getfile(self, name=None) :
	""" Get User File

	    Named args:
		name

	    call SOAP GetUserFile()
	"""
	if not len(name) :
	    raise IsyValueError("user_getfile : invalid name")
	if name[0] != "/" :
	    name = "/USER/WEB/" + name

	r = self.soapcomm("GetUserFile", name=name)
	return r


    def user_uploadfile(self, srcfile="", name=None, data="") :
	""" upload User File

	    Named args:
		name : name of file after upload
		data : date to upload 
		srcfile : file containing data to upload

	    srcfile is use only if data is not set
	    if both data & srcfile are not set then
	    the file "name" is used

	    calls /file/upload/...
	"""
	if name == None :
	    raise IsyValueError("user_uploadfile : invalid name")
	r = self.sendfile(src=srcfile, filename=name, data=data)
	return r

    #
    #  Util Funtions
    #
    def _preload(self, rload=0):
	""" Internal function

	    preload all data tables from ISY device into cache
	    normally this is done "on demand" as needed
	"""
	if rload or  not hasattr(self, "controls") :
	    self.load_conf()

	if rload or not hasattr(self, "_nodedict") :
	    self.load_nodes()

        # self._gen_member_list()
	# if rload or  not hasattr(self, "climateinfo") :
	    # self.load_clim()

	if rload or  not hasattr(self, "_vardict") :
	    self.load_vars()

	if rload or  not hasattr(self, "_progdict") :
	    self.load_prog()

	# if rload or  not hasattr(self, "wolinfo") :
	    #self.load_wol()

	if rload or  not hasattr(self, "nodeCategory") :
	    self.load_node_types()

    def _savedict(self) :
	""" internal debug command """

        self._preload()

        # self._writedict(self.wolinfo, "wolinfo.txt")

        self._writedict(self._nodedict, "nodedict.txt")

        self._writedict(self._nodegroups, "nodegroups.txt")

        self._writedict(self._folderlist, "folderlist.txt")

        self._writedict(self._vardict, "vardict.txt")

        # self._writedict(self.climateinfo, "climateinfo.txt")

        self._writedict(self.controls, "controls.txt")

        self._writedict(self._progdict, "progdict.txt")

        self._writedict(self.nodeCategory, "nodeCategory.txt")



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
        configinfo = self._getXMLetree("/rest/config")
        # Isy._printXML(configinfo)
	# IsyCommunicationError

        self.name2control = dict ( )
        self.controls = dict ( )
        for ctl in configinfo.iter('control') :
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
        for v in ( "platform", "app_version", "driver_timestamp",
		    "app", " build_timestamp" ):
            n = configinfo.find(v)
            if not n is None:
                if isinstance(n.text, str):
                    self.config[v] = n.text
	xelm = configinfo.find("product/id")
	if not xelm is None:
	    if hasattr(xelm, 'text') :
		self.config["product_id"] = xelm.text


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

    def _get_control_id(self, comm):
        """ command name to command ID """
	if not self.controls :
            self.load_conf()

        c = comm.strip().upper()
        if c in self.controls :
            return c
        if c in self.name2control :
            return self.name2control[c]
        return None


    ##
    ## Logs
    ##
    def load_log_type(self):
        """ load log type tables

	    args: None

	**not implemented **
	"""
	pass

    def load_log_id(self):
        """ load log id tables

	**not implemented **
	"""
        pass

    def log_reset(self, errorlog = 0 ):
        """ clear log lines in ISY

	    args:
		errorlog = flag clear error

	""" 
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
        """ format a ISY log line into a more human readable form

	** not implemented **
	"""
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
        comm = str(comm).strip().lower()
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
        unit = unit.strip().upper()

        if not re.match("[A-P]\d{,2}", unit) :
            raise IsyValueError("bad x10 unit name : " + unit)

        print("X10 sent : " + str(unit) + " : " + str(xcmd))
        xurl = "/rest/X10/" + str(unit) + "/" + str(xcmd)
        if self.debug & 0x02 : print("xurl = " + xurl)
        resp = self._getXMLetree(xurl)
        #self._printXML(resp)
        #self._printinfo(resp)
        if resp.attrib["succeeded"] != 'true' :
            raise IsyResponseError("X10 command error : unit=" + str(unit) + " cmd=" + str(cmd))

# /rest/time
#	Returns system time
#
#/rest/network
#    Returns network configuration
# /rest/sys
#	returns system configuration
#
# /rest/subscriptions
# Returns the state of subscriptions

    def subscriptions(self) :
	"""  get event subscriptions list and states

	    args: none

	Returns the state of subscriptions

	calls : /rest/subscriptions
	"""
	xurl = "/rest/subscriptions"
        if self.debug & 0x02 : print("xurl = " + xurl)
	resp = self._getXMLetree(xurl)
	self._printXML(resp)
	return et2d(resp)

    def network(self) :
	""" network configuration

	    args: none

	Returns network configuration
	calls /rest/network
	"""

	xurl = "/rest/network"
        if self.debug & 0x02 : print("xurl = " + xurl)
	resp = self._getXMLetree(xurl)
	self._printXML(resp)
	return et2d(resp)

    def sys(self) :
	""" system configuration

	    args: none

	calls : /rest/sys
	"""  
	xurl = "/rest/sys"
        if self.debug & 0x02 : print("xurl = " + xurl)
	resp = self._getXMLetree(xurl)
	self._printXML(resp)
	return et2d(resp)

    def time(self) :
	"""  system time of ISY

	    args: none

	calls : /rest/time
	"""
	xurl = "/rest/time"
	resp = self._getXMLetree(xurl)
	self._printXML(resp)
	return et2d(resp)

    def batch( self, on=-1) :
	""" Batch mode 

	    args values:
		1 = Turn Batch mode on
		0 = Turn Batch mode off
		-1 or None = Return Batch mode status

	calls /rest/batteryPoweredWrites/
	"""
	xurl = "/rest/batteryPoweredWrites/"

	if on == 0 :
	    xurl += "/off"
	elif on == 1 :
	    xurl += "/on"

        if self.debug & 0x02 : print("xurl = " + xurl)
	resp = self._getXMLetree(xurl)
	if resp == None :
	    print 'The server couldn\'t fulfill the request.'
	    raise IsyResponseError("Batch")
	else :
	    self._printXML(resp)
	    return resp

    #/rest/batterypoweredwrites
    def batterypoweredwrites(self, on=-1) :
	""" Battery Powered Writes

	    args values:
		1 = Turn Batch mode on
		0 = Turn Batch mode off
		-1 or None = Return Batch mode status

	returns status of Battery Powered device operations
	calls /rest/batteryPoweredWrites/
	"""
	xurl = "rest/batteryPoweredWrites/"

	if on == 0 :
	    xurl += "/off"
	elif on == 1 :
	    xurl += "/on"

        if self.debug & 0x02 : print("xurl = " + xurl)
	resp = self._getXMLetree(xurl)
	if resp != None :
	    self._printXML(resp)
	    return et2d(resp)

    def electricity(self):
	""" 
	electricity status

	    args: none

	Returns electricity module info, "Energy Monitor",
	"Open ADR" and "Flex Your Power" status

	Only applicable to 994 Z Series.

	calls: /rest/electricity
	"""

	xurl = "/rest/electricity"
        if self.debug & 0x02 :
            print("xurl = " + xurl)
	resp = self._getXMLetree(xurl)
	if resp != None :
	    self._printXML(resp)
	    return et2d(resp)

    ##
    ## Callback functions
    ##
    def callback_set(self, nid, func, *args):
	"""set a callback function for a Node

	    args:
		node id
		referance to a function
		* arg list

	Sets up a callback function that will be called whenever there
	is a change event for the specified node

	Only one callback per node is supported, If a callback funtion is already
	registared for node_id it will be replaced

	requires IsyClass option "eventupdates" to to set
	"""

	if not isinstance(func, collections.Callable) :
	    raise IsyValueError("callback_set : Invalid Arg, function not callable")
	    # func.__repr__()

	nodeid = self._node_get_id(nid)
	if nodeid == None :
	    raise LookupError("no such Node : " + str(nodeid) )

	self.callbacks[nodeid] = (func, args)

    def callback_get(self, nid):
	"""get a callback funtion for a Nodes

	    args:
		node id

	returns referance to registared callback function for a node
	no none exist then value "None" is returned
	"""

	nodeid = self._node_get_id(nid)

	if nodeid != None and nodeid in self.callbacks :
	    return self.callbacks[nodeid]
	
	return None

    def callback_del(self, nid):
	"""delete a callback funtion

	    args:
		node id


	    delete a callback funtion for a Node, if exists.

	    no error is raised if callback does not exist
	"""
	nodeid = self._node_get_id(nid)
	if nodeid != None and nodeid in self.callbacks :
	    del self.callbacks[nodeid]

    ##
    ## support functions
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
    # __get/setitem__  returns a node obj ?
    def __getitem__(self, nodeaddr):
        """ access node obj line a dictionary entery """
        if nodeaddr in self.nodeCdict :
            return self.nodeCdict[str(nodeaddr)]
        else :
            return self.get_node(nodeaddr)

    def __setitem__(self, nodeaddr, val):
        """ This allows you to set the status of a Node by
	addressing it as dictionary entery """
	val = int(val)
	if val > 0  :
	    self.node_comm(nodeaddr, "DON", val)
	else :
	    self.node_comm(nodeaddr, "DOF")

    def __delitem__(self, nodeaddr):
        raise IsyPropertyError("__delitem__ : can't delete nodes :  " + str(nodeaddr) )

    def __iter__(self):
        """ iterate though Node Obj (see: node_iter() ) """
        return self.node_iter()

    def __del__(self):

	if self.debug & 0x80 :
	    print "__del__ ", self.__repr__()

        #if isinstance(self._isy_event, ISYEvent) :
	#    #ISYEvent._stop_event_loop()
	if hasattr(self._isy_event, "_shut_down") :
	    self._isy_event._shut_down = 1

	self.nodeCdict.clear()
	self.varCdict.clear()
	self.progCdict.clear()
	self.folderCdict.clear()

	# the reasion for his is that 
	#for k in self.nodeCdict.keys() :
	#    del self.nodeCdict[k]
	#for k in self.varCdict.keys() :
	#    del self.varCdict[k]
	#for k in self.progCdict.keys() :
	#    del self.progCdict[k]
	#for k in self.folderCdict.keys() :
	#    del self.folderCdict[k]


    def __repr__(self):
        return "<Isy %s at 0x%x>" % (self.addr, id(self))

#    def debugerror(self) :
#       print("debugerror")
#        raise IsyPropertyError("debugerror : test IsyPropertyError  ")

    def _printdict(self, dic):
        """ Pretty Print dictionary """
        print("===START===")
        pprint.pprint(dic)
        print("===END===")

    def _writedict(self, d, filen):
        """ Pretty Print dict to file  """
	with open(filen, 'w') as fi:
	    pprint.pprint(d, fi)



def IsyGetArg(lineargs) :
    """
	takes argv and extracts name/pass/ipaddr options
    """
    # print "IsyGetArg ", lineargs
    addr=""
    upass=""
    uname=""

    i = 0
    while i < len(lineargs) :

	#print "len = ", len(lineargs)
	#print "lineargs =", lineargs
	#print "check :", i, ":", lineargs[i], 

	if lineargs[i] in [ '--address', '-address', '-a' ] :
	    lineargs.pop(i)
	    addr = lineargs.pop(i)
	    continue

	elif lineargs[i] in [ '--pass', '-pass', '-p' ] :
	    lineargs.pop(i)
	    upass = lineargs.pop(i)
	    continue

	elif lineargs[i] in [ '--user', '-user', '-u' ] :
	    lineargs.pop(i)
	    uname = lineargs.pop(i)
	    continue

	i += 1

    return(addr, uname, upass)
 

def log_time_offset() :
    """  calculates  time format offset used in ISY event logs to localtime format """
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
