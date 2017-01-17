#coding = utf-8
from .CBModel import CBModel
from .CBNGramFeature import CBNGramFeature
from ..base.Node import Node
from ..base.Dat import Dat
from ..base.WordWithTag import WordWithTag
from ..base.AlphaBeta import AlphaBeta
import time
import array

class CBTaggingDecoder:
    def __init__(self):
        self.separator = '_'
        self.maxLength = 50000
        self.len = 0
        self.sequence = ""
        self.allowedLabelLists = []
        for i in range(self.maxLength):
            self.allowedLabelLists.append([])
        self.pocsToTags = None
        self.nGramFeature = None
        self.dat = None
        self.nodes = [Node() for i in range(self.maxLength)]
        self.labelTrans = None
        self.labelTransPre = None
        self.labelTransPost = None
        self.threshold = 0

        self.allowCom = [0 for i in range(self.maxLength)]
        self.tagSize = 0
        self.model = None
        self.alphas = None
        # self.betas = None

    def init(self, modelFile, datFile, labelFile):
        self.model = CBModel(modelFile)
        self.values = {}
        self.result = {}
        for i in range(self.maxLength):
            pre = (i - 1)
            self.nodes[i].predecessors = pre

            pre = (i + 1)
            self.nodes[i].successors = pre
        
        self.dat = Dat(datFile)
        self.nGramFeature = CBNGramFeature(self.dat, self.model)
        
        self.labelInfo = ["" for i in range(10000)]
        self.pocTags = []
        for i in range(16):
            self.pocTags.append([])
        labelin = open(labelFile, "r")
        line = ""
        ind = 0
        line = labelin.readline()
        while(len(line) > 0):
            self.labelInfo[ind] = line
            segInd = int(line[0]) - int('0')
            for j in range(16):
                if(((1 << segInd) & j) != 0):
                    self.pocTags[j].append(ind)
            ind = ind + 1
            line = labelin.readline()
        labelin.close()

        self.pocsToTags = [[] for i in range(16)]
        for j in range(1, 16, 1):
            self.pocsToTags[j] = [0 for i in range(len(self.pocTags[j]) + 1)]
            for k in range(len(self.pocTags[j])):
                self.pocsToTags[j][k] = self.pocTags[j][k]
            self.pocsToTags[j][len(self.pocTags[j])] = -1

        self.labelLookingFor = [[] for i in range(self.model.l_size)]
        for i in range(self.model.l_size):
            self.labelLookingFor[i] = None
        for i in range(self.model.l_size):
            if(self.labelInfo[i][0] == '0' or self.labelInfo[i][0] == '3'):
                continue
            for j in range(i + 1):
                if((self.labelInfo[i][1:] == self.labelInfo[j][1:]) and (self.labelInfo[j][0] == '0')):
                    if(self.labelLookingFor[j] is None):
                        self.labelLookingFor[j] = [0, 0]
                        self.labelLookingFor[j][0] = -1
                        self.labelLookingFor[j][1] = -1
                        self.tagSize = self.tagSize + 1
                    self.labelLookingFor[j][int(self.labelInfo[i][0])-1] = i
                    break

        for i in range(self.maxLength):
            self.allowedLabelLists[i] = None
        self.isGoodChoice = [0 for i in range(self.maxLength * self.model.l_size)]
        print("Model loaded succeed")

    def dp(self):
        if(self.allowedLabelLists[0] is None):
            self.allowedLabelLists[0] = self.pocsToTags[9]
        if(self.allowedLabelLists[self.len - 1] is None):
            self.allowedLabelLists[self.len - 1] = self.pocsToTags[12]
        alp = AlphaBeta()
        self.result = {}
        self.alphas = []
        self.bestScore = alp.dbDecode(self.model.l_size, self.model.ll_weights, self.len, self.nodes, self.values, self.alphas, self.result, self.labelTransPre, self.allowedLabelLists)
        self.allowedLabelLists[0] = None
        self.allowedLabelLists[self.len - 1] = None

    def setLabelTrans(self):
        lSize = self.model.l_size
        preLabels = [[] for i in range(lSize)]
        postLabels = [[] for i in range(lSize)]
        for i in range(lSize):
            for j in range(lSize):
                ni = int(self.labelInfo[i][0]) - 0
                nj = int(self.labelInfo[j][0]) - 0
                iIsEnd = ((ni == 2) or (ni == 3))
                jIsBegin = ((nj == 0) or (nj == 3))
                sameTag = self.labelInfo[i][1:] == self.labelInfo[j][1:]
                if(sameTag):
                    if((ni == 0 and nj == 1) or \
                            (ni == 0 and nj == 2) or \
                            (ni == 1 and nj == 2) or \
                            (ni == 1 and nj == 1) or \
                            (ni == 2 and nj == 0) or \
                            (ni == 2 and nj == 3) or \
                            (ni == 3 and nj == 3) or \
                            (ni == 3 and nj == 0)):
                        preLabels[j].append(i)
                        postLabels[i].append(j)
                else:
                    if(iIsEnd and jIsBegin):
                        preLabels[j].append(i)
                        postLabels[i].append(j)
        self.labelTransPre = [[] for i in range(lSize)]
        for i in range(lSize):
            self.labelTransPre[i] = [0 for k in range(len(preLabels[i])+1)]
            for j in range(len(preLabels[i])):
                self.labelTransPre[i][j] = preLabels[i][j]
            self.labelTransPre[i][len(preLabels[i])] = -1

        self.labelTransPost = [[] for i in range(lSize)]
        for i in range(lSize):
            self.labelTransPost[i] = [0 for k in range(len(postLabels[i])+1)]
            for j in range(len(postLabels[i])):
                self.labelTransPost[i][j] = postLabels[i][j]
            self.labelTransPost[i][len(postLabels[i])] = -1

    def putValues(self):
        if(self.len == 0):
            return
        for i in range(self.len):
            self.nodes[i].type = 0
        self.nodes[0].type += 1
        self.nodes[self.len-1].type += 2
        tmp = [0 for i in range(self.len * self.model.l_size)]
        self.values = array.array("i",  tmp)
        self.nGramFeature.putValues(self.sequence, self.len, self.values)
        self.values = tuple(self.values)

    def segmentTag(self, raw, graph):
        if(len(raw) == 0):
            return 0, []
        for i in range(len(raw)):
            pocs = graph[i]
            if(pocs != 0):
                self.allowedLabelLists[i] = self.pocsToTags[pocs]
            else:
                self.allowedLabelLists[i] = self.pocsToTags[15]
        self.sequence = raw
        self.len = len(raw)
        start = time.clock()
        self.putValues()
        self.dp()

        offset = 0
        if(len(self.labelInfo[0]) < 2):
            return 1, []
        ts = []

        for i in range(self.len):
            if(i not in self.result):
                self.result[i] = 0
            if((i == self.len-1) or (self.labelInfo[self.result[i]][0] == '2') or (self.labelInfo[self.result[i]][0] == '3')):
                ts.append((self.sequence[offset:i+1], self.separator, self.labelInfo[self.result[i]][1:-1]))
                offset = i + 1
        return 1, ts

    def get_seg_result(self):
        segged = []
        offset = 0
        for i in range(self.len):
            if((i == 0) or (self.labelInfo[self.result[i]][0] == '0') or (self.labelInfo[self.result[i]][0] == '3')):
                segged.append(self.sequence[offset:i])
                offset = i
        segged.append(self.sequence[offset:self.len])
        return segged[1:]
