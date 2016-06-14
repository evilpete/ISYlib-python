#!/usr/local/bin/python2.7
"""
    Proof of concept for monitoring network for setting home automation use

    not ready for prime time of any kind

    Example Config file (JSON):

    [
      [ "", "74:75:48:7f:18:27", "is_paperwhite" ],
      [ "", "58:55:ca:92:35:9d", "is_jasper_ipod" ],
      [ "", "60:69:44:11:90:d5", "is_suzanne_ipad" ],
#MotoX      [ "10.1.1.104", "60:be:b5:ad:28:2d", "is_home" ],
      [ "10.1.1.105", "64:bc:0c:43:6b:a6", "is_home" ],
      [ "10.1.1.131", "e4:58:b8:84:b4:f6", "is_deb_home" ],
      [ "10.1.1.83", "a8:e3:ee:93:3d:c3", "is_ps3_on" ],
      [ "10.1.1.93", "6c:ad:f8:18:1c:33", "is_tv_on" ],
      [ "", "a4:77:33:58:d0:f6", "is_garage_tv_on" ]
    ]

"""


import select
import sys
import os
import time
import signal
import traceback
import re
import argparse
import json
import logging
from threading import Thread, current_thread

# import scapy.all
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)
from scapy.all import srp, sniff, conf, Ether, ARP, IP, Ether, Dot3, ICMP

import ISY
from ISY.IsyExceptionClass import IsySoapError

__author__ = "Peter Shipley"

verbose = 0
delta = 1
verbose_time = 0

conf.verb = 0

iface = "eth0" # eth0 em0

isy_conf_path = "/WEB/CONF/scapyarp.jsn"

target_list = None

myisy = None
isy_var = None

start_time = float(time.time())

time_away_default = 660
time_away = None
time_sleep = None
time_recheck = None
config_file = None
upload_config = None

redirect_io = 0
log_dir="/var/tmp"
pid_dir="/var/tmp"

time_var_refresh = None
sniff_timeout = None

mac_targets = {}

time_fmt = "%Y-%m-%d %H:%M:%S"
event_thread = None

class Mtargets(object):
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

        self.last_change = 0
        self.last_seen = 0
        self.is_active = -1
        self.set_var_time = 0
        if mac is None:
            self.mac = mac_from_ip(self.ip)
        if verbose:
            print "Mtargets init: mac={:<18} ip={:<15} var={:<12}".format(self.mac, self.ip, self.var.name)


    def set_var(self, state):

        time_now = time.time()
        strtm = time.strftime(time_fmt, time.localtime(time_now))

        if self.is_active == state and (time_now - self.set_var_time) < (time_var_refresh / 2):
            return

        if verbose or (delta and self.is_active != state):
            if self.is_active == -1:
                self.last_seen = int(start_time)
                self.last_change = int(start_time)

            time_since = time_now - self.last_seen
            time_change = time_now - self.last_change

            print "{}\t{} Last seen   {:<18} : {:3.2f} sec = {}".format(
                    strtm, self.mac, self.var.name,
                    time_since, format_sec(time_since))

            print "{}\t{} Last change {:<18} : {:3.2f} sec = {}".format(
                    strtm, self.mac, self.var.name,
                    time_change, format_sec(time_change))

            print "{}\tset_var: {:<12} {}/{} -> {}: {}\n".format(
                strtm, current_thread().name,
                self.is_active, self.var.value, state, self.var.name),
            sys.stdout.flush()

        if self.is_active != state:
            self.last_change = int(time_now)

        self.is_active = state
        try:
            self.var.value = state
        except Exception, x:
            if verbose:
                print "var set value: ", x
                raise
            return
        self.set_var_time = float(time_now)
        sys.stdout.flush()

    def __repr__(self):
        return "<{} [{}] at 0x{:x}>" % (self.__class__.__name__, self.mac, id(self))


#
# time_sleep  ping_loop sleep time
# time_recheck    = time since last packet before using arping
# time_away       = amount of time before declaring device gone
# time_var_refresh = amount of time before polling IST var to make sure things are in sync
# sniff_timeout    = timeout for capy.sniff, mostly used for house cleaning
#


# pcap_filter = "arp and ether src 60:be:b5:ad:28:2d"
# print time.asctime(time.localtime())

def sig_exit_gracefully(cursignal, frame):
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

def sig_ignore(cursignal, frame):
    """
        ignore signal
    """
    print "Ignoring signal :", cursignal, frame
    return

def refresh_var_all():
    """
        loops though used vars and refeshes ISYlib cache
        since ISY object was stared without eventupdates for efficency
    """

    strtm = time.strftime(time_fmt, time.localtime())

    time_now = time.time() # int(time.time())
    if verbose:
        print strtm, "\trefresh_var_all", current_thread().name, "pid=", os.getppid()

    myisy.load_vars()

    for c in mac_targets.values():
        if c.var.value != c.is_active:

            if verbose or delta:
                print strtm, "\t>>>>Assert", " is_active = ", c.is_active, "isy_var.value =", c.var.value, c.var.name

        c.var.value = c.is_active
        # c.var.set_var(c.is_active)
        c.set_var_time = time_now

    sys.stdout.flush()


def mac_from_ip(ip):
    t_mac = None
    ans, _ = icmp_ping(ip)
    if ans:
        (_, resp) = ans[0]
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

        try:
            pktinfo = pkt.sprintf("{0}\tARP %ARP.hwsrc% %ARP.psrc% %ARP.op% %ARP.pdst%".format(t))
        except Exception, x:
            print "Scapy_Exception ARP : ", x
            pktinfo = None


# #    elif TCP in pkt:
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
        time_since = ti - prev_seen

        # update IP address ( if needed )
        #if ipaddr is not None and ipaddr != "0.0.0.0":
        if ipaddr not in [ None, "0.0.0.0", "255.255.255.255" ]:
            if mac_targets[eaddr].ip is None:
                mac_targets[eaddr].ip = ipaddr
                if verbose:
                    print t, "\t A", pkt.summary()
                    # print t, pkt

                    print t, "\tset_ipaddr\t{} to {}\t{}".format(
                        mac_targets[eaddr].mac, mac_targets[eaddr].ip,
                        mac_targets[eaddr].var.name)
            elif mac_targets[eaddr].ip != mac_targets[eaddr].ip:
                if verbose:
                    print t, "\t B", pkt.summary()
                    print t, "\tSet_ipaddr\t{} changed {} -> {}\t{}".format(
                        mac_targets[eaddr].mac, mac_targets[eaddr].ip,
                        ipaddr, mac_targets[eaddr].var.name)
                mac_targets[eaddr].ip = ipaddr


        # dont react to *every* packet in a row
        if (time_since > (time_recheck / 3)) or (mac_targets[eaddr].is_active < 1):
            # print time.strftime(time_fmt, time.localtime()), t, pkt.time, (pkt.time - t)
            if verbose and mac_targets[eaddr].is_active < 1:
                print t, "\t +", pkt.summary()
            mac_targets[eaddr].set_var(1)
        else:
            if verbose > 2:
                print "{}\tpcap_callback: time_since={} > {}".format(t, time_since, (time_recheck / 10))
                print "{}\tpcap_callback: time_since = {} = {} - {}".format(t, time_since,
                    prev_seen, ti)

        mac_targets[eaddr].last_seen = ti
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
    return ans, unans

def format_sec(total_seconds):
    m, s = divmod(total_seconds, 60)
    h, m = divmod(int(m), 60)
    return "{:d}:{:02d}:{:.2f}".format(h, m, s)

def arp_ping(ip):
    if ip is None:
        return (None, None)
    ans, unans = srp(Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=ip),
                     timeout=1.5, retry=2)
    if verbose & 0x02:
        print "arp_ping: ", ip, " ans = ", len(ans), ", unans = ", len(unans)
        sys.stdout.flush()
    return (ans, unans)

#
# Send arp and/or pings if we have not heard from the target recently
#
def ping_loop():
    """
        init stage:
            loops though mac_targets and try to arp ping each one

        loop stage:
            sleep for a while

            loop though mac_targets and try to arp ping each one we have not seen in a while

            check for timeout on non-responsive targets and set their state to 0

    """

    if verbose:
        print time.strftime(time_fmt, time.localtime()), "\tping_loop init", current_thread().name

    for c in mac_targets.values():

        if c.ip is None:
            #icmp_a, icmp_u = icmp_ping("255.255.255.255", c.mac)
            continue

        icmp_a = None

        # icmp_a, icmp_u = icmp_ping(c.ip)
        arp_a, _ = arp_ping(c.ip)
        # arping(c.ip)

        if arp_a or icmp_a:
            c.set_var(1)
            c.last_seen = int(time.time())
            # print time.strftime(time_fmt, time.localtime()), "PRE",
            # arp_a.summary()

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
                if verbose & 0x02:
                    print strtm, "\tping_loop: {} time_since >= time_recheck".format(c.mac), c.var.name
                    # print "arp_pinging"

                if c.ip is not None:
                    a, u = arp_ping(c.ip)

                    #if len(a) < 1:
                    #    a, u = icmp_ping(c.ip, c.mac)

                    if len(a):
                        if verbose: # or (delta and c.var.value < 1):
                            print strtm, "\tseen", c.mac, c.var.name, \
                                "time_since = {:3.2f} sec = {}".format(
                                    time_since,
                                    format_sec(time_since))
                            print strtm, "\t",
                            a.summary()
                            # last_seen, time.strftime(time_fmt, time.localtime(c.last_seen)), c.var.name
                        c.set_var(1)
                        c.last_seen = int(time.time())
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

                if delta and c.is_active == 1:
                    print "{}\t{}  ping_loop: time_since = {:3.2f} sec = {}".format(
                        strtm,
                        c.mac,
                        time_since,
                        format_sec(time_since))

                # set inital last_seen to start file of prog
                if c.is_active == -1:
                    c.last_seen = int(start_time)

                # dont set var for *every* timeout in a row, unless needed
                if c.is_active or (time_now - c.set_var_time) > (time_away * 2):
                    c.set_var(0)
                else:
                    if verbose:
                        print "\tpass", c.var.name, c.var.value


def do_it():
    global event_thread
    global verbose_time

    print "starting"

    # loop through config, skipping errors if possible
    for tp in target_list:
        # print "tp=", tp

        try:
            isy_v = myisy.get_var(tp[2])
        except Exception, x:
            print >> sys.stderr, "Bad ISY var:", tp, x
            continue

        # check that macaddr is given
        if tp[1] is not None:
            try:
                mac_targets[tp[1]] = Mtargets(mac=tp[1], ip=tp[0], var=isy_v)
            except Exception, x:
                print >> sys.stderr, "Bad target:", tp, isy_v, x

        else:
            try:
                mt = Mtargets(mac=tp[1], ip=tp[0], var=isy_v)
                if mt.mac is not None:
                    mac_targets[mt.mac] = mt
                else:
                    print >> sys.stderr, "unknown mac :", tp, isy_v
                    del mt
            except Exception, x:
                print >> sys.stderr, "Bad target (mac):", tp, isy_v, x


    if verbose:
        # print "Target Macs", " ".join(mac_targets.keys())
        for c in mac_targets.values():
            # print "c=", c
            print "isy_var = {:<4}: {:<19}{:<5}\t{:<5}\t{:}".format(
                c.var.id, c.var.name, c.var.value, c.var.init, c.var.ts)


    event_thread = Thread(target=ping_loop, name="ping_looper")
    event_thread.daemon = True
    event_thread.start()
    if verbose:
        print time.strftime(time_fmt, time.localtime()), "\tdo_it() event_thread:", event_thread.name, current_thread().name
        # print time.strftime(time_fmt, time.localtime()), "\t", current_thread().name, "sniff loop"

        print time.strftime(time_fmt, time.localtime()), "pre sleep", current_thread().name

    time.sleep(2 * len(mac_targets))

    if verbose:
        print time.strftime(time_fmt, time.localtime()), "post sleep", current_thread().name

    sys.stdout.flush()


#def sniff_loop():

    verbose_time = int(time.time()) + (time_var_refresh * 4)

    pcap_filter = "ether src {0}".format(" or ".join(mac_targets.keys()))

    if verbose:
        print "pcap_filter=", pcap_filter


    while True:
        # tcpdump -i em0 -v -v ether src 60:be:b5:ad:28:2d
        try:
            sniff(prn=pcap_callback, iface=iface, filter=pcap_filter, store=0, timeout=sniff_timeout)
        except select.error, se:
            #print "scapy sniff : select.error", se
            continue

        # time_now = int(time.time())

        if verbose:
            print time.strftime(time_fmt, time.localtime()), "\tsniff loop timeout"

        if not event_thread.is_alive():
            print time.strftime(time_fmt, time.localtime()), "\tdaemon thread died", event_thread
            break

        if verbose or delta:
            if verbose_time < int(time.time()):
                verbose_time = int(time.time()) + (time_var_refresh * 4)
                print_status_all()

        refresh_var_all()

        sys.stdout.flush()

def sig_print_status(cursignal, frame):
    # print "cursignal=", cursignal, frame
    print_status_all()

def print_status_all():
    # print "Start Time:", time.strftime(time_fmt, time.localtime(start_time))
    for c in mac_targets.values():
        print time.strftime(time_fmt, time.localtime()), \
                "\t{:<18} {:<10} {:<16} {} = {}\t{}".format(
                    c.mac, c.ip, c.var.name, c.var.value, c.is_active,
                time.strftime("%H:%M:%S %Y%m%d", time.localtime(c.last_seen)))
    sys.stdout.flush()
    return 0

def parse_args():
    global iface

    global time_sleep
    global time_recheck
    global time_away

    global time_var_refresh
    global sniff_timeout
    global redirect_io
    global config_file
    global upload_config
    global log_dir

    parser = argparse.ArgumentParser(
	epilog="optional ISY args: -a ISY_ADDR -u ISY_USER -p ISY_PASS"
    )

    parser.add_argument("--logdir", dest="logdir",
                        help="Path to log directory")

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


    parser.add_argument("-i", "--interface", dest="iface",
                        default=None,
                        help="Network Interface")

    args, _ = parser.parse_known_args()


    if args.logdir:
        log_dir = args.logdir

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
        time_sleep = int(time_away/3)

    if time_recheck is None:
        time_recheck = int(time_away/2) - 30

    if time_var_refresh is None:
        time_var_refresh = int(time_away * 3) + 10

    if sniff_timeout is None:
        sniff_timeout = int(time_var_refresh / 2) + 10

    # redirect_io=1

def normalize_mac(eaddr):
    a = re.split('-|:', eaddr)
    if len(a) != 6:
        raise ValueError("invalid mac")
#    if sum(map(len, a)) != 12:
#       raise ValueError("invalid mac")
    mac = ":".join([i.zfill(2) for i in a]).lower()

def validate_config(config_dat):
    import socket

    if config_dat is None:
        raise ValueError("config_data is None")

    if isinstance(config_dat, str):
        try:
            dat = json.loads(conf_data)
        except Exception, x:
            print "json.loads"
            raise ValueError(str(x))
    elif isinstance(config_dat, list):
        dat = config_dat

    for tp in dat:
        try:
            ip = tp[0]
            if ip is not None and len(ip) > 0:
                socket.inet_aton(ip)

            mac = tp[1]
            a = re.split('-|:', mac)
            if len(a) != 6:
		raise ValueError("invalid mac {}".format(mac))
	    for ia in a:
		if int(ia, 16) > 255:
		    raise ValueError("invalid mac {}".format(mac))

            if sum(map(len, a)) != 12:
		raise ValueError("invalid mac {}".format(mac))

            # will raise exception if var does not exist
            myisy.get_var(tp[2])

#       except socket.error, x:
#           raise ValueError(x + "\n" + str(tp))
        except Exception, x:
            raise ValueError(str(x) + "\n" + str(tp))

    return True

def upload_conf(conf_file, isy_path):
    """
            reads config file
            validates data
            uploads to ISY
    """

    conf_data = None
    print "Config file = {}".format(conf_file)
    with open(conf_file) as confd:
        try:
            conf_data = confd.read()
            target_data = json.loads(conf_data)
        except Exception, x:
            print "json error: ", x
            print conf_data
            exit(1)

    try:
        validate_config(target_data)
    except Exception, x:
        print "Config Error"
        print x
        exit(1)
    else:
        if verbose:
            print "Config Valid"

    try:
        myisy._sendfile(data=conf_data, filename=isy_path)
    except IsySoapError, se:
        if se.code() == 403:
            print "Error uploading {0} : Forbidden ( code=403 )".format(isy_path)

        raise

    else:
        print "Uploaded filename:", isy_path
        print "Uploaded data:\n", conf_data


def init():
    global target_list
    global config_file

    signal.signal(signal.SIGINT, sig_exit_gracefully)
    signal.signal(signal.SIGTERM, sig_exit_gracefully)
    signal.signal(signal.SIGUSR1, sig_print_status)

    if redirect_io:

        logpath = log_dir + "/is_home_stdout"
        if os.path.isfile(logpath):
            os.rename(logpath, logpath + '-prev')
#        sys.stdout = open(logpath, 'w+', 0)
        mewout = os.open(logpath, os.O_WRONLY|os.O_CREAT, 0644)
        sys.stdout.flush()
        os.dup2(mewout, 1)
        os.close(mewout)
        # sys.stdout = os.fdopen(1, 'w')

        logpath = log_dir + "/is_home_stderr"
        if os.path.isfile(logpath):
            os.rename(logpath, logpath + '-prev')
#        sys.stderr = open(logpath, 'w+', 0)
        mewerr = os.open(logpath, os.O_WRONLY|os.O_CREAT, 0644)
        sys.stderr.flush()
        os.dup2(mewerr, 2)
        os.close(mewerr)
        # sys.stderr = os.fdopen(2, 'w')

#        sys.stdin = open('/dev/null', 'r')
        devnull = os.open('/dev/null', os.O_RDONLY)
        os.dup2(devnull, 0)
        os.close(devnull)

        logpath = pid_dir + "/scapy-watch.pid"
        with open(logpath, 'w', 0644) as f:
            f.write("{}\n".format(os.getpid()))


#       try:
#           os.setpgrp()
#        except Exception, x:
#           print "Error: os.setpgrp(): {}".format(str(x))


        # signal.signal(signal.SIGHUP, sig_ignore)
        signal.signal(signal.SIGHUP, signal.SIG_IGN)

    if verbose:
        print "Starting: {}\tpid={}".format(time.strftime(time_fmt, time.localtime()), os.getpid())
        print "time_sleep=\t{:>2}:{:0<2}".format( *divmod(time_sleep, 60))
        print "time_recheck=\t{:>2}:{:0<2}".format( *divmod(time_recheck, 60))
        print "time_away=\t{:>2}:{:0<2}".format( *divmod(time_away, 60))
        print "var_refresh=\t{:>2}:{:0<2}".format( *divmod(time_var_refresh, 60))
        print "sniff_timeout=\t{:>2}:{:0<2}".format( *divmod(sniff_timeout, 60))
        print "config_file", config_file
        sys.stdout.flush()


    #
    # if specified:
    #    read config file from command args
    # else
    #    read from ISY device
    #
    try:
        if config_file is not None:
            print "Config file = {}".format(config_file)
            with open(config_file) as confd:
                conf_data = confd.read()
        else:
            conf_data = myisy.soapcomm("GetSysConf", name=isy_conf_path)
            if verbose:
                print "Downloaded config_file:", isy_conf_path
    except ValueError, ve:
        print "Load Error :", ve
        print conf_data
        raise
    except IsySoapError, se:
        if isy_conf_path.startswith('/WEB/CONF/'):
            print "Downloaded dat:", conf_data
            print "Config file not found of ISY: path={}".format(isy_conf_path)
            print "Not IsySoapError :", se
            raise
        else:
            print "IsySoapError :", se
            raise

    if verbose:
        print conf_data

    target_list = json.loads(conf_data)

    return


if __name__ == '__main__':

    parse_args()

    myisy = ISY.Isy(parsearg=1, faststart=1) # debug=0x223)

    if upload_config is not None:
        upload_conf(config_file, isy_conf_path)
        exit(0)

    init()

    do_it()

    exit(0)

