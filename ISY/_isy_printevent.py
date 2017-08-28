"""
This is a subfile for IsyEvent.py

"""

from __future__ import print_function

__author__ = 'Peter Shipley <peter.shipley@gmail.com>'
__copyright__ = "Copyright (C) 2017 Peter Shipley"
__license__ = "BSD"

import time
import sys
from .IsyEventData import EVENT_CTRL, EVENT_CTRL_ACTION


# @staticmethod

def _action_val(a):
    if isinstance(a, str):
        return a
    elif isinstance(a, dict):
        if "#val" in a:
            return a["#val"]
    else:
        return None

def _print_event(*arg):

    ddat = arg[0]
    # mydat = arg[1]
    exml = arg[2]

# Event Dat:
# {'control': 'DOF', 'node': '16 6C D2 7', 'eventInfo': None, 'Event-seqnum': '141', 'action': '0', 'Event-sid': 'uuid:40'}
# <?xml version="1.0"?><Event seqnum="141" sid="uuid:40"><control>DOF</control><action>0</action><node>16 6C D2 7</node><eventInfo></eventInfo></Event>
#
    ti = time.strftime('%X')
    try:
        if "control" not in ddat or ddat["control"] is None:
            return

        control_val = ddat["control"]

        if "action" in ddat and ddat["action"] is not None:
            action_val = _action_val(ddat["action"])
        else:
            action_val = None

        if control_val in EVENT_CTRL_ACTION and action_val:
            action_str = EVENT_CTRL_ACTION[control_val].get(action_val, action_val)
        else:
            action_str = ""

        node = ddat.get("node", "")
        if node is None:
            node = ""

        control_str = EVENT_CTRL.get(control_val, control_val)

        evi = ""

        if ddat["control"] in ["_0"]:
            pass

        elif ddat["control"] == "ERR":
            print("{!s:<7} {!s:<4}\t{!s:<12}{!s:<12}\t{!s}".format(
                    ti, ddat['Event-seqnum'], "ERR", ddat['node'], action_str))
            return

        #elif ddat["control"] in ["DOF", "DON", "BMAN", "SMAN", "FDUP", "FDSTOP", "FDDOWN"]:
        #    print("{!s:<7} {!s:<4}\t{!s:<12}{!s}\t{!s}".format(
        #            ti, ddat['Event-seqnum'], node, control_str, action_str))
        #    return

        elif ddat["control"] in ["ST", "RR", "OL", "DOF", "DON", "DFOF", "DFON",
                                "BMAN", "SMAN", "FDUP", "FDSTOP", "FDDOWN"]:

            if ddat["eventInfo"] is not None:
                evi = ddat["eventInfo"]
            else:
                evi = ""
            print("{!s:<7} {!s:<4}\t{!s:<12}{!s:<12}\t{!s:<12}\t{!s}".format(
                ti, ddat["Event-seqnum"], node, control_str, action_val, evi))
            return

        elif ddat["control"] == "_1":
            # 'on': None, 'f': '140630 20:55:55', 's': '31', 'r': '140630 20:55:55', 'nr': None, 'id': '1E'}

            #action = EVENT_CTRL_ACTION[ddat["control"]].get(ddat['action'], ddat['action'])
            status = ""

            if action_val == '0':
                st = []

                if 'id' in ddat["eventInfo"]:
                    st.append("id={}".format(ddat["eventInfo"]['id']))

                if 's' in ddat["eventInfo"]:
                    st.append("status={}".format(ddat["eventInfo"]['s']))

                if 'on' in ddat["eventInfo"]:
                    st.append("enabled=true")
                if 'off' in ddat["eventInfo"]:
                    st.append("enabled=false")

                if 'rr' in ddat["eventInfo"]:
                    st.append("runAtStartup=true")
                if 'nr' in ddat["eventInfo"]:
                    st.append("runAtStartup=false")

                if 'r' in ddat["eventInfo"]:
                    st.append("lastRunTime={}".format(ddat["eventInfo"]['r']))

                if 'f' in ddat["eventInfo"]:
                    st.append("lastFinishTime={}".format(ddat["eventInfo"]['f']))

                if 'nsr' in ddat["eventInfo"]:
                    st.append("nextScheduledRunTime={}".format(
                                ddat["eventInfo"]['nsr']))

                status = " ".join(st)

            elif action_val == '6':
                status = "{!s:<12} {!s}:{!s} {!s} {!s}".format(
                    ddat['node'],
                    ddat['eventInfo']['var']['var-type'],
                    ddat['eventInfo']['var']['var-id'],
                    ddat['eventInfo']['var']['val'],
                    ddat['eventInfo']['var']['ts'])

            elif action_val == '7':
                status = "{!s:<12} {!s}:{!s} {!s}".format(
                    ddat['node'],
                    ddat['eventInfo']['var']['var-type'],
                    ddat['eventInfo']['var']['var-id'],
                    ddat['eventInfo']['var']['init'])

            else:
                if isinstance(ddat['eventInfo'], dict):
                    status = " ".join(["{}={}".format(a, b) for a, b in ddat['eventInfo'].items()])
                elif ddat['eventInfo'] is None:
                    status = ""
                else:
                    status = ddat['eventInfo']

            print("{!s:<7} {!s:<4}\t{!s:<12}{!s}\t{!s}\t{!s}".format(
                ti, ddat["Event-seqnum"], node, control_str, action_str, status))

            return

        elif ddat["control"] in [ "_3", "_4", "_5", "_6", "_7", "_8", "_9",
                        "_10", "_11", "_12", "_13", "_14", "_15", "_16", "_19",
                        "_20", "_21", "_22"]:
            d = ddat['eventInfo']
            if isinstance(d, dict):
                status = " ".join(["{}={}".format(a, b) for a, b in d.items()])
            elif d is None:
                status = ""
            else:
                status = eventInfo

            #status = ddat['eventInfo']
            print("{!s:<7} {!s:<4}\t{!s:<12}{!s:<12}\t{!s:<12}\t{!s}".format(
                ti, ddat["Event-seqnum"], node, control_str, action_str, status))

            return


#        elif ddat["control"] == "_11":
#            status = ddat['eventInfo']
#            status = "value={} unit={}".format(
#                        ddat['eventInfo'].get('value', ""),
#                        ddat['eventInfo'].get('unit', ""))
#
#            print("{!s:<7} {!s:<4}\t{!s:<12}\t{!s}\t{!s}\t{!s}".format(
#                ti, ddat["Event-seqnum"], node, control_str, action_str, status))
#            return


        elif ddat["control"] == "_17":
            if action_val == '1':
                status = "total={!s:<12} lastReadTS={!s}".format(
                        ddat['eventInfo'].get('total', ""),
                        ddat['eventInfo'].get('lastReadTS', "")
                    )
            else:
                status = ddat.get('eventInfo', "")

            print("{!s:<7} {!s:<4}\t{!s:<12}{!s:<12}\t{!s:<12}\t{!s}".format(
                ti, ddat["Event-seqnum"], node, control_str, action_str, status))
            return

        elif ddat["control"] == "_18":
            if 'ZBNetwork' in ddat['eventInfo']:
                d = ddat['eventInfo']['ZBNetwork']
                status = " ".join(["{}={}".format(a, b) for a, b in d.items()])
            else:
                status = ddat['eventInfo']
            print("{!s:<7} {!s:<4}\t{!s:<12}{!s:<12}\t{!s:<12}\t{!s}".format(
                ti, ddat["Event-seqnum"], node, control_str, action_str, status))
            return

        elif ddat["control"] == "_23":
            if 'PortalStatus' in ddat['eventInfo']:
                d = ddat['eventInfo']['PortalStatus']
                status = " ".join(["{}={}".format(a, b) for a, b in d.items()])
            else:
                status = ddat['eventInfo']
            print("{!s:<7} {!s:<4}\t{!s:<12}{!s:<12}\t{!s:<12}\t{!s}".format(
                ti, ddat["Event-seqnum"], node, control_str, action_str, status))
            return

        else:
            status = ddat.get('eventInfo', "")
            print("{!s:<7} {!s:<4}\t{!s:<12}{!s:<12}\t{!s:<12}\t{!s}".format(
                ti, ddat["Event-seqnum"], node, control_str, action_str, status))
#           return

#           if node is None:
#               node = ""
#           if action is None:
#               action = ddat.get('action', "")
#           print("{!s:<7} {!s:<4}\t{} : {} : {}\t{!s:<12}".format(
#               ti, ddat['Event-seqnum'],
#               node,
#               control_str,
#               action,
#               ddat.get('eventInfo', "-") ))

            print("Event Dat : \n\t", ddat, "\n\t", exml)


        sys.stdout.flush()
        #print(ddat)
        # print(data)
    except Exception as e:
        print("Unexpected error:", sys.exc_info()[0])
        print(e)
        print(ddat)
        raise
        # print(data)
    finally:
        pass

