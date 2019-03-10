#coding=utf-8
from __future__ import absolute_import

from scrapy import Request
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from scrapy.loader.processors import Identity
from scrapy.spiders import Rule

from ..utils.spiders import BasePortiaSpider
from ..utils.starturls import FeedGenerator, FragmentGenerator
from ..utils.processors import Item, Field, Text, Number, Price, Date, Url, Image, Regex
from ..items import PortiaItem
from ..spiders.utils import Utils


class sciencesocieties(BasePortiaSpider):
    name = "sciencesocieties"
    allowed_domains = ["dl.sciencesocieties.org"]
    start_urls = [
        #'https://dl.sciencesocieties.org/publications/tpg/index',
        'https://dl.sciencesocieties.org/publications/ael/index'
    ]
    rules = [
        Rule(
            LinkExtractor(
                allow=(
                    u'dl.sciencesocieties.org/publications/.*/tocs/\d*/\d*$',
                ),
            ),
        ),
        Rule(
            LinkExtractor(
                allow=(
                    u'tpg/abstracts/\d+/\d+/.+$',
                    u'ael/abstracts/\d+/\d+/.+$',
                ),
            ),
            callback='parse_item',
            follow=True
        )
    ]

    def extract_title(response):
        return response.xpath("//h1[@class='page-title']/text()").extract()

    def extract_sup(response):
        sups = []
        for elem in response.css(".contributor-list li"):
            sups.append(",".join(elem.xpath("./span[@class='sup']/sup/text()").extract()))
        return sups

    def extract_pdf_url(response):
        elem = Utils.select_element_by_content(response, "//div[@class='cb-contents']//div/a", "Full Text (PDF)")
        return elem.xpath("./@href").extract_first()

    items = [[Item(PortiaItem, None,
                   u'',
                   [
                       #---------母体---------
                       Field(u'collection',  #文献集合名称，一般是期刊名或者书名
                             '.breadcrumb > a:nth-of-type(3)',
                             [],  #抽取规则，比如Regex(u'DOI: (\\S+)')
                             ),
                       Field(u'collection_url',  #文献集合url,
                             '',
                             [],
                             ),

                       #---------来源平台-------
                       Field(u'source',  #信息来源名称, 必备!!
                             '',  #可以填写固定值
                             [],
                             ),
                       Field(u'source_url',  #信息来源平台URL, 必备!!
                             '',
                             [],
                             ),

                       #---------出版信息---------
                       Field(u'release_year',  #必备!!
                             '',
                             [],
                             ),
                       Field(u'release_date',  #1900-01-01, 如时间只有年月，则按照XXXX-XX-01著录；如时间只有季度，则按照XXXX-1st Quarter著录
                             'div:last-of-type insert-date',
                             [],
                             ),
                       Field(u'volumn',
                             '.slug-vol volume',
                             [],
                             ),
                       Field(u'issue',  #有可能是非数字
                             '.slug-issue issue',
                             [],
                             ),
                       Field(u'publisher',  #使用;分隔
                             '',
                             [],
                             ),
                       Field(u'place_of_publication',  #
                             '',
                             [],
                             ),

                       #-----------作品----------
                       Field(u'title',  #必备!!
                             extract_title,
                             [],
                             ),
                       Field(u'subtitle',
                             '',
                             [],
                             ),
                       Field(u'author',  #作者, ;分隔
                             '.contributor-list li span:first-of-type',
                             [],
                             ),
                       Field(u'author_sup',  #作者, ;分隔
                             extract_sup,
                             [],
                             ),
                       Field(u'author_affiliation',  #作者, ;分隔
                             '.aff address',
                             [],
                             ),
                       Field(u'EISBN',  #电子出版物书号
                             '',
                             [],
                             ),
                       Field(u'hardcover_PISBN',  #
                             '',
                             [],
                             ),
                       Field(u'ISSN',  #印本刊号
                             '',
                             [],
                             ),
                       Field(u'EISSN',  #电子刊号
                             '',
                             [],
                             ),
                       Field(u'DOI',  #
                             'article-id',
                             [],
                             ),
                       Field(u'keywords',  #
                             '#articleAbbreviations .kwd-group span',
                             [],
                             ),
                       Field(u'abstracts',
                             'div.abstract',
                             [],
                             ),
                       Field(u'access_url',  #必备!!
                             '',
                             [],
                             ),
                       Field(u'pdf_url',  #必备!!
                             extract_pdf_url,
                             [],
                             ),
                       Field(u'pages',
                             '',
                             [],
                             ),

                       #-------载体类型--------
                       Field(u'document_type',
                             '',
                             [],
                             ),

                   ])]]
