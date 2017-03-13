# from distutils.core import setup, find_packages
from setuptools import setup, find_packages

setup(
  name = 'thulac',
  # packages = ['thulac_test'], # this must be the same as the name above
  version = '0.0.4',
  description = 'A efficient Chinese text segmentation tool',
  author = 'thunlp',
  url = 'https://github.com/thunlp/THULAC-Python', # use the URL to the github repo
  author_email = 'liuzy@tsinghua.edu.cn',
  download_url = 'https://github.com/thunlp/THULAC-Python/archive/master.zip', # I'll explain this in a second

  keywords = ['segmentation'], # arbitrary keywords
  classifiers = [],
  packages = find_packages(),
  package_data={'': ['*.txt', '*.dat', '*.bin', 'model_w']}
)