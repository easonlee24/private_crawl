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
    def __init__(self, url_file=None, start_year=None, revised=None):
        self.url_file = url_file
        if start_year is None:
            self.start_year = 0
        else:
            self.start_year = start_year

        if revised is not None and revised == "True":
            self.revised = True
        else:
            self.revised = False

    def start_requests(self):
        #调试
        #meta = {"journal_url": "url"}
        #url = "https://www.embopress.org/doi/10.15252/msb.20188777"
        #yield Request(url, self.crawl_issue_info_2, meta = meta, dont_filter=True)
        #return

        with open(self.url_file, "rb") as f:
            for line in f:
                if self.revised:
                    #元数据校订
                    elem = json.loads(line.strip())
                    meta = {"journal_url": elem["journal_url"]}
                    url = elem["file_path"]
                    yield Request(url, self.crawl_issue_info, meta = meta, dont_filter=True)
                else:
                    meta = {"journal_url": line.strip()}
                    # case1: http://onlinelibrary.wiley.com/journal/10.1111/(ISSN)1474-9726 change to : https://onlinelibrary.wiley.com/loi/14749726
                    journal_id = Utils.regex_extract(line.strip(), "\(ISSN\)(\d+)-([\dX]+)")

                    # case2: https://besjournals.onlinelibrary.wiley.com/journal/13652656 change to: ttps://onlinelibrary.wiley.com/loi/13652656
                    # (不用担心host是besjournals.onlinelibrary.wiley.com，把host改为onlinelibrary.wiley.com会自动重定向的)
                    if journal_id == "":
                        journal_id = Utils.regex_extract(line.strip(), "journal/([\dX]+)")
                    if journal_id == "":
                        journal_id = Utils.regex_extract(line.strip(), "loi/([\dX]+)")
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

        if len(journals) == 0:
            #另一种case，比如: https://www.embopress.org/loi/17574684
            journals = response.xpath("//div[@class='scroll']//li")
            url = "%s/group/d2010.y2019" % response.url
            meta = {"journal_url": response.meta["journal_url"]}
            yield Request(url, self.crawl_journal, meta = meta)

    def crawl_journal(self, response):
        issues = response.xpath("//div[@class='loi__issue']")
        for issue in issues:
            url = urlparse.urljoin(response.url, issue.xpath(".//*[@class='parent-item']/a/@href").extract_first())
            meta = {"journal_url": response.meta["journal_url"]}
            yield Request(url, self.crawl_issue, meta = meta)

    def crawl_issue(self, response):
        issues = response.xpath(".//div[@class='issue-item']")
        for issue in issues:
            url = urlparse.urljoin(response.url, issue.xpath("./a/@href").extract_first())
            if url == response.url:
                url = urlparse.urljoin(response.url, issue.xpath(".//a/@href").extract_first())
            meta = {"journal_url": response.meta["journal_url"]}
            yield Request(url, self.crawl_issue_info_2, meta = meta)

    def crawl_issue_info(self, response):
        article_title = Utils.get_all_inner_texts(response, ".//h1[@class='citation__title']")

        doi = response.xpath("//a[@class='epub-doi']/@href").extract_first()
        if doi is None:
            #另一个case
            print "....hehe....."
            self.crawl_issue_info_2(response)
            return

        #作者和作者机构
        authors = response.xpath(".//a[contains(@class, 'author-name')]")

        index = 0
        author = ""
        auth_institution = ""
        sup = 1
        index = 0
        extracted_authors = []
        extracted_author_ins = []
        email_address = ""
        for author_elem in authors:
            author_name = author_elem.xpath("./span/text()").extract_first()
            if author_name in extracted_authors:
                # wiley的格式有可能每个作者都被爬两次
                continue
            extracted_authors.append(author_name)

            affiliation = [ "".join(v.xpath(".//text()").extract()) for v in author_elem.xpath("following-sibling::div").xpath("./p")]
            affiliation_text = "|".join([ v for v in affiliation if Utils.is_valid_affliation(v, [author_name])])

            #print "author: %s" % author_name
            #print affiliation
            #print "affiliation_text: %s" % affiliation_text

            if index != 0:
                author += ";"

            # 有作者机构
            if affiliation_text != "":
                try:
                    sup = extracted_author_ins.index(affiliation_text) + 1
                except Exception as e:
                    sup = -1

                if sup == -1:
                    extracted_author_ins.append(affiliation_text)
                    sup = len(extracted_author_ins)
                    author += "%s^%s" % (author_name, sup)
                    if index != 0:
                        auth_institution += ";" 
                    auth_institution += "%s^%s" %(affiliation_text, sup)
                else:
                    author += "%s^%s" % (author_name, sup)
            else:
                author += author_name

            # 作者邮箱
            try:
                email_elem = Utils.select_element_by_content(affiliation, ".//span", "E-mail address")
                email_text = email_elem.xpath("following-sibling::a").xpath("./text()").extract_first()
                email_address += "%s;" % email_text
            except Exception as e:
                pass

            index +=1

        source_year = Utils.extract_text_with_xpath(response, "//span[@class='epub-date']").split()[-1]
        volume_issue = response.xpath("//p[@class='volume-issue']//span[@class='val']")
        source_volume = volume_issue[0].xpath("./text()").extract_first().strip()
        source_issue = volume_issue[1].xpath("./text()").extract_first().strip()
        article_abstract = Utils.get_all_inner_texts(response, ".//div[@class='abstract-group']").replace("Abstract", "").strip()
        if article_abstract == "":
            # 质检发现有些abstract是空的
            try:
                abstract_header_elem = Utils.select_element_by_content(response, "//h2", "Abstract")
                article_abstract = Utils.get_all_inner_texts(abstract_header_elem, "following-sibling::div")
            except Exception as e:
                pass
        #(TODO:lizhen05) keyword获取不到，要动态获取。
        keyword = Utils.extract_all_text_with_xpath(response, "//section[@class='keywords']/li/a")
        file_path = response.url
        process_date = Utils.current_date()
        download_path = urlparse.urljoin(response.url, response.xpath("//div[contains(@class, 'PdfLink')]/a/@href").extract_first())

        #页面
        page_info = Utils.get_all_inner_texts(response, "//p[@class='page-range']")
        if page_info != "":
            article_fpage = Utils.regex_extract(page_info, "(\d+)-\d+")
            article_lpage = Utils.regex_extract(page_info, "\d+-(\d+)")
            article_page_range = "%s-%s" % (article_fpage, article_lpage)
            try:
                article_page_count = str(int(article_lpage) - int(article_fpage) + 1)
            except Exception as e:
                article_page_count = 0
        else:
            article_fpage = ""
            article_lpage = ""
            article_page_range = ""
            article_page_count = ""

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
            "journal_url" : response.meta["journal_url"],
            "article_fpage" : article_fpage,
            "article_lpage" : article_lpage,
            "article_page_range" : article_page_range,
            "article_page_count" : article_page_count,
            "author_email": email_address.strip(";")
        }

    def crawl_issue_info_2(self, response):
        print "-----here-------"
        #另一个格式: jourlnal:https://www.embopress.org/loi/17574684, issue: https://www.embopress.org/doi/10.15252/msb.20188777
        article_title = Utils.get_all_inner_texts(response, ".//h1[@class='citation__title']")
        authors = response.xpath(".//div[@class='accordion-tabbed']/div")

        author = ""
        auth_institution = ""
        index = 0
        extracted_author_ins = []
        for author_elem in authors:
            author_name = Utils.get_all_inner_texts(author_elem, "./a")
            #affiliation_text = Utils.get_all_inner_texts(author_elem, "./div/p")

            affiliation = [ "".join(v.xpath("./text()").extract()) for v in author_elem.xpath("./div/p")]
            affiliation_text = "|".join([ v for v in affiliation if Utils.is_valid_affliation(v, [author_name])])

            if (index != 0):
                author += ";"

            # 有作者机构
            if affiliation_text != "":
                try:
                    sup = extracted_author_ins.index(affiliation_text) + 1
                except Exception as e:
                    sup = -1

                if sup == -1:
                    extracted_author_ins.append(affiliation_text)
                    sup = len(extracted_author_ins)
                    author += "%s^%s" % (author_name, sup)
                    if index != 0:
                        auth_institution += ";" 
                    auth_institution += "%s^%s" %(affiliation_text, sup)
                else:
                    author += "%s^%s" % (author_name, sup)
            else:
                author += author_name
            
            index += 1


        doi = Utils.get_all_inner_texts(response, ".//span[@class='issue-item__details__doi']")
        source_year = Utils.get_all_inner_texts(response, ".//span[@class='issue-item__details__date']")
        source_year = Utils.regex_extract(source_year, "\((\d+)\)")

        source_volume = Utils.get_all_inner_texts(response, ".//div[@class='cover-details__volume']")
        source_volume = Utils.regex_extract(source_volume, "(\d+)")

        source_issue = Utils.get_all_inner_texts(response, ".//div[@class='cover-details__issue']")
        source_issue = Utils.regex_extract(source_issue, "(\d+)")
        article_abstract = Utils.get_all_inner_texts(response, ".//div[@class='abstract-group']").replace("Abstract", "").strip()
        file_path = response.url
        process_date = Utils.current_date()
        download_path = urlparse.urljoin(response.url, response.xpath("//div[@class='article-action']/a[contains(@aria-label, 'PDF')]/@href").extract_first())
        
        #页面
        page_info = Utils.get_all_inner_texts(response, "//p[@class='page-range']")
        if page_info != "":
            article_fpage = Utils.regex_extract(page_info, "(\d+)-\d+")
            article_lpage = Utils.regex_extract(page_info, "\d+-(\d+)")
            article_page_range = "%s-%s" % (article_fpage, article_lpage)
            try:
                article_page_count = str(int(article_lpage) - int(article_fpage) + 1)
            except Exception as e:
                article_page_count = 0
        else:
            article_fpage = ""
            article_lpage = ""
            article_page_range = ""
            article_page_count = ""


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
            "journal_url" : response.meta["journal_url"],
            "article_fpage" : article_fpage,
            "article_lpage" : article_lpage,
            "article_page_range" : article_page_range,
            "article_page_count" : article_page_count,
        }
