

:Author: Peter Shipley
:Version: 
:Copyright:

This is a Work in progress

Simple Python lib for the ISY home automation netapp



see also : http://www.universal-devices.com/residential/
	   http://wiki.universal-devices.com/index.php?title=Main_Page

NOTE: This Libaray is not written my or supported by universal devices


-----

to use set the following env vars

ISY_ADDR to the IP address of your ISY device
ISY_AUTH to your loging and password

eg:

    export ISY_AUTH=admin:mypasswd
    export ISY_ADDR=192.168.1.2

Files:

    ISY/*		- ISY Python lib
    bin/isy_find.py	- Upnp probe for devices on your network
    bin/isy_list.py	- List registered devices
    bin/isy_log.py	- Get event or error logs
    bin/isy_showevents.py - print live stream of events from ISY


Library Calls :


