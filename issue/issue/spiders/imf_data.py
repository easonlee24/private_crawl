#!/usr/bin/env python
# -*- coding: utf-8 -*-
import scrapy
import re
import sys
import urlparse
import sys
import json
from scrapy.http.request import Request

reload(sys)
sys.setdefaultencoding('utf8')

class ImfDataSpider(scrapy.Spider):
    name = "imf_data"

    def __init__(self, url_file=None, save_dir = None, *args, **kwargs):
        super(ImfDataSpider, self).__init__(*args, **kwargs)
        self.url_file = url_file
        self.save_dir = save_dir

    def start_requests(self):
        titles = {}
        with open(self.url_file, "rb") as f:
            for line in f:
                json_data = json.loads(line)

                source_title = json_data['source_title'].replace('\n', '').replace('\t', '').strip()
                doi = json_data['doi']
                if source_title in titles:
                    continue

                doi = doi.replace("http://dx.doi.org/", "")
                doi = doi.split("/")[1].split('.')[0]

                filename = source_title + "_doi_" + doi

                titles[filename] = json_data['issue_url']

        for (filename, url) in titles.iteritems():
            meta = {"filename" : filename}
            yield Request(url, self.parse_issue_link, dont_filter=True, meta = meta)

    def parse_issue_link(self, response):
        pdf_link = self.extract_with_xpath(response, "//*[@id='mainContent']/section[1]/div[1]/div/div/ul/li[class='pdf']/a/@href")
        epub_link = self.extract_with_xpath(response, "//*[@id='mainContent']/section[1]/div[1]/div/div/ul/li[class='epub']/a/@href")

        base_filename = response.meta['filename']
        if pdf_link != "":
            response.meta['filename'] = base_filename + ".pdf"
            yield response.follow(pdf_link, self.download_file, dont_filter=True, meta = response.meta)

        if epub_link != "":
            response.meta['filename'] = base_filename + ".epub"
            yield response.follow(pdf_link, self.download_file, dont_filter=True, meta = response.meta)
        
    def download_file(self, response):
        filepath = self.save_dir + "/" + response.meta['filename']

        with open(filepath, "wb") as f:
            f.write(response, body)
        f.close()

    def extract_with_xpath(self, root, xpath_str, default_value = ""):
        try:
            result = root.xpath(xpath_str).extract_first().strip()
        except Exception as e:
            result = default_value

        return result
