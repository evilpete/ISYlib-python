#####
#
#  Place holder for future module that uses SOAP instead of Rest
#
#####
from suds.client import Client
import sys


# import logging
# logging.basicConfig(level=logging.DEBUG)
 

class IsySoap(object) :

    def __init__(self, userl="admin", userp="admin, **kargs) :


	self.addr = get("addr", os.getenv('ISY_ADDR', None))
	self.wsdl = 'http://" + self.addr + "/services.wsdl'

	self.client = Client(self.wsdl, username=userl, password=userp, faults=False)


    def get_methods(self) :
	return self.client.wsdl.services[0].ports[0].methods.values()

    def print_all(self) :
	for method in self.client.wsdl.services[0].ports[0].methods.values():
	    print '%s(%s)' % (method.name, ', '.join('%s: %s' % (part.type, part.name) for part in method.soap.input.body.parts))
    #

#    def __getattr__(self, attr):
#	if attr  in  :
#	    return attr_v
#	else :
#	    print "attr =", attr
#	    raise AttributeError, attr

#print type( client.service )
# print client
 
#result = client.service.GetNodesConfig()
#print result

# Subscribe(xs:string reportURL, xs:string duration, xs:string SID, )

#result = client.service.Subscribe("http://10.1.1.65:9001/", "infinite")
#print result

#uuid=sys.argv[1]

#result = client.service.Unsubscribe(uuid, "")
#print result


# GetSystemDateTime(None: GetSystemTime)
# GetLastError(None: GetLastError)
# GetSMTPConfig(None: GetSMTPConfig)
# SetSystemDateTime(None: SetSystemTime)
# RestoreDevice(None: RestoreDeviceFromNode)
# IsSubscribed(None: IsSubscribed)
# RemoveDDNSHost(None: RemoveDDNSHost)
# GetVariable(None: GetVariable)
# RemoveGroup(None: RemoveGroup)
# SetNTPOptions(None: SetNTPOptions)
# GetSceneProfiles(None: GetSceneProfiles)
# WriteDeviceUpdates(None: WriteDeviceUpdates)
# SetProgramOptions(None: SetProgramOptions)
# RestoreDevices(None: RestoreDevicesFromNodes)
# ReplaceDevice(None: ReplaceDevice)
# StartNodesDiscovery(None: DiscoverNodes)
# RenameNode(None: RenameNode)
# SendTestEmail(None: SendTestEmail)
# GetDebugLevel(None: GetDebugLevel)
# RemoveFromGroup(None: RemoveFromGroup)
# Subscribe(None: Subscribe)
# GetStartupTime(None: GetStartupTime)
# SendHeartbeat(None: SendHeartbeat)
# GetISYConfig(None: GetISYConfig)
# ClearLastError(None: ClearLastError)
# Unsubscribe(None: Unsubscribe)
# SetUserCredentials(None: SetUserCredentials)
# SetSMTPConfig(None: SetSMTPConfig)
# AddDDNSHost(None: AddDDNSHost)
# RenameFolder(None: RenameFolder)
# AddFolder(None: AddFolder)
# StopNodesDiscovery(None: CancelNodesDiscovery)
# RemoveNode(None: RemoveNode)
# RemoveFolder(None: RemoveFolder)
# SetParent(None: SetParent)
# ReplaceModem(None: ReplaceModem)
# Reboot(None: Reboot)
# SetDebugLevel(None: SetDebugLevel)
# UDIService(None: UDIService)
# SetLinkingMode(None: SetDeviceLinkMode)
# SetNodePowerInfo(None: SetNodePowerInfo)
# SetVariable(None: SetVariable)
# RenameGroup(None: RenameGroup)
# RenameNetwork(None: RenameNetwork)
# SetBatteryDeviceWriteMode(None: SetBatteryDeviceWriteMode)
# GetNodesConfig(None: GetNodesConfig)
# SetSceneProfile(None: SetSceneProfile)
# SecuritySystemAction(None: SecuritySystemRequest)
# AddNode(None: AddNode)
# GetSystemOptions(None: GetSystemOptions)
# GetCurrentSystemStatus(None: GetCurrentSystemStatus)
# SetNotificationsOptions(None: SetNotOptions)
# GetVariables(None: GetVariables)
# RemoveModem(None: RemoveModem)
# MoveNode(None: MoveNode)
# GetDDNSHost(None: GetDDNSHost)
# SetNodeEnabled(None: SetNodeEnabled)
# SetBatchMode(None: SetBatchMode)
# AddGroup(None: AddGroup)
# SynchWithNTS(None: SynchWithNTS)
# Query(None: QueryAll)
# GetSystemStatus(None: GetSystemStatus)
# InternetAccess(None: InternetAccess)
# IsDDNSHostAvail(None: IsDDNSHostAvail)
# 
