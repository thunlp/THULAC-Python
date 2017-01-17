#coding = utf-8
# from ..base import Dat
import time

class CBNGramFeature:

    SENTENCE_BOUNDARY = '#'
    SEPERATOR = "_"
    maxLength = 0
    uniBases = []
    biBases = []
    datSize = []
    dat = []
    values = {}

    def __init__(self, myDat, model):
        self.SEPERATOR = ' '
        self.datSize = myDat.getDatSize()
        self.dat = myDat.getDat()
        self.model = model
        self.maxLength = 50000
        self.uniBases = [0 for i in range(self.maxLength + 2)]
        self.biBases = [0 for i in range(self.maxLength + 4)]
    
    def addValues(self, valueOffset, base, dele, tmp):
        ind = self.dat[2 * base] + dele
        if(ind >= self.datSize or self.dat[2 * ind + 1] != base):
            return
        # offset = self.dat[2 * ind]
        weightOffset = self.model.l_size * self.dat[2 * ind]
        if(self.model.l_size == 4):
            # pass
            tmp[0] += self.model.fl_weights[weightOffset]
            tmp[1] += self.model.fl_weights[weightOffset + 1]
            tmp[2] += self.model.fl_weights[weightOffset + 2]
            tmp[3] += self.model.fl_weights[weightOffset + 3]
        else:
            for i in range(self.model.l_size):
                self.values[valueOffset + i] += self.model.fl_weights[weightOffset + i]
    
    def findBases(self, datSize, ch1, ch2):
        result = []
        uniBase = 0
        biBase = 0
        ch1 = ord(ch1)
        ch2 = ord(ch2)
        if(ch1 > 32 and ch1 < 128):
            ch1 += 65248
        if(ch2 > 32 and ch2 < 128):
            ch2 += 65248
        if(ch1 >= datSize or 2 *self.dat[2 * ch1 + 1] != 0):
            # uniBase = -1
            # biBase = -1
            # result = (-1, -1)
            return -1, -1

        uniBase = self.dat[2 * ch1] + ord(self.SEPERATOR)

        ind = self.dat[2 * ch1] + ch2
        if(ind >= datSize or self.dat[2 * ind + 1] != ch1):
            return uniBase, -1

        biBase = self.dat[2 * ind] + ord(self.SEPERATOR)
        return uniBase, biBase

    def putValues(self, sequence, mylen, values):
        if(mylen >= self.maxLength):
            print("larger than max")
            return 1

        self.values = values
        self.uniBases[0], self.biBases[0] = self.findBases(self.datSize, self.SENTENCE_BOUNDARY, self.SENTENCE_BOUNDARY)
        
        self.uniBases[0], self.biBases[1] = self.findBases(self.datSize, self.SENTENCE_BOUNDARY, sequence[0])

        for i in range(mylen - 1):
            self.uniBases[i + 1], self.biBases[i + 2] = self.findBases(self.datSize, sequence[i], sequence[i+1])

        self.uniBases[mylen], self.biBases[mylen + 1] = self.findBases(self.datSize, sequence[mylen - 1], self.SENTENCE_BOUNDARY)
        
        self.uniBases[mylen+1], self.biBases[mylen+2] = self.findBases(self.datSize, self.SENTENCE_BOUNDARY, self.SENTENCE_BOUNDARY)

        for i in range(mylen):
            tmp = [0, 0, 0, 0]
            valueOffset = i * self.model.l_size
            if((self.uniBases[i + 1]) != -1):
                self.addValues(valueOffset, self.uniBases[i + 1], 49, tmp)
            if((self.uniBases[i]) != -1):
                self.addValues(valueOffset, self.uniBases[i], 50, tmp)
            if((self.uniBases[i + 2]) != -1):
                self.addValues(valueOffset, self.uniBases[i + 2], 51, tmp)
            if(self.biBases[i + 1] != -1):
                self.addValues(valueOffset, self.biBases[i + 1], 49, tmp)
            if((self.biBases[i + 2]) != -1):
                self.addValues(valueOffset, self.biBases[i + 2], 50, tmp)
            if((self.biBases[i]) != -1):
                self.addValues(valueOffset, self.biBases[i], 51, tmp)
            if((self.biBases[i + 3]) != -1):
                self.addValues(valueOffset, self.biBases[i + 3], 52, tmp)
            self.values[valueOffset] += tmp[0]
            self.values[valueOffset + 1] += tmp[1]
            self.values[valueOffset + 2] += tmp[2]
            self.values[valueOffset + 3] += tmp[3]
        return 0
