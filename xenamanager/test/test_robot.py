"""
Base class for all traffic generators tests.

@author yoram@ignissoft.com
"""

import unittest

from xenamanager.robot.xena_robot import XenaRobot

chassis='176.22.65.114'
port1 = chassis + '/6/4'
port2 = chassis + '/6/5'


class RobotTest(unittest.TestCase):
    
    def setUp(self):
        self.robot = XenaRobot()
        self.robot.add_chassis(chassis)
        
    def tearDown(self):
        pass
    
    def hello_world(self):
        pass
    
    def add_packet_headers(self):
        self.robot.reserve_ports(port1, port2)
        self.robot.add_stream(port1, 'ip-udp')
        self.robot.add_packet_headers(port1, 0, 'vlan', 'ip', 'udp')
