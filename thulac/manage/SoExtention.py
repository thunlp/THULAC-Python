#!/usr/bin/env python
# -*- coding: utf-8 -*-
from ctypes import cdll, c_char, c_char_p, cast, POINTER
from ..base.compatibility import fixC_char_p, isPython2
import os.path
import platform

fixCCP = fixC_char_p()
# path = os.path.dirname(os.path.realpath(__file__)) #设置so文件的位置
class SoExtention:
    def __init__(self, model_path, user_dict_path, t2s, just_seg, pre_alloc_size=1024*1024*16):
        root = os.path.dirname(os.path.dirname(os.path.realpath(__file__))) #设置so文件的位置
        self._lib = cdll.LoadLibrary(root+'/libthulac.so') #读取so文件
        self._lib.init(c_char_p(fixCCP(model_path)), c_char_p(fixCCP(user_dict_path)), int(pre_alloc_size), int(t2s), int(just_seg)) #调用接口进行初始化

    def clear(self):
        if self._lib != None: self._lib.deinit()

    def seg(self, data):
        r = self._lib.seg(c_char_p(fixCCP(data)))
        assert r > 0
        self._lib.getResult.restype = POINTER(c_char)
        p = self._lib.getResult()
        s = cast(p,c_char_p)
        d = '%s'%s.value
        if(isPython2):
            self._lib.freeResult();
            return d
        s = s.value.decode('utf-8')
        self._lib.freeResult();
        return s
