#coding: utf-8
class TimeWord():
    def __init__(self):
        self.__arabicNumSet = set()
        self.__timeWordSet = set()
        self.__otherSet = set()
        timeWord = {24180, 26376, 26085, 21495, 26102, 28857, 20998, 31186}
        for i in range(48, 58):
            self.__arabicNumSet.add(i)
        for i in range(65296, 65306):
            self.__arabicNumSet.add(i)
        timeWord = {24180, 26376, 26085, 21495, 26102, 28857, 20998, 31186}
        self.__timeWordSet = self.__timeWordSet | timeWord
        for i in range(65, 91):
            self.__otherSet.add(i)
        for i in range(97, 123):
            self.__otherSet.add(i)
        for i in range(48, 58):
            self.__otherSet.add(i)

        other = {65292, 12290, 65311, 65281, 65306, 65307, 8216, 8217, 8220, 8221, 12304, 12305,
                        12289, 12298, 12299, 126, 183, 64, 124, 35, 65509, 37, 8230, 38, 42, 65288,
                        65289, 8212, 45, 43, 61, 44, 46, 60, 62, 63, 47, 33, 59, 58, 39, 34, 123, 125,
                        91, 93, 92, 124, 35, 36, 37, 94, 38, 42, 40, 41, 95, 45, 43, 61, 9700, 9734, 9733}
        self.__otherSet = self.__otherSet | other

    def isArabicNum(self, word):
        allArabic = True
        for i in word:
            if(i not in self.__arabicNumSet):
                allArabic = False
                break
        return allArabic

    def isTimeWord(self, word):
        if(len(word)!= 1):
            return False
        if(word[0] in self.__timeWordSet):
            return True
        else:
            return False

    def isDoubleWord(self, word, postWord):
        if(len(word) != 1 or len(postWord) != 1):
            return False
        else:
            wordInt = word[0]
            postWordInt = postWord[0]
            if(wordInt == postWordInt):
                if(wordInt in self.__otherSet):
                    return True
                else:
                     return False
        return False

    def adjustSeg(self, sentence):
        size = len(sentence)
        word = []
        hasTimeWord = False
        for i in range(size-1, -1, -1):
            word = sentence[i]
            if(self.isTimeWord(word)):
                hasTimeWord = True
            else:
                if(hasTimeWord):
                    if(self.isArabicNum(word)):
                        sentence[i] += sentence[i+1]
                        del sentence[i+1]
                hasTimeWord = False

        postWord = []
        for i in range(size-2, -1, -1):
            word = sentence[i]
            postWord = sentence[i+1]
            if(self.isDoubleWord(word, postWord)):
                sentence[i] += sentence[i+1]
                del sentence[i+1]

    def adjustTag(self, sentence):
        size = len(sentence)
        word = []
        hasTimeWord = False
        for i in range(size-1, -1, -1):
            word = sentence[i][0]
            if(self.isTimeWord(word)):
                hasTimeWord = True
            else:
                if(hasTimeWord):
                    if(self.isArabicNum(word)):
                        sentence[i] = (sentence[i][0] + sentence[i+1][0], sentence[i][1], 't')
                        del sentence[i+1]
                hasTimeWord = False
        size = len(sentence)
        for i in range(size):
            word = sentence[i][0]
            if(self.isHttpWord(word)):
                sentence[i] = (sentence[i][0], sentence[i][1], 'x')

        size = len(sentence)
        preWord = ""
        for i in range(1, size):
            preWord = sentence[i-1][0]
            word = sentence[i][0]
            if(len(preWord) == 1 and preWord[0] == 64):
                if(len(word) != 1 or word[0] != 64):
                    sentence[i] = (sentence[i][0], sentence[i][1], 'np')
        # del word[:]


    def isHttpWord(self, word):
        if(len(word) < 5):
            return False
        else:
            if(word[0] == ord('h') and word[1] == ord('t') and word[2] == ord('t') and word[3] == ord('p')):
                return True
            else:
                return False


    def adjustDouble(self, sentence):
        size = len(sentence)
        word = []
        hasTimeWord = False
        for i in range(size-1, -1, -1):
            word = sentence[i].word
            if(self.isTimeWord(word)):
                hasTimeWord = True
            else:
                if(hasTimeWord):
                    if(self.isArabicNum(word)):
                        sentence[i].word += sentence[i+1].word
                        del sentence[i+1]
                        sentence[i].tag = "t"
                hasTimeWord = False
        size = len(sentence)
        postWord = ""
        for i in range(size - 2, -1, -1):
            word = sentence[i].word
            postWord = sentence[i+1].word
            if(self.isDoubleWord(word, postWord)):
                sentence[i].word += sentence[i+1].word
                del sentence[i+1]

        size = len(sentence)
        for i in range(size):
            word = sentence[i].word
            if(self.isHttpWord(word)):
                sentence[i].tag = 'x'

        size = len(sentence)
        preWord = ""
        for i in range(size):
            preWord = sentence[i-1].word
            word = sentence[i].word
            if(len(preWord) == 1 and preWord[0] == 64):
                if(len(word) != 1 or word[0] != 64):
                    sentence[i].tag = "np"

        del word[:]


if __name__ == '__main__':
    class WordWithTag:
        word = []
        tag = ""

        def __init__(self, word, tag):
            self.word = word
            self.tag = tag
    time = b = [ord(i) for i in "1988".decode('utf-8')]
    year = [ord("年".decode('utf-8'))]
    # print time
    a = [([ord(i) for i in "1988".decode('utf-8')], '_', 'n'), ([ord("年".decode('utf-8'))], '_', 'n')]
    # b = [ord(i) for i in "月".decode('utf-8')]
    tw = TimeWord()
    # for i in '月亮'.decode('utf-8'):
    #   print ord(i)
    tw.adjustTag(a)
    for i in a:
        print(i)
        