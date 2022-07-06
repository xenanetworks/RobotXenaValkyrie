
🔴 **IMPORTANT** 🔴 **RobotXenaValkyrie is now End-of-Life. It will be reborn under Xena OpenAutomation.**



This package implements Python Robot framework API for Xena traffic generator.

Functionality
"""""""""""""
The current version supports the following test flow:
	Load/Build configuration -> Change configuration -> Start/Stop traffic -> Get statistics/capture
Supported operations:
	- Login, connect to chassis and reserve ports
	- Load existing configuration file
	- Build configuration from scratch
	- Get/set attributes
	- Start/Stop - transmit, capture
	- Statistics - ports, streams (end to ends) and TPLDs
	- Capture - get captured packets
	- Release ports and disconnect

Installation
""""""""""""
This version does not support pip install.

Download xenavalkyrie_robot/robot/xena_robot.py to some folder and add the download folder to the Robot search path.

Getting started
"""""""""""""""
Code samples are available under xenavalkyrie_robot.samples.

Assuming you copied the xena_robot under xenavalkyrie package directory then you can import the library as following:

Start over CLI API:
Library    xenavalkyrie.xena_robot.XenaRobot    socket    *user_name*

Start over REST API:
Library    xenavalkyrie.xena_robot.XenaRobot    rest    *user_name*  *server_ip*    *optipnal_server_tcp_poty*   

Contact
"""""""
Feel free to contact me with any question or feature request at yoram@ignissoft.com

Known Issues
============
- Get packet header supports only Ethernet/Vlan/IP[v6], no higher layers.
