#!/usr/bin/env python
# -*- coding: utf-8 -*-
import scrapy
import re
import sys
import urlparse
import sys
from scrapy.http.request import Request

reload(sys)
sys.setdefaultencoding('utf8')


class WorldBankSpider(scrapy.Spider):
    name = "worldbank"
    countrys = {}
    topics = {}

    def __init__(self, country_file=None, topic_file=None, *args, **kwargs):
        super(WorldBankSpider, self).__init__(*args, **kwargs)
        self.countrys = self.readText(country_file)
        self.topics = self.readText(topic_file)
        print self.countrys
        print self.topics

    def readText(self, path):
        print "path is %s" % path
        f = file(path, 'r')
        line = f.readline().strip()
        result = {}
        while len(line) > 0:
            print line
            name = line.split("\t")[0]
            id = line.split("\t")[1]
            result[name] = id
            line = f.readline().strip()
        f.close()
        return result

    def start_requests(self):
        # meta = {'country': 'country', 'topic': 'topic'}
        # url = "https://elibrary.worldbank.org/action/doSearch?ConceptID=8354&ConceptID=6055&dateRange=%5B20050101+TO+20161231%5D&pageSize=100"
        # yield Request(url, self.parse, meta=meta)
        # return
        countrys = self.countrys
        topics = self.topics
        for (country, country_code) in countrys.items():
            for (topic, topic_code) in topics.items():
                url = "https://elibrary.worldbank.org/action/doSearch?ConceptID=" + country_code + "&ConceptID=" + topic_code + "&dateRange=%5B20050101+TO+20161231%5D&pageSize=100"
                meta = {'country': country, 'topic': topic}
                yield Request(url, self.parse, meta=meta)

    def parse(self, response):
        print response.meta['country']
        print response.meta['topic']
        resultNum="ERROR"
        resultNumlist = response.xpath("//*[@id='searchResultContainer']/div[1]/div[1]/div[1]/div[1]/div/span[3]/text()").extract()
        if len(resultNumlist)!=0:
            resultNum=resultNumlist[0].replace(" of","").strip()
        issues = response.xpath("//div[@id='searchResultEntryContainer']/div[@class='art_type']")
        #分页情况
        page_links = response.xpath("// *[ @ id = 'searchResultContainer']/div[1]/div[1]/div[1]/div[2]/ul//a/@href").extract()
        for pagelink in page_links:
            if str(pagelink).strip().__contains__("&startPage=0"):
                continue
            yield response.follow(urlparse.urljoin(response.url,pagelink.strip()), self.parse, response.meta)


        for issue in issues:
            issue_type = issue.xpath("text()").extract_first().strip()
            tables = issue.xpath("following-sibling::table[1]")
            titleList = tables.xpath(".//span[@class='hlFld-Title']/a/text()").extract()
            title="ERROR"
            url="ERROR"
            if len(titleList)!=0:
                title = tables.xpath(".//span[@class='hlFld-Title']/a/text()").extract_first().strip()
                url = urlparse.urljoin(response.url,
                                   tables.xpath(".//span[@class='hlFld-Title']/a/@href").extract_first().strip())

            authorList = tables.xpath(
                ".//span[@class='hlFld-ContribAuthor']/a/text()").extract()
            chapter_authors_editors = "ERROR"
            authors_editors = "ERROR"
            if len(authorList) == 2:
                chapter_authors_editors = authorList[0].strip()
                authors_editors = authorList[1].strip()
            elif len(authorList) == 1:
                authors_editors = authorList[0].strip()
            doi = "ERROR"
            if len(tables.xpath(".//a[@class='displayDoi ref nowrap']/text()").extract()) != 0:
                doi = tables.xpath(".//a[@class='displayDoi ref nowrap']/text()").extract_first().strip()

            published = "ERROR"
            pages = "ERROR"
            vol = "ERROR"
            no = "ERROR"
            # published_pages = tables.xpath(".//div[@class='art_meta']/text()").extract()
            # if len(published_pages) >= 2:
            #     published = published_pages[0].strip()
            #     pages = str(published_pages[1]).replace("\xe2\x80\x93", "-")
            # elif len(published_pages) == 1:
            #     published = published_pages[0].strip()

            months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October","November", "December"]
            timeInfoList = tables.xpath(".//div[@class='art_meta']/text()").extract()
            if len(timeInfoList) != 0:
                for elem in timeInfoList:
                    if months.__contains__(elem.strip().split(" ")[0]):
                        published = elem.strip()
                    if elem.strip().__contains__("Vol.") or elem.strip().__contains__("No."):
                        vol_no = elem.split(",")
                        for item in vol_no:
                            if item.__contains__("Vol."):
                                vol = item.strip()
                            if item.__contains__("No."):
                                no = item.strip()
                    if str(elem).__contains__("\xe2\x80\x93"):
                        pages = elem.strip()


            linkList = tables.xpath(".//div[@class='articleEntryLinks']/a/@href").extract()
            pdf_links = "ERROR"
            epub_links = "ERROR"
            if len(linkList) >= 2:
                pdf_links = urlparse.urljoin(response.url,linkList[0].strip())
                epub_links = urlparse.urljoin(response.url,linkList[1].strip())
            elif len(linkList) == 1:
                if str(linkList[0].strip()).__contains__("pdf"):
                    pdf_links = urlparse.urljoin(response.url,linkList[0].strip())
                if str(linkList[0].strip()).__contains__("epub"):
                    epub_links = urlparse.urljoin(response.url,linkList[0].strip())
            response.meta['type'] = issue_type
            response.meta['title'] = title
            response.meta['published'] = published
            response.meta['pages'] = pages
            response.meta['doi'] = doi
            response.meta['pdf_links'] = pdf_links
            response.meta['epub_links'] = epub_links
            response.meta['resultNum'] = resultNum
            response.meta['chapter_authors_editors'] = chapter_authors_editors
            response.meta['authors_editors'] = authors_editors
            response.meta['vol'] = vol
            response.meta['no'] = no

            if url != "ERROR":
                yield response.follow(url,self.parse_issue, meta=response.meta,dont_filter=True)
            else:
                yield {
                    "country": response.meta['country'],
                    "topic": response.meta['topic'],
                    "resultNum": resultNum,
                    "issue_type": issue_type,
                    "title": title,
                    "chapter_authors_editors": chapter_authors_editors,
                    "authors_editors": authors_editors,
                    "published": published,
                    "pages": pages,
                    "vol": vol,
                    "no": no,
                    "doi": doi,
                    "booktitle": "ERROR",
                    "book_isbn": "ERROR",
                    "book_eisbn": "ERROR",
                    "issn": "ERROR",
                    "book_doi": "ERROR",
                    "abstract": "ERROR",
                    "related_regions": "ERROR",
                    "related_countries": "ERROR",
                    "related_topics": "ERROR",
                    "keywords": "ERROR",
                    "pdf_links": pdf_links,
                    "epub_links": epub_links,
                    "from": response.url
                }
            # if issue_type == 'Chapter':
            #     book_title = meta.xpath(".//div[@class='bookTitle']/text()").extract_first().strip()
            #     chapter_authors_editors = meta.xpath(
            #         ".//span[@class='hlFld-ContribAuthor']/a/text()").extract_first().strip()
            #     authors_editors = meta.xpath(".//span[@class='hlFld-ContribAuthor']/a/text()").extract()[1].strip()
            #     published = meta.xpath(".//div[@class='art_meta']/text()").extract_first().strip()
            #     pages = str(meta.xpath(".//div[@class='art_meta']/text()").extract()[1].strip()).replace("\xe2\x80\x93","-")
            #     links = urlparse.urljoin(response.url,meta.xpath(".//div[@class='articleEntryLinks']/a/@href").extract_first().strip())
            #     abstract=meta.xpath(".//div[@class='NLM_abstract']/p/text()").extract_first().strip()

    def parse_issue(self, response):
        country = response.meta['country']
        topic = response.meta['topic']
        resultNum = response.meta['resultNum']
        issus_type = response.meta['type']
        title = response.meta['title']
        published = response.meta['published']
        pages = response.meta['pages']
        pdf_links = response.meta['pdf_links']
        epub_links = response.meta['epub_links']
        vol = response.meta['vol']
        no = response.meta['no']
        chapter_authors_editors = response.meta['chapter_authors_editors']
        authors_editors = response.meta['authors_editors']
        if authors_editors == 'ERROR':
            authors_editorsList = response.xpath("//a[@class='entryAuthor']/text()").extract()
            if len(authors_editorsList) != 0:
                authors_editors = authors_editorsList[0].strip()

        issn = "ERROR"
        book_doi = "ERROR"
        book_isbn = "ERROR"
        book_eisbn = "ERROR"
        booktitle = "ERROR"
        if issus_type != "Journal Article":
            booktitle = response.xpath(
                "//div[contains(@class,'bookInformationWidget') and contains(@class,'boxWidget')]/div[@class ='book']/h2/text()").extract_first().strip()
            isbn = response.xpath(
                "//div[contains(@class,'bookInformationWidget') and contains(@class,'boxWidget')]/div[@class ='book']//span[@id='seriesIssn']/text()").extract()
            if len(isbn) == 2:
                book_isbn = isbn[0].strip()
                book_eisbn = isbn[1].strip()
            elif len(isbn) == 1:
                book_isbn = isbn[0].strip()
            book_doilist = response.xpath(
                "//div[contains(@class,'bookInformationWidget') and contains(@class,'boxWidget')]/div[@class ='book']/div[@class='info']/a/@href").extract()
            if len(book_doilist) != 0:
                book_doi = book_doilist[0].strip()
        else:
            booktitle = response.xpath(
                "//div[contains(@class, 'seriesNav') and contains(@class, 'boxWidget')]/div[@class='issue']/strong/text()").extract_first().strip()
            issn = response.xpath(
                "//div[contains(@class, 'seriesNav') and contains(@class, 'boxWidget')]/div[@class='issue']//p[@class='issn']/text()").extract_first().strip()

        doi = response.meta['doi']
        if doi == 'ERROR':
            doiList = response.xpath(
                ".//div[@class='doiWidgetContainer']/a[@class='doiWidgetLink']/text()").extract()
            if len(doiList) != 0:
                doi = doiList[0].strip()

        abstractList = response.xpath(".//div[@class='NLM_abstract']/p/text()").extract()
        abstract = "ERROR"
        if len(abstractList) != 0:
            abstract = "".join(abstractList).strip()
        keywordContainer = response.xpath(".//div[@class='keywordContainer']//span[@class='keywordsLabel']")
        related_regions = "ERROR"
        related_countries = "ERROR"
        related_topics = "ERROR"
        keywords = "ERROR"
        for keyword in keywordContainer:
            if str(keyword.xpath("text()").extract()).__contains__("Related Regions"):
                regionsList = keyword.xpath("following-sibling::a/text()").extract()
                related_regions = ",".join(regionsList)
            if str(keyword.xpath("text()").extract()).__contains__("Related Countries"):
                countriesList = keyword.xpath("following-sibling::a/text()").extract()
                related_countries = ",".join(countriesList)
            if str(keyword.xpath("text()").extract()).__contains__("Related Topics"):
                topicsList = keyword.xpath("following-sibling::a/text()").extract()
                related_topics = ",".join(topicsList)
            if str(keyword.xpath("text()").extract()).__contains__("Keywords"):
                keywordsList = keyword.xpath("following-sibling::a/text()").extract()
                keywords = ",".join(keywordsList)
        yield {
            "country": country,
            "topic": topic,
            "resultNum": resultNum,
            "issue_type": issus_type,
            "title": title,
            "chapter_authors_editors": chapter_authors_editors,
            "authors_editors": authors_editors,
            "published": published,
            "pages": pages,
            "vol": vol,
            "no": no,
            "doi": doi,
            "booktitle": booktitle,
            "book_isbn": book_isbn,
            "book_eisbn": book_eisbn,
            "issn": issn,
            "book_doi": book_doi,
            "abstract": abstract,
            "related_regions": related_regions,
            "related_countries": related_countries,
            "related_topics": related_topics,
            "keywords": keywords,
            "pdf_links": pdf_links,
            "epub_links": epub_links,
            "from": response.url
        }
