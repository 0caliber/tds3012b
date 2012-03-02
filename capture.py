#!C:/prog/python24/python.exe


#--------------------------------------------------
#	Python	script	for	Capturing	Raw	Data	on	TDS2014B
#	Author:	Ilias	Alexopoulos
#	Company:	Intralot	SA
#	Date:	29	Feb	2012
#	Version	0.01
#	Using	PyVisa	&	ctypes	on	Python	2.4
#	ctypes	included	in	Python	2.5
#--------------------------------------------------
#	Version	History
#	0.10,	28/02/2012:	Initial
#--------------------------------------------------
# http://192.168.2.19/?COMMAND=:WFMPRe?


import	re
import	os,	sys
import	time
import	getopt

from TWIDecode import *
from DSOGetSamples import *
from MyPrint import *
from DataImporter import *



def	f_usage(name):
	global	version,	vdate,	maxlang

	print	"-----------------------------------------------------------------------------"
	print	"	Script	for	capturing	RAW	Data	from	TDS2014	and	decode	them"
	print	"	Version",	version,	",	",	vdate
	print	"	Written	by	Ilias	Alexopoulos,	Intralot	SA\n"
	print	"	usage:	%s	OPTIONS	[-v]	[-b	bus]	[-i	visa_instr]	[-f	outfile]	[-t	delay_sec]	[-d	blank_lines]\n"	%	name
	print	"		Example:	./%s	-v	-b	I2C	-i	TCPIP::10.70.130.207::INSTR	-f	capture.csv	-t	3\n"	%	name
	print	"	Options:	"
	print	"	-v	:	Verbose"
	print	"	-b	:	Bus	selection:	I2C,	SPI,	RS232"
	print	"	-i	:	VISA	copliant	address"
	print	"	-f	:	File	CSV	appended	output"
	print	"	-t	:	Delay	for	acquisition	(initial)"
	print	"	-d	:	Blank	lines	to	inject	at	the	end	of	the	block,	default	none"	
	print	"-----------------------------------------------------------------------------"


###################################
#	parsing	params
###################################

#	configuration
version	=	"V0.12"
vdate	=	"01/03/2012"
gEnable	=	0

busfname = ""
instr = "TCPIP::192.168.2.19::INSTR"
acqdelay = 1
bus = 2
blanklines = 0

#	Parameters	parsing
try:
	opts, args = getopt.getopt(sys.argv[1:], "v,b:,i:,f:,t:,d:")

except	getopt.GetoptError:
	f_usage(sys.argv[0])
	sys.exit(1)

for	o,	a	in	opts:
	#print	o,	a,	opts
	if	o	==	'-v':	gEnable	=	1
	elif	o	==	'-b':	bus	=	a
	elif	o	==	'-i':	instr	=	a
	elif	o	==	'-t':	acqdelay	=	eval(a)
	elif	o	==	'-f':	busfname	=	a	
	elif	o	==	'-d':	blanklines	=	eval(a)
	else:	print	'****	Warning:	unknown	option:	',	o


MyPrint = MyPrint(gEnable)

MyPrint.f_Print(instr)
MyPrint.f_Print(bus)
MyPrint.f_Print(busfname)

if busfname == "":
	busfname = instr

imp = DataImporter(busfname, 'Capture.csv', gEnable)	
[ch1, ch2] = imp.f_GetSamples() 
del imp

decode = TWIDecode()
twi, bytes = decode.f_TWIDecode('LVCMOS', ch1, ch2)
print twi
line = ""
for b in bytes:
	line = "%s, %02X" %(line, b)

if len(bytes) > 1:
	i2caddr = bytes[0]
	devaddr = i2caddr >> 1
	rw = i2caddr &	0x01
	labrw = 'RD' if rw else 'WR'
	line = "DevAddr: %02X, Operation: %s%s" %(devaddr, labrw, line)
	print line	
else:
	print "No START condition detected probably. No Data."
