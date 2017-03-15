#coding: utf-8
import sys
from ctypes import c_char, c_char_p, cast, POINTER, c_wchar_p
'''本模块用于兼容python2和python3，所有函数都会返回适用于对应版本的处理函数'''

isPython2 = sys.version_info[0] == 2
def decodeGenerator():
    '''兼容2的decode函数'''
    if(isPython2):
        return lambda s: s.decode('utf-8')
    return lambda s: s

def encodeGenerator():
    '''兼容2的encode函数'''
    if(isPython2):
        return lambda s: s.encode('utf-8')
    return lambda s: s

def cInputGenerator():
    '''兼容2的raw_input和3的input函数'''
    if(isPython2):
        return lambda : raw_input().strip()
    else:
        return lambda : input().strip()

def chrGenerator():
    '''兼容2的unichr和3的chr函数'''
    if(isPython2):
        return lambda s: unichr(s)
    else:
        return lambda s: chr(s)

def fixC_char_p():
    '''针对python3中ctypes中c_char_p字符串参数需要手动转码的函数'''
    if(isPython2):
        return lambda s: s
    return lambda s: s.encode('utf-8')
