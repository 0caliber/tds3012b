
import unittest

###############################################################################################
# Main Bus Class Decode Functions
###############################################################################################

class BusDecode:
	def __init__(self):
		print 'Bus Decode'
		self.LevelLo = 0.7
		self.LevelHi = 2.7
		self.EdgeDuration = 0		# used to determine sample scale for edge detection
		self.PulseDurationLo = 0
		self.PulseDurationHi = 0
		self.bitlen = 1
		
		# Comm defaults

	def f_Threshold(self, rawdata):
		dataout = []
		for mydata in rawdata:
			if mydata >= self.LevelHi:
				mydigit = 1
			elif mydata <= self.LevelLo:
				mydigit = 0
			else:
				mydigit = 2
			dataout.append(mydigit)
		return dataout		
		pass
		
	def f_FindClkDuration(self, thrdata):
		low = 0
		hi = 0
		lowmax = 0
		himax = 0
		state = 0
		
		for mydata in thrdata:
			if mydata == 0:
				low += 1
				lowmax = max(lowmax, low)
					
			elif mydata == 1:
				hi += 1
				himax = max(himax, hi)
			
			if state == 0:
				if mydata == 1:
					low = 0
					state = 1
			elif state == 1:
				if mydata == 0:
					hi = 0
					state = 0
		
		
		self.PulseDurationLo = lowmax
		self.PulseDurationHi = himax
		
		pass
		
	def f_FindEdges(self, thrdata):
		
		state = 0
		cnt = 0
		dataout = []
		newdigit = 0
		mydigit = 0
		for mydata in thrdata:
			
			if state == 0:
				if mydata == 1:
					mydigit = 1
					state = 1
				elif mydata == 0:
					mydigit = 0
					state = 0
				else: # mydata == 2:
					state = 2
					mydigit = 0
					newdigit = 1
			
			elif state == 1:
				if mydata == 1:
					mydigit = 0
					state = 1
				elif mydata == 0:
					mydigit = -1
					state = 0
				else: # mydata == 2:
					state = 2
					mydigit = 0
					newdigit = -1
			else:
				if mydata == 1:
					mydigit = newdigit
					state = 1
					cnt = 0
				elif mydata == 0:
					mydigit = newdigit
					state = 0
					cnt = 0
				else:
					mydigit = 0
						
				pass
		
			dataout.append(mydigit)
		
		return dataout		
		
		pass
	
	def f_DecodeData(self, rawdata):
		pass
		
	def f_SetThresholdHi(self, LevelHi):
		self.LevelHi = LevelHi
		pass
	
	def f_SetThresholdLo(self, LevelLo):
		self.LevelLo = LevelLo
		pass

		
	def f_SetThresholdType(self, std_type):
		try:
			(self.LevelLo, self.LevelHi) = {
				"CMOS"		: (1.5, 3.5), 
				"LVCMOS"	: (1, 2.3),
				"TTL"   		: (0.7, 2.4),
				"LVTTL"   	: (0.3, 2),
				"RS422U"	: (1.7, 2.5)
				}[std_type]
		except:
			print 'Unknown standard, ', std_type

	def f_SetEdgeTimeSamples(self, edgesamples):
		self.EdgeDuration = edgesamples
		
###############################################################################################
# TDD Unit Test Class and functions
###############################################################################################

class test_basic(unittest.TestCase):
	# Test Attribute control
	def test_ThesholdTypeCMOSHi(self):
		x=BusDecode()
		x.f_SetThresholdType('CMOS')
		self.assertEqual(3.5, x.LevelHi)
		
	def test_ThesholdTypeCMOSLo(self):
		x=BusDecode()
		x.f_SetThresholdType('CMOS')
		self.assertEqual(1.5, x.LevelLo)
		
	def test_ThesholdTypeLVCMOSHi(self):
		x=BusDecode()
		x.f_SetThresholdType('LVCMOS')
		self.assertEqual(2.3, x.LevelHi)
		
	def test_ThesholdTypeLVCMOSLo(self):
		x=BusDecode()
		x.f_SetThresholdType('LVCMOS')
		self.assertEqual(1, x.LevelLo)
		
	def test_ThesholdTypeTTLHi(self):
		x=BusDecode()
		x.f_SetThresholdType('TTL')
		self.assertEqual(2.4, x.LevelHi)
		
	def test_ThesholdTypeTTLLo(self):
		x=BusDecode()
		x.f_SetThresholdType('TTL')
		self.assertEqual(0.7, x.LevelLo)
		
	def test_ThesholdTypeLVTTLHi(self):
		x=BusDecode()
		x.f_SetThresholdType('LVTTL')
		self.assertEqual(2, x.LevelHi)
		
	def test_ThesholdTypeLVTTLLo(self):
		x=BusDecode()
		x.f_SetThresholdType('LVTTL')
		self.assertEqual(0.3, x.LevelLo)
		
	def test_SetThresholdHi(self):
		x=BusDecode()
		x.f_SetThresholdHi(1.2)
		self.assertEqual(1.2, x.LevelHi)
		
	def test_SetThresholdLo(self):
		x=BusDecode()
		x.f_SetThresholdLo(1)
		self.assertEqual(1, x.LevelLo)

	def test_SetEdgeTimeSamples(self):
		x=BusDecode()
		x.f_SetEdgeTimeSamples(1)
		self.assertEqual(1, x.EdgeDuration)
		
	# Test Threshold to Logic Function of RAW data
	
	def test_ThresholdLVCMOS(self):
		datain = [0.2, 0.2, 0.3, 0.7, 0.9, 1.0, 1.2, 1.3, 1.7, 1.9, 2.2, 2.7, 2.8, 2.8, 2.8 ]
		x=BusDecode()
		x.f_SetThresholdType('LVCMOS')
		dataout = x.f_Threshold(datain)
		dataref = [0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 1, 1, 1, 1 ]
		self.assertEqual(dataref, dataout)
	
	def test_ThresholdLVTTL(self):
		datain = [0.2, 0.2, 0.3, 0.7, 0.9, 1.0, 1.2, 1.3, 1.7, 1.9, 2.2, 2.7, 2.8, 2.8, 2.8 ]
		x=BusDecode()
		x.f_SetThresholdType('LVTTL')
		dataout = x.f_Threshold(datain)
		dataref = [0, 0, 0, 2, 2, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1 ]
		self.assertEqual(dataref, dataout)
	
	# Test Clock Frequency determination
	def test_FindClockFreq(self):
		datain = [0.2, 2.4, 0.2, 2.4, 0.2, 1.5, 2.4, 2.4, 1.5, 0.2, 0.2, 1.7, 2.4, 1.2, 0.2, 2.4, 0.2, 2.4, 0.2]
		x=BusDecode()
		x.f_SetThresholdType('LVTTL')
		dataout = x.f_Threshold(datain)
		x.f_FindClkDuration(dataout)
		self.assertEqual(2, x.PulseDurationLo)
		self.assertEqual(2, x.PulseDurationHi)
		
	# Test Digital Word Determination
	def test_FindEdges(self):
		datain = [0.2, 2.4, 0.2, 2.4, 0.2, 1.5, 2.4, 2.4, 1.5, 0.2, 0.2, 1.7, 2.4, 1.2, 0.2, 2.4, 0.2, 2.4, 0.2]
		x=BusDecode()
		x.f_SetThresholdType('LVTTL')
		x.f_SetEdgeTimeSamples(0)
		dataout = x.f_Threshold(datain)
		digital = x.f_FindEdges(dataout)
		digitalref = [0, 1, -1, 1, -1, 0, 1, 0, 0, -1, 0, 0, 1, 0, -1, 1,-1, 1, -1 ]
		self.assertEqual(digitalref, digital)


	