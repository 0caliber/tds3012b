# License conditions are given in LICENSE.TXT
# This code is licnesed under the MIT License 
# Copyright (c) 2017 Ilialex Research Lab
# www.ilialex.gr, blog.ilialex.gr
#

import os, sys
import re
import time


class VCDExporter:
	def __init__(self, logname, namech1, namech2, gEnable=1):
		self.gEnable = gEnable
		self.VCDfname = logname.replace(".csv", ".vcd")

		t = time
		dt = time.asctime()
		self.hdr = "$date\n %s\n$end\n$version\n CAPTURE DSO \n$end" % dt
		self.namech1 = namech1
		self.namech2 = namech2


	def f_SaveVCD_TWI(self, tbase, ch1, ch2, stream, tim, bitstream):
		#print len(ch1), len(ch2), len(stream), len(tim), len(bitstream)
		busname = 'TWI'

		try:
			fo = open(self.VCDfname, 'w')
		except    IOError:
			print    "Can't open VCD Log file %s for Writing." % self.VCDfname


		ts = "\n$timescale\n %12.9f s \n$end\n" % tbase
		sig = "$var real 1 a %s $end\n$var real 1 b %s $end\n" %(self.namech1, self.namech2)

		if len(stream) > 0:
			sig = sig + '$var wire 16 c %s $end\n' %busname

		if len(tim) > 0:
			sig = sig + '$var wire 8 d pTWI $end\n'

		fo.write(self.hdr)
		fo.write(ts)
		fo.write(sig)
		fo.write("$enddefinitions $end\n")

		currtime = 0
		pd1 = 0
		pd2 = 0
		ps1 = 0
		tidx = 0
		idx = 0
		print len(tim), len(bitstream), len(stream)
		for d1, d2 in zip(ch1, ch2):
			try:
				s1 = stream[tidx]
			except IndexError:
				s1 = 0
				tim.append(0)

			if pd1 != d1 or pd2 != d2 or ps1 != s1 or currtime == tim[tidx]:
				fo.write("#%f\n" % currtime)
				if pd1 != d1:
					fo.write("r%.16g a\n" % d1)
				if pd2 != d2:
					fo.write("r%.16g b\n" % d2)
				#if ps1 != s1:
				if currtime == tim[tidx]:
					#fo.write("b%s c\n" %int(bin(ord(s1))[2:]))
					#print idx, ps1, s1, bitstream[idx]
					#if ps1 == 'S' or ps1 == 'A' or ps1 == 'N' or ps1 == 'R' or ps1 == 'X':
					try:
						if s1 == 'D':
							fo.write("b%s d\n" %bin(bitstream[idx])[2:])
							#print bitstream[idx]
							asc = hex(bitstream[idx]).upper()
							if len(asc) == 3:
								nib1 = format(ord('0'), '08b')
								nib2 = format(ord(asc[2:3]), '08b')
							else:
								nib1= format(ord(asc[2:3]), '08b')
								nib2 = format(ord(asc[3:4]), '08b')
							#print nib1, nib2
							fo.write("b%s%s c\n" %(nib1, nib2))
							idx += 1
							if len(bitstream)-1 < idx:
								idx = len(bitstream)-1
							#print currtime, idx,bitstream[idx]
						elif s1 == 'S' or s1 == 'P' or s1 == 'A' or s1 == 'N' or s1 == 'X' or s1 == 'R':
							fo.write("b%s c\n" % int(bin(ord(s1))[2:]))
						else:
							#fo.write("b%s c\n" %int(bin(ord(s1))[2:]))
							pass
					except IndexError:
						pass
						
					tidx += 1
					if tidx > len(tim) - 1:
						tidx = len(tim) - 1



			pd1 = d1
			pd2 = d2
			ps1 = s1
			currtime += 1

		fo.close()


	def f_SaveVCD_SPI(self, tbase, ch1, ch2, tim=[], bitstream=[]):
		busname = 'SPI'
		try:
			fo = open(self.VCDfname, 'w')
		except    IOError:
			print    "Can't open VCD Log file %s for Writing." % self.VCDfname

		ts = "\n$timescale\n %12.9f s \n$end\n" % tbase
		#print tbase
		sig = "$var real 1 a %s $end\n$var real 1 b %s $end\n" % (self.namech1, self.namech2)

		if len(tim) > 0:
			sig = sig + '$var wire 8 c %s $end\n' % busname

		fo.write(self.hdr)
		fo.write(ts)
		fo.write(sig)
		fo.write("$enddefinitions $end\n")

		currtime = 0
		ctf = 0
		pd1 = 0
		pd2 = 0
		ps1 = 0
		idx = 0
		s1 = 0
		#print bitstream
		for d1, d2 in zip(ch1, ch2):

			if pd1 != d1 or pd2 != d2 or currtime == tim[idx]:
				fo.write("#%d\n" % currtime)
				if pd1 != d1:
					fo.write("r%.16g a\n" % d1)
				if pd2 != d2:
					fo.write("r%.16g b\n" % d2)

				if currtime == tim[idx]:
					s1 = bitstream[idx]
					idx += 1
					if len(bitstream) - 1 < idx:
						idx = len(bitstream) - 1
					#print s1
					fo.write("b%s c\n" %int(bin(s1)[2:]))

			pd1 = d1
			pd2 = d2
			ps1 = s1
			currtime += 1
			ctf += tbase

		fo.close()

	def f_SaveVCD_RS232(self, tbase, ch1, ch2, tim1, bitstream1, tim2, bitstream2):
		#print len(ch1), len(ch2), len(stream), len(tim), len(bitstream)
		busname = 'RS232'

		try:
			fo = open(self.VCDfname, 'w')
		except    IOError:
			print    "Can't open VCD Log file %s for Writing." % self.VCDfname

		ts = "\n$timescale\n %12.9f s \n$end\n" % tbase
		sig = "$var real 1 a %s $end\n$var real 1 b %s $end\n" %(self.namech1, self.namech2)

		if len(tim1) > 0:
			sig = sig + '$var wire 16 c %s_Tx $end\n' %busname

		if len(tim2) > 0:
			sig = sig + '$var wire 16 d %s_Rx $end\n' % busname
		else:
			tim2.append(0)
			tim2.append(0)


		fo.write(self.hdr)
		fo.write(ts)
		fo.write(sig)
		fo.write("$enddefinitions $end\n")

		currtime = 0
		pd1 = 0
		pd2 = 0
		idx1 = 0
		idx2 = 0
		s1 = 0
		s2 = 0
		for d1, d2 in zip(ch1, ch2):
			if pd1 != d1 or pd2 != d2 or currtime == tim1[idx1] or currtime == tim2[idx2]:
				fo.write("#%f\n" % currtime)
				if pd1 != d1:
					fo.write("r%.16g a\n" % d1)
				if pd2 != d2:
					fo.write("r%.16g b\n" % d2)

				if 	currtime == tim1[idx1] and len(tim1) > 5:
					s1 = bitstream1[idx1]
					[idx1, line1, line2] = self.f_RS232_DataProc('c', 'e', idx1, bitstream1)
					if line1 != "":
						fo.write(line1)
					if line2 != "":
						fo.write(line2)

				if currtime == tim2[idx2] and len(tim2) > 5:
					s2 = bitstream2[idx2]
					[idx2, line1, line2] = self.f_RS232_DataProc('d', 'f', idx2, bitstream2)
					if line1 != "":
						fo.write(line1)
					if line2 != "":
						fo.write(line2)

			pd1 = d1
			pd2 = d2

			currtime += 1

		fo.close()


	def f_RS232_DataProc(self, sigdes1, sigdes2,  idx, bitstream):
		s1 = bitstream[idx]
		#print s1
		line1 = ""
		line2 = ""
		if s1 == 'S' or s1 == 'P' or s1 == 'O' or s1 == 'N' or s1 == 'X' or s1 == 'E' or s1 == 'R':
			line1 = "b%s c\n" % int(bin(ord(s1))[2:])
		else:
			s1 = int(s1, 16)
			line1 = "b%s %c\n" %(bin(s1)[2:], sigdes2)
			asc = hex(s1).upper()
			if len(asc) == 3:
				nib1 = format(ord('0'), '08b')
				nib2 = format(ord(asc[2:3]), '08b')
			else:
				nib1 = format(ord(asc[2:3]), '08b')
				nib2 = format(ord(asc[3:4]), '08b')
			# print nib1, nib2
			line2 = "b%s%s %c\n" % (nib1, nib2, sigdes1)
			pass

		ps1 = s1
		idx += 1
		if len(bitstream) - 1 < idx:
			idx = len(bitstream) - 1

		return idx, line1, line2