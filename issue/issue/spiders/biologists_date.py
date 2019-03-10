#coding=utf-8
from __future__ import absolute_import

from scrapy import Request
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from scrapy.loader.processors import Identity
from scrapy.spiders import Rule

from dateparser.date import DateDataParser
from ..utils.spiders import BasePortiaSpider
from ..utils.starturls import FeedGenerator, FragmentGenerator
from ..utils.processors import Item, Field, Text, Number, Price, Date, Url, Image, Regex
from ..items import PortiaItem
from ..spiders.utils import  Utils
import urlparse

class biologists_date(BasePortiaSpider):
    name = "biologists_date"
    allowed_domains = []
    start_urls = [
        u'http://bio.biologists.org/',
    ]
    rules = [
        Rule(
            LinkExtractor(
                allow=(
                    'biologists.org/content/by/year/201[5-8]$',
                ),
            )
        ),
        Rule(
            LinkExtractor(
                allow=(
                    u'biologists.org/content/\d+/\d+$',
                ),
            ),
            callback='parse_url',
            follow=True)
    ]

    def parse_url(self, response):
        date = response.xpath("//span[@class='highwire-cite-metadata-date highwire-cite-metadata']//text()").extract_first()
        release_date = DateDataParser().get_date_data(date)['date_obj'].strftime("%Y-%m-%d")
        for article in response.xpath("//a[@class='highwire-cite-linked-title']"):
            url = urlparse.urljoin(response.url, article.xpath("./@href").extract_first())
            yield {
                "url" : url,
                "release_date" : release_date
            }

    items = [[Item(PortiaItem, None,
                   u'#填写sample页面特有的selector',
                   [
                       #---------母体---------
                       Field(u'collection',  #文献集合名称，一般是期刊名或者书名
                             '#此字段的css selector',
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
                             required=True
                             ),
                       Field(u'source_url',  #信息来源平台URL, 必备!!
                             '',
                             [],
                             required=True
                             ),

                       #---------出版信息---------
                       Field(u'release_year',  #必备!!
                             '',
                             [],
                             required=True
                             ),
                       Field(u'release_date',  #1900-01-01, 如时间只有年月，则按照XXXX-XX-01著录；如时间只有季度，则按照XXXX-1st Quarter著录
                             '',
                             [],
                             ),
                       Field(u'volumn',
                             '',
                             [],
                             ),
                       Field(u'issue',  #有可能是非数字
                             '',
                             [],
                             ),
                       Field(u'publisher',  #使用;分隔
                             '',
                             [],
                             required=True
                             ),
                       Field(u'place_of_publication',  #
                             '',
                             [],
                             ),

                       #-----------作品----------
                       Field(u'title',  #必备!!
                             '',
                             [],
                             required=True
                             ),
                       Field(u'subtitle',
                             '',
                             [],
                             ),
                       Field(u'dc:contributor',  #作者, ;分隔
                             '',
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
                             '',
                             [],
                             ),
                       Field(u'keywords',  #
                             '',
                             [],
                             ),
                       Field(u'abstracts',
                             '',
                             [],
                             ),
                       Field(u'access_url',  #必备!!
                             '',
                             [],
                             required=True
                             ),
                       Field(u'pdf_url',  #必备!!
                             '',
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
