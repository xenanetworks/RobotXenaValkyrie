
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

Download xenamanager/robot/xena_robot.py to some folder and add the download folder to the Robot search path.

Getting started
"""""""""""""""
Code samples are available under xenamanager.samples.

Documentation
"""""""""""""
http://robotxenamanager.readthedocs.io/en/latest/
Under construction...

Contact
"""""""
Feel free to contact me with any question or feature request at yoram@ignissoft.com
