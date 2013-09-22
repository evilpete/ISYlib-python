"""
This is a subfile for IsyClass.py

ZigBee Support 

Only applicable to ISY994 Z Series.


for now these are just empty hooks will I get my ZigBee Net working
to test against

"""

# author : Peter Shipley <peter.shipley@gmail.com>
# copyrigh :  Copyright (C) 2013 Peter Shipley
# license : BSD

def load_zb():
    # /rest/zb/nodes
    pass

def zb_scannetwork():
    # /rest/zb/scanNetwork
    pass

def zb_ntable():
    # /rest/zb/ntable
    pass

def zb_ping_node():
    # /rest/zb/nodes/[euid]/ping
    pass

def get_zbnode():
    pass

def zbnode_addrs():
    pass

def zbnode_names():
    pass

def _zbnode_get_id():
    pass

def zbnode_comm():
    pass

def zbnode_iter():
    pass


# Do nothing
# (syntax check)
#
if __name__ == "__main__":
    import __main__
    print(__main__.__file__)

    print("syntax ok")
    exit(0)
