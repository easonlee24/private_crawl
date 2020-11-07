#!/usr/bin/env python
# -*- coding:UTF-8 -*-
"""
@desc 用来对爬取下来的元数据做一个简单的质检
@author EasonLee
@date 2020/07/18
"""
import scrapy
import re
import sys
import urlparse
import sys
import os.path
import os
import errno
import random
import time
import json
import shutil
from scrapy.http.request import Request
reload(sys)
sys.setdefaultencoding('utf8')

class Check:
    def __int__(self):
        pass

    def check(self, filename):
        with open(filename) as f:
            journal_stat = {}
            for line in f:
                json_data = json.loads(line.strip())

                journal_url = json_data["journal_url"]
                volumn = json_data["source_volume"]
                issue = json_data["source_issue"]

                """
                以下是关键的数据结构,存放每个期刊的检测结果,当前只存了volumn_stat
                {
                    "journalA" : {
                        "volumn_stat" : {
                            "volumn_a": {
                                "issue_number": 1
                            },
                            "volumn_b" : {
                                "issue_number": 2
                            }
                        }
                    }
                }
                """
                if journal_url not in journal_stat:
                    journal_stat[journal_url] = {
                        "volumn_stat": {

                        }
                    }

                if volumn not in journal_stat[journal_url]["volumn_stat"]:
                    journal_stat[journal_url]["volumn_stat"][volumn] = {"issue_number": 0, "issues": []}

                if issue not in journal_stat[journal_url]["volumn_stat"][volumn]["issues"]:
                    journal_stat[journal_url]["volumn_stat"][volumn]["issues"].append(issue)
                    journal_stat[journal_url]["volumn_stat"][volumn]["issue_number"] += 1

                for journal, journal_s in journal_stat.items():
                    for volumn, volomu_stat in journal_s["volumn_stat"].items():
                        #对每一个volumn_stat里的issue进行排序
                        volomu_stat["issues"] = sorted(volomu_stat["issues"], key=int)

        print journal_stat

        for journal, journal_s in journal_stat.items():
            print "journal %s, volumn %s" % (journal, sorted(journal_s["volumn_stat"].keys()))



if __name__ == "__main__":
    url_file = sys.argv[1]
    check = Check()
    check.check(url_file)
