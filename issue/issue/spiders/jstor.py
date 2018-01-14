# -*- coding: utf-8 -*-
import scrapy
import urlparse
from scrapy.http.request import Request
from utils import  Utils
from urllib import quote

class JstorSpider(scrapy.Spider):
    name = 'jstor'
    allowed_domains = ['http://www.emeraldinsight.com/']
    start_urls = ['http://http://www.emeraldinsight.com//']

    def start_requests(self):
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
                meta = {"page" : 1, "current_year": current_year, "current_month": current_month}
                yield Request(start_url, self.parse_result_of_date, meta = meta, dont_filter = True)
                current_month = current_month + 1
            current_year = current_year + 1

    def parse_result_of_date(self, response):
        total_count = Utils.get_all_inner_texts(response, "//*[@id='search-container']/div/div[2]/div[1]/div[1]/h2").split()[-1].replace(",", "")
        if int(total_count) > 1000:
            yield {
                "type": "error",
                "reson": "count is %s, url is: %s" % (total_count, response.url)
            }
            return

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
