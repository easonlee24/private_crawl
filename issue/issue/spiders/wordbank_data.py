#!/usr/bin/env python
# -*- coding: utf-8 -*-
import scrapy
import re
import sys
import urlparse
import sys
from scrapy.http.request import Request

reload(sys)
sys.setdefaultencoding('utf8')

class WordBankDataSpider(scrapy.Spider):
    name = "wordbank_data"

    def __init__(self, url_file=None, save_dir = None, *args, **kwargs):
        super(WordBankDataSpider, self).__init__(*args, **kwargs)
        self.url_file = url_file
        self.save_dir = save_dir

    def start_requests(self):
        with open(self.url_file, "rb") as f:
            for line in f:
                infos = line.split()

                country_name = " ".join(infos[0:-2])
                download_url = infos[-1]
                meta = {'filename': country_name + ".csv"}
                yield Request(download_url, self.download_file, meta = meta)


    def download_file(self, response):
        filepath = self.save_dir + "/" + response.meta['filename']

        with open(filepath, "wb") as f:
            f.write(response, body)
        f.close()
