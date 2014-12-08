#!/bin/python2

from mininet.net import Mininet
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel
from mininet.cli import CLI
import lxbr


# Create a link between node1 and node2, and possibly set
# the IP of the two interfaces involved in the link
def addLinkWithIP(net, node1, ip1, node2, ip2):
    net.addLink(node1, node2)
    pair = node1.connectionsTo(node2)[0]
    if ip1:
        pair[0].setIP(ip1)
    if ip2:
        pair[1].setIP(ip2)

def main():
    net = Mininet()
    # Create hosts. We specify ip = None, so that Mininet
    # does not automatically configure the IPs
    h1 = net.addHost('h1', ip = None)
    h2 = net.addHost('h2', ip = None)
    h3 = net.addHost('h3', ip = None)
    h4 = net.addHost('h4', ip = None)
    h5 = net.addHost('h5', ip = None)

    # Create switches, using the standard linux bridge
    s1 = net.addSwitch('s1', lxbr.LinuxBridge)
    s2 = net.addSwitch('s2', lxbr.LinuxBridge)

    # Create links, and assign IP to the host interfaces
    addLinkWithIP(net, h1, '10.0.1.1/24', h2, '10.0.1.2/24')
    addLinkWithIP(net, h2, '192.168.0.2/24', s1, None)
    addLinkWithIP(net, s1, None, h3, '192.168.0.3/24')
    addLinkWithIP(net, h3, '10.0.2.3/24', s2, None)
    addLinkWithIP(net, s2, None, h4, '10.0.2.4/24')
    addLinkWithIP(net, s2, None, h5, '10.0.2.5/24')

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
