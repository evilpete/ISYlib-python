#!/usr/local/bin/python2.7 
__author__ = "Peter Shipley" 


"""
    Proof of concept for monitoring network for setting home automation use

    not ready for prime time of any kind
"""
from scapy.all import *

from threading import Thread
 
import ISY
import time
import socket
import signal

verbose=1
conf.verb=1

import argparse

last_seen = dict()
targets_dict = dict() 

iface="em0" # eth0

myisy = None
target_var="is_home"
isy_var=None
target_ip="10.1.1.104"
target_mac="60:be:b5:ad:28:2d"
#target_mac=None

time_fmt="%Y-%m-%d %H:%M:%S"
event_thread = None


time_sleep=300
time_recheck=600
time_away=900
#time_sleep=60
#time_recheck=120
#time_away=300

is_home=-1

# pcap_filter="arp and ether src 60:be:b5:ad:28:2d"
# print time.asctime( time.localtime())

def Exit_gracefully(signal, frame):
    print "Exiting in a Graceful way"
    is_home=-1	# assert not home
    set_home(False)
    sys.exit(0)

def set_home(state) :
    global is_home
    global isy_var

    if state == is_home :
	return

    is_home = state

    if is_home :
	isy_var.value = 1
    else :
	isy_var.value = 0

    print "\n>>>>", time.strftime(time_fmt, time.localtime()), " is_home = ", is_home, "\n"



def arp_monitor_callback(pkt):
    global target_ip
    global target_mac
    global last_seen

    eaddr = None

    t = time.strftime(time_fmt, time.localtime())
    if ARP in pkt and pkt[ARP].op in (1,2): #who-has or is-at
	eaddr = pkt[ARP].hwsrc
	if target_ip is None :
	    target_ip = pkt[ARP].pdst
	    print "arp_mon set target_ip = ", target_ip
	pktinfo =  pkt.sprintf("{0}\t%ARP.hwsrc% %ARP.psrc% %ARP.op% %ARP.pdst%".format(t))

    elif TCP in pkt :
	eaddr = pkt[Ether].src
	pktinfo = pkt.sprintf("{0}\tTCP %Ether.src% %Ether.dst% %IP.src%:%TCP.sport% %IP.dst%:%TCP.dport%".format(t))
	set_home(True)

    elif UDP in pkt :
	eaddr = pkt[Ether].src
	pktinfo = pkt.sprintf("{0}\t%IP.proto% %Ether.src% %Ether.dst% %IP.src%:%UDP.sport% %IP.dst%:%UDP.dport%".format(t))

    elif IP in pkt :
	eaddr = pkt[Ether].src
	pktinfo = pkt.sprintf("{0}\t%IP.proto% %Ether.src% %Ether.dst% %IP.src% %IP.dst%".format(t))

    elif Ether in pkt :
	eaddr = pkt[Ether].src
	pktinfo = pkt.sprintf("{0}\t%Ether.src% %Ether.dst% ".format(t))
    elif "802.3" in pkt :
	eaddr = pkt[802.3].src
	pktinfo = pkt.sprintf("{0}\t802.3 %802.3.src% %802.3.dst% ".format(t))
    else :
	pkt.show()
	return "???"

    set_home(True)

    prev_seen = last_seen[eaddr] 
    last_seen[eaddr] = int(time.time())
    if verbose :
	time_since = last_seen[eaddr] - prev_seen
	print "Time_since = {0} sec = {1} min {2} sec".format(
	    time_since,
	    *divmod( time_since , 60) )
	    # int(time_since/60),
	    #int(time_since%60)
	    #)

    return pktinfo

def icmp_ping(ip) :
    global target_mac
    if ip is None :
	return (None,None)

    if target_mac is None :
	ans,unans=srp(Ether()/IP(dst=ip)/ICMP(), timeout=2) 
    else :
	ans,unans=srp(Ether(dst=target_mac)/IP(dst=ip)/ICMP(), timeout=2) 

    print "icmp_ping : ", ip, " ans = ", len(ans), ", unans = ", len(unans)
    if target_mac is None and ans :
	(so,re) = ans[0]
	target_mac = re[Ether].src
	print "icmp_ping set target_mac = ", target_mac
    return ans,unans
 
def arp_ping(ip) :
    global target_mac
    if ip is None :
	return (None,None)
    ans,unans = srp(Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=ip),
              timeout=2, retry=2)
    print "arp_ping : ", ip, " ans = ", len(ans), ", unans = ", len(unans)
    if target_mac is None and ans :
	(so,re) = ans[0]
	target_mac = re[Ether].src
	print "arp_ping set target_mac = ", target_mac
    return (ans,unans)

#
# Send arp and/or pings if we have not heard from the target recently 
#
def ping_loop() :
    global target_mac
    global target_ip
    global last_seen

    print "\nping_loop init"

    arp_a, arp_u = arp_ping(target_ip)
    arping(target_ip)

    if len(arp_a) < 1 :
	icmp_a,icmp_u = icmp_ping(target_ip)

    if arp_a or icmp_a :
	set_home(True)
	last_seen[target_mac] = int(time.time())

    print "\nping_loop start"
    while True :

	time.sleep(time_sleep)
	print "sleep complete",

	time_now = int(time.time())
	time_since = time_now - last_seen[target_mac]

	if time_since >= time_recheck :
	    print "arp_pinging",
	    a, u = arp_ping(target_ip)
	    if len(a) < 1 :
		a, u = icmp_ping(target_ip)
	    if len(a) :
		set_home(True)
		last_seen[target_mac] = int(time.time())
		continue

	    time.sleep(5)
	    time_since = time_now - last_seen[target_mac]

	if time_since >= time_away :
	    print "last_seen = {0}".format(
		    time.strftime(time_fmt,
			time.localtime(last_seen[target_mac])))

	    print "time_since = {0} sec = {1} min {2} sec".format(
		    time_since,
		    *divmod( time_since , 60) )
	    set_home(False)


def do_it() :
    global target_mac
    global target_ip
    global last_seen
    global event_thread
    global myisy
    global isy_var

    print "Starting : {0}".format(time.strftime(time_fmt, time.localtime()))

    myisy = ISY.Isy(parsearg=1, faststart=1) # debug=0x80

    if verbose :
	print "time_sleep=", ( time_sleep / 60 )
	print "time_recheck=", ( time_recheck / 60 )
	print "time_away=", ( time_away / 60 )


    isy_var = myisy.get_var(target_var)
    print "isy_var = {:<4} : {:<19}{:<5}\t{:<5}\t{:}".format(
	    isy_var.id, isy_var.name, isy_var.value, isy_var.init, isy_var.ts )

    signal.signal(signal.SIGINT, Exit_gracefully)

    if target_mac is None :
	ans,unans = icmp_ping(target)
	if ans :
	    (so,re) = ans[0]
	    target_mac = re[Ether].src
	    print "target_mac = ", target_mac

    assert( target_mac is not None )

    pcap_filter="ether src {0}".format(target_mac)

    last_seen[target_mac] = 0

    event_thread = Thread(target=ping_loop, name="ping_looper" )
    event_thread.daemon = True
    event_thread.start()

    print "sniff loop"

    time.sleep(1)


    # tcpdump -i em0 -v -v ether src 60:be:b5:ad:28:2d
    sniff(prn=arp_monitor_callback, iface="em0", filter=pcap_filter, store=0)

def parse_args() :
    global target_mac
    global target_ip
    global target_var
    global iface

    parser = argparse.ArgumentParser()

    parser.add_argument("-m", "--mac", dest="target_mac",
			   default="60:be:b5:ad:28:2d",
			   help="Target Mac")

    parser.add_argument("-a", "--addr", dest="target_ip",
			   default="10.1.1.104",
			   help="Target IP Addr")

    parser.add_argument("-v", "--var", dest="target_var",
			   default="is_home",
			   help="Target ISY Var")

    parser.add_argument("-i", "--interface", dest="iface",
			   default=None,
			   help="Network Interface")

    args, unknown_args = parser.parse_known_args()
 
    if args.target_ip :
	target_ip = args.target_ip

    if args.target_mac :
	target_mac = args.target_mac

    if args.target_var :
	target_var = args.target_var

    if args.iface :
	iface = args.iface


if __name__ == '__main__' :
    parse_args()
    do_it()
    exit(0)

