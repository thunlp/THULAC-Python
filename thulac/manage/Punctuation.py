#coding: utf-8
from ..base.Dat import Dat

class Punctuation():
	def __init__(self, filename):
		self.__pDat = Dat(filename)

	def adjustSeg(self, sentence):
		if(not self.__pDat):
			return
		tmpVec = []
		for i in range(len(sentence)):
			if(i>=len(sentence)):
				break
			tmp = sentence[i]
			if(self.__pDat.getInfo(tmp) >= 0):
				continue
			del tmpVec[:]
			for j in range(i+1, len(sentence)):
				tmp += sentence[j]
				if(self.__pDat.getInfo(tmp) >= 0):
					break
				tmpVec.append(tmp)
			vecSize = len(tmpVec)

			for k in range(vecSize-1, -1, -1):
				tmp = tmpVec[k]
				if(self.__pDat.match(tmp) != -1):
					for j in range(i+1, i+k+2):
						sentence[i] += sentence[j]
					del sentence[i+1:i+k+2]
					break
		del tmpVec[:]

	def adjustTag(self, sentence):
		if(not self.__pDat):
			return
		tmpVec = []
		findMulti = False
		for i in range(len(sentence)):
			if (i >= len(sentence)):
				break
			tmp = sentence[i][0]
			if(self.__pDat.getInfo(tmp) >= 0):
				continue
			del tmpVec[:]

			for j in range(i+1, len(sentence)):
				tmp += sentence[j][0]
				if(self.__pDat.getInfo(tmp) >= 0):
					break
				tmpVec.append(tmp)
			vecSize = len(tmpVec)

			findMulti = False
			for k in range(vecSize-1, -1, -1):
				tmp = tmpVec[k]
				if(self.__pDat.match(tmp) != -1):
					for j in range(i+1, i+k+2):
						sentence[i] = (sentence[i][0] + sentence[j][0], sentence[i][1], 'w')
					del sentence[i+1:i+k+2]
					findMulti = True
					break
			if(not findMulti):
				if(self.__pDat.match(sentence[i][0]) != -1):
					sentence[i] = (sentence[i][0], sentence[i][1], 'w')
			del tmpVec[:]


if __name__ == '__main__':
	class WordWithTag:
		word = []
		tag = ""

		def __init__(self, word, tag):
			self.word = word
			self.tag = tag


	time = b = [i for i in "1988".decode('utf-8')]
	year = ["年".decode('utf-8')]
	dot1 = [".".decode('utf-8')]
	dot2 = [".".decode('utf-8')]
	dot3 = [".".decode('utf-8')]
	# print time
	a = [[".".decode('utf-8')], [".".decode('utf-8')],WordWithTag(dot1, 'n'),WordWithTag(dot2, 'n'),WordWithTag(dot3, 'n')]
	# b = [ord(i) for i in "月".decode('utf-8')]
	pun = Punctuation('../models/singlepun.dat')
	# for i in '月亮'.decode('utf-8'):
	#   print ord(i)
	pun.adjustTag(a)
	print(a)