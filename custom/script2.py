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
    A1_NAT = True
    A2_NAT = True
    A1_A2_P2P_VPN = True
    A2_ACCESS_VPN = False

    # Validation of boolean options
    A1_A2_P2P_VPN = A1_A2_P2P_VPN and A1_NAT and A2_NAT
    A2_ACCESS_VPN = A2_ACCESS_VPN and A2_NAT

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
    if not A1_NAT:
        setHostRoute(h91, '10.0.1.0/24', '192.168.81.1', 'h91-eth0')
    if not A2_NAT:
        setHostRoute(h91, '10.0.2.0/24', '192.168.70.92', 'h91-eth1')
    setHostRoute(h91, '192.168.82.0/24', '192.168.70.92', 'h91-eth1')
    setHostRoute(h91, '10.0.3.0/24',     '192.168.70.93', 'h91-eth1')
    setHostRoute(h91, '192.168.83.0/24', '192.168.70.93', 'h91-eth1')

    if not A1_NAT:
        setHostRoute(h92, '10.0.1.0/24', '192.168.70.91', 'h92-eth1')
    setHostRoute(h92, '192.168.81.0/24', '192.168.70.91', 'h92-eth1')
    if not A2_NAT:
        setHostRoute(h92, '10.0.2.0/24', '192.168.82.11', 'h92-eth0')
    setHostRoute(h92, '10.0.3.0/24',     '192.168.70.93', 'h92-eth1')
    setHostRoute(h92, '192.168.83.0/24', '192.168.70.93', 'h92-eth1')

    if not A1_NAT:
        setHostRoute(h93, '10.0.1.0/24', '192.168.70.91', 'h93-eth1')
    setHostRoute(h93, '192.168.81.0/24', '192.168.70.91', 'h93-eth1')
    if not A2_NAT:
        setHostRoute(h93, '10.0.2.0/24', '192.168.70.92', 'h93-eth1')
    setHostRoute(h93, '192.168.82.0/24', '192.168.70.92', 'h93-eth1')
    setHostRoute(h93, '10.0.3.0/24',     '192.168.83.21', 'h93-eth0')

    # Enable IPv4 forwarding on hosts that must act as router
    enableIpForwarding(h1)
    enableIpForwarding(h11)
    enableIpForwarding(h21)
    enableIpForwarding(h91)
    enableIpForwarding(h92)
    enableIpForwarding(h93)

    if A1_NAT:
        # NAT A1 network at A1 CE router
        h1.cmd('iptables -t nat -A POSTROUTING '
               '--out-interface h1-eth1 -j MASQUERADE')

    if A2_NAT:
        # NAT A2 network at A1 CE router
        h11.cmd('iptables -t nat -A POSTROUTING '
               '--out-interface h11-eth1 -j MASQUERADE')

    if A1_A2_P2P_VPN:
        # A1 and A2 are behind NAT, so they cannot communicate
        # with each other. However, since h1 (A1 CE) and h11 (A2 CE)
        # have public IPs (192.168.81.1 and 192.168.82.11, respectively,
        # we can create an OpenVPN p2p tunnel - represented by the virtual
        # point-to-point subnet 10.4.0.1-10.4.0.2, and route the private
        # subnets through the VPN tunnel (i.e. through tun1).
        h1.cmd('openvpn  --remote 192.168.82.11 --dev tun1 '
                        '--ifconfig 10.4.0.1 10.4.0.2 '
                        '--route 10.0.2.0 255.255.255.0 vpn_gateway &')
        h11.cmd('openvpn --remote 192.168.81.1 --dev tun1 '
                        '--ifconfig 10.4.0.2 10.4.0.1 '
                        '--route 10.0.1.0 255.255.255.0 vpn_gateway &')

    if A2_ACCESS_VPN:
        h11.cmd('openvpn --mode server --dev tun2 '
                        '--port 5000 --tls-server '
                        '--dh /root/easy-rsa/keys/dh2048.pem '
                        '--ca /root/easy-rsa/keys/ca.crt '
                        '--cert /root/easy-rsa/keys/h11.crt '
                        '--key /root/easy-rsa/keys/h11.key '
                        '--topology p2p '
                        '--push "topology p2p" '
                        '--ifconfig 10.8.0.1 10.8.0.2 '
                        '--ifconfig-pool 10.8.0.4 10.8.0.251 '
                        '--route 10.8.0.0 255.255.255.0 vpn_gateway '
                        '--client-to-client '
                        '--push "route 10.8.0.0 255.255.255.0" &')
        h22.cmd('openvpn --remote 192.168.82.11 --dev tun2 '
                        '--port 5000 --tls-client '
                        '--ca /root/easy-rsa/keys/ca.crt '
                        '--cert /root/easy-rsa/keys/h22.crt '
                        '--key /root/easy-rsa/keys/h22.key '
                        '--pull &')

    net.start()
    print "Dumping host connections"
    dumpNodeConnections(net.hosts)
    print "Executing commands"
    #print net.get('h1').cmd('ip route')
    CLI(net)
    s1.cmd('killall openvpn')
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    main()
