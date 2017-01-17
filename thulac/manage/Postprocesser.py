from ..base.Dat import Dat, DATMaker
from ..base.compatibility import decode

class Postprocesser():

    def __init__(self, filename, tag, isTxt):
        if(not filename):
            return None
        self.tag = tag
        if(isTxt):
            lexicon = []
            f = open(filename, "r")  
            for i, line in enumerate(f):
                line = line.split()
                lexicon.append([decode(line[0]), i])
            f.close()
            dm = DATMaker()
            dm.makeDat(lexicon, 0)
            dm.shrink()
            self.p_dat = Dat(datSize=dm.datSize, oldDat=dm.dat)

        else:
            self.p_dat = Dat(filename=filename)


    def adjustSeg(self, sentence):
        if(self.p_dat is None):
            return
        i = 0
        while(i < len(sentence)):
            tmp = sentence[i]
            if(self.p_dat.getInfo(tmp) >= 0):
                i += 1
                continue
            tmpVec = []
            for j in range(i + 1, len(sentence)):
                tmp += sentence[j]

                if(self.p_dat.getInfo(tmp) >= 0):
                    break
                tmpVec.append(tmp)
            vecSize = len(tmpVec)
            
            for k in range(vecSize-1, -1, -1):
                tmp = tmpVec[k]
                if(self.p_dat.match(tmp) != -1):
                    sentence[i] = tmp
                    del sentence[i+1:i+k+2]
                    break
            i += 1


    def adjustTag(self, sentence):
        # print sentence
        if(self.p_dat is None):
            return
        i = 0
        while(i < len(sentence)):
            tmp = sentence[i][0]
            if(self.p_dat.getInfo(tmp) >= 0):
                i+=1
                continue

            tmpVec = []
            for j in range(i+1, len(sentence)):
                tmp += sentence[j][0]
                if(self.p_dat.getInfo(tmp) >= 0):
                    break
                tmpVec.append(tmp)
            vecSize = len(tmpVec)

            for k in range(vecSize-1, -1, -1):
                tmp = tmpVec[k]
                if(self.p_dat.match(tmp) != -1):
                    sentence[i] = (tmp, '_', self.tag)
                    del sentence[i+1:i+k+2]
                    # sentence[i][2] = self.tag;
                    break
            i+=1


if __name__ == '__main__':
    pp = Postprocesser("userwords.txt", "uw", True) 