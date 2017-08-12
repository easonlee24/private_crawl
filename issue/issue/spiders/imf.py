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

    start_urls = ['http://www.elibrary.imf.org/browse?freeFilter=false&fromDate=2015&pageSize=100&sort=datedescending&t_8=urn%3Aeng&toDate=2016']
    #start_urls = ['http://www.elibrary.imf.org/browse?freeFilter=false&fromDate=2015&pageSize=100&sort=datedescending&t_8=urn%3Aeng&toDate=2016&redirect=true']

    country_url = re.compile(".*/browse\?fromDate=\d+&pageSize=100&sort=datedescending&t_5=.*&t_8=urn%3Aeng&toDate=2016$")
    topic_url = re.compile(".*/browse\?fromDate=\d+&pageSize=100&sort=datedescending&t_5=.*&t_6=.*&t_8=urn%3Aeng&toDate=2016")

    def __init__(self, country_file=None, *args, **kwargs):
        super(IMFSpider, self).__init__(*args, **kwargs)
        self.countrys = set(line.strip().lower() for line in open(country_file))
        print self.countrys

    def parse(self, response):
        links = response.xpath("//div[@id='refineCountries']//a")
        for link in links:
            url = link.xpath("@href").extract_first()
            text = ''.join(link.xpath("text()").extract()).strip()
            if url is None or text is None:
                continue
            url = url.strip()
            text = text.strip().lower()
            if self.country_url.match(url):
                if text not in self.countrys:
                    # this country we dont need, just pass
                    #print "get link not country: %s, country: %s" % (url, text)
                    continue

                meta = {"country" : text}
                yield response.follow(url, self.parse_topic, meta = meta)

    def parse_topic(self, response):
        links = response.xpath("//div[@id='refineTopics']//a")
        for link in links:
            url = link.xpath("@href").extract_first()
            text = ''.join(link.xpath("text()").extract()).strip()
            if url is None or text is None:
                continue
            url = url.strip()
            text = text.strip().lower()
            if self.topic_url.match(url):
                meta = response.meta
                meta['topic'] = text
                yield response.follow(url, self.parse_issue, meta = meta)

    def parse_issue(self, response):
        contents = response.xpath("//div[@id='searchContent']/div")
        article_types = ["article", "journal issue"]
        book_types = ["chapter", "front matter", "book", "back matter"]
        for content in contents:
            issue_type = content.xpath(".//div[@class='typeText']/text()").extract_first().strip()
            if (issue_type.lower() in article_types):
                #this type got volume and issue
                volume_issue = content.xpath("./h3[@class='author']/em/text()").extract_first().split('/')
                volume = volume_issue[0]
                issue = volume_issue[1]
            elif (issue_type.lower() in book_types):
                volume = "None"
                issue = "None"
            else:
                self.logger.info("get an unkonw type:" + issue_type + ", link:" + response.url)
                print book_types
                sys.exit(0)

            title = content.xpath("./h2[@class='itemTitle']/a/text()").extract_first().encode('utf-8').strip().replace('\xbb', '').replace('\xc2', '')

            issue_link = content.xpath("./h2[@class='itemTitle']/a/@href").extract_first()
            issue_link = urlparse.urljoin(response.url, issue_link)

            author = content.xpath("./h3[@class='author'][2]/em/text()").extract_first()
            if author is not None:
                author = author.replace("\n", "").strip()
                author = re.subn(" +", " ", author)[0]

            publiser = content.xpath("./h3[@class='publisher']/em/text()").extract_first()
            publicationDate = content.xpath("./h3[@class='publicationDate']/em/text()").extract_first()
            if publicationDate is not None:
                publicationDate = publicationDate.replace("\n", "").strip()
                publicationDate = re.subn(" +", " ", publicationDate)[0]

            doi = content.xpath("./h3[@class='doi']/em/text()").extract_first()
            isbn = content.xpath("./h3[@class='isbn']/em/text()").extract_first()
            source = content.xpath("./h3[@class='source']/em/a/text()").extract_first()
            if source is not None:
                source = source.encode('utf-8')

            keywords = content.xpath("./h3[@class='keyword']/em/a/text()").extract()
            if keywords is not None:
                keywords = ",".join(keywords).encode('utf-8').strip(',')

            yield {
                'title' : self.encode(title),
                'issue_link' : self.encode(issue_link),
                'issue_type' : self.encode(issue_type),
                'volume' : self.encode(volume),
                'issue' : self.encode(issue),
                'author' : self.encode(author),
                'publiser' : self.encode(publiser),
                'publicationDate' : self.encode(publicationDate),
                'doi' : self.encode(doi),
                'isbn' : self.encode(isbn),
                'source' : self.encode(source),
                'keywords' : self.encode(keywords),
                'from' : self.encode(response.url),
                'country' : response.meta['country'],
                'topic' : response.meta['topic']
            }

    def encode(self, value):
        if value is not None:
            return value.encode('utf-8')

        return value

    def extract_with_xpath(self, root, xpath_str, default_value = ""):
        try:
            result = content.xpath(xpath_str).extract_first().strip()
        except Exception as e:
            result = default_value

        return result

