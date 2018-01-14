#!/bin/python
# -*- coding: utf-8 -*-
import sys
import json
import re
from datetime import datetime
from spiders.utils import Utils
import argparse
import os

"""
Meta检查，同时对key做一些归一化的操作
如果指定了pdf的保存目录，还会自动与pdf文件做join
"""
class MetaCheck(object):
    def __init__(self, args):
        self.args = args

        self.meta_file = args.file
        self.pass_meta_file = args.pass_meta_file
        self.bad_meta_file = args.bad_meta_file
        self.miss_pdf_file = args.miss_pdf_file

        self.no_access_url = 0
        self.json_fail = 0
        self.incomplete = 0
        self.total = 0
        self.pass_count = 0
        self.dup = 0
        self.pdf_exist = 0
        self.pdf_non_exist = 0

        self.required_key = [
            #"abstracts",
            #sage的 issue和pages有些确实为空。。。
            #"issue",
            #"pages"
            ]
        self.pass_meta_map = {} # used to uniq
        
        #把一些不规则的key, 都归一化为统一的key
        self.key_map = {
            "url" : "access_url",
            "pdf_download" : "pdf_url",
        }

    def __del__(self):
        self.pass_meta_writer.close()
        self.bad_meta_writer.close()
        self.miss_pdf_writer.close()

    def _init(self):
        #reverse_key_map记录了，那些规则的key,可能有哪些不规则的表达
        self.reverse_key_map = {}
        for k, v in self.key_map.items():
            if v in self.reverse_key_map:
                self.reverse_key_map[v].append(k)
            else:
                self.reverse_key_map[v] = [k]
        
        #创建一个workdir
        workdir = Utils.generate_workdir()
        self.pass_meta_file = workdir + "\\" + self.pass_meta_file
        self.bad_meta_file = workdir + "\\" + self.bad_meta_file
        self.miss_pdf_file = workdir + "\\" + self.miss_pdf_file
        self.pass_meta_writer = open(self.pass_meta_file, "w")
        self.bad_meta_writer = open(self.bad_meta_file, "w")
        self.miss_pdf_writer = open(self.miss_pdf_file, "w")


    def start(self):
        self._init()
        with open(self.meta_file) as f:
            for line in f:
                try:
                    self.total = self.total + 1
                    line = line.strip()
                    json_data = json.loads(line)
                except Exception as e:
                    self.json_fail = self.json_fail + 1
                    continue

                if not self._check_key_exist(json_data, "access_url"):
                    self.no_access_url = self.no_access_url + 1
                    continue
                
                access_url = self._get_value(json_data, "access_url")
                if access_url == "":
                    raise Exception("cannot get access_url from json data, not possible" % json_data)
                
                fail = False
                for key, value in json_data.iteritems():
                    key = key.strip(":").strip()
                    value = Utils.format_value(value)
                    if value == "" and key in self.required_key:
                        if key == "publish_year":
                            publish_data = self._get_value(json_data, "publish_date")
                            if publish_data != "":
                                #if publish data is also empty, there is no way to get publish_year
                                json_data["publish_year"] = publish_data.split()[-1]
                                continue

                        bad_record = {}
                        bad_record['reason'] = "%s empty" % key
                        bad_record['access_url'] = access_url
                        self._mark_bad_record(bad_record)
                        self.incomplete = self.incomplete + 1
                        fail = True
                        break

                if fail:
                    continue
                #this line in legal
                
                if access_url in self.pass_meta_map:
                    title = self._get_value(json_data, "title")
                    if title != self.pass_meta_map[access_url]:
                        #pass
                        raise Exception("same url with different title, not gonna happen :%s" % access_url)
                    self.dup = self.dup + 1
                    continue

                self.pass_count = self.pass_count + 1
                self._mark_success_record(json_data)
                self.pass_meta_map[access_url] = json_data["title"]

        if self.args.pdf_dir is not None:
            print "total: %d, no_access_url: %d, json_fail: %d, incomplete: %d, dup_count: %d, pass_count: %d. pdf_non_exist: %d, pdf_exist_count: %d, pass meta save to: %s, fail meta save to :%s, miss pdf url save to :%s" \
            % (self.total, self.no_access_url, self.json_fail, self.incomplete, self.dup, self.pass_count, self.pdf_non_exist, self.pdf_exist, self.pass_meta_file, self.bad_meta_file, self.miss_pdf_file)
        else:
            print "total: %d, no_access_url: %d, json_fail: %d, incomplete: %d, dup_count: %d, pass_count: %d. pass meta save to: %s, fail meta save to :%s, miss pdf url save to :%s" \
            % (self.total, self.no_access_url, self.json_fail, self.incomplete, self.dup, self.pass_count, self.pass_meta_file, self.bad_meta_file, self.miss_pdf_file)


    def _check_key_exist(self, json_data, key):
        """
        这里的key应该是规则的key
        """
        if key in json_data:
            return True
        
        if key in self.reverse_key_map:
            for alias_key in self.reverse_key_map[key]:
                if alias_key in json_data:
                    return True
        
        return False

    def _get_value(self, json_data, key, default = ""):
        """
        这里的key应该是规则的key
        """
        value = default
        if key in json_data:
            value = json_data[key]
        
        if key in self.reverse_key_map:
            for alias_key in self.reverse_key_map[key]:
                if alias_key in json_data:
                    value =  json_data[alias_key]
        
        return Utils.format_value(value)


    def _mark_success_record(self, json_data):
        """
        Mark an success record.

        1. 对Key做一些归一化的工作，同时也可以加一些必备的字段
        2. 如果指定了pdf save dir，则会和pdf文件做拼接

        @param json_data
        """
        publish_data = self._get_value(json_data, "publish_date")
        if "publish_year" not in json_data or json_data["publish_year"] == "":
            #if publish data is also empty, there is no way to get publish_year
            if "publish_date" in json_data:
                json_data["publish_year"] = publish_data.split()[-1]

        keywords = self._get_value(json_data, "keywords")

        json_data["keywords"] = keywords.replace("Keywords", "").strip()

        convert_data = {}
        for key, value in json_data.iteritems():
            key = key.strip(":").strip().lower()
            if key in self.key_map:
                key = self.key_map[key]

            value = Utils.format_value(value)
            convert_data[key] = value

        if self.args.pdf_dir is not None:
            filename = Utils.get_pdf_filename(json_data)
            pdf_path = os.path.join(self.args.pdf_dir, filename + ".pdf")  
            txt_path = os.path.join(self.args.pdf_dir, filename + ".txt")
            if os.path.exists(pdf_path):
                convert_data["pdf_path"] = filename + ".pdf"
                self.pdf_exist = self.pdf_exist + 1
            elif os.path.exists(txt_path):
                convert_data["pdf_path"] = filename + ".txt"
                self.pdf_exist = self.pdf_exist + 1
            else:
                #print "pdf path(%s) or txt path(%s) not exist" % (pdf_path, txt_path)
                convert_data["pdf_path"] = "wrong"
                self.pdf_non_exist = self.pdf_non_exist + 1
                pdf_link = self._get_value(json_data, "pdf_url")
                if pdf_link == "":
                    raise Exception("cannot get pdf_url from json %s" % json_data)
                self.miss_pdf_writer.write(pdf_link)
                self.miss_pdf_writer.write("\n")
                

        convert_data_str = json.dumps(convert_data)
        self.pass_meta_writer.write(convert_data_str)
        self.pass_meta_writer.write("\n")

    def _mark_bad_record(self, bad_record):
        """
        Mark an bad record

        @param bad_record, format:{"reason: ", "url"}
        """
        bad_record_str = json.dumps(bad_record)
        self.bad_meta_writer.write(bad_record_str)
        self.bad_meta_writer.write("\n")

def parse_init():
    """
    Init argument parser
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', "--file", required=True, help="meta file path")
    parser.add_argument('-d', "--pdf_dir", required=False, help="pdf save dir")
    parser.add_argument('-p', "--pass_meta_file", default="pass_meta", help="file to save pass meta")
    parser.add_argument('-b', "--bad_meta_file", default="bad_meta", help="file to save bad meta")
    parser.add_argument('-m', "--miss_pdf_file", default="miss_pdf_file", help="pdf link that fail to download")
    return parser
    
if __name__ == '__main__':
    meta_file = sys.argv[1]
    args = parse_init().parse_args()
    merge_meta = MetaCheck(args)
    merge_meta.start()
