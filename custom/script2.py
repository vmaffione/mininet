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

def setHostDefaultRoute(host, gw, dev):
    output = host.cmd('ip route add default via %s dev %s' % (gw, dev))

def setHostRoute(host, dest, gw, dev):
    output = host.cmd('ip route add %s via %s dev %s' % (dest, gw, dev))

def enableIpForwarding(host, enable = True):
    value = 1 if enable else 0
    output = host.cmd('sysctl net.ipv4.ip_forward=%s' % (value))

def main():
    net = Mininet()
    # Create hosts and switches. For hosts, we specify ip = None, so that
    # Mininet does not automatically configure the IPs. The switches are
    # implemented by standard linux software bridges.
    h1 = net.addHost('h1', ip = None) # CUstomer Edge A1
    h2 = net.addHost('h2', ip = None)
    h3 = net.addHost('h3', ip = None)
    s1 = net.addSwitch('s1', lxbr.LinuxBridge) # Customer A1 switch

    h11 = net.addHost('h11', ip = None) # Customer Edge A2
    h12 = net.addHost('h12', ip = None)
    h13 = net.addHost('h13', ip = None)
    s2 = net.addSwitch('s2', lxbr.LinuxBridge) # Customer A2 switch

    h21 = net.addHost('h21', ip = None) # Public networks Edge
    h22 = net.addHost('h22', ip = None)
    h23 = net.addHost('h23', ip = None)
    s3 = net.addSwitch('s3', lxbr.LinuxBridge) # Public network switch

    h91 = net.addHost('h91', ip = None) # Provider Edge A1
    h92 = net.addHost('h92', ip = None) # Provider Edge A2
    h93 = net.addHost('h93', ip = None) # Provider Edge public network
    s4 = net.addSwitch('s4', lxbr.LinuxBridge) # ISP switch

    # Create links, and assign IP to the host interfaces for ...

    # ... A1 network
    addLinkWithIP(net, h1, '10.0.1.1/24', s1, None)
    addLinkWithIP(net, h2, '10.0.1.2/24', s1, None)
    addLinkWithIP(net, h3, '10.0.1.3/24', s1, None)
    addLinkWithIP(net, h1, '192.168.81.1/24', h91, '192.168.81.91/24')

    # ... A2 network
    addLinkWithIP(net, h11, '10.0.2.11/24', s2, None)
    addLinkWithIP(net, h12, '10.0.2.12/24', s2, None)
    addLinkWithIP(net, h13, '10.0.2.13/24', s2, None)
    addLinkWithIP(net, h11, '192.168.82.11/24', h92, '192.168.82.92/24')

    # ... public network
    addLinkWithIP(net, h21, '10.0.3.21/24', s3, None)
    addLinkWithIP(net, h22, '10.0.3.22/24', s3, None)
    addLinkWithIP(net, h23, '10.0.3.23/24', s3, None)
    addLinkWithIP(net, h21, '192.168.83.21/24', h93, '192.168.83.93/24')

    # ... ISP network
    addLinkWithIP(net, h91, '192.168.70.91/24', s4, None)
    addLinkWithIP(net, h92, '192.168.70.92/24', s4, None)
    addLinkWithIP(net, h93, '192.168.70.93/24', s4, None)

    # Set default routes for A1, A2 and public networks.
    setHostDefaultRoute(h1, h91.IP(), 'h1-eth1')
    setHostDefaultRoute(h2, h1.IP(), 'h2-eth0')
    setHostDefaultRoute(h3, h1.IP(), 'h3-eth0')

    setHostDefaultRoute(h11, h92.IP(), 'h11-eth1')
    setHostDefaultRoute(h12, h11.IP(), 'h12-eth0')
    setHostDefaultRoute(h13, h11.IP(), 'h13-eth0')

    setHostDefaultRoute(h21, h93.IP(), 'h21-eth1')
    setHostDefaultRoute(h22, h21.IP(), 'h22-eth0')
    setHostDefaultRoute(h23, h21.IP(), 'h23-eth0')

    # Set global routes in default-free zone (ISP network)
    setHostRoute(h91, '10.0.1.0/24',     '192.168.81.1', 'h91-eth0')
    setHostRoute(h91, '10.0.2.0/24',     '192.168.70.92', 'h91-eth1')
    setHostRoute(h91, '192.168.82.0/24', '192.168.70.92', 'h91-eth1')
    setHostRoute(h91, '10.0.3.0/24',     '192.168.70.93', 'h91-eth1')
    setHostRoute(h91, '192.168.83.0/24', '192.168.70.93', 'h91-eth1')

    setHostRoute(h92, '10.0.1.0/24',     '192.168.70.91', 'h92-eth1')
    setHostRoute(h92, '192.168.81.0/24', '192.168.70.91', 'h92-eth1')
    setHostRoute(h92, '10.0.2.0/24',     '192.168.82.11', 'h92-eth0')
    setHostRoute(h92, '10.0.3.0/24',     '192.168.70.93', 'h92-eth1')
    setHostRoute(h92, '192.168.83.0/24', '192.168.70.93', 'h92-eth1')

    setHostRoute(h93, '10.0.1.0/24',     '192.168.70.91', 'h93-eth1')
    setHostRoute(h93, '192.168.81.0/24', '192.168.70.91', 'h93-eth1')
    setHostRoute(h93, '10.0.2.0/24',     '192.168.70.92', 'h93-eth1')
    setHostRoute(h93, '192.168.82.0/24', '192.168.70.92', 'h93-eth1')
    setHostRoute(h93, '10.0.3.0/24',     '192.168.83.21', 'h93-eth0')

    # Enable IPv4 forwarding on hosts that must act as router
    enableIpForwarding(h1)
    enableIpForwarding(h11)
    enableIpForwarding(h21)
    enableIpForwarding(h91)
    enableIpForwarding(h92)
    enableIpForwarding(h93)

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
