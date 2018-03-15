#!/usr/bin/env python
#-*- coding: utf-8 -*-.
import scrapy
import re
import sys
import urlparse
from scrapy.http.request import Request
reload(sys)
sys.setdefaultencoding('utf8')

class HipatiaEnhancedSpider(scrapy.Spider):
        name = "hipatia_enhanced"
        urls = []
        selected_years = [2015 ,2016, 2017]

        def __init__(self,url_file=None,*args,**kwargs):
                super(HipatiaEnhancedSpider,self).__init__(*args,**kwargs)
                self.urls = self.readText(url_file)
                print self.urls

        def readText(self,path):
                print "path is %s" % path
                f = file(path,'r')
                line = f.readline().strip()
                result = []
                while len(line) > 0:
                        result.append(line.strip())
                        line = f.readline().strip()
                f.close()
                return result

        def start_requests(self):
                urls = self.urls
                for url in urls:
                        yield Request(url,self.parse)

        def parse(self,response):
                for item in response.xpath('.//h3/..'):
                        item_year = item.xpath('.//h3/text()').extract()
                        item_year = int(item_year[0])
                        print "item_year :%d" % item_year
                        #meta1 = {}
                        if item_year in self.selected_years:
                                #meta1['release_year'] = item_year
                                #meta1['volumne'] = item.xpath('.//h4/a/text()').extract_first()
                                urls = item.xpath('.//h4/a/@href').extract()
                                for url in urls:
                                        if url is not None :
                                                meta1 = {}
                                                meta1['release_year'] = item_year
                                                meta1['volumne'] = item.xpath('.//h4/a/text()').extract_first()
                                                print meta1
                                                yield response.follow(url,self.parseInnerPage,meta = meta1)
                                                break

        def parseInnerPage(self,response):
                print "meta in parseInnerPage"
                print response.meta
                for article in response.xpath('//table[@class="tocArticle"]'):
                        meta2 = {}
                        meta2['release_year'] = response.meta['release_year']
                        meta2['volumne'] = response.meta['volumne']
                        meta2["authors"] = article.xpath('.//div[@class="tocAuthors"]/text()').extract_first().strip().replace("\t","")
                        meta2["pages"] = article.xpath('.//div[@class="tocPages"]/text()').extract_first().strip()
                        meta2["pdf_url"] = article.xpath('.//div[@class="tocGalleys"]/a/@href').extract_first().replace("view","download")
                        meta2['subtitle'] = article.xpath('//div[@class="tocTitle"]/a/text()').extract_first()
                        url = article.xpath('.//div[@class="tocTitle"]/a/@href').extract_first()
                        print "meta2"
                        print meta2
                        sys.exit(0)
                        #print "================> %s" % url,
                        yield response.follow(url[0],self.parseDetailPage,meta = meta2)

        def parseDetailPage(self,response):
                print "response.meta"
                print response.meta
                volumne_issue_str = response.meta["volumne"][0],
                volumne_group = re.search("Vol(.+),",volumne_issue_str),
                if volumne_group :
                        volumne_str = volumne_group.group(1)
                issue_group = re.search(".*No(.*)\(.*",volumne_issue_str),
                if issue_group :
                        issue_str = issue_group.group(1)
                yield  {
                        "release_year" : response.meta["release_year"][0],
                        "volumne" :volumne_str,
                        "issue" : issue_str,
                        "authors" : response.meta["authors"][0],
                        "pages" : response.meta["pages"][0],
                        "pdf_url" : response.meta["pdf_url"][0],
                        "subtitle" : response.meta["subtitle"][0],  
                        "abstract" : response.xpath('.//p/text()').extract_first(),
                    "doi" : response.xpath('.//a[@id="pub-id::doi"]/text()').extract_first(),
                }

        def extract_with_xpath(self,root,xpath_str,default_value = ""):
                try:
                        result = root.xpath(xpath_str).extract_first().strip()
                except Exception as e:
                        result = default_value
                
                return result

        def encode(self,value):
                if value is not None:
                        return value.encode('utf-8')
                return value
                
