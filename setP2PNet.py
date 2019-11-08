#!/usr/bin/python3  
# -*- coding: utf-8 -*- 

from mininet.net import Mininet
from mininet.topolib import TreeTopo

P2PNet=None

def setupP2PNet(netType="net",weight=1,high=1):

    if netType == "circle":
        print("circle");

    elif netType == "tree":
        print("tree")
        treetopo = TreeTopo(depth=weight,fanout=high)
        P2PNet = Mininet(topo=treetopo)
        
    elif netType == "star":
        print("star");
    
    elif netType == "net":
        print("net");

    P2PNet.start();
    P2PNet.pingAll() 
    P2PNet.stop()


if __name__ == '__main__':
    setupP2PNet(netType='tree',weight=2,high=2)