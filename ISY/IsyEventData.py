
__all__ = ['event_ctrl']

event_ctrl  = {
        "_0" : "Heartbeat", 
        "_1" : "Trigger", 
        "_2" : "Protocol Specific", 
        "_3" : "Nodes Updated",
        "_4" : "System Config Updated", 
        "_5" : "System Status", 
        "_6" : "Internet Access", 
        "_7" : "System Progress", 
        "_8" : "Security System", 
        "_9" : "System Alert", 
        "_10" : "Electricity",
        "_11" : "Climate", 
        "_12" : "AMI/SEP", 
        "_13" : "Ext Energy Mon", 
        "_14" : "UPB Linker", 
        "_15" : "UPB Dev State", 
        "_16" : "UPB Dev Status", 
        "_17" : "Gas", 
        "_18" : "ZigBee", 
        "_19" : "Elk", 
        "_20" : "Device Link", 
        "DON" : "Device On", 
        "DFON" : "Device Fast On", 
        "DOF" : "Device Off", 
        "DFOF" : "Device Fast Off", 
        "ST" : "Status", 
        "OL" : "On Level",
        "RR" : "Ramp Rate", 
        "BMAN" : "Start Manual Change",
        "SMAN" : "Stop Manual Change",
        "CLISP" : "Setpoint",
        "CLISPH" : "Heat Setpoint",
        "CLISPC" : "Cool Setpoint",
        "CLIFS" : "Fan State",
        "CLIMD" : "Thermostat Mode",
        "CLIHUM" : "Humidity",
        "CLIHCS" : "Heat/Cool State",
        "BRT" : "Brighten",
        "DIM" : "Dim",
        "X10" : "Direct X10 Commands",
        "BEEP" : "Beep",
}

#
# Do nothing
# (syntax check)
#
if __name__ == "__main__":
    import __main__
    print __main__.__file__

    print("syntax ok")
    exit(0)
