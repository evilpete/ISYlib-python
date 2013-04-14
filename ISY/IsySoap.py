"""
This is accessing the ISY's SOAP interface using the SUDS library 
 
This is written as a convince  

If you are writing a script that primarily uses the the SOAP / SUDs
interface you may be better off using the SUDS library directly  


known methods ( what is avalible varies by release )

    AddDDNSHost(xs:string host, xs:string ip, )
    AddFolder(xs:string id, xs:string name, )
    AddGroup(xs:string id, xs:string name, ns2:NodeTypeFlag flag, )
    AddNode(xs:string id, xs:string name, xs:string type, ns2:NodeOperationsFlag flag, )
    ClearLastError()
    GetCurrentSystemStatus(xs:string SID, )
    GetDDNSHost()
    GetDebugLevel()
    GetISYConfig()
    GetLastError()
    GetNodesConfig()
    GetSMTPConfig()
    GetSceneProfiles(xs:string node, xs:string controller, )
    GetStartupTime()
    GetSystemDateTime()
    GetSystemOptions()
    GetSystemStatus()
    GetVariable(ns2:UDIVariableType type, xs:string id, )
    GetVariables(ns2:UDIVariableType type, )
    InternetAccess(ns2:InternetAccessFlag flag, )
    IsDDNSHostAvail(xs:string host, )
    IsSubscribed(xs:string SID, )
    MoveNode(xs:string node, xs:string group, ns2:LinkModeFlag flag, )
    Query(xs:string node, ns2:NodeTypeFlag flag, )
    Reboot()
    RemoveDDNSHost(xs:string name, xs:string ip, )
    RemoveFolder(xs:string id, )
    RemoveFromGroup(xs:string node, xs:string group, )
    RemoveGroup(xs:string id, )
    RemoveModem()
    RemoveNode(xs:string id, )
    RenameFolder(xs:string id, xs:string name, )
    RenameGroup(xs:string id, xs:string name, )
    RenameNetwork(xs:string name, )
    RenameNode(xs:string id, xs:string name, )
    ReplaceDevice(xs:string node, xs:string NewNode, xs:string firmware, )
    ReplaceModem()
    RestoreDevice(xs:string node, ns2:RestoreDevicesFlag flag, )
    RestoreDevices(ns2:RestoreDevicesFlag flag, )
    SecuritySystemAction(xs:string SecAction, xs:string code, )
    SendHeartbeat()
    SendTestEmail(xs:string id, )
    SetBatchMode(ns2:BatchModeFlag flag, )
    SetBatteryDeviceWriteMode(ns2:BatteryDeviceWriteFlag flag, )
    SetDebugLevel(xs:string option, )
    SetLinkingMode(ns2:LinkModeFlag flag, )
    SetNTPOptions(xs:string NTPHost, xs:boolean NTPEnabled, xs:int NTPInterval, )
    SetNodeEnabled(xs:string node, ns2:SetNodeEnabledFlag flag, )
    SetNodePowerInfo(xs:string node, ns2:DeviceClass deviceClass, xs:unsignedInt wattage, xs:unsignedInt dcPeriod, )
    SetNotificationsOptions(xs:string MailTo, xs:boolean CompactEmail, )
    SetParent(xs:string node, ns2:NodeHierarchyFlag nodeType, xs:string parent, ns2:NodeHierarchyFlag parentType, )
    SetProgramOptions(xs:boolean PCatchUp, xs:int PGracePeriod, ns2:HTMLRoleFlag HTMLRole, )
    SetSMTPConfig(xs:boolean UseDefaultSMTP, xs:string SMTPServer, xs:int SMTPPort, xs:string SMTPUID, xs:string SMTPPWD, xs:string SMTPFrom, xs:int SMTPTimeout, xs:boolean UseTLS, )
    SetSceneProfile(xs:string node, xs:string controller, ns2:ControlType control, xs:string action, )
    SetSystemDateTime(xs:long NTP, xs:int TMZOffset, xs:boolean DST, xs:float Lat, xs:float Long, xs:long Sunrise, xs:long Sunset, xs:boolean IsMilitary, )
    SetUserCredentials(xs:string name, xs:string password, )
    SetVariable(ns2:UDIVariableType type, xs:string id, xs:string val, )
    StartNodesDiscovery(xs:string type, )
    StopNodesDiscovery(ns2:NodeOperationsFlag flag, )
    Subscribe(xs:string reportURL, xs:string duration, xs:string SID, )
    SynchWithNTS()
    UDIService(ns2:ControlType control, xs:string action, xs:string node, ns2:NodeTypeFlag flag, )
    Unsubscribe(xs:string SID, xs:int flag, )
    WriteDeviceUpdates(xs:string node, )

"""

try:
    from suds.client import Client
    heterodox = 0
except ImportError :
    heterodox = 1

import sys

import urllib2 as URL
from urllib2 import URLError, HTTPError

from ISY.IsyExceptionClass import  IsyInvalidCmdError
from ISY.IsyUtilClass import IsyUtil

__ALL_ = [ 'IsySoap', 'IsyInvalidSoapCmdError' ]

# import logging
# logging.basicConfig(level=logging.DEBUG)
 
class IsyInvalidSoapCmdError(IsyInvalidCmdError,AttributeError):
    """General exception for command errors."""
    pass


#
# ToDo : Add heterodox mothods : Hardcoded calls to SOAP methods
#
heterodox_methods = [ "Reboot" ]

class IsySoap(object) :

    def __init__(self, isy) :

	print "IsySoap: __init__"
	self.isy = isy
	self.debug = isy.debug
	self.baseurl = isy.baseurl

	xurl = self.baseurl + '/services.wsdl'
	if self.debug & 0x02 :
	    print("xurl = " + xurl)

	if not heterodox :
	    self.client = Client(xurl, username=isy.userl, password=isy.userp, faults=False)
	else :
	    print "No Suds, using unorthodox method"
	self.opener = isy._opener


    def list_methods(self) :
	print "IsySoap: list_methods"
	if heterodox :
	    return heterodox_methods
	else :
	    return (me.name for me in self.client.wsdl.services[0].ports[0].methods.values())

    def reboot(self) :
	if heterodox :
	    print "call _Reboot"
	    self._reboot()
	else :
	    #self.client.service.Reboot()
	    print "client.service.Reboot"

    def call_method(self, meth_name, *arg):
	print "IsySoap: call_method"

	if heterodox :
	    print "Cant call_method : heterodox"
	    return

	if not isinstance(meth_name, str) or not len(meth_name) :
	    raise IsyInvalidSoapCmdError("Method name missing")

	meth = getattr(self.client.service, meth_name)

	if not meth :
	    raise IsyInvalidSoapCmdError("Method not found: {!s}".format(meth_name))

	res = meth(*arg)
	return res

    def print_all(self) :
	print "IsySoap: print_all"
	if heterodox :
	    print "Cant print_all : heterodox"
	    return

	for method in self.client.wsdl.services[0].ports[0].methods.values():
	    print '%s(%s)' % (method.name, ', '.join('%s: %s' % (part.type, part.name) for part in method.soap.input.body.parts))

    def _reboot(self) :
	print "_reboot"
	return

#    def __getattr__(self, attr):
#	if attr  in  :
#	    return attr_v
#	else :
#	    print "attr =", attr
#	    raise AttributeError, attr

#
# Do nothing
# (syntax check)
#
if __name__ == "__main__":
    import __main__
    print(__main__.__file__)

    print("syntax ok")
    exit(0)
