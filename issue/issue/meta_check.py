#!/bin/python
# -*- coding: utf-8 -*-
import sys
import json
import re
from datetime import datetime
import argparse

"""
Meta检查
"""
class MetaCheck(object):
    def __init__(self, meta_file, pass_meta_file, bad_meta_file):
        self.meta_file = meta_file

        self.pass_meta_file = pass_meta_file
        self.bad_meta_file = bad_meta_file

        self.pass_meta_writer = open(pass_meta_file, "w")
        self.bad_meta_writer = open(bad_meta_file, "w")

        self.no_access_url = 0
        self.json_fail = 0
        self.incomplete = 0
        self.total = 0
        self.pass_count = 0
        self.dup = 0

        self.nullable_key = ["abstracts"]
        self.pass_meta_map = {} # used to uniq

    def __del__(self):
        self.pass_meta_writer.close()
        self.bad_meta_writer.close()

    def start(self):
        with open(self.meta_file) as f:
            for line in f:
                try:
                    self.total = self.total + 1
                    line = line.strip()
                    json_data = json.loads(line)
                except Exception as e:
                    self.json_fail = self.json_fail + 1
                    continue

                if "access_url" not in json_data or json_data["access_url"] == "":
                    self.no_access_url = self.no_access_url + 1
                    continue
                
                access_url = json_data["access_url"]
                
                fail = False
                for key, value in json_data.iteritems():
                    key = key.strip(":").strip()
                    value = value.strip()
                    if value == "" and key not in self.nullable_key:
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
                    title = json_data["title"]
                    if title != self.pass_meta_map[access_url]:
                        pass
                        #raise Exception("same url with different title, not gonna happen :%s" % access_url)
                    self.dup = self.dup + 1
                    continue

                self.pass_count = self.pass_count + 1
                self._mark_success_record(json_data)
                self.pass_meta_map[access_url] = json_data["title"]

        print "total: %d, no_access_url: %d, json_fail: %d, incomplete: %d, dup_count: %d, pass_count: %d. pass meta save to: %s, fail meta save to :%s" \
            % (self.total, self.no_access_url, self.json_fail, self.incomplete, self.dup, self.pass_count, self.pass_meta_file, self.bad_meta_file)

    def _mark_success_record(self, json_data):
        """
        Mark an success record.

        对Key做一些归一化的工作，同时也可以加一些必备的字段

        @param json_data
        """
        convert_data = {}
        for key, value in json_data.iteritems():
            key = key.strip(":").strip().lower()
            value = value.strip()
            convert_data[key] = value

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
    parser.add_argument('-p', "--pass_meta", default="pass_meta", help="file to save pass meta")
    parser.add_argument('-b', "--bad_meta", default="bad_meta", help="file to save bad meta")
    return parser
    
if __name__ == '__main__':
    meta_file = sys.argv[1]
    args = parse_init().parse_args()
    merge_meta = MetaCheck(meta_file = args.file, pass_meta_file = args.pass_meta, bad_meta_file = args.bad_meta)
    merge_meta.start()
