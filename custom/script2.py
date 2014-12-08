#!/bin/python2

from mininet.net import Mininet
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel
from mininet.cli import CLI
import lxbr


def main():
    net = Mininet()
    h1 = net.addHost('h1')
    h2 = net.addHost('h2')
    h3 = net.addHost('h3')
    h4 = net.addHost('h4')
    s1 = net.addSwitch('s1', lxbr.LinuxBridge)
    net.addLink(h1, h2)
    net.addLink(h2, s1)
    net.addLink(s1, h3)
    net.addLink(h3, h4)
    net.start()
    print "Dumping host connections"
    dumpNodeConnections(net.hosts)
    print "Executing commands"
    #print net.get('h1').cmd('ip route')
    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    main()
