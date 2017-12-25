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
from .base.compatibility import decodeGenerator, cInputGenerator, encodeGenerator
from functools import reduce, partial
import itertools
import time
import os
import re

decode = decodeGenerator()
cInput = cInputGenerator()
encode = encodeGenerator()

'''程序入口，提供所有面向用户的接口'''
class thulac:
    def __init__(self, user_dict = None, model_path = None, T2S = False, \
                 seg_only = False, filt = False, max_length = 50000, deli='_', rm_space=False):
        '''初始化函数，传入用户设置的参数，并且根据参数初始化不同
        模型（调入不同的.dat文件，该文件存储了一个双数组trie树）'''
        self.__user_specified_dict_name = user_dict
        self.__model_path_char = model_path
        self.__separator = deli
        self.__useT2S = T2S
        self.__seg_only = seg_only
        self.__use_filter = filt
        self.__maxLength = max_length
        self.rmSpace = rm_space
        self.__coding = "utf-8"
        self.__prefix = self.__setPrefix()
        self.__poc_cands = []
        self.__cws_tagging_decoder = None
        self.__tagging_decoder = None
        self.__preprocesserpreprocesser = Preprocesser(rm_space=rm_space)
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
            self.__cws_tagging_decoder.separator = self.__separator
            self.__cws_tagging_decoder.setLabelTrans()
        else:
            self.__tagging_decoder = CBTaggingDecoder()
            self.__tagging_decoder.init((self.__prefix+"model_c_model.bin"),(self.__prefix+"model_c_dat.bin"),(self.__prefix+"model_c_label.txt"))
            self.__tagging_decoder.threshold = 10000
            self.__tagging_decoder.separator = self.__separator
            self.__tagging_decoder.setLabelTrans()

    def __setPrefix(self):
        '''获取程序运行的路径，以此来确定models的绝对路径以及其他资源文件的路径'''
        __prefix = ""
        if(self.__model_path_char is not None):
            __prefix = self.__model_path_char
            if(__prefix[-1] != "/"):
                __prefix = __prefix + "/"
        else:
            __prefix = os.path.dirname(os.path.realpath(__file__))+"/models/"
        return __prefix

    def __cutWithOutMethod(self, oiraw, cut_method, text = True):
        '''分词，先将原始句子split为一个数组，之后遍历每一行，调用对单行分词的函数（有两种）。
        text=True会返回分词好的字符串，为False则会返回一个二位数组方便用户做后续处理。
        函数中有一些细节处理主要是用于规范输出格式'''
        oiraw = oiraw.split('\n')
        txt = ""
        array = []
        if(text):
            for line in oiraw:
                if(self.__seg_only):
                    temp_txt = reduce(lambda x, y: x + ' ' + y if y != " " else x, cut_method(line), '') + '\n'
                else:
                    temp_txt = reduce(lambda x, y: x + ' ' + "".join(y), cut_method(line), '') + '\n'
                txt += temp_txt[1:]
            return txt[:-1]
        else:
            for line in oiraw:
                if(line):
                    if(self.__seg_only):
                        array += (reduce(lambda x, y: x + [[y, '']], cut_method(line), []))
                    else:
                        array += (reduce(lambda x, y: x + [[y[0], y[2]]], cut_method(line), []))
                array += [['\n', '']]
            return array[:-1]



    def cut(self, oiraw, text = False):
        return self.__cutWithOutMethod(oiraw, self.__cutline, text = text)

    def fast_cut(self, oiraw, text = False):
        return self.__cutWithOutMethod(oiraw, self.__fast_cutline, text = text)

    def __cutline(self, oiraw):
        '''对单行进行分词，这段函数包含前处理preprogress.py以及一系列后处理，将分词结果返回为一个map'''
        oiraw = decode(oiraw)
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
                # raw = oiraw

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
            return map(lambda x: (encode(x[0]), encode(x[1]), encode(x[2])), ans)
        
    def foo(self, x):
        return x
    def __SoInit(self):
        '''fast_cut函数需要使用thulac.so，在这里导入.so文件'''
        if(not self.__user_specified_dict_name):
            self.__user_specified_dict_name = ''
        return SoExtention(self.__prefix, self.__user_specified_dict_name, self.__useT2S, self.__seg_only)

    def __fast_cutline(self, oiraw):
        if(not self.__so):
            self.__so = self.__SoInit()
        result = self.__so.seg(oiraw).split()
        if not self.__seg_only:
            result = map(lambda x: re.split(r'(_)', x), result)
        return result


    def run(self):
        '''命令行交互程序'''
        while(True):
            oiraw = cInput()
            if(len(oiraw) < 1):
                break
            cutted = self.cut(oiraw, text = True)
            print(cutted)
            
    def cut_f(self, input_file, output_file):
        input_f = open(input_file, 'r')
        output_f = open(output_file, 'w')
        for line in input_f:
            cutted = self.cut(line, text = True)
            output_f.write(cutted + "\n")

        output_f.close()
        input_f.close()
        print("successfully cut file " + input_file + "!")

    def fast_cut_f(self, input_file, output_file):
        input_f = open(input_file, 'r')
        output_f = open(output_file, 'w')
        
        for line in input_f:
            cutted = self.fast_cut(line, text = True)
            output_f.write(cutted + "\n")
        output_f.close()
        input_f.close()
        print("successfully cut file " + input_file + "!")

    def __cutRaw(self, oiraw, maxLength):
        '''现将句子按句子完结符号切分，如果切分完后一个句子长度超过限定值
        ，再对该句子进行切分'''
        vec = []
        m = re.findall(u".*?[。？！；;!?]", oiraw)
        num, l, last = 0, 0, 0
        for i in range(len(m)):
            if(num + len(m[i]) >= maxLength):
                vec.append("".join(m[last:i]))
                last = i
                num = len(m[i])
            else:
                num += len(m[i])
            l += len(m[i])
        if(len(oiraw)-l + num >= maxLength):
            vec.append("".join(m[last:len(m)]))
            vec.append(oiraw[l:])
        else:
            vec.append(oiraw[l-num:])
        return vec

    def multiprocessing_cut_f(self, input_file, output_file, core = 0):
        from multiprocessing import Pool
        if core:
            p = Pool(1)
        else:
            p = Pool()
        output_f = open(output_file, 'w')
        input_f = open(input_file, 'r')
        f = input_f.readlines()
        # thu = thulac(seg_only=True)
        cutline = partial(_cutline, self)
        # print(cutline("我爱北京天安门"))
        x = p.map(func_cutline, itertools.izip(itertools.repeat(self), f))
        for line in x:
            line_text = " ".join(line)
            output_f.write(line_text)
        output_f.close()

    def cutline(self, oiraw):
        return self.__cutline(oiraw)

def _cutline(lac, x):
    return lac.cutline(x)

def func_cutline(lac_x):
    """Convert `f([1,2])` to `f(1,2)` call."""
    return _cutline(*lac_x)
