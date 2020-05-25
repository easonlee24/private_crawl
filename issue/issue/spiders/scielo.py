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
    def __init__(self, url_file=None, start_year=None, revised = None):
        self.url_file = url_file
        if start_year is None:
            self.start_year = "2018"
        else:
            self.start_year = start_year

        if revised is not None and revised == "True":
            self.revised = True
        else:
            self.revised = False

    def start_requests(self):
        #url = "http://www.scielo.br/scielo.php?script=sci_arttext&pid=S0103-507X2019000100106&lng=en&nrm=iso&tlng=pt"
        #meta = {"volume": "42", "issue": "42", "journal_url": "journal_url", "year": 1}
        #yield Request(url, self.crawl_issue_info, meta = meta)
        #return

        with open(self.url_file, "rb") as f:
            for line in f:
                if self.revised:
                    #元数据校订
                    elem = json.loads(line.strip())
                    meta = {"journal_url": elem["journal_url"], "volume": elem["source_volume"], "issue": elem["source_issue"], "year": elem["source_year"]}
                    url = elem["file_path"]
                    yield Request(url, self.crawl_issue_info, meta = meta, dont_filter=True)

                else:
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

            elems = affiliation.split(' ')
            auth_sup = elems[0]
            auth_name = " ".join(elems[1:])
            auth_institution += "%s^%s" % (auth_name, auth_sup)
            index += 1

        source_year = Utils.regex_extract(Utils.extract_all_text_with_xpath(response, "h3"), ".*(\\d{4})$")
        doi = Utils.extract_all_text_with_xpath(response, "//h4[@id='doi']")

        # volume有可能为空，在这里补充一下
        volume = response.meta['volume']
        if volume == '':
            meta_info = response.xpath("//h3/text()").extract_first()
            volume = Utils.regex_extract(meta_info, "vol.(\d+)")

        # issue可能是ahead of print, 尝试修正一下。
        # volume和issue相同时，表示上一层爬错了。修正版本时需要重爬一下。
        issue = response.meta['issue']
        if issue == 'ahead of print' or volume == issue:
            meta_info = response.xpath("//h3/text()").extract_first()
            issue = Utils.regex_extract(meta_info, "no.(\d+)")

        yield {
            "article_title": article_title,
            "author": author,
            "auth_institution": auth_institution,
            "doi": doi,
            "source_year": source_year,
            "source_volume": volume,
            "source_issue": issue,
            "article_abstract": article_abstract,
            "keyword": keyword,
            "file_path": response.url,
            "download_path": download_path,
            "process_date": Utils.current_date(),
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
        title = Utils.get_all_inner_texts(response, "//p[@class='trans-title']")
        if title == "":
            title = Utils.get_all_inner_texts(response, "//p[@class='title']")
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

        return Utils.format_text(title)

    def get_abstract(self, response):
        try:
            elems = response.xpath("//div[@class='abstract']/div[@class='section']")
            abstract_text = ""
            if elems is not None and len(elems) > 0:
                for elem in elems:
                    abstract_text += " ".join(elem.xpath(".//text()").extract()) + "\n"
            else:
                try:
                    abstract_elem = Utils.select_element_by_content(response, "//div[contains(@class, 'index')]//p", "ABSTRACT|Abstract")
                    abstract_text = Utils.get_all_inner_texts(abstract_elem, "./following-sibling::p[1]").replace("Abstract:", "").strip()
                except Exception as e:
                    abstract_text = Utils.get_all_inner_texts(response, "//div[@class='abstract']").strip()
            try:
                #把关键词去掉
                abstract_text = abstract_text[0: abstract_text.index("Descritores:")]
            except Exception as e:
                pass
            return abstract_text
        except Exception as e:
            return ""

    def get_keyword(self, response):
        try:
            keyword_elem = Utils.select_element_by_content(response, "//div[contains(@class, 'index')]//p", "Keywords|Index terms|Key words|PALAVRAS-CHAVE|Key-Words|Descritores")
            keyword_text = ";".join(keyword_elem.xpath(".//text()").extract()).replace("Keywords:", "").replace("Key words", "").replace("Key-Words", "").replace("PALAVRAS-CHAVE", "").replace("Descritores", "").replace("Index terms", "").strip(";")
            keyword_text = ";".join([i.strip() for i in keyword_text.split(";") if i.strip() != "" and i.strip() != ":"])
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
            #author_sup = response.xpath("//div[@class='autores']/p[@class='author']/sup/a/text()").extract()
            elems = response.xpath("//div[@class='autores']/p[@class='author']")
            author_sup = []
            for elem in elems:
                sup = ",".join(elem.xpath("./sup/a/text()").extract())

                author_sup.append(sup)

            if len(author_sup) == 0:
                i = 0
                num = 1 #len(response.xpath("//div[contains(@class, 'index')]/p//sup"))
                sup_elem = response.xpath("//div[contains(@class, 'index')]/p//sup")[0]
                author_elem = sup_elem.xpath("./..")
                author_sup = author_elem.xpath("./sup/text()").extract()
        except Exception as e:
            print "error......."
            return []


        format_author_sup = []
        for sup in author_sup:
            elems = sup.split(",")
            format_elems = []
            for elem in elems:
                try:
                    text = Utils.transform_roman_num2_alabo(elem)
                except Exception as e:
                    text = elem
                text = str(text)
                if text >= 'a' and text <= 'z':
                    text = ord(text) - ord('a') + 1
                format_elems.append(str(text))
            author_sup = ",".join(format_elems)
            if author_sup == "*":
                author_sup = 1
            elif author_sup == "**":
                author_sup = 2
            elif author_sup == "***":
                author_sup = 3
            elif author_sup == "****":
                author_sup = 4
            elif author_sup == "*****":
                author_sup = 5
            elif author_sup == "******":
                author_sup = 6

            format_author_sup.append(author_sup)
                
        return format_author_sup

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

            format_author_aff = []
            for elem in author_aff:
                if elem.startswith("*****"):
                    elem = elem.replace("*", "5")
                elif elem.startswith("****"):
                    elem = elem.replace("****", "4")
                elif elem.startswith("***"):
                    elem = elem.replace("***", "3")
                elif elem.startswith("**"):
                    elem = elem.replace("**", "2")
                elif elem.startswith("*"):
                    elem = elem.replace("*", "1")

                format_author_aff.append(elem)

        except Exception as e:
            return  ""
        return format_author_aff
