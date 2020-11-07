        # -*- coding: utf-8 -*-
# 2019-11-17
# Asm期刊的爬虫，支持续采
import scrapy
import urlparse
from utils import Utils
from scrapy.http.request import Request
import re
import json
import urlparse

class AsmSpider(scrapy.Spider):
    name = 'asm'

    """
    @param start_year 爬起的期刊发布日期>=start_year, 为None时没有此限制。
    @param save_dir xml的保存路径
    """
    def __init__(self, url_file=None, start_year=None, save_dir = None):
        self.url_file = url_file
        if start_year is None:
            self.start_year = 0
            self.save_dir = None
        else:
            self.start_year = start_year
            self.save_dir = save_dir

    def start_requests(self):
        #调试
        #meta = {"journal_url": "url", "year": "2019"}
        #url = "https://jvi.asm.org/content/83/10"
        #yield Request(url, self.crawl_issue_info, meta = meta, dont_filter=True)
        #return

        with open(self.url_file, "rb") as f:
            for line in f:
                meta = {"journal_url": line.strip()}
                yield Request(line.strip(), self.crawl_homepage, meta = meta, dont_filter=True)

    def crawl_homepage(self, response):
        url = "%s/content/by/year" % response.url.strip("/")
        meta = {"journal_url": response.meta["journal_url"]}
        yield Request(url, self.crawl_journal, meta = meta, dont_filter=True)

    def crawl_journal(self, response):
        journals = response.xpath("//div[@class='highwire-list']//li[contains(@class, year)]/a")
        for journal in journals:
            year = journal.xpath("./text()").extract_first()
            url = urlparse.urljoin(response.url, journal.xpath("./@href").extract_first())

            if year == "All":
                continue

            if year >= self.start_year:
                if year == '2020':
                    return
                meta = {"journal_url": response.meta["journal_url"], "year": year}
                yield Request(url, self.crawl_issue, meta = meta)

    def crawl_issue(self, response):
        issues = response.xpath(".//a[@class='hw-issue-meta-data']")
        for issue in issues:
            url = urlparse.urljoin(response.url, issue.xpath("./@href").extract_first())

            yield Request(url, self.crawl_issue_info, meta = response.meta)


    def crawl_issue_info(self, response):
        articles = response.xpath("//a[@class='highwire-cite-linked-title']")
        for article in articles:
            article_url = article.xpath("./@href").extract_first()
            yield Request(urlparse.urljoin(response.url, article_url), self.crawl_title, meta = response.meta)

    def crawl_title(self, response):
        article_title = Utils.get_all_inner_texts(response, "//h1[@class='highwire-cite-title']")

        try:
            authors = response.xpath("//span[@class='highwire-citation-authors']")[0].xpath(".//span[contains(@class, highwire-citation-author)]")
            author_text = []
            for author in authors:
                author_text.append(Utils.get_all_inner_texts(author, ""))
            author_text = ";".join(author_text)
        except Exception as e:
            author_text = ""

        doi_elem = Utils.select_element_by_content(response, "//strong", "DOI:").xpath("..")
        doi = Utils.replcace_not_ascii(Utils.get_all_inner_texts(doi_elem, "").replace("DOI", ""), "")

        download_path = urlparse.urljoin(response.url, response.xpath("//a[@data-trigger='full-text.pdf']/@href").extract_first())

        volume = Utils.regex_extract(response.url, "content/(\d+)")
        issue = Utils.regex_extract(response.url, "content/\d+/(\d+)")

        try:
            keywords_elem = Utils.select_element_by_content(response, "//h2[@class='pane-title']", "KEYWORDS")
            keyword = ";".join(keywords_elem.xpath("./following-sibling::div[@class='pane-content']//div[contains(@class, field-item)]/a/text()").extract())
        except Exception as e:
            keyword = ""

        try:
            abstract_elem = Utils.select_element_by_content(response, "//h2", "ABSTRACT")
            abstract = Utils.get_all_inner_texts(abstract_elem.xpath("./following-sibling::p")[0], "")
        except Exception as e:
            abstract = ""



        yield {
            "article_title" : article_title,
            "author": author_text,
            "doi": doi,
            "source_year": response.meta["year"],
            "source_volume": volume,
            "source_issue": issue,
            "file_path": response.url,
            "download_path": download_path,
            "process_date": Utils.current_date(),
            "keyword": keyword,
            "article_abstract": abstract,
            "journal_url" : response.meta["journal_url"],
        }

