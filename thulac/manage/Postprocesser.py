from .base.Dat import Dat


class Postprocesser():

    def __init__(self, filename, tag, isTxt):
        self.tag = tag
        self.p_dat = Dat(filename)


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
