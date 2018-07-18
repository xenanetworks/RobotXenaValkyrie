"""
Base class for all traffic generators tests.

@author yoram@ignissoft.com
"""

from __future__ import unicode_literals
from os import path
import unittest

from xenavalkyrie_robot.xena_robot import XenaRobot

chassis = '192.168.1.197'
port0 = chassis + '/0/0'
port1 = chassis + '/0/1'


class RobotTest(unittest.TestCase):

    def setUp(self):
        self.robot = XenaRobot()
        self.robot.add_chassis(chassis)

    def tearDown(self):
        pass

    def hello_world(self):
        pass

    def investigate_configuration(self):
        self.robot.reserve_ports(port0, port1)
        self.robot.load_config(port0, path.join(path.dirname(path.dirname(__file__)), 'samples', 'test_config.xpc'))
        self.robot.get_modifier(port0, '0', '4')

    def build_configuration(self):
        self.robot.reserve_ports(port0, port1)
        self.robot.add_stream(port1, 'ip-udp')
        self.robot.add_packet_headers(port1, '0', 'ip', 'udp')
        self.robot.set_packet_header_fields(port1, '0', 'Ethernet', src_s='11:11:11:11:11:11',
                                            dst_s='22:22:22:22:22:22')
        self.robot.set_packet_header_fields(port1, '0', 'ip', src_s='1.1.1.1', dst_s='2.2.2.2')
        self.robot.add_stream(port1, 'vlan-ip6-tcp')
        self.robot.set_stream_attributes(port1, '1', ps_packetlength='FIXED 128 128')
        self.robot.add_packet_headers(port1, '1', 'VLAN', 'IP6', 'TCP')
        self.robot.set_packet_header_fields(port1, '1', 'VLAN[0]', vid=17)
        self.robot.set_packet_header_fields(port1, '1', 'IP6', src_s='11::11', dst_s='22::22')
        self.robot.add_modifier(port1, '0', '4')
        self.robot.set_modifier_attributes(port1, '0', '4', min_val='10', max_val='20', action='decrement')
        self.robot.remove_modifier(port1, '0', '4')
