#!/usr/bin/env python
# -*- coding: utf-8 -*- 
import scrapy
import re
import sys
import urlparse
import sys
reload(sys)
sys.setdefaultencoding('utf8')

class IMFSpider(scrapy.Spider):
    name = "imf"

    #start_urls = ['http://www.elibrary.imf.org/browse?freeFilter=false&fromDate=2005&pageSize=100&sort=datedescending&t_8=urn%3Aeng&toDate=2016']
    start_urls = ['https://www.elibrary.imf.org/browse?fromDate=2019&pageSize=10&sort=titlesort&t_6=urn%3A10%2FBUS000000&t_8=urn%3Aeng&toDate=2020']

    country_url = re.compile(".*/browse\?fromDate=\d+&pageSize=100&sort=datedescending&t_5=.*&t_8=urn%3Aeng&toDate=2016$")
    topic_url = re.compile(".*/browse\?fromDate=\d+&pageSize=100&sort=datedescending&t_5=.*&t_6=.*&t_8=urn%3Aeng&toDate=2016")

    def __init__(self, country_file=None, *args, **kwargs):
        super(IMFSpider, self).__init__(*args, **kwargs)
        self.countrys = set(line.strip().lower() for line in open(country_file))
        print self.countrys

        self.focus_topics = ['Economics - Macroeconomics', 'Environmental Economics', 'Global Warming and Climate Change', 'Environmental - Water Supply', 'Food Science']

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
        #response.meta['country'] = 'country'
        #response.meta['result_url'] = 'result_url'
        #response.meta['topic'] = 'topic'
        #response.meta['keywords'] = 'keywords'
        #response.meta['issue_type'] = 'issue_type'
        #response.meta['result_total'] = 'result_total'
        #yield response.follow(response.url, self.parse_book, meta = response.meta)
        #return
        links = response.xpath("//div[@id='refineCountries']//a")
        self.exist_countrys = {}
        for link in links:
            url = link.xpath("@href").extract_first()
            text = ''.join(link.xpath("text()").extract()).strip()
            if url is None or text is None:
                continue
            url = url.strip()
            text = text.strip().lower()
            if self.country_url.match(url):
               self.exist_countrys[text] = [text ,url]
               # this country we dont need, just pass
               #print "get link not country: %s, country: %s" % (url, text)

        for country_name in self.countrys:
            country_info = self.get_country_info(country_name)
            if country_info is None:
                continue
            meta = {"country" : country_info[0]}
            yield response.follow(country_info[1], self.parse_topic,  meta = meta)

    def parse_topic(self, response):
        links = response.xpath("//div[@id='refineTopics']//a")
        for link in links:
            url = link.xpath("@href").extract_first()
            text = ''.join(link.xpath("text()").extract()).strip()
            if url is None or text is None:
                continue
            url = url.strip()
            text = text.strip()
            if self.topic_url.match(url):
                if text in self.focus_topics:
                    meta = response.meta
                    meta['topic'] = text
                    yield response.follow(url, self.parse_issue, meta = meta)

    def parse_issue(self, response):
        contents = response.xpath("//div[@id='searchContent']/div")
        article_types = ["article", "journal issue"]
        book_types = ["chapter", "front matter", "book", "back matter"]
        result_total = self.extract_with_xpath(response, "//*[@id='resultTotal']/text()")
        for content in contents:
            keywords = content.xpath("./h3[@class='keyword']/em/a/text()").extract()
            if keywords is not None:
                keywords = ",".join(keywords).encode('utf-8').strip(',')


            #keywords cannot get in issue home page, so get is in result page
            response.meta['keywords'] = keywords
            response.meta['result_url'] = response.url
            response.meta['result_total'] = result_total

            issue_type = content.xpath(".//div[@class='typeText']/text()").extract_first().strip()
            issue_link = content.xpath("./h2[@class='itemTitle']/a/@href").extract_first()

            response.meta['issue_type'] = issue_type
            if (issue_type.lower() in article_types):
                #this type got volume and issue
                yield response.follow(issue_link, self.parse_article, dont_filter = True, meta = response.meta)
            elif (issue_type.lower() in book_types):
                yield response.follow(issue_link, self.parse_book, dont_filter = True,  meta = response.meta)
            else:
                raise Exception("unkonw type: %s" % issue_type)
        
        #get other pages
        page_links = response.xpath("//*[@id='resultsBarTop']/div[2]/div/a/@href").extract()
        for page_link in page_links:
            yield response.follow(page_link, self.parse_issue, meta = response.meta)

    def parse_article(self, response):
        source_title = self.extract_with_xpath(response, "//*[@id='pagetitle']/text()")
        volume_issue = self.extract_with_xpath(response, "//*[@id='articleInfo']/dd[1]/text()").split('/')
        volume = volume_issue[0]
        issue = volume_issue[1]
        series = self.extract_with_xpath(response, "//*[@id='articleInfo']/dd[2]/text()")
        authors = self.extract_with_xpath(response, "//*[@id='articleInfo']/dd[3]/text()")
        publisher = self.extract_with_xpath(response, "//*[@id='articleInfo']/dd[4]/text()")
        publish_date = self.extract_with_xpath(response, "//*[@id='articleInfo']/dd[5]/text()")
        doi = self.extract_with_xpath(response, "//*[@id='articleInfo']/dd[6]/text()")
        isbn = self.extract_with_xpath(response, "//*[@id='articleInfo']/dd[7]/text()")
        issn = self.extract_with_xpath(response, "//*[@id='articleInfo']/dd[8]/text()")
        page = self.extract_with_xpath(response, "//*[@id='articleInfo']/dd[9]/text()")
        abstract = self.extract_with_xpath(response, "//*[@id='mainContent']/section/div[2]/div[3]/text/text()")
        subtitle = self.extract_with_xpath(response, "//*[@id='toc']/ul/li[@class='current']/a/text()")

        pdf_link = self.extract_with_xpath(response, "//*[@id='mainContent']/section[1]/div[1]/div/div/ul/li[class='pdf']/a/@href")
        epub_link = self.extract_with_xpath(response, "//*[@id='mainContent']/section[1]/div[1]/div/div/ul/li[class='epub']/a/@href")

        yield {
            'source_title' : source_title,
            'volume' : volume,
            'issue' : issue,
            'series' : series,
            'author' : authors,
            'publiser' : publisher,
            'publish_date' : publish_date,
            'doi' : doi,
            'isbn' : isbn,
            'issn' : issn,
            'page' : page,
            'abstract' : abstract,
            'subtitle' : subtitle,
            'pdf_link' : pdf_link,
            'epub_link' : epub_link,
            'keywords' : response.meta['keywords'],
            'country' : response.meta['country'],
            'issue_type' : response.meta['issue_type'],
            'topic' : response.meta['topic'],
            'result_url' : response.meta['result_url'],
            'issue_url' : response.url,
            'result_total' : response.meta['result_total']
        }

    def parse_book(self, response):
        source_title = self.extract_with_xpath(response, "//*[@id='pagetitle']/text()")
        series = self.extract_with_xpath(response, "//*[@id='articleInfo']/dd[1]/text()")
        authors = self.extract_with_xpath(response, "//*[@id='articleInfo']/dd[2]/text()")
        publisher = self.extract_with_xpath(response, "//*[@id='articleInfo']/dd[3]/text()")
        publish_date = self.extract_with_xpath(response, "//*[@id='articleInfo']/dd[4]/text()")
        doi = self.extract_with_xpath(response, "//*[@id='articleInfo']/dd[5]/text()")
        isbn = self.extract_with_xpath(response, "//*[@id='articleInfo']/dd[6]/text()")
        page = self.extract_with_xpath(response, "//*[@id='articleInfo']/dd[8]/text()")
        abstract = self.extract_with_xpath(response, "//*[@id='mainContent']/section/div[2]/div[3]/text/text()")

        subtitle = self.extract_with_xpath(response, "//*[@id='toc']/ul/li[@class='current']/a/text()")

        pdf_link = self.extract_with_xpath(response, "//*[@id='mainContent']/section/div[1]/div/div/ul/li[@class='pdf']/a/@href")
        epub_link = self.extract_with_xpath(response, "//*[@id='mainContent']/section/div[1]/div/div/ul/li[@class='epub']/a/@href")

        yield {
            'source_title' : source_title,
            'volume' : "",
            'issue' : "",
            'series' : series,
            'author' : authors,
            'publiser' : publisher,
            'publish_date' : publish_date,
            'doi' : doi,
            'isbn' : isbn,
            'issn' : "",
            'page' : page,
            'abstract' : abstract,
            'subtitle' : subtitle,
            'pdf_link' : pdf_link,
            'epub_link' : epub_link,
            'keywords' : response.meta['keywords'],
            'country' : response.meta['country'],
            'issue_type' : response.meta['issue_type'],
            'topic' : response.meta['topic'],
            'result_url' : response.meta['result_url'],
            'issue_url': response.url,
            'result_total' : response.meta['result_total']
        }

    def encode(self, value):
        if value is not None:
            return value.encode('utf-8')

        return value

    def extract_with_xpath(self, root, xpath_str, default_value = ""):
        try:
            result = root.xpath(xpath_str).extract_first().strip()
        except Exception as e:
            result = default_value

        return result

