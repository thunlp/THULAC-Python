#coding = utf-8
import struct
import os


class Dat:

    def __init__(self, filename):
        inputfile = open(filename, "rb")
        self.datSize = int(os.path.getsize(filename) / 8)
        s = inputfile.read(8 * self.datSize)
        tmp = "<"+str(self.datSize*2)+"i"
        self.dat = struct.unpack(tmp, s)
        self.dat = tuple(self.dat)
        inputfile.close()

    
    def printDat(self, filename):
        f = open(filename, "w")
        for i in range(self.datSize):
            f.write(""+self.dat[2 * i]+" "+self.dat[2 * i + 1]+"\n")
        f.close()
    
    def getIndex(self, base, character):
        ind = self.dat[2 * base] + character
        if((ind >= self.datSize) or self.dat[2 * ind + 1] != base):
            return -1
        return ind
    
    def search(self, sentence, bs, es):
        bs = []
        es = []
        empty = True
        for offset in range(len(sentence)):
            preBase = 0
            preInd = 0
            ind = 0
            for i in range(offset, len(sentence)):
                ind = preBase + sentence[i]
                if(ind < 0 or ind >= self.datSize or self.dat[2 * ind + 1] != preInd):
                    break
                preInd = ind
                preBase = self.dat[2 * ind]
                ind = preBase
                if(not (ind < 0 or ind >= self.datSize or self.dat[2 * ind + 1] != preInd)):
                    bs.append(offset)
                    es.append(i + 1)
                    if(empty):
                        empty = False
        return not empty
    
    def match(self, word):
        ind = 0
        base = 0
        for i in range(len(word)):
            ind = self.dat[2 * ind] + ord(word[i])
            if((ind > self.datSize) or (self.dat[2 * ind + 1] != base)):
                return -1
            base = ind
        ind = self.dat[2 * base]
        if((ind < self.datSize) and (self.dat[2 * ind + 1] == base)):
            return ind
        return -1

    def update(self, word, value):
        base = self.match(word)
        if(base >= 0):
            self.dat[2 * base] = value

    def getInfo(self, prefix):
        ind = 0
        base = 0
        for i in range(len(prefix)):
            ind = self.dat[2 * ind] + ord(prefix[i])
            if((ind >= self.datSize) or self.dat[2 * ind + 1] != base):
                return i
            base = ind
        return -base

    def getDatSize(self):
        return self.datSize
    
    def getDat(self):
        return self.dat
    
if __name__ == '__main__':
    dat = Dat("cws_dat.bin")
    
        
