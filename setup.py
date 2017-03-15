#coding: utf-8
from setuptools import setup, find_packages

setup(
  name = 'thulac',
  # packages = ['thulac_test'], # this must be the same as the name above
  version = '0.1.1',
  description = 'A efficient Chinese text segmentation tool',
  author = 'thunlp',
  url = 'https://github.com/thunlp/THULAC-Python', # use the URL to the github repo
  author_email = 'liuzy@tsinghua.edu.cn',
  download_url = 'https://github.com/thunlp/THULAC-Python/archive/master.zip', # I'll explain this in a second
  classifiers=[
    'Programming Language :: Python :: 2.4',
    'Programming Language :: Python :: 2.5',
    # 'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.1',
    # 'Programming Language :: Python :: 3.2',
    # 'Programming Language :: Python :: 3.3',
    'Programming Language :: Python :: 3.4',
],
  keywords = ['segmentation'], # arbitrary keywords
  packages = find_packages(),
  package_data={'': ['*.txt', '*.dat', '*.bin', 'model_w']}
)