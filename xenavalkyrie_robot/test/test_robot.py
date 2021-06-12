"""
Base class for all traffic generators tests.

@author yoram@ignissoft.com
"""

from os import path
import unittest

from xenavalkyrie_robot.xena_robot import XenaRobot

chassis = '176.22.65.117'
port0 = chassis + '/0/0'
port1 = chassis + '/0/1'


class RobotTest(unittest.TestCase):

    def setUp(self):
        self.robot = XenaRobot(api='socket', user='robot', ip='localhost')
        self.robot.add_chassis(chassis)

    def tearDown(self):
        pass

    def test_hello_world(self):
        pass

    def test_investigate_configuration(self):
        self.robot.reserve_ports_by_force(port0, port1)
        self.robot.load_config(port0, path.join(path.dirname(path.dirname(__file__)), 'samples', 'test_config.xpc'))
        self.robot.get_modifier(port0, '0', '0')
        self.robot.get_packet_header(port0, '1', 'Ethernet')

    def test_build_configuration(self):
        self.robot.reserve_ports_by_force(port0, port1)
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
        self.robot.set_modifier_attributes(port1, '0', '0', min_val='10', max_val='20', action='decrement')
        self.robot.remove_modifier(port1, '0', '0')

    def test_run_traffic(self):
        self.robot.reserve_ports_by_force(port0, port1)
        self.robot.load_config(port0, path.join(path.dirname(path.dirname(__file__)), 'samples', 'test_config.xpc'))
        self.robot.load_config(port1, path.join(path.dirname(path.dirname(__file__)), 'samples', 'test_config.xpc'))
        self.robot.start_capture('0')
        self.robot.clear_statistics('0', '1')
        self.robot.run_traffic_blocking()
        self.robot.start_capture('1')
        stats = self.robot.get_statistics('Port')
        self.robot.g
        print(stats)

    def test_misc_operations(self):
        print(self.robot.send_command_return(chassis, '0/0 p_comment ?'))
