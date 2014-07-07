"""Simple Python lib for the ISY home automation netapp

 This is a Python interface to the ISY rest interface
 providomg simple commands to query and control registared Nodes and Scenes
 and well as a method of setting or querying vars
 
"""
__author__ = 'Peter Shipley <peter.shipley@gmail.com>'
__copyright__ = "Copyright (C) 2013 Peter Shipley"
__license__ = "BSD"
__version__ = "0.1.20140313"


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

import json


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
from ISY.IsyDebug import *

# import netrc

# Debug Flags:
# 0x0001 = report loads
# 0x0002 = report urls call
# 0x0004 = report func call
# 0x0008 = Dump loaded data
#
# 0x0010 = report changes to nodes
# 0x0020 = report soap web
# 0x0040 = report events
# 0x0080 = print __del__()
#
# 0x0100 =
# 0x0200 = report responce data
# 0x0400 =
# 0x0800 =
#
# 0x1000 =
# 0x2000 =
# 0x4000 =
# 0x8000 =
#
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
            addr :      IP address of ISY
            userl/userp : User Login / Password

            debug :     Debug flags (default 0)
            cachetime : cache experation time [NOT USED] (default 0)
            faststart : ( ignored if eventupdate is used )
                    0=preload cache as startup
                    1=load cache on demand
            eventupdates: run a sub-thread and stream  events updates from ISY
                        same effect as calling  Isy().start_event_thread()



    """

    # import functions
    from ISY._isyclimate import load_clim, clim_get_val, clim_query, clim_iter
    from ISY._isyvar  import load_vars, \
                var_get_value, var_set_value, _var_set_value, \
		var_addrs, var_ids, get_var, _var_get_id, \
                var_get_type, var_iter, var_add, \
		var_delete,  _var_delete, \
                var_rename, _var_rename, \
		var_refresh_value

    from ISY._isyprog import load_prog, get_prog, _prog_get_id, \
                prog_iter, prog_get_src, prog_addrs, \
                prog_comm, _prog_comm, \
                prog_get_path, _prog_get_path, \
                prog_rename, _prog_rename

    from ISY._isynode import load_nodes, _gen_member_list, _gen_folder_list, \
                _gen_nodegroups, _gen_nodedict, node_names, scene_names, \
                node_addrs, scene_addrs, get_node, _node_get_id, node_get_prop, \
                node_set_prop, _node_send, node_comm, _updatenode, \
                load_node_types, node_get_type, node_iter, _updatenode, \
                node_get_path, _node_get_path, _node_get_name, \
		node_set_powerinfo, node_enable, \
		node_del, _node_remove, \
		node_restore, node_restore_all
		# node_rename, \


    from ISY._isynet_resources import _load_networking, load_net_resource, \
                _net_resource_get_id, net_resource_run, \
                net_resource_names, net_resource_iter, \
                load_net_wol, net_wol, _net_wol_get_id, net_wol_names, net_wol_iter, \
                net_wol_ids, net_resource_ids
#    from ISY._isyzb import load_zb, zb_scannetwork, zb_ntable, zb_ping_node, \
#               zbnode_addrs, zbnode_names, zbnode_iter



##    set_var_value, _set_var_value, var_names


    if sys.hexversion < 0x3000000 :
        _password_mgr = URL.HTTPPasswordMgrWithDefaultRealm()
        _handler = URL.HTTPBasicAuthHandler(_password_mgr)
        _opener = URL.build_opener(_handler)
        #_opener = URL.build_opener(_handler, URL.HTTPHandler(debuglevel=1)) 

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

        # (self.userl, self.userp, self.addr) = authtuple

        # print "AUTH: ", self.addr, self.userl, self.userp

        self.debug = kwargs.get("debug", 0)

        if "ISY_DEBUG" in os.environ :
            self.debug = self.debug & int(os.environ["ISY_DEBUG"])


        # self.cachetime = kwargs.get("cachetime", 0)
        self.faststart = kwargs.get("faststart", 1)
        self.eventupdates = kwargs.get("eventupdates", 0)

        # and experiment alt to IsyGetArg
        self.parsearg = kwargs.get("parsearg", False)
        if self.parsearg :
            self.parse_args()

        self._isy_event = None
        self.event_heartbeat = 0;
        self.error_str = ""
        self.callbacks = None
        self._is_pro = True


        # data dictionaries for ISY state
        self._name2id = dict()
        self.controls = None
        self.name2control = None
        self._nodefolder = None
        self._folder2addr = None
        self._progdict = None      
        self._nodedict = None
        self._nodegroups = None
        self._groups2addr = None
        self._node2addr = None
        self._nodeCategory = None
        self._vardict = None        
        self._wolinfo = None
        self._net_resource = None
        self.climateinfo  = None
        
        self.isy_status = dict()
        self.zigbee = dict()

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

#       print "\n\taddr", "=>", self.addr, "\n\n"


#       if ( not self.userl or not self.userp ) :
#           netrc_info = netrc.netrc()
#           login, account, password = netrc_info.authenticators(self.addr)
#           print "login", "=>", repr(login)
#           print "account", "=>", repr(account)
#           print "password", "=>", repr(password)
#           self.userl = "admin"
#           self.userp = "admin"

        if self.debug & _debug_loads_ :
            print("class Isy __init__")
            print("debug ", self.debug)
            # print("cachetime ", self.cachetime)
            print("faststart ", self.faststart)
            print("address ", self.addr)

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
            if not self._progdict :
                self.load_prog()
            if  not self._nodedict :
                self.load_nodes()
            self.start_event_thread()

    # and experimental alternitive to IsyGetArg
    def parse_args(self) :
        """
            Use argparse to extract common options

            unused options placed in self.unknown_args

            this is a alternitive to IsyGetArg
        """
        import argparse

        parser = argparse.ArgumentParser(add_help=False)

        parser.add_argument("-d", "--debug", dest="debug",
                default=self.debug,
                type=int,
                # action="count",
                nargs='?',
                help="debug options")

        parser.add_argument("-a", "--address", dest="addr",
                default=os.getenv('ISY_ADDR', None),
                help="hostname or IP device")

        parser.add_argument("-u", "--user", dest="user",
                default=os.getenv('ISY_USER', None),
                help="Admin Username")

        parser.add_argument("-p", "--pass", dest="passw",
                default=os.getenv('ISY_PASS', None),
                help="Admin Password")

        args, self.unknown_args = parser.parse_known_args()

        if args.addr :
            self.addr = args.addr

        if args.user :
            self.userl = args.user

        if args.passw :
            self.userp = args.passw

        if args.debug :
            self.debug = args.debug

        self.parser = parser

    #
    # Event Subscription Code
    # Allows for treaded realtime node status updating
    #
    def start_event_thread(self, mask=0):
        """  starts event stream update thread

        mask will eventually be used to "masking" events


        """
        from threading import Thread

        if ( self.debug & 0x40 ) :
            print "start_event_thread"

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
        self._isy_event.subscribe(addr=self.addr, userp=self.userp, userl=self.userl)
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
        skip_default = [
#               "_0", "_2", "_4", "_5", "_6", "_7", "_8",
#               "_9", "_10", "_11", "_12", "_13", "_14",
#               "_15", "_16", "_17", "_18", "_19", "_20",
                "DON", "DOF",
                ]

        skip = skip_default

        assert isinstance(evnt_dat, dict), "_read_event Arg must me dict"

        # event_targ holds the node address or var id
        # for the current event ( if applicable )
        event_targ = None

        #if evnt_dat["control"] in skip :
        #    return

        # print "evnt_dat ", evnt_dat

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
                        IsyRuntimeWarning)

        elif evnt_dat["control"] == "_0" : # HeartBeat
            #self.event_heartbeat = time.gmtime()
            pass

        #
        # handle VAR value change
        #
        elif evnt_dat["control"] == "_1" : # Trigger Events

            #
            # action = "0" -> Event Status   
            # action = "1" -> Client Should Get Status
            # action = "2" -> Key Changed   
            # action = "3" -> Info String    
            # action = "4" -> IR Learn Mode   
            # action = "5" -> Schedule (schedule status changed)    
            # action = "6" -> Variable Status (status of variable changed)    
            # action = "7" -> Variable Initialized (initial value of a variable    )
            # 
            if evnt_dat["action"] == "0" and 'nr' in evnt_dat['eventInfo'] :
                prog_id = '{0:0>4}'.format(evnt_dat['eventInfo']['id'])
                event_targ = prog_id

                if self._progdict and prog_id in self._progdict :
                    prog_dict = self._progdict[prog_id]
                    if 'on' in evnt_dat['eventInfo'] :
                        prog_dict['enabled'] = 'true'
                    else :
                        prog_dict['enabled'] = 'false'
                    if 'rr' in evnt_dat['eventInfo'] :
                        prog_dict['runAtStartup'] = 'true'
                    else :
                        prog_dict['runAtStartup'] = 'false'
                    prog_dict['lastRunTime'] = evnt_dat['eventInfo']['r']
                    prog_dict['lastFinishTime'] = evnt_dat['eventInfo']['f']

                    ev_status = int(evnt_dat['eventInfo']['s'])
                    if ev_status & 0x01 :
                        prog_dict['running'] = 'idle'
                    elif ev_status & 0x02 :
                        prog_dict['running'] = 'then'
                    elif ev_status & 0x03 :
                        prog_dict['running'] = 'else'

                    if ev_status & 0x10 :
                        prog_dict['status'] = 'unknown'
                    elif ev_status & 0x20 :
                        prog_dict['status'] = 'true'
                    elif ev_status & 0x30 :
                        prog_dict['status'] = 'false'
                    elif ev_status & 0xF0 :
                        prog_dict['status'] = 'not_loaded'
                else :
                    self.load_prog(prog_id)


#   '0002': {  'enabled': 'true',
#              'folder': 'false',
#              'id': '0002',
#              'lastFinishTime': '2013/03/30 15:11:25',
#              'lastRunTime': '2013/03/30 15:11:25',
#              'name': 'QueryAll',
#              'nextScheduledRunTime': '2013/03/31 03:00:00',
#              'parentId': '0001',
#              'runAtStartup': 'false',
#              'running': 'idle',
#              'status': 'false'},


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
                    warn("Event for Unknown Var : {0}".format(vid), IsyRuntimeWarning)

        elif evnt_dat["control"] == "_2" : # Driver Specific Events
            pass

        elif evnt_dat["control"] == "_3" : # Node Change/Updated Event
            if ( self.debug & 0x40 ) :
                print("Node Change/Updated Event :  {0}".format(evnt_dat["node"]))
                print("evnt_dat : ", evnt_dat)
            #
            # action = "NN" -> Node Renamed   
            # action = "NR" -> Node Removed    
            # action = "ND" -> Node Added    
            # action = "NR" -> Node Revised   
            # action = "MV" -> Node Moved (into a scene)   
            # action = "CL" -> Link Changed (in a scene)   
            # action = "RG" -> Removed From Group (scene)   
            # action = "EN" -> Enabled   
            # action = "PC" -> Parent Changed    
            # action = "PI" -> Power Info Changed   
            # action = "DI" -> Device ID Changed   
            # action = "DP" -> Device Property Changed   
            # action = "GN" -> Group Renamed    
            # action = "GR" -> Group Removed    
            # action = "GD" -> Group Added    
            # action = "FN" -> Folder Renamed   
            # action = "FR" -> Folder Removed    
            # action = "FD" -> Folder Added    
            # action = "NE" -> Node Error (Comm. Errors)    
            # action = "CE" -> Clear Node Error (Comm. Errors Cleared)    
            # action = "SN" -> Discovering Nodes (Linking)    
            # action = "SC" -> Node Discovery Complete     
            # action = "WR" -> Network Renamed    
            # action = "WH" -> Pending Device Operation         
            # action = "WD" -> Programming Device     
            # action = "RV" -> Node Revised (UPB)  

            if evnt_dat['action'] == 'EN' : # Enable
                if  evnt_dat['node'] in self._nodedict :
                    self._nodedict[ evnt_dat['node'] ]['enabled'] =  evnt_dat['eventInfo']['enabled']

            elif evnt_dat['action'] == 'GN' : # Group Renamed    
                if  evnt_dat['node'] in self._nodegroups :
                    oldname = self._nodegroups[ evnt_dat['node'] ]['name']
                    self._nodegroups[ evnt_dat['node'] ]['name'] = evnt_dat['eventInfo']['newName']
                    self._groups2addr[ evnt_dat['eventInfo']['newName'] ] = evnt_dat['node']
                    del self._groups2addr[ oldname ]
                    
                    if evnt_dat['eventInfo']['newName'] in self._name2id :
                        # warn Dup ID
                        if self._name2id[ evnt_dat['eventInfo']['newName'] ][0] == "group" :
                            self._name2id[ evnt_dat['eventInfo']['newName'] ] = ("group", evnt_dat['node'] )
                    else :
                        self._name2id[ evnt_dat['eventInfo']['newName'] ] = ("group", evnt_dat['node'] )
                    # Delete old entery if it is 'ours'
                    if oldname in self._name2id and self._name2id[ oldname ][0] == "group" :
                        del self._name2id[ oldname ]

            elif evnt_dat['action'] == 'GR' : # Group Removed/Deleted    
                    if ( self.debug & 0x40 ) :
                        print("evnt_dat :", evnt_dat)
                    pass
            elif evnt_dat['action'] == 'GD' : # New Group Added    
                    if ( self.debug & 0x40 ) :
                        print("evnt_dat :", evnt_dat)
                    pass
            

            elif evnt_dat['action'] == 'ND' :
		node_id = evnt_dat["node"]
		node_dat = evnt_dat['eventInfo']['node']
		if node_id in self.nodedict :
		    self.nodedict[node_id].update(node_dat)
		else :
		    self.nodedict[node_id] = node_dat


	    #
	    # At this time results are undefined for
	    # Node class objects that represent a deleted node 
	    #
            elif evnt_dat['action'] == 'NR' :
		node_id = evnt_dat["node"]
		if node_id in self.nodedict :
		    node_name = self.nodedict[node_id]["name"]
		    if "property" in self.nodedict[node_id] :
			self.nodedict[node_id]["property"].clear()
			del self.nodedict[node_id]["property"]
		    if self._node2addr and node_name in self._node2addr :
			self._node2addr[ node_name ]
		    if self._name2id and node_name in self._name2id :
			self._name2id[ node_name ]

		if node_id in self.nodeCdict :
		    self.nodeCdict[ node_id ]



            elif evnt_dat['action'] == 'FD' :
                if 'folder' in evnt_dat['eventInfo'] and isinstance(evnt_dat['eventInfo']['folder'], dict) :
                    self._nodefolder[ evnt_dat['node'] ] = evnt_dat['eventInfo']['folder']
                    self._folder2addr[ evnt_dat['eventInfo']['folder']['name'] ] = evnt_dat['node']
            elif evnt_dat['action'] == 'FR' :
                if  evnt_dat['node'] in self._nodefolder :
                    if evnt_dat['node'] in self.nodeCdict :
                        # this is tricky if the user has a IsyNodeFolder obj
                        # more has to be done to tell the Obj it's dead
                        del self.nodeCdict[ evnt_dat['node'] ]
                    del self._nodefolder[ evnt_dat['node'] ]
            elif evnt_dat['action'] == 'FN' :
                if  evnt_dat['node'] in self._nodefolder :
                    oldname = self._nodefolder[ evnt_dat['node'] ]['name']
                    self._nodefolder[ evnt_dat['node'] ]['name'] = evnt_dat['eventInfo']['newName']
                    self._folder2addr[ evnt_dat['eventInfo']['newName'] ] = evnt_dat['node']
                    del self._folder2addr[ oldname ]

        elif evnt_dat["control"] == "_4" : # System Configuration Updated
            pass
            #
            # action = "0" -> Time Changed
            # action = "1" -> Time Configuration Changed
            # action = "2" -> NTP Settings Updated
            # action = "3" -> Notifications Settings Updated
            # action = "4" -> NTP Communications Error
            # action = "5" -> Batch Mode Updated
            #    node = null
            #    <eventInfo>
            #        <status>"1"|"0"</status>
            #    </eventInfo>
            # action = "6"  Battery Mode Programming Updated
            #    node = null
            #    <eventInfo>
            #        <status>"1"|"0"</status>
            #    </eventInfo>
            if evnt_dat['action'] == '5' :
                if 'status' in evnt_dat['eventInfo'] :
                    if evnt_dat['eventInfo']['status'] == "1" :
                        self.isy_status['batchmode'] = True
                    else :
                        self.isy_status['batchmode'] = False
                    # self.isy_status['batchmode'] = (evnt_dat['eventInfo']['status'] == "1")
            elif evnt_dat['action'] == '6' :
                if 'status' in evnt_dat['eventInfo'] :
                    if evnt_dat['eventInfo']['status'] == "1" :
                        self.isy_status['battery_mode_prog_update'] = True
                    else :
                        self.isy_status['battery_mode_prog_update'] = False
                    #self.isy_status['battery_mode_prog_update'] = (evnt_dat['eventInfo']['status'] == "1")

                # status_battery_mode_prog_update

        elif evnt_dat["control"] == "_5" : # System Status Updated
            pass
            # 
            # node = null
            # action = "0" -> Not Busy
            # action = "1" -> Busy
            # action = "2" -> Idle
            # action = "3" -> Safe Mode
            # 

        elif evnt_dat["control"] == "_6" : # Internet Access Status
            pass
            #
            # action = "0" -> Disabled
            # action = "1" -> Enabled
            #     node = null
            #     <eventInfo>external URL</eventInfo>
            # action = "2" -> Failed
            #

        elif evnt_dat["control"] == "_7" : # Progress Report
            pass

        elif evnt_dat["control"] == "_8" : # Security System Event
            pass

        elif evnt_dat["control"] == "_9" : # System Alert Event
            pass

        elif evnt_dat["control"] == "_10" : # OpenADR and Flex Your Power Events
            pass

        elif evnt_dat["control"] == "_11" : # Climate Events
            pass

        elif evnt_dat["control"] == "_12" : # AMI/SEP Events
            pass
#           if evnt_dat['action'] == '1' :
#               if 'ZBNetwork' in evnt_dat['eventInfo'] :
#                   self.zigbee['network'] = evnt_dat['eventInfo']['ZBNetwork']
#           elif evnt_dat['action'] == '10' :
#               if 'MeterFormat' in evnt_dat['eventInfo'] :
#                   self.zigbee['MeterFormat'] = evnt_dat['eventInfo']['MeterFormat']
#

        elif evnt_dat["control"] == "_13" : # External Energy Monitoring Events
            pass

        elif evnt_dat["control"] == "_14" : # UPB Linker Events
            pass

        elif evnt_dat["control"] == "_15" : # UPB Device Adder State
            pass

        elif evnt_dat["control"] == "_16" : # UPB Device Status Events
            pass

        elif evnt_dat["control"] == "_17" : # Gas Meter Events
            pass

        elif evnt_dat["control"] == "_18" : # Zigbee Events
            pass

        elif evnt_dat["control"] == "_19" : # Elk Events
            pass
#           if evnt_dat["action"] == "6" :
#               if 'se" in evnt_dat['eventInfo'] :
#                   if evnt_dat['eventInfo']['se']['se-type'] == '156' :
#                       print "Elk Connection State : ", evnt_dat['eventInfo']['se']['se-val']
#                   elif evnt_dat['eventInfo']['se']['se-type'] == '157' :
#                       print "Elk Enable State : ", evnt_dat['eventInfo']['se']['se-val']



        elif evnt_dat["control"] == "_20" : # Device Linker Events
            pass


        else:
            if ( self.debug & 0x40 ) :
                print("evnt_dat :", evnt_dat)
                print("Event fall though : '{0}'".format(evnt_dat["node"]))


        if self.callbacks != None :
            call_targ = None
            if event_targ in self.callbacks :
                call_targ = event_targ
            elif evnt_dat["control"] in self.callbacks :
                call_targ = evnt_dat["control"] 

            if call_targ != None :
                cb = self.callbacks[call_targ]
                if isinstance(cb[0], collections.Callable) :
                    try :
                        cb[0](evnt_dat, *cb[1])
                    except Exception as e:
                        print "e=",e
                        print "sys.exc_info()=",sys.exc_info()
                        print("Callback Error:", sys.exc_info()[0])

                else :
                    warn("callback for {!s} not callable, deleting callback".format(call_targ),
                            IsyRuntimeWarning)
                    del self.callbacks[call_targ]

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



    def addnode(self, id=None, nname=None, ntype=None, flag="0") :
        """
            Adds a predefined node for a device with a given address

            args:
                id
                nname
                ntype
                flag

        """
        if nname is None :
            nname = id
        if id is None :
            raise IsyValueError("invalid node id : " + type)
        if type is None :
            raise IsyValueError("invalid node type : " + type)

        return  self.soapcomm("AddNode", id=id, name=nname, type=ntype, flag=flag)


    def getsystemdatetime(self) :
        """
            timestamp of when ISY was last started
        """
        r = self.soapcomm("GetSystemDateTime")
        return (r)

    def startuptime(self) :
        """
            timestamp of when ISY was last started
        """
        r = self.soapcomm("GetStartupTime")
        return (r)

    def webcam_get(self) :
        """
            get webcam list avalible in ISY's ajax web UI

            returns dict
        """
        #campath="/WEB/CONF/cams.jsn"
        r = self.soapcomm("GetSysConf", name="/WEB/CONF/cams.jsn")
        return json.loads(r)



    def webcam_add(self, brand=None, num=None, ip=None, model='1', name=None, passwd='', port='80', user='') :
        """
            Add webcam to UI

                args :
                    brand               brand of cam (one of : Foscam Smarthome Axis Panasonic MJPGstreamer)
                    ip                  IP of cam
                    port                TCP port for cam (default = 80)
                    model
                    name
                    user
                    passwd              

        """
        if not ( brand is None) and  (brand.lower() not in ["foscam", "smarthome", "axis", "panasonic", "mjpgstreamer"]) :
            raise IsyValueError("webcam_add : invalid value for arg 'brand' ")
        else :
            brand = brand.lower()

        if ip is None :
            raise IsyValueError("webcam_add : invalid ip")

        if name is None :
            name = brand

        camlist = self.webcam_get()

        if 'lastId' in camlist :
            maxid = int( camlist['lastId'] ) + 2
        else :
            maxid = camlist.__len__() + 2

        if num is None :
            for i in range(1, maxid) : 
                if str(i) not in camlist :
                    num = str(i)
                    break
            else :
                raise RuntimeError( "webcam_add : failed cam index")
        elif isinstance(num, int) :
            num = str(num)

        if self.debug & 0x100 :
            print "using num : ", num

        newcam = {'brand': brand, 'ip': ip, 'model': model, 'name': name, 'pass': passwd, 'port': port, 'user': user}

        camlist[num] = newcam

        if self.debug & 0x100 :
            print "webcam_add : ",
            pprint.pprint(camlist)

        if num > camlist['lastId'] :
            if self.debug & 0x100 :
                print "new lastId = ", num, ":", camlist['lastId'] 
            camlist['lastId'] = num

        return self._webcam_set(camlist)

    def webcam_del(self, camid=None) :
        """
            delete an entery from UI's webcam list

            arg:
                camid           index for camera in camlist
        """
        if camid is None :
            raise IsyValueError("webcam_del : arg camid is None")

        camlist = self.webcam_get()

        if self.debug & 0x100 :
            pprint.pprint(camlist)

        if isinstance(camid, int) :
            camid = str(camid)

        if camid not in camlist :
            raise IsyValueError("webcam_del : invalid camid")

        del camlist[camid]

        if 'lastId' in camlist :
            maxid = int( camlist['lastId'] ) + 2
        else :
            maxid = camlist.__len__() + 2

        lastid = -1
        for i in range(1, maxid) : 
            if str(i) in camlist and lastid < i :
                    lastid = i

        camlist['lastId'] = str(lastid)

        return self._webcam_set(camlist)



    def _webcam_set(self, camdict=None) :
        if camdict is None :
            raise IsyValueError("_webcam_set : arg camdict invalid")

        camjson =  json.dumps(camdict, sort_keys=True)
        r = self._sendfile(data=camjson, filename="/WEB/CONF/cams.jsn", load="n")
        return r

    def set_debug_level(self, level=1) :
        """
            Sets the debug options and current level

            args :
                option    value 0 -> 3
        """
        ret =  self.soapcomm("SetDebugLevel", option=level )
        return ret

    def get_debug_level(self, level=1) :
        """
            Gets the debug options and current level
        """
        ret =  self.soapcomm("GetDebugLevel",  )
        return ret

    def node_discover_cancel(self, flag="1") :
        """
            Puts ISY out of discovery (linking) mode

            The flag decides the operations (reset, crawl, spider) 
            to be performed after device(s) are discovered

            args :
                NodeOperationsFlag      enum value '1', '2', '3' or '4' 

            Valid values
                1 = add the node and reset all previous setting if any
                2 = unused 
                3 = add the node, find all the associated nodes, and create all the linkages thereto 
                4 = add the node, find all the associated nodes, but do not create any linkages 

        """
        flag = str(flag)
        if flag not in ['1', '2', '3', '4'] :
            raise IsyValueError("invalid flag value : " + flag)


        # if code == 501 then device was alread not in link/Discovery mode
        ret =  self.soapcomm("CancelNodesDiscovery", flag=flag)

        return ret



    #
    # need to add code to update name2id and *2addr lookup arrays
    #
    def rename(self, objid, nname) :
        """ rename 

                args: 
                    id = Node/Scene/Folder name or ID
                    name = new name

            calls SOAP RenameNode() / RenameGroup() / RenameFolder()
        """
        (idtype, nid) = self.getid(objid)
        if nid == None :
            raise IsyValueError("unknown node/obj : " + objid)
        if idtype == "node" :
            return self.soapcomm("RenameNode", id=nid, name=nname)
        elif idtype == "group" :
            return self.soapcomm("RenameGroup", id=fid, name=nname)
        elif idtype == "folder" :
            return self.soapcomm("RenameFolder", id=fid, name=nname)
        elif idtype == "var" :
            # return self.var_rename(var=nid, name=nname)
            raise IsyValueError("can not rename var, use var_rename() ")
        elif idtype == "prog" :
            raise IsyValueError("can not rename prog use prog_rename() ")
        else : 
            raise IsyValueError("node/obj " + objid + " not node (" + idtype + ")" )

    #
    # need to add code to update name2id and *2addr lookup arrays
    #
    def node_rename(self, nodeid, nname) :
        """ rename Node

                args: 
                    id = Node ID
                    name = new Node name

            calls SOAP RenameNode()
        """
        (idtype, nid) = self._node_get_id(nodeid)
        if nid == None :
            raise IsyValueError("unknown node/obj : " + nodeid)
	print "nodeid ", nodeid
	print "nid ", nid
        return self.soapcomm("RenameNode", id=nid, name=nname)

#    def node_new(self, sid, nname) :
#       """ create new Folder """
#       return  self.soapcomm("AddNode", id=1234, name=nname, type="T", flag="Y")

    ## scene

    #
    # need to add code to update name2id and *2addr lookup arrays
    #
    def scene_rename(self, sid, fname) :
        """ rename Scene/Group

                args: 
                    sid = a Scene/Group id
                    name = new name 


            calls SOAP RenameGroup()
        """
        (idtype, grid) = self._node_get_id(sid)
        return self.soapcomm("RenameGroup", id=grid, name=fname)

    #
    # need to add code to update name2id and *2addr lookup arrays
    #
    def scene_del(self, sid=None ) :
        """ delete Scene/Group 

                args: 
                    id : Scene address, name or Folder Obj

            calls SOAP RemoveGroup()
        """
        (idtype, sceneid) = self._node_get_id(sid)
        if sceneid == None :
            raise IsyValueError("no such Scene : " + str(sid) )
        #
        # add code to update self._nodegroups
        #
        return  self.soapcomm("RemoveGroup", id=sceneid)

    #
    # need to add code to update name2id and *2addr lookup arrays
    #
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
            while nid in self._nodefolder or nid in self._nodegroups :
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
        (idtype, nodeid) = self._node_get_id(nid)
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
        (idtype, nodeid) = self._node_get_id(nid)
        if nodeid == None :
            raise IsyValueError("no such Node : " + str(nid) )
        r = self.soapcomm("RemoveFromGroup", group=groupid, id=nodeid)
        return r

    ## folder

    #
    # need to add code to update name2id and *2addr lookup arrays
    #
    def folder_rename(self, fid, fname) :
        """ rename Folder

                args: 
                    id = folder ID
                    name = new folder name

            calls SOAP RenameFolder()
        """
        (idtype, fid) = self._node_get_id(fid)
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
            while fid in self._nodefolder or fid in self._nodegroups :
                iid += 1
                fid = str(iid)
        r = self.soapcomm("AddFolder", fid=1234, name=fname)
        if  isinstance(r, tuple) and r[0] == '200' :
            self._nodefolder[fid] = dict()
            self._nodefolder[fid]['address'] = fid
            self._nodefolder[fid]['folder-flag'] = '0'
            self._nodefolder[fid]['name'] = 'fname'

        return r

    def folder_del(self,fid) :
        """ delete folder
                args: 
                    fid : folder address, name or Folder Obj

            calls SOAP RemoveFolder()
        """
        (idtype, fid) = self._node_get_id(fid)
        if fid == None :
            raise IsyValueError("Unknown Folder : " + str(fid) )
        r = self.soapcomm("RemoveFolder", id=fid)
        if  isinstance(r, tuple) and r[0] == '200' :
            self._nodefolder[fid] = dict()

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
        (idtype, nodeid) = self._node_get_id(nid)
        if nodeid == None :
            raise IsyValueError("no such Node/Scene : " + str(nid) )

        if parent != "" :
            (idtype, fldid) = self._node_get_id(parent)
            if fldid == None :
                raise IsyValueError("no such Folder : " + str(parent) )
            parentid = fldid
        else :
            parentid = parent

        r = self.soapcomm("SetParent", node=nodeid, nodeType=nodeType, parent=parentid, parentType=parentType)
        return r

    def folder_del_node(self, nid, nodeType=1) :
        """ remove node from folder

            args:
                node
                nodeType

            remove node/scene from folder ( moves to default/main folder )

            calls SOAP SetParent()
        """
        return self.folder_add_node(nid, nodeType=nodeType, \
                parent="", parentType=3)


    def set_user_credentials(self, name=None, password=None) :
	"""
	    Changes the userid and password for a user ( admin )

	    args: 
		name         user name
		password     user password 
	"""
	if name is None :
            raise IsyValueError("set_user_credentials : name argument required ")
	if password is None :
            raise IsyValueError("set_user_credentials : pass argument required ")
        return self.soapcomm("SetUserCredentials", name=name, password=password)

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

    def queryall(self, node=None, flag=None) :
        """
            Queries a node, a scene, or even the whole network

            Named args:
                node : name of node or scene to query (optional)
                flag : enum { '1', '4', '8' }
        """
        soapargs = dict()
        if node is not None :
            soapargs['node'] = ntype
        if flag is not None :
            soapargs['flag'] = flag
        r = self.soapcomm("QueryAll", **soapargs)


    #
    #  Util Funtions
    #
    def _preload(self, rload=0):
        """ Internal function

            preload all data tables from ISY device into cache
            normally this is done "on demand" as needed
        """
        if rload or  not self.controls :
            self.load_conf()

        if rload or not self._nodedict :
            self.load_nodes()

        # self._gen_member_list()
        # if rload or not self.climateinfo :
            # self.load_clim()

        if rload or not self._vardict :
            self.load_vars()

        if rload or not self._progdict :
            self.load_prog()

        # if rload or not self._wolinfo :
            #self.load_wol()

        if rload or not self._nodeCategory :
            self.load_node_types()

    def _savedict(self) :
        """ internal debug command """

        self._preload()

        # self._writedict(self._wolinfo, "wolinfo.txt")

        self._writedict(self._nodedict, "nodedict.txt")

        self._writedict(self._nodegroups, "nodegroups.txt")

        self._writedict(self._nodefolder, "folderlist.txt")

        self._writedict(self._vardict, "vardict.txt")

        # self._writedict(self.climateinfo, "climateinfo.txt")

        self._writedict(self.controls, "controls.txt")

        self._writedict(self._progdict, "progdict.txt")

        self._writedict(self._nodeCategory, "nodeCategory.txt")



    ##
    ## Load System config / info and command information
    ##
    def load_conf(self) :
        """ Load configuration of the system with permissible commands 

            args : none

            internal function call

        """
        if self.debug & 0x01 :
            print("load_conf")
        configinfo = self._getXMLetree("/rest/config")
        # Isy._printXML(configinfo)
        # IsyCommunicationError

        if configinfo is None :
            raise IsyCommunicationError("Load Configuration Fail : " \
                        + self.error_str)

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

        n = configinfo.find("root/id")
        if not n is None:
            if isinstance(n.text, str):
                self.config['id'] = n.text

        xelm = configinfo.find("product/id")
        if not xelm is None:
            if hasattr(xelm, 'text') :
                self.config["product_id"] = xelm.text


        # print("self.controls : ", self.controls)
        #self._printdict(self.controls)
        #print("self.name2control : ", self.name2control)

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
    ## property
    ##
    def _get_platform(self) :
        """ name of ISY platform (readonly) """
        return self.config["platform"]
    platform = property(_get_platform)

    def _get_id(self) :
        """ id of ISY (readonly) """
        return self.config["id"]
    id = property(_get_id)

    def _get_app_version(self) :
        """ name of ISY app_version (readonly) """
        return self.config["app_version"]
    app_version = property(_get_app_version)

#    def _get_debug(self) :
#        """ debug flag for Obj """
#        return self._debug
#    def _set_debug(self, val) :
#       self._debug = val
#    debug = property(_get_debug,_set_debug)


    ##
    ## Logs
    ##
    def load_log_type(self):
        """ load log type tables

            args: None

        **not implemented **
        """
        if self.debug & 0x01 :
            print("load_log_type")
        pass

    def load_log_id(self):
        """ load log id tables

        **not implemented **
        """
        if self.debug & 0x01 :
            print("load_log_id")
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
        try:

            res = self._opener.open(req)

        except URL.URLError as e:
            # Error log can return a 404 is there are not logs ( yet )
            return [ ]

        else :
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

#        print("X10 sent : " + str(unit) + " : " + str(xcmd))
        xurl = "/rest/X10/" + str(unit) + "/" + str(xcmd)
        if self.debug & 0x02 : print("xurl = " + xurl)
        resp = self._getXMLetree(xurl)
        #self._printXML(resp)
        #self._printinfo(resp)
        if resp.attrib["succeeded"] != 'true' :
            raise IsyResponseError("X10 command error : unit=" + str(unit) + " cmd=" + str(cmd))

# /rest/time
#       Returns system time
#
#/rest/network
#    Returns network configuration
# /rest/sys
#       returns system configuration
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
        #self._printXML(resp)
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
        #self._printXML(resp)
        return et2d(resp)

    def sys(self) :
        """ system configuration

            args: none

        calls : /rest/sys
        """  
        xurl = "/rest/sys"
        if self.debug & 0x02 : print("xurl = " + xurl)
        resp = self._getXMLetree(xurl)
        #self._printXML(resp)
        return et2d(resp)

    def time(self) :
        """  system time of ISY

            args: none

        calls : /rest/time
        """
        xurl = "/rest/time"
        resp = self._getXMLetree(xurl)
        #self._printXML(resp)
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
            #self._printXML(resp)
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
            #self._printXML(resp)
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
            #self._printXML(resp)
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

        Only one callback per node is supported,
        If a callback funtion is already registared for
        node or var id it will be replaced

        requires IsyClass option "eventupdates" to to set
        """

        if not isinstance(func, collections.Callable) :
            raise IsyValueError("callback_set : Invalid Arg, function not callable")
            # func.__repr__()

        if self.callbacks == None :
            self.callbacks = dict ()

        (idtype, nodeid) = self._node_get_id(nid)
        if nodeid == None :
            # raise LookupError("no such Node : " + str(nodeid) )
            self.callbacks[nid] = (func, args)
        else :
            self.callbacks[nodeid] = (func, args)

    def callback_get(self, nid):
        """get a callback funtion for a Nodes

            args:
                node id

        returns referance to registared callback function for a node
        no none exist then value "None" is returned
        """

        if self.callbacks != None :
            (idtype, nodeid) = self._node_get_id(nid)

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
        if self.callbacks != None :
            (idtype, nodeid) = self._node_get_id(nid)
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
    ## the following are obj independent get methods
    ##

    #
    # Untested
    #
    def gettype(self, nobj) :
        if isinstance(nobj, IsySubClass) :
              return nobj.objtype()
        (idtype, nid) = self._node_get_id(nobj)
        return(idtype)

    #
    # Untested
    #
    def getid(self, objaddr):
        (idtype, nid) = self._node_get_id(objaddr)
        return(nid)

    #
    # Untested
    #
    def getobj(self, objaddr):
        """ access node obj line a dictionary entery """
        (idtype, nid) = self.getid(objid)
        if nid == None :
            raise IsyValueError("unknown node/obj : " + objid)
        if nid in self.nodeCdict :
            return self.nodeCdict[nid]

        if idtype in ['node', 'group', 'folder'] :
            return self.get_node(nid)
        elif idtype == "var" :
            return self.get_var(nid)
        elif idtype == "prog" :
            return self.get_prog(nid)
        else :
            raise IsyValueError("don't know how to get obj for type : " + idtype)

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
        if hasattr(self, "_isy_event") :
            if hasattr(self._isy_event, "_shut_down") :
                self._isy_event._shut_down = 1

        if  hasattr(self, "nodeCdict" ) :
            self.nodeCdict.clear()

        if  hasattr(self, "varCdict" ) :
            self.varCdict.clear()

        if  hasattr(self, "progCdict" ) :
            self.progCdict.clear()

        if  hasattr(self, "folderCdict" ) :
            self.folderCdict.clear()

        # the reasion for this is that 
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

        if lineargs[i] in [ '--isyaddress', '-isyaddress', '--isyaddr' '-isyaddr' ] :
            lineargs.pop(i)
            addr = lineargs.pop(i)
            continue

        elif lineargs[i] in [ '--isypass', '-isypass' ] :
            lineargs.pop(i)
            upass = lineargs.pop(i)
            continue

        elif lineargs[i] in [ '--isyuser', '-isyuser' ] :
            lineargs.pop(i)
            uname = lineargs.pop(i)
            continue

        i += 1

#    if not addr :
#        addr = os.getenv('ISY_ADDR', "isy")
#    if not uname :
#       userl = os.getenv('ISY_USER', "admin")
#    if not upass :
#       userp = os.getenv('ISY_PASS', "admin")

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
