# -*- coding:utf-8 -*- 
import sys
import json
import re
import os

"""
Ourui的元数据不是json的格式的，而是以|分隔的。具体格式如下：
TOPIC|GEO|TYPE|DATE|AUTHOR|TITLE

本脚本用来分析是否有楼下的PDF

Usage:python analyse_ourui.py [meta_file_path] [pdf_save_path]
"""
filename = sys.argv[1]
pdf_dir = sys.argv[2]

exist_count = 0
non_exist_count = 0
with open(filename) as fp:
    for line in fp:
        datas = line.strip().split('|')
        if len(datas) != 6:
            raise Exception("unexcept meta: %s" % line)

        title = datas[5]
        pdf_path = pdf_dir + "\\" + title
        if os.path.exists(pdf_path):
            exist_count = exist_count + 1
        else:
            non_exist_count = non_exist_count + 1

print "exist_count:%d, non_exist_count: %d" % (exist_count, non_exist_count)
