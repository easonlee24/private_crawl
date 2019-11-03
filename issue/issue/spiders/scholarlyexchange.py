    # -*- coding: utf-8 -*-
# 2019-06-16
# scholarlyexchange期刊的爬虫，支持续采
import scrapy
import urlparse
from utils import Utils
from scrapy.http.request import Request
import re
import json
import urlparse

class ScholarlyexchangeSpider(scrapy.Spider):
    name = 'scholarlyexchange'

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
        #url = "https://www.neuroregulation.org/article/view/18189"
        #yield Request(url, self.crawl_issue_info, meta = meta, dont_filter=True)
        #return

        with open(self.url_file, "rb") as f:
            for line in f:
                meta = {"journal_url": line.strip()}
                # http://onlinelibrary.wiley.com/journal/10.1111/(ISSN)1474-9726 change to : https://onlinelibrary.wiley.com/loi/14749726
                journal_issue_url = "%s/issue/archive" % (line.strip())
                yield Request(journal_issue_url, self.crawl_homepage, meta = meta, dont_filter=True)

    def crawl_homepage(self, response):
        journals = response.xpath("//ul[@class='issues_archive']/li")
        for journal in journals:
            link_text = Utils.extract_text_with_xpath(journal, ".//a[@class='title']")
            year = Utils.regex_extract(link_text, "No.*\((\d+)\)")
            #print "link_text: %s, year: %s" % (link_text, year)
            url = urlparse.urljoin(response.url, journal.xpath(".//a[@class='title']/@href").extract_first())
            if year >= self.start_year:
                meta = {"journal_url": response.meta["journal_url"]}
                yield Request(url, self.crawl_issue, meta = meta)

    def crawl_issue(self, response):
        issues = response.xpath("//div[@class='sections']/div[@class='section']")
        for issue in issues:
            url = urlparse.urljoin(response.url, issue.xpath(".//div[@class='title']/a/@href").extract_first())
            meta = {"journal_url": response.meta["journal_url"]}
            yield Request(url, self.crawl_issue_info, meta = meta)

    def crawl_issue_info(self, response):
        article_title = Utils.get_all_inner_texts(response, ".//h1[@class='page_title']")

        #作者和作者机构
        authors = response.xpath(".//ul[@class='item authors']/li")
        institutions = []
        index = 0
        author = ""
        auth_institution = ""
        sup = 1
        index = 0
        for author_elem in authors:
            author_name = author_elem.xpath("./span[@class='name']/text()").extract_first().strip()

            affiliation_text = Utils.extract_text_with_xpath(author_elem, "./span[@class='affiliation']")

            if index != 0:
                author += ";"

            # 有作者机构
            if affiliation_text != "":
                try:
                    institution_index = institutions.index(affiliation_text)
                except Exception as e:
                    institution_index = -1

                if institution_index == -1:
                    if index != 0:
                        auth_institution += ";"
                    author += "%s^%s" % (author_name, sup)
                    auth_institution += "%s^%s" %(affiliation_text, sup)
                    institutions.append(affiliation_text)
                    sup += 1
                else:
                    author += "%s^%s" % (author_name, institution_index + 1)

            else:
                author += author_name

            index +=1

        doi = Utils.extract_text_with_xpath(response, "//div[@class='item doi']/span[@class='value']/a")
        keyword = Utils.get_all_inner_texts(response, "//div[@class='item keywords']/span[@class='value']")
        article_abstract = Utils.get_all_inner_texts(response, "//div[@class='item abstract']").replace("Abstract", "").strip()

        crumbs = response.xpath("//nav[@class='cmp_breadcrumbs']/ol/li[3]/a/text()").extract_first().strip()
        source_year = Utils.regex_extract(crumbs, "\((\d+)\)")
        source_volume = Utils.regex_extract(crumbs, "Vol (\d+)")
        source_issue = Utils.regex_extract(crumbs, "No (\d+)")
        file_path = response.url
        process_date = Utils.current_date()
        download_path = urlparse.urljoin(response.url, response.xpath("//a[@class='obj_galley_link pdf']/@href").extract_first())
        yield {
            "article_title" : article_title,
            "author": author,
            "auth_institution": auth_institution,
            "doi": doi,
            "source_year": source_year,
            "source_volume": source_volume,
            "source_issue": source_issue,
            "keyword": keyword,
            "article_abstract": article_abstract,
            "file_path": file_path,
            "download_path": download_path,
            "process_date": process_date,
            "journal_url" : response.meta["journal_url"]
        }
