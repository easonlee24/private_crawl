#!/usr/bin/env python
# -*- coding: utf-8 -*-
import scrapy
import re
import sys
import urlparse
import sys
import os.path
import os
import errno
from scrapy.http.request import Request

reload(sys)
sys.setdefaultencoding('utf8')

"""
This spider is custion file download spider, you can use this spider like this:

scrapy file_download -a url_file=[@url_file_path]

Notice: format of [url_file[ must like following:

[download_file_name],[download_url]
[download_file_name],[download_url]
[download_file_name],[download_url]
[download_file_name],[download_url]
[download_file_name],[download_url]
[download_file_name],[download_url]
.......

"""
class FileDownload(scrapy.Spider):
    name = "file_download"

    def __init__(self, url_file=None, save_dir = None, *args, **kwargs):
        super(FileDownload, self).__init__(*args, **kwargs)
        self.url_file = url_file
        self.save_dir = save_dir

    def start_requests(self):
        with open(self.url_file, "rb") as f:
            for line in f:
                infos = line.split('|')

                filename = infos[0]
                download_url = infos[1]
                meta = {'filename': filename}
                yield Request(download_url, self.download_file, meta = meta, dont_filter=True)


    def download_file(self, response):
        filename = response.meta['filename']
        filename = filename.replace("/", "_")
        filename = filename.replace(": ", "_")
        filename = self.save_dir + "/" + filename
        print "save to %s" % filename

        with open(filename, "wb") as f:
            f.write(response.body)
        f.close()
