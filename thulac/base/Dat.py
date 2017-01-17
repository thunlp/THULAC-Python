#coding: utf-8
import struct
import os
import functools
import sys

class Dat:

    def __init__(self, filename=None, datSize=None, oldDat=None):
        if(filename):
            inputfile = open(filename, "rb")
            self.datSize = int(os.path.getsize(filename) / 8)
            s = inputfile.read(8 * self.datSize)
            tmp = "<"+str(self.datSize*2)+"i"
            self.dat = struct.unpack(tmp, s)
            self.dat = tuple(self.dat)
            inputfile.close()
        else:
            self.dat = oldDat
            self.dat = tuple(self.dat)
            self.datSize = datSize



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

def compareWords(firstLex, secondLex):
    minSize = min(len(firstLex[0]), len(secondLex[0]))
    for i in range(minSize):
        if(firstLex[0][i] > secondLex[0][i]):
            return 1
        if(firstLex[0][i] < secondLex[0][i]):
            return -1
    if(len(firstLex[0]) > len(secondLex[0])):
        return 1
    if(len(firstLex[0]) < len(secondLex[0])):
        return -1
    return 0


class DATMaker(Dat):
    def __init__(self):
        self.head = 0
        self.tail = 0
        self.datSize = 1
        self.dat = [1, -1]



    def use(self, ind):
        if(self.dat[2 * ind + 1] >= 0):
            print("cell reused!")
        if(self.dat[2 * ind] == 1):
            self.head = self.dat[2 * ind + 1]
        else:
            self.dat[2 * (-self.dat[2 * ind]) +1] = self.dat[2 * ind +1]
        if(self.dat[2 * ind + 1] == -self.datSize):
            self.tail = self.dat[2 * ind]
        else:
            self.dat[2 * (-self.dat[2 * ind + 1])] = self.dat[2 * ind]
        self.dat[2 * ind + 1] = ind

    def extends(self):
        oldSize = self.datSize
        self.datSize *= 2
        # self.dat = [self.dat[i] if i < 2*oldSize else 0 for i in range(2*self.datSize)]
        for i in range(oldSize):
            self.dat.append(-(oldSize + i - 1))
            self.dat.append(-(oldSize + i + 1))
        self.dat[2 * oldSize] = self.tail
        if(-self.tail >= 0):
            self.dat[2 * (-self.tail) + 1] = -oldSize;
        self.tail = -(oldSize * 2 - 1)

    def shrink(self):
        last = self.datSize - 1
        while(self.dat[2 * last + 1] < 0):
            last -= 1
        self.datSize = last + 1
        self.dat = [self.dat[i] for i in range(2 * self.datSize)]

    def alloc(self, offsets):
        size = len(offsets)
        base = -self.head

        while(1):
            if(base == self.datSize):
                self.extends()
            if(size):
                while(2 * (base + ord(offsets[size - 1])) >= self.datSize):
                    self.extends()
            flag = True

            if(self.dat[2 * base + 1] >= 0):
                flag = False
            else:
                for i in range(size):
                    if(self.dat[2 * (base + ord(offsets[i])) + 1] >= 0 or self.dat[2 * (base + ord(offsets[i])) + 1] >=0):
                        flag = False
                        break
            if(flag):
                self.use(base)
                for i in range(size):
                    self.use(base + ord(offsets[i]))
                return base
            if(self.dat[2 * base + 1] == -self.datSize):
                self.extends()
            base = -self.dat[2 * base + 1]

    def genChildren(self, lexicon, start, prefix, children):
        del children[:]
        l = len(prefix)
        for ind in range(start, len(lexicon)):
            word = lexicon[ind][0]
            if(len(word) < l):
                return
            for i in range(l):
                if(word[i] != prefix[i]):
                    return
            if(len(word) > l):
                a = word[l]
                if(not children or word[l] != children[-1]):
                    children.append(word[l])


    def assign(self, check, offsets, isWord=False):
        base = self.alloc(offsets)
        self.dat[2 * base] = 0
        if(isWord):
            self.dat[2 * base + 1] = check
        else:
            self.dat[2 * base + 1] = base
        for i in range(len(offsets)):
            self.dat[2 * (base + ord(offsets[i]))] = 0
            self.dat[2 * (base + ord(offsets[i])) + 1] = check
        self.dat[2 * check] = base
        return base

    def makeDat(self, lexicon, noPrefix=0):
        # print(type(lexicon))
        if(sys.version_info[0] == 2):
            lexicon = sorted(lexicon, cmp=compareWords)
        else:
            lexicon = sorted(lexicon, key=functools.cmp_to_key(compareWords))
        # for i in lexicon:
        #     print i[0].encode('utf-8')
        size = len(lexicon)
        children = []
        prefix = ""
        self.genChildren(lexicon, 0, prefix, children)
        base = self.assign(0, children, True)
        self.dat[0] = base
        for i in range(len(lexicon)):

            word = lexicon[i][0]
            off = Dat.getInfo(self, word)
            if(off <= 0):
                off = len(word)
            for offset in range(off, len(word)+1):
                prefix = ""
                for j in range(offset):
                    prefix += word[j]
                pBase = -Dat.getInfo(self, prefix)
                self.genChildren(lexicon, i, prefix, children)
                base = self.assign(pBase,children,offset == len(word))
            off = -Dat.getInfo(self, word)
            self.dat[2 * self.dat[2 * off]] = lexicon[i][1]
        self.shrink()


if __name__ == '__main__':
    dat = DATMaker()
    lexicon = []
    f = open("../../cs.txt", "r")
    for i, line in enumerate(f):
        line = line.split()
        lexicon.append([line[0].decode("utf-8"), i])
    f.close()
    dat.makeDat(lexicon)
    # dat.shrink
    print(len(dat.dat)/2)
    print(dat.dat[:500])
