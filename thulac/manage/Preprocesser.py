# coding = utf-8
import os
import struct


class Preprocesser:
    def __init__(self):
        self.otherSet = []
        self.singlePunSet = []
        self.httpSet = []
        self.t2s = {}
        self.s2t = {}
        for i in range(65, 91):
            self.otherSet.append(i)
            self.httpSet.append(i)
        for i in range(97, 123):
            self.otherSet.append(i)
            self.httpSet.append(i)
        for i in range(48, 58):
            self.otherSet.append(i)
            self.httpSet.append(i)
        other = [65292, 12290, 65311, 65281, 65306, 65307, 8216, \
                8217, 8220, 8221, 12304, 12305, \
                12289, 12298, 12299, 126, 183, 64, 124, 35, 65509, 37, 8230, 38, 42, 65288, \
                65289, 8212, 45, 43, 61, 44, 46, 60, 62, 63, 47, 33, 59, 58, 39, 34, 123, 125, \
                91, 93, 92, 124, 35, 36, 37, 94, 38, 42, 40, 41, 95, 45, 43, 61, 9700, 9734, 9733]
        templen = 63
        for i in range(templen):
            self.otherSet.append(other[i])

        singlePun = [65292, 12290, 65311, 65281, 65306, 65307, 8216, 8217, 8220, 8221, 1230, 12304, \
                    12305, 12289, 12298, 12299, 64,35, 65288, 65289, 34, 91, 93, 126, 47, 44, 58, \
                    63, 9700, 9734, 9733, 8230, 39, 33, 42, 43, 62, 40, 41, 59, 61]
        templen = 41
        for i in range(templen):
            self.singlePunSet.append(singlePun[i])

        httpChar = ['/', '.', ':', '#', '"', '_', '-', '=', '+', '&', '$', ';']
        templen = 12
        for i in range(templen):
            self.httpSet.append(ord(httpChar[i]))

    def isOther(self, c):
        if(c in self.otherSet):
            return True
        else:
            return False
    
    def isSinglePun(self, c):
        if(c in self.singlePunSet):
            return True
        else:
            return False
    
    def isHttp(self, c):
        if(c in self.httpSet):
            return True
        else:
            return False

    def setT2SMap(self, filename):
        file = open(filename, "rb")
        self.datSize = int(os.path.getsize(filename) / 8)
        tempbytes = file.read(4 * self.datSize)
        tra = struct.unpack("<"+str(self.datSize)+"i", tempbytes)
        tempbytes = file.read(4 * self.datSize)
        sim = struct.unpack("<"+str(self.datSize)+"i", tempbytes)
        for i in range(self.datSize):
            self.t2s[tra[i]] = sim[i]
            self.s2t[sim[i]] = tra[i]

    def clean(self, sentence):
        senClean = ""
        graph = []
        hasSpace = False
        hasOther = False
        hasSinglePun = False
        hasHttp = False
        hasAt = False
        hasTitle = False
        httpStartVec = []
        httpStart = -1
        httpVec = []
        c = -1
        tmpRaw = []
        npRaw = []
        npStart = -1
        npStartVec = []
        npVec = []
        titleRaw = []
        titleStart = -1
        titleStartVec = []
        titleVec = []
        for i in range(len(sentence)):
            c = ord(sentence[i])
            if(c == 32 or c == 12288):
                hasOther = False
                if(hasSpace):
                    continue
                else:
                    if(len(graph) > 0):
                        o = graph[-1] & 12
                        graph[-1] = o
                    hasSpace = True
                    continue

                # if(hasAt):
                #     npVec.append(npRaw)
                #     npStartVec.append(npStart)
                #     hasAt = False
            elif(self.isOther(c)):
                if(hasSpace):
                    senClean += sentence[i]
                    if(self.isSinglePun(c)):
                        graph.append(8)
                        hasSinglePun = True
                    else:
                        graph.append(9)
                        hasSinglePun = False
                    hasSpace = False
                elif(hasOther):
                    if(self.isSinglePun(c)):
                        if(len(graph) > 0):
                            o = graph[-1] & 12
                            graph[-1] = o
                        senClean += sentence[i]
                        graph.append(8)
                        hasSinglePun = True

                    else:
                        if(hasSinglePun):
                            senClean += sentence[i]
                            graph.append(9)
                        else:              
                            if(graph[-1] == 0):
                                graph[-1] = 7
                            senClean += sentence[i]
                            graph.append(2)
                        hasSinglePun = False
                else:
                    senClean += sentence[i]
                    graph.append(9)
                    if(self.isSinglePun(c)):
                        hasSinglePun = True
                    else:
                        hasSinglePun = False

                if(c == 12299):
                    if(hasTitle):
                        titleVec.append(titleRaw)
                        titleStartVec.append(titleStart)
                        hasTitle = False
                hasOther = True
            else:
                if(hasSpace):
                    senClean += sentence[i]
                    graph.append(9)
                elif(hasOther):
                    graph[-1] = graph[-1] & 12
                    if(hasSinglePun):
                        senClean += sentence[i]
                        graph.append(9)
                        hasSinglePun = False
                    else:  
                        senClean += sentence[i]
                        graph.append(15)
                else:
                    senClean += sentence[i]
                    graph.append(15)
                hasSpace = False
                hasOther = False
            if(c == 12298):
                hasTitle = True
                titleStart = len(graph)
                titleRaw = []
            elif(hasTitle):
                titleRaw.append(c)

        for i in range(len(titleVec)):
            titleRaw = titleVec[i]
            if(self.isPossibleTitle(titleRaw)):
                start = titleStartVec[i]
                size = len(titleRaw)
                # print sentence + ":Here" + str(titleRaw) + ":" + str(start) + ":" + str(size) + ":" + str(len(graph))
                if(len(titleRaw) == 1):
                    graph[start] =  9
                    continue    
                graph[start] = 1
                for j in range(start + 1, start + size - 1):
                    graph[j] = 2
                graph[start + size - 1] = 4
        
        if(len(graph) != 0):
            graph[0] = graph[0] & 9
            graph[-1] = graph[-1] & 12
            if(graph[0] == 0):
                graph[0] = 9
            if(graph[-1] == 0):
                graph[-1] = 12
        return senClean, graph

    def isPossibleTitle(self, titleRaw):
        if(len(titleRaw) > 10 or len(titleRaw) == 0):
            return False
        else:
            for i in range(len(titleRaw)):
                if(self.isOther(titleRaw[i])):
                    return False
            return True

    def getT2S(self, c):
        if(c in self.t2s):
            return t2s[c]
        else:
            return c

    def getS2T(self, c):
        if(c in self.s2t):
            return s2t[c]
        else:
            return c

    def T2S(self, sentence):
        newSentence = ""
        for i in range(sentence):
            newSentence += str(getT2S(sentence[i]))
        return newSentence
    
    def S2T(self, sentence, oriSentence):
        count = 0
        for i in range(len(sentence)):
            for j in range(len(sentence[i].word)):
                sentence[i].word = sentence[i].word[0, j-1]+oriSentence[count] \
                        + sentence[i].word[j+1:]
                count = count + 1

    def cleanSpace(self, sentence, senClean, graph):
        senClean = ""
        graph = []
        hasSpace = False
        c = -1
        wordLength = 0
        # for(int i=0;i<(int)sentence.length();i++)
        for i in range(len(sentence)):
            c = sentence[i]
            if(c==32 or c==12288):
                if(hasSpace):
                    continue
                else:
                    if(len(graph) > 0):
                        if(wordLength == 1):   
                            graph[-1] = 8
                        else:
                            graph[-1] = 4
                    hasSpace = True
                wordLength = 0
            else:
                if(hasSpace):
                    senClean += sentence[i]
                    graph.append(1)
                    hasSpace = False
                else:
                    senClean += sentence[i]
                    if(len(graph) == 0):
                        graph.append(1)
                    else:
                        graph.append(2)

                wordLength = wordLength + 1
        if(len(graph) > 0):
            if(wordLength == 1):   
                graph[-1] = 8
            else:
                graph[-1] = 4
        return graph

if __name__ == '__main__':
    preprocesser = Preprocesser()
    preprocesser.setT2SMap("t2s.dat")
    f = open("cs.txt", "r")
    s = f.readline().decode('utf-8')
    a = []
    b, a = preprocesser.clean(s)
    print(a)
    print(b.encode("utf-8"))
