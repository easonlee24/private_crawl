#coding=utf-8
# 2019-05-20
# Scielo期刊的爬虫，支持续采

import scrapy
import urlparse
from utils import Utils
from scrapy.http.request import Request
import re
import json
import urlparse


class Scielo(scrapy.Spider):
    name = "scielo"
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
        with open(self.url_file, "rb") as f:
            for line in f:
                meta = {"journal_url": line.strip()}
                url = line.strip().replace("sci_serial", "sci_issues")
                yield Request(url, self.crawl_homepage, meta = meta, dont_filter=True)

    def crawl_homepage(self, response):
        journals = response.xpath("//div[@class='content']/table[2]//tr//tr")
        journal_index = 0
        for journal in journals:
            if journal_index == 0:
                #第一个tr是标题栏
                journal_index += 1
                continue

            year = Utils.extract_text_with_xpath(journal, ".//font/b")
            if year < self.start_year:
                break
            volume =  Utils.extract_all_text_with_xpath(journal.xpath(".//td[@align='middle']")[0], ".//font")
            for issue_elem in journal.xpath("./td[@align='middle']//a"):
                url = issue_elem.xpath("./@href").extract_first().strip()
                issue = issue_elem.xpath("./text()").extract_first().strip()
                meta = {"volume": volume, "issue": issue, "journal_url": response.meta["journal_url"], "year": year}
                yield Request(url, self.crawl_journal, meta = meta)

    def crawl_journal(self, response):
        links = response.xpath(".//a/@href").extract()
        pattern1 = ".*script=sci_arttext&pid=.*&lng=en&nrm=iso&tlng=en$"
        pattern2 = ".*script=sci_arttext&pid=.*&lng=en&nrm=iso&tlng=pt$"
        for link in links:
            if re.match(pattern1, link) or re.match(pattern2, link):
                meta = {"volume": response.meta['volume'], "issue": response.meta["issue"],
                        "journal_url": response.meta["journal_url"], "year": response.meta["year"]}
                yield Request(link, self.crawl_issue_info, meta = meta)

    def crawl_issue_info(self, response):
        download_path = self.get_pdf(response)
        article_title = self.get_title(response)
        article_abstract = self.get_abstract(response)
        keyword = self.get_keyword(response)

        authors = self.get_author(response)
        author_sups = self.get_author_sup(response)
        #输出作者
        index = 0
        author = ""
        for author_elem in authors:
            author_name = author_elem
            if index != 0:
                author += ";"

            # 有可能没有作者机构
            if len(author_sups) < index + 1:
                author += author_name
            else:
                author += "%s^%s" % (author_name, author_sups[index])
            index += 1


        #作者机构
        affiliations = self.get_author_affiliation(response)
        auth_institution = ""
        index = 0
        for affiliation in affiliations:
            if index != 0:
                auth_institution += ";"
            auth_institution += "%s^%s" % (affiliation, index + 1)
            index += 1

        source_year = Utils.regex_extract(Utils.extract_all_text_with_xpath(response, "h3"), ".*(\\d{4})$")
        doi = Utils.extract_all_text_with_xpath(response, "//h4[@id='doi']")

        yield {
            "article_title": article_title,
            "author": author,
            "auth_institution": auth_institution,
            "doi": doi,
            "source_year": source_year,
            "source_volume": response.meta['volume'],
            "source_issue": response.meta['issue'],
            "article_abstract": article_abstract,
            "keyword": keyword,
            "file_path": response.url,
            "download_path": download_path,
            "process_date": Utils.current_date(),
            "volume": response.meta["volume"],
            "issue": response.meta["issue"],
            "journal_url": response.meta["journal_url"],
            "source_year": response.meta["year"]
        }


    def get_pdf(self, response):
        try:
            pdf_link_elem = Utils.select_element_by_content(response, "//*[@id='toolBox']/div/ul/li/a", "English (pdf)|Portuguese (pdf)")
        except Exception as e:
            return ""
        pdf_link = pdf_link_elem.xpath("@href").extract_first()
        pdf_link = urlparse.urljoin(response.url, pdf_link)
        return pdf_link

    def get_title(self, response):
        #title也有多种情况..醉了
        title = response.xpath("//p[@class='trans-title']/text()").extract_first()
        if title is None:
            title = response.xpath("//p[@class='title']/text()").extract_first()
            if title is None:
                try:
                    title_elem = response.xpath("//div[contains(@class, 'index')]//p[@align='CENTER']")[0]
                    title = " ".join(title_elem.xpath(".//text()").extract())
                except Exception as e:
                    top_a_elem = response.xpath("//div[contains(@class, 'index')]//a[@name='top']")
                    title = top_a_elem.xpath("./..//b/text()").extract_first()
                    if title is None:
                        title_elem = response.xpath("//div[contains(@class, 'index')]/p")[2]
                        title = " ".join(title_elem.xpath(".//text()").extract())

        print "title is %s" % title
        return Utils.format_text(title)

    def get_abstract(self, response):
        try:
            abstract_elem = Utils.select_element_by_content(response, "//div[contains(@class, 'index')]//p", "ABSTRACT|Abstract")
            abstract_text = Utils.get_all_inner_texts(abstract_elem, "./following-sibling::p[1]").replace("Abstract:", "").strip()
            return abstract_text
        except Exception as e:
            return ""

    def get_keyword(self, response):
        try:
            keyword_elem = Utils.select_element_by_content(response, "//div[contains(@class, 'index')]//p", "Keywords|Index terms|Key words")
            keyword_text = ";".join(keyword_elem.xpath(".//text()").extract()).replace("Keywords:", "").replace("Key words", "").strip(";")
        except Exception as e:
            return ""
        return keyword_text

    def get_author(self, response):
        #有两种格式的author
        try:
            author = response.xpath("//div[@class='autores']/p[@class='author']/span[@class='author-name']/text()").extract()
            if len(author) == 0:
                sup_elem = response.xpath("//div[contains(@class, 'index')]/p//sup")[0]
                author_elem = sup_elem.xpath('./..')
                tag_name = author_elem.xpath('name()').extract_first()
                while tag_name != "p":
                    author_elem = author_elem.xpath('./..')
                    tag_name = author_elem.xpath('name()').extract_first()

                author_raw_text = author_elem.extract()
                author = author_raw_text
        except Exception as e:
            return ""

        return author

    def get_author_sup(self, response):
        #有两种格式的author_sup
        try:
            author_sup = response.xpath("//div[@class='autores']/p[@class='author']/sup/a/text()").extract()
            if len(author_sup) == 0:
                i = 0
                num = 1 #len(response.xpath("//div[contains(@class, 'index')]/p//sup"))
                sup_elem = response.xpath("//div[contains(@class, 'index')]/p//sup")[0]
                author_elem = sup_elem.xpath("./..")
                author_sup = author_elem.xpath("./sup/text()").extract()
        except Exception as e:
            return ""

        return author_sup

    def get_author_affiliation(self, response):
        #有两种格式的author_affiliation
        try:
            author_aff = []
            elems = response.xpath("//p[@class='aff']")
            for elem in elems:
                txt = " ".join(elem.xpath(".//text()").extract()).strip().replace("\n", "")
                txt = ' '.join(txt.split()) #remove multi space
                author_aff.append(txt)

            if len(author_aff) == 0:
                sup_elem = response.xpath("//div[contains(@class, 'index')]/p//sup")[-1]
                author_raw_text = sup_elem.xpath("./..").extract()
                author_aff = author_raw_text
                print "author affiliation is :%s" % author_aff
        except Exception as e:
            return  ""
        return author_aff
