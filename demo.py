#coding:utf-8

import thulac

thu1 = thulac.thulac(seg_only=True, model_path="请查看README下载相关模型放到thulac根目录或在这里写路径")  #设置模式为行分词模式
a = thu1.cut("我爱北京天安门")

print(a)
