#!/usr/bin/env python
# -*- coding: utf-8 -*-
import scrapy
import re
import sys
import urlparse
import sys
from scrapy.http.request import Request

reload(sys)
sys.setdefaultencoding('utf8')


class ConferenceSpider(scrapy.Spider):
    name = "conference"

    def __init__(self, conference_file=None, *args, **kwargs):
        super(ConferenceSpider, self).__init__(*args, **kwargs)
        self.conferences = set(line.strip().lower() for line in open(conference_file))


    def start_requests(self):
        #meta = {'totalCount': 10, 'searchUrl': 'searchUrl'}
        #yield Request("http://www.oc.ac.cn/SubjectDisplay?subject=%E7%94%9F%E7%89%A9%E7%A7%91%E5%AD%A6&currentpage=1&pagenumber=59&pagetype=jump", self.parse_search_result,meta= meta)
        #yield Request("http://www.oc.ac.cn/ConferenceDetail?id=17165", self.parse_conference, meta = meta)
        for conference in self.conferences:
            url = "http://www.oc.ac.cn/SubjectDisplay?currentpage=0&pagetype=init&subject=%s" % conference
            meta = {'conference' : conference}
            yield Request(url, self.parse, meta = meta)

    def parse(self, response):
        totalCount = self.extract_with_xpath(response,"//form[@name='jumpSubject']/table//table//td[2]/text()")
        totalCount = int(totalCount.replace("Display.Totalcount", "").replace("Display.Item", ""))
        pageCount = totalCount/10 + 1

        meta = {}
        meta['conference'] = response.meta['conference']
        meta['totalCount'] = totalCount

        for page in range(1, pageCount + 1):
            content_url = "http://www.oc.ac.cn/SubjectDisplay?subject=%s&currentpage=1&pagenumber=%d&pagetype=jump" % (response.meta['conference'], page)
            yield response.follow(content_url, self.parse_search_result, meta = meta)


    def parse_search_result(self, response):
        conference_links = response.xpath("//table[@width='712']//span[@class='hei2']/a/@href").extract()
        print conference_links
        for link in conference_links:
            conference_link = urlparse.urljoin(response.url, link).strip()

            meta = {}
            meta['conference'] = response.meta['conference']
            meta['totalCount'] = response.meta['totalCount']
            meta['searchUrl'] = response.url

            yield response.follow(conference_link, self.parse_conference, meta= meta)

    def parse_conference(self, response):
        title = self.extract_with_xpath(response, "//table[@height='98%']//span[@class='red2']//text()")

        #some span may not have text content,in this mark it as 'none'
        original_infos = response.xpath("//table[@height='98%']//span[@class='en-hei2']")
        infos = []
        for info in original_infos:
            text = self.extract_with_xpath(info, "./text()", "none")
            if text == "none":
                text = self.extract_with_xpath(info, "./a/text()", "none")
            infos.append(text)
            
        infos.insert(0, title)
        keys = response.xpath("//table[@height='98%']//td[@class='red2']//text()").extract()
        #infos = [x.strip() for x in infos if x.strip() != ""]
        #keys  = [x.strip() for x in keys if x.strip() != ""]
        
        if len(keys) != len(infos):
            print infos
            print keys
            raise Exception("unexpected keys and infos lens")

        print response.meta

        item = {}
        item['conference_url'] = response.url
        item['conference'] = response.meta['conference']
        item['searchUrl'] = response.meta['searchUrl']
        item['totalCount'] = response.meta['totalCount']

        for index, key in enumerate(keys):
            item[key] = infos[index]

        yield item
        

    def extract_with_xpath(self, root, xpath_str, default_value = ""):
        try:
            result = root.xpath(xpath_str).extract_first().strip()
        except Exception as e:
            result = default_value

        return result
   

