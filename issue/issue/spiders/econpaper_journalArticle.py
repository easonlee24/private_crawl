#!/usr/bin/env python
# -*- coding: utf-8 -*-
import scrapy
import urlparse
import sys
from scrapy.http.request import Request

reload(sys)
sys.setdefaultencoding('utf8')


class econpaper_journalArticle(scrapy.Spider):
    name = "econpaper_journalArticle"
    urls = []

    def __init__(self, urlPath=None, *args, **kwargs):
        super(econpaper_journalArticle, self).__init__(*args, **kwargs)
        self.urls = self.readText(urlPath)
        print self.urls

    def readText(self, path):
        print "path is %s" % path
        f = file(path, 'r')
        line = f.readline().strip()
        result = []
        while len(line) > 0:
            result.append(line.strip())
            line = f.readline().strip()
        f.close()
        return result

    def start_requests(self):
        urls = self.urls
        for url in urls:
            meta = {'search_url': url}
            yield Request(url, self.parse, meta=meta)
            # meta = {'search_url': url, 'article_url': url}
            # yield Request(url, self.parse_issue, meta=meta)

    def parse(self, response):
        meta = {'source': 'econpapers', 'source_url': 'https://econpapers.repec.org/',
                'document_type': 'journal articles'}
        collectionxpath = response.xpath(".//div[@class='bodytext']/table//dl[@class='notopmargin']//a")
        collection_urls = set()
        for elem in set(collectionxpath):
            collection = elem.xpath("text()").extract_first().strip()
            collection_url = urlparse.urljoin(response.url, elem.xpath("@href").extract_first().strip())
            if (collection_urls.__contains__(collection_url)):
                continue
            meta['collection'] = collection
            meta['collection_url'] = collection_url
            collection_urls.add(collection_url)
            yield response.follow(collection_url, self.parse_journal, meta=meta)

    def parse_journal(self, response):
        meta = {'source': response.meta['source'],
                'source_url': response.meta['source_url'],
                'document_type': response.meta['document_type'],
                'collection': response.meta['collection'],
                'collection_url': response.meta['collection_url'],
                }
        search_url = []
        urls = set()
        search_urlxpath = response.xpath(".//div[@class='issuelinks']//a/@href")
        for elem in search_urlxpath:
            url = urlparse.urljoin(response.url, elem.extract().strip())
            if urls.__contains__(url):
                continue
            urls.add(url)
            search_url.append(url)
        search_url.append(response.url)
        for item in search_url:
            if item.__contains__("/#"):
                continue
            meta['search_url'] = item
            yield response.follow(item, self.parse_issue, meta=meta)

    def parse_issue(self, response):
        meta = {'source': response.meta['source'],
                'source_url': response.meta['source_url'],
                'document_type': response.meta['document_type'],
                'collection': response.meta['collection'],
                'collection_url': response.meta['collection_url'],
                'search_url': response.meta['search_url']
                }
        issues_xpath = response.xpath(".//div[@class='bodytext']//dl")
        for elem in issues_xpath:
            volume_issue_yearInfo = elem.xpath("preceding-sibling::p[1]/b/a/text()").extract_first().strip()
            meta['volume_issue_yearInfo'] = volume_issue_yearInfo
            papers_xpath = elem.xpath(".//dt")
            for item in papers_xpath:
                accsse_url = urlparse.urljoin(response.url, item.xpath("./a/@href").extract_first().strip())
                title = item.xpath("./a/text()").extract_first().strip()
                page = item.xpath("./text()").extract_first().strip()
                meta['accsse_url'] = accsse_url
                meta['title'] = title
                meta['page'] = page
                author = ";".join(item.xpath("following-sibling::dd[1]//i/text()").extract())
                meta['author'] = author
                yield response.follow(accsse_url, self.parse_paper, meta=meta)

    def parse_paper(self, response):
        result = {'source': response.meta['source'],
                  'source_url': response.meta['source_url'],
                  'document_type': response.meta['document_type'],
                  'collection': response.meta['collection'],
                  'collection_url': response.meta['collection_url'],
                  'search_url': response.meta['search_url'],
                  'volume_issue_yearInfo': response.meta['volume_issue_yearInfo'],
                  'accsse_url': response.meta['accsse_url'],
                  'title': response.meta['title'],
                  'page': response.meta['page'],
                  'author': response.meta['author']
                  }
        p_xpath = response.xpath(".//div[@class='bodytext']/p")

        pdf_urlxpath = [elem for elem in p_xpath if elem.xpath("./b/text()").extract().__contains__("Downloads:")]
        pdf_url = "wrong"
        if len(pdf_urlxpath) != 0:
            pdf_urls = pdf_urlxpath[0].xpath("./a")
            pdf_urllist = []
            for item in pdf_urls:
                desc = item.xpath("following-sibling::text()[1]").extract_first().strip()
                link_text = item.xpath("text()").extract_first().strip()
                link = urlparse.urljoin(response.url, item.xpath("@href").extract_first().strip())
                if link_text.__contains__("..."):
                    pdf_urllist.append(desc+"DD" + "@@" + link)
                else:
                    pdf_urllist.append(desc + "@@" + link_text)
            pdf_url = "$$".join(pdf_urllist)
        result['pdf_url'] = pdf_url

        abstract_xpath = [elem for elem in p_xpath if elem.xpath("./b/text()").extract().__contains__("Abstract:")]
        abstract = "wrong"
        if len(abstract_xpath) != 0:
            abstract = abstract_xpath[0].xpath("text()").extract_first()
        result['abstract'] = abstract
        citations = "wrong"
        release_date = "wrong"
        keywords = "wrong"
        JELcodes = "wrong"
        otherinfo_xpath = [elem for elem in p_xpath if elem.xpath("./b/text()").extract().__contains__("Date:")]
        if len(otherinfo_xpath) != 0:
            otherinfo_b_xpath = otherinfo_xpath[0].xpath("./b")

            citation_xpath = [elem for elem in otherinfo_b_xpath if
                              elem.xpath("text()").extract().__contains__("Citations")]
            if len(citation_xpath) != 0:
                citations = ";".join(citation_xpath[0].xpath("following-sibling::a/text()").extract())


            release_datelist = [elem.strip() for elem in otherinfo_xpath[0].xpath("text()").extract() if
                                len(elem.strip()) >= 4 and len(elem.strip()) <= 10]
            if len(release_datelist) != 0:
                release_date = release_datelist[0]

            keywords_b = [elem for elem in otherinfo_b_xpath if
                          elem.xpath("text()").extract().__contains__("Keywords:")]
            if len(keywords_b) != 0:
                keywords_b_xpath = keywords_b[0]
                keywords_br_xpath = keywords_b_xpath.xpath("following-sibling::br[1]")
                keywords_1 = set(keywords_br_xpath.xpath("preceding-sibling::a/text()").extract())
                keywords_2 = set(keywords_b_xpath.xpath("following-sibling::a/text()").extract())
                keywords=";".join(keywords_1.intersection(keywords_2))

            JELcodes_b = [elem for elem in otherinfo_b_xpath if
                              elem.xpath("text()").extract().__contains__("JEL-codes:")]

            if len(JELcodes_b) != 0:
                JELcodes_b_xpath = JELcodes_b[0]
                JELcodes_br_xpath = JELcodes_b_xpath.xpath("following-sibling::br[1]")
                JELcodes_1 = set(JELcodes_br_xpath.xpath("preceding-sibling::a/text()").extract())
                JELcodes_2 = set(JELcodes_b_xpath.xpath("following-sibling::a/text()").extract())
                JELcodes = ";".join(JELcodes_1.intersection(JELcodes_2))

        result['citations'] = citations
        result['keywords'] = keywords
        result['release_date'] = release_date
        result['jelcodes'] = JELcodes
        yield result
