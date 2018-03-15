#!/bin/python
# -*- coding: utf-8 -*-
import sys
import json
import re
import xlrd
import os
from datetime import datetime
from spiders.utils import  Utils

class OaConferenceFormat(object):
    """
    OA会议爬取完元数据以后，需要和excel里面的做一下join，并且归一化一下元数据
    """
    def __init__(self, origin_meta_file, excel_file):
        self.origin_meta_file = origin_meta_file
        self.excel_file = excel_file
        self.journal_meta = {}

    def start(self):
        self._load_journal_meta()
        with open(self.origin_meta_file) as f:
            for line in f:
                try:
                    line = line.strip()
                    json_data = json.loads(line)
                except Exception as e:
                    continue

                if json_data["from_url"] not in self.journal_meta:
                    raise Exception("conference_url %s not excepted" % json_data["from_url"])

                journal_meta = self.journal_meta[json_data["from_url"]]

                new_data = {}
                new_data["id"] = journal_meta["id"]
                new_data["conference"] = journal_meta["conference"]
                new_data["issn"] = json_data.get("issn")
                new_data["title"] = json_data.get("title")
                new_data["abstract"] = json_data.get("abstract")
                new_data["author"] = json_data.get("author")
                new_data["keywords"] = json_data.get("keywords")
                new_data["release_year"] = json_data.get("release_year")

                page = json_data.get("page", "").replace("Pages", "").replace("Page", "").strip()
                page_infos = page.split("-")
                if len(page_infos) != 1:
                    start_page = Utils.str_to_num(page_infos[0].strip())
                    end_page = Utils.str_to_num(page_infos[1].strip())
                    total_page = end_page - start_page + 1
                else:
                    start_page = Utils.str_to_num(page_infos[0].strip())
                    end_page = start_page
                    total_page = 1

                new_data["start_page"] = start_page
                new_data["end_page"] = end_page
                new_data["total_page"] = total_page
                new_data["pdf_path"] = os.path.join(
                    journal_meta["id"], Utils.get_pdf_filename(json_data))
                new_data["doi"] = json_data.get("doi")
                new_data["conference_url"] = json_data["from_url"]
                new_data["access_url"] = json_data["access_url"]
                new_data["pdf_url"] = json_data["pdf_url"]
                print json.dumps(new_data)

    def _load_journal_meta(self):
        data = xlrd.open_workbook(self.excel_file)

        #TODO 其他需求journal元数据表可能不是这样
        table = data.sheets()[1] #3rd sheet is main sheet
        nrows = table.nrows
        ncols = table.ncols
        for i in xrange(0,nrows):
            #TODO 前两行没用，其他需求可能不适用
            if (i < 1):
                continue

            rowValues= table.row_values(i)

            conference_url = rowValues[8]
            self.journal_meta[conference_url] = {
                "id": rowValues[1],
                "conference": rowValues[5],
                "release_year": rowValues[6],
            }

if __name__ == '__main__':
    origin_meta_file = sys.argv[1]
    excel_file = sys.argv[2]
    meta_format = OaConferenceFormat(origin_meta_file, excel_file)
    meta_format.start()
    
