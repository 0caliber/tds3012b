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


		ts = "\n$timescale\n %f s \n$end\n" % tbase
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
		idx = 0
		for d1, d2, s1 in zip(ch1, ch2, stream):
			if pd1 != d1 or pd2 != d2 or ps1 != s1 or currtime == tim[idx]:
				fo.write("#%f\n" % currtime)
				if pd1 != d1:
					fo.write("r%.16g a\n" % d1)
				if pd2 != d2:
					fo.write("r%.16g b\n" % d2)
				if ps1 != s1:
					#fo.write("b%s c\n" %int(bin(ord(s1))[2:]))

					if ps1 == 'S' or ps1 == 'A' or ps1 == 'N' or ps1 == 'R' or ps1 == 'X':
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

		ts = "\n$timescale\n %f s \n$end\n" % tbase
		sig = "$var real 1 a %s $end\n$var real 1 b %s $end\n" % (self.namech1, self.namech2)

		if len(tim) > 0:
			sig = sig + '$var wire 8 c %s $end\n' % busname

		fo.write(self.hdr)
		fo.write(ts)
		fo.write(sig)
		fo.write("$enddefinitions $end\n")

		currtime = 0
		pd1 = 0
		pd2 = 0
		ps1 = 0
		idx = 0
		s1 = 0
		#print bitstream
		for d1, d2 in zip(ch1, ch2):

			if pd1 != d1 or pd2 != d2 or currtime == tim[idx]:
				fo.write("#%f\n" % currtime)
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

		fo.close()
