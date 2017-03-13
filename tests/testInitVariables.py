#coding: utf-8
import thulac
import sys
prefix = sys.path[0]

def testSegOnly():
	test_text = "我爱北京天安门"
	thu = thulac.thulac(seg_only = True)
	gold = thu.cut(test_text, text = True)
	assert gold == "我 爱 北京 天安门"

#由于Tag模型初始化耗时较大，在这里将两个Tag模型的测试放在一起
def testTagAndDeli():
	test_text = "我爱北京天安门"
	thu = thulac.thulac(deli = '#')
	gold = thu.cut(test_text, text = True)
	assert gold == "我#r 爱#v 北京#ns 天安门#ns"

def testUserDict():
	test_text = "我爱北京天安门"
	thu = thulac.thulac(seg_only = True, user_dict = prefix + "/userDict.txt")
	gold = thu.cut(test_text, text = True)
	assert gold == "我爱北京天安门"

def testT2S():
	test_text = "我愛北京天安門"
	thu = thulac.thulac(seg_only = True, T2S = True)
	gold = thu.cut(test_text, text = True)
	print gold
	assert gold == "我 爱 北京 天安门"

def testFilt():
	test_text = "我可以爱北京天安门"
	thu = thulac.thulac(seg_only = True, filt = True)
	gold = thu.cut(test_text, text = True)
	print gold
	assert gold == "我 爱 北京 天安门"

