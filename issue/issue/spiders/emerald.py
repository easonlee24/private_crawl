# -*- coding: utf-8 -*-
import scrapy
import urlparse
from scrapy.http.request import Request


class EmeraldSpider(scrapy.Spider):
    name = 'emerald'
    allowed_domains = ['http://www.emeraldinsight.com/']
    start_urls = ['http://http://www.emeraldinsight.com//']

    def start_requests(self):
        i = 0
        final_page = 251 #1.14, total result is 25105
        #final_page = 1
        
        while i <= final_page:
            start_url = "http://www.emeraldinsight.com/action/doSearch?backfile=on&content=articlesChapters&dateRange=%5B20050101+TO+20171231%5D&earlycite=on&field1=AllField&field2=AllField&field3=AllField&logicalOpe1=OR&logicalOpe2=OR&target=default&text1=agriculture&text2=agricultural&text3=rural&pageSize=100&startPage=" + str(i)
            yield Request(start_url, self.parse, dont_filter = True)
            i = i + 1

    def parse(self, response):
        titles = response.xpath("//*[@id='searchResultItems']/li")
        for title in titles:
            url = title.xpath(".//span[@class='art_title']//a/@href").extract_first()
            url = urlparse.urljoin(response.url, url)
            pdf_link = title.xpath(".//a[@class='ref nowrap pdfplus']/@href").extract_first()
            pdf_link = urlparse.urljoin(response.url, pdf_link)
            yield {
                'url' : url,
                'pdf_link' : pdf_link,
                'search_url': response.url
            }
