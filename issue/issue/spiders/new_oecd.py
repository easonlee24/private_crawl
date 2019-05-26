#!/usr/bin/env python
# -*- coding: utf-8 -*- 
# Description: 20190408: oecd的网站又发生了改版，且需求也有一定的变化。新需求是新增的需求，检索出来了380条内容，主要是Books和Statistics。本程序输入检索出来的url，爬取urol
# Usage: scrapy crawl new_oecd -a url_file=xxx
import scrapy
import re
import sys
import urlparse
import sys
import datetime
from utils import Utils
reload(sys)
sys.setdefaultencoding('utf8')
from scrapy.http.request import Request

class NewOECDSpider(scrapy.Spider):
    name = "new_oecd"

    def __init__(self, url_file=None, *args, **kwargs):
        super(NewOECDSpider, self).__init__(*args, **kwargs)
        self.url_file = url_file

    def start_requests(self):
        with open(self.url_file, "rb") as f:
            for line in f:
                yield Request(line.strip(), self.parse, dont_filter=True)

    def parse(self, response):
        type = response.xpath(".//ol[@class='breadcrumb']/li[2]/a/text()").extract_first().strip()
        if type == "Statistics":
            return self.process(response, "Statistics")
        elif  type == "Books":
            return self.process(response, "Books")
        else:
            raise Exception("unexcepted type: %s" % type)

    #def process_statistics(self, response):
    #    latest = response.xpath(".//div[@class='row section-title']")
    #    edition_type = latest.xpath(".//p[@class='edition-type']/text()").extract_first().strip()
    #    if edition_type not in  ('Latest Edition', 'Latest Issue'):
    #        raise Exception("unexcepted edition type: %s" % edition_type)

    #    title = latest.xpath(".//h2/text()").extract_first()
    #    description = Utils.get_all_inner_texts(latest, ".//div[@class='description js-fulldescription']")
    #    pdf_link = urlparse.urljoin(response.url, latest.xpath(".//a[@class='action-pdf enabled']/@href").extract_first())

    #    meta_section = response.xpath(".//div[@class='block-infos-sidebar date-daily col-xs-12']")
    #    author = Utils.get_all_inner_texts(meta_section, "./p[1]")
    #    release_date = Utils.format_datetime(Utils.get_all_inner_texts(meta_section, "./p[2]"))
    #    pages = Utils.get_all_inner_texts(meta_section, "./p[3]")
    #    isbn = Utils.get_all_inner_texts(meta_section, "./p[5]")
    #    doi = Utils.get_all_inner_texts(meta_section, "./a")
    #    yield {
    #        "url": response.url,
    #        "title": title,
    #        "abstract": description,
    #        "pdf_link": pdf_link,
    #        "author": author,
    #        "release_date": release_date,
    #        "pages": pages,
    #        "isbn": isbn,
    #        "doi": doi,
    #        "type": "Statistics"
    #    }

    def process(self, response, type):
        #如果有过去(old)的文章集合，那么从old的数据中选择大于等于2017年的数据
        if type not in response.meta or response.meta == 'page':
            old_records = response.xpath("//table[@id='collectionsort']//tr")
            index = 0
            for old_record in old_records:
                index = index + 1
                release_date = old_record.xpath("./td[@class='date-td']//@data-order").extract_first()
                if release_date is None:
                    continue
                release_year = release_date.split('-')[0]
                if int(release_year) < 2017:
                    break

                meta = {"type": "not-first"}
                if index == len(old_records):
                    #如果最后一篇文章仍然大于等于2017年
                    next_url = urlparse.urljoin(response.url, response.xpath("//div[@class='paginator pull-right']/span[@class='inactiveLink']/following-sibling::a[1]/@href").extract_first())
                    if next_url is not None and next_url != "":
                        page_meta = {"type": "page"}
                        yield response.follow(next_url, self.parse, meta = page_meta)

                article_url = urlparse.urljoin(response.url, old_record.xpath(".//td[@class='title-td']/a/@href").extract_first())
                yield response.follow(article_url, self.parse, meta = meta)

        #尝试获取本篇文章或者是lattest的信息
        latest = response.xpath(".//div[@class='row section-title']")[-1]
        if latest is not None and response.meta != 'page':
            title = Utils.get_all_inner_texts(latest, ".//h2").strip("\"")
            description = Utils.get_all_inner_texts(latest, ".//div[@class='description js-fulldescription']")
            pdf_link = urlparse.urljoin(response.url, latest.xpath(".//a[@class='action-pdf enabled']/@href").extract_first())
            meta_section = response.xpath(".//div[@class='block-infos-sidebar date-daily col-xs-12']")
            author = Utils.get_all_inner_texts(meta_section, "./p[1]").replace("Authors", "").strip()
            release_date = Utils.format_datetime(Utils.get_all_inner_texts(meta_section, "./p[2]"))
            pages = Utils.get_all_inner_texts(meta_section, "./p[3]").replace("pages", "").strip()
            isbn = Utils.get_all_inner_texts_from_selected_element(meta_section, "./p", "(PDF)|(EPUB)|(HTML)")
            doi = Utils.get_all_inner_texts(meta_section, "./a")
            language = Utils.get_all_inner_texts(latest, ".//p[@class='language']//strong[@class='bold']")
            pdf_file = Utils.doi_to_filname(doi) + ".pdf"
            if doi == '':
                return
            yield {
                "url": response.url,
                "title": title,
                "abstract": description,
                "pdf_link": pdf_link,
                "pdf_file": pdf_file,
                "author": author,
                "release_date": release_date,
                "pages": pages,
                "isbn": isbn,
                "doi": doi,
                "type": type,
                "language": language
            }

        
