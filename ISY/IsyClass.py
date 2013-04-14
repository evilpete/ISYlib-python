"""Simple Python lib for the ISY home automation netapp

 This is a Python interface to the ISY rest interface
 providomg simple commands to query and control registared Nodes and Scenes
 and well as a method of setting or querying vars
 
"""


#from xml.dom.minidom import parse, parseString
# from StringIO import StringIO
# import xml.etree.ElementTree as # ET
# import base64
import re
import os
from pprint import pprint
import sys
#import string
import pprint
import time
from warnings import warn






if sys.hexversion < 0x3000000 :
    import urllib2 as URL
    from urllib2 import URLError, HTTPError
    # HTTPPasswordMgrWithDefaultRealm = URL.HTTPPasswordMgrWithDefaultRealm
else :
    import urllib as URL
    from urllib.request import HTTPPasswordMgrWithDefaultRealm

from ISY.IsyUtilClass import IsyUtil, IsySubClass, et2d
# from ISY.IsyNodeClass import IsyNode, IsyScene, IsyNodeFolder, _IsyNodeBase
from ISY.IsyProgramClass import *
#from ISY.IsyVarClass import IsyVar
from ISY.IsyExceptionClass import  *
from ISY.IsyEvent import ISYEvent
from ISY.IsySoap import IsySoap

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

    from _isyclimate import load_clim, clim_get_val, clim_query, clim_iter
    from _isyvar  import load_vars, var_set_value, _var_set_value, \
		var_get_value, var_addrs, get_var, _var_get_id, \
		var_get_type, var_iter
    from _isyprog import load_prog, get_prog, _prog_get_id, \
		prog_iter, prog_comm, _prog_comm
    from _isynode import load_nodes, _gen_member_list, _gen_folder_list, \
		_gen_nodegroups, _gen_nodedict, node_names, scene_names, \
		node_addrs, scene_addrs, get_node, _node_get_id, node_get_prop, \
		node_set_prop, _node_send, node_comm, _updatenode, \
		load_node_types, node_get_type, node_iter, _updatenode
    from _isynet_resources import _load_networking, load_net_resource, \
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
	self.userl = kwargs.get("userl", "admin")
	self.userp = kwargs.get("userp", "admin")
        self.debug = kwargs.get("debug", 0)
        self.cachetime = kwargs.get("cachetime", 0)
        self.faststart = kwargs.get("faststart", 1)
        self.eventupdates = kwargs.get("eventupdates", 0)
        self.addr = kwargs.get("addr", os.getenv('ISY_ADDR', None))
	self._isy_event = None
	self.error_str = ""
	self.soap_client = None

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
        Isy._handler.add_password(None, self.addr, self.userl, self.userp)
        # self._opener = URL.build_opener(Isy._handler, URL.HTTPHandler(debuglevel=1))
        # self._opener = URL.build_opener(Isy._handler)
        if self.debug & 0x02:
            print("baseurl: " + self.baseurl + " : " + self.userl + " : " + self.userp)

	if self.faststart < 2 :
	    try:
		self.load_conf()
	    except URLError as e:
		print("Unexpected error:", sys.exc_info()[0])
		print 'Problem connecting with ISY device'
		raise IsyCommunicationError(e)


        if kwargs.get("usesoap", False) :
	    self.soap_client = IsySoap(self)

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
	# IsyCommunicationError

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

    def _get_control_id(self, comm):
        """ command name to command ID """
        try:
            self.controls
        except AttributeError:
            self.load_conf()

        c = comm.strip().upper()
        if c in self.controls :
            return c
        if c in self.name2control :
            return self.name2control[c]
        return None

    ##
    ## Soap
    ##
    def get_soap(self) :
	if not self.soap_client :
	    self.soap_client = IsySoap(self)

	return self.soap_client


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
	xurl = "/rest/subscriptions"
        if self.debug & 0x02 : print("xurl = " + xurl)
	resp = self._getXMLetree(xurl)
	self._printXML(resp)
	return et2d(resp)

    def network(self) :
	xurl = "/rest/network"
        if self.debug & 0x02 : print("xurl = " + xurl)
	resp = self._getXMLetree(xurl)
	self._printXML(resp)
	return et2d(resp)

    def sys(self) :
	xurl = "/rest/sys"
        if self.debug & 0x02 : print("xurl = " + xurl)
	resp = self._getXMLetree(xurl)
	self._printXML(resp)
	return et2d(resp)

    def time(self) :
	xurl = "/rest/time"
	resp = self._getXMLetree(xurl)
	self._printXML(resp)
	return et2d(resp)

    def batch( self, on=-1) :
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
	Returns electricity module info and specifically Energy Monitor,
	Open ADR and Flex Your Power status
	Only applicable to 994 Z Series.
	"""

	xurl = "/rest/electricity"
        if self.debug & 0x02 :
            print("xurl = " + xurl)
	resp = self._getXMLetree(xurl)
	if resp != None :
	    self._printXML(resp)
	    return et2d(resp)


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
        #if isinstance(self._isy_event, ISYEvent) :
	#    #ISYEvent._stop_event_loop()
	if hasattr(self._isy_event, "_shut_down") :
	    self._isy_event._shut_down = 1


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
        fi = open(filen, 'w')
        pprint.pprint(d, fi)
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
