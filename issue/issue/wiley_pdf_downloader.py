"""
Usage:
    python pdf_download.py links_file_path
"""
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchFrameException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys
import time
import json
from selenium.webdriver.chrome.options import Options
import os
from concurrent.futures import ThreadPoolExecutor
import traceback


filename = sys.argv[1]
start_count = int(sys.argv[2])

base_dir = "D:\chenlu\oa_2019\wiley_pdf"

def close(driver):
    try:
        driver.close()
    except Exception as e:
        print "close windows catch exception: %s" % traceback.format_exc()

def download_file(index, link, filename):
    print "start to download %dth pdf: %s, time: %s" % (index, link, time.asctime(time.localtime(time.time())))
    success = False
    try:
        download_dir = base_dir + "\\" + str(filename)
        print "download_dir %s" % download_dir
        if not os.path.exists(download_dir):
            os.makedirs(download_dir)
        else:
            files = os.listdir(download_dir)
            if len(files) >= 1:
                print "%s exist, pass" % filename
                return True

        chromeOptions = webdriver.ChromeOptions()
        prefs = {"download.default_directory": download_dir}
        chromeOptions.add_experimental_option("prefs", prefs)
        #chromeOptions.add_argument("download.default_directory=%s" % download_dir)
        driver = webdriver.Chrome(executable_path='C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe', chrome_options=chromeOptions)
        driver.set_page_load_timeout(10)
        try:
            driver.get(link)
            print "load success"
        except TimeoutException:
            print "load timeout, continue download"
            driver.execute_script("window.stop()")

        wait = WebDriverWait(driver, 30)
        print "wait iframe"
        wait.until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, "//iframe[@class='rc-reader-frame']")))

        print "wait download button"
        wait = WebDriverWait(driver, 30)
        wait.until(EC.presence_of_element_located((By.XPATH, "//menu-button[@class='download']")))
        #wait.until(EC.presence_of_element_located((By.XPATH, "//div[@class='menu-btn download sticky']")))

    except Exception as e:
        print "download pdf %s fail, reson: %s" % (link, traceback.format_exc())
        close(driver)
        return False

    need_retry = True
    current_retry = 0
    max_retry = 1
    while need_retry and current_retry < max_retry:
        need_retry = False
        try:
            current_retry += 1
            time.sleep(1)
            driver.find_element_by_xpath("//menu-button[@class='download']").click()
            time.sleep(5)
            print "download success"
            close(driver)
            return True
        except Exception as e:
            need_retry = True
            print "click catch exception : %s" % traceback.format_exc()
            close(driver)
            return False

with open(filename) as fp:
    index = 0
    pool = ThreadPoolExecutor(max_workers=2)
    index = 0
    for line in fp:
        index = index + 1
        if index <= start_count:
            continue

        try:
            json_data = json.loads(line)
            #filename = json_data.get("doi", "unkown").replace("/", "_")
            link = json_data.get("download_path", "unkown")
        except Exception as e:
            try:
                link = line.split("|")[1].strip()
            except Exception as e:
                link = line.strip()

        if link.find("pdf") == -1:
            print "illegal pdf link: %s" % link
            continue
        filename = "_".join(link.split('/')[-1:]) + ".pdf"
        retry = 1
        isContinue = True
        while( isContinue and retry <=3):
            isContinue = not download_file(index, link, filename)
            retry = retry +1
