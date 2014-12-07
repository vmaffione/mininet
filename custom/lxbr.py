from mininet.node import Switch


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

switches = { 'lxbr': LinuxBridge }

