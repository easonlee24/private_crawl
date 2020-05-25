# -*- coding: utf-8 -*-
import scrapy
import urlparse
from utils import Utils
from scrapy.http.request import Request
import re
import json

"""
20200510更新
得到oecd期刊的url
"""
class OecdUrlSpider(scrapy.Spider):
    name = 'oecd_url'
    def __init__(self, start_year):
        self.start_year = start_year
        

    def start_requests(self):
        urls = [
            #"https://www.oecd-ilibrary.org/books/english?sortField=prism_publicationDate&sortDescending=true&pageSize=800",
            #"https://www.oecd-ilibrary.org/papers/english?sortField=prism_publicationDate&sortDescending=true&pageSize=800",
            "https://www.oecd-ilibrary.org/books/chinese?sortField=prism_publicationDate&sortDescending=true&pageSize=20"

        ]
        for url in urls:
            yield Request(url, self.process)

    def process(self, response):
        items = response.xpath("//div[@id='listItems']//div[@class='resultItem table-row']")
        for item in items:
            url = urlparse.urljoin(response.url, item.xpath(".//h5[@class='search_title']/a/@href").extract_first())
            year = item.xpath(".//ul[@class='search-metaitem comma_separated']/li").extract_first().split()[3]
            if year < self.start_year:
                break;
            yield {
                "url" : url
            }
            
