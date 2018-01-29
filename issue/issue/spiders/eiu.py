#!/usr/bin/env python
# -*- coding: utf-8 -*- 
import scrapy
import re
import sys
import urlparse
import sys
reload(sys)
sys.setdefaultencoding('utf8')

class EIUSpider(scrapy.Spider):
    name = "eiu"

    start_urls = ['http://www.eiu.com/index.asp?layout=displayPublication&publication_type_id=480000248&eiu_publication_id=2000002400']

    def __init__(self, country_file=None, *args, **kwargs):
        super(EIUSpider, self).__init__(*args, **kwargs)
        self.countrys = []
        for line in open(country_file):
            countrys = line.strip().lower().split("|")
            for country in countrys:
                country = country.strip()
                self.countrys.append(country)

        self.download_dir = "eiu_pdfs"
        print self.countrys

    def parse(self, response):
        countrys = response.xpath("//div[@class='PageTitleGray']/following-sibling::table[1]//td")
        for country in countrys:
            country_name = country.xpath("./a/text()").extract_first()
            if country_name is None:
                continue
            country_name = country_name.strip().lower()
            if country_name not in self.countrys:
                continue
            url = country.xpath("./a/@href").extract_first()
            url = urlparse.urljoin(response.url, url)

            meta = {'country': country_name} 

            yield response.follow(url, self.parse_pdf_links, meta = meta)

    def parse_pdf_links(self, response):
        links = response.xpath("//div[@class='PageTitleGray']//following-sibling::table[1]//tr[@valign='top']")
        for link in links:
            pdf_link = link.xpath(".//a[2]/@href").extract_first()
            pdf_link = urlparse.urljoin(response.url, pdf_link)
            date = link.xpath("./td[2]/text()").extract_first().split()[0]

            meta = response.meta
            meta['date'] = date

            yield response.follow(pdf_link, self.download_pdf, meta = meta)

    def download_pdf(self, response):
        path = "%s/%s_%s.pdf" % (self.download_dir, response.meta['country'], response.meta['date']) 

        with open(path, "wb") as f:
            f.write(response.body)

        f.close()
