from ..base.Dat import Dat

class VerbWord():
	def __init__(self, filename1, filename2):
		self.__vmDat = Dat(filename=filename1)
		self.__vdDat = Dat(filename=filename2)
		self.__tagV = 'v'

	def adjustTag(self, sentence):
		if(not self.__vmDat or not self.__vdDat):
			return
		for i in range(len(sentence)-1):
			if(sentence[i].tag == self.__tagV and sentence[i+1].tag == self.__tagV):
				if(self.__vmDat.match(sentence[i].word) != -1):
					sentence[i].tag = 'vm'
				elif(self.__vdDat.match(sentence[i+1].word) != -1):
					sentence[i+1].tag = 'vd'


