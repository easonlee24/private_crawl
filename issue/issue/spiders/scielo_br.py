#coding=utf-8
from __future__ import absolute_import

from scrapy import Request
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from scrapy.loader.processors import Identity
from scrapy.spiders import Rule

from ..utils.spiders import BasePortiaSpider
from ..utils.starturls import FeedGenerator, FragmentGenerator
from ..utils.processors import Item, Field, Text, Number, Price, Date, Url, Image, Regex,Identity
from ..items import PortiaItem
from ..spiders.utils import Utils
import urlparse


class ScieloBr(BasePortiaSpider):
    name = "scielo_br"
    allowed_domains = [u'www.scielo.br', u'www.scielo.org.mx']
    start_urls = [
        #OA补漏
        'http://www.scielo.br/scielo.php?script=sci_issuetoc&pid=0102-093520170001&lng=en&nrm=iso',
        'http://www.scielo.br/scielo.php?script=sci_issuetoc&pid=0102-093520170002&lng=en&nrm=iso',
        'http://www.scielo.br/scielo.php?script=sci_issuetoc&pid=0102-093520170003&lng=en&nrm=iso',
        'http://www.scielo.br/scielo.php?script=sci_issuetoc&pid=0102-093520170004&lng=en&nrm=iso',
        'http://www.scielo.br/scielo.php?script=sci_issuetoc&pid=0102-093520170005&lng=en&nrm=iso',
        'http://www.scielo.br/scielo.php?script=sci_issuetoc&pid=0102-093520170006&lng=en&nrm=iso',
        'http://www.scielo.br/scielo.php?script=sci_issuetoc&pid=1679-395120160007&lng=en&nrm=iso',
        'http://www.scielo.br/scielo.php?script=sci_issuetoc&pid=1980-509820100001&lng=pt&nrm=iso',
        'http://www.scielo.br/scielo.php?script=sci_issuetoc&pid=1980-509820100002&lng=pt&nrm=iso',
        'http://www.scielo.br/scielo.php?script=sci_issuetoc&pid=1980-509820100003&lng=pt&nrm=iso',
        'http://www.scielo.br/scielo.php?script=sci_issuetoc&pid=1980-509820100004&lng=pt&nrm=iso',
        'http://www.scielo.br/scielo.php?script=sci_issuetoc&pid=1980-509820110001&lng=pt&nrm=iso',
        'http://www.scielo.br/scielo.php?script=sci_issuetoc&pid=1980-509820110002&lng=pt&nrm=iso',
        'http://www.scielo.br/scielo.php?script=sci_issuetoc&pid=1980-509820110003&lng=pt&nrm=iso',
        'http://www.scielo.br/scielo.php?script=sci_issuetoc&pid=1980-509820110004&lng=pt&nrm=iso',
        'http://www.scielo.br/scielo.php?script=sci_issuetoc&pid=1980-509820120001&lng=pt&nrm=iso',
        'http://www.scielo.br/scielo.php?script=sci_issuetoc&pid=1980-509820120002&lng=pt&nrm=iso',
        'http://www.scielo.br/scielo.php?script=sci_issuetoc&pid=1980-509820120003&lng=pt&nrm=iso',
        'http://www.scielo.br/scielo.php?script=sci_issuetoc&pid=1980-509820120004&lng=pt&nrm=iso',
        'http://www.scielo.br/scielo.php?script=sci_issuetoc&pid=1980-509820130001&lng=pt&nrm=iso',
        'http://www.scielo.br/scielo.php?script=sci_issuetoc&pid=1980-509820130002&lng=pt&nrm=iso',
        'http://www.scielo.br/scielo.php?script=sci_issuetoc&pid=1980-509820130003&lng=pt&nrm=iso',
        'http://www.scielo.br/scielo.php?script=sci_issuetoc&pid=1980-509820130004&lng=pt&nrm=iso',
        'http://www.scielo.br/scielo.php?script=sci_issuetoc&pid=1980-576420100001&lng=en&nrm=iso',
        'http://www.scielo.br/scielo.php?script=sci_issuetoc&pid=1980-576420100002&lng=en&nrm=iso',
        'http://www.scielo.br/scielo.php?script=sci_issuetoc&pid=1980-576420100003&lng=en&nrm=iso',
        'http://www.scielo.br/scielo.php?script=sci_issuetoc&pid=1980-576420100004&lng=en&nrm=iso',
        'http://www.scielo.br/scielo.php?script=sci_issuetoc&pid=1980-576420110001&lng=en&nrm=iso',
        'http://www.scielo.br/scielo.php?script=sci_issuetoc&pid=1980-576420110002&lng=en&nrm=iso',
        'http://www.scielo.br/scielo.php?script=sci_issuetoc&pid=1980-576420110003&lng=en&nrm=iso',
        'http://www.scielo.br/scielo.php?script=sci_issuetoc&pid=1980-576420110004&lng=en&nrm=iso',
        'http://www.scielo.br/scielo.php?script=sci_issuetoc&pid=1980-576420120001&lng=en&nrm=iso',
        'http://www.scielo.br/scielo.php?script=sci_issuetoc&pid=1980-576420120002&lng=en&nrm=iso',
        'http://www.scielo.br/scielo.php?script=sci_issuetoc&pid=1980-576420120003&lng=en&nrm=iso',
        'http://www.scielo.br/scielo.php?script=sci_issuetoc&pid=1980-576420120004&lng=en&nrm=iso',
        'http://www.scielo.br/scielo.php?script=sci_issuetoc&pid=1980-576420130002&lng=en&nrm=iso',
        'http://www.scielo.br/scielo.php?script=sci_issuetoc&pid=1980-576420130003&lng=en&nrm=iso',
        'http://www.scielo.br/scielo.php?script=sci_issuetoc&pid=1980-576420130004&lng=en&nrm=iso',
        'http://www.scielo.br/scielo.php?script=sci_issuetoc&pid=0031-104920160001&lng=pt&nrm=iso',
        'http://www.scielo.br/scielo.php?script=sci_issuetoc&pid=0031-104920160005&lng=pt&nrm=iso',
        'http://www.scielo.br/scielo.php?script=sci_issuetoc&pid=0031-104920160017&lng=pt&nrm=iso',
        'http://www.scielo.br/scielo.php?script=sci_issuetoc&pid=0031-104920170002&lng=pt&nrm=iso',
        'http://www.scielo.br/scielo.php?script=sci_issuetoc&pid=0031-104920170010&lng=pt&nrm=iso',
        'http://www.scielo.br/scielo.php?script=sci_issuetoc&pid=0031-104920170015&lng=pt&nrm=iso',
        'http://www.scielo.br/scielo.php?script=sci_issuetoc&pid=0031-104920170017&lng=pt&nrm=iso',
        'http://www.scielo.br/scielo.php?script=sci_issuetoc&pid=0031-104920170036&lng=pt&nrm=iso',
        'http://www.scielo.br/scielo.php?script=sci_issuetoc&pid=0031-104920170039&lng=pt&nrm=iso',
        'http://www.scielo.br/scielo.php?script=sci_issuetoc&pid=0031-104920170040&lng=pt&nrm=iso',
        'http://www.scielo.br/scielo.php?script=sci_issuetoc&pid=1808-243220160001&lng=en&nrm=iso',
        'http://www.scielo.br/scielo.php?script=sci_issuetoc&pid=1808-243220160002&lng=en&nrm=iso',
        'http://www.scielo.org.mx/scielo.php?script=sci_issuetoc&pid=0185-330920100001&lng=en&nrm=iso',
        'http://www.scielo.org.mx/scielo.php?script=sci_issuetoc&pid=0185-330920100002&lng=en&nrm=iso',
        'http://www.scielo.org.mx/scielo.php?script=sci_issuetoc&pid=0185-330920110001&lng=en&nrm=iso',
        'http://www.scielo.org.mx/scielo.php?script=sci_issuetoc&pid=0185-330920110002&lng=en&nrm=iso',
        'http://www.scielo.org.mx/scielo.php?script=sci_issuetoc&pid=0185-330920120001&lng=en&nrm=iso',
        'http://www.scielo.org.mx/scielo.php?script=sci_issuetoc&pid=0185-330920120002&lng=en&nrm=iso',
        'http://www.scielo.org.mx/scielo.php?script=sci_issuetoc&pid=0185-330920140001&lng=en&nrm=iso',
        'http://www.scielo.org.mx/scielo.php?script=sci_issuetoc&pid=0185-330920140002&lng=en&nrm=iso',
        'http://www.scielo.org.mx/scielo.php?script=sci_issuetoc&pid=0185-330920150001&lng=en&nrm=iso',
        'http://www.scielo.org.mx/scielo.php?script=sci_issuetoc&pid=0185-330920150002&lng=en&nrm=iso',
        'http://www.scielo.br/scielo.php?script=sci_issuetoc&pid=2175-786020100001&lng=en&nrm=iso',
        'http://www.scielo.br/scielo.php?script=sci_issuetoc&pid=2175-786020100002&lng=en&nrm=iso',
        'http://www.scielo.br/scielo.php?script=sci_issuetoc&pid=2175-786020100003&lng=en&nrm=iso',
        'http://www.scielo.br/scielo.php?script=sci_issuetoc&pid=2175-786020100004&lng=en&nrm=iso',
        'http://www.scielo.br/scielo.php?script=sci_issuetoc&pid=2175-786020100005&lng=en&nrm=iso',
        'http://www.scielo.br/scielo.php?script=sci_issuetoc&pid=2175-786020110001&lng=en&nrm=iso',
        'http://www.scielo.br/scielo.php?script=sci_issuetoc&pid=2175-786020110002&lng=en&nrm=iso',
        'http://www.scielo.br/scielo.php?script=sci_issuetoc&pid=2177-705520160001&lng=pt&nrm=is',
        'http://www.scielo.br/scielo.php?script=sci_issuetoc&pid=2177-705520160002&lng=pt&nrm=is',
        'http://www.scielo.br/scielo.php?script=sci_issuetoc&pid=2177-705520160003&lng=pt&nrm=is',
        'http://www.scielo.br/scielo.php?script=sci_issuetoc&pid=2177-705520170001&lng=pt&nrm=is',
        'http://www.scielo.br/scielo.php?script=sci_issuetoc&pid=2177-705520170002&lng=pt&nrm=is',
        'http://www.scielo.br/scielo.php?script=sci_issuetoc&pid=2177-705520170003&lng=pt&nrm=is',
        'http://www.scielo.br/scielo.php?script=sci_issuetoc&pid=0101-662820160001&lng=en&nrm=iso',
        'http://www.scielo.br/scielo.php?script=sci_issuetoc&pid=0101-662820160002&lng=en&nrm=iso',
        'http://www.scielo.br/scielo.php?script=sci_issuetoc&pid=0101-662820160003&lng=en&nrm=iso',
        'http://www.scielo.br/scielo.php?script=sci_issuetoc&pid=0101-662820170001&lng=en&nrm=iso',
        'http://www.scielo.br/scielo.php?script=sci_issuetoc&pid=0101-662820170002&lng=en&nrm=iso',
        'http://www.scielo.br/scielo.php?script=sci_issuetoc&pid=0101-662820170003&lng=en&nrm=iso',
        'http://www.scielo.br/scielo.php?script=sci_issuetoc&pid=1984-467020170001&lng=en&nrm=iso'
        u'http://www.scielo.org.mx/scielo.php?script=sci_issues&pid=0185-3309&lng=en&nrm=iso',
        u'http://www.scielo.br/scielo.php?script=sci_issues&pid=0102-0935&lng=en&nrm=iso',
        'http://www.scielo.br/scielo.php?script=sci_arttext&pid=S0100-204X2000000900007&lng=en&nrm=iso&tlng=pt'
        'http://www.scielo.br/scielo.php?script=sci_arttext&pid=S0102-09351999000600014&lng=en&nrm=iso&tlng=pt'
        'http://www.scielo.br/scielo.php?script=sci_arttext&pid=S0102-09352011000500030&lng=en&nrm=iso&tlng=pt',
        'http://www.scielo.br/scielo.php?script=sci_arttext&pid=S0102-09352011000600001&lng=en&nrm=iso&tlng=pt',
        'http://www.scielo.br/scielo.php?script=sci_arttext&pid=S0100-204X2015000900854&lng=en&nrm=iso&tlng=pt'
    ]
    rules = [
        #Rule(
        #    LinkExtractor(
        #        allow=(
        #            u'script=sci_issuetoc&pid=.*&lng=en&nrm=iso$'
        #        ),
        #    )),
        Rule(
            LinkExtractor(
                allow=(
                    u'script=sci_arttext&pid=.*&lng=en&nrm=iso&tlng=en',
                    u'script=sci_arttext&pid=.*&lng=en&nrm=iso&tlng=pt'
                ),),
            callback='parse_item',
            )
    ]

    def get_pdf(response):
        try:
            pdf_link_elem = Utils.select_element_by_content(response, "//*[@id='toolBox']/div/ul/li/a", "English (pdf)|Portuguese (pdf)")
        except Exception as e:
            return ""
        pdf_link = pdf_link_elem.xpath("@href").extract_first()
        pdf_link = urlparse.urljoin(response.url, pdf_link)
        return pdf_link

    def get_title(response):
        #title也有多种情况..醉了
        title = response.xpath("//p[@class='trans-title']/text()").extract_first()
        if title is None:
            title = response.xpath("//p[@class='title']/text()").extract_first()
            if title is None:
                try:
                    title_elem = response.xpath("//div[contains(@class, 'index')]//p[@align='CENTER']")[0]
                    title = " ".join(title_elem.xpath(".//text()").extract())
                except Exception as e:
                    top_a_elem = response.xpath("//div[contains(@class, 'index')]//a[@name='top']")
                    title = top_a_elem.xpath("./..//b/text()").extract_first()
                    if title is None:
                        title_elem = response.xpath("//div[contains(@class, 'index')]/p")[2]
                        title = " ".join(title_elem.xpath(".//text()").extract())

        print "title is %s" % title
        return Utils.format_text(title)

    def get_abstract(response):
        try:
            abstract_elem = Utils.select_element_by_content(response, "//div[contains(@class, 'index')]//p", "ABSTRACT|Abstract")
            abstract_text = Utils.get_all_inner_texts(abstract_elem, "./following-sibling::p[1]")
            return abstract_text
        except Exception as e:
            return ""

    def get_keyword(response):
        try:
            keyword_elem = Utils.select_element_by_content(response, "//div[contains(@class, 'index')]//p", "Keywords|Index terms|Key words")
            keyword_text = "".join(keyword_elem.xpath(".//text()").extract()).replace("Keywords:", "").split(",")
        except Exception as e:
            return ""
        return keyword_text

    def get_author(response):
        #有两种格式的author
        try:
            author = response.xpath("//div[@class='autores']/p[@class='author']/span[@class='author-name']/text()").extract()
            if len(author) == 0:
                sup_elem = response.xpath("//div[contains(@class, 'index')]/p//sup")[0]
                author_elem = sup_elem.xpath('./..')
                tag_name = author_elem.xpath('name()').extract_first()
                while tag_name != "p":
                    author_elem = author_elem.xpath('./..')
                    tag_name = author_elem.xpath('name()').extract_first()
                    
                author_raw_text = author_elem.extract()
                author = author_raw_text
        except Exception as e:
            return ""

        return author

    def get_author_sup(response):
        #有两种格式的author_sup
        try:
            author_sup = response.xpath("//div[@class='autores']/p[@class='author']/sup/a/text()").extract()
            if len(author_sup) == 0:
                i = 0
                num = 1 #len(response.xpath("//div[contains(@class, 'index')]/p//sup"))
                sup_elem = response.xpath("//div[contains(@class, 'index')]/p//sup")[0]
                author_elem = sup_elem.xpath("./..")
                author_sup = author_elem.xpath("./sup/text()").extract()
        except Exception as e:
            return ""

        return author_sup

    def get_author_affiliation(response):
        #有两种格式的author_affiliation
        try:
            author_aff = []
            elems = response.xpath("//p[@class='aff']")
            for elem in elems:
                txt = " ".join(elem.xpath(".//text()").extract()).strip().replace("\n", "")
                txt = ' '.join(txt.split()) #remove multi space
                author_aff.append(txt)

            if len(author_aff) == 0:
                sup_elem = response.xpath("//div[contains(@class, 'index')]/p//sup")[-1]
                author_raw_text = sup_elem.xpath("./..").extract()
                author_aff = author_raw_text
                print "author affiliation is :%s" % author_aff
        except Exception as e:
            return  ""
        return author_aff

    items = [[Item(PortiaItem,
                   None,
                   '',
                   [Field(u'pdf_link',
                          get_pdf,
                          []),
                       Field(u'journal',
                             '.content h2 a',
                             []),
                       Field(u'print_issn',
                             'h2:nth-child(6) *::text',
                             [Regex(u'Print version ISSN (\\d+-\\d+)')]),
                       Field(u'online_issn',
                             'h2:nth-child(6) *::text',
                             [Regex(u'On-line version ISSN (\\d+-\\d+)')]),
                       Field(u'issue',
                             'h3 *::text',
                             [Regex(u'.*(no\\.|supl\\.|n\\.)(\\d+).*$')]),
                       Field(u'volumn',
                             'h3 *::text',
                             [Regex(u'(vol\\.\\d+|ahead of print)')]),
                       Field(u'date',
                             'h3 *::text',
                             [Regex(u'.*(\\d{4})$')]),
                       Field(u'doi',
                             'h4 *::text',
                             [Regex(u'dx.doi.org/(.*)')]),
                       Field(u'title',
                             get_title,
                             []),
                       Field(u'author_raw',
                             get_author,
                             []),
                       #Field(u'author_sup',
                       #      get_author_sup,
                       #      []),
                       #Field(u'author_affiliation_raw', #如果命名为author_affiliation，那么因为此field已经在item里面注册了process，爬取到的数据标签会被处理掉
                       #      get_author_affiliation,
                       #      []),
                       Field(u'abstracts',
                             get_abstract,
                             []),
                       Field(u'keywords',
                             get_keyword,
                             []),
                       Field(u'copyright',
                             '.copyright *::text',
                             []),
                       Field(u'license_text',
                             '.license',
                             []),
                       Field(u'license_url',
                             '.license a:first-child::attr(href)',
                             [])])]]
