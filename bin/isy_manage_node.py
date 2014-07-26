#!/usr/local/bin/python2.7
"""
    Node managment

    WORK IN PROGRESS

    Some command may not work yet

"""

__author__ = "Peter Shipley"

import ISY
# from ISY.IsyExceptionClass import IsyError

class cmdException(Exception):
    def __init__(self, msg) :
	Exception.__init__(self, msg)


verbose=0

commands_help = {
    "LINK, DISCOVER" : "place PLM into discover mode",
    "MV, RENAME" : "rename node",
    "RM, DEL, DELETE" : "delete node",
    "RESTORE" : "Restore node settings",
    "MD, NEWFOLDER, MKDIR" : "create new node folder",
    "RMDIR*" : "delete node folder",
    "ENABLE" : "enable node",
    "DISABLE" : "disable node",
    "LIST, LS" : "list nodes",
    "SCENE" : "add or delete node from scene",
    "FOLDER*" : "add or delete node from folder",
    "DEBUGLEVEL*" : "set/get ISY debug level",
    "REBOOT*" : "Reboot ISY",
    "HELP" : "print command list",
    "VERBOSE" : "set verbose",
    "ERROR" : "print last ISY error",
    "EXIT" : "exit program",
}

def doit(isy) :

    interactive = False

    argv = isy.unknown_args[:]

    if len(argv) == 0 :
	print "Entering interactive mode"
	import shlex
	interactive = True

    while 1:
	try :

	    if interactive is True :
		print "isylib> ",
		argv = shlex.split(raw_input())
		if argv is None or len(argv) == 0 :
		    continue

	    run_comm(isy, argv)
	except EOFError :
	    interactive = False
	    break
	except cmdException as e :
	    print e
	except ISY.IsyError as e :
	    print "IsyError :"
	    print "\t", e
	finally :
	    if interactive is not True :
		break


def run_comm(isy, argv) :
    global verbose

    cmd = argv.pop(0).upper()

    if cmd in ["LINK", "DISCOVER"] :
	link_nodes(isy, cmd,  argv)

    elif cmd in ["MV", "RENAME"] :
	do_rename_nodes(isy ,cmd, argv)

    elif cmd in [ "LS", "LIST" ] :
	do_list_node(isy, cmd, argv)

    elif cmd in [ "RM", "DEL", "DELETE"] :
	do_del_node(isy, cmd, argv)

    elif cmd in ["RESTORE"] :
	do_restore(isy, cmd, argv)

    elif cmd in ["MD", "NEWFOLDER", "MKDIR"] :
	if ( len(argv) > 0 and argv[0] != "?" ) :
	    foldername = argv.pop(0)
	    print "newfolder {!s}".format(foldername)
	else :
	    raise cmdException("Syntax :\n\t{!s} <foldername>".format(cmd))

    elif cmd in ["RMDIR"] :
	pass

    elif cmd in ["FOLDER", "DIR"] :
	do_folder(isy, cmd, argv)

    elif cmd in ["SCENE"] :
	do_scene(isy, cmd, argv)

    elif cmd in ["ENABLE", "EN" ] :
	if ( len(argv) > 0 and argv[0] != "?" ) :
	    nodeid = argv.pop(0)
	    isy.node_enable(nodeid, enable=1)
	else :
	    raise cmdException("Syntax :\n\t{!s} <node_id>".format(cmd))

    elif cmd in ["DISABLE","DIS"] :
	if ( len(argv) > 0 and argv[0] != "?" ) :
	    nodeid = argv.pop(0)
	    isy.node_enable(nodeid, enable=0)
	else :
	    raise cmdException("Syntax :\n\t{!s} <node_id>".format(cmd))

    elif cmd in ["ERROR", "ERR"] :
	# print last ISY error
	pass

    elif cmd in ["VERBOSE"] :
	if ( len(argv) > 0 ):
	    if (argv[0] == "?") :
		raise cmdException("Syntax :\n\t{!s} [level]".format(cmd))
	    else :
		verbose = int(argv[0])
	print "verbose = ", verbose


    elif cmd in ["REBOOT"] :
	do_reboot(isy)

    elif cmd in ["DEBUGLEVEL", "DBG"] :
	do_debuglevel(isy)

    elif cmd in ["HELP", "?"] :
	print_cmds()

    elif cmd in ["EXIT"] :
	if ( len(argv) > 0 and argv[0] != "?") :
	    raise cmdException("Syntax :\n\t{!s}".format(cmd))
	else :
	    exit(0)

    # DEBUG
    elif cmd in ["TEST"] :
	if ( len(argv) > 0 and argv[0] != "?") :
	    do_test(isy, cmd, argv)
	else :
	    raise cmdException("+\t{!s} <node_id>".format(cmd))

    else :
	print "Unknown command : ", cmd # str(" ").join(argv)

#
# TODO deal with  MV node Folder
#
def do_rename_nodes(isy, cmd, argv) :
    """
	rename node glue
    """
    if ( len(argv) > 1  and argv[0] != "?" ) :
	old = argv.pop(0)
	new = argv.pop(0)
	print cmd, old, new
	isy.rename(old, new)
    else :
	raise cmdException("Syntax :\n\t{!s} <node_id> <new_name>".format(cmd))

# DEBUG
def do_test(isy, cmd, argv) :
    if len(argv) == 1 :
	raise cmdException("Missing Arg:\n\t{!s} <node_id> <new_name>".format(cmd))
    else :
	print "TEST ", str(", ").join(argv)


def link_nodes(isy, cmd, argv) :
    """
	Link mode glue
    """
    if len(argv) == 0 :
	do_interactive_link(isy)

    cmd = argv.pop(0).upper()

    if cmd in [ "START" ] :
	isy.node_discover_start()
    elif cmd in [ "STOP" ] :
	isy.node_discover_stop()
    elif cmd in [ "?" ] :
	raise cmdException("Syntax :\n\tLINK [START|STOP]\n"
	    + "\tPlace PLM into discovery mode\n" )
    exit(0)


def do_interactive_link(isy) :

	isy.load_nodes()
	old_node_set = set(isy.node_addrs())

	print "Entering Linking Mode"
	isy.node_discover()
	raw_input("Press Enter to continue...")

	isy.node_discover_cancel()

	print "Exited Linking Mode"
	isy.load_nodes(reload=1)
	updated_node_set = set(isy.node_addrs() )

	new_node_set = updated_node_set - old_node_set
	print "New Nodes : ",  str(", ").join(new_node_set)

	exit(0)
def do_del_node(isy, cmd, argv) :
    """
	Delete node glue
    """
    if ( len(argv) == 0 or argv[0] == '?' or len(argv) > 1) :
	raise cmdException("Syntax :\n\t{!s} <node_id>".format(cmd))
    nodeid = argv.pop(0)
    print "isy.node_del(nodeid)"


def do_restore(isy, cmd, argv) :
    """
	restore node glue
    """
    if ( len(argv) > 0 and argv[0] != "?" ) :
	nodeid = argv.pop(0)
	if nodeid.upper() == "ALL" :
	    print "isy.node_restore_all(nodeid)"
	else  :
	    print "isy.node_restore(nodeid)"
    else :
	raise cmdException("Syntax :\n\t{!s} <node_id>\n\tto restore all nodes, use 'ALL' as node_id\n".format(cmd))


def do_folder(isy, cmd, argv) :
    pass

def do_scene(isy, cmd, argv) :
    """
	add/del node to/from scene glue
	create new scene/group glue
    """
    if ( len(argv) == 0 or argv[0] == "?" or len(argv) < 3 ) :
	print "1"
	op = "ERR"
    else :
	op = "ADD"
	nflag=0x10
	op = argv.pop(0).upper()
	
	if op in ["ADD", "DELETE", "DEL", "RM" ] :
	    nodeid = argv.pop(0)
	    sceneid = argv.pop(0)
	elif op in ["NEW"] :
	    sceneid = argv.pop(0)
	else :
	    op = "ERR"


	# print "a do_scene", op, nodeid, "sceneid",  nflag, "argv=", str(",").join(argv)

	if len(argv) > 0 :
	    optflag = argv.pop(0).upper()
	    if optflag in [ "CONTROLLER", "0X10", "16" ] or optflag.startswith("CON") :
		nflag=0x10
	    elif optflag in [ "RESPONDER", "0X20", "32" ] or optflag.startswith("RES") :
		nflag=0x20
	    else :
		op = "ERR"

    if op in [ "ADD" ] :
	# isy.scene_add_node( sceneid, nodeid, nflag)
	print "isy.scene_add_node", sceneid, nodeid, nflag
    elif op in [  "DELETE", "DEL", "RM" ] :
	# isy.scene_del_node( sceneid, nodeid)
	print "isy.scene_del_node", sceneid, nodeid
    elif op in [ "NEW" ]:
	pass
    else :
	raise cmdException("Syntax :\n\t{!s} [ADD|DEL] <scene_id> <node_id> [controller|responder]\n".format(cmd))



def do_list_node(isy, cmd, argv) :
    """
	list node glue
    """
    if ( len(argv) > 0 and argv[0] == "?" ) :
	raise cmdException("Syntax :\n\t{!s} [-l]".format(cmd))

    if len(argv) > 0 and argv[0] == "-l" :
	pfmt = "{:<22} {:>12}\t{:<12}{!s:<12} {!s:}"
    else :
	pfmt = "{:<22} {:>12}\t{:<12}{!s:<12}"

    # see isy_nodes.py
    if len(argv) > 0 :
	nodeid = argv.pop(0)
	node = isy.get_node(nodeid)
	print node.name, node.address, node.formatted, node.enabled, node.ramprate
    else :
	print(pfmt.format("Node Name", "Address", "Status", "Enabled", "Path"))
	print(pfmt.format("---------", "-------", "------", "------", "----"))
	for nod in isy :
	    if nod.objtype == "scene" :
		print(pfmt.format(nod.name, nod.address, "-", "-", "-"))
	    else :
		print(pfmt.format(nod.name, nod.address,
			nod.formatted, nod.enabled, nod.path))


def do_debuglevel(isy) :
    pass

def do_reboot(isy) :
    pass
    # ask "are you sure ?"
    # isy.reboot(isy)

def print_cmds() :
    for k, v in commands_help.items() :
	print "    {!s:<22} :\t{!s}".format(k, v)
    print "\nFor more detail on command run command with arg '?'"
    print "\n* == may not be implemented"


if __name__ == '__main__' :
    myisy = ISY.Isy(parsearg=1, faststart=1) # debug=0x80
    doit(myisy)
    exit(0)

