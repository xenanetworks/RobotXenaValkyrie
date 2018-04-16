"""
Base class for all traffic generators tests.

@author yoram@ignissoft.com
"""

import unittest
from xenamanager.robot.xena_robot import XenaRobot

chassis='176.22.65.114'


class RobotTest(unittest.TestCase):
    
    def setUp(self):
        self.robot = XenaRobot()
        self.robot.add_chassis(chassis)
        
    def tearDown(self):
        pass
    
    def hello_world(self):
        pass
