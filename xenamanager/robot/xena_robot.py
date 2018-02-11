"""
Xena Robot Framework library.

@author yoram@ignissoft.com
"""

import sys
import getpass
import logging

from xenamanager.xena_app import init_xena
from xenamanager.xena_statistics_view import XenaPortsStats, XenaStreamsStats, XenaTpldsStats


class XenaRobot():
    
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    def __init__(self, user=None):
        user = user if user else getpass.getuser()
        self.logger = logging.getLogger('log')
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(logging.StreamHandler(sys.stdout))
        self.xm = init_xena(self.logger, user)

    def add_chassis(self, chassis='None', port=22611, password='xena'):
        """ Add chassis.

        XenaManager-2G -> Add Chassis.
        """
        self.xm.session.add_chassis(chassis, port, password)

    def reserve_ports(self, *locations):
        """ Reserve ports only if ports are released.
        
        If one of the ports is reserved by another user the operation will fail.
        
        :param locations: list <ip/module/port> of port locations.
        """
        self.ports = self.xm.session.reserve_ports(locations, force=False)

    def reserve_ports_by_force(self, *locations):
        """ Reserve ports forcefully even if ports are reserved by other user.
        
        :param locations: list <ip/module/port> of port locations.
        """
        self.ports = self.xm.session.reserve_ports(locations, force=True)
        
    def load_config(self, port, config_file_name):
        self.logger.info(type(port))
        if port.isdecimal():
            self.ports.values()[int(port)].load_config(config_file_name)
        else:            
            self.ports[port].load_config(config_file_name)
    
    def clear_statistics(self, *ports):
        self.xm.session.clear_stats(*ports)
    
    def start_traffic(self, *ports):
        self.xm.session.start_traffic(False, *ports)
    
    def run_traffic_blocking(self, *ports):
        self.xm.session.start_traffic(True, *ports)
        
    def get_statistics(self, view='port'):
        return _view_name_2_object[view.lower()](self.xm.session).read_stats()


_view_name_2_object = {'port': XenaPortsStats,
                       'stream': XenaStreamsStats,
                       'tpld': XenaTpldsStats}
