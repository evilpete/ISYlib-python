#!/usr/local/bin/python2.7
"""
    Node managment

    WORK IN PROGRESS 

    Some command may not work yet

"""

__author__ = "Peter Shipley"

import ISY

def doit(isy) :
    argv = isy.unknown_args[:]

    if len(argv) == 0 :
	print "no args"
	exit(0)

    cmd = argv.pop(0).upper()
    if cmd in ["LINK", "DISCOVER"] :
	link_nodes(isy, argv)

    elif cmd in ["MV", "RENAME"] :
	do_rename_nodes(isy, argv)

    elif cmd in [ "RM", "DEL", "DELETE"] :
	if ( len(argv) > 0 ) :
	    nodeid = argv.pop(0)
	    print "isy.node_del(nodeid)"
	else :
	    print "Missing Arg:\n\t{!s} <node_id>".format(cmd)

    elif cmd in ["RESTORE"] :
	if ( len(argv) > 0 ) :
	    nodeid = argv.pop(0)
	    if nodeid.upper() == "ALL" :
		print "isy.node_restore_all(nodeid)"
	    else  :
		print "isy.node_restore(nodeid)"
	else :
	    print "Missing Arg:\n\t{!s} <node_id>".format(cmd)
	exit(0)

    elif cmd in ["MD", "NEWFOLDER", "MKDIR"] :
	print "Missing COMMAND:\n\t{!s} <folder_id>".format(cmd)
	exit(0)

    elif cmd in ["ENABLE"] :
	if ( len(argv) > 0 ) :
	    nodeid = argv.pop(0)
	    isy.node_enable(nodeid, enable=1)
	else :
	    print "Missing Arg:\n\t{!s} <node_id>".format(cmd)
	exit(0)

    elif cmd in ["DISABLE"] :
	if ( len(argv) > 0 ) :
	    nodeid = argv.pop(0)
	    isy.node_enable(nodeid, enable=0)
	else :
	    print "Missing Arg:\n\t{!s} <node_id>".format(cmd)
	exit(0)

    else :
	print "Unknown commands : ", str(" ").join(argv)

#
# TODO deal with  MV node Folder
#
def do_rename_nodes(isy, argv) :
    if ( len(argv) > 1 ) :
	old = argv.pop(0)
	new = argv.pop(0)
	isy.rename(old, new)
    else :
	print "Missing Arg:\n\t{!s} <node_id> <new_name>".format(cmd)
    exit(0)




def link_nodes(isy, argv) :
    """ 
	node's infomation
    """
    if len(argv) == 0 :
	do_interactive_link(isy)

    cmd = argv.pop(0).upper()

    if cmd in [ "START" ] :
	isy.node_discover()
    elif cmd in [ "STOP" ] :
	node_discover_cancel()
    exit(0)


def do_interactive_link(isy) :

	isy.load_nodes()
	old_node_set = set(isy.node_addrs())

	print "Entering Linking Mode"
	isy.node_discover()
	raw_input("Press Enter to continue...")

	isy.node_discover_cancel()

	print "Exiedt Linking Mode"
	isy.load_nodes(reload=1)
	updated_node_set = set(isy.node_addrs() )

	new_node_set = updated_node_set - old_node_set
	print "New Nodes : ",  str(", ").join(new_node_set)

	exit(0)


if __name__ == '__main__' :
    myisy = ISY.Isy(parsearg=1, faststart=1) # debug=0x80
    doit(myisy)
    exit(0)

