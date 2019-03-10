# -*- coding: utf-8 -*-
import scrapy
import urlparse
import json
from utils import Utils
from scrapy.http.request import Request


class TandfonlineSpider(scrapy.Spider):
    name = 'tandfonline'
    start_urls = [
      #'http://www.tandfonline.com/loi/taar20',
      #'http://www.tandfonline.com/loi/tgnh20',
      #'http://www.tandfonline.com/loi/tcyt20',
      #'http://www.tandfonline.com/loi/tbeq20',
      #'http://www.tandfonline.com/loi/tjbd20',
      #'http://tandfonline.com/loi/tejr20',

      #'http://www.tandfonline.com/loi/kbac20',
      #'http://www.tandfonline.com/loi/kbim20',
      #'http://www.tandfonline.com/loi/kcll20',
      #'http://www.tandfonline.com/loi/kidp20',
      #'http://www.tandfonline.com/loi/kinv20',
      #'http://www.tandfonline.com/loi/kjks20',
      #'http://www.tandfonline.com/loi/kmge20',
      #'http://www.tandfonline.com/loi/kpsb20',
      #'http://www.tandfonline.com/loi/kspe20',
      #'http://www.tandfonline.com/loi/kwrm20',

      #'http://www.tandfonline.com/loi/uetp',
      #'http://www.tandfonline.com/loi/tjar20',
      'https://www.tandfonline.com/toc/taar20/38/1?nav=tocList',
    ]

    def __init__(self, url_file = None, meta_file = None):
      self.meta_file = meta_file
      self.url_file = url_file
      self.crawl_urls = []
      if meta_file:
          with open(meta_file, "rb") as f:
              for line in f:
                  json_data = json.loads(line.strip())
                  issue_url = json_data["url"]
                  self.crawl_urls.append(issue_url)

    def parse(self, response):
        with open(self.url_file) as f:
            for line in f:
                url = line.strip()
                yield response.follow(url, self.parse_journal_tandfonline_issue)
        return
        year_links = response.xpath("//li[@class='vol_li ']/a/@href").extract()
        for link in year_links:
            year = int(Utils.regex_extract(link, "year=(\d+)&repitition"))
            if year >= 2016:
                volume_url = urlparse.urljoin(response.url, link)
                yield response.follow(volume_url, self.parse_tandfonline_volumn)

    def parse_tandfonline_volumn(self, response):
      issues = response.xpath("//li[@class='vol_li active']/ul/li")
      for issue in issues:
        url = issue.xpath("./a/@href").extract_first()
        date = issue.xpath(".//span[@id='loiIssueCoverDateText']/text()").extract_first().strip()
        meta = {"release_date": date}
        yield response.follow(url, self.parse_journal_tandfonline_issue, meta = meta)

    def parse_journal_tandfonline_issue(self, response):
        fields = response.url.split('/')
        size = len(fields)

        if "release_date" not in response.meta:
            release_date = response.xpath("//span[@class='slider-vol-year']/text()").extract_first().strip()
        else:
            release_date = response.meta["release_date"]

        # url must be like http://www.tandfonline.com/toc/kcll20/{volume_id}/{issue_id}
        volume = fields[size - 2]
        issue = fields[size - 1].split('?')[0]

        journal = response.xpath("//div[@class='journalMetaTitle page-heading']//span/text()").extract_first()

        articles = response.xpath("//form[@name='frmAbs']//div[@class='tocContent']/table")
        for article in articles:
            title = " ".join(article.xpath(".//div[@class='art_title linkable']//span")[0].xpath(".//text()").extract())
            article_url = urlparse.urljoin(response.url, article.xpath(".//div[@class='art_title linkable']/a/@href").extract_first())
            page = article.xpath(".//div[@class='tocPageRange maintextleft']/text()").extract_first().split(':')[1].strip()
            doi = urlparse.urljoin(response.url, article.xpath(".//div[@class='art_title linkable']/a/@href").extract_first().replace("/doi/full/", ""))
            link = str(urlparse.urljoin(response.url, article.xpath(".//a[@class='ref nowrap pdf']/@href").extract_first()))
            author = article.xpath(".//span[@class='articleEntryAuthorsLinks']/span/a/text()").extract_first()

            meta = {
                'journal' : journal,
                'title' : title,
                'release_date' : release_date,
                'volume' : volume,
                'issue' : issue,
                'page' : page,
                'doi' : doi,
                'pdf_url' : link,
                'author': author,
                'url' : article_url,
                "from_url" : response.url,
            }

            if article_url in self.crawl_urls:
              print "%s crawled, pass" % article_url
              continue

            yield response.follow(article_url, self.parse_journal_tandfonline_article, meta = meta)

    def parse_journal_tandfonline_article(self, response):
      author = response.xpath("//span[@class='NLM_contrib-group']/span/a/text()").extract()
      author_affiliation = response.xpath("//span[@class='NLM_contrib-group']/span/a/span/text()").extract()
      abstract = Utils.get_all_inner_texts(response, "//div[@class='abstractSection abstractInFull']")
      keywords = response.xpath("//div[@class='hlFld-KeywordText']/a/text()").extract()
      yield {
        'journal' : response.meta['journal'],
        'title' : response.meta['title'],
        'release_date' : response.meta['release_date'],
        'volume' : response.meta['volume'],
        'issue' : response.meta['issue'],
        'page' : response.meta['page'],
        'doi' : response.meta['doi'],
        'pdf_url' : response.meta['pdf_url'],
        'url': response.url,
        'author': author,
        'author_affiliation' : author_affiliation,
        'keywords' : keywords,
        'from_url' : response.meta["from_url"],
      }

