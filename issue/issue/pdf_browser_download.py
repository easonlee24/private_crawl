# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
import sys
import os
import random

class PDFBrowserDownloader:
    def __init__(self, url_file, save_dir):
        self.url_file = url_file
        self.sava_dir = save_dir
        options = webdriver.ChromeOptions()
        profile = {"plugins.plugins_list": [{"enabled": False, "name": "Chrome PDF Viewer"}],
                   "download.default_directory": self.sava_dir,
                   "download.extensions_to_open": ""}
        options.add_experimental_option("prefs", profile)
        self.driver = webdriver.Chrome(
            executable_path='C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe', chrome_options=options)
        self.wait = WebDriverWait(self.driver, 15)

    def download(self):
        exist_count = 0
        download_count = 0
        with open(self.url_file) as f:
            for line in f:
                line = line.strip()
                url = line.replace("full", "pdf")

                filename = url.split("/")[-1]
                filepath = self.sava_dir + "\\" + filename + ".pdf"
                if os.path.exists(filepath):
                    exist_count = exist_count + 1
                    print "%s exits, now exist count is :%d, download count is %d" % (filepath, exist_count, download_count)
                    continue

                download_count = download_count + 1
                print "%s not exists, start to get %s, now exist count is %d, download count is: %d" % (filepath, url, exist_count, download_count)

                url = url + "?download=true"
                self.driver.get(url)
                time.sleep(random.randint(30, 60))

                #working with shadow root: https://stackoverflow.com/questions/28911799/accessing-elements-in-the-shadow-dom
                #self.wait.until(EC.visibility_of_element_located((By.XPATH, "//*[@id='toolbar'']")))
                #time.sleep(10)

                ##root1 = self.driver.find_element_by_xpath("//*[@id='toolbar']")
                #root1 = self.driver.find_element_by_id("toolbar")
                #shadow_root1 = self._expand_shadow_element(root1)
                #shadow_root1.find_element_by_xpath("//*[@id='download']").click()

                #root2 = self.driver.find_element_by_xpath((By.XPATH, "//*[@id='download']"))

    def _wait_and_click(self, xpath):
        self.wait.until(EC.visibility_of_element_located((By.XPATH, xpath)))
        try:
            self.driver.find_element_by_xpath(xpath).click()
        except Exception as e:
            time.sleep(5)
            self.driver.find_element_by_xpath(xpath).click()

    def _expand_shadow_element(self, element):
        shadow_root = driver.execute_script('return arguments[0].shadowRoot', element)
        return shadow_root



if __name__ == "__main__":
    url_file = sys.argv[1]
    save_dir = sys.argv[2]
    browser_dowenload = PDFBrowserDownloader(url_file, save_dir)
    browser_dowenload.download()