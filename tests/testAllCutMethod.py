#coding: utf-8
import thulac
import sys
prefix = sys.path[0]

thu = thulac.thulac(seg_only = True)

def readFile(file_name):
    with open(file_name) as result:
        for line in result:
            return line

def testCutFile():
    thu.cut_f(prefix +"/textForTest/input.txt", prefix +"/textForTest/output.txt")
    print(readFile(prefix +"/textForTest/output.txt"))
    assert readFile(prefix + "/textForTest/output.txt") == "我 爱 北京 天安门\n"

def testFastCut():
    test_text = "我爱北京天安门"
    gold = thu.fast_cut(test_text, text = True)
    assert gold == "我 爱 北京 天安门"

def testFastCutFile():
    thu.fast_cut_f(prefix +"/textForTest/input.txt", prefix +"/textForTest/output.txt")
    print(readFile(prefix +"/textForTest/output.txt"))
    assert readFile(prefix +"/textForTest/output.txt") == "我 爱 北京 天安门\n"
