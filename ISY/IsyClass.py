#!/usr/bin/python

"""Simple Python lib for the ISY home automation netapp

 This is a Python interface to the ISY rest interface
 providomg simple commands to query and control registared Nodes and Scenes
 and well as a method of setting or querying vars

"""

# pylint: disable=unsubscriptable-object,unsupported-membership-test,unused-argument

# ppylint: disable=superfluous-parens,unsubscriptable-object
# global-statement,protected-access,invalid-name,missing-docstring,broad-except


from __future__ import print_function
# from xml.dom.minidom import parse, parseString
# from StringIO import StringIO
# import xml.etree.ElementTree as # ET
# import base64
import re
import os
import sys
# import string
import time
from warnings import warn
# import logging
import xml.etree.ElementTree as ET
from configparser import SafeConfigParser as ConfigParser
# from ConfigParser import SafeConfigParser as ConfigParser
# from ConfigParser import Error as ConfigParserError

import json


# logging.basicConfig(level=logging.INFO)

import collections



# try:
#    from suds.client import Client
#    suds_import = 1
# except ImportError:
#    suds_import = 0


import pprint

import ISY.IsyDebug as IsyD
import ISY.IsyExceptionClass as IsyE
from .IsyUtilClass import IsyUtil, IsySubClass, et2d
# from .IsyNodeClass import IsyNode, IsyScene, IsyNodeFolder, _IsyNodeBase
# from .IsyProgramClass import *
# from .IsyVarClass import IsyVar
# from .IsyEvent import ISYEvent

# import netrc

__author__ = 'Peter Shipley <peter.shipley@gmail.com>'
__copyright__ = "Copyright (C) 2017 Peter Shipley"
__license__ = "BSD"
__version__ = "0.1.20170829"

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
# 0x0400 = report raw events
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

_pro_models = [1100, 1110, 1040, 1050]

__all__ = ['Isy', 'IsyGetArg']


# if hasattr(instance, 'tags') and isinstance(instance.tags, dict):
#     for tag in instance.tags:

# def batch .write


# _nodedict     dictionary of node data indexed by node ID
# node2addr     dictionary mapping node names to node ID
# nodeCdict     dictionary cache or node objects indexed by node ID

def _action_val(a):
    if isinstance(a, str):
        return a
    elif isinstance(a, dict):
        if "#val" in a:
            return a["#val"]
    else:
        return None

class Isy(IsyUtil):
    """ Obj class the represents the ISY device

        Keyword Args:
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
    from ._isyclimate import load_clim, clim_get_val, clim_query, clim_iter
    from ._isyvar import load_vars, \
        var_get_value, var_set_value, _var_set_value, \
        var_addrs, var_ids, get_var, _var_get_id, \
        var_get_type, var_iter, var_add, \
        var_delete, _var_delete, \
        var_rename, _var_rename, \
        var_refresh_value

    from ._isyprog import load_prog, get_prog, _prog_get_id, \
        prog_iter, prog_get_src, prog_addrs, \
        prog_comm, _prog_comm, \
        prog_get_path, _prog_get_path, \
        prog_rename, _prog_rename

    from ._isynode import load_nodes, _gen_member_list, _gen_folder_list, \
        _gen_nodegroups, _gen_nodedict, node_names, scene_names, \
        node_addrs, scene_addrs, get_node, _node_get_id, node_get_prop, \
        node_set_prop, _node_send, node_comm, \
        load_node_types, node_get_type, node_iter, _updatenode, \
        node_get_path, _node_get_path, _node_get_name, \
        node_set_powerinfo, node_enable, \
        node_del, _node_remove, \
        node_restore, node_restore_all, \
        node_get_notes
        # _status_reload
        # node_rename,

    from _isy_readevent import start_event_thread, stop_event_thread

    from ._isynet_resources import _load_networking, load_net_resource, \
        _net_resource_get_id, net_resource_run, \
        net_resource_names, net_resource_iter, \
        load_net_wol, net_wol, _net_wol_get_id, net_wol_names, net_wol_iter, \
        net_wol_ids, net_resource_ids

#    from ._isyzb import load_zb, zb_scannetwork, zb_ntable, zb_ping_node, \
#               zbnode_addrs, zbnode_names, zbnode_iter


##    set_var_value, _set_var_value, var_names



    def __init__(self, **kwargs):
        # pylint: disable=super-init-not-called,too-many-statements,too-many-branches


        # default
        self.userl = self.userp = "admin"
        self.addr = None
        self.parsearg = None
        self.debug = 0
        self.event_thread = None


        self.config_file = kwargs.get("config_file", "isylib.cfg")

        # check for "isylib.cfg"
        self.read_config()

        #
        # Keyword args and env
        #
        self.userl = kwargs.get("userl", os.getenv('ISY_USER', self.userl))
        self.userp = kwargs.get("userp", os.getenv('ISY_PASS', self.userp))
        self.addr = kwargs.get("addr", os.getenv('ISY_ADDR', self.addr))

        # (self.userl, self.userp, self.addr) = authtuple

        # print("AUTH: ", self.addr, self.userl, self.userp)

        if 'debug' in kwargs:
            self.debug = kwargs['debug']

        if "ISY_DEBUG" in os.environ:
            self.debug = self.debug & int(os.environ["ISY_DEBUG"])


        # self.cachetime = kwargs.get("cachetime", 0)
        self.faststart = kwargs.get("faststart", 1)
        self.eventupdates = kwargs.get("eventupdates", 0)

        # and experiment alt to IsyGetArg
        self.parsearg = kwargs.get("parsearg", False)
        if self.parsearg:
            self.parse_args()

        self._isy_event = None
        self.event_heartbeat = 0
        self.error_str = ""
        self.callbacks = None
        self._is_pro = True


        # data dictionaries for ISY state
        self._name2id = dict()
        self.controls = None
        self.name2control = None
        self._nodefolder = {}
        self._folder2addr = {}
        self._progdict = None
        self._nodedict = {}
        self._nodegroups = None
        self._groups2addr = {}
        self._node2addr = {}
        self._nodeCategory = None
        self._vardict = None
        self._wolinfo = None
        self._net_resource = None
        self.climateinfo = None

        self.isy_status = dict()
        self.zigbee = dict()

        if self.addr is None:
            from .IsyDiscover import isy_discover

            units = isy_discover(count=1)
            for device in units.values():
                self.addr = device['URLBase'][7:]
                self.baseurl = device['URLBase']
        else:
            self.baseurl = "http://" + self.addr

        if self.addr is None:
            warn("No ISY address : guessing \"isy\"")
            self.addr = "isy"

#       print("\n\taddr", "=>", self.addr, "\n\n")


#       if (not self.userl or not self.userp):
#           netrc_info = netrc.netrc()
#           login, account, password = netrc_info.authenticators(self.addr)
#           print("login", "=>", repr(login))
#           print("account", "=>", repr(account))
#           print("password", "=>", repr(password))
#           self.userl = "admin"
#           self.userp = "admin"

        if self.debug & IsyD._debug_loads_:
            print("class Isy __init__")
            print("debug ", self.debug)
            # print("cachetime ", self.cachetime)
            print("faststart ", self.faststart)
            print("address ", self.addr)

        # parse   ISY_AUTH as   LOGIN:PASS

        #
        # general setup logic
        #

        self._initReqSession()

        self._req_session.auth = (self.userl, self.userp)

        if self.debug & 0x02:
            print("baseurl: " + self.baseurl + " : " + self.userl + " : " + self.userp)

        if self.faststart < 2:
            try:
                self.load_conf()
            except Exception as e:
                print("Unexpected error:", sys.exc_info()[0])
                print('Problem connecting with ISY device :', self.addr)
                print(e)
                # raise IsyE.IsyCommunicationError(e)
                raise


        if not self.faststart:
            self.load_nodes()

        # There for id's to Node/Var/Prog objects
        self.nodeCdict = dict()
        self.varCdict = dict()
        self.progCdict = dict()
        self.folderCdict = dict()

        if self.eventupdates:
            if not self._progdict:
                self.load_prog()
            if not self._nodedict:
                self.load_nodes()
            self.start_event_thread()

    # and experimental alternitive to IsyGetArg
    def parse_args(self):
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

        if args.addr:
            self.addr = args.addr

        if args.user:
            self.userl = args.user

        if args.passw:
            self.userp = args.passw

        if args.debug:
            self.debug = args.debug

        self.parser = parser

    def read_config(self):

        ini = ConfigParser()
        # ?? os.path.expanduser('~/.config/isylib/isylib.cfg')
        ini.read([self.config_file, "." + self.config_file, os.path.expanduser('~/.' + self.config_file)])

        if ini.has_option('libisy', 'addr'):
            self.addr = ini.get('libisy', 'addr')

        if ini.has_option('libisy', 'user'):
            self.userl = ini.get('libisy', 'user')

        if ini.has_option('libisy', 'pass'):
            self.userp = ini.get('libisy', 'pass')

        if ini.has_option('libisy', 'debug'):
            self.debug = ini.getint('libisy', 'debug')


    def _format_val(self, vs):
        try:
            if isinstance(vs, dict):
                if "#val" in vs:
                    v = int(vs["#val"])
                else:
                    return None
            else:
                v = int(vs)
        except ValueError:
            return "0"
        else:
            if v == 0:
                return "off"
            elif v == 255:
                return "on"

            return str((int(v)*100) // 255)


    def addnode(self, nid=None, nname=None, ntype=None, flag="0"):
        """
            Adds a predefined node for a device with a given address

            args:
                nid
                nname
                ntype
                flag

        """
        if nname is None:
            nname = nid
        if nid is None:
            raise IsyE.IsyValueError("invalid node id : " + type)
        if type is None:
            raise IsyE.IsyValueError("invalid node type : " + type)

        return  self.soapcomm("AddNode", nid=nid, name=nname, type=ntype, flag=flag)


    def getsystemdatetime(self):
        """
            timestamp of when ISY was last started
        """
        r = self.soapcomm("GetSystemDateTime")
        return r

    def startuptime(self):
        """
            timestamp of when ISY was last started
        """
        r = self.soapcomm("GetStartupTime")
        return r

    def webcam_get(self):
        """
            get webcam list avalible in ISY's ajax web UI

            returns dict
        """
        # campath="/WEB/CONF/cams.jsn"
        r = self.soapcomm("GetSysConf", name="/WEB/CONF/cams.jsn")
        return json.loads(r)




    def webcam_add(self, brand=None, num=None, ip=None, model='1', name=None, passwd='', port='80', user=''):
        """
            Add webcam to UI

                args:
                    brand               brand of cam (one of : Foscam Smarthome Axis Panasonic MJPGstreamer)
                    ip                  IP of cam
                    port                TCP port for cam (default = 80)
                    model
                    name
                    user
                    passwd

        """
        # pylint: disable=too-many-arguments
        if not (brand is None) \
            and (brand.lower() not in ["foscam", "smarthome", "axis", "panasonic", "mjpgstreamer"]):
            raise IsyE.IsyValueError("webcam_add : invalid value for arg 'brand' ")
        else:
            brand = brand.lower()

        if ip is None:
            raise IsyE.IsyValueError("webcam_add : invalid ip")

        if name is None:
            name = brand

        camlist = self.webcam_get()

        if 'lastId' in camlist:
            maxid = int(camlist['lastId']) + 2
        else:
            maxid = camlist.__len__() + 2

        if num is None:
            for i in range(1, maxid):
                if str(i) not in camlist:
                    num = str(i)
                    break
            else:
                raise RuntimeError("webcam_add : failed cam index")
        elif isinstance(num, int):
            num = str(num)

        if self.debug & 0x100:
            print("using num : ", num)

        newcam = {
            'brand': brand, 'ip': ip, 'model': model,
            'name': name, 'pass': passwd, 'port': port,
            'user': user}

        camlist[num] = newcam

        if self.debug & 0x100:
            print("webcam_add : ",)
            pprint.pprint(camlist)

        if num > camlist['lastId']:
            if self.debug & 0x100:
                print("new lastId = ", num, ":", camlist['lastId'])
            camlist['lastId'] = num

        return self._webcam_set(camlist)

    def webcam_del(self, camid=None):
        """
            delete an entery from UI's webcam list

            arg:
                camid           index for camera in camlist
        """
        if camid is None:
            raise IsyE.IsyValueError("webcam_del : arg camid is None")

        camlist = self.webcam_get()

        if self.debug & 0x100:
            pprint.pprint(camlist)

        if isinstance(camid, int):
            camid = str(camid)

        if camid not in camlist:
            raise IsyE.IsyValueError("webcam_del : invalid camid")

        del camlist[camid]

        if 'lastId' in camlist:
            maxid = int(camlist['lastId']) + 2
        else:
            maxid = camlist.__len__() + 2

        lastid = -1
        for i in range(1, maxid):
            if str(i) in camlist and lastid < i:
                lastid = i

        camlist['lastId'] = str(lastid)

        return self._webcam_set(camlist)



    def _webcam_set(self, camdict=None):
        if camdict is None:
            raise IsyE.IsyValueError("_webcam_set : arg camdict invalid")

        camjson = json.dumps(camdict, sort_keys=True)
        r = self._sendfile(data=camjson, filename="/WEB/CONF/cams.jsn", load="n")
        return r

    def set_debug_level(self, level=1):
        """
            Sets the debug options and current level

            args:
                option    value 0 -> 3
        """
        ret = self.soapcomm("SetDebugLevel", option=level)
        return ret

    def get_debug_level(self):
        """
            Gets the debug options and current level
        """
        ret = self.soapcomm("GetDebugLevel",)
        return ret

    def node_discover_start(self, nodetype=None):
        soapargs = dict()
        if nodetype is not None:
            soapargs['type'] = nodetype
        ret = self.soapcomm("StartNodesDiscovery", **soapargs)
        return ret

    def node_discover_stop(self, flag="1"):
        """
            Puts ISY out of discovery (linking) mode

            The flag decides the operations (reset, crawl, spider)
            to be performed after device(s) are discovered

            args:
                NodeOperationsFlag      enum value '1', '2', '3' or '4'

            Valid values
                1 = add the node and reset all previous setting if any
                2 = unused
                3 = add the node, find all the associated nodes, and create all the linkages thereto
                4 = add the node, find all the associated nodes, but do not create any linkages

        """
        flag = str(flag)
        if flag not in ['1', '2', '3', '4']:
            raise IsyE.IsyValueError("invalid flag value : " + flag)


        # if code == 501 then device was alread not in link/Discovery mode
        ret = self.soapcomm("CancelNodesDiscovery", flag=flag)

        return ret



#    def node_get_props(self, naddr):
#       """"
#       Soap call GetNodeProps
#       """
#       (nodetype, node_id) = self._node_get_id(naddr)
#
#       if self.debug & 0x04:
#           print("node_get_props", naddr)
#
#       if not node_id:
#           raise LookupError(
#               "node_del: {0} not a node ({1}={2} )".format(
#                       naddr, node_id, nodetype))
#
#       try:
#           r = self.soapcomm("GetNodeProps", node=node_id)
#       except IsySoapError as se:
#
#       # if error code is 404 then Node did not exist or was already deleted
#       # this is messy and needs to change or be removed
#           code = se.code()
#           if code == 404:
#               return None
#           raise
#       else:
#           return et2d(ET.fromstring(r))




    #
    # need to add code to update name2id and *2addr lookup arrays
    #
    def rename(self, objid, nname):
        """ rename

                args:
                    id = Node/Scene/Folder name or ID
                    name = new name

            calls SOAP RenameNode() / RenameGroup() / RenameFolder()
        """
        (idtype, nid) = self._node_get_id(objid)
        if nid is None:
            raise IsyE.IsyValueError("unknown node/obj : " + objid)
        if idtype == "node":
            return self.soapcomm("RenameNode", id=nid, name=nname)
        elif idtype == "group":
            return self.soapcomm("RenameGroup", id=nid, name=nname)
        elif idtype == "folder":
            return self.soapcomm("RenameFolder", id=nid, name=nname)
        elif idtype == "var":
            # return self.var_rename(var=nid, name=nname)
            raise IsyE.IsyValueError("can not rename var, use var_rename() ")
        elif idtype == "prog":
            raise IsyE.IsyValueError("can not rename prog use prog_rename() ")
        else:
            raise IsyE.IsyValueError("node/obj " + objid + " not node (" + idtype + ")")

    #
    # need to add code to update name2id and *2addr lookup arrays
    #
    def node_rename(self, nodeid, nname):
        """ rename Node

                args:
                    id = Node ID
                    name = new Node name

            calls SOAP RenameNode()
        """
        # idtype
        (_, nid) = self._node_get_id(nodeid)
        if nid is None:
            raise IsyE.IsyValueError("unknown node/obj : " + nodeid)
        print("nodeid ", nodeid)
        print("nid ", nid)
        return self.soapcomm("RenameNode", id=nid, name=nname)

#    def node_new(self, sid, nname):
#       """ create new Folder """
#       return  self.soapcomm("AddNode", id=1234, name=nname, type="T", flag="Y")

    ## scene

    #
    # need to add code to update name2id and *2addr lookup arrays
    #
    def scene_rename(self, sid, fname):
        """ rename Scene/Group

                args:
                    sid = a Scene/Group id
                    name = new name


            calls SOAP RenameGroup()
        """
        (_, grid) = self._node_get_id(sid)
        return self.soapcomm("RenameGroup", id=grid, name=fname)

    #
    # need to add code to update name2id and *2addr lookup arrays
    #
    def scene_del(self, sid=None):
        """ delete Scene/Group

                args:
                    id : Scene address, name or Folder Obj

            calls SOAP RemoveGroup()
        """
        (_, sceneid) = self._node_get_id(sid)
        if sceneid is None:
            raise IsyE.IsyValueError("no such Scene : " + str(sid))
        #
        # add code to update self._nodegroups
        #
        return  self.soapcomm("RemoveGroup", id=sceneid)

    #
    # need to add code to update name2id and *2addr lookup arrays
    #
    def scene_new(self, nid=0, sname=None):
        """ new Scene/Group

                args:
                    id = a unique (unused) Group ID
                    name = name for new Scene/Group

            ***No error is given if Scene/Group ID is already in use***

            calls SOAP AddGroup()
        """
        #if not isinstance(sname, str) or not len(sname):
        if not isinstance(sname, str) or not sname:
            raise IsyE.IsyValueError("scene name must be non zero length string")

        if nid == 0:
            iid = 30001
            nid = str(iid)
            while nid in self._nodefolder or nid in self._nodegroups:
                iid += 1
                nid = str(iid)
        if sname is None:
            sname = nid
        self.soapcomm("AddGroup", id=nid, name=sname)
        #
        # add code to update self._nodegroups
        #
        return nid

    def scene_add_node(self, groupid, nid, nflag=0x10):
        """ add node to Scene/Group

                args:
                    group = a unique (unused) scene_id ID
                    node = id, name or Node Obj
                    flag = set to 0x10 if node is a controler for Scene/Group
                           set to 0x20 if node is responder for Scene/Group

            Add new Node to Scene/Group


            calls SOAP MoveNode()
        """
        (_, nodeid) = self._node_get_id(nid)
        if nodeid is None:
            raise IsyE.IsyValueError("no such Node : " + str(nid))
        r = self.soapcomm("MoveNode", group=groupid, node=nodeid, flag=nflag)
        return r

    def scene_del_node(self, groupid, nid):
        """ Remove Node from Scene/Group

                args:
                    group = address, name or Scene Obj
                    id = address, name or Node Obj

            calls SOAP RemoveFromGroup()
        """
        (_, nodeid) = self._node_get_id(nid)
        if nodeid is None:
            raise IsyE.IsyValueError("no such Node : " + str(nid))
        r = self.soapcomm("RemoveFromGroup", group=groupid, id=nodeid)
        return r

    ## folder

    #
    # need to add code to update name2id and *2addr lookup arrays
    #
    def folder_rename(self, fid, fname):
        """ rename Folder

                args:
                    id = folder ID
                    name = new folder name

            calls SOAP RenameFolder()
        """
        (_, fid) = self._node_get_id(fid)
        r = self.soapcomm("RenameFolder", id=fid, name=fname)
        return r

    def folder_new(self, fid, fname):
        """ create new Folder

                args:
                    folder_id = a unique (unused) folder ID
                    folder name = name for new folder


            returns error if folder ID is already in use

            calls SOAP AddFolder()
        """
        # ppylint: disable=unsubscriptable-object
        if not self._nodefolder:
            self.load_nodes()
        if fid == 0:
            iid = 50001
            fid = str(iid)
            while fid in self._nodefolder or fid in self._nodegroups:
                iid += 1
                fid = str(iid)
        r = self.soapcomm("AddFolder", fid=1234, name=fname)
        if isinstance(r, tuple) and r[0] == '200':
            self._nodefolder[fid] = dict()
            self._nodefolder[fid]['address'] = fid
            self._nodefolder[fid]['folder-flag'] = '0'
            self._nodefolder[fid]['name'] = 'fname'

        return r

    def folder_del(self, fid):
        """ delete folder
                args:
                    fid : folder address, name or Folder Obj

            calls SOAP RemoveFolder()
        """
        (_, fid) = self._node_get_id(fid)
        if fid is None:
            raise IsyE.IsyValueError("Unknown Folder : " + str(fid))
        r = self.soapcomm("RemoveFolder", id=fid)
        if isinstance(r, tuple) and r[0] == '200':
            self._nodefolder[fid] = dict()

    # SetParent(node, nodeType, parent, parentType)
    def folder_add_node(self, nid, nodeType=1, parent="", parentType=3):
        """ move node/scene from folder

            Named args:
                node
                nodeType
                parent
                parentType

            sets Parent for node/scene

            calls SOAP SetParent()
        """
        # idtype
        (_, nodeid) = self._node_get_id(nid)
        if nodeid is None:
            raise IsyE.IsyValueError("no such Node/Scene : " + str(nid))

        if parent != "":
            (_, fldid) = self._node_get_id(parent)
            if fldid is None:
                raise IsyE.IsyValueError("no such Folder : " + str(parent))
            parentid = fldid
        else:
            parentid = parent

        r = self.soapcomm("SetParent", node=nodeid, nodeType=nodeType, parent=parentid, parentType=parentType)
        return r

    def folder_del_node(self, nid, nodeType=1):
        """ remove node from folder

            args:
                node
                nodeType

            remove node/scene from folder (moves to default/main folder)

            calls SOAP SetParent()
        """
        return self.folder_add_node(nid, nodeType=nodeType, \
                parent="", parentType=3)


    def set_user_credentials(self, name=None, password=None):
        """
            Changes the userid and password for a user (admin )

            args:
                name         user name
                password     user password
        """
        if name is None:
            raise IsyE.IsyValueError("set_user_credentials : name argument required")
        if password is None:
            raise IsyE.IsyValueError("set_user_credentials : pass argument required")
        return self.soapcomm("SetUserCredentials", name=name, password=password)

    def reboot(self):
        """ Reboot ISY Device
                args: none

            calls SOAP Reboot()
        """
        return self.soapcomm("Reboot")

    #
    # User web  commands
    #
    def user_fsstat(self):
        """ ISY Filesystem Status

            calls SOAP GetFSStat()
        """
        r = self.soapcomm("GetFSStat")
        return et2d(ET.fromstring(r))


    def user_dir(self, name="", pattern=""):
        """ Get User Folder/Directory Listing

            Named args:
                name
                pattern

            call SOAP GetUserDirectory()
        """
        r = self.soapcomm("GetUserDirectory", name=name, pattern=pattern)
        # print("GetUserDirectory : ", r)
        return et2d(ET.fromstring(r))

    def user_mkdir(self, name=None):
        """ Make new User Folder/Directory

            Named args:
                name

            call SOAP MakeUserDirectory()
        """
        if name is None:
            raise IsyE.IsyValueError("user_mkdir : invalid dir name")
        if name[0] != "/":
            name = "/USER/WEB/" + name
        r = self.soapcomm("MakeUserDirectory", name=name)
        return et2d(ET.fromstring(r))

    def user_rmdir(self, name=None):
        """ Remove User Folder/Directory

            Named args:
                name

            call SOAP RemoveUserDirectory()
        """
        if name is None:
            raise IsyE.IsyValueError("user_rmdir : invalid dir name")
        name = name.rstrip('/')
        if name[0] != "/":
            name = "/USER/WEB/" + name
        r = self.soapcomm("RemoveUserDirectory", name=name)
        return et2d(ET.fromstring(r))


    def user_mv(self, name=None, newName=None):
        """ Move/Rename User Object (File or Directory)

            Named args:
                oldn
                newn

            call SOAP MoveUserObject()
        """
        if name is None or newName is None:
            raise IsyE.IsyValueError("user_mv : invalid name")
        if name[0] != "/":
            name = "/USER/WEB/" + name
        if newName[0] != "/":
            newName = "/USER/WEB/" + newName
        r = self.soapcomm("MoveUserObject", name=name, newName=newName)
        return r

    def user_rm(self, name=None):
        """ Remove User File

            Named args:
                name

            call SOAP RemoveUserFile()
        """
        if name is None:
            raise IsyE.IsyValueError("user_mkdir : invalid name")
        if name[0] != "/":
            name = "/USER/WEB/" + name
        r = self.soapcomm("RemoveUserFile", name=name)
        return r

    def user_getfile(self, name=None):
        """ Get User File

            Named args:
                name

            call SOAP GetUserFile()
        """
        # if not len(name):
        if not name:
            raise IsyE.IsyValueError("user_getfile : invalid name")
        if name[0] != "/":
            name = "/USER/WEB/" + name

        r = self.soapcomm("GetUserFile", name=name)
        return r


    def user_uploadfile(self, srcfile="", name=None, data=""):
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
        if name is None:
            raise IsyE.IsyValueError("user_uploadfile : invalid name")
        r = self.sendfile(src=srcfile, filename=name, data=data)
        return r

    def queryall(self, node=None, flag=None):
        """
            Queries a node, a scene, or even the whole network

            Named args:
                node : name of node or scene to query (optional)
                flag : enum { '1', '4', '8' }
        """
        soapargs = dict()
        if node is not None:
            soapargs['node'] = node # ntype
        if flag is not None:
            soapargs['flag'] = flag
        r = self.soapcomm("QueryAll", **soapargs)
        return r


    #
    #  Util Funtions
    #
    def _preload(self, rload=0):
        """ Internal function

            preload all data tables from ISY device into cache
            normally this is done "on demand" as needed
        """
        if rload or not self.controls:
            self.load_conf()

        if rload or not self._nodedict:
            self.load_nodes()

        # self._gen_member_list()
        # if rload or not self.climateinfo:
            # self.load_clim()

        if rload or not self._vardict:
            self.load_vars()

        if rload or not self._progdict:
            self.load_prog()

        # if rload or not self._wolinfo:
            # self.load_wol()

        if rload or not self._nodeCategory:
            self.load_node_types()

    def _savedict(self):
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
    def load_conf(self):
        """ Load configuration of the system with permissible commands

            args : none

            internal function call

        """
        # pylint: disable=too-many-branches
        if self.debug & 0x01:
            print("load_conf")
        configinfo = self._getXMLetree("/rest/config")
        # Isy._printXML(configinfo)
        # IsyE.IsyCommunicationError

        if configinfo is None:
            raise IsyE.IsyCommunicationError("Load Configuration Fail : " \
                        + self.error_str)

        self.name2control = dict()
        self.controls = dict()
        for ctl in configinfo.iter('control'):
            # self._printXML(ctl)
            # self._printinfo(ctl, "configinfo : ")
            cprop = dict()

            for child in list(ctl):
                # print("child.tag " + str(child.tag) + "\t=" + str(child.text))
                if child.tag == "actions":
                    adict = dict()
                    for act in child.iter('action'):
                        n = act.find('label').text
                        v = act.find('name').text
                        adict[n] = v
                    cprop[child.tag] = adict
                else:
                    # self._printinfo(child, "child")
                    cprop[child.tag] = child.text

                # check this
                for n, v in child.items():
                    cprop[n] = v

            # print("cprop ", cprop)
            if "name" in cprop:
                self.controls[cprop["name"].upper()] = cprop
                if "label" in cprop:
                    self.name2control[cprop["label"].upper()] \
                        = cprop["name"].upper()

        self.config = dict()
        for v in ("platform", "app_version", "driver_timestamp",
                  "app", "build_timestamp"):
            n = configinfo.find(v)
            if n is not None:
                if isinstance(n.text, str):
                    self.config[v] = n.text

        n = configinfo.find("root/id")
        if n is not None:
            if isinstance(n.text, str):
                self.config['id'] = n.text

        xelm = configinfo.find("product/id")
        if xelm is not None:
            if hasattr(xelm, 'text'):
                self.config["product_id"] = xelm.text


        # print("self.controls : ", self.controls)
        # self._printdict(self.controls)
        # print("self.name2control : ", self.name2control)

    def _get_control_id(self, comm):
        """ command name to command ID """
        if not self.controls:
            self.load_conf()
        c = comm.strip().upper()
        if c in self.controls:
            return c
        if c in self.name2control:
            return self.name2control[c]
        return None

    ##
    ## property
    ##
    def _get_platform(self):
        """ name of ISY platform (readonly) """
        return self.config["platform"]
    platform = property(_get_platform)

    def _get_id(self):
        """ id of ISY (readonly) """
        return self.config["id"]
    id = property(_get_id)

    def _get_app_version(self):
        """ name of ISY app_version (readonly) """
        return self.config["app_version"]
    app_version = property(_get_app_version)

#    def _get_debug(self):
#        """ debug flag for Obj """
#        return self._debug
#    def _set_debug(self, val):
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
        if self.debug & 0x01:
            print("load_log_type")

    def load_log_id(self):
        """ load log id tables

        **not implemented **
        """
        if self.debug & 0x01:
            print("load_log_id")

    def log_reset(self, errorlog=0):
        """ clear log lines in ISY

            args:
                errorlog = flag clear error

        """
        self.log_query(errorlog, 1)

    def log_iter(self, error=0):
        """ iterate though log lines

            args:
                error : return error logs or now

            returns:
                Return an iterator log enteries
        """
        for l in self.log_query(error):
            yield l

    def log_query(self, errorlog=0, resetlog=0):
        """ get log from ISY """
        xurl = self.baseurl + "/rest/log"
        if errorlog:
            xurl += "/error"
        if resetlog:
            xurl += "?reset=true"
        if self.debug & 0x02:
            print("xurl = " + xurl)

        data = self._geturl(xurl)

        return data.splitlines()

    def log_format_line(self, line):
        """ format a ISY log line into a more human readable form

        ** not implemented **
        """
        pass


    ##
    ## X10 Code
    ##
    _x10re = re.compile(r'([a-pA-P]\d{,2)')
    _x10comm = {
        'alllightsoff' : 1,
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
        'extended data' : 16
        }

    def _get_x10_comm_id(self, comm):
        """ X10 command name to id """
        comm = str(comm).strip().lower()
        if comm.isdigit():
            if int(comm) >= 1 and int(comm) <= 16:
                return comm
            else:
                raise IsyE.IsyValueError("bad x10 command digit : " + comm)
        if comm in self._x10comm:
            return self._x10comm[comm]
        else:
            raise IsyE.IsyValueError("unknown x10 command : " + comm)


    def x10_comm(self, unit, cmd):
        """ direct send x10 command """
        xcmd = self._get_x10_comm_id(str(cmd))
        unit = unit.strip().upper()

        if not re.match(r'[A-P]\d{,2}', unit):
            raise IsyE.IsyValueError("bad x10 unit name : " + unit)

#        print("X10 sent : " + str(unit) + ": " + str(xcmd))
        xurl = "/rest/X10/" + str(unit) + "/" + str(xcmd)
        if self.debug & 0x02:
            print("xurl = " + xurl)
        resp = self._getXMLetree(xurl)
        # self._printXML(resp)
        # self._printinfo(resp)
        if resp.attrib["succeeded"] != 'true':
            raise IsyE.IsyResponseError("X10 command error : unit=" + str(unit) + " cmd=" + str(cmd))

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

    def subscriptions(self):
        """  get event subscriptions list and states

            args: none

        Returns the state of subscriptions

        calls : /rest/subscriptions
        """
        xurl = "/rest/subscriptions"
        if self.debug & 0x02:
            print("xurl = " + xurl)
        resp = self._getXMLetree(xurl)
        # self._printXML(resp)
        return et2d(resp)

    def network(self):
        """ network configuration

            args: none

        Returns network configuration
        calls /rest/network
        """

        xurl = "/rest/network"
        if self.debug & 0x02:
            print("xurl = " + xurl)
        resp = self._getXMLetree(xurl)
        # self._printXML(resp)
        return et2d(resp)

    def sys(self):
        """ system configuration

            args: none

        calls : /rest/sys
        """
        xurl = "/rest/sys"
        if self.debug & 0x02:
            print("xurl = " + xurl)
        resp = self._getXMLetree(xurl)
        # self._printXML(resp)
        return et2d(resp)

    def time(self):
        """  system time of ISY

            args: none

        calls : /rest/time
        """
        xurl = "/rest/time"
        resp = self._getXMLetree(xurl)
        # self._printXML(resp)
        return et2d(resp)

    def batch(self, on=-1):
        """ Batch mode

            args values:
                1 = Turn Batch mode on
                0 = Turn Batch mode off
                -1 or None = Return Batch mode status

        calls /rest/batteryPoweredWrites/
        """
        xurl = "/rest/batteryPoweredWrites/"

        if on == 0:
            xurl += "/off"
        elif on == 1:
            xurl += "/on"

        if self.debug & 0x02:
            print("xurl = " + xurl)
        resp = self._getXMLetree(xurl)
        if resp is None:
            print('The server couldn\'t fulfill the request.')
            raise IsyE.IsyResponseError("Batch")
        else:
            # self._printXML(resp)
            return resp

    #/rest/batterypoweredwrites
    def batterypoweredwrites(self, on=-1):
        """ Battery Powered Writes

            args values:
                1 = Turn Batch mode on
                0 = Turn Batch mode off
                -1 or None = Return Batch mode status

        returns status of Battery Powered device operations
        calls /rest/batteryPoweredWrites/
        """
        xurl = "rest/batteryPoweredWrites/"

        if on == 0:
            xurl += "/off"
        elif on == 1:
            xurl += "/on"

        if self.debug & 0x02:
            print("xurl = " + xurl)
        resp = self._getXMLetree(xurl)
        if resp is not None:
            # self._printXML(resp)
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
        if self.debug & 0x02:
            print("xurl = " + xurl)
        resp = self._getXMLetree(xurl)
        if resp is not None:
            # self._printXML(resp)
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

        if not isinstance(func, collections.Callable):
            raise IsyE.IsyValueError("callback_set : Invalid Arg, function not callable")
            # func.__repr__()

        if self.callbacks is None:
            self.callbacks = dict()

        #(idtype, nodeid) = self._node_get_id(nid)
        (_, nodeid) = self._node_get_id(nid)
        if nodeid is None:
            # raise LookupError("no such Node : " + str(nodeid))
            self.callbacks[nid] = (func, args)
        else:
            self.callbacks[nodeid] = (func, args)

    def callback_get(self, nid):
        """get a callback funtion for a Nodes

            args:
                node id

        returns referance to registared callback function for a node
        no none exist then value "None" is returned
        """

        if self.callbacks is not None:
            (_, nodeid) = self._node_get_id(nid)

            if nodeid is not None and nodeid in self.callbacks:
                return self.callbacks[nodeid]

        return None

    def callback_del(self, nid):
        """delete a callback funtion

            args:
                node id


            delete a callback funtion for a Node, if exists.

            no error is raised if callback does not exist
        """
        if self.callbacks is not None:
            (_, nodeid) = self._node_get_id(nid)
            if nodeid is not None and nodeid in self.callbacks:
                del self.callbacks[nodeid]

    ##
    ## support functions
    ##
    def _printinfolist(self, uobj, ulabel="_printinfo"):
        print("\n\n" + ulabel + " : ")
        for attr in dir(uobj):
            print("   obj.%s = %s" % (attr, getattr(uobj, attr)))
        print("\n\n")


    ##
    ## the following are obj independent get methods
    ##

    #
    # Untested
    #
    def gettype(self, nobj):
        if isinstance(nobj, IsySubClass):
            return nobj.objtype()
        #(idtype, nid) = self._node_get_id(nobj)
        (idtype, _) = self._node_get_id(nobj)
        return idtype

    #
    # Untested
    #
    def getid(self, objaddr):
        (_, nid) = self._node_get_id(objaddr)
        return nid

    #
    # Untested
    #
    def getobj(self, objid):
        """ access node obj line a dictionary entery """
        (idtype, nid) = self._node_get_id(objid)
        if nid is None:
            raise IsyE.IsyValueError("unknown node/obj : " + objid)
        if nid in self.nodeCdict:
            return self.nodeCdict[nid]

        if idtype in ['node', 'group', 'folder']:
            return self.get_node(nid)
        elif idtype == "var":
            return self.get_var(nid)
        elif idtype == "prog":
            return self.get_prog(nid)
        else:
            raise IsyE.IsyValueError("don't know how to get obj for type : " + idtype)

    ##
    ## Special Methods
    ##

    # Design question:
    # __get/setitem__  returns a node obj ?
    def __getitem__(self, nodeaddr):
        """ access node obj line a dictionary entery """
        if nodeaddr in self.nodeCdict:
            return self.nodeCdict[str(nodeaddr)]

        return self.get_node(nodeaddr)

    def __setitem__(self, nodeaddr, val):
        """ This allows you to set the status of a Node by
        addressing it as dictionary entery """
        val = int(val)
        if val > 0:
            self.node_comm(nodeaddr, "DON", val)
        else:
            self.node_comm(nodeaddr, "DOF")

    def __delitem__(self, nodeaddr):
        raise IsyE.IsyPropertyError("__delitem__ : can't delete nodes :  " + str(nodeaddr))

    def __iter__(self):
        """ iterate though Node Obj (see: node_iter() ) """
        return self.node_iter()

    def __del__(self):

        if self.debug & 0x80:
            print("__del__ ", self.__repr__())

        # if isinstance(self._isy_event, ISYEvent):
        #    #ISYEvent._stop_event_loop()
        if hasattr(self, "_isy_event"):
            if hasattr(self._isy_event, "_shut_down"):
                self._isy_event._shut_down = 1

        if hasattr(self, "nodeCdict"):
            self.nodeCdict.clear()

        if hasattr(self, "varCdict"):
            self.varCdict.clear()

        if hasattr(self, "progCdict"):
            self.progCdict.clear()

        if hasattr(self, "folderCdict"):
            self.folderCdict.clear()

        # the reasion for this is that
        # for k in self.nodeCdict.keys():
        #    del self.nodeCdict[k]
        # for k in self.varCdict.keys():
        #    del self.varCdict[k]
        # for k in self.progCdict.keys():
        #    del self.progCdict[k]
        # for k in self.folderCdict.keys():
        #    del self.folderCdict[k]


    def __repr__(self):
        return "<Isy %s at 0x%x>" % (self.addr, id(self))

#    def debugerror(self):
#       print("debugerror")
#        raise IsyE.IsyPropertyError("debugerror : test IsyPropertyError  ")


#    @staticmethod
#    def _printdict(dic):
#        """ Pretty Print dictionary """
#        print("===START===")
#        pprint.pprint(dic)
#        print("===END===")

    @staticmethod
    def _writedict(d, filen):
        """ Pretty Print dict to file  """
        with open(filen, 'w') as fi:
            pprint.pprint(d, fi)



def IsyGetArg(lineargs):
    """
        takes argv and extracts name/pass/ipaddr options
    """
    # print("IsyGetArg ", lineargs)
    addr = ""
    upass = ""
    uname = ""

    i = 0
    while i < len(lineargs):

        # print("len = ", len(lineargs))
        # print("lineargs =", lineargs)
        # print("check :", i, ":", lineargs[i],)

        if lineargs[i] in ['--isyaddress', '-isyaddress', '--isyaddr' '-isyaddr']:
            lineargs.pop(i)
            addr = lineargs.pop(i)
            continue

        elif lineargs[i] in ['--isypass', '-isypass']:
            lineargs.pop(i)
            upass = lineargs.pop(i)
            continue

        elif lineargs[i] in ['--isyuser', '-isyuser']:
            lineargs.pop(i)
            uname = lineargs.pop(i)
            continue

        i += 1

#    if not addr:
#        addr = os.getenv('ISY_ADDR', "isy")
#    if not uname:
#       userl = os.getenv('ISY_USER', "admin")
#    if not upass:
#       userp = os.getenv('ISY_PASS', "admin")

    return(addr, uname, upass)


def log_time_offset():
    """  calculates  time format offset used in ISY event logs to localtime format """
    lc_time = time.localtime()
    gm_time = time.gmtime()
    return ((lc_time[3]) - (gm_time[3] - gm_time[8])) * 60 * 60
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
