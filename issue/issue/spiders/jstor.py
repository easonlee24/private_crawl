# -*- coding: utf-8 -*-
import scrapy
import urlparse
import json
from scrapy.http.request import Request
from utils import  Utils
from urllib import quote

class JstorSpider(scrapy.Spider):
    name = 'jstor'

    """
    有两种工作模式：
    1、指定了url_file，表示爬取详情页元数据
    2、没有制定url_file，表示爬取详情页url.

    两种模式设置了meta_file文件，都能用来去重
    """
    def __init__(self, meta_file = None, url_file = None, revised = None):
        self.meta_file = meta_file
        self.crawled_url = []
        self.url_file = url_file
        if self.meta_file:
            with open(self.meta_file) as f:
                for line in f:
                    json_data = json.loads(line)
                    if "origin_url" in json_data:
                        self.crawled_url.append(json_data["origin_url"])
                    #elif "search_url" in json_data:
                    #    self.crawled_url.append(json_data["search_url"])

        if revised == 'True':
            self.revised = True
        else:
            self.revised = False

    def start_requests(self):
        #meta = {"search_url" : "search_url"}
        ##书籍
        #yield Request("http://www.jstor.org/stable/10.7249/mg358cf.10?seq=1#page_scan_tab_contents", self.parse_issue, meta = meta, dont_filter = True)
        ##期刊
        ##yield Request("http://www.jstor.org/stable/40279148?Search=yes&resultItemClick=true&searchText=agriculture&searchText=OR&searchText=agricultural&searchText=OR&searchText=rural&searchUri=%2Faction%2FdoBasicSearch%3Fgroup%3Dnone%26amp%3Bsd%3D2009%252F03%26amp%3BsearchType%3DfacetSearch%26amp%3BQuery%3Dagriculture%2BOR%2Bagricultural%2BOR%2Brural%26amp%3Bpage%3D6%26amp%3Bfc%3Doff%26amp%3Bed%3D2009%252F04%26amp%3Bacc%3Don%26amp%3Bwc%3Don&seq=1#page_scan_tab_contents", self.parse_issue, meta = meta, dont_filter = True)
        #return
        meta = {"origin_url": "origin_url"}
        yield Request("https://www.jstor.org/stable/26270352", self.parse_issue, meta = meta, dont_filter = True)
        return
        if self.url_file:
            #指定了爬取哪些url
            with open(self.url_file) as f:
                for line in f:
                    json_data = json.loads(line)
                    if "stable_url" in json_data:
                        url = json_data["stable_url"]
                        if url in self.crawled_url:
                            print "filter url: %s" % url
                        else:
                            meta = {"origin_url" : json_data["url"]}
                            yield Request(json_data["url"], self.parse_issue, meta = meta, dont_filter = True)
                        #return
            return

        i = 0
        final_page = 250 #11.25, total result is 25028
        #final_page = 1

        start_year = 2005
        end_yrar = 2017
        start_month = 1
        end_month = 12
        current_year = start_year
        while (current_year <= end_yrar):
            current_month = start_month
            while (current_month < end_month):
                start_date = str(current_year) + "%2F" + "%02d" % current_month
                end_date = str(current_year) + "%2F" + "%02d" % (current_month + 1)
                start_url = "http://www.jstor.org/action/doBasicSearch?searchType=facetSearch&page=1&sd=%s&ed=%s&wc=on&acc=on&fc=off&Query=agriculture+OR+agricultural+OR+rural&group=none" % (start_date, end_date)
                if start_url in self.crawled_url:
                    print "start_url crawled, filter: %s" % start_url
                else:
                    meta = {"page" : 1, "current_year": current_year, "current_month": current_month}
                    yield Request(start_url, self.parse_result_of_date, meta = meta, dont_filter = True)
                current_month = current_month + 1
            current_year = current_year + 1

    def parse_issue(self, response):
        print "parse issue..."
        print response.xpath("//li[@class='breadcrumb-issue']")
        title = Utils.extract_text_with_xpath(response, "//h1[contains(@class,'title') and contains(@class,'medium-heading')]")
        if title == "":
            #书籍类型
            title = Utils.extract_text_with_xpath(response, "//h1[@class='medium-heading']/span[@class='title']")
        book_title = Utils.extract_text_with_xpath(response, "//div[@class='book-title']/a")

        meta_type = Utils.extract_text_with_xpath(response, "//div[@data-qa='content-type']")
        journal = Utils.extract_text_with_xpath(response, "//div[@class='journal']/cite")
        infos = Utils.extract_text_with_xpath(response, "//div[@class='src mbl']")
        volume = Utils.regex_extract(infos, "Vol\. (\d+)")
        issue = Utils.regex_extract(infos, "No\. (\w+)")
        publish_date = Utils.regex_extract(infos, "No\..*\((.*)\)")

        if publish_date == "":
            publish_date = Utils.extract_text_with_xpath(response, "//div[@class='published_date']")

        page_range = Utils.extract_text_with_xpath(response, "//div[@class='page-range']")
        if page_range == "":
            page_range = infos

        start_page = Utils.regex_extract(page_range, "pp\. (\d+)-")
        end_page = Utils.regex_extract(page_range, "pp\. \d+-(\d+)")
        page_count = Utils.extract_text_with_xpath(response, "//div[@class='count']")
        page_count = page_count.replace("Page Count: ", "")

        publisher = Utils.extract_text_with_xpath(response, "//a[@class='publisher-link']/")

        stable_url = Utils.extract_text_with_xpath(response, "//div[@class='stable']")
        stable_url = Utils.regex_extract(stable_url, "Stable URL: (.*)$" )
        stable_id = Utils.regex_extract(stable_url, "stable/(.*)$")
        pdf_url = "http://www.jstor.org/stable/pdf/%s.pdf" % stable_id

        keywords = Utils.extract_all_text_with_xpath(response, "//div[@class='topics-list mtl']/a", join_str = ",")

        doi = Utils.extract_text_with_xpath(response, "//div[@class='doi']").replace("DOY:", "").strip()

        yield {
            "url" : response.url,
            "stable_url" : stable_url,
            "origin_url" : response.meta["origin_url"],
            "journal" : journal,
            "title" : title,
            "book_title" : book_title,
            "volume" : volume,
            "issue" : issue,
            "release_date" : publish_date,
            "start_page" : start_page,
            "end_page" : end_page,
            "page_count" : page_count,
            "keywords" : keywords,
            "pdf_url" : pdf_url,
            "meta_type" : meta_type,
            "publisher" : publisher,
            "doi": doi
        }

    def parse_result_of_date(self, response):
        total_count = Utils.get_all_inner_texts(response, "//*[@id='search-container']/div/div[2]/div[1]/div[1]/h2").split()[-1].replace(",", "")
        if int(total_count) > 1000:
            yield {
                "type": "error",
                "reson": "count is %s, url is: %s" % (total_count, response.url)
            }
            #return

        for article in response.xpath("//*[@id='searchFormTools']/ol//li[contains(@class, 'row result-item')]"):
            type = article.xpath(".//div[@class='badge']/text()").extract_first().strip()
            article_url = article.xpath(".//div[@class='title']//a/@href").extract_first()
            article_url = urlparse.urljoin(response.url, article_url)
            title = article.xpath(".//div[@class='title']//a/text()").extract_first().strip()
            yield {
                "type" : type,
                "url" : article_url,
                "title": title,
                "current_year": response.meta["current_year"],
                "current_month": response.meta["current_month"],
                "search_url": response.url,
                "page": response.meta['page'],
            }

        if response.meta["page"] == 1:
            #this is start page
            total_page = int(total_count) / 25 + 1
            current_year = response.meta["current_year"]
            current_month = response.meta["current_month"]
            next_page = 2
            while (next_page <= total_page):
                start_date = str(current_year) + "%2F" + "%02d" % current_month
                end_date = str(current_year) + "%2F" + "%02d" % (current_month + 1)
                next_url = "http://www.jstor.org/action/doBasicSearch?searchType=facetSearch&page=%d&sd=%s&ed=%s&wc=on&acc=on&fc=off&Query=agriculture+OR+agricultural+OR+rural&group=none" % (next_page, start_date, end_date)
                meta = {"page" : next_page, "current_year": current_year, "current_month": current_month}
                yield Request(next_url, self.parse_result_of_date, meta = meta, dont_filter = True)
                next_page = next_page + 1
