#!usr/bin/python
#coding=utf-8
from __future__ import absolute_import

from scrapy import Request
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from scrapy.loader.processors import Identity
from scrapy.spiders import Rule

from ..utils.spiders import BasePortiaSpider
from ..utils.starturls import FeedGenerator, FragmentGenerator
from scrapy.loader.processors import Identity
from ..utils.processors import Item, Field, Text, Number, Price, Date, Url, Image, Regex
from ..items import PortiaItem
from ..spiders.utils import  Utils


class biologists(BasePortiaSpider):
    name = "biologists"
    allowed_domains = []
    start_urls = [
        'http://bio.biologists.org/',
        #'http://bio.biologists.org/content/6/12/1771'
    ]
    rules = [
        Rule(
            LinkExtractor(
                allow=(
                    'biologists.org/content/by/year/201[5-8]$',
                    'biologists.org/content/\d+/\d+$',
                ),
            )),
        Rule(
            LinkExtractor(
                allow=(
                    'biologists.org/content/\d+/\d+/\d+$'
                ),
            ),
            callback='parse_item',
            )
    ]

    def get_issue(response):
        return Utils.regex_extract(response.url, "/content/\d+/(\d+)")


    """
    1. 所有标记了selecotr的field都会输出，未匹配到时，置为空
    """
    items = [[Item(PortiaItem, None,
                   u'',
                   [
                       #---------母体---------
                       Field(u'collection',  #文献集合名称，一般是期刊名或者书名
                             '.has-author-tooltip .highwire-cite-metadata-journal-title',
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
                             '.has-author-tooltip .highwire-cite-metadata-date',
                             [],
                             ),
                       Field(u'volumn',
                             '.has-author-tooltip .highwire-cite-metadata-volume',
                             [],
                             ),
                       Field(u'issue',  #有可能是非数字
                             get_issue,
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
                             '#page-title',
                             [],
                             required=True
                             ),
                       Field(u'subtitle',
                             '',
                             [],
                             ),
                       Field(u'author',  #作者, ;分隔
                             '.has-author-tooltip .highwire-citation-author',
                             [],
                             ),
                       Field(u'author_affiliation',  #作者, ;分隔
                             '.author-tooltip-affiliation > span',
                             [Text()],
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
                             []

                             ),
                       Field(u'DOI',  #
                             '.has-author-tooltip .highwire-cite-metadata-doi',
                             [],
                             ),
                       Field(u'keywords',  #
                             '',
                             [],
                             ),
                       Field(u'abstracts',
                             '.section .abstract',
                             [],
                             ),
                       Field(u'pdf_url',  #必备!!
                             '.item-list li.last a:first-of-type::attr(href)',
                             [],
                        ),
                       Field(u'pages',
                             '.has-author-tooltip .highwire-cite-metadata-pages',
                             [],
                       ),

                       #access_url自动添加
                       #acquisition_time自动添加

                       # -------载体类型--------
                       Field(u'document_type',
                             '.pane-content .field-item',
                             [],
                       ),
                   ]
    )]]
