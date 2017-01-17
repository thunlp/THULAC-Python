from ..base.Dat import Dat


class Filter:
    def __init__(self, xuWordFile, timeWordFile):
        self.xu_dat = Dat(xuWordFile)
        self.time_dat = Dat(timeWordFile)
        self.posSet = ["n","np","ns","ni","nz","v","a","id","t","uw"]
        self.arabicNumSet = []
        self.chineseNumSet = [12295,19968,20108,19977,22235,20116,20845,19971,20843,20061]
        for i in range(48, 58):
            self.arabicNumSet.append(i)
        for i in range(65296, 65306):
            self.arabicNumSet.append(i)

    def adjustSeg(self, sentence):
        if((self.xu_dat is None) or (self.time_dat is None)):
            return
        size = len(sentence)
        count = 0
        checkArabic = False
        checkChinese = False
        for i in range(size-1, -1, -1):
            word = sentence[i]
            if(self.xu_dat.match(word) != -1):
                sentence.remove(word)
                continue
            count = 0
            checkArabic = False
            checkChinese = False
            for j in range(len(word)):
                if(ord(word[j]) in self.arabicNumSet):
                    checkArabic = True
                    break
                if(ord(word[j]) in self.chineseNumSet):
                    count = count + 1
                    if(count == 2):
                        checkChinese = True
                        break
            if(checkArabic or checkChinese or (self.time_dat.match(word) != -1)):
                sentence.remove(word)

    def adjustTag(self, sentence):
        if(self.xu_dat is None or self.time_dat is None):
            return
        size = len(sentence)
        word = ""
        tag = ""
        count = 0
        checkArabic = False
        checkChinese = False

        for i in range(size-1, -1, -1):
            word = sentence[i][0]
            tag = sentence[i][2]
            if(tag in self.posSet):
                if(self.xu_dat.match(word) != -1):               
                    sentence.remove(sentence[i])
                    continue
                if(tag == "t"):  
                    count = 0
                    checkArabic = False
                    checkChinese = False
            
                    for j in range(len(word)):
                        if(ord(word[j]) in self.arabicNumSet):
                            checkArabic = True
                            break
                        if(ord(word[j]) in self.chineseNumSet):
                            count = count + 1
                            if(count == 2):
                                checkChinese = True
                                break
                    if(checkArabic or checkChinese or (self.time_dat.match(word) != -1)):
                        sentence.remove(sentence[i])
                        continue
            else:
                sentence.remove(sentence[i])
                continue
