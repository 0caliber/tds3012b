# License conditions are given in LICENSE.TXT
# This code is licnesed under the MIT License 
# Copyright (c) 2017 Ilialex Research Lab
# www.ilialex.gr, blog.ilialex.gr
#

class MyPrint:
	def __init__(self, gEnable):
		self.gEnable = gEnable
		
	
	def	f_Print(self, *params):
		if	self.gEnable:
			s	=	''
			for	mind in params:
				s = s + str(mind)
			print (s)
		