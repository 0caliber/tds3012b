
import	visa
from MyPrint import *

class DSOGetSamples:
	def __init__(self, instr_addr, gEnable, SampleStart=1, SampleStop=10000):
		print 'DSO Get Samples'
		
		self.gEnable = gEnable
		self.MyPrint = MyPrint(gEnable)
		
		self.cmd_frmt	=	"DATA:ENCDG	ASCIi;WIDTH	1"
		#cmd_frmt	=	"DATA:ENCDG	RIBinary;WIDTH	1"
		self.cmd_samples = "HORIZONTAL:RECORDLENGTH	10000"
		self.cmd_start	=	"DATA:START %d" %SampleStart
		self.cmd_stop	=	"DATA:STOP %d" %SampleStop
		self.cmd_src1	=	"DATA:SOURCE CH1"
		self.cmd_src2	=	"DATA:SOURCE CH2"

		self.cmd_acq	=	"ACQUIRE:STATE STOP"
		self.cmd_WfmScale = "WFMPRe?"
		self.cmd_getraw	=	"CURVe?"
		#cmd_save	=	"SAVe:EVENTtable:BUS%d	%s"	%(bus,	usbfname)
		#cmd_get	=	"FILESystem:READFile	%s"	%usbfname

		
		try:
			self.mso = visa.instrument(instr_addr)
		except:
			print "Cannot Open Instrument %s" %instr_addr
			raise IOError
		
		if	self.gEnable	==	1:	
			print self.mso.ask("*IDN?")
			
			
	def __del__(self):
		self.mso.close()
	
	def f_Exit(self):
		self.mso.close()
		
	def f_Setup(self):
		self.MyPrint.f_Print("Format Set.")
		self.mso.write(self.cmd_frmt)
		self.MyPrint.f_Print("Stop Acquisitions.")
		self.mso.write(self.cmd_acq)
		self.MyPrint.f_Print("Data Start Pointer.")
		self.mso.write(self.cmd_start)
		self.MyPrint.f_Print("Data Stop Pointer.")
		self.mso.write(self.cmd_stop)
			
			
	def f_GetChannel(self, chan):
		cmd_src = "DATA:SOURCE CH%d" %chan
		self.MyPrint.f_Print("Source Channel %d" %chan)
		self.mso.write(cmd_src)
		self.MyPrint.f_Print("Get Waveform scaling and headers.")
		wfmhdr = self.mso.ask(self.cmd_WfmScale)
		self.MyPrint.f_Print(wfmhdr)
		self.MyPrint.f_Print("Get Curve Data.")
		self.mso.write(self.cmd_getraw)

		try:
			data = self.mso.read()
		except:
			print "Can't Get Curve data."
			raise IOError, "Can't Get Curve data."
			
		return wfmhdr, data
		
	def f_ScaleVolt(self, wfmhdr, data):
		v=data.split(',')
		length = len(v)

		# volt = (point - yoff) * ymult + yzero
		fields	=	wfmhdr.split(';')

		yoff	= eval(fields[14])
		ymult	= eval(fields[12])
		yzero	= eval(fields[13])
		chan = []
		if (length > 1):
			for idx in range(1, length):
				point	= eval(v[idx])
				volt	= (point - yoff) * ymult + yzero
				chan.append(volt)
		else:
			print "Data Captured too small... some error"
			raise ValueError, "Data Captured too small... some error"
	
		return chan