from mininet.topo import Topo
from mininet.net import Mininet
from mininet.util import irange, dumpNodeConnections
from mininet.log import setLogLevel
from mininet.node import CPULimitedHost
from mininet.link import TCLink

class StarTopo(Topo):
    def build(self, n=2,bw=10,delay=5,loss=0): #bw=10, delay='5ms',max_queue_size=1000, loss=10, use_htb=True
        self.hostNum=n; 
        self.switchNum = 1;
        switch = self.addSwitch( 's%s' % 1 )
        for i in irange( 1, n ):
            host = self.addHost( 'h%s' %i ) 
            self.addLink(host, switch,cls=TCLink,bw=bw,delay=delay,loss=loss)

class CircleTopo(Topo):
    def build(self, n=2,m=2,bw=10,delay=5,loss=0):
        self.hostNum=n*m; 
        self.switchNum = n;
        switch ={};
        for i in irange( 1, n ):
            switch[i]= self.addSwitch( 's%s' % i )
            for j in irange( 1, m ):
                host = self.addHost( 's%s-h%s' %(i,j) ) 
                self.addLink(host, switch[i],cls=TCLink,bw=bw,delay=delay,loss=loss)
        for i in irange( 1, n-1 ):
            self.addLink(switch[i],switch[i+1])
        #self.addLink(switch[n],switch[1]);

class NetTopo(Topo):
    def build(self, n=2,m=2,bw=10,delay=5,loss=0):
        self.hostNum=n * n *n; 
        self.switchNum = n*n;
        switch ={};
        for i in irange( 1, n ):
            for k in irange( 1, n ):
                switch[(i-1)*n+k]= self.addSwitch( 's%s' % ((i-1)*n+k) )
                for j in irange( 1, m ):
                    host = self.addHost( 's%s-h%s' %((i-1)*n+k,j) ) 
                    self.addLink(host, switch[(i-1)*n+k],cls=TCLink,bw=bw,delay=delay,loss=loss)
        
        for i in irange( 1, n-1 ):
            
            for k in irange( 1, n-1 ):
                self.addLink(switch[(i-1)*n+k],switch[i*n+k]);
                self.addLink(switch[(i-1)*n+k],switch[(i-1)*n+k+1]);

            self.addLink(switch[(i-1)*n+n],switch[i*n+n]);

