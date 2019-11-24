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
class SupSpider(scrapy.Spider):
    name = 'sup'
    def __init__(self, url_file=None, meta_file = None):
        self.url_file = url_file
        self.crawl_urls = []
        if meta_file:
            with open(meta_file, "rb") as f:
                for line in f:
                    try:
                      json_data = json.loads(line.strip())
                      issue_url = json_data["url"]
                    except Exception:
                      continue
                    self.crawl_urls.append(issue_url)

    def start_requests(self):
        with open(self.url_file, "rb") as f:
            for line in f:
                try:
                    json_data = json.loads(line.strip())
                    issue_url = json_data["url"]
                except Exception:
                    issue_url = line.strip()
                if issue_url in self.crawl_urls:
                    print "filter url: %s" % issue_url
                    continue
                #print "crawl url :%s" % issue_url
                #yield Request(issue_url, self.sage_sub, dont_filter=True)
                #yield Request(issue_url, self.oxford_sub, dont_filter=True)
                #yield Request(issue_url, self.bmj_sub, dont_filter=True)
                #yield Request(issue_url, self.tandfonline_sup, dont_filter=True)
                yield Request(issue_url, self.jstor_sup, dont_filter=True)

    def oxford_sub(self, response):
        """
        oxford的作者和作者机构需要单独爬取,用portia比较难
        """
        authors = response.xpath("//div[@class='al-authors-list']//*[@class='al-author-name']")
        author_list = []
        author_affliation_list = []
        for author in authors:
            author_name = Utils.get_all_inner_texts(author, ".//div[@class='info-card-name']")
            author_affiliation = Utils.get_all_inner_texts(author, ".//div[@class='aff'][1]")
            author_list.append(author_name)
            author_affliation_list.append(author_affiliation)

        pdf_link = response.xpath("//li[@class='toolbar-item item-pdf']/a/@href").extract_first()
        pdf_link = urlparse.urljoin(response.url, pdf_link)

        if len(author_list) != len(author_affliation_list):
            raise Exception("autho and author affliation len not equal: %s" % response.url)

        yield {
            "author" : author_list,
            "author_affilation" : author_affliation_list,
            "url" : response.url,
            "pdf_link": pdf_link,
        }

    def bmj_sub(self, response):
        """
        bmj的作者和作者机构单独爬一下爬,用portia爬错了
        """
        authors = response.xpath("//ol[@class='contributor-list']/li")
        author_list = []
        author_affliation_list = []
        author_sup_list = []
        for author in authors:
            author_name = Utils.get_all_inner_texts(author, ".//span[@class='name']")
            author_sup = ",".join(author.xpath(".//a[@class='xref-aff']/text()").extract())
            author_list.append(author_name)
            author_sup_list.append(author_sup)

        if len(author_list) != len(author_sup_list):
            raise Exception("autho and author sup len not equal: %s" % response.url)

        affs = response.xpath("//li[@class='aff']")
        for aff in affs:
            author_affiliation = Utils.get_all_inner_texts(aff, ".//address")
            author_affiliation = Utils.regex_extract(author_affiliation, "\d*(.*)$")
            author_affliation_list.append(author_affiliation)

        yield {
            "author" : author_list,
            "author_affilation" : author_affliation_list,
            "author_sup" : author_sup_list,
            "url" : response.url,
        }

    """
    Sage质检结果，发现少了一些字段
    """
    def sage_sub(self, response):
        publish_year = Utils.extract_with_xpath(response, "//div[@class='articleJournalNavTitle']/text()").split(',')
        keywords = ",".join(response.xpath("//div[@class='hlFld-KeywordText']/kwd-group/a/text()").extract())
        author = ",".join(response.xpath("//div[@class='authors']//div[@class='header']/a[@class='entryAuthor']/text()").extract())
        if author == "":
            author = ",".join(response.xpath("//div[@class='authors']//span[@class='contrib']/a[@class='entryAuthor']/text()").extract())

        publish_date = Utils.extract_all_with_xpath(response, "//span[@class='publicationContentEpubDate dates']/text()")
        abstract = ",".join(response.xpath("//div[@class='abstractSection abstractInFull']/p/text()").extract())
        source = 'sage'
        source_url = 'http://journals.sagepub.com/'
        acquisition_time = Utils.current_time()
        if len(publish_year)!= 3:
            raise Exception("cannot find publish_year for %s" % response.url)
        else:
            publish_year = publish_year[-1]

        yield {
            'publish_year': publish_year,
            'keywords': keywords,
            'author': author,
            'publish_date': publish_date,
            'abstract': abstract,
            'source': source,
            'source_url': source_url,
            'acquisition_time': acquisition_time,
            'url': response.url
        }
    
    """
    Tandfonline一开始的元数据是从列表页获取的，需要从详情页增加字段
    """
    def tandfonline_sup(self, response):
      author = response.xpath("//span[@class='NLM_contrib-group']/span/a/text()").extract()
      author_affiliation = response.xpath("//span[@class='NLM_contrib-group']/span/a/span/text()").extract()
      abstract = Utils.get_all_inner_texts(response, "//div[@class='abstractSection abstractInFull']")
      keywords = response.xpath("//div[@class='hlFld-KeywordText']/a/text()").extract()
      doi = response.xpath("//li[@class='dx-doi']/a/@href").extract_first()
      yield {
        "author" : author,
        "author_affliation" : author_affiliation,
        "abstract" : abstract,
        "keywords" : keywords,
        "doi" : doi,
        "url" : response.url
      }

    def jstor_sup(self, response):
         author = response.xpath("//div[@data-qa='item-authors']/div/text()").extract_first()
         doi = response.xpath("//div[@data-qa='crossref-doi']/text()").extract_first()
         collection_title = response.xpath("//h2[@data-qa='parent-content-title']/text()").extract_first()
         collection_url = response.xpath("//a[@data-qa='parent-content-text-link']/@href").extract_first()
         topics = ",".join(response.xpath("//ol[@data-qa='topics-list']/li/a/text()").extract())
         publisher = response.xpath("//a[@class='publisher-link']/text()").extract_first()
         meta_src = response.xpath("//div[@data-qa='item-src-info']/text()").extract_first()
         if meta_src is not None:
             volume = Utils.regex_extract(meta_src, "Vol. (\d+)")
             issue = Utils.regex_extract(meta_src, "Vol. \d+, No. (\d+)")
             start_page = Utils.regex_extract(meta_src, "pp. (\d+)-\d+")
             end_page = Utils.regex_extract(meta_src, "pp. \d+-(\d+)")
         else:
             volume = ""
             issue = ""
             start_page = ""
             end_page = ""
         yield {
             "stable_url": response.url,
             "author" : author,
             "doi": doi,
             "collection_title": collection_title,
             "collection_url": collection_url,
             "topics": topics,
             "publisher": publisher,
             "volume": volume,
             "issue": issue,
             "start_page": start_page,
             "end_page": end_page
         }





