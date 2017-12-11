# -*- coding: utf-8 -*-
import scrapy
import urlparse
from scrapy.http.request import Request


class SageSpider(scrapy.Spider):
    name = 'sage'
    allowed_domains = ['http://journals.sagepub.com/']
    start_urls = ['http://http://journals.sagepub.com//']

    def start_requests(self):
        i = 0
        final_page = 111
        #final_page = 1
        
        while i <= final_page:
            start_url = "http://journals.sagepub.com/action/doSearch?field1=Abstract&text1=agriculture+OR+agricultural+OR+rural&field2=AllField&text2=&Ppub=&AfterYear=2005&BeforeYear=2018&earlycite=on&access=&ContentItemType=research-article&pageSize=100&startPage=%d" % i
            yield Request(start_url, self.parse, dont_filter = True)
            i = i + 1

    def parse(self, response):
        titles = response.xpath("//*[@id='frmSearchResults']/ol/li")
        for title in titles:
            url = title.xpath(".//div[@class='art_title  hlFld-Title']/a/@href").extract_first()
            url = urlparse.urljoin(response.url, url)
            pdf_link = title.xpath(".//a[@class='ref nowrap full']/@href").extract_first()
            pdf_link = urlparse.urljoin(response.url, url)
            yield {
                'url' : url,
                'pdf_link' : pdf_link,
                'search_url': response.url
            }
