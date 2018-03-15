# -*- coding: utf-8 -*-
import scrapy
import urlparse
import json
from utils import Utils
from scrapy.http.request import Request


class EmeraldSpider(scrapy.Spider):
    name = 'emerald'
    allowed_domains = ['http://www.emeraldinsight.com/']
    start_urls = ['http://http://www.emeraldinsight.com//']

    def __init__(self, meta_file = None):
        self.meta_file = meta_file
        self.crawled_urls = []
        if self.meta_file is not None:
            with open(self.meta_file) as f:
                for line in f:
                    json_data = json.loads(line)
                    self.crawled_urls.append(json_data["url"])

    def start_requests(self):
        i = 0
        #final_page = 251 #1.14, total result is 25105
        final_page = 251

        #meta = {"pdf_url": "pdf_link", "article_type": "article_type"}
        #yield Request("https://www.emeraldinsight.com/doi/full/10.1108/CAER-09-2013-0131", self.parse_issue, meta = meta, dont_filter = True)
        #return
        
        while i <= final_page:
            start_url = "http://www.emeraldinsight.com/action/doSearch?backfile=on&content=articlesChapters&dateRange=%5B20050101+TO+20171231%5D&earlycite=on&field1=AllField&field2=AllField&field3=AllField&logicalOpe1=OR&logicalOpe2=OR&target=default&text1=agriculture&text2=agricultural&text3=rural&pageSize=100&startPage=" + str(i)
            yield Request(start_url, self.parse, dont_filter = True)
            i = i + 1

    def parse(self, response):
        titles = response.xpath("//*[@id='searchResultItems']/li")
        for title in titles:
            url = title.xpath(".//span[@class='art_title']//a/@href").extract_first()
            print "get url :%s" % url
            url = urlparse.urljoin(response.url, url)
            pdf_link = title.xpath(".//a[@class='ref nowrap pdfplus']/@href").extract_first()
            pdf_link = urlparse.urljoin(response.url, pdf_link)

            article_type = title.xpath(".//div[@class='art_type notRecommendedInfo']/text()").extract_first().replace("Type: ", "").strip()

            meta = {"pdf_url": pdf_link, "article_type": article_type}

            book_series = title.xpath(".//div[@class='bookSeries']")
            article_title =  title.xpath(".//span[@class='hlFld-Title']/a/text()").extract_first()
            if len(book_series) != 0:
                #print "%s is book_series: " % article_title
                book_series = book_series[0]
                #是书籍
                meta["meta_type"] = "book_series"
                meta["book_series"] = book_series.xpath("./a/text()").extract_first().strip()
                meta["volume"] = book_series.xpath(".//volume-title/text()").extract_first().strip()
                meta["release_year"] = book_series.xpath(".//span[@class='notRecommendedInfo']/text()").extract_first().replace(",", "").strip()
            else:
                elems = title.xpath(".//div[@class='reference']//*[@class='notRecommendedInfo']/text()").extract()
                if len(elems) == 4:
                    #print "%s is journal: " % article_title
                    #是期刊
                    meta["meta_type"] = "journal"
                    meta["journal"] = Utils.get_all_inner_texts(title, ".//span[@class='publicationInfo']").strip()
                    meta["volume"] = elems[0].replace(", Volume:", "").strip()
                    meta["issue"] = elems[1].replace("Issue:", "").strip()
                    meta["release_year"] = elems[3].strip()
                elif len(elems) == 0:
                    #print "%s is book: " % article_title
                    meta["meta_type"] = "book"
                else:
                    meta["meta_type"] = "unkown"

            if url in self.crawled_urls:
                print "%s has crawled, filter" % url

            else:
                yield response.follow(url, self.parse_issue, meta = meta, dont_filter = True)

            #yield {
            #    'url' : url,
            #    'pdf_link' : pdf_link,
            #    'article_type': article_type,
            #    'search_url': response.url
            #}

    def parse_issue(self, response):
        result = {}
        title = Utils.get_all_inner_texts(response, "//h1[@class='titleGroup']")
        if title == "":
            title = Utils.get_all_inner_texts(response, "//h1[@class='articleTitle']")

        result["title"] = title

        keys = response.xpath("//article[@class='article']//dt/text()").extract()
        values = response.xpath("//article[@class='article']//dd")
        if len(keys) != len(values):
            raise Exception("key and value length not equal :%s" % response.url)

        i = 0
        while i < len(keys):
            key = keys[i].replace(":", "")
            result[key] = " ".join(values[i].xpath(".//text()").extract()).strip()
            i += 1

        result["pdf_url"] = response.meta["pdf_url"]
        result["meta_type"] = response.meta["meta_type"]
        result["url"] = response.url

        if "release_year" in response.meta:
            result["release_year"] = response.meta["release_year"]
        result["article_type"] = response.meta["article_type"]
        if response.meta["meta_type"] == "journal":
            result["journal"] = response.meta["journal"]
            result["volume"] = response.meta["volume"]
            result["issue"] = response.meta["issue"]
        elif response.meta["meta_type"] == "book_series":
            result["book_series"] = response.meta["book_series"]
            result["volume"] = response.meta["volume"]
            result["book_series_issn"] = response.xpath("//*[@id='seriesIssn']/text()")\
                .extract_first().replace("Series ISSN:", "").strip()
            result["book_series_editor"] = response.xpath("//div[@class='bookSerialNavigation journal']/text()").extract_first()\
                .replace("Series editor(s):", "").strip()
            try:
                result["book_subject_area"] = response.xpath("//div[@class='bookSerialNavigation journal']/div//a/text()").extract_first().strip()
                result["book_subject_area"] = result["book_subject_area"].replace("Current Volume", "")
            except Exception as e:
                pass
        elif response.meta["meta_type"] == "book": 
            result["book"] = response.xpath("//div[@class='bookInfo']/h3/text()").extract_first()
            texts = response.xpath("//div[@class='bookInfo']/text()").extract()
            result["book_isbn"] = texts[0].replace("ISBN:", "").strip()
            result["book_eISBN"] = texts[1].replace("eISBN:", "").strip()
            result["book_editor"] = texts[2].replace("Edited by:", "").strip()
            result["release_year"] = texts[3].replace("Published:", "").strip()

        yield result
