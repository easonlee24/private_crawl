# -*- coding: utf-8 -*-
"""
@date 2020-05-25
@brief 提供了一种示例, 使用cookies打开需要登录的网址，在爬取imf网站时编写

1) 调用cookies函数，输入账号，密码，保存cookies放入cookies_data文件
2) 调用download函数，爬取元数据

"""
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from utils import Utils
import time
import sys
import os
import random
import json

class PDFBrowserDownloader:
    """
    @param output_meta_file 输出元数据的文件路径,追加写.输出格式为json:{"pdf_url", "pdf_path", "pdf_save_dir"}
    """
    def __init__(self, output_meta_file):
        self.output_meta_file = output_meta_file

        options = webdriver.ChromeOptions()
        profile = {"plugins.plugins_list": [{"enabled": False, "name": "Chrome PDF Viewer"}],
                   "download.default_directory": ".",
                   "download.extensions_to_open": ""}
        options.add_experimental_option("prefs", profile)
        self.driver = webdriver.Chrome(chrome_options=options)
        self.wait = WebDriverWait(self.driver, 15)

    # 打开浏览器，输入密码保存cookies
    def cookies(self):
        self.driver.get("https://animalpharm.agribusinessintelligence.informa.com/")
        time.sleep(60)
        print "get and save cookies"
        cookies = self.driver.get_cookies()
    	jsoncookies = json.dumps(cookies)
        with open('cookies_data','w') as f:
		    f.write(jsoncookies)
        print "cookies saver"

    def download(self):
        self._download_url("https://animalpharm.agribusinessintelligence.informa.com/pdf-library", "animalpharm");
        self._download_url("https://iegpolicy.agribusinessintelligence.informa.com/ieg-policy-weekly-briefing", "iegpolicy");
        self._download_url("https://iegvu.agribusinessintelligence.informa.com/ieg-vu-weekly-briefing", "iegvu");

    def _download_url(self, url, journal):
        self.driver.delete_all_cookies()
    	with open('cookies_data' ,'r') as f:
            listcookies = json.loads(f.read())

        self.driver.get(url)
        for cookie in listcookies:
            try:
                self.driver.add_cookie(cookie)
            except Exception as e:
                continue
		
        self.driver.get(url)
        elems = self.driver.find_elements_by_xpath("//*[@class='pdfs-section']//tr")
        print "len is: %d" % len(elems)
        index = 0

        output_meta_file_writer = open(self.output_meta_file, "a+")
        for elem in elems:
            if index == 0:
                #过滤标题
                index += 1
                continue;

            index += 1

            tds = elem.find_elements_by_xpath(".//td")
            date = tds[0].text.split();

            pdf_path = "%s-%s-%s" % (date[2], date[1], date[0]);
            pdf_url = tds[2].find_element_by_tag_name("a").get_attribute("href");

            meta = {"pdf_url": pdf_url, "pdf_path": pdf_path, "pdf_save_dir": journal};

            print "pdf_url: %s, pdf_path: %s, pdf_save_dir: %s" % (pdf_url, pdf_path, journal)
            output_meta_file_writer.write(json.dumps(meta))
            output_meta_file_writer.write("\n");

        output_meta_file_writer.close();

if __name__ == "__main__":
    output_meta_file = sys.argv[1]
    browser_dowenload = PDFBrowserDownloader(output_meta_file)
    #browser_dowenload.cookies()
    browser_dowenload.download()
