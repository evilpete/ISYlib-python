#!/usr/local/bin/python2.7
"""
    Proof of concept for monitoring network for setting home automation use

    not ready for prime time of any kind
"""

import time
import signal
import traceback
import argparse
import ISY
from ISY.IsyExceptionClass import IsySoapError
import json

import logging
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)
from scapy.all import *

from threading import Thread, current_thread
import pprint

__author__ = "Peter Shipley"

verbose = 1
verbose_time = 0

conf.verb = 0

iface = "eth0" # eth0 em0

conf_path="/WEB/CONF/scapyarp.jsn"

target_conf = None
old_target_conf= [
    ("10.1.1.104", "60:be:b5:ad:28:2d", "is_home"),
#old    ("10.1.1.77", "f8:f1:b6:22:a5:ab", "is_deb_home"),
#new    ("10.1.1.131", "e4:58:b8:84:b4:f6", "is_deb_home"),
    (None, "e4:58:b8:84:b4:f6", "is_deb_home"),
    ("10.1.1.83", "a8:e3:ee:93:3d:c3", "is_ps3_on"),
    ("10.1.1.93", "6c:ad:f8:18:1c:33", "is_tv_on"),
    ]

myisy = None
isy_var = None

start_time =  float(time.time())

time_away_default = 600
time_away = None
time_sleep = None
time_recheck = None
config_file = None
upload_config = None
validate_config = None

#time_sleep = 60
#time_recheck = 120
#time_away = 300

redirect_io=1

time_var_refresh = None # 960
sniff_timeout = None # 360

mac_targets = {}

time_fmt = "%Y-%m-%d %H:%M:%S"
event_thread  =  None

class mtargets(object):
    def __init__(self, mac=None, ip=None, var=None):

	# Normalize MAC address
        self.mac = ":".join([i.zfill(2) for i in re.split('-|:', mac)]).lower()

        self.ip = ip
	if len(self.ip) < 1:
	    self.ip = None

        if isinstance(var, str):
            self.var = myisy.get_var(var)
        else:
            self.var = var

        self.last_seen = 0
        self.is_home = -1
        self.set_var_time = 0
        if mac is None:
            self.mac = mac_from_ip(self.ip)
        if verbose:
            print "mtargets init: mac={:<18} ip={:<15} var={:<12}".format(self.mac, self.ip, self.var.name)


    def set_var(self, state):

        time_now = time.time()
        strtm = time.strftime(time_fmt, time.localtime(time_now))

        if self.is_home == state and (time_now - self.set_var_time) < (time_var_refresh / 2):
            if verbose > 1:
                print "{}\tset_var: {} pass val={} state={}\t{}\n".format(
                strtm, current_thread().name, self.var.value, state, self.var.name),
            sys.stdout.flush()
            return

            if verbose > 1:
                print "{}\tset_var: {} {:.2f} < {}\n".format(
                    strtm, current_thread().name,
                    (time_now - self.set_var_time), (time_var_refresh / 2)),

        else:
            if verbose > 1:
                print "{}\tset_var: {} {:.2f} > {}\n".format(
                    strtm, current_thread().name,
                    (time_now - self.set_var_time), (time_var_refresh / 2)),

        sys.stdout.flush()

        if verbose:
            print "{}\tset_var: {:<12} {}/{} -> {}: {}\n".format(
                strtm, current_thread().name,
                self.is_home, self.var.value, state, self.var.name),
        #sys.stdout.flush()


        try:
            self.var.value = state
        except Exception, x:
            if verbose:
                print "var set value: ", x
            return

        self.set_var_time = float(time_now)
        self.is_home = state

    def __repr__(self):
        return "<{} [{}] at 0x{:x}>" % (self.__class__.__name__, self.mac, id(self))


#
# time_sleep  ping_loop sleep time
# time_recheck    = time since last packet before using arping
# time_away       = amount of time before declaring device gone
# time_var_refresh = amount of time before polling IST var to make sure things are in sync
# sniff_timeout    = timeout for capy.sniff, mostly used for house cleaning
#


# pcap_filter="arp and ether src 60:be:b5:ad:28:2d"
# print time.asctime(time.localtime())

def Exit_gracefully(cursignal, frame):
    """
        Signal handler for clean exits
    """
    print "Exiting in a Graceful way sig=", cursignal, frame
    traceback.print_exc(file=sys.stdout)
    #for c in mac_targets.values():
    #    try:
    #        c.set_var(0)
    #    except Exception, x:
    #        print "Exception:", x
    sys.stdout.flush()
    sys.stderr.flush()
    sys.exit(0)

def refresh_var():
    global mac_targets

    strtm = time.strftime(time_fmt, time.localtime())
    time_now = time.time() # int(time.time())

    if verbose:
        print strtm, "\trefresh_var", current_thread().name, "pid=", os.getppid()

    for c in mac_targets.values():


        if (time_now - c.set_var_time) >= time_var_refresh:

            if c.is_home == -1:
                continue

            if verbose:
                print "{}\trefresh_var: mac={:<18} ip={:<10} var={:<8} = {:<2} is_home={:<2}".format(
                    strtm, c.mac, c.ip, c.var.name, c.var.value, c.is_home)
            try:
                c.var.refresh()
            except Exception, x:
                print "var.refresh: ", x
                continue

	    if verbose:
		if c.var.value != c.is_home:
                    print strtm, "\n>>>>Assert", " is_home = ", c.is_home, "isy_var.value =", c.var.value, "\n"
		    sys.stdout.flush()

	    c.var.value == c.is_home
	    c.set_var_time = time_now
	    # c.set_var(c.is_home)


def mac_from_ip(ip):
    t_mac = None
    ans, unans = icmp_ping(ip)
    if ans:
        (so, resp) = ans[0]
        t_mac = resp[Ether].src
        if verbose:
            print "mac_from_ip {0} -> {1}".format(ip, t_mac)
    return t_mac


def pcap_callback(pkt):

    eaddr = None
    ipaddr = None
    pktinfo = None

    t = time.strftime(time_fmt, time.localtime())
    if ARP in pkt and pkt[ARP].op in (1, 2): #who-has or is-at
        eaddr = pkt[ARP].hwsrc
        ipaddr = pkt[ARP].psrc
#        if target_ip is None:
#            target_ip = pkt[ARP].pdst
#            if verbose:
#                print "arp_mon set target_ip = ", target_ip
        try:
            pktinfo =  pkt.sprintf("{0}\tARP %ARP.hwsrc% %ARP.psrc% %ARP.op% %ARP.pdst%".format(t))
        except Exception, x:
            print "Scapy_Exception ARP : ", x
            pktinfo = None


#    elif TCP in pkt:
#        eaddr = pkt[Ether].src
#        pktinfo = pkt.sprintf("{0}\tTCP %Ether.src% %Ether.dst% %IP.src%:%TCP.sport% %IP.dst%:%TCP.dport%".format(t))

#    elif UDP in pkt:
#        eaddr = pkt[Ether].src
#        pktinfo = pkt.sprintf("{0}\t%IP.proto% %Ether.src% %Ether.dst% %IP.src%:%UDP.sport% %IP.dst%:%UDP.dport%".format(t))
#
    elif IP in pkt:
        eaddr = pkt[Ether].src
        ipaddr = pkt[IP].src
        try:
            pktinfo = pkt.sprintf("{0}\tIP %IP.proto% %Ether.src% %Ether.dst% %IP.src% %IP.dst%".format(t))
        except Exception, x:
            print "Scapy_Exception IP : ", x
            pktinfo = None

    elif Ether in pkt:
        eaddr = pkt[Ether].src
        try:
            pktinfo = pkt.sprintf("{0}\tEther %Ether.src% %Ether.dst% ".format(t))
        except Exception, x:
            print "Scapy_Exception Ether : ", x
            pktinfo = None

    elif Dot3 in pkt:
        eaddr = pkt[Dot3].src
        try:
            pktinfo = pkt.sprintf("{0}\tDot3 %Dot3.src% %Dot3.dst% ".format(t))
        except Exception, x:
            print "Scapy_Exception Dot3 : ", x
            print "pkt", pkt, "\n"
            pkt.show()
            pktinfo = None

    else:
        if verbose:
            # print ">> pkt __dict__", pkt.__dict__
            print "pkt", pkt
            print "dir", dir(pkt)
            print "pkt.name", pkt.name
            pkt.show()
            return "???"
        else:
            return None


    if eaddr in mac_targets:
        # print t, "\tmac_{0}".format(eaddr), mac_targets[eaddr].ip
        ti = int(time.time())
        prev_seen = mac_targets[eaddr].last_seen
        mac_targets[eaddr].last_seen = ti
        time_since = ti - prev_seen

	# update IP address ( if needed )
	if ipaddr is not None and ipaddr != "0.0.0.0" :
	    if mac_targets[eaddr].ip is None:
		mac_targets[eaddr].ip = ipaddr
		if verbose:
		    print  t, "\tset_ipaddr\t{} to {}\t{}".format(mac_targets[eaddr].mac, mac_targets[eaddr].ip, mac_targets[eaddr].var.name)
	    elif mac_targets[eaddr].ip != mac_targets[eaddr].ip:
		if verbose:
		    print  t, "\tset_ipaddr\t{} changed {} -> {}\t{}".format(
			mac_targets[eaddr].mac, mac_targets[eaddr].ip, ipaddr, mac_targets[eaddr].var.name)
		mac_targets[eaddr].ip = ipaddr


        # dont react to *every* packet in a row
        if  (time_since > (time_recheck / 3)) or (mac_targets[eaddr].is_home < 1):
            # print time.strftime(time_fmt, time.localtime()), t, pkt.time, (pkt.time - t)
            mac_targets[eaddr].set_var(1)
        else:
            if verbose > 1:
                print  "{}\tpcap_callback: time_since={} > {}".format(t, time_since, (time_recheck / 10))
                print  "{}\tpcap_callback: time_since = {} = {} - {}".format(t, time_since,
                    prev_seen, ti)


    sys.stdout.flush()

    if verbose > 3:
        return pktinfo
    else:
        return None


def icmp_ping(ip, mac=None):

    if ip is None:
        return (None, None)

    if mac is None:
        ans, unans = srp(Ether()/IP(dst=ip)/ICMP(), timeout=2)
    else:
        ans, unans = srp(Ether(dst=mac)/IP(dst=ip)/ICMP(), timeout=2)

    if verbose:
        print "icmp_ping: ", ip, " ans = ", len(ans), ", unans = ", len(unans)
        sys.stdout.flush()
#    if target_mac is None and ans:
#        (so, re) = ans[0]
#        target_mac = re[Ether].src
#        if verbose:
#            print "icmp_ping set target_mac = ", target_mac
    return ans, unans

def arp_ping(ip):
    if ip is None:
        return (None, None)
    ans, unans = srp(Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=ip),
              timeout=2, retry=2)
    if verbose > 1:
        print "arp_ping: ", ip, " ans = ", len(ans), ", unans = ", len(unans)
        sys.stdout.flush()
#    if target_mac is None and ans:
#        (so, re) = ans[0]
#        target_mac = re[Ether].src
#        if verbose:
#            print "arp_ping set target_mac = ", target_mac
    return (ans, unans)

#
# Send arp and/or pings if we have not heard from the target recently
#
def ping_loop():
    global mac_targets

    if verbose:
        print time.strftime(time_fmt, time.localtime()), "\tping_loop init", current_thread().name

    for c in mac_targets.values():

	if c.ip is None:
	    #icmp_a, icmp_u = icmp_ping("255.255.255.255", c.mac)
	    continue

        icmp_a=None

        # icmp_a, icmp_u = icmp_ping(c.ip)
	arp_a, arp_u = arp_ping(c.ip)
        # arping(c.ip)

        if arp_a or icmp_a:
            c.set_var(1)
            c.last_seen = int(time.time())

    if verbose:
        print time.strftime(time_fmt, time.localtime()), "\tping_loop start"

    while True:


        if verbose:
            print time.strftime(time_fmt, time.localtime()), "\tping_loop sleep start"

        sys.stdout.flush()
        time.sleep(time_sleep)

        if verbose:
            print time.strftime(time_fmt, time.localtime()), "\tping_loop sleep complete"

        for c in mac_targets.values():

            time_now = float(time.time()) # int(time.time())
            time_since = time_now - c.last_seen

            strtm = time.strftime(time_fmt, time.localtime())

            if time_since >= time_recheck:

                if verbose > 2:
                    print strtm, "\tping_loop: {} time_since >= time_recheck".format(c.mac), c.var.name
                    # print "arp_pinging"

		if c.ip is not None:
		    a, u = arp_ping(c.ip)

		    #if len(a) < 1:
		    #    a, u = icmp_ping(c.ip, c.mac)

		    if len(a):
			c.set_var(1)
			c.last_seen = int(time.time())
			if verbose:
			    print strtm, "\tcontinue seen", c.mac, c.var.name
			    # last_seen, time.strftime(time_fmt, time.localtime(c.last_seen)), c.var.name
			continue

                # wait to see if sniffer sees it
                # time.sleep(5)
                # strtm = time.strftime(time_fmt, time.localtime())
                # time_since = int(time.time()) - c.last_seen

            if time_since >= time_away:
                if verbose and c.ip is None:
                    #print "{}\tping_loop: time_since >= time_away, last_seen = {}".format(
                    #    strtm,
                    #    time.strftime(time_fmt, time.localtime(c.last_seen)))
		    print "\t", c.mac, c.ip, c.var.name

                if verbose and c.is_home == 1:
                    print "{}\tping_loop: time_since = {:.2f} sec = {:.2f} min {:.2f} sec".format(
                        strtm,
                        time_since,
                        *divmod(time_since, 60))

		# set inital last_seen to start file of prog
		if c.is_home == -1 :
		    c.last_seen = int(start_time)

		# dont set var for *every* timeout in a row, unless needed
		if c.is_home or (time_now - c.set_var_time) > (time_away * 2):
		    c.set_var(0)
		else:
		    print "\tpass", c.var.name


def do_it():
    global event_thread
    global myisy
    global target_conf
    global time_var_refresh
    global verbose_time

    for tp in target_conf:
        # print "tp=", tp

	try:
	    isy_v = myisy.get_var(tp[2])
	except Exception, x:
	    print >> sys.stderr, "Bad ISY var:", tp, x
	    continue

	# check that macaddr is given
        if tp[1] is not None:
	    try :
		mac_targets[tp[1]] = mtargets(mac=tp[1], ip=tp[0], var=isy_v)
	    except Exception, x:
		print >> sys.stderr, "Bad target:", tp, isy_v, x

        else:
	    try :
		mt = mtargets(mac=tp[1], ip=tp[0], var=isy_v)
		if mt.mac is not None :
		    mac_targets[mt.mac] = mt
		else :
		    print >> sys.stderr, "unknown mac :", tp, isy_v
		    del(mt)
	    except Exception, x:
		print >> sys.stderr, "Bad target (mac):", tp, isy_v, x


    if verbose:
        # print "Target Macs", " ".join(mac_targets.keys())
        for c in mac_targets.values():
            # print "c=", c
            print "isy_var = {:<4}: {:<19}{:<5}\t{:<5}\t{:}".format(
                c.var.id, c.var.name, c.var.value, c.var.init, c.var.ts)

    signal.signal(signal.SIGINT, Exit_gracefully)
    signal.signal(signal.SIGHUP, Exit_gracefully)
    signal.signal(signal.SIGTERM, Exit_gracefully)

    # assert(target_mac is not None)

    pcap_filter = "ether src {0}".format(" or ".join(mac_targets.keys()))

    if verbose:
        print "pcap_filter=", pcap_filter


    event_thread = Thread(target=ping_loop, name="ping_looper")
    event_thread.daemon = True
    event_thread.start()
    if verbose:
        print time.strftime(time_fmt, time.localtime()), "\tdo_it() event_thread:", event_thread.name, current_thread().name
        # print time.strftime(time_fmt, time.localtime()), "\t", current_thread().name, "sniff loop"

        print time.strftime(time_fmt, time.localtime()), "pre sleep"

    time.sleep(15)

    if verbose:
        print time.strftime(time_fmt, time.localtime()), "post sleep"


    while(True):
        # tcpdump -i em0 -v -v ether src 60:be:b5:ad:28:2d
        sniff(prn=pcap_callback, iface=iface, filter=pcap_filter, store=0, timeout=sniff_timeout)
        # time_now = int(time.time())

        if verbose:
            print time.strftime(time_fmt, time.localtime()), "\tsniff loop timeout"

        if not event_thread.is_alive():
            print time.strftime(time_fmt, time.localtime()), "\tdaemon thread died", event_thread
            break

	if verbose:
	    if verbose_time < int(time.time()):
		verbose_time = int(time.time()) + ( time_var_refresh * 4 )
		for c in mac_targets.values():
		    # print "c=", c
		    print time.strftime(time_fmt, time.localtime()), "\tmac={:<18} ip={:<15} var={:<12} {} = {}".format(c.mac, c.ip, c.var.name, c.var.value, c.is_home)

        refresh_var()

        sys.stdout.flush()

#target_ip = None #target_conf[0][0]
#target_mac = None #target_conf[0][1]
#target_var = None #target_conf[0][2]

def parse_args():
#    global target_mac
#    global target_ip
#    global target_var
    global iface
    global upload_conf
    global validate_config

    global time_sleep
    global time_recheck
    global time_away

    global time_var_refresh
    global sniff_timeout
    global redirect_io
    global config_file
    global upload_config

    parser = argparse.ArgumentParser()

    parser.add_argument("-c", "--config", dest="config",
                        help="load config from file")

    parser.add_argument("--upload", dest="upload_config",
                        action='store_true',
                        help="store/upload current config to ISY")

    parser.add_argument("-r", "--redirect-io", dest="redirect_io",
                        action='store_true',
                        # default=redirect_io,
                        help="Redirect_IO for file")

    parser.add_argument("--time-sleep", dest="time_sleep",
                        type=int,
                        help="pause time for ping_loop")

    parser.add_argument("--time-recheck", dest="time_recheck",
                        type=int,
                        help="wait time before arpping")

    parser.add_argument("--time-away", dest="time_away",
                        type=int,
                        help="away timeout")

    parser.add_argument("--var-refresh", dest="var_refresh",
                        type=int,
                        help="ISY var refresh time")

#    parser.add_argument("-m", "--mac", dest="target_mac",
#                        default="60:be:b5:ad:28:2d",
#                        help="Target Mac")
#
#    parser.add_argument("-a", "--addr", dest="target_ip",
#                        default="10.1.1.104",
#                        help="Target IP Addr")
#
#    parser.add_argument("-v", "--var", dest="target_var",
#                        default=-1,
#                        help="Target ISY Var")
#

    parser.add_argument("-i", "--interface", dest="iface",
                        default=None,
                        help="Network Interface")

    args, unknown_args = parser.parse_known_args()


#    if args.target_ip:
#        target_ip = args.target_ip
#
#    if args.target_mac:
#        target_mac = args.target_mac
#
#    if args.target_var:
#        target_var = args.target_var

    if args.upload_config:
        upload_config = args.upload_config

    if args.config:
        config_file = args.config

    if args.iface:
        iface = args.iface

    if args.redirect_io:
        redirect_io = args.redirect_io

    if args.time_away:
        time_away = args.time_away

    if args.time_sleep:
        time_sleep = args.time_sleep

    if args.time_recheck:
        time_recheck = args.time_recheck

    if args.var_refresh:
        time_var_refresh = args.var_refresh


    if upload_config and config_file is None:
        print "upload option require have config file option"
        sys.exit()


    #
    # calc other settings
    #
    if time_away is None:
        time_away = time_away_default

    if time_sleep is None:
        time_sleep = int(time_away/4)

    if time_recheck is None:
        time_recheck = int(time_away/3)

    if time_var_refresh is None:
        time_var_refresh = int(time_away + time_sleep) * 2

    if sniff_timeout is None:
        sniff_timeout = int(time_var_refresh / 2) + 10

    # redirect_io=1

def validate_config(config_dat):

    if config_dat is None:
	raise ValueError("config_data is None")

    if type(config_dat) is str:
	try :
	    dat = json.loads(conf_data)
	except Exception, x:
	    raise ValueError( str(x) )
    elif type(config_dat) is list:
	dat = config_dat

    for tp in dat:
	try:
	    ip = tp[0]
	    if ip is not None and len(ip) > 0:
		socket.inet_aton(ip)

	    mac = tp[1]
	    a  = re.split('-|:', mac)
	    if len(a) != 6 :
		raise ValueError( "invalid mac" )
	    if sum(map(len, a)) != 12 :
		raise ValueError( "invalid mac" )


	    isy_v = myisy.get_var(tp[2])

#	except socket.error, x:
#	    raise ValueError( x + "\n" + str(tp) )
	except Exception, x:
	    raise ValueError( str(x) + "\n" + str(tp) )

    return True

def upload_conf(config_file):
    """
	    reads config file
	    validates data
	    uploads to ISY
    """

    conf_data = None
    print "Config file = {}".format(config_file)
    with open(config_file) as confd:
	try :
	    conf_data = confd.read()
	    target_conf = json.loads(conf_data)
	except Exception, x:
	    print "json error: ", x
	    print conf_data
	    exit(1)

    try :
	validate_config(target_conf) 
    except Exception, x:
	print "Config Error"
	print x
	exit(1)
    else :
	if verbose :
	    print "Config Valid"

    try :
	r = myisy._sendfile(data=conf_data, filename=conf_path)
    except IsySoapError, se :
	if se.code() == 403 :
	    print "Error uploading {0} : Forbidden ( code=403 )".format(z.filename)

	raise

    else :
	print "Uploaded filename:", conf_path
	print "Uploaded data:\n", conf_data


def init():
    global target_conf
    global validate_config


    if redirect_io or not sys.stdout.isatty() :
        if os.path.isfile('/var/tmp/is_home_stdout'):
            os.rename('/var/tmp/is_home_stdout', '/var/tmp/is_home_stdout-prev')
        sys.stdout = open('/var/tmp/is_home_stdout', 'w+', 0)
        if os.path.isfile('/var/tmp/is_home_stderr'):
            os.rename('/var/tmp/is_home_stderr', '/var/tmp/is_home_stderr-prev')
        sys.stderr = open('/var/tmp/is_home_stderr', 'w+', 0)

    if verbose:
        print "Starting: {}\tpid={}".format(time.strftime(time_fmt, time.localtime()), os.getppid())
        print "time_sleep=\t{:>2}:{:0<2}".format( *divmod(time_sleep, 60))
        print "time_recheck=\t{:>2}:{:0<2}".format( *divmod(time_recheck, 60))
        print "time_away=\t{:>2}:{:0<2}".format( *divmod(time_away, 60))
        print "var_refresh=\t{:>2}:{:0<2}".format( *divmod(time_var_refresh, 60))
        print "sniff_timeout=\t{:>2}:{:0<2}".format( *divmod(sniff_timeout, 60))
        print "config_file", config_file



    try :
	if config_file is not None :
	    print "Config file = {}".format(config_file)
	    with open(config_file) as confd:
		conf_data = confd.read()
	else :
	    conf_data = myisy.soapcomm("GetSysConf", name=conf_path)
	    if verbose :
		print "Downloaded config_file:", conf_path
    except ValueError, ve:
	print "Load Error :", ve
	print conf_data
	raise
    except IsySoapError, se:
	if conf_path.startswith('/WEB/CONF/'):
	    print "Downloaded dat:", conf_data
	    print "Config file not found of ISY: path={}".format(conf_path)
	    print "Not IsySoapError :", se
	    raise
	else:
	    print "IsySoapError :", se
	    raise

    if verbose:
	print conf_data

    target_conf = json.loads(conf_data)

    return


if __name__ == '__main__':

    parse_args()

    myisy = ISY.Isy(parsearg=1, faststart=1) # debug=0x80

    if upload_config is not None:
	upload_conf(config_file)
	exit(0)


    init()

    #conf.verb = verbose
    do_it()
    exit(0)

