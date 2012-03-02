
class MyPrint:
	def __init__(self, gEnable):
		self.gEnable = gEnable
		
	
	def	f_Print(self, *params):
		if	self.gEnable:
			s	=	''
			for	mind in params:
				s = s + str(mind)
			print s
		