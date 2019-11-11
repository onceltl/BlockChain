#!/usr/bin/python3  
# -*- coding: utf-8 -*- 

import time
import sys
from mininet.net import Mininet
from mininet.topolib import TreeTopo
from CustomTopo import *

P2PNet=None

def xtermCMD(peer,ip1, port1, ip2, port2, mode):
    name="Host_%d: " % peer

    file = "main.py"
   # file = os.path.join(cur_path, file)

    args = "%s %d %s %d %s" % (ip1,port1,ip2,port2,mode)

    name = "%s %s %d" % (name, ip1, port1)

    cmd = 'xterm -hold -geometry 130x40+0+900 -title "%s" -e python3 -u "%s" %s &'
    return cmd % (name, file, args)

def setupP2PNet(netType="net",weight=1,high=1,bw=10,delay=5,loss=0,mode='test'):

    if netType == "circle":
        print("circle");
        circletopo = CircleTopo(weight,high,bw=bw,delay=delay,loss=loss)
        P2PNet = Mininet(topo=circletopo)
    elif netType == "tree":
        print("tree")
        treetopo = TreeTopo(depth=weight,fanout=high,bw=bw,delay=delay,loss=loss)
        P2PNet = Mininet(topo=treetopo)
    elif netType == "star":
        print("star");
        startopo = StarTopo(weight * high,bw=bw,delay=delay,loss=loss)
        P2PNet = Mininet(topo=startopo)
    elif netType == "net":
        print("net");
        nettopo = NetTopo(weight,high,bw=bw,delay=delay,loss=loss)
        P2PNet = Mininet(topo=nettopo)
    else:
        print("netType error!");
        sys.exit(0);

    P2PNet.start();
    for i, host in enumerate(P2PNet.hosts):
        print(i,host.IP)
        cmd= xtermCMD(i,host.IP(), 50000, P2PNet.hosts[0].IP(), 50000, mode)
        print(cmd)
        host.cmd(cmd)
        time.sleep(1)
    P2PNet.pingAll() 
    #P2PNet.stop()
    try:
        while True:
            time.sleep(60*60*24) # one day in seconds
    except KeyboardInterrupt:
        sys.exit(0)

if __name__ == '__main__':
    setupP2PNet(netType='star',weight=2,high=3)
