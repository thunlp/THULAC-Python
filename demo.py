#coding=utf-8

import thulac

thu1 = thulac.thulac("-seg_only")  #设置模式为行分词模式
thu1.run() #根据参数运行分词程序，从屏幕输入输出
print " ".join(thu1.cut("我爱北京天安门")) #进行一句话分词

#==============================================
thu2 = thulac.thulac("-input cs.txt") #设置模式为分词和词性标注模式
thu2.run() #根据参数运行分词和词性标注程序，从cs.txt文件中读入，屏幕输出结果
print " ".join(thu2.cut("我爱北京天安门")) #进行一句话分词和词性标注
