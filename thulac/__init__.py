#coding:utf-8
from .character.CBModel import CBModel
from .character.CBNGramFeature import CBNGramFeature
from .character.CBTaggingDecoder import CBTaggingDecoder
from .manage.Preprocesser import Preprocesser
from .manage.Postprocesser import Postprocesser
from .manage.Filter import Filter
from .manage.TimeWord import TimeWord
from .manage.Punctuation import Punctuation
from .base.compatibility import decode, cInput, encode
from functools import reduce 
import time
import os
import re

class thulac:
    def __init__(self, user_dict = None, model_path = None, T2S = False, \
                 seg_only = False, filt = False, maxLength = 50000, deli='_'):
        self.user_specified_dict_name = user_dict
        self.model_path_char = model_path
        self.separator = deli
        self.useT2S = T2S
        self.seg_only = seg_only
        self.useFilter = filt
        self.maxLength = maxLength
        self.input_file = ""
        self.output_file = ""
        self.coding = "utf-8"
        self.prefix = self.setPrefix()
        self.oiraw = ""
        self.raw = ""
        self.poc_cands = []
        self.cws_tagging_decoder = None
        self.tagging_decoder = None
        self.preprocesser = Preprocesser()
        self.preprocesser.setT2SMap((self.prefix+"t2s.dat"))
        self.nsDict = Postprocesser((self.prefix+"ns.dat"), "ns", False)
        self.idiomDict = Postprocesser((self.prefix+"idiom.dat"), "i", False)
        self.userDict = None
        self.timeword = TimeWord()
        self.punctuation = Punctuation(self.prefix+"singlepun.dat")
        self.myfilter = None

        if(self.user_specified_dict_name):
            self.userDict = Postprocesser(self.user_specified_dict_name, "uw", True)
        if(self.useFilter):
            self.myfilter = Filter((self.prefix+"xu.dat"), (self.prefix+"time.dat"))
        if(self.seg_only):
            self.cws_tagging_decoder = CBTaggingDecoder()
            self.cws_tagging_decoder.init((self.prefix+"cws_model.bin"), (self.prefix+"cws_dat.bin"),(self.prefix+"cws_label.txt"))
            self.cws_tagging_decoder.threshold = 0
            self.cws_tagging_decoder.separator = self.separator
            self.cws_tagging_decoder.setLabelTrans()
        else:
            self.tagging_decoder = CBTaggingDecoder()
            self.tagging_decoder.init((self.prefix+"model_c_model.bin"),(self.prefix+"model_c_dat.bin"),(self.prefix+"model_c_label.txt"))
            self.tagging_decoder.threshold = 10000
            self.tagging_decoder.separator = self.separator
            self.tagging_decoder.setLabelTrans()

    def setPrefix(self):
        prefix = ""
        if(self.model_path_char is not None):
            prefix = self.model_path_char
            if(prefix[-1] != "/"):
                prefix = prefix + "/"
        else:
            prefix = os.path.dirname(os.path.realpath(__file__))+"/models/"
        return prefix

    def cut(self, oiraw, text=False):
        oiraw = oiraw.split('\n')
        txt = ""
        array = []
        if(text):
            for line in oiraw:
                if(line):
                    txt += reduce(lambda x, y: x + ' ' + y, self.cutline(line)) + '\n'
                else:
                    txt += reduce(lambda x, y: x + ' ' + y, self.cutline(line), '') + '\n'
            if(txt[-1] == '\n'):
                return txt[:-1] #去掉最后一行的\n
            return txt
        else:
            for line in oiraw:
                if(line):
                    if(self.seg_only):
                        array += (reduce(lambda x, y: x + [[y, '']], self.cutline(line), []))
                    else:
                        array += (reduce(lambda x, y: x + [y.split(self.separator)], self.cutline(line), []))
                array += [['\n', '']]
            return array[:-1]

    def cutline(self, oiraw):
        oiraw = decode(oiraw, coding=self.coding)
        vec = []
        if(len(oiraw) < self.maxLength):
            vec.append(oiraw)
        else:
            vec = self.cutRaw(oiraw, self.maxLength)
        ans = []
        for oiraw in vec:
            if(self.useT2S):
                traw, poc_cands = self.preprocesser.clean(oiraw)
                raw = self.preprocesser.T2S(traw)
            else:
                raw, poc_cands = self.preprocesser.clean(oiraw)

            if(len(raw) > 0):
                if(self.seg_only):
                    tmp, tagged = self.cws_tagging_decoder.segmentTag(raw, poc_cands)
                    segged = self.cws_tagging_decoder.get_seg_result()
                    if(self.userDict is not None):
                        self.userDict.adjustSeg(segged)
                    if(self.useFilter):
                        self.myfilter.adjustSeg(segged)
                    self.nsDict.adjustSeg(segged)
                    self.idiomDict.adjustSeg(segged)
                    self.timeword.adjustSeg(segged)
                    self.punctuation.adjustSeg(segged)
                    ans.extend(segged)
                    # return list(map(lambda x: encode(x), segged))
                    
                else:
                    tmp, tagged = self.tagging_decoder.segmentTag(raw, poc_cands)
                    if(self.userDict is not None):
                        self.userDict.adjustTag(tagged)
                    if(self.useFilter):
                        self.myfilter.adjustTag(tagged)
                    self.nsDict.adjustTag(tagged)
                    self.idiomDict.adjustTag(tagged)
                    self.timeword.adjustTag(tagged)
                    self.punctuation.adjustTag(tagged)
                    ans.extend(tagged)
        if(self.seg_only):
            return map(lambda x: encode(x), ans)
        else:
            return map(lambda x: encode("".join(x)), ans)
        
    def run(self):
        while(True):
            oiraw = cInput()
            if(len(oiraw) < 1):
                break
            cutted = self.cut(oiraw, text=True)
            print(cutted)
            
    def cut_f(self, input_file, output_file):
        input_f = open(input_file, 'r')
        output_f = open(output_file, 'w')
        while(True):
            oiraw = self.getRaw(input_f)
            if(len(oiraw) < 1):
                break
            cutted = self.cut(oiraw, text=True)
            output_f.write(cutted + '\n')

        output_f.close()
        print("successfully cut file " + input_file + "!")

    def getRaw(self, inputfile):
        return inputfile.readline().strip()

    def cutRaw(self, oiraw, maxLength):
        vec = []
        m = re.findall(u".*?[。？！；;!?]", oiraw)
        num, l, last = 0, 0, 0
        for i in range(len(m)):
            if(num + len(m[i]) > maxLength):
                vec.append("".join(m[last:i]))
                last = i
                num = len(m[i])
            else:
                num += len(m[i])
            l += len(m[i])
        if(len(oiraw)-l + num > maxLength):
            vec.append("".join(m[last:len(m)]))
            vec.append(oiraw[l:])
        else:
            vec.append(oiraw[l-num:])
        return vec