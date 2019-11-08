#!/usr/bin/python3  
# -*- coding: utf-8 -*- 

from mininet.net import Mininet
from mininet.topolib import TreeTopo
from CustomTopo import *
P2PNet=None
def setupP2PNet(netType="net",weight=1,high=1,bw=10,delay=5,loss=0):

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
        startopo = StarTopo(weight * high)
        P2PNet = Mininet(topo=startopo)
    elif netType == "net":
        print("net");
        nettopo = NetTopo(weight,high,bw=bw,delay=delay,loss=loss)
        P2PNet = Mininet(topo=nettopo)
    else:
        print("netType error!");
        sys.exit(0);

    P2PNet.start();
    #P2PNet.pingAll() 
    P2PNet.stop()


if __name__ == '__main__':
    setupP2PNet(netType='net',weight=2,high=3)