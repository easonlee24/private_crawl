# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
import sys
import os
import random
import json
import requests
import time

class PDFBrowserDownloader:
    def __init__(self, url_file, save_dir):
        self.url_file = url_file
        self.sava_dir = save_dir
        options = webdriver.ChromeOptions()
        appState = {
            "recentDestinations": [
                {
                    "id": "Save as PDF",
                    "origin": "local"
                }
            ],
            "selectedDestinationId": "Save as PDF",
            "version": 2
        }
        options.add_experimental_option('prefs', {
            "download.default_directory": self.sava_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "plugins.always_open_pdf_externally": True
        }
                                               )
        self.driver = webdriver.Chrome(
            executable_path='C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe', chrome_options=options)
        self.wait = WebDriverWait(self.driver, 15)



    def download(self):
        exist_count = 0
        download_count = 0
        with open(self.url_file, 'rb') as fp:
            for line in fp:
                json_date = json.loads(line)
                pdf_url = json_date['pdf_url']
                if pdf_url.__contains__(".pdf"):
                    filename = pdf_url.split("/")[-2]
                    filepath = self.sava_dir + "\\" + filename
                    if os.path.exists(filepath):
                        exist_count = exist_count + 1
                        print "%s exits, now exist count is :%d, download count is %d" % (
                            filepath, exist_count, download_count)
                        continue
                    if filename.__contains__('WS-D-'):
                        continue
                    if filename.__contains__('WT-D-'):
                        continue
                    download_count = download_count + 1
                    print "%s not exists, start to get %s, now exist count is %d, download count is: %d" % (
                        filepath, pdf_url, exist_count, download_count)
                    #pdf_url = pdf_url + "?download=true"
                    self.driver.get(pdf_url)
                    time.sleep(20)
                    used_name = self.sava_dir + "\\" + pdf_url.split("/")[-1]
                    os.rename(used_name, filepath)
                    #self.driver.execute_script('window.print();')
                    # self.driver.find_element_by_id('icon').click()
                    #self.downloadPDF(pdf_url,filepath)
                    #time.sleep(random.randint(30, 60))
                else:
                    print str(pdf_url) + " is wrong !!!"

    def _wait_and_click(self, xpath):
        self.wait.until(EC.visibility_of_element_located((By.XPATH, xpath)))
        try:
            self.driver.find_element_by_xpath(xpath).click()
        except Exception as e:
            time.sleep(5)
            self.driver.find_element_by_xpath(xpath).click()

    def _expand_shadow_element(self, element):
        shadow_root = self.driver.execute_script('return arguments[0].shadowRoot', element)
        return shadow_root

    def downloadPDF(self, pdf_url, filePath):
        print "start to download %s" % pdf_url
        r = requests.get(pdf_url, stream=True)

        if os.path.exists(filePath):
            print "%s exits" % pdf_url
        else:
            with open(filePath, "wb") as pdf:
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk:
                        pdf.write(chunk)
            print filePath + " successful!!!"
            time.sleep(random.randint(10, 30))


if __name__ == "__main__":
    url_file="D:\chenlu\eonly\cup_eonly_2019_ok.jl"
    save_dir ="D:\chenlu\eonly\cup1"
    browser_dowenload = PDFBrowserDownloader(url_file, save_dir)
    browser_dowenload.download()
