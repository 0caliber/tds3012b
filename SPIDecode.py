import unittest
from BusDecode import *


class SPIDecode(BusDecode):
	def f_SPIDecode(self, thrlevel, sclk, miso, mode, msbfirst=1):
		# Clock polarity
		if mode == 0 or mode == 1:
			cpol = 0  # Idle state is 0
		else:
			cpol = 1  # Idle state is 1

		# Phase sampling
		if mode == 0 or mode == 2:
			cpha = 0  # Leading edge sample
		else:
			cpha = 1  # Trailing edge sample

		self.f_SetThresholdType(thrlevel)
		self.f_SetEdgeTimeSamples(0)
		tclk = self.f_Threshold(sclk)
		tdata = self.f_Threshold(miso)
		eclk = self.f_FindEdges(tclk)
		fclk = self.f_SPIFilterStartOfBufferEdge(eclk, tclk)
		bytes = self.f_SPIParseStream(fclk, tdata, cpol, cpha, msbfirst)

		return bytes

	def f_SPIGetStream(self):
		return [self.vcdt, self.vcdd]

	# Decode edges and data to SPI bytes
	# default MSB is first
	def f_SPIParseStream(self, eclk, miso, cpol, cpha, msbfirst = 1):
		bytes = []
		self.vcdt = []
		self.vcdd = []

		if cpol == 0:
			LeadingEdge = 1
			TrailingEdge = -1
		else:
			LeadingEdge = -1
			TrailingEdge = 1

		valid = 0
		bitcnt = 0
		byte = 0
		idx = 0

		# Scan full buffer
		for edge, data in zip(eclk, miso):
			if cpha == 1: # Scan for trailing edge
				if edge == TrailingEdge:
					bit = data
					valid = 1
				else:
					pass
			else: # Scan for leading edge
				if edge == LeadingEdge:
					bit = data
					valid = 1
				else:
					pass

			# valid data, shift and store
			if valid == 1:
				if bitcnt == 0:
					self.vcdt.append(idx)

				if msbfirst == 1:
					byte = (byte << 1) + bit
				else:
					byte = (byte >> 1) + (bit << 7)

				bitcnt += 1
				valid = 0
				# separate bytes
				if bitcnt == 8:
					bytes.append("%02X" %byte)
					self.vcdd.append(byte)
					bitcnt = 0
					byte = 0
			idx += 1

		return bytes

	# Filter the first edge if the buffer starts with a steady state 1 value
	# For zero initial buffer value we do not need to do this
	def f_SPIFilterStartOfBufferEdge(self, eclk, tclk):
		if tclk[0] == 1:
			eclk[0] = 0
		return eclk

###############################################################################################
# TDD Unit Test Class and functions
###############################################################################################

class test_basic(unittest.TestCase):
	# Capture on Leading Edge, positive clock
	def test_DecodeMode0(self):

		sclk = [2.3, 2.4, 2.2, 2.4, 0.2, 0.2, 2.4, 2.4, 0.2, 0.2, 2.4, 2.4, 0.2, 0.2, 2.4, 2.4, 0.2, 0.2, 2.4, 2.4, 0.2,
				0.2, 2.4, 2.4, 0.2, 0.2, 2.4, 2.4, 0.2, 0.2, 2.4, 2.4, 2.4, 0.2, 0.2, 2.4, 2.4, 2.4, 2.4]
		miso = [0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 2.4, 2.4, 2.4, 2.4, 2.4, 2.5, 2.4, 2.5, 0.2, 0.2, 0.2, 0.2, 2.4,
				2.5, 2.4, 2.4, 0.2, 0.2, 0.2, 0.2, 2.4, 2.4, 2.4, 2.4, 2.4, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3]

		data = ['6A']
		cpol = 0
		cpha = 0
		x = SPIDecode()
		x.f_SetThresholdType('LVTTL')
		x.f_SetEdgeTimeSamples(0)
		tclk = x.f_Threshold(sclk)
		tdata = x.f_Threshold(miso)

		eclk = x.f_FindEdges(tclk)
		fclk = x.f_SPIFilterStartOfBufferEdge(eclk, tclk)
		bytes = x.f_SPIParseStream(fclk, tdata, cpol, cpha)
		self.assertEqual(data, bytes)

	# Capture on Trailing Edge, positive clock
	def test_DecodeMode1(self):
		sclk = [2.3, 2.4, 2.2, 2.4, 0.2, 0.2, 2.4, 2.4, 0.2, 0.2, 2.4, 2.4, 0.2, 0.2, 2.4, 2.4, 0.2, 0.2, 2.4, 2.4, 0.2,
				0.2, 2.4, 2.4, 0.2, 0.2, 2.4, 2.4, 0.2, 0.2, 2.4, 2.4, 2.4, 0.2, 0.2, 2.4, 2.4, 2.4, 2.4]
		miso = [0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 2.4, 2.4, 2.4, 2.4, 2.4, 2.5, 2.4, 2.5, 0.2, 0.2, 0.2, 0.2, 2.4, 2.4, 2.4,
				2.5, 2.4, 2.4, 0.2, 0.2, 0.2, 0.2, 2.4, 2.4, 2.4, 2.4, 2.4, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3]

		data = ['6A']
		cpol = 0
		cpha = 1
		x = SPIDecode()
		x.f_SetThresholdType('LVTTL')
		x.f_SetEdgeTimeSamples(0)
		tclk = x.f_Threshold(sclk)
		tdata = x.f_Threshold(miso)

		eclk = x.f_FindEdges(tclk)

		bytes = x.f_SPIParseStream(eclk, tdata, cpol, cpha)
		self.assertEqual(data, bytes)

	# Capture on Leading Edge, Test LSB first
	def test_DecodeMode0_lsbfirst(self):

		sclk = [2.3, 2.4, 2.2, 2.4, 0.2, 0.2, 2.4, 2.4, 0.2, 0.2, 2.4, 2.4, 0.2, 0.2, 2.4, 2.4, 0.2, 0.2, 2.4, 2.4, 0.2,
				0.2, 2.4, 2.4, 0.2, 0.2, 2.4, 2.4, 0.2, 0.2, 2.4, 2.4, 2.4, 0.2, 0.2, 2.4, 2.4, 2.4, 2.4]
		miso = [0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 2.4, 2.4, 2.4, 2.4, 2.4, 2.5, 2.4, 2.5, 0.2, 0.2, 0.2, 0.2, 2.4,
				2.5, 2.4, 2.4, 0.2, 0.2, 0.2, 0.2, 2.4, 2.4, 2.4, 2.4, 2.4, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3]

		data = ['56']
		cpol = 0
		cpha = 0
		msbfirst = 0
		x = SPIDecode()
		x.f_SetThresholdType('LVTTL')
		x.f_SetEdgeTimeSamples(0)
		tclk = x.f_Threshold(sclk)
		tdata = x.f_Threshold(miso)

		eclk = x.f_FindEdges(tclk)
		fclk = x.f_SPIFilterStartOfBufferEdge(eclk, tclk)
		bytes = x.f_SPIParseStream(fclk, tdata, cpol, cpha, msbfirst)
		self.assertEqual(data, bytes)


	# Capture on Leading Edge, Negative clock
	def test_DecodeMode2(self):

		sclk = [2.3, 2.4, 2.2, 2.4, 0.2, 0.2, 2.4, 2.4, 0.2, 0.2, 2.4, 2.4, 0.2, 0.2, 2.4, 2.4, 0.2, 0.2, 2.4, 2.4, 0.2,
				0.2, 2.4, 2.4, 0.2, 0.2, 2.4, 2.4, 0.2, 0.2, 2.4, 2.4, 2.4, 0.2, 0.2, 2.4, 2.4, 2.4, 2.4]
		miso = [0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 2.4, 2.4, 2.4, 2.4, 2.4, 2.5, 2.4, 2.5, 0.2, 0.2, 0.2, 0.2, 2.4, 2.4, 2.4,
				2.5, 2.4, 2.4, 2.4, 2.4, 0.2, 0.2, 0.2, 0.2, 2.4, 2.4, 2.4, 2.4, 2.4, 0.3, 0.3, 0.3, 0.3]

		data = ['6D']
		cpol = 1
		cpha = 0
		x = SPIDecode()
		x.f_SetThresholdType('LVTTL')
		x.f_SetEdgeTimeSamples(0)
		tclk = x.f_Threshold(sclk)
		tdata = x.f_Threshold(miso)

		eclk = x.f_FindEdges(tclk)
		fclk = x.f_SPIFilterStartOfBufferEdge(eclk, tclk)
		bytes = x.f_SPIParseStream(fclk, tdata, cpol, cpha)
		self.assertEqual(data, bytes)

	# Filter fixed level at start of buffer (if was 1) so that a virtual edge is not detected
	def test_FilterClk(self):
		sclk = [2.3, 2.4, 2.2, 2.4, 0.2, 0.2, 2.4, 2.4, 0.2, 0.2, 2.4, 2.4, 0.2, 0.2, 2.4, 2.4, 0.2, 0.2, 2.4, 2.4, 0.2,
				0.2, 2.4, 2.4, 0.2, 0.2, 2.4, 2.4, 0.2, 0.2, 2.4, 2.4, 2.4, 0.2, 0.2, 2.4, 2.4, 2.4, 2.4]

		refclk = [0,   0,   0,   0,  -1,   0,   1,  0,   -1,   0,   1,   0,  -1,   0,   1,   0,  -1,   0,   1,   0,  -1,
				  0,   1,   0,  -1,   0,   1,   0,  -1,   0,   1,   0,   0,  -1,   0,   1,   0,   0,   0]

		x = SPIDecode()
		x.f_SetThresholdType('LVTTL')
		x.f_SetEdgeTimeSamples(0)
		tclk = x.f_Threshold(sclk)
		eclk = x.f_FindEdges(tclk)
		fclk = x.f_SPIFilterStartOfBufferEdge(eclk, tclk)
		self.assertEqual(refclk, fclk)

