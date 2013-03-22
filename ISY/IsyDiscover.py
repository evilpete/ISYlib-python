#!/usr/local/bin/python 

#
# THIS IS BAD CODE
# DOES NOT PROPERLY HANDLE XML namespace FOR Upnp
#

import socket
import struct
import sys
import xml.etree.ElementTree as ET
# import base64
import urllib2 as URL

import re
from pprint import pprint
from pprint import pprint


import signal

__all__ = ['isy_discover']

class UpnpLimitExpired(Exception): pass


def isy_discover( **kwargs ):

    class DiscoveryData:
	debug = 0
	timeout = 60
	passive = 0
	count = 1
	upnp_urls = []

    ddata = DiscoveryData()

    ddata.debug = kwargs.get("debug", 0)
    ddata.timeout = kwargs.get("timeout", 60)
    ddata.passive = kwargs.get("passive", 0)
    ddata.count = kwargs.get("count", 1)

    if ddata.debug :
	print "isy_discover :debug=%s\ttimeout=%s\tpassive=%s\tcount=%s\n" % \
	    (ddata.debug, ddata.timeout, ddata.passive, ddata.count )

    def isy_discover_timeout(signum, frame):
	print "isy_discover_timeout CALL"
	raise UpnpLimitExpired, "Timed Out"

    def isy_timeout(signum, frame):
	print "isy_timeout CALL"
	print 'Signal handler called with signal', signum

    def isy_upnp( ddata):

	if ddata.debug :
	    print "isy_upnp CalL"

	    print "isy_upnp debug=%s\ttimeout=%s\tpassive=%s\tcount=%s\n" % \
		    (ddata.debug, ddata.timeout, ddata.passive, ddata.count )

	multicast_group = '239.255.255.250'
	multicast_port = 1900
	server_address = ('', multicast_port)


	# Create the socket
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sock.bind(server_address)
	group = socket.inet_aton(multicast_group)
	mreq = struct.pack('4sL', group, socket.INADDR_ANY)
	sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

	if not ddata.passive :
	    probe= "M-SEARCH * HTTP/1.1\r\nHOST:239.255.255.250:1900\r\n" \
		"MAN:\"ssdp.discover\"\r\nMX:1\r\n"  \
		"ST:urn:udi-com:device:X_Insteon_Lighting_Device:1\r\n\r\n" 

	    #print "sending : ", probe
	    sock.sendto(probe, (multicast_group, multicast_port))


	while  len(ddata.upnp_urls) < ddata.count :

	    if ddata.debug :
		print "while IN"

	    data, address = sock.recvfrom(1024)

	    if ddata.debug :
		print >>sys.stderr, 'received %s bytes from %s' % (len(data), address)
		print >>sys.stderr, data
		print "ddata.upnp_urls = ", ddata.upnp_urls

	    # only ISY devices
	    # if should I look for 
	    # SERVER:UCoS, UPnP/1.0, UDI/1.0
	    if not "X_Insteon_Lighting_" in data :
		continue

	    upnp_packet = data.splitlines() 

	    if "M-SEARCH " in upnp_packet[0] :
		continue

	    # extract LOCATION
	    for l in upnp_packet :
		a = l.split(':', 1)
		if len(a) == 2 :
		    if str(a[0]).upper() == "LOCATION" :
			ddata.upnp_urls.append( str(a[1]).strip() )
			# uniq the list
			ddata.upnp_urls = list(set(ddata.upnp_urls))

	#print "returning ", ddata.upnp_urls


    old_handler = signal.signal(signal.SIGALRM, isy_discover_timeout)

    #isy_upnp(ddata)
    try :
	signal.alarm(ddata.timeout) 
	isy_upnp(ddata)
	signal.alarm(0) 
	signal.signal(signal.SIGALRM, old_handler)
    except UpnpLimitExpired:
	pass
    except :
	print "Unexpected error:", sys.exc_info()[0]
    finally :
	signal.alarm(0) 
	signal.signal(signal.SIGALRM, old_handler)
	if ddata.debug :
	    print "return data.upnp_urls = ", ddata.upnp_urls

    result = {}
    result_tags = ["UDN", "URLBase", "SCPDURL",
		"controlURL", "eventSubURL"]


    for s in ddata.upnp_urls : 
	req = URL.Request(s)
	resp= URL.urlopen(req)
	pagedata = resp.read()
	resp.close()



	# does this even work ??
	# ET.register_namespace("isy", 'urn:schemas-upnp-org:device-1-0')
	#print "_namespace_map = {0}".format(ET._namespace_map)

	# this is a hack to deal with namespace :
	pa = re.sub(r" xmlns=\"urn:schemas-upnp-org:device-1-0\"", "", pagedata)
	# grok the XML from the Upnp discovered server 
	xmlres = ET.fromstring(pa)

	# print "_namespace_map : ",
	# pprint(ET._namespace_map)

	#if hasattr(xmlres, 'tag') :
	#    xmlns = re.search('\{(.*)\}', xmlres.tag).group(1)
	#else :
	#    continue

	#print "xmlns ", xmlns

	isy_res = dict ()

	el = xmlres.find("URLBase")
	if hasattr(el, 'text') :
	    isy_res["URLBase"] = el.text

	el = xmlres.find("device/friendlyName")
	if hasattr(el, 'text') :
	    isy_res["friendlyName"] = el.text

	el = xmlres.find("device/UDN")
	if hasattr(el, 'text') :
	    isy_res["UDN"] = el.text

	for el in xmlres.iter("service") :
	    serv = el.find('serviceType')
	    if hasattr(serv, 'text') and serv.text == "urn:udi-com:service:X_Insteon_Lighting_Service:1" :

		serv = el.find('SCPDURL')
		if hasattr(serv, 'text') :
		    isy_res["SCPDURL"] = serv.text

		serv = el.find('controlURL')
		if hasattr(serv, 'text') :
		    isy_res["controlURL"] = serv.text

		serv = el.find('eventSubURL>')
		if hasattr(serv, 'text') :
		    isy_res["eventSubURL>"] = serv.text

	result[isy_res["UDN"]] = isy_res

    return result




if __name__ == "__main__":
    import __main__
    print __main__.__file__
    print("ISY.py syntax ok")

#    res = isy_discover( count=1, timeout=10, passive=0)
#    for h in res :
#	print "res : ", h
    exit(0)
