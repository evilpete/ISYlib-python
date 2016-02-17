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

verbose = 1

conf.verb = 0

import argparse

last_seen = dict()
targets_dict = dict()

iface="eth0" # eth0 em0

target_conf= [
    ("10.1.1.104", "60:be:b5:ad:28:2d", "is_home")
    ]

myisy = None
isy_var=None

mac_targets={ }
target_ip=target_conf[0][0]
target_mac=target_conf[0][1]
target_var=target_conf[0][2]

time_fmt="%Y-%m-%d %H:%M:%S"
event_thread = None

class mtargets(object) :
    def __init__(self, mac=None, ip=None, var=None):
        self.mac = mac
        self.ip = ip
        self.var = var
        self.last_seen = 0
        self.is_home = -1
        self.is_home_time = 0

    def set_home(self, state):
        self.var.value = state
        self.is_home = state
        self.is_home_time = int(time.time())

    def get_mac(ip) :
        if target_mac is None :
            ans,unans = icmp_ping(ip)
            if ans :
                (so,re) = ans[0]
                target_mac = re[Ether].src
                if verbose:
                    print "target_mac = ", target_mac
                return(target_mac)
            return(None)

#
# time_sleep  ping_loop sleep time
# time_recheck    = file since last packet before using arping
# time_away       = amount of time before declaring device gone
# time_var_refresh = amount of time before polling IST var to make sure things are in sync
# sniff_timeout    = timeout for capy.sniff, mostly used for house cleaning
#

#time_sleep=300
#time_recheck=600
#time_away=900
time_sleep=60
time_recheck=120
time_away=300
time_var_refresh=900
sniff_timeout=300

is_home=-1
is_home_set_time=None

# pcap_filter="arp and ether src 60:be:b5:ad:28:2d"
# print time.asctime( time.localtime())

def Exit_gracefully(signal, frame):
    print "Exiting in a Graceful way"
    is_home=-1  # assert not home
    set_home(0)
    sys.exit(0)

def refresh_var() :
    global is_home
    global isy_var
    global is_home_set_time
    strtm = time.strftime(time_fmt, time.localtime())

    print "\nrefresh_var", strtm

    isy_var.refresh()

    if isy_var.value != is_home :
        # if verbose:
        print "\n>>>>Assert", strtm, " is_home = ", is_home, "isy_var.value =", isy_var.value, "\n"
        sys.stdout.flush()
        isy_var.value == is_home

    is_home_set_time=int(time.time())


def set_home(state, mac=None) :
    global is_home
    global isy_var
    global is_home_set_time

    if mac is None :
        mac = target_mac


    if state == is_home :
        print "\n>>>> set_home", time.strftime(time_fmt, time.localtime()), "state == is_home = ", is_home, "\n"
        return

    is_home = state
    is_home_set_time=int(time.time())

    isy_var.value = state

    # if verbose:
    print "\n>>>> set_home", time.strftime(time_fmt, time.localtime()), "set is_home = ", is_home, "\n"
    sys.stdout.flush()



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
            if verbose:
                print "arp_mon set target_ip = ", target_ip
        pktinfo =  pkt.sprintf("{0}\t%ARP.hwsrc% %ARP.psrc% %ARP.op% %ARP.pdst%".format(t))

    elif TCP in pkt :
        eaddr = pkt[Ether].src
        pktinfo = pkt.sprintf("{0}\tTCP %Ether.src% %Ether.dst% %IP.src%:%TCP.sport% %IP.dst%:%TCP.dport%".format(t))

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
        if verbose:
            pkt.show()
            return "???"
        else:
            return None

    if eaddr == target_mac :
        set_home(1)
        print "++++ set_home(1) ", eaddr
    else :
        print "---- pass", eaddr

    if verbose :
        prev_seen=0
        if eaddr in last_seen:
            prev_seen = last_seen[eaddr]

    last_seen[eaddr] = int(time.time())
    # print eaddr, "last_seen", last_seen

    if eaddr in mac_targets :
        mac_targets[eaddr].last_seen = int(time.time())
	mac_targets[eaddr].set_home(1)

    if verbose :
        time_since = last_seen[eaddr] - prev_seen
        if verbose:
            print "Time_since = {0} sec = {1} min {2} sec".format(
            time_since,
            *divmod( time_since , 60) )
            # int(time_since/60),
            #int(time_since%60)
            #)

    if verbose :
        return pktinfo
    else:
        return None


def icmp_ping(ip) :
    global target_mac
    if ip is None :
        return (None,None)

    if target_mac is None :
        ans,unans=srp(Ether()/IP(dst=ip)/ICMP(), timeout=2)
    else :
        ans,unans=srp(Ether(dst=target_mac)/IP(dst=ip)/ICMP(), timeout=2)

    if verbose:
        print "icmp_ping : ", ip, " ans = ", len(ans), ", unans = ", len(unans)
    if target_mac is None and ans :
        (so,re) = ans[0]
        target_mac = re[Ether].src
        if verbose:
            print "icmp_ping set target_mac = ", target_mac
    return ans,unans

def arp_ping(ip) :
    global target_mac
    if ip is None :
        return (None,None)
    ans,unans = srp(Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=ip),
              timeout=2, retry=2)
    if verbose:
        print "arp_ping : ", ip, " ans = ", len(ans), ", unans = ", len(unans)
    if target_mac is None and ans :
        (so,re) = ans[0]
        target_mac = re[Ether].src
        if verbose:
            print "arp_ping set target_mac = ", target_mac
    return (ans,unans)

#
# Send arp and/or pings if we have not heard from the target recently
#
def ping_loop() :
    global mac_targes
    global target_mac
    global target_ip
    global last_seen
    global is_home_set_time

    if verbose:
        print "\nping_loop init"


    arp_a, arp_u = arp_ping(target_ip)
    arping(target_ip)

    if len(arp_a) < 1 :
        icmp_a,icmp_u = icmp_ping(target_ip)

    if arp_a or icmp_a :
        set_home(1)
        last_seen[target_mac] = int(time.time())

    if verbose:
        print "\nping_loop start"
    while True :


        if verbose:
            print "sleep start"
        sys.stdout.flush()
        time.sleep(time_sleep)

        time_now = int(time.time())

        if verbose:
            print "sleep complete", time_now

#       if (time_now - is_home_set_time) >= time_var_refresh :
#           refresh_var()

        time_since = time_now - last_seen[target_mac]

        if time_since >= time_recheck :
            if verbose:
                print "time_since >= time_recheck"
                print "arp_pinging",
            a, u = arp_ping(target_ip)
            if len(a) < 1 :
                a, u = icmp_ping(target_ip)
            if len(a) :
                set_home(1)
                last_seen[target_mac] = time_now
                print "continue 1", "last_seen", target_mac, last_seen[target_mac]
                continue

            time.sleep(5)
            time_since = time_now - last_seen[target_mac]

        if time_since >= time_away :
            if verbose:
                print "time_since >= time_away"
                print "last_seen = {0}".format(
                    time.strftime(time_fmt,
                        time.localtime(last_seen[target_mac])))

            if verbose:
                print "time_since = {0} sec = {1} min {2} sec".format(
                    time_since,
                    *divmod( time_since , 60) )
            set_home(0)


def do_it() :
    global target_mac
    global target_ip
    global last_seen
    global event_thread
    global myisy
    global isy_var
    global is_home_set_time

    if verbose:
        print "Starting : {0}".format(time.strftime(time_fmt, time.localtime()))
        print "Target Mac", target_mac

    myisy = ISY.Isy(parsearg=1, faststart=1) # debug=0x80

    if verbose :
        print "time_sleep=", ( time_sleep / 60 )
        print "time_recheck=", ( time_recheck / 60 )
        print "time_away=", ( time_away / 60 )


    isy_var = myisy.get_var(target_var)

    for tp in target_conf :
        last_seen[ tp[1] ] = 0

        mac_targets[ tp[1] ] = mtargets(mac=tp[1], ip=tp[0], var=isy_var )


    if verbose:
        print "isy_var = {:<4} : {:<19}{:<5}\t{:<5}\t{:}".format(
            isy_var.id, isy_var.name, isy_var.value, isy_var.init, isy_var.ts )

    signal.signal(signal.SIGINT, Exit_gracefully)

    if target_mac is None :
        ans,unans = icmp_ping(target)
        if ans :
            (so,re) = ans[0]
            target_mac = re[Ether].src
            if verbose:
                print "target_mac = ", target_mac

    assert( target_mac is not None )

    pcap_filter="ether src {0}".format(target_mac)

    print "pcap_filter=", pcap_filter

    last_seen[target_mac] = 0

    event_thread = Thread(target=ping_loop, name="ping_looper" )
    event_thread.daemon = True
    event_thread.start()

    if verbose:
        print "sniff loop"

    time.sleep(1)


    while(True) :
        # tcpdump -i em0 -v -v ether src 60:be:b5:ad:28:2d
        sniff(prn=arp_monitor_callback, iface=iface, filter=pcap_filter, store=0, timeout=sniff_timeout)
        time_now = int(time.time())

        if verbose:
            print "sniff loop timeout", time_now
            print "len last_seen", len(last_seen)

        if not event_thread.is_alive() :
            print "daemon thread died", event_thread
            break

        if (time_now - is_home_set_time) >= time_var_refresh :
            refresh_var()

        sys.stdout.flush()

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

redirect_io=1

if __name__ == '__main__' :
    if redirect_io or not sys.stdout.isatty() :
        sys.stdout = open('/var/tmp/is_home_stdout', 'w+', 0)
        sys.stderr = open('/var/tmp/is_home_stderr', 'w+', 0)

    parse_args()
    #conf.verb = verbose
    do_it()
    exit(0)

