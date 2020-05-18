# -*- coding: utf-8 -*-
"""
@date 2020-05-25
@brief 有些pdf文件不能用scrapy直接爬取，需要使用浏览器打开然后自动保存为pdf文件

@note 本文件中的方法亲测在mac下不适用
"""
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
import sys
import os
import random
import json
import shutil

class PDFBrowserDownloader:
    def __init__(self, url_file, save_dir):
        self.url_file = url_file
        self.sava_dir = save_dir

    def download(self):
        exist_count = 0
        download_count = 0
        with open(self.url_file) as f:
            index = 0
            for line in f:
                index = index + 1

                line = line.strip()
                json_data = json.loads(line)

                url = json_data["pdf_url"]
                filename = json_data["pdf_path"]
                if "pdf_save_dir" in json_data:
                    filename = os.path.join(json_data["pdf_save_dir"], filename)

                #不包含pdf结尾的文件
                filepath = os.path.join(self.sava_dir, filename)
                targer_file = filepath + ".pdf"

                if os.path.exists(targer_file):
                    exist_count = exist_count + 1
                    print "%s exits, now exist count is :%d, download count is %d" % (targer_file, exist_count, download_count)
                    continue

                download_count = download_count + 1
                print "%s not exists, start to get %s, now exist count is %d, download count is: %d" % (targer_file, url, exist_count, download_count)

                self._download(url, filepath)

    def _download(self, url, filepath):
        options = webdriver.ChromeOptions()
        if not os.path.exists(filepath):
            os.makedirs(filepath)

        options.add_experimental_option('prefs', {
            "download.default_directory": filepath,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "plugins.always_open_pdf_externally": True
        })
        self.driver = webdriver.Chrome(
            executable_path='C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe', chrome_options=options)
        self.driver.get(url)
        pdf_download_success = False
        while(not pdf_download_success):
            print "downloading...check"
            files = os.listdir(filepath)
            for file in files:
                if os.path.splitext(file)[1] == ".pdf":
                    pdf_download_success = True
                    break;
            time.sleep(1)

        print "download %s success" % filepath
        self.driver.close()

        #下载完以后，把文件move
        files = os.listdir(filepath)
        for file in files:
            if os.path.splitext(file)[1] == ".pdf":
                oldfile = os.path.join(filepath, file)
                newfile = filepath + ".pdf"
                print "download finish, move temp file %s to target file %s" % (oldfile, newfile)
                shutil.move(oldfile, newfile)
                shutil.rmtree(filepath)

if __name__ == "__main__":
    url_file = sys.argv[1]
    save_dir = sys.argv[2]
    browser_dowenload = PDFBrowserDownloader(url_file, save_dir)
    browser_dowenload.download()
