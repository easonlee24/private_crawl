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
        origin_title = title

        title = re.sub("[\?]$", "", title)
        title = re.sub("[:\?,] ?", "_", title)
        title = re.sub("[&\.%\+\'\"]", "", title)
        #title = re.sub(" +", "_", title)
        title = title.replace(" ", "_")
        #title = title.replace(".", "")# Web 2.0 ==> Web_20
        #不知道为啥?不能在sub函数里面替换了
        #title = title.replace("? ", "_")
        #title = title.replace(": ", "_")
        #title = title.replace(",", "_")
        pdf_path = pdf_dir + "\\" + title + ".pdf"
        if os.path.exists(pdf_path):
            #print "%s exist" % pdf_path
            exist_count = exist_count + 1
        else:
            print "title: %s, pdf: %s not exist" % (origin_title, pdf_path)
            non_exist_count = non_exist_count + 1

print "exist_count:%d, non_exist_count: %d" % (exist_count, non_exist_count)
