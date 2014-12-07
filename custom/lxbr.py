from mininet.node import Switch
from mininet.topo import Topo


class LinuxBridge( Switch ):
    "Linux Bridge"
    prio = 0

    def __init__( self, name, stp=True, **kwargs ):
        self.stp = stp
        Switch.__init__( self, name, **kwargs )

    def start( self, controllers ):
        self.cmd( 'ifconfig', self, 'down' )
        self.cmd( 'brctl delbr', self )
        self.cmd( 'brctl addbr', self )
        if self.stp:
            self.cmd( 'brctl setbridgeprio', self.prio )
            self.cmd( 'brctl stp', self, 'on' )
            LinuxBridge.prio += 1
        for i in self.intfList():
            if self.name in i.name:
                self.cmd( 'brctl addif', self, i )
        self.cmd( 'ifconfig', self, 'up' )

    def stop( self ):
        self.cmd( 'ifconfig', self, 'down' )
        self.cmd( 'brctl delbr', self )


class ABCTopo( Topo ):
    "Simple topology example."

    def __init__( self ):
        "Create custom topo."

        # Initialize topology
        Topo.__init__( self )

        # Add hosts and switches
        leftHost = self.addHost( 'h1' )
        middleHost = self.addHost( 'h2' )
        rightHost = self.addHost( 'h3' )

        # Add links
        self.addLink( leftHost, middleHost )
        self.addLink( middleHost, rightHost )


class ABCTopoSwitched( Topo ):
    "Simple topology example."

    def __init__( self ):
        "Create custom topo."

        # Initialize topology
        Topo.__init__( self )

        # Add hosts and switches
        leftHost = self.addHost( 'h1' )
        middleHost = self.addHost( 'h2' )
        rightHost = self.addHost( 'h3' )
        leftSwitch = self.addSwitch( 's1' )
        rightSwitch = self.addSwitch( 's2' )

        # Add links
        self.addLink( leftHost, leftSwitch )
        self.addLink( leftSwitch, middleHost )
        self.addLink( middleHost, rightSwitch )
        self.addLink( rightSwitch, rightHost )

topos = { 'abctopo': ( lambda: ABCTopo() ),
          'abctopo-switched': ( lambda: ABCTopoSwitched() ) }
switches = { 'lxbr': LinuxBridge }
