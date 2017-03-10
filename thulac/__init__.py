#__coding:utf-8
from .character.CBModel import CBModel
from .character.CBNGramFeature import CBNGramFeature
from .character.CBTaggingDecoder import CBTaggingDecoder
from .manage.Preprocesser import Preprocesser
from .manage.Postprocesser import Postprocesser
from .manage.Filter import Filter
from .manage.TimeWord import TimeWord
from .manage.Punctuation import Punctuation
from .manage.SoExtention import *
from .base.compatibility import decode, cInput, encode
from functools import reduce 
import time
import os
import re

class thulac:
    def __init__(self, user_dict = None, model_path = None, T2S = False, \
                 seg_only = False, filt = False, max_length = 50000, deli='_'):
        self.__user_specified_dict_name = user_dict
        self.__model_path_char = model_path
        self.__separator = deli
        self.__useT2S = T2S
        self.__seg_only = seg_only
        self.__use_filter = filt
        self.__maxLength = max_length
        self.__coding = "utf-8"
        self.__prefix = self.__setPrefix()
        self.__poc_cands = []
        self.__cws_tagging_decoder = None
        self.__tagging_decoder = None
        self.__preprocesserpreprocesser = Preprocesser()
        self.__preprocesserpreprocesser.setT2SMap((self.__prefix+"t2s.dat"))
        self.__nsDict = Postprocesser((self.__prefix+"ns.dat"), "ns", False)
        self.__idiomDict = Postprocesser((self.__prefix+"idiom.dat"), "i", False)
        self.__userDict = None
        self.__timeword = TimeWord()
        self.__punctuation = Punctuation(self.__prefix+"singlepun.dat")
        self.__myfilter = None
        self.__so = None

        if(self.__user_specified_dict_name):
            self.__userDict = Postprocesser(self.__user_specified_dict_name, "uw", True)
        if(self.__use_filter):
            self.__myfilter = Filter((self.__prefix+"xu.dat"), (self.__prefix+"time.dat"))
        if(self.__seg_only):
            self.__cws_tagging_decoder = CBTaggingDecoder()
            self.__cws_tagging_decoder.init((self.__prefix+"cws_model.bin"), (self.__prefix+"cws_dat.bin"),(self.__prefix+"cws_label.txt"))
            self.__cws_tagging_decoder.threshold = 0
            self.__cws_tagging_decoder.__separator = self.__separator
            self.__cws_tagging_decoder.setLabelTrans()
        else:
            self.__tagging_decoder = CBTaggingDecoder()
            self.__tagging_decoder.init((self.__prefix+"model_c_model.bin"),(self.__prefix+"model_c_dat.bin"),(self.__prefix+"model_c_label.txt"))
            self.__tagging_decoder.threshold = 10000
            self.__tagging_decoder.__separator = self.__separator
            self.__tagging_decoder.setLabelTrans()

    def __setPrefix(self):
        __prefix = ""
        if(self.__model_path_char is not None):
            __prefix = self.__model_path_char
            if(__prefix[-1] != "/"):
                __prefix = __prefix + "/"
        else:
            __prefix = os.path.dirname(os.path.realpath(__file__))+"/models/"
        return __prefix

    def __cutWithOutMethod(self, oiraw, cut_method, text = True):
        oiraw = oiraw.split('\n')
        txt = ""
        array = []
        if(text):
            for line in oiraw:
                if(line):
                    txt += reduce(lambda x, y: x + ' ' + y, cut_method(line)) + '\n'
                else:
                    txt += reduce(lambda x, y: x + ' ' + y, cut_method(line), '') + '\n'
            if(txt[-1] == '\n'):
                return txt[:-1] #去掉最后一行的\n
            return txt
        else:
            for line in oiraw:
                if(line):
                    if(self.__seg_only):
                        array += (reduce(lambda x, y: x + [[y, '']], cut_method(line), []))
                    else:
                        array += (reduce(lambda x, y: x + [y.split(self.__separator)], cut_method(line), []))
                array += [['\n', '']]
            return array[:-1]

    def cut(self, oiraw, text = False):
        return self.__cutWithOutMethod(oiraw, self.__cutline, text = text)

    def fast_cut(self, oiraw, text = False):
        return self.__cutWithOutMethod(oiraw, self.__fast_cutline, text = text)

    def __cutline(self, oiraw):
        oiraw = decode(oiraw, coding = self.__coding)
        vec = []
        if(len(oiraw) < self.__maxLength):
            vec.append(oiraw)
        else:
            vec = self.__cutRaw(oiraw, self.__maxLength)
        ans = []
        for oiraw in vec:
            if(self.__useT2S):
                traw, __poc_cands = self.__preprocesserpreprocesser.clean(oiraw)
                raw = self.__preprocesserpreprocesser.T2S(traw)
            else:
                raw, __poc_cands = self.__preprocesserpreprocesser.clean(oiraw)

            if(len(raw) > 0):
                if(self.__seg_only):
                    tmp, tagged = self.__cws_tagging_decoder.segmentTag(raw, __poc_cands)
                    segged = self.__cws_tagging_decoder.get_seg_result()
                    if(self.__userDict is not None):
                        self.__userDict.adjustSeg(segged)
                    if(self.__use_filter):
                        self.__myfilter.adjustSeg(segged)
                    self.__nsDict.adjustSeg(segged)
                    self.__idiomDict.adjustSeg(segged)
                    self.__timeword.adjustSeg(segged)
                    self.__punctuation.adjustSeg(segged)
                    ans.extend(segged)
                    # return list(map(lambda x: encode(x), segged))
                    
                else:
                    tmp, tagged = self.__tagging_decoder.segmentTag(raw, __poc_cands)
                    if(self.__userDict is not None):
                        self.__userDict.adjustTag(tagged)
                    if(self.__use_filter):
                        self.__myfilter.adjustTag(tagged)
                    self.__nsDict.adjustTag(tagged)
                    self.__idiomDict.adjustTag(tagged)
                    self.__timeword.adjustTag(tagged)
                    self.__punctuation.adjustTag(tagged)
                    ans.extend(tagged)
        if(self.__seg_only):
            return map(lambda x: encode(x), ans)
        else:
            return map(lambda x: encode("".join(x)), ans)
        

    def __SoInit(self):
        if(not self.__user_specified_dict_name):
            self.__user_specified_dict_name = ''
        return SoExtention(self.__prefix, self.__user_specified_dict_name, self.__useT2S, self.__seg_only)

    def __fast_cutline(self, oiraw):
        self.__so = self.__SoInit()
        result = self.__so.seg(oiraw)
        return result.split()

    def run(self):
        while(True):
            oiraw = cInput()
            if(len(oiraw) < 1):
                break
            cutted = self.cut(oiraw, text = True)
            print(cutted)
            
    def cut_f(self, input_file, output_file):
        input_f = open(input_file, 'r')
        output_f = open(output_file, 'w')
        for oiraw in input_f.readlines():
            cutted = self.cut(oiraw, text = True)
            output_f.write(cutted)

        output_f.close()
        print("successfully cut file " + input_file + "!")

    def fast_cut_f(self, input_file, output_file):
        input_f = open(input_file, 'r')
        output_f = open(output_file, 'w')
        self.__so = self.__SoInit()
        for oiraw in input_f.readlines():
            cutted = self.__so.seg(oiraw)
            output_f.write(cutted + '\n')
        output_f.close()
        self.__so.clear()
        print("successfully cut file " + input_file + "!")

    def __cutRaw(self, oiraw, maxLength):
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