# -*- coding: utf-8 -*-
import scrapy
import urlparse
from utils import Utils
from scrapy.http.request import Request
import re
import json

"""
This sipder will continue to crawl some fields that:
1. cannot easy crawled by portia
2. miss fields 
"""
class ScieloSpider(scrapy.Spider):
    name = 'scielo_up'
    allowed_domains = ['www.scielo.br']

    def __init__(self, url_file=None):
        self.url_file = url_file

    def start_requests(self):
        with open(self.url_file, "rb") as f:
            for line in f:
                json_data = json.loads(line)
                issue_url = json_data["access_url"]
                yield Request(issue_url, self.crawl_sup_3, dont_filter=True)

    """
    发现少了一些字段
    """
    def crawl_sup_1(self, response):
        authors = response.xpath("//div[@class='autores']/p[@class='author']")
        author_sup_texts = [",".join(author.xpath("./sup/a/text()").extract()) for author in authors]
        date = response.xpath("//h3/text()").extract_first()

        yield {
            'author_sup_texts': author_sup_texts,
            'publish-date': date,
            'url': response.url
        }

    """
    11.19更新，重爬：
    1. pdf_link,不知道为啥漏了很多
    2. abstract, 另一种格式的摘要
    3. author_affiliation,一些作业机构
    4. keywords, 另一种格式的keywords
    5. volumn and issue, 还一中special issue的例子，比如:http://www.scielo.br/scielo.php?script=sci_issues&pid=0103-6351&lng=en&nrm=iso
    """
    def crawl_sup_2(self, response):
        pdf_link_elem = Utils.select_element_by_content(response, "//*[@id='toolBox']/div/ul/li/a", "English (pdf)")

        pdf_link = pdf_link_elem.xpath("@href").extract_first()
        pdf_link = urlparse.urljoin(response.url, pdf_link)

        abstract = Utils.get_all_inner_texts(response, "//div[@class='abstract']/div[@class='section']/p")

        keywords = response.xpath("//div[@class='abstract']/p/b/../text()").extract_first()
        if keywords is None:
            keywords = ''
        #try:
        #    keywords = Utils.select_element_by_content(response, "//div[@class='abstract']/p/b", "Key words:|Descriptors").xpath("../text()").extract_first()
        #except Exception as e:
        #    pass

        author_affiliation = [v for v in response.xpath("//div[@class='autores']/following-sibling::p/text()").extract() if v.strip() != ""]

        volumn_issue = response.xpath("//h3/text()").extract_first().strip()
        volumn_issue = Utils.replcace_not_ascii(volumn_issue)
        volumn = ""
        issue = ""

        match = re.match(".*vol\.(?P<volumn>\d+) (no\.)?(?P<issue>(suppl\.)?\S+) \S+", volumn_issue)
        if match:
            volumn = match.group("volumn")
            issue = match.group("issue")

        yield {
            'pdf_link': pdf_link,
            'abstract': abstract,
            'keywords': keywords,
            'author_affiliation': author_affiliation,
            'volumn': volumn,
            'issue': issue,
            "url" : response.url
        }

    """
    2018.08.15 补采集下面的字段：
    2018.09.17 补采集下面的字段：
    1、date
    """
    def crawl_sup_3(self, response):
        date = response.xpath("//h3/text()").extract_first().split("/")[-1]
        abstract = Utils.get_all_inner_texts(response, "//div[@class='abstract']")
        title = Utils.get_all_inner_texts(response, "//p[@class='title']")

        yield {
            'access_url': response.url,
            'date': date,
            "abstract": abstract,
            'title': title
        }
