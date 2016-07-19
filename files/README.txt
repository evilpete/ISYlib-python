

to run scapy-watch.py at startup with systemd :

    cp scapy-watch.service /lib/systemd/system/
    chmod 644  /lib/systemd/system/scapy-watch.service
    systemctl enable scapy-watch
		     
