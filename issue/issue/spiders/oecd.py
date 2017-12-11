#!/usr/bin/env python
# -*- coding: utf-8 -*- 
import scrapy
import re
import sys
import urlparse
import sys
import datetime
from utils import Utils
reload(sys)
sys.setdefaultencoding('utf8')

class OECDSpider(scrapy.Spider):
    name = "oecd"

    start_urls = ['http://www.oecd-ilibrary.org/search/advanced']

    def __init__(self, country_file=None, *args, **kwargs):
        super(OECDSpider, self).__init__(*args, **kwargs)
        self.countrys = []
        for line in open(country_file):
            country = line.strip().lower()
            self.countrys.append(country)

        self.download_dir = "oecd_data"
        self.source = "oecd"
        self.source_url = "http://www.oecd-ilibrary.org/"
        print self.countrys

    """check whether country exist in country_option

    @param country country may be like Congo | Repblication of Congo
    """
    def get_country_info(self, country):
        countrys = country.split("|")
        for country_name in countrys:
            country_name = country_name.strip().lower()
            if (country_name in self.exist_countrys):
                return self.exist_countrys[country_name]
        return None

    def parse(self, response):
        #meta = {'theme': 'theme', "country": 'country', 'issue_type': 'issue_type', 'result_count': 11, 'result_url' : 'result_url'}
        #url = "http://www.oecd-ilibrary.org/agriculture-and-food/agricultural-policy-monitoring-and-evaluation-2015/australia_agr_pol-2015-6-en"
        #yield response.follow(url, self.parse_chapter, meta = meta)
        #return
        base_url = "http://www.oecd-ilibrary.org/search?form_name=advanced&value1=*&option1=fullText&operator2=AND&value2=&option2=fullText&operator3=AND&value3=&option3=fullText&option4=year_from&value4=2005&option5=year_to&value5=2016&option24=oecd_imprintIGO&value24=&option6=imprint&value6=http%3A%2F%2Foecd.metastore.ingenta.com%2Fcontent%2Fimprint%2Foecd&option7=lang&option8=lang&option9=lang&operator8=OR&operator9=OR&value7=en&value9=&option25=includeResource&option26=includeResource&option27=includeResource&option28=includeResource&option29=includeResource&option30=includeResource&option31=includeResource&option32=includeResource&option33=includeResource&option34=includeResource&option35=includeResource&option36=includeResource&option37=includeResource&option38=includeResource&operator26=OR&operator27=OR&operator28=OR&operator29=OR&operator30=OR&operator31=OR&operator32=OR&operator33=OR&operator34=OR&operator35=OR&operator36=OR&operator37=OR&operator38=OR&value25=BookSeries&value26=Book&value27=Chapter&value31=Article&value37=WorkingPaperSeries&value38=WorkingPaper&value20=18147364%2C15615537&option20=factbooks&option18=sort&value18=&refinelevel=0&option21=discontinued&value21=true&option22=excludeKeyTableEditions&value22=true&isSelectedIGO=true"
        country_options = response.xpath(".//select[@id='restrictions-country-select']/option")

        #meta= {"theme": "theme", "country": "lizhen", "issue_type": "article"}
        #yield response.follow("http://www.oecd-ilibrary.org/trade/korea_itcs-v2015-5-5-en", self.parse_article, meta = meta)
        #return

        #extract all exist countrys
        self.exist_countrys = {}
        for country_option in country_options:
            country_value = country_option.xpath("./@value").extract_first().strip()
            country_name = country_option.xpath("./text()").extract_first().strip().lower()
            self.exist_countrys[country_name] = [country_name, country_value]

        for country_name in self.countrys:
            country_info = self.get_country_info(country_name)
            if country_info is None:
                print "country_name %s not found" % country_name
                yield {
                    "country" : country_name,
                    "meta_type" : "not_exist",
                }
                continue

            country_name = country_info[0]
            country_value = country_info[1]

            theme_choices = [
                ["%2Fcontent%2Fsubject%2F30", "Agriculture and Food"],
                ["%2Fcontent%2Fsubject%2F40", "Development"],
                ["%2Fcontent%2Fsubject%2F33", "Employment"],
                ["%2Fcontent%2Fsubject%2F78", "Trade"],
                ["%2Fcontent%2Fsubject%2F46", "Urban, Rural and Regional Development"]]

            for theme in theme_choices:
                url = base_url + "&option16=theme&value16=" + theme[0] + "&option17=country&value17=" + country_value
                meta= {"theme": theme[1], "country": country_name}
                yield response.follow(url, self.parse_issue, meta = meta)

    def parse_issue(self, response):
        contents = response.xpath(".//table[contains(@class, 'listing') and contains(@class, 'search-results')]/tbody/tr")
        result_count = response.xpath("//div[@class='top-content']/div[@class='sans']/strong/text()").extract_first()
        if result_count is None or int(result_count.strip()) == 0:
            yield {
                "country" : response.meta['country'],
                "theme" : response.meta['theme'],
                "meta_type" : "no_result",
            }
            return
        for result in contents:
            date = result.xpath("./td[3]/text()").extract_first().strip()
            issue_type = result.xpath("./td[4]/strong/text()").extract_first().strip()
            title = result.xpath("./td[5]/strong/a/@title").extract_first().strip()
            subtitle = result.xpath("./td[5]/strong//span[@class='subTitle']/text()").extract_first()
            if subtitle is not None:
                title = "title : %s" % subtitle
            link = urlparse.urljoin(response.url, result.xpath("./td[5]/strong/a/@href").extract_first().strip()).split(";")[0]

            meta = {
                "theme" : response.meta['theme'],
                "country" : response.meta['country'],
                "issue_type" : issue_type,
                "result_url" : response.url, 
                "result_count" : result_count
            }

            if issue_type == "Book":
                yield response.follow(link, self.parse_book, meta = meta, dont_filter=True)
            elif issue_type == "Chapter":
                yield response.follow(link, self.parse_chapter, meta = meta, dont_filter=True)
            elif issue_type == "Working/Policy Paper":
                yield response.follow(link, self.parse_working, meta = meta, dont_filter=True)
            elif issue_type == "Article":
                yield response.follow(link, self.parse_article, meta = meta, dont_filter=True)
            else:
                raise Exception("unkown type:" + issue_type)
        if 'page' not in response.meta:
            #表示不是分页, 那么就处理一下分页的情况
            page_count = int(int(result_count) / 20) + 1
            current_page = 1
            while current_page < page_count:
                current_page = current_page + 1
                meta = {
                    "page" : current_page,
                    "theme" : response.meta['theme'],
                    "country" : response.meta['country']
                }
                response.meta['page'] = current_page
                page_url = "%s&pageSize=20&page=%d" % (response.url, current_page)
                yield response.follow(page_url, self.parse_issue, meta = meta, dont_filter=True)


    def parse_book(self, response):
        issn_online = self.extract_with_xpath(response, "//*[@id='ui-top']/div[3]/div[2]/dl/dd[1]/text()")
        if issn_online == "":
            issn_online = self.extract_with_xpath(response, "//*[@id='ui-top']/div[2]/div[2]/dl/dd[2]/text()")

        issn_print = self.extract_with_xpath(response, "//*[@id='ui-top']/div[3]/div[2]/dl/dd[2]/text()")
        if issn_print == "":
            issn_print = self.extract_with_xpath(response, "//*[@id='ui-top']/div[2]/div[2]/dl/dd[3]/text()")

        issn = issn_online + ";" + issn_print 

        ui_content = response.xpath("//*[@id='ui-content']").extract()
        if len(ui_content) < 1:
            issue_info =  self.parse_book_with_no_top(response)
        else:
            book_title = self.extract_with_xpath(response, "//*[@id='ui-top']/h1/span/text()")
            book_doi = self.extract_with_xpath(response, "//*[@id='ui-top']//dl[@class='document-identifiers']/dd[3]/a/text()")
            if book_doi.find("http://dx.doi.org") == -1:
                book_doi = self.extract_with_xpath(response, "//*[@id='ui-top']//dl[@class='document-identifiers']/dd[4]/a/text()")

            title = self.extract_with_xpath(response, "//*[@id='ui-content']/div/div[2]/h1/span/text()")
            sub_title = self.extract_with_xpath(response, "//*[@id='ui-content']/div/div[2]/h2/span/text()")
            pdf_link = self.extract_with_xpath(response, "//*[@id='ui-content']/div/div[2]/ul/li/a[@class='pdf']/@href")
            epub_link = self.extract_with_xpath(response, "//*[@id='ui-content']/div/div[2]/ul/li/a[@class='epub']/@href")
            authors = self.extract_with_xpath(response, "//*[@id='ui-content']/div/div[2]/dl/dd/text()")
            date_text = self.extract_with_xpath(response, "//*[@id='ui-content']/div/div[2]/div[4]/div/dl/dd[1]/text()")
            date_obj = Utils.strptime(date_text)
            release_date = date_obj.strftime("%Y-%m-%d")
            release_year = date_obj.strftime("%Y")
            pages = self.extract_with_xpath(response, "//*[@id='ui-content']/div/div[2]/div[4]/div/dl/dd[2]/text()")
            isbn = self.extract_with_xpath(response, "//*[@id='ui-content']/div/div[2]/div[4]/div/dl/dd[3]/text()")
            doi = self.extract_with_xpath(response, "//*[@id='ui-content']/div/div[2]/div[4]/div/dl/dd[4]/a/text()")
            pdf_link = urlparse.urljoin(response.url, pdf_link)
            language = self.extract_with_xpath(response, "//*[@id='ui-content']//div[@class='langdiv langdivnofloat']//span[2]/text()")

            #TODO(lizhen): get abstract

            issue_info = {
                "result_url" : response.meta['result_url'],
                "result_count" : response.meta['result_count'],

                "collection": book_title,
                "collection_url" : book_doi,
                "source" : self.source,
                "source_url" : self.source_url,

                "release_year" : release_year,
                "release_date" : release_date,
                "title" : title,
                "subtitle" : sub_title,
                "dc:contributor" : authors,
                "EISBN" : isbn,
                "doi" : doi,
                "abstracts" : "",
                "subject" : response.meta['theme'],
                "subject_country" : response.meta['country'],
                "access_url" : response.url,
                "pdf_url" : pdf_link,
                'epub_url': epub_link,
                "language_of_work" : language,
                "page" : pages,
                "document_type" : response.meta['issue_type'],
            }

        filename = Utils.doi_to_filname(issue_info['doi']) # book, 一个链接对应一个pdf
        issue_info['filename'] = filename
        issue_info['acquisition_time'] = Utils.current_time()

        yield issue_info

        meta = {}
        pdf_link = issue_info['pdf_url']
        epub_link = issue_info['epub_url']
        if pdf_link != "":
            meta['download_name'] = filename + ".pdf"
            yield response.follow(pdf_link, self.download_file, meta = meta)
        
        if epub_link != "":
            meta['download_name'] = filename + ".epub"
            yield response.follow(epub_link, self.download_file, meta = meta)

    def parse_book_with_no_top(self, response):
        title = self.extract_with_xpath(response, "//div[@class='content']/h1/span/text()")
        sub_title = self.extract_with_xpath(response, "//div[@class='content']/h2/span/text()")
        authors = self.extract_with_xpath(response, "//div[@class='content']/dl[@class='authors']/dd/text()")
        language = self.extract_with_xpath(response, "//div[@class='content']/div[@class='langdiv langdivnofloat']//span[2]/text()")
        pdf_link = self.extract_with_xpath(response, "//div[@class='content']//a[@class='pdf']/@href")
        pdf_link = urlparse.urljoin(response.url, pdf_link)
        epub_link = self.extract_with_xpath(response, "//div[@class='content']//a[@class='epub']/@href")
        epub_link = urlparse.urljoin(response.url, epub_link)
        date_text = self.extract_with_xpath(response, "//div[@class='content']//dl[@class='document-identifiers']/dd[1]/text()")
        date_obj = Utils.strptime(date_text)
        release_date = date_obj.strftime("%Y-%m-%d")
        release_year = date_obj.strftime("%Y")
        pages = self.extract_with_xpath(response, "//div[@class='content']//dl[@class='document-identifiers']/dd[2]/text()")
        isbn = self.extract_with_xpath(response, "//div[@class='content']//dl[@class='document-identifiers']/dd[3]/text()")
        doi = self.extract_with_xpath(response, "//div[@class='content']//dl[@class='document-identifiers']/dd[4]/a/text()")
        abstracts = ""

        issue_info = {
            "result_url" : response.meta['result_url'],
            "result_count" : response.meta['result_count'],

            "source" : self.source,
            "source_url" : self.source_url,

            "release_year" : release_year,
            "release_date" : release_date,
            "title" : title,
            "subtitle" : sub_title,
            "dc:contributor" : authors,
            "EISBN" : isbn,
            "doi" : doi,
            "abstracts" : "",
            "subject" : response.meta['theme'],
            "subject_country" : response.meta['country'],
            "access_url" : response.url,
            "pdf_url" : pdf_link,
            'epub_url': epub_link,
            "language_of_work" : language,
            "page" : pages,
            "document_type" : response.meta['issue_type'],
        }

        return issue_info

    def parse_article(self, response):
        volume_issue = self.extract_with_xpath(response, "//*[@id='breadcrumbs']/span[3]/span[3]/a/span/text()").split(",")
        volumn = volume_issue[0].replace("Volume ", "").strip()
        issue = volume_issue[1].replace("Issue ", "").strip()

        journal = self.extract_with_xpath(response, "//*[@id='breadcrumbs']/span[3]/span[2]/a/span/text()")

        book_title = self.extract_with_xpath(response, "//*[@id='content']/div/div/div/div[2]/div[1]/div[2]/h1/a/span/text()")
        date_text = self.extract_with_xpath(response, "//*[@id='content']/div/div/div/div[2]/div[1]/div[2]/div[2]/div[3]/dl/dd[1]/text()")
        date_obj = Utils.strptime(date_text)
        release_date = date_obj.strftime("%Y-%m-%d")
        release_year = date_obj.strftime("%Y")

        authors = self.extract_with_xpath(response, "//*[@id='ui-content']/div[2]/div[2]/dl/dd/text()")
        language = self.extract_with_xpath(response, "//*[@id='ui-content']//div[@class='langdiv langdivnofloat']//span[2]/text()")
        chapter_title = self.extract_with_xpath(response, "//*[@id='ui-content']/div[2]/div[2]/h1/span/text()")
        pdf_link = self.extract_with_xpath(response, "//*[@id='ui-content']/div[2]/div[2]/ul/li/a[@class='pdf']/@href")
        epub_link = self.extract_with_xpath(response, "//*[@id='ui-content']/div[2]/div[2]/ul/li/a[@class='epub']/@href")
        chapter_page = self.extract_with_xpath(response, "//*[@id='ui-content']/div[2]/div[2]/div[4]/dl/dd[3]/text()")
        doi = self.extract_with_xpath(response, "//*[@id='ui-content']/div[2]/div[2]/div[4]/dl/dd[4]/a/text()")

        pdf_link = urlparse.urljoin(response.url, pdf_link)
        filename = Utils.doi_to_filname(doi) # 一个chapter对应一个pdf

        issue_info = {
            "result_url" : response.meta['result_url'],
            "result_count" : response.meta['result_count'],
            "filename" : filename,
            "acquisition_time" : Utils.current_time(),

            "collection": journal,
            "collection_url" : doi,
            "source" : self.source,
            "source_url" : self.source_url,

            "release_year" : release_year,
            "release_date" : release_date,
            "title" : chapter_title,
            "dc:contributor" : authors,
            "doi" : doi,
            "volumn" : volumn,
            "issue" : issue,
            "abstracts" : "",
            "subject" : response.meta['theme'],
            "subject_country" : response.meta['country'],
            "access_url" : response.url,
            "pdf_url" : pdf_link,
            'epub_url': epub_link,
            "language_of_work" : language,
            "page" : chapter_page,
            "document_type" : response.meta['issue_type'],
        }
        yield issue_info

        meta = {}
        if pdf_link != "":
            meta['download_name'] = filename + ".pdf"
            yield response.follow(pdf_link, self.download_file, meta = meta)
        
        if epub_link != "":
            meta['download_name'] = filename + ".epub"
            yield response.follow(epub_link, self.download_file, meta = meta)


    def parse_working(self, response):
        book_title = self.extract_with_xpath(response, "//*[@id='ui-top']/h3/a/span/text()")
        issn = self.extract_with_xpath(response, "//*[@id='ui-top']/div[2]/div/dl/dd[1]/text()").replace(" (online)", "")
        doi = self.extract_with_xpath(response, "//*[@id='ui-top']/div[2]/div/dl/dd[2]/a/@href")
        chapter_title = self.extract_with_xpath(response, "//*[@id='ui-content']/div/div[2]/h1/span/text()")
        language = self.extract_with_xpath(response, "//*[@id='ui-content']//div[@class='langdiv langdivnofloat']//span[2]/text()")
        pdf_link = self.extract_with_xpath(response, "//*[@id='ui-content']/div/div[2]/ul/li/a[@class='pdf']/@href")
        epub_link = self.extract_with_xpath(response, "//*[@id='ui-content']/div/div[2]/ul/li/a[@class='epub']/@href")
        authors = ";".join(response.xpath("//*[@id='ui-content']/div/div[2]/dl/dd[1]/text()").extract())
        authors = authors.replace(",", "")
        date_text = self.extract_with_xpath(response, "//*[@id='ui-content']/div/div[2]/div[4]/dl/dd[1]/text()")
        date_obj = Utils.strptime(date_text)
        release_date = date_obj.strftime("%Y-%m-%d")
        release_year = date_obj.strftime("%Y")

        no = self.extract_with_xpath(response, "//*[@id='ui-content']/div/div[2]/div[4]/dl/dd[2]/dl/dd/text()")
        chapter_page = self.extract_with_xpath(response, "//*[@id='ui-content']/div/div[2]/div[4]/dl/dd[3]/text()")
        chapter_doi = self.extract_with_xpath(response, "//*[@id='ui-content']/div/div[2]/div[4]/dl/dd[4]/a/@href")
        keywords = "".join(response.xpath("//*[@id='ui-content']/div/div[2]/div[7]/dl/dd/text()").extract()).replace("\n", "")
        pdf_link = urlparse.urljoin(response.url, pdf_link)
        epub_link = urlparse.urljoin(response.url, epub_link)
        
        filename = Utils.doi_to_filname(chapter_doi) # working, 一个链接对应一个pdf

        issue_info = {
            "result_url" : response.meta['result_url'],
            "result_count" : response.meta['result_count'],
            "filename" : filename,
            "acquisition_time" : Utils.current_time(),

            "collection": book_title,
            "collection_url" : doi,
            "source" : self.source,
            "source_url" : self.source_url,

            "release_year" : release_year,
            "release_date" : release_date,
            "eissn" : issn,
            "title" : chapter_title,
            "dc:contributor" : authors,
            "doi" : chapter_doi,
            "issue" : no,
            "abstracts" : "",
            "keywords" : keywords,
            "subject" : response.meta['theme'],
            "subject_country" : response.meta['country'],
            "access_url" : response.url,
            "pdf_url" : pdf_link,
            'epub_url': epub_link,
            "language_of_work" : language,
            "page" : chapter_page,
            "document_type" : response.meta['issue_type'],
        }

        yield issue_info

        meta = {}
        if pdf_link != "":
            meta['download_name'] = filename + ".pdf"
            yield response.follow(pdf_link, self.download_file, meta = meta)
        
        if epub_link != "":
            meta['download_name'] = filename + ".epub"
            yield response.follow(epub_link, self.download_file, meta = meta)

    def parse_chapter(self, response):
        book_title = self.extract_with_xpath(response, "//*[@id='content']/div/div/div/div[2]/div[1]/div[2]/h1/a/span/text()")
        date = self.extract_with_xpath(response, "//*[@id='content']/div/div/div/div[2]/div[1]/div[2]/div[3]/div[3]/dl/dd[1]/text()")
        book_doi = self.extract_with_xpath(response, "//*[@id='content']/div/div/div/div[2]/div[1]/div[2]/div[3]/div[3]/dl/dd[2]/a/text()")

        chapter_title = self.extract_with_xpath(response, "//*[@id='ui-content']/div[2]/div[2]/h1/span/text()")
        language = self.extract_with_xpath(response, "//*[@id='ui-content']//div[@class='langdiv langdivnofloat']//span[2]/text()")
        pdf_link = self.extract_with_xpath(response, "//*[@id='ui-content']/div[2]/div[2]/ul/li/a[@class='pdf']/@href")
        epub_link = self.extract_with_xpath(response, "//*[@id='ui-content']/div[2]/div[2]/ul/li/a[@class='epub']/@href")
        authors = self.extract_with_xpath(response, "//div[@class='authors']//dd/text()")
        date_text = self.extract_with_xpath(response, "//*[@id='content']/div/div/div/div[2]/div[1]/div[2]/div[3]/div[3]/dl/dd[1]/text()")
        date_obj = Utils.strptime(date_text)
        release_date = date_obj.strftime("%Y-%m-%d")
        release_year = date_obj.strftime("%Y")
        isbn = self.extract_with_xpath(response, "//*[@id='ui-content']/div/div[2]/div[4]/div/dl/dd[3]/text()")
        abstracts = self.extract_with_xpath(response, "//div[@class='abstract']//p/text()")
        
        chapter_page = self.extract_with_xpath(response, "//*[@id='ui-content']//dl[@class='document-identifiers']/dd[2]/text()")
        chapter_doi = self.extract_with_xpath(response, "//*[@id='ui-content']//dl[@class='document-identifiers']/dd[3]/a/text()")
        if chapter_doi == "":
            chapter_doi = self.extract_with_xpath(response, "//*[@id='ui-content']//dl[@class='document-identifiers']/dd[2]/a/text()")

        filename = Utils.doi_to_filname(chapter_doi) # 一个chapter对应一个pdf

        pdf_link = urlparse.urljoin(response.url, pdf_link)

        issue_info = {
            "result_url" : response.meta['result_url'],
            "result_count" : response.meta['result_count'],
            "filename" : filename,
            "acquisition_time" : Utils.current_time(),

            "collection": book_title,
            "collection_url" : book_doi,
            "source" : self.source,
            "source_url" : self.source_url,

            "release_year" : release_year,
            "release_date" : release_date,
            "title" : chapter_title,
            "doi" : chapter_doi,
            "abstracts" : abstracts,
            "subject" : response.meta['theme'],
            "subject_country" : response.meta['country'],
            "access_url" : response.url,
            "pdf_url" : pdf_link,
            'epub_url': epub_link,
            "language_of_work" : language,
            "page" : chapter_page,
            "document_type" : response.meta['issue_type'],
        }

        yield issue_info

        meta = {}
        if pdf_link != "":
            meta['download_name'] = filename + ".pdf"
            yield response.follow(pdf_link, self.download_file, meta = meta)
        
        if epub_link != "":
            meta['download_name'] = filename + ".epub"
            yield response.follow(epub_link, self.download_file, meta = meta)

    def download_file(self, response):
        issue_info = response.meta
        pdf_save_path = "%s/%s" % (self.download_dir, issue_info['download_name'])
        with open(pdf_save_path, "wb") as f:
            f.write(response.body)
        f.close()

    def extract_with_xpath(self, root, xpath_str, default_value = ""):
        try:
            result = root.xpath(xpath_str).extract_first().strip()
        except Exception as e:
            result = default_value

        return result

