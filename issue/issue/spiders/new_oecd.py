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
import json
from utils import Utils
reload(sys)
sys.setdefaultencoding('utf8')
from scrapy.http.request import Request

class NewOECDSpider(scrapy.Spider):
    name = "new_oecd"

    def __init__(self, url_file=None, revised = None, *args, **kwargs):
        super(NewOECDSpider, self).__init__(*args, **kwargs)
        self.url_file = url_file

        if revised == "True":
            self.revised = True
        else:
            self.revised = False

    def start_requests(self):
        #url = 'https://www.oecd-ilibrary.org/taxation/oecd-transfer-pricing-guidelines-for-multinational-enterprises-and-tax-administrations-2017_tpg-2017-en'
        #meta = {"type": "Books"}
        #yield Request(url, self.parse, dont_filter=True, meta = meta)
        #return
        with open(self.url_file, "rb") as f:
            for line in f:
                elem = json.loads(line.strip())
                if self.revised:
                    meta = {"type": elem["type"]}
                    yield Request(elem['url'], self.process_issue, dont_filter=True, meta = meta)
                else:
                    yield Request(elem['url'], self.parse, dont_filter=True)

    def parse(self, response):
        type = response.xpath(".//ol[@class='breadcrumb']/li[2]/a/text()").extract_first().strip()
        if type == "Statistics":
            return self.process(response, "Statistics")
        elif  type == "Books":
            return self.process(response, "Books")
        elif  type == "Papers":
            return self.process(response, "Papers")
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

    # 修正
    def process_issue(self, response):
        latest = response.xpath(".//div[@class='row section-title']")[-1]
        title = Utils.get_all_inner_texts(latest, ".//h2[1]").strip("\"")
        description = Utils.get_all_inner_texts(latest, ".//div[@class='description js-fulldescription']")
        pdf_link = urlparse.urljoin(response.url, latest.xpath(".//a[@class='action-pdf enabled']/@href").extract_first())
        meta_section = response.xpath(".//div[@class='block-infos-sidebar date-daily col-xs-12']")
        author = Utils.get_all_inner_texts(meta_section, "./p[1]").replace("Authors", "").strip()
        release_date = Utils.format_datetime(Utils.get_all_inner_texts(meta_section, "./p[2]"))
        pages = Utils.get_all_inner_texts(meta_section, "./p[3]").replace("pages", "").strip()
        isbn = Utils.get_all_inner_texts_from_selected_element(meta_section, "./p", "(PDF)|(EPUB)|(HTML)")
        isbn = Utils.regex_extract(isbn, "\w+")
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
            "type": response.meta["type"],
            "language": language
        }

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
        if latest is not None:
            if len(response.xpath("//ol[@class='breadcrumb']/li").extract()) > 3: #可能是一个比较trick的做法，看导航栏的条目
                book_title = Utils.get_all_inner_texts(response, "//ol[@class='breadcrumb']/li[3]")
                book_doi = urlparse.urljoin(response.url, response.xpath("//ol[@class='breadcrumb']/li[3]/a/@href").extract_first())
            else:
                book_title = ""
                book_doi = ""

            title = Utils.get_all_inner_texts(latest, ".//h2").strip("\"")
            subtitle = Utils.get_all_inner_texts(latest, ".//*[@class='sub-title']")
            description = Utils.get_all_inner_texts(latest, ".//div[@class='description js-fulldescription']")
            pdf_link = urlparse.urljoin(response.url, latest.xpath(".//a[@class='action-pdf enabled']/@href").extract_first())
            meta_section = response.xpath(".//div[@class='block-infos-sidebar date-daily col-xs-12']")

            author = meta_section.xpath("./p[1]/text()").extract()
            author = [ Utils.replcace_not_ascii(Utils.remove_separator(i)).replace("and ", "") for i in author ]
            author = [ i for i in author if i.strip() != "" ]
            author = ";".join(author)

            release_date = Utils.format_datetime(Utils.get_all_inner_texts(meta_section, "./p[2]"))
            pages = Utils.get_all_inner_texts(meta_section, "./p[3]").replace("pages", "").strip()
            isbn = Utils.get_all_inner_texts_from_selected_element(meta_section, "./p", "(PDF)|(EPUB)|(HTML)")
            if isbn == "":
                try:
                    isbn_elem = Utils.select_element_by_content(response, "////ul[@class='identifiers']/li", "ISSN")
                except Exception as e:
                    pass
                isbn = isbn_elem.xpath("./text()").extract_first()
                isbn = Utils.regex_extract(isbn, "ISSN: (\w+)")
            doi = Utils.get_all_inner_texts(meta_section, "./a")
            language = Utils.get_all_inner_texts(latest, ".//p[@class='language']//strong[@class='bold']")
            pdf_file = Utils.doi_to_filname(doi) + ".pdf"
            keywords = Utils.get_all_inner_texts(latest, ".//div[@class='col-xs-10 keyword']").replace("Keywords: ", "")
            if doi == '':
                return
            yield {
                "collection": book_title,
                "collection_url": book_doi,

                "url": response.url,
                "title": title,
                "subtitle": subtitle,
                "abstract": description,
                "pdf_link": pdf_link,
                "pdf_file": pdf_file,
                "author": author,
                "release_date": release_date,
                "pages": pages,
                "isbn": isbn,
                "doi": doi,
                "type": type,
                "language": language,
                "keywords": keywords
            }
