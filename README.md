# README #

[TOC]

## Introduction
This is about a script I use to gather and decode serial data from my Tektronix TDS2014B (two channel) Digital Oscilloscope.
The oscilloscope is connected to gather TWI, SPI or RS232 data and the script acquires and decodes to a human readable format.

The output provided is:

* ASCII decode on command line
* CSV file to check on Excel or any other compatible tool
* Recently added VCD format to use with GTKWave

This is a command line tool, without any GUI.

## What is this repository for? ##

### Quick Summary ###
This is the development repository of the script with all sources needed to run or modify the tool.
In addition the modules of this script were developed with TDD methodology.

### Version ###
Check repo for latest version

### Tutorials ###
NA Yet

### How do I get set up? ###

* Prerequisites
* Summary of set up

See Dependencies below.


Go ahead and try:

```
$ hg clone https://bitbucket.org/ialexo/tds3012 tds3012
```

This will clone this repository to tds3012 folder in your system.



### Running The Script ###

Example Command Line Executions:

RS232: 
```
capture.py -b RS232 -l TTL -a 115200 -I CaptureRS232_LVCMOS.csv -n 0
```
TWI: 
```
capture.py -v -b I2C -I CaptureI2C.csv
```

SPI: 
```
capture.py -b SPI -l LVCMOS -s 0 --visa -I TCPIP::192.168.2.19::INSTR
```

The first two examples use an already captured file, while the last command shows an example of direct instrument acquisition.
## Dependencies: ##

You will need the following to be able to run the script.

* Python Interpreter (code is written in 2.7 generation) (https://www.python.org/downloads/ ) 
* VISA Libraries (Either from National Instruments [NIVISA](https://www.ni.com/visa/) or from Tektronix [TekVISA](http://uk.tek.com/oscilloscope/tds7054-software))
* PyVISA module [PyVISA](https://pyvisa.readthedocs.io/en/stable/)

License:
This code is licensed under the MIT License.
See License file.

## Contribution guidelines ##

* Proposing functionality
* Pull back improvements
* Report issues

### Who do I talk to? ###

* Repo owner or admin
[Ilias](https://bitbucket.org/ialexo/)