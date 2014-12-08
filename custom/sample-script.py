#!/bin/python2

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel
from mininet.cli import CLI


class SingleSwitchTopo(Topo):
    "Single switch connected to n hosts"
    def __init__(self, n=2, **opts):
        Topo.__init__(self, **opts)
        switch = self.addSwitch('s1')
        for h in range(n):
            host = self.addHost('h%s' % (h+1))
            self.addLink(host, switch)

def simpleTest():
    topo = SingleSwitchTopo(n=4)
    net = Mininet(topo)
    net.start()
    print "Dumping host connections"
    dumpNodeConnections(net.hosts)
    print "Executing commands"
    #print net.get('h1').cmd('ip route')
    #CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    simpleTest()
