ISYlib-python
=============

Simple Python lib for the ISY home automation netapp Supporting a Simple and OO interface


The Goal / design concept is to provide a fast and simple to use interface
supporting both object oriented and procedural methods

Also Supports real time cache updating by optionally running a sub-thread subscribing to event stream )


Note:
    This Lib has grown to the point it needs to be restructured / split up

----

This is a work in progress ( so expect new features )

see [/bin]  (/bin) for more examples

nodes, programs and iay  vars can be controlled via objects or call methods.

Get and print the status for the node called "Garage Light"

    import ISY
    myisy = ISY.Isy(addr="admin", userp="admin, userl="isy")

    garage_light = myisy.get_node("Garage Light")

    print "Node {:} is {:}".format(garage_light.name, garage_light.formatted)


--

Get an object that represents the node called "Garage Light"
and turn it off if it is on

    import ISY
    myisy = ISY.Isy()

    garage_light = myisy.get_node("Garage Light")
    if garage_light :
        garage_light.off()


--

Alternately you can obtain a Node's object by indexing
a Isy obj my the node name or address

    import ISY
    myisy = ISY.Isy()
    myisy["16 3F E5 1"].off()
or
    myisy["Garage Light"].off()


on 50% :

    garage_light = myisy["Garage Light"]
    garage_light.on(128)

or without node device objs

    myisy.node_comm("Garage Light", "on", 128)

list all nodes and scenes and their status :

    pfmt = "{:<22} {:>12}\t{:<12}{!s:<12}"
    print(pfmt.format("Node Name", "Address", "Status", "Enabled"))
    print(pfmt.format("---------", "-------", "------", "------"))
    for nod in isy :
        if nod.objtype == "scene" :
            print(pfmt.format(nod.name, nod.address, "-", "-", ))
        else :
            print(pfmt.format(nod.name, nod.address, nod.formatted, nod.enabled, ))


--

Callbacks can be set up as easy as

    def mycall(*args):
        print "mycall called: "
        for i in args :
            print "arg : ", type(i), i

    myisy = ISY.Isy(addr="10.1.1.3", eventupdates=1)
    myisy.callback_set("Garage Light", mycall, "my extra args")

or

    garage_light = myisy["Garage Light"]
    garage_light.set_callback(mycall, "my extra args")

or if your not passing extra arguments you can just :

    garage_light = myisy["Garage Light"]
    garage_light.set_callback = mycall

Callback will be call for all events relating to the node it is registared to

Callbacks are executed as a part of the event subthread 

--

see also :
    http://www.universal-devices.com/residential/
and/or
    http://wiki.universal-devices.com/index.php?title=Main_Page

NOTE: This Libaray is not written by or supported by universal devices




ISYlib-python Documentation
---------------------------
[This needs to be updated]

* [Using_Isy_Class]  (/docs/Using_Isy_Class.txt) This is the main class that used to represent the ISY device iitself

* [Using_IsyNode_Class]  (/docs/Using_IsyNode_Class.txt) This class is used to represent and control individual Nodes ( aka: sensors and light switches ) 

* [Using_IsyVar_Class]  (/docs/Using_IsyVar_Class.txt) This class is used to represent varabibles internal to the ISY




Notes:
    - Todo: Apply Style Guide @: http://www.python.org/dev/peps/pep-0008/
    - Todo: split up main Class (IsyClass) into several subclasses


