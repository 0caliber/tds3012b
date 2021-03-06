# License conditions are given in LICENSE.TXT
# This code is licnesed under the MIT License 
# Copyright (c) 2017 Ilialex Research Lab
# www.ilialex.gr, blog.ilialex.gr


import os, sys
import re
from DSOGetSamples import *

class DataImporter:
	def __init__(self, visarsc, fname, logname, gEnable):

		self.gEnable = gEnable
		self.logfname = logname
		
		# VISA addresses have ::
		length = len(fname.split('::'))
		
		if length == 1:
			print ("Import File: ", fname)
			ch1, ch2, tbase = self.f_FileGet(fname)
		else:
			print ("Import from DSO: ", fname, length)
			ch1, ch2, tbase = self.f_DSOGet(visarsc, fname)
		
		print ("TBase ", tbase)
		self.ch1 = ch1
		self.ch2 = ch2
		self.tbase = tbase
	
	def f_GetSamples(self):
		return self.ch1, self.ch2
		
	def f_GetTBase(self):
		return self.tbase
		
	def f_FileGet(self, fname):

		chan1 = []
		chan2 = []
		try:
			fi = open(fname, 'r')
		except    IOError:
			print("Can't open Input file %s for Writing."    %    fname)
			return chan1, chan2
			

		try:
			hdrline = fi.readline()
			v = hdrline.split(';')
			tbase = eval(v[8])
		except:
			tbase = 2E-7 # random set
			pass
			
		for line in fi.readlines():
			v = re.split(';|,',line)
			chan1.append(eval(v[0]))
			chan2.append(eval(v[1]))
			
		fi.close()
		
		return chan1, chan2, tbase
		pass
	
	def f_DSOGet(self, visarsc, instr):
		dso = DSOGetSamples(visarsc, instr, self.gEnable)
		
		chan1 = []
		chan2 = []
		tbase = 1
		
		try:
			fo = open(self.logfname,    'w')
		except    IOError:
			print("Can't open Log file %s for Writing."    %self.logfname)
			del dso
			return [chan1, chan2, tbase]
			
		try:
			dso.f_Setup()
			[wfmhdr, data] = dso.f_GetChannel(1)
			chan1 = dso.f_ScaleVolt(wfmhdr, data)
			[wfmhdr, data] = dso.f_GetChannel(2)
			chan2 = dso.f_ScaleVolt(wfmhdr, data)
			tbase = dso.f_TimeBase(wfmhdr)
			print ("TBase: ", tbase)
		except IOError:
			fo.close()
			del dso
			return [chan1, chan2]

		length = len(chan1)

		fo.write(wfmhdr)
		for idx in range(1, length):
			volt1    = chan1[idx]
			volt2    = chan2[idx]
			line    = "%3.3f;%3.3f\n" %(volt1, volt2)
			fo.write(line)
				
			
		print ("Raw Table Capture Success!!")
		fo.close()
		del dso
	
		return [chan1, chan2, tbase]
		pass
        
        