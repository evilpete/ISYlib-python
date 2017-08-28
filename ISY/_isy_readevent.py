"""
This is a subfile for IsyClass.py

These funtions are accessable via the Isy class opj
"""

from __future__ import print_function

__author__ = 'Peter Shipley <peter.shipley@gmail.com>'
__copyright__ = "Copyright (C) 2017 Peter Shipley"
__license__ = "BSD"


import sys
# from .IsyNodeClass import IsyNode, IsyScene, IsyNodeFolder#, _IsyNodeBase
# from .IsyUtilClass import IsySubClass

import ISY.IsyExceptionClass as IsyE
from ISY.IsyEvent import ISYEvent

# import IsyExceptionClass as IsyE
# from IsyEvent import ISYEvent

# #from .IsyExceptionClass import IsyPropertyError, IsyResponseError, IsyRuntimeWarning, \
#    IsyWarning, IsyCommunicationError, IsyInvalidCmdError, IsySoapError


# __all__ = ['start_event_thread', 'stop_event_thread']

#
# Event Subscription Code
# Allows for threaded realtime node status updating
#
def start_event_thread(self, mask=0):
    """  starts event stream update thread

    mask will eventually be used to "masking" events


    """
    from threading import Thread

    if self.debug & 0x40:
        print("start_event_thread")

    # if thread already runing we should update mask
    # if hasattr(self, 'event_thread') and isinstance(self.event_thread, Thread):
    if isinstance(self.event_thread, Thread):
        if self.event_thread.is_alive():
            print("Thread already running ?")
            return

    # st = time.time()
    # print("start preload")

    self._preload(rload=0)

    # sp = time.time()
    # print("start complete")
    # print("load in ", (sp - st))

    self._isy_event = ISYEvent(debug=self.debug)
    self._isy_event.subscribe(addr=self.addr, userp=self.userp, userl=self.userl)
    self._isy_event.set_process_func(self._read_event, self)

    self.event_thread = Thread(target=self._isy_event.events_loop, name="event_looper")
    self.event_thread.daemon = True
    self.event_thread.start()

    self.eventupdates = True
    # print(self.event_thread)

def stop_event_thread(self):
    """ Stop update thread """
    if hasattr(self._isy_event, "_shut_down"):
        self._isy_event._shut_down = 1
    self.eventupdates = False

# @staticmethod
def _read_event(self, evnt_dat, *arg):
    """ read event stream data and copy into internal state cache

        internal function call

    """

    # pylint: disable=too-many-branches,too-many-statements,too-many-locals
    # pylint: disable=unsubscriptable-object,unsupported-membership-test,unused-variable

    # print("_read_event")
    skip_default = [
        "DON", "DOF",
    ]
#               "_0", "_2", "_4", "_5", "_6", "_7", "_8",
#               "_9", "_10", "_11", "_12", "_13", "_14",
#               "_15", "_16", "_17", "_18", "_19", "_20",

    # skip = skip_default

    assert isinstance(evnt_dat, dict), "_read_event Arg must me dict"

    # event_targ holds the node address or var id
    # for the current event ( if applicable)
    event_targ = None

    # if evnt_dat["control"] in skip:
    #    return

    # print("evnt_dat ", evnt_dat)

    control_val = _action_val(evnt_dat["control"])
    # action_val = _action_val(evnt_dat["action"])

    #
    # Status/property changed
    #
    if control_val in ["ST", "RR", "OL", "DON"]:
        if evnt_dat["node"] in self._nodedict:
            # ADD LOCK ON NODE DATA
            # print("===evnt_dat :", evnt_dat)
            # print("===a :", ar)
            # print(self._nodedict[evnt_dat["node"]])
            target_node = self._nodedict[evnt_dat["node"]]

            event_targ = evnt_dat["node"]

            # create property if we do not have it yet
            if control_val not in target_node["property"]:
                target_node["property"][control_val] = dict()

            target_node["property"][control_val]["value"] \
                    = evnt_dat["action"]
            target_node["property"][control_val]["formatted"] \
                    = self._format_val(evnt_dat["action"])

            if self.debug & 0x10:
                print("_read_event :", evnt_dat["node"], control_val, evnt_dat["action"])
                print(">>>", self._nodedict[evnt_dat["node"]]["property"])
        else:
            warn("Event for Unknown node : {0}".format(evnt_dat["node"]), \
                    IsyE.IsyRuntimeWarning)

    elif control_val == "_0":  # HeartBeat
        # self.event_heartbeat = time.gmtime()
        pass

    #
    # handle VAR value change
    #
    elif control_val == "_1":  # Trigger Events

        #
        # action = "0" -> Event Status
        # action = "1" -> Client Should Get Status
        # action = "2" -> Key Changed
        # action = "3" -> Info String
        # action = "4" -> IR Learn Mode
        # action = "5" -> Schedule (schedule status changed)
        # action = "6" -> Variable Status (status of variable changed)
        # action = "7" -> Variable Initialized (initial value of a variable )
        #
        if evnt_dat["action"] == "0" and 'nr' in evnt_dat['eventInfo']:
            prog_id = '{0:0>4}'.format(evnt_dat['eventInfo']['id'])
            event_targ = prog_id

            if self.debug & 0x40:
                print("Prog Change/Updated :\t{0}".format(evnt_dat['eventInfo']['id']))
                print("Prog Id :\t", prog_id)
                print("evnt_dat :\t", evnt_dat)

            if self._progdict is None:
                self.load_prog(prog_id)
            elif prog_id in self._progdict:
                prog_dict = self._progdict[prog_id]
                if 'on' in evnt_dat['eventInfo']:
                    prog_dict['enabled'] = 'true'
                elif 'off' in evnt_dat['eventInfo']:
                    prog_dict['enabled'] = 'false'
                else:
                    pass

                if 'rr' in evnt_dat['eventInfo']:
                    prog_dict['runAtStartup'] = 'true'
                elif 'nr' in evnt_dat['eventInfo']:
                    prog_dict['runAtStartup'] = 'false'
                else:
                    pass

                # not all prog change events have time Info
                if 'r' in evnt_dat['eventInfo']:
                    prog_dict['lastRunTime'] = evnt_dat['eventInfo']['r']
                if 'f' in evnt_dat['eventInfo']:
                    prog_dict['lastFinishTime'] = evnt_dat['eventInfo']['f']
                if 'nsr' in evnt_dat['eventInfo']:
                    prog_dict['nextScheduledRunTime'] = evnt_dat['eventInfo']['nsr']

                if 's' in evnt_dat['eventInfo']:
                    ev_status = int(evnt_dat['eventInfo']['s'])
                    if ev_status & 0x01:
                        prog_dict['running'] = 'idle'
                    elif ev_status & 0x02:
                        prog_dict['running'] = 'then'
                    elif ev_status & 0x03:
                        prog_dict['running'] = 'else'

                    if ev_status & 0x10:
                        prog_dict['status'] = 'unknown'
                    elif ev_status & 0x20:
                        prog_dict['status'] = 'true'
                    elif ev_status & 0x30:
                        prog_dict['status'] = 'false'
                    elif ev_status & 0xF0:
                        prog_dict['status'] = 'not_loaded'

            else:
                # TODO : Figure out why we are here...
                pass




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


        if evnt_dat["action"] == "6" or evnt_dat["action"] == "7":
            var_eventInfo = evnt_dat['eventInfo']['var']
            vid = var_eventInfo['var-type'] + ":" + var_eventInfo['var-id']

            # check if the event var exists in out world
            if vid in self._vardict:
                # ADD LOCK ON VAR DATA
                # copy var properties from event

                event_targ = vid

                self._vardict[vid].update(var_eventInfo)
                self._vardict[vid]["val"] = int(self._vardict[vid]["val"])
                self._vardict[vid]["init"] = int(self._vardict[vid]["init"])

            else:
                warn("Event for Unknown Var : {0}".format(vid), IsyE.IsyRuntimeWarning)

    elif control_val == "_2":  # Driver Specific Events
        pass

    elif control_val == "_3":  # Node Change/Updated Event
        if self.debug & 0x40:
            print("Node Change/Updated Event:  {0}".format(evnt_dat["node"]))
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

        if evnt_dat['action'] == 'EN':  # Enable
            if evnt_dat['node'] in self._nodedict:
                self._nodedict[evnt_dat['node']]['enabled'] = evnt_dat['eventInfo']['enabled']

        elif evnt_dat['action'] == 'GN':  # Group Renamed
            if evnt_dat['node'] in self._nodegroups:
                oldname = self._nodegroups[evnt_dat['node']]['name']
                self._nodegroups[evnt_dat['node']]['name'] = evnt_dat['eventInfo']['newName']
                self._groups2addr[evnt_dat['eventInfo']['newName']] = evnt_dat['node']
                del self._groups2addr[oldname]

                if evnt_dat['eventInfo']['newName'] in self._name2id:
                    # warn Dup ID
                    if self._name2id[evnt_dat['eventInfo']['newName']][0] == "group":
                        self._name2id[evnt_dat['eventInfo']['newName']] = ("group", evnt_dat['node'])
                else:
                    self._name2id[evnt_dat['eventInfo']['newName']] = ("group", evnt_dat['node'])
                # Delete old entery if it is 'ours'
                if oldname in self._name2id and self._name2id[oldname][0] == "group":
                    del self._name2id[oldname]

        elif evnt_dat['action'] == 'GR':  # Group Removed/Deleted
            if self.debug & 0x40:
                print("evnt_dat:", evnt_dat)

        elif evnt_dat['action'] == 'GD':  # New Group Added
            if self.debug & 0x40:
                print("evnt_dat:", evnt_dat)

        elif evnt_dat['action'] == 'ND':
            node_id = evnt_dat["node"]
            node_dat = evnt_dat['eventInfo']['node']
            if node_id in self._nodedict:
                self._nodedict[node_id].update(node_dat)
            else:
                self._nodedict[node_id] = node_dat


        #
        # At this time results are undefined for
        # Node class objects that represent a deleted node
        #
        elif evnt_dat['action'] == 'NR':
            node_id = evnt_dat["node"]
            if node_id in self._nodedict:
                node_name = self._nodedict[node_id]["name"]
                if "property" in self._nodedict[node_id]:
                    self._nodedict[node_id]["property"].clear()
                    del self._nodedict[node_id]["property"]
                if self._node2addr and node_name in self._node2addr:
                    del self._node2addr[node_name]
                if self._name2id and node_name in self._name2id:
                    del self._name2id[node_name]

            if node_id in self.nodeCdict:
                del self.nodeCdict[node_id]


        elif evnt_dat['action'] == 'FD':
            if 'folder' in evnt_dat['eventInfo'] and isinstance(evnt_dat['eventInfo']['folder'], dict):
                self._nodefolder[evnt_dat['node']] = evnt_dat['eventInfo']['folder']
                self._folder2addr[evnt_dat['eventInfo']['folder']['name']] = evnt_dat['node']
        elif evnt_dat['action'] == 'FR':
            if evnt_dat['node'] in self._nodefolder:
                if evnt_dat['node'] in self.nodeCdict:
                    # this is tricky if the user has a IsyNodeFolder obj
                    # more has to be done to tell the Obj it's dead
                    del self.nodeCdict[evnt_dat['node']]
                del self._nodefolder[evnt_dat['node']]
        elif evnt_dat['action'] == 'FN':
            if evnt_dat['node'] in self._nodefolder:
                oldname = self._nodefolder[evnt_dat['node']]['name']
                self._nodefolder[evnt_dat['node']]['name'] = evnt_dat['eventInfo']['newName']
                self._folder2addr[evnt_dat['eventInfo']['newName']] = evnt_dat['node']
                del self._folder2addr[oldname]

    elif control_val == "_4":  # System Configuration Updated
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
        if evnt_dat['action'] == '5':
            if 'status' in evnt_dat['eventInfo']:
                self.isy_status['batchmode'] = (evnt_dat['eventInfo']['status'] == "1")
        elif evnt_dat['action'] == '6':
            if 'status' in evnt_dat['eventInfo']:
                self.isy_status['battery_mode_prog_update'] = (evnt_dat['eventInfo']['status'] == "1")

            # status_battery_mode_prog_update

    elif control_val == "_5":  # System Status Updated
        pass
        #
        # node = null
        # action = "0" -> Not Busy
        # action = "1" -> Busy
        # action = "2" -> Idle
        # action = "3" -> Safe Mode
        #

    elif control_val == "_6":  # Internet Access Status
        pass
        #
        # action = "0" -> Disabled
        # action = "1" -> Enabled
        #     node = null
        #     <eventInfo>external URL</eventInfo>
        # action = "2" -> Failed
        #

    elif control_val == "_7":  # Progress Report
        pass

    elif control_val == "_8":  # Security System Event
        pass

    elif control_val == "_9":  # System Alert Event
        pass

    elif control_val == "_10":  # OpenADR and Flex Your Power Events
        pass

    elif control_val == "_11":  # Climate Events
        pass

    elif control_val == "_12":  # AMI/SEP Events
        pass
#           if evnt_dat['action'] == '1':
#               if 'ZBNetwork' in evnt_dat['eventInfo']:
#                   self.zigbee['network'] = evnt_dat['eventInfo']['ZBNetwork']
#           elif evnt_dat['action'] == '10':
#               if 'MeterFormat' in evnt_dat['eventInfo']:
#                   self.zigbee['MeterFormat'] = evnt_dat['eventInfo']['MeterFormat']
#

    elif control_val == "_13":  # External Energy Monitoring Events
        pass

    elif control_val == "_14":  # UPB Linker Events
        pass

    elif control_val == "_15":  # UPB Device Adder State
        pass

    elif control_val == "_16":  # UPB Device Status Events
        pass

    elif control_val == "_17":  # Gas Meter Events
        pass

    elif control_val == "_18":  # Zigbee Events
        pass

    elif control_val == "_19":  # Elk Events
        pass
#           if evnt_dat["action"] == "6":
#               if 'se" in evnt_dat['eventInfo']:
#                   if evnt_dat['eventInfo']['se']['se-type'] == '156':
#                       print("Elk Connection State : ", evnt_dat['eventInfo']['se']['se-val'])
#                   elif evnt_dat['eventInfo']['se']['se-type'] == '157':
#                       print("Elk Enable State : ", evnt_dat['eventInfo']['se']['se-val'])



    elif control_val == "_20":  # Device Linker Events
        pass


    else:
        if self.debug & 0x40:
            print("evnt_dat :", evnt_dat)
            print("Event fall though : '{0}'".format(evnt_dat["node"]))


    if self.callbacks is not None:
        call_targ = None
        if event_targ in self.callbacks:
            call_targ = event_targ
        elif control_val in self.callbacks:
            call_targ = control_val

        if call_targ is not None:
            cb = self.callbacks[call_targ]
            if isinstance(cb[0], collections.Callable):
                try:
                    cb[0](evnt_dat, *cb[1])
                except Exception as e:
                    print("e=", e)
                    print("sys.exc_info()=", sys.exc_info())
                    print("Callback Error:", sys.exc_info()[0])

            else:
                warn("callback for {!s} not callable, deleting callback".format(call_targ),
                     IsyE.IsyRuntimeWarning)
                del self.callbacks[call_targ]

    return

# Do nothing
# (syntax check)
#
if __name__ == "__main__":
    import __main__
    print(__main__.__file__)

#    a1 = [key for key in locals().keys()
#       if isinstance(locals()[key], type(sys)) and not key.startswith('__')]
#    print(a1)

    print("syntax ok")
    exit(0)
