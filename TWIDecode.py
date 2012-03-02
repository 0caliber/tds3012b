import unittest
from BusDecode import *

###############################################################################################
# Main Bus Class Decode Functions
###############################################################################################

class TWIDecode(BusDecode):

	def f_TWIDecode(self, thrlevel, scl, sda):
		self.f_SetThresholdType(thrlevel)
		self.f_SetEdgeTimeSamples(0)
		tsda = self.f_Threshold(sda)
		tscl = self.f_Threshold(scl)
		escl = self.f_FindEdges(tscl)
		esda = self.f_FindEdges(tsda)
		cond = self.f_ScanStartStop(tscl, esda)
		stream = self.f_Decode(escl, tsda, cond)
		bytes = self.f_GetBytes(stream)
		
		return bytes
	
	def f_GetBytes(self, bitstream):
		state = 'Start'
		byte = 0
		line = ""
		rawbytes = []
		for mydata in bitstream:
			if state == 'Start':
				if mydata == 'S':
					state = 'Data'
					if line == "" :
						line = " S-"
					else:
						line = "%s - S-" %(line)

				rot = 0
				byte = 0
				
			elif state == 'Data':
					
				if mydata == 1:
					byte *= 2
					byte += 1
					rot += 1
				elif mydata == 0:
					byte *= 2
					byte += 0
					rot += 1
				elif mydata == 'P':
						# stop
						line = "%sP" %(line)
						state = 'Start'
				elif mydata == 'S':
						# start
						line = "%sS-" %(line)
						state = 'Data'
						rot = 0
						byte  = 0
				else:
					# unknown input
					line = "%s-'%c'" %(line, mydata)
					state = 'Start'
					rot = 0
					byte = 0
					
				if rot == 8:
					state = 'AckNack'
				
			elif state == 'AckNack':
				if mydata == 1:
					line = "%s%02X-N-" %(line, byte)
				elif mydata == 0:
					line = "%s%02X-A-" %(line, byte)
					rawbytes.append(byte)
				rot = 0
				byte = 0
				
				state = 'Data'
				
			elif state == 'Stop':
				state = 'Start'
				
				
					
		return line, rawbytes
		pass
		
	def f_Decode(self, eclk, tdata, cond):
		bitstream = []
		for idx in range(0, len(eclk)):
			edge = eclk[idx]
			data = tdata[idx]
			mycond = cond[idx]
			
			if edge == 1:
				if data == 0:
					bit = 0
				elif data == 1:
					bit = 1
				else:
					bit = 'X'
				bitstream.append(bit)
			elif mycond != ' ':
				bitstream.append(mycond)
		
		return bitstream
		
	def f_ScanStartStop(self, tclk, edata):
		ScanStream = []
		for idx in range(0, len(tclk)):
			edge = edata[idx]
			clk = tclk[idx]
			cond = ' '
			
			if clk == 1:
				if edge == -1:
					cond = 'S'
				elif edge == 1:
					cond = 'P'
			
			ScanStream.append(cond)
			
		return ScanStream
		pass

###############################################################################################
# TDD Unit Test Class and functions
###############################################################################################

class test_basic(unittest.TestCase):
	# Test Attribute control
	def test_Decode(self):
		data = [0, 2.3, 2.4, 0.2, 0.2, 0.2, 2.4, 2.4, 2.4, 2.4, 2.4, 2.4, 0.2, 0.2, 0.2, 0.2, 2.4, 0.2, 2.4, 0.2, 2.4, 0.2, 0.2, 0.2, 2.4,] 
		clk =  [0, 0.2, 2.4, 2.4, 2.4, 0.2, 0.2, 0.2, 2.4, 2.4, 2.4, 0.2, 0.2, 1.5, 2.4, 0.2, 2.4, 0.2, 2.4, 0.2, 2.4, 0.2, 2.4, 2.4, 2.4,] 
		x=TWIDecode()
		x.f_SetThresholdType('LVTTL')
		x.f_SetEdgeTimeSamples(0)
		tdata = x.f_Threshold(data)
		tclk = x.f_Threshold(clk)
		eclk = x.f_FindEdges(tclk)
		edata = x.f_FindEdges(tdata)
		cond = x.f_ScanStartStop(tclk, edata)
		v = x.f_Decode(eclk, tdata, cond)
		vref = [1, 'S', 1, 0, 1, 1, 1, 0, 'P']
		self.assertEqual(vref, v)
			
	def test_ScanStartStop(self):
		clk =    [2.5, 2.4, 2.5, 0.2, 0.2, 0.2, 2.5, 2.4, 0.2, 0.2, 0.2, 2.4, 2.5, 2.5, 0.2, 0.2, 0.2, 2.4, 0.2, 2.4, 0.2, 2.4, 2.4, 2.4,]
		vtclk =  [  1,   1,   1,   0,   0,   0,   1,   1,   0,   0,   0,   1,   1,   1,   0,   0,   0,   1,   0,   1,   0,   1,   1,   1,]  
		vedata = [  1,  -1,   0,   0,  0,    1,   0,  0,   -1,   1,   0,   0,   0,  0,    0,   -1,  0,   0,  0,   0,   0,   0,   1,   0,] 
		data =   [2.3, 0.2, 0.2, 0.2, 0.3, 2.4, 2.4, 2.4, 0.2, 2.4, 2.4, 2.4, 2.4, 2.4, 2.5, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 2.4, 2.4,] 
		
		x=TWIDecode()
		x.f_SetThresholdType('LVTTL')
		x.f_SetEdgeTimeSamples(0)
		tdata = x.f_Threshold(data)
		tclk = x.f_Threshold(clk)
		edata = x.f_FindEdges(tdata)
		self.assertEqual(vedata, edata)
		self.assertEqual(vtclk, tclk)
		v = x.f_ScanStartStop(tclk, edata)
		vref = ['P', 'S', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', 'P', ' ',] 
		self.assertEqual(vref, v)	
		
		
	def test_GetSingleByteAck(self):		
		stream = [1, 'S', 1, 0, 1, 1, 1, 0, 0, 1, 0, 'P']
		x=TWIDecode()
		byte, bytes = x.f_GetBytes(stream)
		self.assertEqual(" S-B9-A-P", byte)	
	
	def test_GetSingleByteNAck(self):		
		stream = [1, 'S', 1, 0, 1, 1, 1, 0, 0, 1, 1, 'P']
		x=TWIDecode()
		byte, bytes = x.f_GetBytes(stream)
		self.assertEqual(" S-B9-N-P", byte)	
		
	def test_GetMultiByteAck(self):		
		stream = [1, 'S', 1, 0, 1, 1, 1, 0, 0, 1, 0, 1, 1, 1, 0, 1, 1, 0, 0, 0, 'P']
		x=TWIDecode()
		byte, bytes = x.f_GetBytes(stream)
		self.assertEqual(" S-B9-A-EC-A-P", byte)	
		
	def test_GetMultiByteNAck(self):		
		stream = [1, 'S', 1, 0, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 0, 1, 1, 0, 0, 0, 'P']
		x=TWIDecode()
		byte, bytes = x.f_GetBytes(stream)
		self.assertEqual(" S-B9-N-EC-A-P", byte)	
		
		
	def test_GetMultiByteRestartAck(self):		
		stream = [1, 'S', 1, 0, 1, 1, 1, 0, 0, 1, 0, 'S', 1, 1, 1, 0, 1, 1, 0, 0, 0, 'P']
		x=TWIDecode()
		byte, bytes = x.f_GetBytes(stream)
		self.assertEqual(" S-B9-A-S-EC-A-P", byte)	
		
	def test_GetMultiByteRestartNAck(self):		
		stream = [1, 'S', 1, 0, 1, 1, 1, 0, 0, 1, 0, 'S', 1, 1, 1, 0, 1, 1, 0, 0, 1, 'P']
		x=TWIDecode()
		byte, bytes = x.f_GetBytes(stream)
		self.assertEqual(" S-B9-A-S-EC-N-P", byte)	
		
		
		
		