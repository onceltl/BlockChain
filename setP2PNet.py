#!/usr/bin/python3  
# -*- coding: utf-8 -*- 

import time
import sys
import os
from mininet.net import Mininet
from mininet.topolib import TreeTopo
from mininet.link import Link
from CustomTopo import *
from cmd import Cmd

P2PNet=None
defaultPort = 50000
def xtermCMD(peer,ip1, port1, ip2, port2, mode):
    name="Host_%d: " % peer

    file = "main.py"
   # file = os.path.join(cur_path, file)

    args = "%s %d %s %d %s" % (ip1,port1,ip2,port2,mode)

    name = "%s %s %d" % (name, ip1, port1)

    cmd = 'xterm -hold -geometry 130x40+0+900 -title "%s" -e python -u "%s" %s &'
    return cmd % (name, file, args)

def setupP2PNet(netType="net",weight=1,high=1,bw=10,delay=5,loss=0,mode='test'):
    global P2PNet
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
        cmd= xtermCMD(i,host.IP(), defaultPort, P2PNet.hosts[0].IP(), defaultPort, mode)
        print(cmd)
        host.cmd(cmd)
        time.sleep(1)
    P2PNet.pingAll() 


class NetworkCMD(Cmd):
    intro = "Control simulation network. Type ? to list commands.\n"
    prompt = "Bitcoin>>> "

    def __init(self,bw=10,delay=5,loss=0,mode='test'):
        reload(sys)
        super(NetworkCMD, self).__init__()
        sys.setdefaultencoding('utf-8')

    def do_exit(self,arg):
        print ('Bye!')
        return True 
    def do_KillXterm(self,line):
        os.system("killall -SIGKILL xterm")
        os.system("mn --clean > /dev/null 2>&1")

    def do_ShowHosts(self, line):
        for i, host in enumerate(P2PNet.hosts):
            print(i, host.IP, host.name)

    def do_AddHost(self, line):
        
        global P2PNet
        id = len(P2PNet.hosts) + 1

        newHost = P2PNet.addHost("h%d" % id)

        switch = P2PNet.switches[0];

        P2PNet.addLink(switch, newHost);

        slink = Link(switch, newHost)
        switch.attach(slink);
        switch.start(P2PNet.controllers);

        newHost.configDefault(defaultRoute=newHost.defaultIntf())

        print(P2PNet.hosts[0].cmd("ping -c1 %s" % newHost.IP() )) 

        print(newHost.cmd("ping -c1 10.0.0.1"))

        cmd = xtermCMD(id,newHost.IP(),defaultPort,P2PNet.hosts[0].IP(),defaultPort, 'test')

        print(cmd)

        newHost.cmd(cmd)

        print("Started new node: %s" % newHost)

    def do_DelHost(self, line):

        global P2PNet
        args = line.split()
        if (len(args) != 1):
            print("Expected 1 argument, %d given" % len(args))
        else:
            hostName = args[0].strip()
            node = None;
            for host in P2PNet.hosts:
                if host.name == hostName:
                    node = host;
                    break;
            if node == None:
                print("Wrong hostName.")
            else:
                P2PNet.delNode(node)
                print("Deleted %s" %hostName)
                
if __name__ == '__main__':
    setupP2PNet(netType='star',weight=3,high=2)
    myCmd = NetworkCMD()
    myCmd.cmdloop()