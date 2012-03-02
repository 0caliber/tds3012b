
import	os,	sys
from DSOGetSamples import *

class DataImporter:
	def __init__(self, fname, logname, gEnable):

		self.gEnable = gEnable
		self.logfname = logname
		
		# VISA addresses have ::
		length = len(fname.split('::'))
		
		if length == 1:
			print "Import File: ", fname
			ch1, ch2 = self.f_FileGet(fname)
		else:
			print "Import from DSO: ", fname
			ch1, ch2 = self.f_DSOGet(fname)
		
		self.ch1 = ch1
		self.ch2 = ch2
	
	def f_GetSamples(self):
		return self.ch1, self.ch2
		
	
	def f_FileGet(self, fname):

		chan1 = []
		chan2 = []
		try:
			fi = open(fname, 'r')
		except	IOError:
			print	"Can't open Input file %s for Writing."	%	fname	
			return chan1, chan2
			

		for line in fi.readlines():
			v = line.split(",")
			chan1.append(eval(v[0]))
			chan2.append(eval(v[1]))
			
		fi.close()
		
		return chan1, chan2
		pass
	
	def f_DSOGet(self, instr):
		dso = DSOGetSamples(instr, self.gEnable)
		
		chan1 = []
		chan2 = []
		
		try:
			fo = open(self.logfname,	'w')
		except	IOError:
			print	"Can't open Log file %s for Writing."	%	busfname	
			del dso
			return [chan1, chan2]
			
		try:
			dso.f_Setup()
			[wfmhdr, data] = dso.f_GetChannel(1)
			chan1 = dso.f_ScaleVolt(wfmhdr, data)
			[wfmhdr, data] = dso.f_GetChannel(2)
			chan2 = dso.f_ScaleVolt(wfmhdr, data)
		except IOError:
			fo.close()
			del dso
			return [chan1, chan2]

		length = len(chan1)


		for idx in range(1, length):
			volt1	= chan1[idx]
			volt2	= chan2[idx]
			line	= "%3.3f, %3.3f\n" %(volt1,	volt2)
			fo.write(line)
				
			
		print	"Raw Table Capture Success!!"	
		fo.close()
		del dso
	
		return [chan1, chan2]
		pass
		
		