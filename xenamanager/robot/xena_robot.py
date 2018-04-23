"""
Xena Robot Framework library.

This module should contain ONLY wrapper methods. All logic should be implemented inside xenamanager package.
Wrappers should follow:
- short and meaningful name
- minimal number of parameters and with simple order
- its better to create new wrapper than complicating parameters or add logic
- try to avoid default values

Limitations:
- no multi chassis support
- no multi-line support

@author yoram@ignissoft.com
"""

from __future__ import unicode_literals
import sys
import os
import getpass
import logging
import re
from importlib import import_module
from collections import OrderedDict

from xenamanager.xena_app import init_xena
from xenamanager.xena_stream import XenaModifierType, XenaModifierAction
from xenamanager.xena_statistics_view import XenaPortsStats, XenaStreamsStats, XenaTpldsStats

__version__ = '0.2'
ROBOT_LIBRARY_DOC_FORMAT = 'reST'

python_path = os.path.dirname(sys.executable)
site_packages_path = os.path.join(python_path, 'Lib', 'site-packages')
pypacker_path = os.path.join(site_packages_path, 'pypacker')


class XenaRobot():

    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    #
    # Session management.
    #

    def __init__(self, user=None):
        user = user if user else getpass.getuser()
        self.logger = logging.getLogger('log')
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(logging.StreamHandler(sys.stdout))
        self.xm = init_xena(self.logger, user)

    def add_chassis(self, chassis='None', port=22611, password='xena'):
        """ Add chassis.

        :param chassis: chassis IP address
        :param port: chassis port number
        :param password: chassis password
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

    def release_ports(self, *ports):
        """ Reserve list of ports.

        :param ports: ports indices (zero based) or ports locations as used in reserve command. If empty - clear stats
                      for all ports.
        """
        for port in self._port_names_or_indices_to_objects(*ports):
            port.release()

    def load_config(self, port, config_file_name):
        """ Load configuration file onto port.

        :param port: port index (zero based) or port location as used in reserve command.
        :param config_file_name: full path to configuration file name (xpc).
        """
        self._port_name_or_index_to_object(port).load_config(config_file_name)

    def save_config(self, port, config_file_name):
        """ Save configuration file from port.

        :param port: port index (zero based) or port location as used in reserve command.
        :param config_file_name: full path to configuration file name (xpc).
        """
        self._port_name_or_index_to_object(port).save_config(config_file_name)

    def clear_statistics(self, *ports):
        """ Clear statistics for list of ports.

        :param ports: ports indices (zero based) or ports locations as used in reserve command. If empty - clear stats
                      for all ports.
        """
        self.xm.session.clear_stats(*self._port_names_or_indices_to_objects(*ports))

    def start_traffic(self, *ports):
        """ Start traffic on list of ports and return immediately.

        :param ports: ports indices (zero based) or ports locations as used in reserve command. If empty - start
                      traffic on all ports.
        """
        self.xm.session.start_traffic(False, **self._port_names_or_indices_to_objects(*ports))

    def run_traffic_blocking(self, *ports):
        """ Start traffic on list of ports and wait until all traffic is finished.

        :param ports: ports indices (zero based) or ports locations as used in reserve command. If empty - start
                      traffic on all ports.
        """
        self.xm.session.start_traffic(True, **self._port_names_or_indices_to_objects(*ports))

    def stop_traffic(self, *ports):
        """ Stop traffic on list of ports.

        :param ports: ports indices (zero based) or ports locations as used in reserve command. If empty - stop
                      traffic on all ports.
        """
        self.xm.session.stop_traffic(**self._port_names_or_indices_to_objects(*ports))

    def start_capture(self, *ports):
        """ Start capture on list of ports.

        :param ports: ports indices (zero based) or ports locations as used in reserve command. If empty - start
                      capture on all ports.
        """
        self.xm.session.start_capture(**self._port_names_or_indices_to_objects(*ports))

    def stop_capture(self, *ports):
        """ Stop capture on list of ports.

        :param ports: ports indices (zero based) or ports locations as used in reserve command. If empty - stop
                      capture on all ports.
        """
        self.xm.session.stop_capture(False, **self._port_names_or_indices_to_objects(*ports))

    def get_statistics(self, view='port'):
        """ Get statistics for all ports/streams/TPLDs.

        :param view: port/stream/tpld.
        :return: dictionary of requested statistics.
        """
        stats = _view_name_2_object[view.lower()](self.xm.session).read_stats()
        return {k.name: v for k, v in stats.items()}

    #
    # Ports
    #

    def reset_port(self, port):
        """ Reset port-level parameters to standard values, and delete all streams, filters, capture, and dataset
            definitions.

        :param port: port index (zero based) or port location as used in reserve command.
        """
        self._port_name_or_index_to_object(port).reset()

    def get_port_attribute(self, port, attribute):
        """ Get port attribute.

        :param port: port index (zero based) or port location as used in reserve command.
        :param attribute: attribute name.
        :return: attribute value.
        :rtype: str
        """
        return self._port_name_or_index_to_object(port).get_attribute(attribute)

    def set_port_attributes(self, port, **attributes):
        """ Set port attribute.

        :param port: port index (zero based) or port location as used in reserve command.
        :param attributes: dictionary of {attribute: value} to set
        """
        return self._port_name_or_index_to_object(port).set_attributes(**attributes)

    def exec_port_command(self, port, command, *arguments):
        """ Execute any port command and return the returned value.

        :param port: port index (zero based) or port location as used in reserve command.
        :param command: command to execute.
        :param arguments: optional list of command arguments.
        """
        return self._port_name_or_index_to_object(port).send_command_return(command, *arguments)

    #
    # Streams.
    #

    def add_stream(self, port, name=None):
        """ Add stream. The newly created stream will have unique TPLD.

        :param port: port index (zero based) or port location as used in reserve command.
        :param name: stream name.
        :return: stream index.
        """
        stream = self._port_name_or_index_to_object(port).add_stream(name)
        return stream.id

    def remove_stream(self, port, stream):
        """ Remove stream.

        :param port: port index (zero based) or port location as used in reserve command.
        :param stream: stream index (zero based) or stream name.
        """
        index = self._stream_name_or_index_to_object(port, stream).id
        self._port_name_or_index_to_object(port).remove_stream(index)

    def get_stream_attribute(self, port, stream, attribute):
        """ Get port attribute.

        :param port: port index (zero based) or port location as used in reserve command.
        :param stream: stream index (zero based) or stream name.
        :param attribute: attribute name.
        :return: attribute value.
        :rtype: str
        """
        return self._stream_name_or_index_to_object(port, stream).get_attribute(attribute)

    def set_stream_attributes(self, port, stream, **attributes):
        """ Set stream attribute.

        :param port: port index (zero based) or port location as used in reserve command.
        :param stream: stream index (zero based) or stream name.
        :param attributes: dictionary of {attribute: value} to set
        """
        return self._stream_name_or_index_to_object(port, stream).set_attributes(**attributes)

    def exec_stream_command(self, port, stream, command, *arguments):
        """ Execute any stream command and return the returned value.

        :param port: port index (zero based) or port location as used in reserve command.
        :param stream: stream index (zero based) or stream name.
        :param command: command to execute.
        :param arguments: optional list of command arguments.
        """
        return self._stream_name_or_index_to_object(port, stream).send_command_return(command, *arguments)

    #
    # Packet headers.
    #

    def get_packet(self, port, stream):
        """ Get packet as a printable string.

        :param port: port index (zero based) or port location as used in reserve command.
        :param stream: stream index (zero based) or stream name.
        :return: string representation of stream packet.
        """
        return self._stream_name_or_index_to_object(port, stream).get_packet_headers()

    def get_packet_header(self, port, stream, header):
        """ Get packet header.

        :param port: port index (zero based) or port location as used in reserve command.
        :param stream: stream index (zero based) or stream name.
        :param header: requested packet header.
        :return: dictionary of <field: value>.
        :rtype: dict of (str, str)
        """

        header_body = self._get_packet_header(port, stream, header)
        fields_str = self._get_packet_header(port, stream, header)._summarize()
        fields = OrderedDict()
        for field_value in re.sub('vlan=\[.*\], ', '', re.findall('\((.*)\)', fields_str)[0]).split(','):
            field, value = field_value.strip().split('=')
            fields[field] = value
            try:
                fields[field + '_s'] = getattr(header_body, field + '_s')
            except Exception as _:
                pass
        return fields

    def add_packet_headers(self, port, stream, *headers):
        """ Add packet headers.

        All headers will be added with some default values (not the same as Xena Manager default) and it is the test
        responsibility to set them.

        :param port: port index (zero based) or port location as used in reserve command.
        :param stream: stream index (zero based) or stream name.
        :param headers: list of header names to add (vlan, ip, ip6, tcp, etc.).
        """

        packet_headers = self._stream_name_or_index_to_object(port, stream).get_packet_headers()
        for header in headers:
            if header.lower() == 'vlan':
                header_py = 'ethernet.py'
                header_class = 'Dot1Q'
            else:
                header_py = header.lower() + '.py'
                header_class = header.upper()
            for dirpath, _, filenames in os.walk(pypacker_path):
                if header_py in filenames:
                    module_name = dirpath[len(site_packages_path) + 1:]
            header_module = import_module(module_name.replace(os.path.sep, '.') + '.' + header_py[:-3])
            header_object = getattr(header_module, header_class)()
            if header.lower() == 'vlan':
                packet_headers.vlan.append(header_object)
            else:
                packet_headers += header_object
        self._stream_name_or_index_to_object(port, stream).set_packet_headers(packet_headers)

    def set_packet_header_fields(self, port, stream, header, **fields):
        """ Set packet header fields.

        :param port: port index (zero based) or port location as used in reserve command.
        :param stream: stream index (zero based) or stream name.
        :param header: packet header.
        :param fields: dictionary of <field, value> to set.
        :type fields: dict of (str, str)
        """

        print('header = ' + header)
        headers = self._stream_name_or_index_to_object(port, stream).get_packet_headers()
        header_body = self._get_packet_header(header=header, headers=headers)
        for field, value in fields.items():
            setattr(header_body, field, int(value) if unicode(value).isdecimal() else value)
        self._stream_name_or_index_to_object(port, stream).set_packet_headers(headers)

    #
    # Modifiers.
    #

    def add_modifier(self, port, stream, position, modifier_type='standard'):
        """ Add packet modifier.

        :param port: port index (zero based) or port location as used in reserve command.
        :param stream: stream index (zero based) or stream name.
        :param position: requested packet modifier position.
        :param modifier_type: standard/extended
        """
        self._stream_name_or_index_to_object(port, stream).add_modifier(XenaModifierType[modifier_type.lower()],
                                                                        position=int(position))

    def remove_modifier(self, port, stream, position):
        """ Add packet modifier.

        :param port: port index (zero based) or port location as used in reserve command.
        :param stream: stream index (zero based) or stream name.
        :param position: requested packet modifier position.
        """
        self._stream_name_or_index_to_object(port, stream).remove_modifier(int(position))

    def get_modifier(self, port, stream, position):
        """ Get packet modifier attributes.

        :param port: port index (zero based) or port location as used in reserve command.
        :param stream: stream index (zero based) or stream name.
        :param position: requested packet modifier position.
        :return: dictionary of <field: value>.
        :rtype: dict of (str, str)
        """

        modifier = self._stream_name_or_index_to_object(port, stream).modifiers[int(position)]
        return {'mask': modifier.mask,
                'action': modifier.action,
                'repeat': modifier.repeat,
                'min_val': modifier.min_val,
                'step': modifier.step,
                'max_val': modifier.max_val}

    def set_modifier_attributes(self, port, stream, position, **attributes):
        """ Set packet modifier attributes.

        :param port: port index (zero based) or port location as used in reserve command.
        :param stream: stream index (zero based) or stream name.
        :param position: requested packet modifier position.
        :param attributes: dictionary of {attribute: value} to set
        """

        modifier = self._stream_name_or_index_to_object(port, stream).modifiers[int(position)]
        for attribute, value in attributes.items():
            if attribute.lower() == 'action':
                setattr(modifier, attribute.lower(), XenaModifierAction[value.lower()])
            else:
                setattr(modifier, attribute.lower(), value.lower())

    #
    # Basic 'back-door' commands.
    #

    def exec_command(self, command):
        return self.xm.session.chassis_list.values()[0].api.sendQuery(command)

    #
    # Private methods.
    #

    def _port_names_or_indices_to_objects(self, *names_or_indices):
        """
        :rtype: list of (xenamanager.xena_port.XenaPort)
        """
        return [self._port_name_or_index_to_object(n) for n in names_or_indices]

    def _port_name_or_index_to_object(self, name_or_index):
        """
        :rtype: xenamanager.xena_port.XenaPort
        """
        return self.ports.values()[int(name_or_index)] if name_or_index.isdecimal() else self.ports[name_or_index]

    def _stream_name_or_index_to_object(self, port, name_or_index):
        """
        :rtype: xenamanager.xena_port.XenaPort
        """
        if name_or_index.isdecimal():
            return self._port_name_or_index_to_object(port).streams[int(name_or_index)]
        else:
            for stream in self._port_name_or_index_to_object(port).streams.values():
                if stream.name == name_or_index:
                    return stream

    def _get_packet_header(self, port=None, stream=None, header=None, headers=None):
        headers = headers if headers else self._stream_name_or_index_to_object(port, stream).get_packet_headers()
        if header.lower() == 'ethernet':
            header_body = headers
        elif header.lower().startswith('vlan'):
            header_body = headers.vlan[int(re.findall('vlan\[([\d])\]', header.lower())[0])]
        else:
            header_body = getattr(headers, header.lower())
        return header_body


_view_name_2_object = {'port': XenaPortsStats,
                       'stream': XenaStreamsStats,
                       'tpld': XenaTpldsStats}
