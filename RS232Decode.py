# License conditions are given in LICENSE.TXT
# This code is licnesed under the MIT License 
# Copyright (c) 2017 Ilialex Research Lab
# www.ilialex.gr, blog.ilialex.gr
#

import unittest
from BusDecode import *

###############################################################################################
# Main Bus Class Decode Functions
###############################################################################################

class RS232Decode(BusDecode):

	def f_RS232Decode(self, sample_period, thrlevel, baudrate, dbits, parity, polarity, rx, tx):
		self.f_SetThresholdType(thrlevel)

		self.vcdt1 = []
		self.vcdd1 = []
		self.vcdt2 = []
		self.vcdd2 = []

		rxdata = self.f_Threshold(rx)
		txdata = self.f_Threshold(tx)
		
		bitlen = self.f_GetBitDuration(sample_period, baudrate)
		#print "bitlen: ", bitlen
		#print rxdata, ";", txdata, ";"
		
		trx = self.f_Polarity(polarity, rxdata)
		ttx = self.f_Polarity(polarity, txdata)
		
		[vrx, ttrx] = self.f_Decode(sample_period, baudrate, dbits, parity, trx)
		self.vcdt1 = self.vcdt2 # We always copy data to dt2
		self.vcdd1 = self.vcdd2 # We always copy data to dt2
		self.vcdt2 = []
		self.vcdd2 = []
		[vtx, tttx] = self.f_Decode(sample_period, baudrate, dbits, parity, ttx)


		print (len(ttx), vtx)
		print (len(trx), vrx)
		
		[statrx, datarx] = self.f_GetBytes(dbits, parity, vrx)
		[stattx, datatx] = self.f_GetBytes(dbits, parity, vtx)

		self.vcdd1 = self.f_RS232PassData(statrx, datarx, self.vcdd1)

		retb, rets, reta = self.f_CombineStreams(datarx, statrx, ttrx, datatx, stattx, tttx, sample_period, baudrate)
		
		return retb, rets, reta

	def f_RS232GetStream(self):
		return [self.vcdt1, self.vcdd1, self.vcdt2, self.vcdd2]

	def f_RS232PassData(selfself, stat, data, vcd):
		startidx = 0
		for	s,d in zip(stat, data):
			for idx in range(startidx, len(vcd)):
				if vcd[idx] == 'D':
					vcd[idx] = d
					#print d
					startidx = idx
					break

		return vcd

	# simpler decoder
	def f_Decode(self, sample_period, baud, data_bits, parity, tdata):
		bitstream = []
		timestream = []
		state = 'IDLE'
		prevsig = tdata[1]

		# parity duration in bit time
		if parity != 'N':
			pardur_bits = 1
		else:
			pardur_bits = 0
		
		stopdur_bits = 1		# default stop duration 1 bit
		
		bitdur_samples = self.f_GetBitDuration(sample_period, baud)
		bitdur_samples -= 1							# just compensate for possible round off values
		byte_bits = ( 1 + data_bits + pardur_bits + stopdur_bits)		
		
		diff = 1
		skipf = 0
		idx = diff + 1
		finish = len(tdata) - bitdur_samples * byte_bits 
		while idx < finish:
			currsig = tdata[idx]
			# on Idle state
			if currsig == 0:
				if prevsig == 1:
					# Start Condition detected
					# check for valid digit duration (ignore spikes)
					#print idx
					idx, bitstream, timestream = self.f_DecodeByte(tdata, idx, bitstream, timestream, byte_bits, bitdur_samples, data_bits, pardur_bits, stopdur_bits)
				else:
					idx += 1
			else:
				idx += 1

			prevsig = tdata[idx-diff]
						
		return bitstream, timestream
		
	
		
	def f_DecodeByte(self, tdata, idx, bitstream, timestream, byte_bits, bitdur_samples, data_bits, pardur_bits, stopdur_bits):
		curridx = idx
		for byteidx in range(0, byte_bits):
			
			v_err, v_bit, curridx = self.f_DecodeBit(tdata, curridx, bitdur_samples)
			#print v_err, v_bit
			
			if v_err == 0:
				if byteidx == 0:
					if v_bit == 0:	# start condition detected (should, we got here because of this unless there is a spike)
						timestream.append(curridx)
						bitstream.append('S')
						self.vcdd2.append('S')
						#print 'S - ', curridx
					else:
						bitstream.append('s')
						self.vcdd2.append('s')
						#curridx += 1
						break
					self.vcdt2.append(curridx)
				elif byteidx > 0 and byteidx <= (data_bits + pardur_bits): # data + parity
					bitstream.append(v_bit)
					#print 'Data - ', curridx, v_bit
					if byteidx == 1:
						self.vcdd2.append('D')
						self.vcdt2.append(curridx)
					elif byteidx  == (data_bits -1):
						if pardur_bits > 0:
							self.vcdd2.append('R')
							self.vcdt2.append(curridx)
				elif byteidx == (data_bits + pardur_bits + stopdur_bits): # stop bit
					if v_bit == 1:	# start condition detected (should, we got here because of this unless there is a spike)
						bitstream.append('P')
						self.vcdd2.append('P')
						#print 'P - ', curridx
					else:
						bitstream.append('E')
						self.vcdd2.append('E')
						#print 'E - ', curridx
						#curridx += 1
						break
					self.vcdt2.append(curridx)
					#print curridx
				else:
					print ("boo")
					pass
						
			else:
				bitstream.append('X')
				self.vcdt2.append(curridx)
				#curridx += 1
				break
				
			# update pointer
			#curridx +=  bitdur_samples
				
		return curridx, bitstream, timestream
	
	
	def f_DecodeBit(self, tdata, bitidx, bitdur_samples):
		v_error = 0
		# span bit scan between +1/4 - 3/4 of the bit width (span 1/2)
		minidx = bitidx + int(1*bitdur_samples/4)
		maxidx = bitidx + int(3*bitdur_samples/4)
		
		minidx = bitidx
		maxidx = bitidx + bitdur_samples
		mididx = bitidx + int(2*bitdur_samples/4)
		# bit has middle value
		v_midbit = tdata[mididx]
		v_startbit = tdata[minidx]
		
		# scan from start to middle to find when this bit starts (if start is earlier)
		for idx in range(minidx, mididx):
			v_bit = tdata[idx] # detect bit change if any
			if v_startbit != v_bit:
				minidx = idx # bit change before reaching the middle value
				break
			
		# Scan to find correct end of bit
		for idx in range(mididx, maxidx):
			v_bit = tdata[idx] # detect bit change if any
			if v_midbit != v_bit:
				maxidx = idx # bit change before reaching the end, value change earlier
				break
		
		# Check that every bit inside is same
		v_cnt = 0	
		for idx in range(minidx, maxidx):
			if v_midbit == tdata[idx]: # should be same in this area
				v_cnt += 1
		
		if v_cnt > int(bitdur_samples/3):
			curridx = maxidx
			pass
		else:
			v_error = 1
			v_midbit = 'X'
			curridx = bitidx + 1
			#print 'X: ', minidx, maxidx, bitidx
			
		#print v_midbit, curridx, v_error, minidx, maxidx
		return v_error, v_midbit, curridx
		
	
	def f_Decode2(self, sample_period, baud, dbits, parity, tdata):
		bitstream = []
		timestream = []
		state = 'IDLE'
		prevsig = tdata[1]
		
		
		bitdur = self.f_GetBitDuration(sample_period, baud)
		bitdur -= 1
		diff = 1
		skipf = 0
		idx = diff + 1
		while idx < len(tdata):
			currsig = tdata[idx]
			# on Idle state
			
			if state == 'IDLE':
				#print state, prevsig, currsig
				if currsig == 0:
					if prevsig == 1:
						# Start Condition detected
						# check for valid digit duration (ignore spikes)
						vbit, skipf = self.f_CheckBitDuration(tdata, idx)
						if vbit == 0:
							# valid duration of start bit
							state = 'START'
							bitstream.append('S')
							idxstart = idx
							print ("Start: ", idxstart)
							timestream.append(idx)
							bitcnt = 0
						else:
							skipf = 0
								
			elif state == 'START':
				if skipf > 0: 
					skipf -= 1
				else:
					vbit, skipf = self.f_CheckBitDuration(tdata, idx)
					bitstream.append(vbit)
					if vbit == 'X':
						skipf = 0
						state = 'IDLE'	
						print (idx)
					else:
						bitcnt += 1
						state = 'DATA'
		
			elif state == 'DATA':
				if skipf > 0: 
					skipf -= 1
				else:
					vbit, skipf = self.f_CheckBitDuration(tdata, idx)
					bitstream.append(vbit)
					if vbit == 'X':
						skipf = 0
						state = 'IDLE'	
					else:
						bitcnt += 1
						#skipf = bitdur
						if bitcnt == dbits:
							if parity == 'N':
								state = 'STOP'	
							else:
								state = 'PARITY'
						
			elif state == 'PARITY':
				if skipf > 0: 
					skipf -= 1
				else:
					vbit, skipf = self.f_CheckBitDuration(tdata, idx)
					if vbit != 'X':
						bitstream.append(vbit)
						state = 'STOP'
					else:
						bitstream.append(vbit)
						skipf = 0
						state = 'IDLE'
					
					
			elif state == 'STOP':
				if skipf > 0: 
					skipf -= 1
				else:
					vbit, skipf = self.f_CheckBitDuration(tdata, idx)
					#print "Stop ", vbit, skipf
					if vbit == 'X':
						bitstream.append(vbit)
						skipf = 0
					elif vbit == 0:
						bitstream.append('E')
						print ("Stop Error ", vbit, skipf, idx)
						skipf = 0
					else:
						bitstream.append('P')
			
						
					
					state = 'IDLE'	
			else:
				pass
				
			prevsig = tdata[idx-diff]
			if skipf > 0: 
				idx += skipf
			else:
				idx += 1
						
		return bitstream, timestream
		
		
		
	def f_Polarity(self, pol, tdata):
		bitstream = []
		for mybit in tdata:
			bitstream.append(pol ^ mybit)
		
		return bitstream
	
	def f_CheckBitDuration(self, tdata, idx):
		InitialBit = tdata[idx]
		result = InitialBit
		state2 = ''
		majvot1 = 0.0
		majvot2 = 0.0
		for bitidx in range(0, self.bitlen):
			nmybit = tdata[idx+bitidx]
			if nmybit == 2:
				#mybit = 1
				pass
			else:
				mybit = nmybit
				
			if InitialBit != mybit:
				majvot1 += 1
				state2 = mybit
			else:
				majvot2 += 1
			
		# If initial bit was earlier than actual bit, valid value is the majority
		if majvot2 < majvot1:
			InitialBit = state2
			majvot = majvot1
		else:
			majvot = majvot2
		
		#majvot = majvot2
		
		decision = majvot/self.bitlen
		if decision > 0.5:
			result = InitialBit
			pass
		else:
			result = 'X'
			pass
		
		#skip = majvot-1
		skip = self.bitlen
		print ("Majority1: ", majvot1, "Majority2: ", majvot2, "Decision: ", decision, "Skip: ", skip, result)
		return result, skip
	
	def f_GetBitDuration(self, sample_period, baud_rate):
		fs = 1/sample_period
		bitlen = int(round(fs/baud_rate))
		self.bitlen = bitlen
		print (bitlen)
		return bitlen
	
	def f_GetBytes(self, dbits, parity, bitstream):
		stat = []
		data = []
		for idx in range(0, len(bitstream)):
			bit = bitstream[idx]
			if bit == 'S':
				byte = 0
				par = 0
				fe = 0
				for idx2 in range(dbits-1, -1, -1):
					bit = bitstream[idx+idx2+1]
					if bit == 1:
						byte |= 1 << idx2
						par += 1
					elif bit == 'X':
						fe = 1
					elif bit == 'P':
						fe = 1
					else:
						#bit zero
						pass
				strbyte = "%02X" %byte
				if idx+dbits+1 > len(bitstream)-1:
					break
				else:
					parbit = bitstream[idx+dbits+1]
					d = par % 2
					
				if parity == 'E':
					# Parity is even
					if d == 1:
						# Parity is odd
						if parbit == 0:
							stbyte = 'OK'
						else:
							stbyte = 'PE'
					else:
						# Parity is even
						if parbit == 1:
							stbyte = 'OK'
						else:
							stbyte = 'PE'
					pass
				elif parity == 'O':
					# Parity is odd
					if d == 1:
						# Parity is odd
						if parbit == 1:
							stbyte = 'OK'
						else:
							stbyte = 'PE'
					else:
						# Parity is even
						if parbit == 0:
							stbyte = 'OK'
						else:
							stbyte = 'PE'
				else:
					# Parity None
					stbyte = 'OK'
					pass
					
				if fe == 1:
					stbyte = 'FE'
					
				data.append(strbyte)
				stat.append(stbyte)
				
					
						
		return stat, data
		pass
	
	# Test: capture.py -b RS232 -l TTL -a 115200 -p N -n 0 -v -i CaptureTTL422.csv
	def f_CombineStreams(self, rx, rxstat, rxtime , tx, txstat, txtime, sr, baud):
		ret = ''
		reta = ''
		rets = ''
		frm = 0
		txidx = 0
		rxidx = 0
		flagendrx = 0
		flagendtx = 0
		while (rxidx < len(rxtime) and txidx < len(txtime)):
			
			# take care of premature data end on Rx
			if rxidx > len(rx) - 1:
				rxbyte = ' '
				rxcascii = ' '
				rxidx = len(rx) - 1
				flagendrx = 1
			else:
				rxbyte = rx[rxidx]
				rxcascii = int("0x%s" %rxbyte, 16)
			
			# take care of premature data end on Tx
			if txidx > len(tx) - 1:
				txbyte = ' '
				txcascii = ' '
				txidx = len(tx) - 1
				flagendtx = 1
			else:
				txbyte = tx[txidx]
				txcascii = int("0x%s" %txbyte, 16)
			
			if flagendtx == 1 and flagendrx == 1:
				break
			
			if rxtime[rxidx] < txtime[txidx]:
				if frm != 1:
					ret += "\nRx: %s" %rxbyte
					reta += "\nRx: %c" %rxcascii
					rets += "\nRx: %s" %rxstat[rxidx]
					frm = 1
				else:
					ret += " %s" %rxbyte
					reta += "%c" %rxcascii
					rets += " %s" %rxstat[rxidx]
				rxidx += 1
					
			elif rxtime[rxidx] == txtime[txidx]:
				if frm == 1:
					ret += " %s" %rxbyte
					reta += "%c" %rxcascii
					rets += " %s" %rxstat[rxidx]
					rxidx += 1
				ret += "\nTx: %s" %txbyte
				reta += "\nTx: %c" %txcascii
				rets += "\nTx: %s" %txstat[txidx]
				txidx += 1
				frm = 2
			else:
				if frm != 2:
					ret += "\nTx: %s" %txbyte
					reta += "\nTx: %c" %txcascii
					rets += "\nTx: %s" %txstat[txidx]
					frm = 2
				else:
					ret += " %s" %txbyte
					reta += "%c" %txcascii
					rets += " %s" %txstat[txidx]
				
				txidx += 1

		while (rxidx < len(rxtime)):
			rxbyte = rx[rxidx]
			rxcascii = eval("0x%s" %rx[rxidx])
			if frm != 1:
				ret += "\nRx: %s" %rxbyte
				reta += "\nRx: %c" %rxcascii
				rets += "\nRx: %s" %rxstat[rxidx]
				frm = 1
			else:
				ret += " %s" %rxbyte
				reta += "%c" %rxcascii
				rets += " %s" %rxstat[rxidx]
			rxidx += 1

		while (txidx < len(txtime)):
			txbyte = tx[txidx]
			txcascii = eval("0x%s" %tx[txidx])
			if frm != 2:
				ret += "\nTx: %s" %txbyte
				reta += "\nTx: %c" %txcascii
				rets += "\nTx: %s" %txstat[txidx]
				frm = 2
			else:
				ret += " %s" %txbyte
				reta += "%c" %txcascii
				rets += " %s" %txstat[txidx]
			
			txidx += 1		
			
		ret += '\n'
		rets += '\n'
		reta += '\n'
		
		return ret, rets, reta
		

		
###############################################################################################
# TDD Unit Test Class and functions
###############################################################################################

class test_basic(unittest.TestCase):

	def test_CombineStreamsPackets(self):
		rxdata = ['S', 1, 0, 1, 1, 1, 0, 1, 0, 'P', 'S', 0, 0, 1, 1, 1, 0, 0, 0, 'P']
		txdata = ['S', 1, 0, 1, 1, 1, 0, 0, 0, 'P', 'S', 0, 0, 0, 1, 1, 0, 0, 0, 'P']
		rxtime = [4, 50]
		txtime = [100, 150]
		
		baud = 115200
		dbits = 8
		parity = 'N'
		sr = 2.89E-6
		
		
		x=RS232Decode()
		[vsrx, vrx] = x.f_GetBytes(dbits, parity, rxdata)
		[vstx, vtx] = x.f_GetBytes(dbits, parity, txdata)
		
		#rx, rxtime, rxstat, tx, txtime, txstat)
		ret, rets, reta = x.f_CombineStreams(vrx, vsrx, rxtime, vtx, vstx, txtime, sr, baud)
		
		vrefdata = "\nRx: 5D 1C\nTx: 1D 18\n"
		self.assertEqual(ret, vrefdata)
		
		vrefdata = "\nRx: ]\x1C\nTx: \x1D\x18\n"
		self.assertEqual(reta, vrefdata)

		
	def test_CombineStreams(self):
		rxdata = ['S', 1, 0, 1, 1, 1, 0, 1, 0, 'P', 'S', 0, 0, 1, 1, 1, 0, 0, 0, 'P']
		txdata = ['S', 1, 0, 1, 1, 1, 0, 0, 0, 'P', 'S', 0, 0, 0, 1, 1, 0, 0, 0, 'P']
		rxtime = [4, 100]
		txtime = [50, 150]
		
		baud = 115200
		dbits = 8
		parity = 'N'
		sr = 2.89E-6
		
		
		x=RS232Decode()
		[vsrx, vrx] = x.f_GetBytes(dbits, parity, rxdata)
		[vstx, vtx] = x.f_GetBytes(dbits, parity, txdata)
		
		#rx, rxtime, rxstat, tx, txtime, txstat)
		ret, rets, reta = x.f_CombineStreams(vrx, vsrx, rxtime, vtx, vstx, txtime, sr, baud)
		vrefdata = "\nRx: 5D\nTx: 1D\nRx: 1C\nTx: 18\n"
		self.assertEqual(ret, vrefdata)
		
		vrefdata = "\nRx: OK\nTx: OK\nRx: OK\nTx: OK\n"
		self.assertEqual(rets, vrefdata)
		

		
	def test_RealTestTx(self):
		rxdata = [
			1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 
			1, 1, 1, 1, 1, 1, 1, 1, 1,
			
			0, 0, 0, 0, 0, 0, 0, 0, 
			1, 1, 1, 1, 1, 1, 1, 1, 1, 
			1, 1, 1, 1, 1, 1, 1, 1, 1, 
			0, 0, 0, 0, 0, 0, 0, 0, 
			1, 1, 1, 1, 1, 1, 1, 1, 1, 
			1, 1, 1, 1, 1, 1, 1, 1, 1, 
			1, 1, 1, 1, 1, 1, 1, 1, 1, 
			1, 1, 1, 1, 1, 1, 1, 1, 
			0, 0, 0, 0, 0, 0, 0, 0, 0, 
			1, 1, 1, 1, 1, 1, 1, 1, 1, 
			
			0, 0, 0, 0, 0, 0, 0, 0, 
			1, 1, 1, 1, 1, 1, 1, 1, 1, 
			0, 0, 0, 0, 0, 0, 0, 0, 0, 
			0, 0, 0, 0, 0, 0, 0, 0, 0, 
			0, 0, 0, 0, 0, 0, 0, 0, 0, 
			0, 0, 0, 0, 0, 0, 0, 0, 
			1, 1, 1, 1, 1, 1, 1, 1, 1, 
			1, 1, 1, 1, 1, 1, 1, 1, 
			0, 0, 0, 0, 0, 0, 0, 0, 0, 
			1, 1, 1, 1, 1, 1, 1, 1, 
			
			0, 0, 0, 0, 0, 0, 0, 0, 0, 
			0, 0, 0, 0, 0, 0, 0, 0, 0, 
			1, 1, 1, 1, 1, 1, 1, 1, 1, 
			1, 1, 1, 1, 1, 1, 1, 1, 1, 
			1, 1, 1, 1, 1, 1, 1, 1, 
			1, 1, 1, 1, 1, 1, 1, 1, 
			0, 0, 0, 0, 0, 0, 0, 0, 0, 
			1, 1, 1, 1, 1, 1, 1, 1, 1, 
			0, 0, 0, 0, 0, 0, 0, 0, 
			1, 1, 1, 1, 1, 1, 1, 1, 1, 
			
			0, 0, 0, 0, 0, 0, 0, 0, 0, 
			1, 1, 1, 1, 1, 1, 1, 1, 
			0, 0, 0, 0, 0, 0, 0, 0, 0, 
			1, 1, 1, 1, 1, 1, 1, 1, 1,
			1, 1, 1, 1, 1, 1, 1, 1, 1, 
			1, 1, 1, 1, 1, 1, 1, 1, 1, 
			1, 1, 1, 1, 1, 1, 1, 1, 
			0, 0, 0, 0, 0, 0, 0, 0, 0, 
			0, 0, 0, 0, 0, 0, 0, 0, 
			1, 1, 1, 1, 1, 1, 1, 1, 1, 
			
			0, 0, 0, 0, 0, 0, 0, 0, 0, 
			0, 0, 0, 0, 0, 0, 0, 0, 0, 
			0, 0, 0, 0, 0, 0, 0, 0, 0, 
			0, 0, 0, 0, 0, 0, 0, 0, 
			0, 0, 0, 0, 0, 0, 0, 0, 
			1, 1, 1, 1, 1, 1, 1, 1, 1, 
			1, 1, 1, 1, 1, 1, 1, 1, 1, 
			0, 0, 0, 0, 0, 0, 0, 0, 0, 
			0, 0, 0, 0, 0, 0, 0, 0, 
			1, 1, 1, 1, 1, 1, 1, 1, 1, 
			
			0, 0, 0, 0, 0, 0, 0, 0, 0, 
			0, 0, 0, 0, 0, 0, 0, 0, 0, 
			0, 0, 0, 0, 0, 0, 0, 0, 
			0, 0, 0, 0, 0, 0, 0, 0, 
			1, 1, 1, 1, 1, 1, 1, 1, 1, 
			1, 1, 1, 1, 1, 1, 1, 1, 1, 
			1, 1, 1, 1, 1, 1, 1, 1, 1, 
			1, 1, 1, 1, 1, 1, 1, 1, 
			0, 0, 0, 0, 0, 0, 0, 0, 0, 
			1, 1, 1, 1, 1, 1, 1, 1, 1, 
			
			0, 0, 0, 0, 0, 0, 0, 0, 0, 
			0, 0, 0, 0, 0, 0, 0, 0, 0, 
			0, 0, 0, 0, 0, 0, 0, 2, 
			1, 1, 1, 1, 1, 1, 1, 1, 
			0, 0, 0, 0, 0, 0, 0, 0, 0, 
			1, 1, 1, 1, 1, 1, 1, 1, 1, 
			1, 1, 1, 1, 1, 1, 1, 1, 
			0, 0, 0, 0, 0, 0, 0, 0, 0, 
			0, 0, 0, 0, 0, 0, 0, 0, 0, 
			1, 1, 1, 1, 1, 1, 1, 1,
			
			0, 0, 0, 0, 0, 0, 0, 0, 0, 
			0, 0, 0, 0, 0, 0, 0, 0, 0, 
			0, 0, 0, 0, 0, 0, 0, 0, 0, 
			0, 0, 0, 0, 0, 0, 0, 0, 0, 
			0, 0, 0, 0, 0, 0, 0, 0, 
			1, 1, 1, 1, 1, 1, 1, 1, 1, 
			1, 1, 1, 1, 1, 1, 1, 1, 
			0, 0, 0, 0, 0, 0, 0, 0, 0, 
			0, 0, 0, 0, 0, 0, 0, 0, 
			1, 1, 1, 1, 1, 1, 1, 1, 1,
			
			0, 0, 0, 0, 0, 0, 0, 0, 0, 
			0, 0, 0, 0, 0, 0, 0, 0, 0, 
			0, 0, 0, 0, 0, 0, 0, 0, 0, 
			0, 0, 0, 0, 0, 0, 0, 0, 0, 
			0, 0, 0, 0, 0, 0, 0, 
			1, 1, 1, 1, 1, 1, 1, 1, 1, 
			1, 1, 1, 1, 1, 1, 1, 1, 1, 
			0, 0, 0, 0, 0, 0, 0, 0, 0, 
			0, 0, 0, 0, 0, 0, 0, 0, 
			1, 1, 1, 1, 1, 1, 1, 1, 1, 
			
			0, 0, 0, 0, 0, 0, 0, 0, 0, 
			0, 0, 0, 0, 0, 0, 0, 0, 0, 
			0, 0, 0, 0, 0, 0, 0, 0, 0, 
			0, 0, 0, 0, 0, 0, 0, 0, 
			1, 1, 1, 1, 1, 1, 1, 1, 1, 
			1, 1, 1, 1, 1, 1, 1, 1, 1, 
			1, 1, 1, 1, 1, 1, 1, 1, 
			0, 0, 0, 0, 0, 0, 0, 0, 0, 
			0, 0, 0, 0, 0, 0, 0, 0, 
			1, 1, 1, 1, 1, 1, 1, 1, 1, 
			

		]
		
		sr = 964e-9
		baud = 115200
		parity = 'N'
		dbits = 8
		
		x=RS232Decode()
		[vrx, vtrx] = x.f_Decode(sr, baud, dbits, parity, rxdata)

		vrefrx = [	'S', 1, 1, 0, 1, 1, 1, 1, 0, 'P', 'S', 1, 0, 0, 0, 0, 1, 1, 0, 'P',
					'S', 0, 1, 1, 1, 1, 0, 1, 0, 'P', 'S', 1, 0, 1, 1, 1, 1, 0, 0, 'P', 
					'S', 0, 0, 0, 0, 1, 1, 0, 0, 'P', 'S', 0, 0, 0, 1, 1, 1, 1, 0, 'P',
					'S', 0, 0, 1, 0, 1, 1, 0, 0, 'P', 'S', 0, 0, 0, 0, 1, 1, 0, 0, 'P',
					'S', 0, 0, 0, 0, 1, 1, 0, 0, 'P', 'S', 0, 0, 0, 1, 1, 1, 0, 0, 'P'
					]
					
		self.assertEqual(vrx, vrefrx)
		
		[stat, data] = x.f_GetBytes(dbits, parity, vrx)
		vrefdata = ['7B', '61', '5E', '3D', '30', '78', '34', '30', '30', '38']
		vrefstat = ['OK', 'OK', 'OK', 'OK', 'OK', 'OK', 'OK', 'OK', 'OK', 'OK' ]
		vrefttx = [65, 152, 238, 325, 412, 499, 586, 672, 759, 846]
		
		self.assertEqual(data, vrefdata)
		self.assertEqual(stat, vrefstat)
		self.assertEqual(vtrx, vrefttx)
	
	
	def test_RealTestRx(self):
		rxdata = [ 	1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
					1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 
					
					0, 0, 0, 0, 0, 0, 0, 0, 0, 
					1, 1, 1, 1, 1, 1, 1, 1, 1, 
					1, 1, 1, 1, 1, 1, 1, 1, 
					0, 0, 0, 0, 0, 0, 0, 0, 0, 
					1, 1, 1, 1, 1, 1, 1, 1, 1, 
					1, 1, 1, 1, 1, 1, 1, 1, 1, 
					1, 1, 1, 1, 1, 1, 1, 1, 1, 
					1, 1, 1, 1, 1, 1, 1, 1, 
					0, 0, 0, 0, 0, 0, 0, 0, 
					1, 1, 1, 1, 1, 1, 1, 1, 1, 
					
					0, 0, 0, 0, 0, 0, 0, 0, 0, 
					1, 1, 1, 1, 1, 1, 1, 1, 
					0, 0, 0, 0, 0, 0, 0, 0, 0, 
					0, 0, 0, 0, 0, 0, 0, 0, 0, 
					0, 0, 0, 0, 0, 0, 0, 0, 0, 
					0, 0, 0, 0, 0, 0, 0, 0, 
					1, 1, 1, 1, 1, 1, 1, 1, 
					1, 1, 1, 1, 1, 1, 1, 1, 1, 
					0, 0, 0, 0, 0, 0, 0, 0, 0, 
					1, 1, 1, 1, 1, 1, 1, 1, 1, 
					
					0, 0, 0, 0, 0, 0, 0, 0, 0, 
					0, 0, 0, 0, 0, 0, 0, 0, 
					1, 1, 1, 1, 1, 1, 1, 1, 1, 
					1, 1, 1, 1, 1, 1, 1, 1, 1, 
					1, 1, 1, 1, 1, 1, 1, 1, 1, 
					1, 1, 1, 1, 1, 1, 1, 1, 
					0, 0, 0, 0, 0, 0, 0, 0, 0, 
					1, 1, 1, 1, 1, 1, 1, 1, 
					0, 0, 0, 0, 0, 0, 0, 0, 0, 
					1, 1, 1, 1, 1, 1, 1, 1, 1, 
					
					0, 0, 0, 0, 0, 0, 0, 0, 0, 
					0, 0, 0, 0, 0, 0, 0, 0, 0, 
					0, 0, 0, 0, 0, 0, 0, 0, 
					1, 1, 1, 1, 1, 1, 1, 1, 
					0, 0, 0, 0, 0, 0, 0, 0, 0, 
					1, 1, 1, 1, 1, 1, 1, 1, 1, 
					1, 1, 1, 1, 1, 1, 1, 1, 
					0, 0, 0, 0, 0, 0, 0, 0, 0, 
					0, 0, 0, 0, 0, 0, 0, 0, 0, 
					1, 1, 1, 1, 1, 1, 1, 1,
					
					0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
					1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 
					
					0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 
					0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 
					
					0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0,	0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 
					1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 
					
					1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1 ]

		sr = 964e-9
		baud = 115200
		parity = 'N'
		dbits = 8
		
		x=RS232Decode()
		[vrx, vtrx] = x.f_Decode(sr, baud, dbits, parity, rxdata)

		vrefrx = [	'S', 1, 1, 0, 1, 1, 1, 1, 0, 'P', 'S', 1, 0, 0, 0, 0, 1, 1, 0, 'P',
					'S', 0, 1, 1, 1, 1, 0, 1, 0, 'P', 'S', 0, 0, 1, 0, 1, 1, 0, 0, 'P', 
					'S', 0, 1, 1, 0, 0, 0, 1, 0, 'P', 'S', 1, 1, 0, 0, 1, 1, 0, 0, 'P',
					'S', 1, 0, 1, 1, 1, 1, 1, 0, 'P']
		self.assertEqual(vrx, vrefrx)
		
		[stat, data] = x.f_GetBytes(dbits, parity, vrx)
		vrefdata = ['7B', '61', '5E', '34', '46', '33', '7D']
		vrefstat = ['OK', 'OK', 'OK', 'OK', 'OK', 'OK', 'OK' ]
		vrefttx = [ 119, 206, 293, 380, 466, 553, 640]
		
		self.assertEqual(data, vrefdata)
		self.assertEqual(stat, vrefstat)
		self.assertEqual(vtrx, vrefttx)
		
		
	def test_GetBytesD8PO(self):
		rxdata = ['S', 1, 0, 1, 1, 1, 0, 1, 0, 0, 'P', 'S', 0, 0, 1, 1, 1, 0, 0, 0, 1, 'P']
		dbits = 8
		parity = 'O'
		
		x=RS232Decode()
		[stat, data] = x.f_GetBytes(dbits, parity, rxdata)
		vrefdata = ['5D', '1C']
		vrefstat = ['PE', 'OK']
		self.assertEqual(data, vrefdata)
		self.assertEqual(stat, vrefstat)
		
	def test_GetBytesD8PE(self):
		rxdata = ['S', 1, 0, 1, 1, 1, 0, 1, 0, 0, 'P', 'S', 0, 0, 1, 1, 1, 0, 0, 0, 1, 'P']
		dbits = 8
		parity = 'E'
		
		x=RS232Decode()
		[stat, data] = x.f_GetBytes(dbits, parity, rxdata)
		vrefdata = ['5D', '1C']
		vrefstat = ['OK', 'PE']
		self.assertEqual(data, vrefdata)
		self.assertEqual(stat, vrefstat)
		
	def test_GetBytesD8PN(self):
		rxdata = ['S', 1, 0, 1, 1, 1, 0, 1, 0, 'P', 'S', 0, 0, 1, 1, 1, 0, 0, 0, 'P']
		dbits = 8
		parity = 'N'
		
		x=RS232Decode()
		[stat, data] = x.f_GetBytes(dbits, parity, rxdata)
		vrefdata = ['5D', '1C']
		vrefstat = ['OK', 'OK']
		self.assertEqual(data, vrefdata)
		self.assertEqual(stat, vrefstat)
		
	# Test Attribute control
	def test_DecodeMultiByteDB8N(self):
		rx = [0, 4.8, 4.9, 4.7, 0.3, 0.4, 0.2, 4.8, 4.9, 4.7, 0.3, 0.4, 0.2, 4.8, 4.9, 4.7, 4.8, 4.9, 4.7, 4.8, 4.9, 4.7, 0.3, 0.4, 0.2, 4.8, 4.9, 4.7, 0.3, 0.4, 0.2, 4.8, 4.9, 4.7, 4.8, 4.9, 4.7, 
		4.8, 4.8, 4.9, 4.7, 0.3, 0.4, 0.2,  0.3, 0.4, 0.2, 0.3, 0.4, 0.2, 4.8, 4.9, 4.7, 4.8, 4.9, 4.7, 4.8, 4.9, 4.7, 0.3, 0.4, 0.2, 0.3, 0.4, 0.2, 0.3, 0.4, 0.2, 4.8, 4.9, 4.7, 4.8, 4.9, 4.7]
		 
		sr = 2.89E-6
		baud = 115200
		pol = 0
		parity = 'N'
		dbits = 8
		
		x=RS232Decode()
		x.f_SetThresholdType('TTL')

		rxdata = x.f_Threshold(rx)
		rxdatap = x.f_Polarity(pol, rxdata)
	
		[vrx, vtrx] = x.f_Decode(sr, baud, dbits, parity, rxdatap)

		vrefrx = ['S', 1, 0, 1, 1, 1, 0, 1, 0, 'P', 'S', 0, 0, 1, 1, 1, 0, 0, 0, 'P']
		self.assertEqual(vrefrx, vrx)
		vreftrx = [4, 41]
		self.assertEqual(vreftrx, vtrx)
		

	def test_DecodeSingleByteDB7EvenParity(self):
		rx = [0, 4.8, 4.9, 4.7, 0.3, 0.4, 0.2, 4.8, 4.9, 4.7, 0.3, 0.4, 0.2, 4.8, 4.9, 4.7, 4.8, 4.9, 4.7, 0.3, 0.4, 0.2, 4.8, 4.9, 4.7, 0.3, 0.4, 0.2, 4.8, 4.9, 4.7, 4.8, 4.9, 4.7, 4.8, 4.9, 4.7]
		 
		sr = 2.89E-6
		baud = 115200
		pol = 0
		parity = 'E'
		dbits = 7
		
		x=RS232Decode()
		x.f_SetThresholdType('TTL')

		rxdata = x.f_Threshold(rx)
		rxdatap = x.f_Polarity(pol, rxdata)

		[vrx, vtrx] = x.f_Decode(sr, baud, dbits, parity, rxdatap)
		
		vrefrx = ['S', 1, 0, 1, 1, 0, 1, 0, 1, 'P']
		self.assertEqual(vrefrx, vrx)
		
	def test_DecodeSingleByteEvenParity(self):
		rx = [0, 4.8, 4.9, 4.7, 0.3, 0.4, 0.2, 4.8, 4.9, 4.7, 0.3, 0.4, 0.2, 4.8, 4.9, 4.7, 4.8, 4.9, 4.7, 4.8, 4.9, 4.7, 0.3, 0.4, 0.2, 4.8, 4.9, 4.7, 0.3, 0.4, 0.2, 4.8, 4.9, 4.7, 4.8, 4.9, 4.7, 4.8, 4.9, 4.7]
		 
		sr = 2.89E-6
		baud = 115200
		pol = 0
		parity = 'E'
		dbits = 8
		
		x=RS232Decode()
		x.f_SetThresholdType('TTL')

		rxdata = x.f_Threshold(rx)
		rxdatap = x.f_Polarity(pol, rxdata)

		[vrx, vtrx] = x.f_Decode(sr, baud, dbits, parity, rxdatap)
		
		vrefrx = ['S', 1, 0, 1, 1, 1, 0, 1, 0, 1, 'P']
		self.assertEqual(vrefrx, vrx)
		
	# Test Attribute control
	def test_DecodeSingleByteNoParity(self):
		rx = [0, 4.8, 4.9, 4.7, 0.3, 0.4, 0.2, 4.8, 4.9, 4.7, 0.3, 0.4, 0.2, 4.8, 4.9, 4.7, 4.8, 4.9, 4.7, 4.8, 4.9, 4.7, 0.3, 0.4, 0.2, 4.8, 4.9, 4.7, 0.3, 0.4, 0.2, 4.8, 4.9, 4.7, 4.8, 4.9, 4.7]
		#tx = [0, 4.8, 4.9, 4.7, 0.3, 0.4, 0.2,  0.3, 0.4, 0.2, 0.3, 0.4, 0.2, 4.8, 4.9, 4.7, 4.8, 4.9, 4.7, 4.8, 4.9, 4.7, 0.3, 0.4, 0.2, 0.3, 0.4, 0.2, 0.3, 0.4, 0.2, 4.8, 4.9, 4.7, 4.8, 4.9, 4.7]
		 
		sr = 2.89E-6
		baud = 115200
		pol = 0
		parity = 'N'
		dbits = 8
		
		x=RS232Decode()
		x.f_SetThresholdType('TTL')

		rxdata = x.f_Threshold(rx)
		rxdatap = x.f_Polarity(pol, rxdata)
	
		[vrx, vtrx] = x.f_Decode(sr, baud, dbits, parity, rxdatap)

		vrefrx = ['S', 1, 0, 1, 1, 1, 0, 1, 0, 'P']
		self.assertEqual(vrefrx, vrx)
		
	def test_PolarityPos(self):
		rx = [0, 4.8, 4.9, 4.7, 0.3, 0.4, 0.2, 4.8, 4.9, 4.7, 0.3, 0.4, 0.2, 4.8, 4.9, 4.7, 4.8, 4.9, 4.7, 4.8, 4.9, 4.7, 0.3, 0.4, 0.2, 4.8, 4.9, 4.7, 0.3, 0.4, 0.2, 4.8, 4.9, 4.7, 4.8, 4.9, 4.7]
		
		x=RS232Decode()
		x.f_SetThresholdType('TTL')
		rxdata = x.f_Threshold(rx)
		rxdatap = x.f_Polarity(0, rxdata)
		
		vrefrx = [0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1]
		self.assertEqual(vrefrx, rxdatap)
		
	def test_PolarityNeg(self):
		rx = [0, 4.8, 4.9, 4.7, 0.3, 0.4, 0.2, 4.8, 4.9, 4.7, 0.3, 0.4, 0.2, 4.8, 4.9, 4.7, 4.8, 4.9, 4.7, 4.8, 4.9, 4.7, 0.3, 0.4, 0.2, 4.8, 4.9, 4.7, 0.3, 0.4, 0.2, 4.8, 4.9, 4.7, 4.8, 4.9, 4.7]
		
		x=RS232Decode()
		x.f_SetThresholdType('TTL')
		rxdata = x.f_Threshold(rx)
		rxdatap = x.f_Polarity(1, rxdata)
		
		vrefrx = [1, 0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0]
		#vrefrx = [0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1]
		self.assertEqual(vrefrx, rxdatap)
		
	def test_BitDurationOne(self):
		rx = [0, 4.8, 4.9, 4.7, 0.3, 0.4, 0.2, 4.8, 0.3, 4.7, 0.3, 4.5, 0.2]
		sr = 2.89E-6
		baud = 115200
		
		x=RS232Decode()
		x.f_SetThresholdType('TTL')
		rxdata = x.f_Threshold(rx)
		x.f_GetBitDuration(sr, baud)
		# check valid one
		idx = 1
		[dur, skip] = x.f_CheckBitDuration(rxdata, idx)
		self.assertEqual(1, dur)	
	
	def test_BitDurationZero(self):
		rx = [0, 4.8, 4.9, 4.7, 0.3, 0.4, 0.2, 4.8, 0.3, 4.7, 0.3, 4.5, 0.2]
		sr = 2.89E-6
		baud = 115200
		
		x=RS232Decode()
		x.f_SetThresholdType('TTL')
		x.f_GetBitDuration(sr, baud)
		rxdata = x.f_Threshold(rx)
	
		
		# check valid zero
		idx = 4
		[dur, skip] = x.f_CheckBitDuration(rxdata, idx)
		self.assertEqual(0, dur)	
	
	def test_BitDurationSpikeOne(self):
		rx = [0, 4.8, 4.9, 4.7, 0.3, 0.4, 0.2, 4.8, 0.3, 4.7, 0.3, 4.5, 0.2]
		sr = 2.89E-6
		baud = 115200
		
		x=RS232Decode()
		x.f_SetThresholdType('TTL')
		x.f_GetBitDuration(sr, baud)
		rxdata = x.f_Threshold(rx)	
		
		# check in valid zero
		idx = 6
		[dur, skip] = x.f_CheckBitDuration(rxdata, idx)
		#self.assertEqual('X', dur)		
		self.assertEqual(0, dur)		
		
	def test_BitDurationSpikeZero(self):
		rx = [0, 4.8, 4.9, 4.7, 0.3, 0.4, 0.2, 4.8, 0.3, 4.7, 0.3, 4.5, 0.2]
		sr = 2.89E-6
		baud = 115200
		
		x=RS232Decode()
		x.f_SetThresholdType('TTL')
		x.f_GetBitDuration(sr, baud)
		rxdata = x.f_Threshold(rx)	
		
		# check in valid zero
		idx = 7
		[dur, skip] = x.f_CheckBitDuration(rxdata, idx)
		#self.assertEqual('X', dur)	
		self.assertEqual(1, dur)	

	def test_BitDurationStart(self):
		rx = [0, 4.8, 4.9, 4.7, 0.3, 0.4, 0.2, 4.8, 4.9, 4.7, 0.3, 0.4, 0.2, 4.8, 4.9, 4.7, 4.8, 4.9, 4.7, 4.8, 4.9, 4.7, 0.3, 0.4, 0.2, 4.8, 4.9, 4.7, 0.3, 0.4, 0.2, 4.8, 4.9, 4.7, 4.8, 4.9, 4.7]
		sr = 2.89E-6
		baud = 115200
		
		x=RS232Decode()
		x.f_SetThresholdType('TTL')
		x.f_GetBitDuration(sr, baud)
		rxdata = x.f_Threshold(rx)	
		
		# check in valid zero
		idx = 7
		[dur, skip] = x.f_CheckBitDuration(rxdata, idx)
		self.assertEqual(1, dur)	
		idx = 10
		[dur, skip] = x.f_CheckBitDuration(rxdata, idx)
		self.assertEqual(0, dur)		
	
	
	def test_BitDurationSync(self):
		rxdata = [ 	1, 1, 1, 1, 1, 1, 1, 1, 1, 
					0, 0, 0, 0, 0, 0, 0, 0, 0, 
					1, 1, 1, 1, 1, 1, 1, 1, 1, 
					1, 1, 1, 1, 1, 1, 1, 1, 
					0, 0, 0, 0, 0, 0, 0, 0, 0, 
					1, 1, 1, 1, 1, 1, 1, 1, 1, 
					1, 1, 1, 1, 1, 1, 1, 1, 1, 
					1, 1, 1, 1, 1, 1, 1, 1, 1, 
					1, 1, 1, 1, 1, 1, 1, 1, 
					0, 0, 0, 0, 0, 0, 0, 0, 
					1, 1, 1, 1, 1, 1, 1, 1, 1, 
					]
		sr = 964e-9
		baud = 115200
		parity = 'N'
		dbits = 8
		
		x=RS232Decode()
		x.f_GetBitDuration(sr, baud)
		
		idx = 0
		[dur, skip] = x.f_CheckBitDuration(rxdata, idx)
		self.assertEqual(1, dur)	
		self.assertEqual(8, skip)	

		
		idx = 27
		[dur, skip] = x.f_CheckBitDuration(rxdata, idx)
		self.assertEqual(1, dur)	
		self.assertEqual(7, skip)	


					
	def test_GetBitDuration(self):
		sr = 2.89E-6
		baud = 115200
		
		x=RS232Decode()
		x.f_SetThresholdType('TTL')
		bitdur = x.f_GetBitDuration(sr, baud)	
		
		# check in valid zero
		self.assertEqual(3, bitdur)	


		