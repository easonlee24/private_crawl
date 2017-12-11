# -*- coding: utf-8 -*-
import scrapy
from scrapy.spider import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.http.request import Request

import urlparse
import re

class IssueSpider(CrawlSpider):
    name = 'issue'

    #def __init__(self, url_file=None, *args, **kwargs):
    #    self.url_file = url_file

    #def start_requests(self):
    #    with open(self.url_file, "rb") as f:
    #        for line in f:
    #            request_url = line.strip()
    #            yield Request(request_url, self.parse_journal_wiley, dont_filter=True)

    start_urls = [
        #'http://jvi.asm.org/content/by/year',
        #'http://aem.asm.org/content/by/year',
        #'http://jb.asm.org/content/by/year',
        #'http://mmbr.asm.org/content/by/year',
        #'http://mcb.asm.org/content/by/year'
        #'https://dl.sciencesocieties.org/publications/cftm/index' #10
        #'https://dl.sciencesocieties.org/publications/vzj/index',
        #'https://dl.sciencesocieties.org/publications/nse/index'
        #'https://dl.sciencesocieties.org/publications/jpr/index'
        #'http://www.tandfonline.com/loi/kcll20',
        #'http://www.tandfonline.com/loi/kbac20',
        #'http://www.tandfonline.com/loi/kidp20',
        #'http://www.tandfonline.com/loi/tjar20',
        #'http://www.tandfonline.com/loi/kinv20',
        #'http://www.tandfonline.com/loi/kpsb20',
        #'http://www.tandfonline.com/loi/kjks20',
        #'http://www.tandfonline.com/loi/kmge20',
        #'http://www.tandfonline.com/loi/kbim20',
        #'http://www.tandfonline.com/loi/kwrm20',
        #'http://www.tandfonline.com/loi/kspe20'
        #'http://www.wageningenacademic.com/loi/qas'
        #'http://onlinelibrary.wiley.com/doi/10.1111/gtc.2017.22.issue-8/issuetoc'
        'http://onlinelibrary.wiley.com/journal/10.1111/(ISSN)1365-2435/issues',
        'http://onlinelibrary.wiley.com/journal/10.1111/(ISSN)1469-8137/issues',
        'http://onlinelibrary.wiley.com/journal/10.1002/(ISSN)1521-1878/issues',
        'http://onlinelibrary.wiley.com/journal/10.1002/(ISSN)1618-2863/issues',
        'http://onlinelibrary.wiley.com/journal/10.1111/(ISSN)2041-210X/issues'
    ]

    rules = (
        # Extract links matching 'item.php' and parse them with the spider's method parse_item
        #Rule(LinkExtractor(allow=('jvi.asm.org/content/vol\d+/issue\d+/index.dtl$', )), callback='parse_issue'),
        Rule(LinkExtractor(allow=('aem.asm.org/content/vol\d+/issue\d+/index.dtl$', )), callback='parse_issue'),
        Rule(LinkExtractor(allow=('jb.asm.org/content/vol\d+/issue\d+/index.dtl$', )), callback='parse_issue'),
        Rule(LinkExtractor(allow=('mmbr.asm.org/content/vol\d+/issue\d+/index.dtl$', )), callback='parse_issue'),
        Rule(LinkExtractor(allow=('mcb.asm.org/content/vol\d+/issue\d+/index.dtl$', )), callback='parse_issue'),
        Rule(LinkExtractor(allow=('dl.sciencesocieties.org/publications/cftm/tocs/\d*/\d*$', )), callback='parse_journal_10'),
        Rule(LinkExtractor(allow=('dl.sciencesocieties.org/publications/vzj/tocs/\d*/\d*$', )), callback='parse_journal_10'),
        Rule(LinkExtractor(allow=('dl.sciencesocieties.org/publications/nse/tocs/\d*/\d*$', )), callback='parse_journal_10'),
        Rule(LinkExtractor(allow=('dl.sciencesocieties.org/publications/jpr/tocs/\d*/\d*$', )), callback='parse_journal_10'),
        Rule(LinkExtractor(allow=('www.tandfonline.com/toc/kcll20/\d*/\d*\?nav=tocList$', )), callback='parse_journal_100'),
        Rule(LinkExtractor(allow=('www.tandfonline.com/toc/kbac20/\d*/\d*\?nav=tocList$', )), callback='parse_journal_100'),
        Rule(LinkExtractor(allow=('www.tandfonline.com/toc/kidp20/\d*/\d*\?nav=tocList$', )), callback='parse_journal_100'),
        Rule(LinkExtractor(allow=('www.tandfonline.com/toc/tjar20/\d*/\d*\?nav=tocList$', )), callback='parse_journal_100'),
        Rule(LinkExtractor(allow=('www.tandfonline.com/toc/kinv20/\d*/\d*\?nav=tocList$', )), callback='parse_journal_100'),
        Rule(LinkExtractor(allow=('www.tandfonline.com/toc/kpsb20/\d*/\d*\?nav=tocList$', )), callback='parse_journal_100'),
        Rule(LinkExtractor(allow=('www.tandfonline.com/toc/kjks20/\d*/\d*\?nav=tocList$', )), callback='parse_journal_100'),
        Rule(LinkExtractor(allow=('www.tandfonline.com/toc/kmge20/\d*/\d*\?nav=tocList$', )), callback='parse_journal_100'),
        Rule(LinkExtractor(allow=('www.tandfonline.com/toc/kbim20/\d*/\d*\?nav=tocList$', )), callback='parse_journal_100'),
        Rule(LinkExtractor(allow=('www.tandfonline.com/toc/kwrm20/\d*/\d*\?nav=tocList$', )), callback='parse_journal_100'),
        Rule(LinkExtractor(allow=('onlinelibrary.wiley.com/doi/.*/.*/issuetoc', )), callback='parse_journal_wiley'),
        Rule(LinkExtractor(allow=('www.wageningenacademic.com/toc/qas/\d+/\d+', )), callback='parse_wageningena'),

        # Extract links matching 'category.php' (but not matching 'subsection.php')
        # and follow links from them (since no callback means follow=True by default).
#        Rule(LinkExtractor(allow=('jvi.asm.org/content', ),
#			deny=('jvi.asm.org/content/.*[+=&?#]', 'jvi.asm.org/content/.*full$', 'jvi.asm.org/content/.*figures-only$', 'jvi.asm.org/content/.*abstract'))),
#
        Rule(LinkExtractor(allow=(
                #'.*jvi.asm.org/content/by/year/201[2-7]$', #92
                '.*aem.asm.org/content/by/year/201[2-7]$', #92
                '.*jb.asm.org/content/by/year/201[2-7]$', #92
                '.*mmbr.asm.org/content/by/year/201[2-7]$', #92
                '.*mcb.asm.org/content/by/year/201[2-7]$' #92
            ))),

        Rule(LinkExtractor(allow=(
                '.*journal/10.1111/\(ISSN\)1365\-2435/issues\?activeYear=201[2-7]$', #102
                '.*journal/10.1002/\(ISSN\)1522\-239Xb/issues\?activeYear=201[2-7]$' #92
            ))),

        Rule(LinkExtractor(allow=(
                '.*/loi/kcll20\?open=\d+&year=201[2-7]&repitition=\d+.*', #102
                '.*/loi/kbac20\?open=\d+&year=201[2-7]&repitition=\d+.*', #102
                '.*/loi/kidp20\?open=\d+&year=201[2-7]&repitition=\d+.*', #102
                '.*/loi/tjar20\?open=\d+&year=201[2-7]&repitition=\d+.*', #102
                '.*/loi/kinv20\?open=\d+&year=201[2-7]&repitition=\d+.*', #102
                '.*/loi/kpsb20\?open=\d+&year=201[2-7]&repitition=\d+.*', #102
                '.*/loi/kjks20\?open=\d+&year=201[2-7]&repitition=\d+.*', #102
                '.*/loi/kmge20\?open=\d+&year=201[2-7]&repitition=\d+.*', #102
                '.*/loi/kbim20\?open=\d+&year=201[2-7]&repitition=\d+.*', #102
                '.*/loi/kwrm20\?open=\d+&year=201[2-7]&repitition=\d+.*', #102
            ))),
    )

    def extract_with_css(self, root, query):
        return root.css(query).extract_first().strip()

    def extract_with_xpath(self, root, xpath_str, default_value = ""):
        try:
            result = root.xpath(xpath_str).extract_first().strip()
        except Exception as e:
            result = default_value

        return result

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

                author = article.xpath(".//div[@class='citation tocArticle']/p[1]/text()").extract_first()
                elems =  article.xpath(".//div[@class='citation tocArticle']/p[last()]/text()").extract_first().split('|')
                doi = elems[1].split(':')[1].strip()

                link = urlparse.urljoin(response.url, article.xpath(".//ul[@class='productMenu']/li[3]/a/@href").extract_first())
                abstract = article.xpath(".//div[@class='articleAbstract']//p/text()").extract_first()

                yield {
                    'journal' : journal,
                    "title" : title,
                    "date" : date,
                    "vol" : volume,
                    "issue" : issue,
                    "abstract": abstract,
                    "page" : page,
                    "doi" : doi,
                    "author": author,
                    "pdf_link": link,
                    'journal_url': response.url,
                    "url" : article_url
                }

    def parse_journal_10(self, response):
        self.logger.info('Get an issue page for jorunal 10: %s', response.url)
        start_year = 2012

        fields = response.url.split('/')
        size = len(fields)
        # url must be like dl.sciencesocieties.org/publications/cftm/tocs/{volumd_id}/{issue_id}
        volume = fields[size - 2]
        issue = fields[size -1]

        journal = response.xpath("//div[@id='one']//div[@class='breadcrumb']/a[last()]/text()").extract_first()
        date = response.xpath("//div[@id='tabs']/following::p[1]/text()").extract()[1]

        if int(date) < start_year:
            #only crawl issue >=2012
            return


        sections = response.xpath("//form[@action='/publications/select-items']/ul/li")
        for section in sections:
            articles = section.xpath("./ul/li")
            for article in articles:
                author = article.xpath("./text()").extract_first()
                title_elem = article.css("span")[1]
                title = self.extract_full_text(title_elem)

                texts = title_elem.xpath("./following-sibling::text()[preceding-sibling::br]").extract()
                filter_texts = [x for x in texts if x.strip() != ""]
                doi = filter_texts[0].replace("doi:", "")

                pages = filter_texts[1].split(' ')[-1]

                url = urlparse.urljoin(response.url, article.xpath("./a[2]/@href").extract_first())
                pdf_link = urlparse.urljoin(response.url, article.xpath("./a[3]/@href").extract_first())

                yield {
                    'journal' : journal,
                    'author' : author.strip(),
                    "title" : title,
                    "date" : date,
                    "vol" : volume,
                    "issue" : issue,
                    "doi" : doi,
                    "pdf_link": pdf_link,
                    "url": url,
                    'pages': pages,
                    "pdf_name" : doi.replace("/", "_")
                }

    def parse_journal_100(self, response):
        self.logger.info("Get an journal page for journal 100: %s", response.url)
        fields = response.url.split('/')
        size = len(fields)

        # url must be like http://www.tandfonline.com/toc/kcll20/{volume_id}/{issue_id}
        volume = fields[size - 2]
        issue = fields[size - 1].split('?')[0]

        journal = response.xpath("//div[@class='journalMetaTitle page-heading']//span/text()").extract_first()

        articles = response.xpath("//form[@name='frmAbs']//div[@class='tocContent']/table")
        for article in articles:
            title = " ".join(article.xpath(".//div[@class='art_title linkable']//span")[0].xpath(".//text()").extract())
            page = article.xpath(".//div[@class='tocPageRange maintextleft']/text()").extract_first().split(':')[1].strip()
            date = article.xpath(".//div[@class='tocEPubDate']/span/text()").extract_first().split(' ')[3]
            doi = article.xpath(".//div[@class='art_title linkable']/a/@href").extract_first().replace("/doi/full/", "")
            link = str(urlparse.urljoin(response.url, article.xpath(".//a[@class='ref nowrap pdf']/@href").extract_first()))
            pdf_name = doi.replace("/", "_")
            author = article.xpath(".//span[@class='articleEntryAuthorsLinks']/span/a/text()").extract_first()

            yield {
                'journal' : journal,
                'title' : title,
                'date' : date,
                'volume' : volume,
                'issue' : issue,
                'page' : page,
                'doi' : doi,
                'link' : link,
                'url': response.url,
                'pdf_name': pdf_name,
                'author': author
            }




    def parse_wageningena(self, response):
        print "process url: %s" % response.url
        if response.url == "http://www.wageningenacademic.com/toc/qas/0/0":
            #this is in-press title
            return
        journal = self.extract_with_xpath(response, "//ul[@class='breadcrumbs']/li[2]/a/text()")
        vol_issue_date = response.xpath("//h3[@class='tocListHeader']/text()").extract_first().strip().split(',')
        vol = vol_issue_date[0].replace("Vol.", "").strip()
        issue = vol_issue_date[1].replace("No. ", "").strip()
        date = vol_issue_date[2].strip()

        sections = response.xpath("//div[@class='tocContent']/table")
        for section in sections:
            title = "".join(section.xpath(".//span[@class='hlFld-Title']//text()").extract())
            article_url = urlparse.urljoin(response.url, self.extract_with_xpath(section, "//a[@class='ref nowrap']/@href"))
            authors = ",".join(section.xpath(".//span[@class='articleEntryAuthorsLinks']/a/text()").extract())
            pages = self.extract_with_xpath(section, ".//span[@class='articlePageRange ']/text()").replace("pp. ", "")
            doi = self.extract_with_xpath(section, ".//div[@class='tocArticleDoi']/a/text()").replace("https://doi.org/", "")
            pdf_name = doi.replace("/", "_")
            keywords = ",".join(section.xpath(".//div[@class='tocListKeywords']/a/text()").extract())
            pdf_link = self.extract_with_xpath(section, ".//a[@class='ref nowrap pdf']/@href")
            yield {
                'journal': journal,
                'title': title,
                'date' : date,
                'volume': vol,
                'issue': issue,
                'page': pages,
                'doi': doi,
                'journal_url': response.url,
                'article_url': article_url,
                'pdf_name': pdf_name,
                'pdf_link': pdf_link,
                'author': authors,
                'keywords': keywords,
            }
        

    def parse_issue(self, response):
        self.logger.info('Get an issue page: %s', response.url)


        sections=response.css("div#content-block form div")
        for section in sections:
            section_name = section.css("h2 span::text").extract()
            cit_list = section.css("ul.cit-list > li")
            for cit in cit_list:
                cit_metadata = cit.css("div.cit-metadata")
                title = " ".join(cit_metadata.xpath("./h4//text()").extract())
                title = title.replace("\n", "")
                title = re.sub( '\s+', ' ', title).strip()
                print_date = cit_metadata.css(".cit-print-date::text").extract_first().split()[-1]
                vol = cit_metadata.css(".cit-vol::text").extract_first()
                issue = cit_metadata.css(".cit-issue::text").extract_first()
                start_page = cit_metadata.xpath(".//span[@class='cit-first-page']/text()").extract_first()
                if start_page is None:
                    start_page = ""
                end_page = cit_metadata.xpath(".//span[@class='cit-last-page']/text()").extract_first()
                if end_page is None:
                    end_page = ""

                pdf_link = cit.xpath(".//a[@rel='full-text.pdf']/@href").extract_first()
                doi = cit_metadata.xpath(".//span[@class='cit-doi']/text()").extract_first().strip()
                pdf_name = doi.replace("/", "_")

                url = cit.xpath(".//ul[@class='cit-views']/li[@class='first-item']/a/@href").extract_first().strip()
                url = urlparse.urljoin(response.url, url)
                journal = cit.xpath(".//abbr[@class='site-title']/@title").extract_first()
                author = ','.join(cit.xpath(".//ul[@class='cit-auth-list']//span[@class='cit-auth cit-auth-type-author']/text()").extract())

                yield {
                    'journal': journal,
                    'title' : title,
                    'date' : print_date,
                    'volume' : vol,
                    'issue' : issue,
                    'page': start_page + "-" + end_page,
                    'doi': doi,
                    'journal_url': response.url,
                    'url': url,
                    'pdf_name': pdf_name,
                    'pdf_link' : pdf_link,
                    'author': author
                }
