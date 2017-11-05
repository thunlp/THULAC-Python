#coding: utf-8
import os
import struct
from ..base.compatibility import chrGenerator

chr = chrGenerator()

class Preprocesser:
    def __init__(self, rm_space=False):
        self.otherSet = [65292, 12290, 65311, 65281, 65306, 65307, 8216, \
                8217, 8220, 8221, 12304, 12305, \
                12289, 12298, 12299, 126, 183, 64, 124, 35, 65509, 37, 8230, 38, 42, 65288, \
                65289, 8212, 45, 43, 61, 44, 46, 60, 62, 63, 47, 33, 59, 58, 39, 34, 123, 125, \
                91, 93, 92, 124, 35, 36, 37, 94, 38, 42, 40, 41, 95, 45, 43, 61, 9700, 9734, 9733, 32, 12288, \
                 21543, 32610, 21591, 21877, 30340, 20215, 23478, 21862, 26469, 21819, \
                 20102, 22046, 21737, 21671, 21679, 21872, 21949, 21527, 22043, 22172, 20040, \
                 21738, 21602, 21584, 21542, 21621, 21704, 19981, 20846, 33324, 21017, 36830, \
                 32599, 32473, 22139, 21705, 38463, 21834, 21571, 27448, 21703, 21568, 20063, \
                 32822, 21727, 27428, 21589, 22114, 21606, 22050
                 ]
        self.singlePunSet = [65292, 12290, 65311, 65281, 65306, 65307, 8216, 8217, 8220, 8221, 1230, 12304, \
                    12305, 12289, 12298, 12299, 64,35, 65288, 65289, 34, 91, 93, 126, 47, 44, 58, \
                    63, 9700, 9734, 9733, 8230, 39, 33, 42, 43, 62, 40, 41, 59, 61, 32, 12288]
        self.httpSet = [47, 46, 58, 35, 34, 95, 45, 61, 43, 38, 36, 59]
        self.modalParticleSet = [20040, 21602, 21543, 21834, 21602, 21734]
        self.t2s = {}
        self.s2t = {}
        self.rmSpace = rm_space
        self.isOther = self.is_X(self.otherSet)
        self.isSinglePun = self.is_X(self.singlePunSet)
        self.isHttp = self.is_X(self.httpSet)
        self.isModalParticleSet = self.is_X(self.modalParticleSet)


    def is_X(self, charType):
        def func(c):
            if(c in charType):
                return True
            else:
                return False
        return func



    # def isOther(self, c):
    #     if(c in self.otherSet):
    #         return True
    #     else:
    #         return False
    
    # def isSinglePun(self, c):
    #     if(c in self.singlePunSet):
    #         return True
    #     else:
    #         return False
    
    # def isHttp(self, c):
    #     if(c in self.httpSet):
    #         return True
    #     else:
    #         return False

    # def isModalParticleSet(self, c):
    #     if(c in self.modalParticleSet):
    #         return True
    #     else:
    #         return False

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
                    if(not self.rmSpace):
                        senClean += sentence[i]
                        graph.append(9)
                    continue

            elif(self.isOther(c)):
                if(hasSpace):
                    senClean += sentence[i]
                    if(self.isSinglePun(c) or self.isModalParticleSet(c)):
                        graph.append(8)
                        if(self.isSinglePun(c)):
                            hasSinglePun = True
                    else:
                        graph.append(9)
                        hasSinglePun = False
                    hasSpace = False
                elif(hasOther):
                    if(self.isSinglePun(c) or self.isModalParticleSet(c)):
                        if(len(graph) > 0):
                            o = graph[-1] & 12
                            graph[-1] = o
                        senClean += sentence[i]
                        graph.append(8)
                        if(self.isSinglePun(c)):
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
        if(ord(c) in self.t2s):
            return chr(self.t2s[ord(c)])
        else:
            return c

    def getS2T(self, c):
        if(c in self.s2t):
            return self.s2t[c]
        else:
            return c

    def T2S(self, sentence):
        newSentence = ""
        for w in sentence:
            newSentence += self.getT2S(w)
        return newSentence
    
    def S2T(self, sentence, oriSentence):
        count = 0
        for w in sentence:
            for j in range(len(w.word)):
                w.word = w.word[0, j-1]+oriSentence[count] \
                        + w.word[j+1:]
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
