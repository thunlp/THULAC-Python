# THULAC：一个高效的中文词法分析工具包
## 目录
* [项目介绍](#项目介绍)
* [编译和安装](#编译和安装)
* [使用方式](#使用方式)
* [各类分词的性能对比](#各类分词的性能对比)
* [词性解释](#词性解释)
* [THULAC模型介绍](#THULAC模型介绍)
* [注意事项](#注意事项)
* [其他语言实现](#其他语言实现)
* [历史](#历史)
* [开源协议](#开源协议)
* [相关论文](#相关论文)
* [作者](#作者)

## 项目介绍

THULAC（THU Lexical Analyzer for Chinese）由清华大学自然语言处理与社会人文计算实验室研制推出的一套中文词法分析工具包，具有中文分词和词性标注功能。THULAC具有如下几个特点：

1. 能力强。利用我们集成的目前世界上规模最大的人工分词和词性标注中文语料库（约含5800万字）训练而成，模型标注能力强大。
2. 准确率高。该工具包在标准数据集Chinese Treebank（CTB5）上分词的F1值可达97.3％，词性标注的F1值可达到92.9％，与该数据集上最好方法效果相当。
3. 速度较快。同时进行分词和词性标注速度为300KB/s，每秒可处理约15万字。只进行分词速度可达到1.3MB/s。

## 编译和安装
* python版(兼容python2.x版和python3.x版)
    1. 从github下载(需下载模型文件，见[获取模型](#2获取模型))
	
		```
		将thulac文件放到目录下，通过 import thulac 来引用
		thulac需要模型的支持，需要将下载的模型放到thulac目录下。
		```
	2. pip下载(自带模型文件)
		
		```
		sudo pip install thulac
		通过 import thulac 来引用
		```

## 使用方式(新增[fast接口](#14fast接口))
### 1.分词和词性标注程序
#### 1.1.接口使用示例
* python版

	```
	代码示例1
	import thulac	

	thu1 = thulac.thulac()  #默认模式
	text = thu1.cut("我爱北京天安门", text=True)  #进行一句话分词
	print(text)
	```
	
	```
	代码示例2
	thu1 = thulac.thulac(seg_only=True)  #只进行分词，不进行词性标注
	thu1.cut_f("input.txt", "output.txt")  #对input.txt文件内容进行分词，输出到output.txt
	```
	
#### 1.2.接口参数

* `thulac(user_dict=None, model_path=None, T2S=False, seg_only=False, filt=False, deli='_') `初始化程序，进行自定义设置

	```
	user_dict	      	设置用户词典，用户词典中的词会被打上uw标签。词典中每一个词一行，UTF8编码
	T2S					默认False, 是否将句子从繁体转化为简体
	seg_only	   		默认False, 时候只进行分词，不进行词性标注
	filt		   		默认False, 是否使用过滤器去除一些没有意义的词语，例如“可以”。
	model_path	 	    设置模型文件所在文件夹，默认为models/
	deli	 	      	默认为‘_’, 设置词与词性之间的分隔符
    rm_space            默认为False, 是否去掉原文本中的空格后再进行分词
	```
	
* `cut(文本, text=False)` 对一句话进行分词

	```
	text 				默认为False, 是否返回文本，不返回文本则返回一个二维数组([[word, tag]..]),seg_only模式下tag为空字符。
	```

* `cut_f(输入文件, 输出文件)` 对文件进行分词

* `run()` 命令行交互式分词(屏幕输入、屏幕输出)

#### 1.3.命令行运行(限pip安装使用)
直接调用

	python -m thulac input.txt output.txt
	#从input.txt读入，并将分词和词性标注结果输出到ouptut.txt中

	#如果只需要分词功能，可在增加参数"seg_only" 
	python -m thulac input.txt output.txt seg_only

#### 1.4.fast接口
(请[下载](https://github.com/thunlp/THULAC.so)make后将得到的libthulac.so放入models文件夹同目录下)

有两个函数实现了fast接口，仅函数名改变，参数使用同普通函数
```
cut -> fast_cut, cut_f -> fast_cut_f
```


### 2.获取模型

THULAC需要分词和词性标注模型的支持，获取下载好的模型用户可以登录[thulac.thunlp.org](http://thulac.thunlp.org/message_v1_1)网站填写个人信息进行下载，并放到THULAC的根目录即可，或者使用参数`model_path`指定模型的位置。

## 代表分词软件的性能对比
我们选择LTP、ICTCLAS、结巴分词等国内代表分词软件与THULAC做性能比较。我们选择Windows作为测试环境，根据第二届国际汉语分词测评发布的国际中文分词测评标准，对不同软件进行了速度和准确率测试。

在第二届国际汉语分词测评中，共有四家单位提供的测试语料（Academia Sinica、 City University 、Peking University 、Microsoft Research）, 在评测提供的资源[icwb2-data](http://sighan.cs.uchicago.edu/bakeoff2005/)中包含了来自这四家单位的训练集（training）、测试集（testing）, 以及根据各自分词标准而提供的相应测试集的标准答案（icwb2-data/scripts/gold）．在icwb2-data/scripts目录下含有对分词进行自动评分的perl脚本score。

我们在统一测试环境下，对若干流行分词软件和THULAC进行了测试，使用的模型为各分词软件自带模型。THULAC使用的是随软件提供的简单模型Model_1。评测环境为 Intel Core i5 2.4 GHz 评测结果如下：

msr_test（560KB）

|Algorithm | Time| Precision | Recall|
|:------------|-------------:|------------:|-------:|
|LTP-3.2.0 | 3.21s  | 0.867 | 0.896|
|ICTCLAS(2015版) | 0.55s | 0.869 | 0.914|
|jieba|0.26s|0.814|0.809|
|THULAC | 0.62s  | 0.877 | 0.899|

pku_test（510KB）

|Algorithm | Time| Precision | Recall|
|:------------|-------------:|------------:|-------:|
|LTP-3.2.0 | 3.83s  | 0.960 | 0.947|
|ICTCLAS(2015版) | 0.53s | 0.939 | 0.944|
|jieba|0.23s|0.850|0.784|
|THULAC | 0.51s  | 0.944 | 0.908|

除了以上在标准测试集上的评测，我们也对各个分词工具在大数据上的速度进行了评测，结果如下：

CNKI_journal.txt（51 MB）

|Algorithm | Time | Speed |
|:------------|-------------:|------------:|
|LTP-3.2.0 | 348.624s  | 149.80KB/s|
|ICTCLAS(2015版) | 106.461s | 490.59KB/s|
|jieba|22.5583s|2314.89KB/s|
|THULAC | 42.625s  | 1221.05KB/s|


## 词性解释

```
n/名词 np/人名 ns/地名 ni/机构名 nz/其它专名
m/数词 q/量词 mq/数量词 t/时间词 f/方位词 s/处所词
v/动词 a/形容词 d/副词 h/前接成分 k/后接成分 
i/习语 j/简称 r/代词 c/连词 p/介词 u/助词 y/语气助词
e/叹词 o/拟声词 g/语素 w/标点 x/其它 
```

## THULAC模型介绍
1. 我们随THULAC源代码附带了简单的分词模型Model_1，仅支持分词功能。该模型由人民日报分词语料库训练得到。

2. 我们随THULAC源代码附带了分词和词性标注联合模型Model_2，支持同时分词和词性标注功能。该模型由人民日报分词和词性标注语料库训练得到。

3. 我们还提供更复杂、完善和精确的分词和词性标注联合模型Model_3和分词词表。该模型是由多语料联合训练训练得到（语料包括来自多文体的标注文本和人民日报标注文本等）。由于模型较大，如有机构或个人需要，请填写“[doc/资源申请表.doc](http://thulac.thunlp.org/register)”，并发送至 thunlp@gmail.com ，通过审核后我们会将相关资源发送给联系人。


## 注意事项

该工具目前仅处理UTF8编码中文文本，之后会逐渐增加支持其他编码的功能，敬请期待。

## 其他语言实现

### THULAC（C++版）
[https://github.com/thunlp/THULAC](https://github.com/thunlp/THULAC)

### THULAC（Java版）
[https://github.com/thunlp/THULAC-Java](https://github.com/thunlp/THULAC-Java)

### THULAC（so版）
[https://github.com/thunlp/THULAC.so](https://github.com/thunlp/THULAC.so)

## 历史

|更新时间 | 更新内容|
|:------------|:-------------:| 
|2017-01-17| 在pip上发布THULAC分词python版本。|
|2016-09-29| 增加THULAC分词so版本。|
|2016-03-31| 增加THULAC分词python版本。|
|2016-01-20| 增加THULAC分词Java版本。|
|2016-01-10| 开源THULAC分词工具C++版本。|


## 开源协议
1. THULAC面向国内外大学、研究所、企业以及个人用于研究目的免费开放源代码。
2. 如有机构或个人拟将THULAC用于商业目的，请发邮件至thunlp@gmail.com洽谈技术许可协议。
3. 欢迎对该工具包提出任何宝贵意见和建议。请发邮件至thunlp@gmail.com。
4. 如果您在THULAC基础上发表论文或取得科研成果，请您在发表论文和申报成果时声明“使用了清华大学THULAC”，并按如下格式引用：

* **中文： 孙茂松, 陈新雄, 张开旭, 郭志芃, 刘知远. THULAC：一个高效的中文词法分析工具包. 2016.**

* **英文： Maosong Sun, Xinxiong Chen, Kaixu Zhang, Zhipeng Guo, Zhiyuan Liu. THULAC: An Efficient Lexical Analyzer for Chinese. 2016.**


## 相关论文
* Zhongguo Li, Maosong Sun. Punctuation as Implicit Annotations for Chinese Word Segmentation. Computational Linguistics, vol. 35, no. 4, pp. 505-512, 2009.


## 作者

[Maosong Sun](http://www.thunlp.org/site2/index.php/zh/people?id=16) （孙茂松，导师）,  Xinxiong Chen（陈新雄，博士生）,  Kaixu Zhang (张开旭，硕士生）,  Zhipeng Guo（郭志芃，本科生）, Junhua Ma （马骏骅，访问学生）,  [Zhiyuan Liu](http://www.thunlp.org/~lzy/)（刘知远，助理教授）.


