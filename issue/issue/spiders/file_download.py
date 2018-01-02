#!/usr/bin/env python
# -*- coding:UTF-8 -*-
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
from scrapy.http.request import Request
from utils import  Utils

reload(sys)
sys.setdefaultencoding('utf8')

"""
This spider is custion file download spider, you can use this spider like this:

scrapy file_download -a url_file=[@url_file_path]

Notice: format of [url_file[ must like following:

format1:
[download_file_name]|[download_url]
[download_file_name]|[download_url]
[download_file_name]|[download_url]
[download_file_name]|[download_url]
[download_file_name]|[download_url]
[download_file_name]|[download_url]

fotmat2:
download_url
download_url
download_url
download_url
download_url
download_url

.......
1. 如果没有传入save_dir, 那么就写到当前目录
2. 格式2中，downliad_url里面应该包含doi,这样filename默认就是doi
"""
class FileDownload(scrapy.Spider):
    name = "file_download"

    def __init__(self, url_file=None, save_dir = None, download_txt = "False", start_count = 0, *args, **kwargs):
        super(FileDownload, self).__init__(*args, **kwargs)
        self.url_file = url_file
        self.download_txt = download_txt.lower() == "true"
        if save_dir is None:
            self.save_dir = ""
        else:
            self.save_dir = save_dir
        self.start_count = start_count
        self.pdf_error_file_write = open("./not_pdf_url", "w")
        self.pdf_error_count = 0
        self.download_count = 0
        self.txt_download_count = 0
        self.pdf_exist_count = 0

    def start_requests(self):
        download_count = 0
        exist_count = 0
        current_index = 0
        with open(self.url_file, "rb") as f:
            for line in f:
                current_index = current_index + 1
                if current_index < self.start_count:
                    continue

                line = line.strip()
                infos = line.split('|')
                if len(infos) == 1:
                    download_url = infos[0].replace("full", "pdf")
                    #filename = "_".join(download_url.split('/')[-2:]) + ".pdf"
                    filename = "_".join(download_url.split('/')[-1:]) + ".pdf"
                else:
                    filename = infos[0]
                    download_url = infos[1].strip()
                if download_url == '':
                    continue
                meta = {'filename': filename}
                pdf_path = filename
                #print "origin filename: %s" % line
                pdf_path = pdf_path.replace(":", "_")
                pdf_path = pdf_path.replace("/", "_")
                if self.save_dir != "":
                    pdf_path = self.save_dir + "\\" + pdf_path

                another_pdf_path =  pdf_path.replace("txt", "pdf")
                if os.path.exists(pdf_path) or os.path.exists(another_pdf_path):
                    self.pdf_exist_count = self.pdf_exist_count + 1
                    print "pdf exist: %s, now exist count :%d" % (pdf_path, self.pdf_exist_count)
                    continue
                else:
                    print "pdf not exist %s" % pdf_path

                try:
                    #download_url = download_url + "?download=true"
                    #time.sleep(random.randint(30,60))
                    yield Request(download_url, self.download_file, meta = meta, dont_filter=True)
                except Exception as e:
                    pass

    def download_file(self, response):
        filename = response.meta['filename']
        filename = filename.replace(":", "_")
        filename = filename.replace("/", "_")
        if self.save_dir != "":
            filename = self.save_dir + "\\" + filename

        if not self._content_is_pdf(response):
            if not self.download_txt:
                self.pdf_error_file_write.write(response.url)
                self.pdf_error_file_write.write("\n")
                self.pdf_error_count = self.pdf_error_count + 1
                self._print_download_status()
                return

            #如果是下载国研网的话，不是pdf类型的页面，则把正文爬取下来，并保存到txt文件里
            content = self.download_guoyan_content(response)
            self.txt_download_count = self.txt_download_count + 1
            if content == "":
                raise Exception("cannot get content from url: %, source url :%s" %  (response.url, response.request.url))

        else:
            filename = filename.replace(".txt", ".pdf")
            content = response.body
            self.download_count = self.download_count + 1

        print "save file to %s" % filename
        self._print_download_status()

        with open(filename, "wb") as f:
            f.write(content)
        f.close()

    def _content_is_pdf(self, response):
        content_type = response.headers['Content-Type']
        if content_type.find("application/pdf") != -1:
            return True

        #对国研网来说, pdf类型的content type为html,但是header里面附带了这个字段
        if 'Content-Disposition' in response.headers:
            return True

        return False

    def _print_download_status(self):
        print "%s pdf_error_count is :%d, exist_count: %d, pdf_download_count is %d, txt_download_count: %d" % (Utils.current_time(), self.pdf_error_count, self.pdf_exist_count, self.download_count, self.txt_download_count)

    #国研网有的详情页是需要从网页上下载得到txt文件
    def download_guoyan_content(self, response):
        paras = response.xpath("//*[@id='docContent']/p")
        texts = ""
        for para in paras:
            para_content = " ".join([v.replace("\n", " ") for v in para.xpath(".//text()").extract()]).strip()
            if para_content != "":
                texts += para_content + "\n"
        return texts
