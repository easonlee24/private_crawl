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
import json
import shutil
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

format3:
[json_data]
[json_data]
.......
1. 如果没有传入save_dir, 那么就写到当前目录
2. 格式2中，downliad_url里面应该包含doi,这样filename默认就是doi
"""
class FileDownload(scrapy.Spider):
    name = "file_download"

    def __init__(self, url_file=None, save_dir = None, download_txt = "False", force_download = "False", is_worldbank = "False", start_count = 0, max_count = None, *args, **kwargs):
        super(FileDownload, self).__init__(*args, **kwargs)
        self.url_file = url_file
        self.download_txt = download_txt.lower() == "true"
        self.force_download = force_download.lower() == "true"
        self.is_worldbank = is_worldbank.lower() == "true"
        if save_dir is None:
            self.save_dir = ""
        else:
            self.save_dir = save_dir
        self.start_count = int(start_count)
        self.pdf_error_file_write = open("./not_pdf_url", "w")
        self.pdf_error_count = 0
        self.download_count = 0
        self.txt_download_count = 0
        self.pdf_exist_count = 0
        self.meta_error = 0
        self.request_count = 0
        self.max_count = max_count

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
                if Utils.is_json_string(line):
                    json_data = json.loads(line)
                    try:
                        if "pdf_path" in json_data:
                            filename = json_data["pdf_path"]
                        else:
                            doi = Utils.format_value(json_data['doi']).replace("DOI:", "").strip()
                            filename = Utils.doi_to_filname(doi)
                        if not filename.endswith(".pdf"):
                            filename = filename + ".pdf"
                    except Exception as e:
                        self.meta_error = self.meta_error + 1
                        self._print_download_status()
                        continue
                    download_url = Utils.format_value(json_data['pdf_url'])
                    #download_url = json_data['pdf_url']
                else:
                    infos = line.split('|')
                    if len(infos) == 1:
                        download_url = infos[0].replace("full", "pdf")
                        #filename = "_".join(download_url.split('/')[-2:]) + ".pdf"
                        filename = "_".join(download_url.split('/')[-1:]) + ".pdf"
                    else:
                        filename = infos[0]
                        if filename.find("pdf") == -1 and filename.find("txt") == -1:
                            filename = filename + ".pdf"
                        download_url = infos[1].strip()
                if download_url == '':
                    continue
                meta = {'filename': filename}
                pdf_path = filename
                #print "origin filename: %s" % line
                pdf_path = pdf_path.replace(":", "_")
                #pdf_path = pdf_path.replace("/", "_")
                if self.save_dir != "":
                    pdf_path = os.path.join(self.save_dir,pdf_path)

                another_pdf_path =  pdf_path.replace("txt", "pdf")
                if os.path.exists(pdf_path) or os.path.exists(another_pdf_path):
                    self.pdf_exist_count = self.pdf_exist_count + 1
                    print "pdf exist: %s, now exist count :%d" % (pdf_path, self.pdf_exist_count)
                    continue
                else:
                    print "pdf not exist %s" % pdf_path

                self.request_count = self.request_count + 1
                if self.max_count is not None and self.request_count > int(self.max_count):
                    print "reach max request count: %s" % self.max_count
                    break
                else:
                    print "max count :%s, current count: %s" % (self.max_count, self.request_count)

                try:
                    if self.is_worldbank:
                        download_url = download_url + "?download=true"
                        #time.sleep(random.randint(30,60))
                    download_url = "https://www.sciencedirect.com" + download_url
                    yield Request(download_url, self.download_file, meta = meta, dont_filter=True)
                except Exception as e:
                    raise Exception(e)
                    pass

    def download_file(self, response):
        
        filename = response.meta['filename']
        filename = filename.replace(":", "_")
        #filename = filename.replace("/", "_")
        if self.save_dir != "":
            filename = os.path.join(self.save_dir, filename)

        dirname = os.path.dirname(filename)
        if not os.path.exists(dirname):
            print "make dir: %s" % dirname
            os.makedirs(dirname)

        #是否是pdf文档还真的不太好判断，比如对于wiley的
        if not self._content_is_pdf(response):
            #下载sciencedirect的时候，发现pdf原始网页打开是一个html，这个html包含了cdn分配的pdf地址
            redict_url = response.xpath("//*[@id='redirect-message']//a/@href")
            if len(redict_url) != 0:
                redict_url = redict_url.extract_first()
                meta = {"filename": response.meta['filename']}
                yield Request(redict_url, self.download_file, meta = meta, dont_filter=True)
            return

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
                print "cannot get content from url: %s, source url :%s" %  (response.url, response.request.url)
                return

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
        #print "check if is pdf, print header:"
        #print response.headers
        content_type = response.headers['Content-Type']
        if content_type.find("application/pdf") != -1:
            return True

        #对国研网来说, pdf类型的content type为html,但是header里面附带了这个字段
        if 'Content-Disposition' in response.headers:
            return True

        return False

    def _print_download_status(self):
        print "%s:meta_error_count is :%d, pdf_error_count is :%d, exist_count: %d, pdf_download_count is %d, txt_download_count: %d" \
              % (Utils.current_time(), self.meta_error, self.pdf_error_count, self.pdf_exist_count, self.download_count, self.txt_download_count)

    #国研网有的详情页是需要从网页上下载得到txt文件
    def download_guoyan_content(self, response):
        paras = response.xpath("//*[@id='docContent']//p")
        texts = ""
        for para in paras:
            para_content = " ".join([v.replace("\n", " ") for v in para.xpath(".//text()").extract()]).strip()
            if para_content != "":
                texts += para_content + "\n"

        if len(paras) == 0 or texts == "":
            txt = Utils.get_all_inner_texts(response, "//*[@id='docContent']")
            return txt
        return texts
