    # -*- coding: utf-8 -*-
# 2019-06-15
# Pensoft期刊的爬虫，支持续采
# 注意：pensoft的abstract和keywords字段，很难爬取，因为是iframe嵌入的。有两种方法：
#      1. 采用selenium，但在本地和服务器上都试了，针对这个网站打开网页太慢了。
#      2. 把xml下载下来，然后从xml里面解析缺少的字段。最终采用这种方式。
import scrapy
import urlparse
from utils import Utils
from scrapy.http.request import Request
import re
import json
import urlparse

class PensoftSpider(scrapy.Spider):
    name = 'pensoft'

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
        #meta = {"journal_url": "url"}
        #url = "https://zookeys.pensoft.net/issue/1384/"
        #yield Request(url, self.crawl_issue_info, meta = meta, dont_filter=True)
        #return

        with open(self.url_file, "rb") as f:
            for line in f:
                meta = {"journal_url": line.strip()}
                yield Request(line.strip(), self.crawl_homepage, meta = meta, dont_filter=True)

    def crawl_homepage(self, response):
        url = "%s/issues" % response.url.strip("/")
        meta = {"journal_url": response.meta["journal_url"]}
        yield Request(url, self.crawl_journal, meta = meta, dont_filter=True)

    def crawl_journal(self, response):
        journals = response.xpath("//div[@class='filterBlockContent']/a")
        for journal in journals:
            year = journal.xpath("./text()").extract_first()
            url = urlparse.urljoin(response.url, journal.xpath("./@href").extract_first())

            if year == "All":
                continue

            if year >= self.start_year:
                meta = {"journal_url": response.meta["journal_url"], "is_first": True}
                yield Request(url, self.crawl_issue, meta = meta)

    def crawl_issue(self, response):
        issues = response.xpath(".//a[@class='green issueTitle']")
        for issue in issues:
            url = urlparse.urljoin(response.url, issue.xpath("./@href").extract_first())

            meta = {"journal_url": response.meta["journal_url"]}
            yield Request(url, self.crawl_issue_info, meta = meta)

        if response.meta["is_first"]:
            identifier = response.xpath("//h1[@class='issue_title_identifier']/text()").extract_first()
            total_issue_num = Utils.regex_extract(identifier, ".*-(\d+) issues.*")
            total_issue_num = int(total_issue_num)
            total_page = total_issue_num / 12 + 1
            for i in range(1, total_page):
                next_page_url = "%s&p=%d" % (response.url, i)
                meta = {"journal_url": response.meta["journal_url"], "is_first": False}
                yield Request(next_page_url, self.crawl_issue, meta = meta)


    def crawl_issue_info(self, response):
        header_text = response.xpath(".//div[@class='zag']/text()").extract_first()
        issue_number = Utils.regex_extract(header_text, ".* (\d+) \(\d+\)")
        articles = response.xpath("//div[@class='article']")
        for article in articles:
            article_title = Utils.get_all_inner_texts(article, ".//div[@class='articleHeadline']")
            author = Utils.get_all_inner_texts(article, ".//div[@class='authors_list_holder']")
            doi = Utils.get_all_inner_texts(article, ".//a[@class='ArtDoi subLink']").replace("doi: ", "")
            pub_date = Utils.get_all_inner_texts(article, ".//span[@class='pub_date']")
            source_year = Utils.regex_extract(pub_date, ".*\d+-\d+-(\d+)")
            page_info = article.xpath(".//span[@class='pages_icon']/following-sibling::span[1]/text()").extract_first().strip()
            article_page_info = page_info
            article_fpage = Utils.regex_extract(article_page_info, "(\d+)-\d+")
            article_lpage = Utils.regex_extract(article_page_info, "\d+-(\d+)")
            article_page_count = int(article_lpage) - int(article_fpage) + 1
            meta = {
                "journal_url": response.meta["journal_url"],
                "source_issue": issue_number,
                "article_title": article_title,
                "author": author,
                "doi": doi,
                "source_year": source_year,
                "article_fpage": article_fpage,
                "article_lpage": article_lpage,
                "article_page_count": article_page_count,
                "article_page_range": article_page_info
            }


            article_url = article.xpath(".//div[@class='articleHeadline']//a/@href").extract_first()
            yield Request(urlparse.urljoin(response.url, article_url), self.crawl_title, meta = meta)

    def crawl_title(self, response):
        pdf_element = Utils.select_element_by_content(response, "//div[@class='col-xs browse_button']", "PDF")
        download_path = urlparse.urljoin(response.url, pdf_element.xpath("./a/@href").extract_first())

        xml_element = Utils.select_element_by_content(response, "//div[@class='col-xs browse_button']", "XML")
        xml_download_path = urlparse.urljoin(response.url, xml_element.xpath("./a/@href").extract_first())

        process_date = Utils.current_date()


        yield {
            "article_title" : response.meta["article_title"],
            "author": response.meta["author"],
            "doi": response.meta["doi"],
            "source_year": response.meta["source_year"],
            "source_issue": response.meta["source_issue"],
            "file_path": response.url,
            "download_path": download_path,
            "process_date": process_date,
            "journal_url" : response.meta["journal_url"],
            "article_fpage": response.meta["article_fpage"],
            "article_lpage": response.meta["article_lpage"],
            "article_page_count": response.meta["article_page_count"],
            "article_page_range": response.meta["article_page_range"]
        }

        filename = "%s/%s.xml" % (self.save_dir, Utils.doi_to_filname(response.meta["doi"]))
        meta = {'filename': filename}
        yield Request(xml_download_path, self.download_file, meta = meta)

    def download_file(self, response):
        filename = response.meta["filename"]
        print "save file to %s" % filename
        with open(filename, "wb") as f:
            f.write(response.body)
        f.close()
