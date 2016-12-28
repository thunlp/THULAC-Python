#coding = utf-8
from .character.CBModel import CBModel
from .character.CBNGramFeature import CBNGramFeature
from .character.CBTaggingDecoder import CBTaggingDecoder
from .manage.Preprocesser import Preprocesser
from .manage.Postprocesser import Postprocesser
from .manage.Filter import Filter
import time
import os
import sys

class thulac:
    def __init__(self, args):
        self.user_specified_dict_name = None
        self.model_path_char = None
        self.separator = '_'
        self.useT2S = False
        self.seg_only = False
        self.useFilter = False
        self.use_second = False
        self.input_file = ""
        self.output_file = ""
        self.coding = "utf-8"
        self.version = sys.version_info[0]
        c = 0
        if(len(args) > 0):
            args = args.split(" ")
        else:
            args = []
        while(c < len(args)):
            arg = args[c]
            if(arg == "-t2s"):
                self.useT2S = True
            # elif(arg == "-user"):
                # self.user_specified_dict_name = arg
            elif(arg == "-deli"):
                c += 1
                self.separator = args[c]
            elif(arg == "-model_dir"):
                c += 1
                self.model_path_char = args[c]
            elif(arg == "-seg_only"):
                self.seg_only = True
            elif(arg == "-filter"):
                self.useFilter = True
            elif(arg == "-input"):
                c += 1
                self.input_file = args[c]
            elif(arg == "-output"):
                c += 1
                self.output_file = args[c]
            else:
                return
            c = c + 1
        self.prefix = ""
        if(self.model_path_char is not None):
            self.prefix = self.model_path_char
            if(self.prefix[-1] != "/"):
                self.prefix = self.prefix + "/"
        else:
            self.prefix = os.path.dirname(os.path.realpath(__file__))+"/models/"
        self.oiraw = ""
        self.raw = ""
        self.poc_cands = []
        self.cws_tagging_decoder = None
        self.tagging_decoder = None
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
        self.preprocesser = Preprocesser()
        self.preprocesser.setT2SMap((self.prefix+"t2s.dat"))
        self.nsDict = Postprocesser((self.prefix+"ns.dat"), "ns", False)
        self.idiomDict = Postprocesser((self.prefix+"idiom.dat"), "i", False)
        # self.userDict = None
        # if(self.user_specified_dict_name is not None):
        #     self.userDict = Postprocesser(self.user_specified_dict_name, "uw", True)
        self.myfilter = None
        if(self.useFilter):
            self.myfilter = Filter((self.prefix+"xu.dat"), (self.prefix+"time.dat"))

    def encode(self, s):
        if(self.version == 2):
            return s.encode(self.coding)
        return s

    def cut(self, oiraw):
        if(self.version == 2):
            oiraw = oiraw.decode(self.coding)
        if(self.useT2S):
            traw, poc_cands = self.preprocesser.clean(oiraw)
            raw = self.preprocesser.T2S(traw)
        else:
            raw, poc_cands = self.preprocesser.clean(oiraw)

        if(len(raw) > 0):
            if(self.seg_only):
                tmp, tagged = self.cws_tagging_decoder.segmentTag(raw, poc_cands)
                segged = self.cws_tagging_decoder.get_seg_result()
                # if(self.userDict is not None):
                    # self.userDict.adjustSeg(segged)
                if(self.useFilter):
                    self.myfilter.adjustSeg(segged)
                self.nsDict.adjustSeg(segged)
                self.idiomDict.adjustSeg(segged)
                
                return list(map(lambda x: self.encode(x), segged))
                
            else:
                tmp, tagged = self.tagging_decoder.segmentTag(raw, poc_cands)

                # if(self.userDict is not None):
                    # self.userDict.adjustTag(tagged)
                if(self.useFilter):
                    self.myfilter.adjustTag(tagged)
                self.nsDict.adjustTag(tagged)
                self.idiomDict.adjustTag(tagged)
                    
                return list(map(lambda x: self.encode(x), segged))
        
    def run(self):
        start = time.clock()
        input_f = None
        output_f = None
        if(len(self.input_file) > 0):
            input_f = open(self.input_file, "r")
        if(len(self.output_file) > 0):
            output_f = open(self.output_file, "w")
        while(True):
            if(input_f is not None):
                oiraw = self.getRaw(input_f)
            else:
                oiraw = raw_input().strip()
            if(len(oiraw) < 1):
                break
            if(self.seg_only):
                segged = self.cut(oiraw)
                if(output_f is not None):
                    output_f.write(" ".join(segged))
                    output_f.write("\n")
                else:
                    print(" ".join(segged))
            else:
                tagged = self.cut(oiraw)
                if(output_f is not None):
                    output_f.write(" ".join(tagged))
                    output_f.write("\n")
                else:
                    print(" ".join(tagged))
        end = time.clock()
        print("Time used: %f s" % (end - start))
            

    def getRaw(self, inputfile):
        return inputfile.readline().strip()


# if __name__ == "__main__":
#     thu = thulac("-seg_only -input cs.txt -output out.txt")
#     thu.run()

