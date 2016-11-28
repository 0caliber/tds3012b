#!C:/prog/python24/python.exe


# --------------------------------------------------
#	Python	script	for	Capturing	Raw	Data	on	TDS2014B
#	Author:	Ilias	Alexopoulos
#	Company:	Intralot	SA
#	Date:	29	Feb	2012
#	Version	0.01
#	Using	PyVisa	&	ctypes	on	Python	2.4
#	ctypes	included	in	Python	2.5
# --------------------------------------------------
#	Version	History
#	0.10,	28/02/2012:	Initial
#	0.90,	21/06/2013: ??
# 	1.00,	07/11/2016: Added SPI Decode
# --------------------------------------------------
# http://192.168.2.19/?COMMAND=:WFMPRe?
#
# capture.py -b RS232 -l TTL -a 115200 -i Capture.csv -n 0
# capture.py -b RS232 -l TTL -a 115200 -i CaptureRS422_LVCMOS.csv -n 0
# capture.py -v -b I2C -i CaptureI2C.csv
# capture.py -v -b SPI -i CaptureSPI.csv -s 0


import re
import os, sys
import time
import getopt

# Diagnostics
import sys
import os

from TWIDecode import *
from RS232Decode import *
from SPIDecode import *
from DSOGetSamples import *
from MyPrint import *
from DataImporter import *
from VCDExporter import *

VersionNum = "0.91"
VersionDate = "2016-11-07"

VersionInfo = """
---------------------------------------------------------------------------------------------------
Script for Capturing RAW data from TDS2014 and decode them
Date: %s, Version: %s
Written	by Ilias Alexopoulos\n
---------------------------------------------------------------------------------------------------
""" % (VersionDate, VersionNum)

Usageopt = """
  usage: %s OPTIONS [-v] [-b bus] [-i visa_instr] [-l voltage level] [-f outfile] [-t delay_sec] [-k blank_lines] [-d databits] [-p parity] [-a baud] [-n polarity]
  Example: ./%s -v -b I2C -i TCPIP::10.70.130.207::INSTR -f	capture.csv -t 3\n
"""

Optionparams = """
  Options:
    -v : Verbose
    -b : Bus selection: I2C,SPI,RS232
	-l : Level selection (LVCMOS, LVTTL, CMOS, TTL, RS232, RS422U)
    -i : VISA compliant address (ie. TCPIP::10.70.130.207::INSTR) OR filename (ie. capture.csv)
    -f : File CSV appended output
    -t : Delay for acquisition (initial)
    -k : Blank lines to inject at the end of the block, default none
	-a : RS232: Baud rate (2400, 19200 etc)
	-p : RS232: Parity (N, E, O)
	-d : RS232: Data bits (6,7,8)
	-n : RS232: Polarity: 0 for positive, 1 for negative (invert)
	-s : SPI Phase/Polarity: 0:PolPha[00], 1:PolPha[01], 2:PolPha[10], 3:PolPha[11]
	-m : SPI MSB First: 0: LSB First, 1: MSBFirst
---------------------------------------------------------------------------------------------------

"""

def f_Diag():
	print(sys.executable)
	print(os.getcwd())
	print(sys.path)

def f_usage(fname):
	global VersionInfo, Optionparams, Usageopt

	v = fname.split("\\")
	name = v[len(v) - 1]
	print(VersionInfo)
	print(Usageopt % (name, name))
	print(Optionparams)


def f_DisplayI2C(twi, bytes):
	line = ""
	for b in bytes:
		line = "%s, %02X" % (line, b)

	if len(bytes) > 1:
		i2caddr = bytes[0]
		devaddr = i2caddr >> 1
		rw = i2caddr & 0x01
		labrw = 'RD' if rw else 'WR'
		line = "DevAddr: %02X, Operation: %s%s" % (devaddr, labrw, line)
		print(line)
	else:
		print("No START condition detected probably. No Data.")


###################################
#	parsing	params
###################################

#	configuration
gEnable = 0

busfname = ""
levels = 'LVCMOS'
instr = "TCPIP::192.168.2.19::INSTR"
acqdelay = 1
bus = 'I2C'
blanklines = 0
baud = 2400
polarity = 0
parity = 'N'
dbits = 8
sample_period = 964e-9
polpha = 0
msbfirst = 1
logname = 'Capture.csv'

#	Parameters	parsing
try:
	opts, args = getopt.getopt(sys.argv[1:], "v,b:,i:,f:,t:,k:, d:,l:,a:,p:,n:,s:,m:")

except    getopt.GetoptError:
	f_usage(sys.argv[0])
	sys.exit(1)

for o, a in opts:
	# print	o,	a,	opts
	if o == '-v':
		gEnable = 1
	elif o == '-b':
		bus = a
	elif o == '-l':
		levels = a
	elif o == '-i':
		instr = a
	elif o == '-t':
		acqdelay = eval(a)
	elif o == '-f':
		busfname = a
	elif o == '-k':
		blanklines = eval(a)
	elif o == '-a':
		baud = eval(a)
	elif o == '-n':
		polarity = eval(a)
	elif o == '-p':
		parity = a
	elif o == '-d':
		dbits = eval(a)
	elif o == '-s':
		polpha = eval(a)
	elif o == '-m':
		msbfirst = eval(a)
	else:    print('****	Warning:	unknown	option:	', o)

#f_Diag()
MyPrint = MyPrint(gEnable)
MyPrint.f_Print(instr)
MyPrint.f_Print(bus)
MyPrint.f_Print(busfname)
MyPrint.f_Print(levels)

if busfname == "":
	busfname = instr

imp = DataImporter(busfname, logname, gEnable)
[ch1, ch2] = imp.f_GetSamples()
sample_period = imp.f_GetTBase()
del imp

print("------------------------------------------------------------------------")

if bus == 'I2C':
	decode = TWIDecode()
	twi, bytes = decode.f_TWIDecode(levels, ch1, ch2)
	print(twi)
	f_DisplayI2C(twi, bytes)
	nch1 = 'SCL'
	nch2 = 'SDA'
	[vcd, vcdt, vcdd] = decode.f_TWIGetStream()

elif bus == 'SPI':
	print("SPI Bus Decode")
	decode = SPIDecode()
	bytes = decode.f_SPIDecode(levels, ch1, ch2, polpha, msbfirst)
	print bytes
	nch1 = 'SCLK'
	nch2 = 'MISO'
	[vcdt, vcdd] = decode.f_SPIGetStream()

elif bus == 'RS232':
	print ("RS232 Bus Decode")
	decode = RS232Decode()
	[dbin, dstat, dascii] = decode.f_RS232Decode(sample_period, levels, baud, dbits, parity, polarity, ch1, ch2)
	print (dbin)
	print (dascii)
	print (dstat)
	nch1 = 'Tx'
	nch2 = 'Rx'
	[vcdt1, vcdd1, vcdt2, vcdd2] = decode.f_RS232GetStream()

else:
	print ("Unknown bus: %s" % bus)
	nch1 = 'NA'
	nch2 = 'NA'

print ("------------------------------------------------------------------------")

myvcd = VCDExporter(logname, nch1, nch2)
if bus == 'I2C':
	myvcd.f_SaveVCD_TWI(sample_period, ch1, ch2, vcd, vcdt, vcdd)
elif bus == 'SPI':
	myvcd.f_SaveVCD_SPI(sample_period, ch1, ch2, vcdt, vcdd)
	pass
elif bus == 'RS232':
	print len(vcdt1), len(vcdt2), len(vcdd1), len(vcdd2)
	myvcd.f_SaveVCD_RS232(sample_period, ch1, ch2, vcdt1, vcdd1, vcdt2, vcdd2)
	pass
else:
	pass
