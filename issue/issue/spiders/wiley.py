# -*- coding: utf-8 -*-
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

import urlparse
from ..spiders.utils import  Utils

class WileySpider(CrawlSpider):
    name = 'wiley'
    allowed_domains = [
        'jvi.asm.org',
        'dl.sciencesocieties.org', #10
        'onlinelibrary.wiley.com',
        ]
    start_urls = [
        #'http://onlinelibrary.wiley.com/journal/10.1111/(ISSN)1365-2435/issues', #102
        #'http://onlinelibrary.wiley.com/journal/10.1111/(ISSN)1365-2443/issues', #103
        #'http://onlinelibrary.wiley.com/journal/10.1002/(ISSN)1521-6551/issues', #104
        #'http://onlinelibrary.wiley.com/journal/10.1111/(ISSN)1600-048X/issues', #105
        #'http://onlinelibrary.wiley.com/journal/10.1111/(ISSN)1364-3703/issues', #106
        #'http://onlinelibrary.wiley.com/journal/10.1111/(ISSN)1756-1051/issues', #107
        #'http://onlinelibrary.wiley.com/journal/10.1111/(ISSN)1600-0706/issues', #108
        #'http://onlinelibrary.wiley.com/journal/10.1111/(ISSN)1440-1835/issues', #109
        #'http://onlinelibrary.wiley.com/journal/10.1111/(ISSN)1442-1984/issues', #110
        #'http://onlinelibrary.wiley.com/journal/10.1111/(ISSN)1439-0531/issues', #111
        #'http://onlinelibrary.wiley.com/journal/10.1111/(ISSN)1445-6664/issues', #112
        #'http://onlinelibrary.wiley.com/journal/10.1111/(ISSN)1744-697X/issues', #113
        #'http://onlinelibrary.wiley.com/journal/10.1002/(ISSN)1938-5455/issues', #115
        #'http://onlinelibrary.wiley.com/journal/10.1111/(ISSN)1468-2257/issues', #131
        #'http://onlinelibrary.wiley.com/journal/10.1111/(ISSN)1744-7976/issues', #132
        #'http://onlinelibrary.wiley.com/journal/10.1111/(ISSN)1471-0366/issues', #133
        #'http://onlinelibrary.wiley.com/journal/10.1111/(ISSN)1095-8312/issues', #134
        #'http://onlinelibrary.wiley.com/journal/10.1002/(ISSN)1460-2075/issues', #135
        #'http://onlinelibrary.wiley.com/journal/10.1002/(ISSN)1469-3178/issues', #136
        #'http://onlinelibrary.wiley.com/journal/10.1111/(ISSN)1096-3642/issues', #137
        #'http://onlinelibrary.wiley.com/journal/10.1111/(ISSN)1939-165X/issues', #138
        #'http://onlinelibrary.wiley.com/journal/10.1002/(ISSN)1099-0755/issues', #40
        #'http://onlinelibrary.wiley.com/journal/10.1111/(ISSN)1472-4669/issues', #41
        #'http://onlinelibrary.wiley.com/journal/10.1111/(ISSN)1745-4514/issues', #42
        #'http://onlinelibrary.wiley.com/journal/10.1111/(ISSN)1745-4549/issues', #43
        #'http://onlinelibrary.wiley.com/journal/10.1111/(ISSN)1745-4557/issues', #44
        #'http://onlinelibrary.wiley.com/journal/10.1111/(ISSN)1745-4565/issues', #45
        #'http://onlinelibrary.wiley.com/journal/10.1002/(ISSN)1520-6327/issues', #46
        #'http://onlinelibrary.wiley.com/journal/10.1002/(ISSN)1618-2863/issues', #47
        #'http://onlinelibrary.wiley.com/journal/10.1111/(ISSN)1365-2052/issues', #48
        #'http://onlinelibrary.wiley.com/journal/10.1111/(ISSN)1469-8137/issues', #49
        #'http://onlinelibrary.wiley.com/journal/10.1021/(ISSN)1520-6033/issues', #57
        #'http://onlinelibrary.wiley.com/journal/10.1111/(ISSN)1744-7429/issues', #58
        #'http://onlinelibrary.wiley.com/journal/10.1111/(ISSN)1440-169X/issues', #59
        #'http://onlinelibrary.wiley.com/journal/10.1111/(ISSN)1600-0633/issues', #60
        #'http://onlinelibrary.wiley.com/journal/10.1111/(ISSN)1748-5967/issues', #61
        #'http://onlinelibrary.wiley.com/journal/10.1111/(ISSN)1479-8298/issues', #62
        #'http://onlinelibrary.wiley.com/journal/10.1111/(ISSN)1365-2095/issues', #63
        #'http://onlinelibrary.wiley.com/journal/10.1111/(ISSN)1748-7692/issues', #64
        #'http://onlinelibrary.wiley.com/journal/10.1111/(ISSN)1365-3024/issues', #65
        #'http://onlinelibrary.wiley.com/journal/10.1111/(ISSN)1550-7408/issues', #66
        #'http://onlinelibrary.wiley.com/journal/10.1111/(ISSN)1439-0426/issues', #68
        #'http://onlinelibrary.wiley.com/journal/10.1111/(ISSN)2041-210X/issues', #69
        #'http://onlinelibrary.wiley.com/journal/10.1002/(ISSN)1757-7012/issues', #70
        #'http://onlinelibrary.wiley.com/journal/10.1002/(ISSN)1757-7799/issues', #71
        #'http://onlinelibrary.wiley.com/journal/10.1111/(ISSN)1759-7692/issues', #72
        #'http://onlinelibrary.wiley.com/journal/10.1002/(ISSN)1936-0592/issues', #75
        #'http://onlinelibrary.wiley.com/journal/10.1002/(ISSN)1521-1878/issues', #76
        #'http://onlinelibrary.wiley.com/journal/10.1002/(ISSN)2042-5805/issues', #77
        #'http://onlinelibrary.wiley.com/journal/10.1002/(ISSN)2152-3878/issues', #78
        #'http://onlinelibrary.wiley.com/journal/10.1111/(ISSN)1740-0929/issues', #79
        #'http://onlinelibrary.wiley.com/journal/10.1111/(ISSN)1939-7445/issues', #81
        #'http://onlinelibrary.wiley.com/journal/10.1111/(ISSN)1759-0884/issues', #82
        #'http://onlinelibrary.wiley.com/journal/10.1111/(ISSN)1467-7652/issues', #87
        #'http://onlinelibrary.wiley.com/journal/10.1111/(ISSN)1439-0329/issues', #88
        #'http://onlinelibrary.wiley.com/journal/10.1111/(ISSN)1753-5131/issues', #89
        #'http://onlinelibrary.wiley.com/journal/10.1002/(ISSN)1938-5463a/issues', #90
        #'http://onlinelibrary.wiley.com/journal/10.1002/(ISSN)1526-968X/issues', #91
        #'http://onlinelibrary.wiley.com/journal/10.1002/(ISSN)1522-239Xb/issues' #92

        #以下是OA的wiley需求
        #'http://onlinelibrary.wiley.com/journal/10.1002/(ISSN)2198-3844/issues',
        #'http://onlinelibrary.wiley.com/journal/10.1111/(ISSN)1474-9726/issues',
        #'http://onlinelibrary.wiley.com/journal/10.1002/(ISSN)2328-9503/issues',
        #'http://onlinelibrary.wiley.com/journal/10.1002/(ISSN)2050-2680/issues',
        #'http://onlinelibrary.wiley.com/journal/10.1002/(ISSN)2157-9032/issues',
        #'http://onlinelibrary.wiley.com/journal/10.1002/(ISSN)2045-7634/issues',
        #'http://onlinelibrary.wiley.com/journal/10.1111/(ISSN)1349-7006/issues',
        #'http://onlinelibrary.wiley.com/journal/10.1002/(ISSN)2191-1363/issues',
        #'http://onlinelibrary.wiley.com/journal/10.1002/(ISSN)2057-4347/issues',
        #'http://onlinelibrary.wiley.com/journal/10.1002/(ISSN)2050-0904/issues',
        #'http://onlinelibrary.wiley.com/journal/10.1002/(ISSN)2163-8306/issues',
        #'http://onlinelibrary.wiley.com/journal/10.1002/(ISSN)2055-4877/issues',
        #'http://onlinelibrary.wiley.com/journal/10.1111/(ISSN)1755-263X/issues',
        #'http://onlinelibrary.wiley.com/journal/10.1002/(ISSN)2045-7758/issues',
        #'http://onlinelibrary.wiley.com/journal/10.1002/(ISSN)2050-0505/issues',
        #'http://onlinelibrary.wiley.com/journal/10.1002/(ISSN)1757-4684/issues',
        #'http://onlinelibrary.wiley.com/journal/10.1002/(ISSN)2055-5822/issues',
        #'http://onlinelibrary.wiley.com/journal/10.1002/(ISSN)2054-703X/issues',
        #'http://onlinelibrary.wiley.com/journal/10.1111/(ISSN)1752-4571/issues',
        #'http://onlinelibrary.wiley.com/journal/10.1002/(ISSN)2048-3694/issues',
        #'http://onlinelibrary.wiley.com/journal/10.1002/(ISSN)2048-7177/issues',
        #'http://onlinelibrary.wiley.com/journal/10.1002/(ISSN)2054-4049/issues',
        #'http://onlinelibrary.wiley.com/journal/10.1002/(ISSN)2049-6060/issues',
        #'http://onlinelibrary.wiley.com/journal/10.1002/(ISSN)2050-4527/issues',
        #'http://onlinelibrary.wiley.com/journal/10.1111/(ISSN)1750-2659/issues',
        #'http://onlinelibrary.wiley.com/journal/10.1002/(ISSN)2375-2920/issues',
        #'http://onlinelibrary.wiley.com/journal/10.1007/13539.2190-6009/issues',
        #'http://onlinelibrary.wiley.com/journal/10.1111/(ISSN)1582-4934/issues',
        #'http://onlinelibrary.wiley.com/journal/10.1111/(ISSN)2040-1124/issues',
        #'http://onlinelibrary.wiley.com/journal/10.1002/(ISSN)2058-3273/issues',
        #'http://onlinelibrary.wiley.com/journal/10.1002/(ISSN)2051-3909/issues',
        #'http://onlinelibrary.wiley.com/journal/10.1002/(ISSN)2056-4538/issues',
        #'http://onlinelibrary.wiley.com/journal/10.1002/(ISSN)2047-9980/issues',
        #'http://onlinelibrary.wiley.com/journal/10.1111/(ISSN)1939-1676/issues',
        #'http://onlinelibrary.wiley.com/journal/10.1111/(ISSN)1751-7915/issues',
        #'http://onlinelibrary.wiley.com/journal/10.1002/(ISSN)2045-8827/issues',
        #'http://onlinelibrary.wiley.com/journal/10.1002/(ISSN)2324-9269/issues',
        #'http://onlinelibrary.wiley.com/journal/10.1002/(ISSN)2054-1058/issues',
        #'http://onlinelibrary.wiley.com/journal/10.1002/(ISSN)1744-4292/issues',
        #'http://onlinelibrary.wiley.com/journal/10.1002/(ISSN)2055-2238/issues',
        #'http://onlinelibrary.wiley.com/journal/10.1002/(ISSN)2052-1707/issues',
        #'http://onlinelibrary.wiley.com/journal/10.1002/(ISSN)2051-817X/issues',
        #'http://onlinelibrary.wiley.com/journal/10.1002/(ISSN)2052-4412/issues',
        #'http://onlinelibrary.wiley.com/journal/10.1002/(ISSN)2056-3485/issues',
        #'http://onlinelibrary.wiley.com/journal/10.1002/(ISSN)2051-3380/issues',
        #'http://onlinelibrary.wiley.com/journal/10.1002/(ISSN)2050-1161/issues',
        #'http://onlinelibrary.wiley.com/journal/10.1111/(ISSN)1759-7714/issues',
        #'http://onlinelibrary.wiley.com/journal/10.1002/(ISSN)2053-1095/issues'

        #以下是OA的新增需求
        #'https://onlinelibrary.wiley.com/loi/14677652',
        #'https://onlinelibrary.wiley.com/loi/17571707',

        #以下是eonly的返工
        #'http://onlinelibrary.wiley.com/journal/loi/17454557',
        #'http://onlinelibrary.wiley.com/journal/loi/15206033',
        #'http://onlinelibrary.wiley.com/journal/loi/21523878',
        #'http://onlinelibrary.wiley.com/journal/loi/19385463a',
        #'http://onlinelibrary.wiley.com/journal/loi/1526968X',
        #'http://onlinelibrary.wiley.com/journal/loi/1522239Xb',
        #'http://onlinelibrary.wiley.com/journal/loi/1600048X',
        #'http://onlinelibrary.wiley.com/journal/loi/1744697X',
        #'http://onlinelibrary.wiley.com/journal/loi/1939165X',
        #'http://onlinelibrary.wiley.com/journal/loi/2041210X',
        #'http://onlinelibrary.wiley.com/journal/loi/14635224',
        #'http://onlinelibrary.wiley.com/journal/loi/14390264',
        #'http://onlinelibrary.wiley.com/journal/loi/19372817'
        'https://ascpt.onlinelibrary.wiley.com/toc/21638306/2013/2/1',
        'https://ascpt.onlinelibrary.wiley.com/toc/21638306/2013/2/2',
        'https://ascpt.onlinelibrary.wiley.com/toc/21638306/2013/2/3',
        'https://ascpt.onlinelibrary.wiley.com/toc/21638306/2013/2/4',
        'https://ascpt.onlinelibrary.wiley.com/toc/21638306/2013/2/5',
        'https://ascpt.onlinelibrary.wiley.com/toc/21638306/2013/2/6',
        'https://ascpt.onlinelibrary.wiley.com/toc/21638306/2013/2/7',
        'https://ascpt.onlinelibrary.wiley.com/toc/21638306/2013/2/8',
        'https://agupubs.onlinelibrary.wiley.com/toc/23335084/2016/3/7',
        'https://onlinelibrary.wiley.com/toc/20513909a/2010/57/1',
        'https://onlinelibrary.wiley.com/toc/20513909a/2010/57/2',
        'https://onlinelibrary.wiley.com/toc/20513909a/2010/57/3',
        'https://onlinelibrary.wiley.com/toc/20513909a/2011/58/1',
        'https://onlinelibrary.wiley.com/toc/20513909a/2011/58/2',
        'https://onlinelibrary.wiley.com/toc/20513909a/2011/58/3',
        'https://onlinelibrary.wiley.com/toc/20513909a/2011/58/4',
        'https://onlinelibrary.wiley.com/toc/20513909a/2012/59/1',
        'https://onlinelibrary.wiley.com/toc/20513909a/2012/59/2',
        'https://onlinelibrary.wiley.com/toc/20513909a/2012/59/3',
        'https://onlinelibrary.wiley.com/toc/20513909a/2012/59/4',
        'https://onlinelibrary.wiley.com/toc/17517915/2016/9/2',
        'https://onlinelibrary.wiley.com/toc/17517915/2016/9/3',
        'https://onlinelibrary.wiley.com/toc/17517915/2016/9/4',
        'https://onlinelibrary.wiley.com/toc/17517915/2016/9/5',
        'https://onlinelibrary.wiley.com/toc/17517915/2016/9/6',
        'https://onlinelibrary.wiley.com/toc/17517915/2017/10/1',
        'https://onlinelibrary.wiley.com/toc/17517915/2017/10/2',
        'https://onlinelibrary.wiley.com/toc/17517915/2017/10/3',
        'https://onlinelibrary.wiley.com/toc/17517915/2017/10/4',
        'https://onlinelibrary.wiley.com/toc/17517915/2017/10/5',
        'https://onlinelibrary.wiley.com/toc/17517915/2017/10/6',
    ]

    rules = (
        # Extract links matching 'item.php' and parse them with the spider's method parse_item

        #Rule(LinkExtractor(allow=('onlinelibrary.wiley.com/doi/.*/.*/issuetoc', )), callback='parse_journal_wiley'),
        Rule(LinkExtractor(allow=('issue/.*issue-\d+/$', )), callback='parse_journal_wiley'),
        Rule(LinkExtractor(allow=('toc/\w+/\d+/\d+/\d+$', )), callback='parse_journal_wiley_new'),

        # Extract links matching 'category.php' (but not matching 'subsection.php')
        # and follow links from them (since no callback means follow=True by default).
        Rule(LinkExtractor(allow=(
                '.*journal/.*issues\?activeYear=201[5-7]$', #103
                #'loi/\d+/year/200[5-9]$',
                'loi/\w+/year/201[6-7]$',
            ))),
    )

    def extract_with_css(self, root, query):
        return root.css(query).extract_first().strip()

    """
    Extract full text inner a scrapy selector, for examlpe:

	html like:
    <div class="result-title">
    	<a href="#"><em>Name: </em> lizhen, <em>Age: </em> 18</a>
	</div>
    
    code:
    for a in response.css(".result-title a"):
        print self.extract_full_text(a)
        
    result:
        Name: lizhen, Age: 18
    """
    def extract_full_text(self, selector):
        return ("".join(selector.xpath(".//text()").extract()))

    """
    爬取wiley的详情页
    """
    def parse_wiley_issue(self, response):
        #暂时决定用portia爬取
        pass

    def parse_journal_wiley(self, response):
        self.logger.info('Get an issue page for wiley :%s', response.url)

        journal = response.xpath("//h1[@id='productTitle']/text()").extract_first()
        volume = response.xpath("//div[@id='metaData']//span[@class='issueTocVolume']/text()").extract_first().split()[1]
        issue = response.xpath("//div[@id='metaData']//span[@class='issueTocIssue']/text()").extract_first().split()[1]
        date = response.xpath("//div[@id='metaData']//h2[@class='noMargin']/text()").extract_first()

        sections = response.xpath("//ol[@id='issueTocGroups']/li")
        for section in sections:
            articles = section.xpath(".//ol[@class='articles']/li")
            for article in articles:
                article_url = urlparse.urljoin(response.url, article.xpath(".//div[@class='citation tocArticle']/a/@href").extract_first())
                title = article.xpath(".//div[@class='citation tocArticle']/a/text()").extract_first()
                try:
                    page = article.xpath(".//div[@class='citation tocArticle']/a/span/text()").extract_first().split()[1].strip(')')
                except Exception as e:
                    page = ""

                try:
                    elems = article.xpath(".//div[@class='citation tocArticle']/p[last()]/text()").extract_first().split('|')
                    doi = elems[1].split(':')[1].strip()
                except Exception as e:
                    doi = ""

                link = urlparse.urljoin(response.url, article.xpath(".//ul[@class='productMenu']/li[3]/a/@href").extract_first())
                
                #yield response.follow(article_url, self.parse_wiley_issue, meta = met)

                yield {
                    'journal_id': 'wiley',
                    'journal' : journal,
                    "title" : title,
                    "date" : date,
                    "vol" : volume,
                    "issue" : issue,
                    "page" : page,
                    "doi" : doi,
                    "pdf_link": link,
                    'journal_url': response.url,
                    "article_url" : article_url
                }

    def parse_journal_10(self, response):
        self.logger.info('Get an issue page for jorunal 10: %s', response.url)
        fields = response.url.split('/')
        size = len(fields)
        # url must be like dl.sciencesocieties.org/publications/cftm/tocs/{volumd_id}/{issue_id}
        volume = fields[size - 2]
        issue = fields[size -1]

        journal = response.xpath("//div[@id='one']//div[@class='breadcrumb']/a[last()]/text()").extract()
        date = response.xpath("//div[@id='tabs']/following::p[1]/text()").extract()[1]


        sections = response.xpath("//form[@action='/publications/select-items']/ul/li")
        for section in sections:
            articles = section.xpath("./ul/li")
            for article in articles:
                title_elem = article.css("span")[1]
                title = self.extract_full_text(title_elem)

                texts = title_elem.xpath("./following-sibling::text()[preceding-sibling::br]").extract()
                filter_texts = [x for x in texts if x.strip() != ""]
                doi = filter_texts[0]

                yield {
                    'journal_id': 10,
                    'journal' : journal,
                    "title" : title,
                    "date" : date,
                    "vol" : volume,
                    "issue" : issue,
                    "page" : "unkonw", #cannot get page
                    "doi" : doi,
                    "link": "unkonw"
                }

    #2018年，发现wiley改版了
    def parse_journal_wiley_new(self, response):
        journal = response.xpath("//*[@id='journal-banner-text']/text()").extract_first()
        volume_issue_info = Utils.get_all_inner_texts(response, "//div[@class='cover-image__parent-item']")
        volume = Utils.regex_extract(volume_issue_info, "Volume (\d+),")
        issue = Utils.regex_extract(volume_issue_info, "Issue (\d+)")

        articles = response.xpath("//div[@class='issue-item']")
        for article in articles:
            title = Utils.get_all_inner_texts(article, ".//a[@class='issue-item__title']/h2").strip().replace("\n", " ")
            article_url = article.xpath(".//a[@class='issue-item__title']/@href").extract_first()
            article_url = urlparse.urljoin(response.url, article_url)

            author = article.xpath("./ul[@class='rlist--inline loa comma loa-authors-trunc']/li//span/text()").extract()

            try:
                page_elem = Utils.select_element_by_content(article, "./ul[@class='rlist--inline separator']/li", "Pages")
                page = page_elem.xpath(".//span[last()]/text()").extract_first()
            except Exception as e:
                page_elem = article.xpath("./ul[@class='rlist--inline separator']/li[1]")
                page = page_elem.xpath(".//span[last()]/text()").extract_first()

            try:
                release_date_elem = Utils.select_element_by_content(article, "./ul[@class='rlist--inline separator']/li", "Published:")
                release_date = release_date_elem.xpath(".//span[last()]/text()").extract_first()
            except Exception as e:
                release_date = ""

            pdf_link = urlparse.urljoin(response.url, article.xpath(".//li[@class='readcubeEPdfLink']/a/@href").extract_first())
            doi = Utils.regex_extract(article_url, ".*onlinelibrary.wiley.com/doi/(.*)")

            meta =  {
                'journal' : journal,
                "title" : title,
                "release_date" : release_date,
                "volume" : volume,
                "issue" : issue,
                "page" : page,
                "pdf_link": pdf_link,
                'journal_url': response.url,
                "access_url" : article_url,
                "author" : author,
                "doi": doi,
            }

            yield response.follow(article_url, self.parse_journal_wiley_article_new, meta = meta)

    #主要是为了获得摘要
    def parse_journal_wiley_article_new(self, response):
        abstract = Utils.get_all_inner_texts(response, "//div[@class='article-section__content en main']")
        yield {
            'journal' : response.meta["journal"],
            "title" : response.meta["title"],
            "release_date" : response.meta["release_date"],
            "volume" : response.meta["volume"],
            "issue" : response.meta["issue"],
            "page" : response.meta["page"],
            "pdf_link": response.meta["pdf_link"],
            'journal_url': response.meta["journal_url"],
            "access_url" : response.meta["access_url"],
            "author" : response.meta["author"],
            "doi": response.meta["doi"],
            "abstract": abstract,
        }

    def parse_journal_100(self, response):
        self.logger.info("Get an journal page for journal 100: %s", response.url)
        fields = response.url.split('/t')
        size = len(fields)

        # url must be like http://www.tandfonline.com/toc/kcll20/{volume_id}/{issue_id}
        volumd = fields[size - 2]
        issue = fields[size - 1]

        journal = response.xpath("//div[@class='journalMetaTitle page-heading']//span/text()").extract_first()

        articles = response.xpath("//form[@name='frmAbs']//div[@class='tocContent']/table")
        for article in articles:
            title = article.xpath(".//div[@class='art_title linkable']//span/text()").extract()
            page = article.xpath(".//div[@class='tocPageRange maintextleft']/text()").extract_first().split(':')[1]
            date = article.xpath(".//div[@class='tocEPubDate']/span/text()").extract_first().split(' ')[3]
            doi = article.xpath(".//div[@class='art_title linkable']/a/@href").extract_first().replace("/doi/full/", "")
            link = str(urlparse.urljoin(response,url, article.xpath(".//a[@class='ref nowrap pdf']/@href").extract()))

            yield {
                'journal_id' : 100,
                'journal' : journal,
                'title' : title,
                'date' : date,
                'vol' : volumd_id,
                'issue' : issue,
                'page' : page,
                'doi' : doi,
                'link' : link
            }





    def parse_issue(self, response):
        self.logger.info('Get an issue page: %s', response.url)


        sections=response.css("div#content-block form div")
        for section in sections:
            section_name = section.css("h2 span::text").extract()
            cit_list = section.css("ul.cit-list > li")
            for cit in cit_list:
                cit_metadata = cit.css("div.cit-metadata")
                title = cit_metadata.css("h4::text").extract_first()
                print_date = cit_metadata.css(".cit-print-date::text").extract()
                vol = cit_metadata.css(".cit-vol::text").extract()
                issue = cit_metadata.css(".cit-issue::text").extract()
                page_count = cit_metadata.css(".cit-page-count::text").extract()
                elocation = cit_metadata.css(".cit-elocation::text").extract()
                link = cit_metadata.css("div.cit-extra a[rel='full-text.pdf']::attr(href)").extract()

                yield {
                    'scetion' : section_name,
                    'title' : title,
                    'date' : print_date,
                    'vol' : vol,
                    'issue' : issue,
                    'page_count' : page_count,
                    'elocation' : elocation,
                    'link' : link,
                }
