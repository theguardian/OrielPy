# OrielPy

This program shows "at-a-glance" hardware and system information for your Linux server through any web browser, 
including variants such as: Ubuntu, QNAP appliances, RaspberryPi, etc; without the need to login to terminal.  OrielPy
is based on Oriel-Window and ported for the CherryPy framework.  It now has the ability to send a tweet if
the server is experiencing user-defined off-nominal conditions.
 
# Screenshots
![ScreenShot](https://raw.github.com/theguardian/OrielPy/master/data/images/screenshots/qnap_interface.jpg)

## Features

1. CPU Type, Max Speed & Cache Values
2. Internal HDD Status (R/W, Idle, etc)
3. External HDD Status (R/W, Idle, etc)
4. Network Status (Active / Inactive)
5. Per-Core CPU Load Percentage
6. RAM (Free / Total)
7. Swap Memory (Free / Total)
8. CPU Temperature & Fan Speed (When Pseudofile Exists)
9. System Temperature & Fan Speed (When Pseudofile Exists)
10. Network Tx/Rx Rates
11. Disk Per-Volume Memory (Format / Free / Total)
12. Monitor Actively Running Processes
13. Monitor User-Defined Log Files
14. [Optional] Tweet messages regarding off-nominal performance on a set schedule

## Prerequisites
1. Currently works on Linux systems with Python installed
2. Requires installation of psutil (https://code.google.com/p/psutil/)
3. lm-sensors package is required to generate pseudofiles on Ubuntu systems
* Note that psutil package required is NOT the same as apt-get repository "psutils". Right now, psutil must be downloaded and installed manually with "python setup.py install"
* If installation of psutil results in "error: command 'gcc' failed with exit status 1", you also need to install python development headers with "sudo apt-get install python-dev"

## Use
1. Git clone onto your Linux Server
2. cd into OrielPy
3. >> python OrielPy.py
4. Go to http://your.ip.address:5151

## Advanced Use
1. Click "restart" to run as daemon
2. Click "Configuration" to configure specifics for your particular system (pseudofiles, ranges, log files, etc)

## Disclaimers

This has been tested on:
1. QNAP TS-509 with 3.7, 3.8, 4.0, 4.1 firmwares.  
2. Raspberry Pi, Rev. B
3. Ubuntu Desktop/Server 13.10

No warranty implied or provided.  
Feel free to request new features or report bugs.  
OrielPy is licensed under GNU v2.0.