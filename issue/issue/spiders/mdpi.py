# -*- coding: utf-8 -*-
# 2019-05-18
# Mdpi期刊的爬虫，支持续采
import scrapy
import urlparse
from utils import Utils
from scrapy.http.request import Request
import re
import json
import urlparse

class MdpiSpider(scrapy.Spider):
    name = 'mdpi'

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
        # 调试
        #meta = {"journal_url": "url"}
        #url = "https://www.mdpi.com/2079-3200/7/3/20"
        #yield Request(url, self.crawl_issue_info, meta = meta, dont_filter=True)
        #return

        with open(self.url_file, "rb") as f:
            for line in f:
                meta = {"journal_url": line.strip()}
                yield Request(line.strip(), self.crawl_homepage, meta = meta, dont_filter=True)

    def crawl_homepage(self, response):
        journals = response.xpath("//div[@class='show-for-large-up']//li[@class='side-menu-li']/a")
        for journal in journals:
            link_text = journal.xpath("./text()").extract_first().strip()
            year = Utils.regex_extract(link_text, "Vol.*\((\d+)\).*")
            url = urlparse.urljoin(response.url, journal.xpath("./@href").extract_first())
            if year >= self.start_year:
                meta = {"journal_url": response.meta["journal_url"]}
                yield Request(url, self.crawl_journal, meta = meta)

    def crawl_journal(self, response):
        issues = response.xpath("//div[@id='middle-column']//div[@class='issue-cover']")
        for issue in issues:
            url = urlparse.urljoin(response.url, issue.xpath(".//a/@href").extract_first())
            meta = {"journal_url": response.meta["journal_url"]}
            yield Request(url, self.crawl_issue, meta = meta)

        if len(issues) == 0:
            #另一种格式，比如:https://www.mdpi.com/2079-8954/7
            issues = response.xpath("//div[@class='ul-spaced']//li")
            for issue in issues:
                url = urlparse.urljoin(response.url, issue.xpath("./a/@href").extract_first())
                meta = {"journal_url": response.meta["journal_url"]}
                yield Request(url, self.crawl_issue, meta = meta)
                


    def crawl_issue(self, response):
        issues = response.xpath(".//a[@class='title-link']")
        for issue in issues:
            url = urlparse.urljoin(response.url, issue.xpath("./@href").extract_first())
            meta = {"journal_url": response.meta["journal_url"]}
            yield Request(url, self.crawl_issue_info, meta = meta)

    def crawl_issue_info(self, response):
        article_title = Utils.get_all_inner_texts(response, ".//h1[@class='title hypothesis_container']")

        #作者
        authors = response.xpath(".//div[@class='art-authors hypothesis_container']/span[@class='inlineblock']")
        index = 0
        author = ""
        for author_elem in authors:
            author_name = author_elem.xpath("./a[@itemprop='author']/text()").extract_first()
            if author_name is None:
                author_name = author_elem.xpath("./span/a/text()").extract_first()
            try:
                sup = author_elem.xpath("./sup/text()").extract_first().strip()
            except Exception as e:
                sup = ""
            if index != 0:
                author += ";"

            # 有可能没有作者机构
            sup = Utils.format_oa_sup(sup)
            if sup == "*":
                author += "%s^%s" % (author_name, "*1")
            elif sup != "":
                author += "%s^%s" % (author_name, sup)
            else:
                author += "%s^%s" % (author_name, "1")
            index += 1

        #作者机构
        affiliations = response.xpath(".//div[@class='affiliation']")
        index = 0
        auth_institution = ""
        for affiliation in affiliations:
            sup = affiliation.xpath(".//sup/text()").extract_first()
            if sup is None:
                sup = "1"
            text = Utils.extract_text_with_xpath(affiliation, "./div[@class='affiliation-name ']")
            if text == "":
                text = Utils.extract_text_with_xpath(affiliation, "./div[contains(@class, 'affiliation-name')]")
            if index != 0:
                auth_institution += ";"
            if Utils.is_valiad_affliation_sup(sup):
                auth_institution += "%s^%s" %(text, sup)
            else:
                # 非法的作者机构，忽略
                continue
                
            index += 1

        identity = response.xpath(".//div[@class='bib-identity']")
        doi = Utils.extract_text_with_xpath(identity, "./a")
        source_year = Utils.extract_text_with_xpath(identity, "./b")
        source_volume = Utils.extract_text_with_xpath(identity, "./em[last()]")
        text = Utils.get_all_inner_texts(response, ".//div[@class='bib-identity']")
        source_issue = Utils.regex_extract(text, ".*\((\d+)\).*")
        article_abstract = Utils.get_all_inner_texts(response, ".//div[@class='art-abstract in-tab hypothesis_container']").replace("Abstract", "").strip()
        keyword = Utils.get_all_inner_texts(response, ".//span[@itemprop='keywords']")
        file_path = response.url

        #pdf连接
        try:
            pdf_elem = Utils.select_element_by_content(response, ".//div[@class='download']/a", "PDF")
            download_path = urlparse.urljoin(response.url, pdf_elem.xpath("./@href").extract_first())
        except Exception as e:
            pdf_elem = response.xpath(".//div[@class='dwnld_block']")
            download_path = urlparse.urljoin(response.url, pdf_elem[-1].xpath("./a/@href").extract_first())

        process_date = Utils.current_date()
        yield {
            "article_title" : article_title,
            "author": author,
            "auth_institution": auth_institution,
            "doi": doi,
            "source_year": source_year,
            "source_volume": source_volume,
            "source_issue": source_issue,
            "article_abstract": article_abstract,
            "keyword": keyword,
            "file_path": file_path,
            "download_path": download_path,
            "process_date": process_date,
            "journal_url" : response.meta["journal_url"]
        }
