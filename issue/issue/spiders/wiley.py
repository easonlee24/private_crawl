# -*- coding: utf-8 -*-
import scrapy
from scrapy.spider import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

import urlparse

class WileySpider(CrawlSpider):
    name = 'wiley'
    allowed_domains = [
        'jvi.asm.org',
        'dl.sciencesocieties.org', #10
        'onlinelibrary.wiley.com',
        ]
    start_urls = [
        'http://onlinelibrary.wiley.com/journal/10.1111/(ISSN)1365-2435/issues', #102
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
    ]

    rules = (
        # Extract links matching 'item.php' and parse them with the spider's method parse_item
        Rule(LinkExtractor(allow=('onlinelibrary.wiley.com/doi/.*/.*/issuetoc', )), callback='parse_journal_wiley'),
        Rule(LinkExtractor(allow=('issue/.*issue-\d+/$', )), callback='parse_journal_wiley'),

        # Extract links matching 'category.php' (but not matching 'subsection.php')
        # and follow links from them (since no callback means follow=True by default).
        Rule(LinkExtractor(allow=(
                '.*journal/.*/issues/201[2-7]/$', #102
                #'.*journal/10.1111/\(ISSN\)1365\-2443/issues\?activeYear=201[2-7]$', #103
                #'.*journal/10.1002/\(ISSN\)1521\-6551/issues\?activeYear=201[2-7]$', #104
                #'.*journal/10.1111/\(ISSN\)1600\-048X/issues\?activeYear=201[2-7]$', #105
                #'.*journal/10.1111/\(ISSN\)1364\-3703/issues\?activeYear=201[2-7]$', #106
                #'.*journal/10.1111/\(ISSN\)1756\-1051/issues\?activeYear=201[2-7]$', #107
                #'.*journal/10.1111/\(ISSN\)1600\-0706/issues\?activeYear=201[2-7]$', #108
                #'.*journal/10.1111/\(ISSN\)1440\-1835/issues\?activeYear=201[2-7]$', #109
                #'.*journal/10.1111/\(ISSN\)1442\-1984/issues\?activeYear=201[2-7]$', #110
                #'.*journal/10.1111/\(ISSN\)1439\-0531/issues\?activeYear=201[2-7]$', #111
                #'.*journal/10.1111/\(ISSN\)1445\-6664/issues\?activeYear=201[2-7]$', #112
                #'.*journal/10.1111/\(ISSN\)1744\-697X/issues\?activeYear=201[2-7]$', #113
                #'.*journal/10.1002/\(ISSN\)1938\-5455/issues\?activeYear=201[2-7]$', #115
                #'.*journal/10.1111/\(ISSN\)1468\-2257/issues\?activeYear=201[2-7]$', #131
                #'.*journal/10.1111/\(ISSN\)1744\-7976/issues\?activeYear=201[2-7]$', #132
                #'.*journal/10.1111/\(ISSN\)1471\-0366/issues\?activeYear=201[2-7]$', #133
                #'.*journal/10.1111/\(ISSN\)1095\-8312/issues\?activeYear=201[2-7]$', #134
                #'.*journal/10.1002/\(ISSN\)1460\-2075/issues\?activeYear=201[2-7]$', #135
                #'.*journal/10.1002/\(ISSN\)1469\-3178/issues\?activeYear=201[2-7]$', #136
                #'.*journal/10.1111/\(ISSN\)1096\-3642/issues\?activeYear=201[2-7]$', #137
                #'.*journal/10.1111/\(ISSN\)1939\-165X/issues\?activeYear=201[2-7]$', #138
                #'.*journal/10.1002/\(ISSN\)1099\-0755/issues\?activeYear=201[2-7]$', #40
                #'.*journal/10.1111/\(ISSN\)1472\-4669/issues\?activeYear=201[2-7]$', #41
                #'.*journal/10.1111/\(ISSN\)1745\-4514/issues\?activeYear=201[2-7]$', #42
                #'.*journal/10.1111/\(ISSN\)1745\-4549/issues\?activeYear=201[2-7]$', #43
                #'.*journal/10.1111/\(ISSN\)1745\-4557/issues\?activeYear=201[2-7]$', #44
                #'.*journal/10.1111/\(ISSN\)1745\-4565/issues\?activeYear=201[2-7]$', #45
                #'.*journal/10.1002/\(ISSN\)1520\-6327/issues\?activeYear=201[2-7]$', #46
                #'.*journal/10.1002/\(ISSN\)1618\-2863/issues\?activeYear=201[2-7]$', #47
                #'.*journal/10.1111/\(ISSN\)1365\-2052/issues\?activeYear=201[2-7]$', #48
                #'.*journal/10.1111/\(ISSN\)1469\-8137/issues\?activeYear=201[2-7]$', #49
                #'.*journal/10.1021/\(ISSN\)1520\-6033/issues\?activeYear=201[2-7]$', #57
                #'.*journal/10.1111/\(ISSN\)1744\-7429/issues\?activeYear=201[2-7]$', #58
                #'.*journal/10.1111/\(ISSN\)1440\-169X/issues\?activeYear=201[2-7]$', #59
                #'.*journal/10.1111/\(ISSN\)1600\-0633/issues\?activeYear=201[2-7]$', #60
                #'.*journal/10.1111/\(ISSN\)1748\-5967/issues\?activeYear=201[2-7]$', #61
                #'.*journal/10.1111/\(ISSN\)1479\-8298/issues\?activeYear=201[2-7]$', #62
                #'.*journal/10.1111/\(ISSN\)1365\-2095/issues\?activeYear=201[2-7]$', #63
                #'.*journal/10.1111/\(ISSN\)1748\-7692/issues\?activeYear=201[2-7]$', #64
                #'.*journal/10.1111/\(ISSN\)1365\-3024/issues\?activeYear=201[2-7]$', #65
                #'.*journal/10.1111/\(ISSN\)1550\-7408/issues\?activeYear=201[2-7]$', #66
                #'.*journal/10.1111/\(ISSN\)1439\-0426/issues\?activeYear=201[2-7]$', #68
                #'.*journal/10.1111/\(ISSN\)2041\-210X/issues\?activeYear=201[2-7]$', #69
                #'.*journal/10.1002/\(ISSN\)1757\-7012/issues\?activeYear=201[2-7]$', #70
                #'.*journal/10.1002/\(ISSN\)1757\-7799/issues\?activeYear=201[2-7]$', #71
                #'.*journal/10.1111/\(ISSN\)1759\-7692/issues\?activeYear=201[2-7]$', #72
                #'.*journal/10.1002/\(ISSN\)1936\-0592/issues\?activeYear=201[2-7]$', #75
                #'.*journal/10.1002/\(ISSN\)1521\-1878/issues\?activeYear=201[2-7]$', #76
                #'.*journal/10.1002/\(ISSN\)2042\-5805/issues\?activeYear=201[2-7]$', #77
                #'.*journal/10.1002/\(ISSN\)2152\-3878/issues\?activeYear=201[2-7]$', #78
                #'.*journal/10.1111/\(ISSN\)1740\-0929/issues\?activeYear=201[2-7]$', #79
                #'.*journal/10.1111/\(ISSN\)1939\-7445/issues\?activeYear=201[2-7]$', #81
                #'.*journal/10.1111/\(ISSN\)1759\-0884/issues\?activeYear=201[2-7]$', #82
                #'.*journal/10.1111/\(ISSN\)1467\-7652/issues\?activeYear=201[2-7]$', #87
                #'.*journal/10.1111/\(ISSN\)1439\-0329/issues\?activeYear=201[2-7]$', #88
                #'.*journal/10.1111/\(ISSN\)1753\-5131/issues\?activeYear=201[2-7]$', #89
                #'.*journal/10.1002/\(ISSN\)1938\-5463a/issues\?activeYear=201[2-7]$', #90
                #'.*journal/10.1002/\(ISSN\)1526\-968X/issues\?activeYear=201[2-7]$', #91
                #'.*journal/10.1002/\(ISSN\)1522\-239Xb/issues\?activeYear=201[2-7]$' #92
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
                page = article.xpath(".//div[@class='citation tocArticle']/a/span/text()").extract_first().split()[1].strip(')')

                elems = article.xpath(".//div[@class='citation tocArticle']/p[last()]/text()").extract_first().split('|')
                doi = elems[1].split(':')[1].strip()

                link = urlparse.urljoin(response.url, article.xpath(".//ul[@class='productMenu']/li[3]/a/@href").extract_first())

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
