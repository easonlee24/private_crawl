# -*- coding: utf-8 -*-
# 2019-06-01
# Wiley期刊的爬虫，支持续采
import scrapy
import urlparse
from utils import Utils
from scrapy.http.request import Request
import re
import json
import urlparse

class WileySpider(scrapy.Spider):
    name = 'wiley'

    """
    @param start_year 爬起的期刊发布日期>=start_year, 为None时没有此限制。
    """
    def __init__(self, url_file=None, start_year=None):
        self.url_file = url_file
        if start_year is None:
            self.start_year = 0
        else:
            self.start_year = start_year

    def start_requests(self):
        #调试
        #meta = {"journal_url": "url"}
        #url = "https://onlinelibrary.wiley.com/doi/10.1111/acel.12898"
        #yield Request(url, self.crawl_issue_info, meta = meta, dont_filter=True)
        #return

        with open(self.url_file, "rb") as f:
            for line in f:
                meta = {"journal_url": line.strip()}
                # http://onlinelibrary.wiley.com/journal/10.1111/(ISSN)1474-9726 change to : https://onlinelibrary.wiley.com/loi/14749726
                journal_id = Utils.regex_extract(line.strip(), "\(ISSN\)(\d+)-([\dX]+)")
                journal_issue_url = "http://onlinelibrary.wiley.com/loi/%s" % journal_id
                yield Request(journal_issue_url, self.crawl_homepage, meta = meta, dont_filter=True)

    def crawl_homepage(self, response):
        journals = response.xpath("//ul[@class='rlist loi__list']/li")
        for journal in journals:
            link_text = Utils.extract_text_with_xpath(journal, "./a/span")
            year = Utils.regex_extract(link_text, "(\d+) - Volume")
            url = urlparse.urljoin(response.url, journal.xpath("./a/@href").extract_first())
            if year >= self.start_year:
                meta = {"journal_url": response.meta["journal_url"]}
                yield Request(url, self.crawl_journal, meta = meta)

    def crawl_journal(self, response):
        issues = response.xpath("//div[@class='loi__issue']")
        for issue in issues:
            url = urlparse.urljoin(response.url, issue.xpath(".//h4[@class='parent-item']/a/@href").extract_first())
            meta = {"journal_url": response.meta["journal_url"]}
            yield Request(url, self.crawl_issue, meta = meta)

    def crawl_issue(self, response):
        issues = response.xpath(".//div[@class='issue-item']")
        for issue in issues:
            url = urlparse.urljoin(response.url, issue.xpath("./a/@href").extract_first())
            meta = {"journal_url": response.meta["journal_url"]}
            yield Request(url, self.crawl_issue_info, meta = meta)

    def crawl_issue_info(self, response):
        article_title = Utils.get_all_inner_texts(response, ".//h2[@class='citation__title']")

        #作者和作者机构
        authors = response.xpath(".//a[contains(@class, 'author-name')]")
        index = 0
        author = ""
        auth_institution = ""
        sup = 1
        index = 0
        for author_elem in authors:
            author_name = author_elem.xpath("./span/text()").extract_first()

            affiliation = author_elem.xpath("following-sibling::div")
            affiliation_text = "|".join([ v for v in affiliation.xpath("./p/text()").extract() if Utils.is_valid_affliation(v)])

            if index != 0:
                author += ";"
                auth_institution += ";"

            # 有作者机构
            if affiliation_text != "":
                author += "%s^%s" % (author_name, sup)
                auth_institution += "%s^%s" %(affiliation_text, sup)
                sup += 1
            else:
                author += author_name
                auth_institution += affiliation_text

            index +=1

        doi = response.xpath("//a[@class='epub-doi']/@href").extract_first()
        source_year = Utils.extract_text_with_xpath(response, "//span[@class='epub-date']").split()[-1]
        volume_issue = response.xpath("//p[@class='volume-issue']//span[@class='val']")
        source_volume = volume_issue[0].xpath("./text()").extract_first().strip()
        source_issue = volume_issue[1].xpath("./text()").extract_first().strip()
        article_abstract = Utils.get_all_inner_texts(response, ".//div[@class='abstract-group']").replace("Abstract", "").strip()
        #(TODO:lizhen05) keyword获取不到，要动态获取。
        keyword = Utils.extract_all_text_with_xpath(response, "//section[@class='keywords']/li/a")
        file_path = response.url
        process_date = Utils.current_date()
        download_path = urlparse.urljoin(response.url, response.xpath("//div[contains(@class, 'PdfLink')]/a/@href").extract_first())
        yield {
            "article_title" : article_title,
            "author": author,
            "auth_institution": auth_institution,
            "doi": doi,
            "source_year": source_year,
            "source_volume": source_volume,
            "source_issue": source_issue,
            "article_abstract": article_abstract,
            "file_path": file_path,
            "download_path": download_path,
            "process_date": process_date,
            "journal_url" : response.meta["journal_url"]
        }
