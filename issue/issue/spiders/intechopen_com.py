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


class Intechopen(BasePortiaSpider):
    name = "www.intechopen.com"
    allowed_domains = [u'www.intechopen.com']
    start_urls = [u'https://www.intechopen.com/books']
    rules = [
        Rule(
            LinkExtractor(
                allow=(
                    u'https://www.intechopen.com/books/[\\w-]+$',
                    u'https://www.intechopen.com/books/latest/\\d+/list$',
                    u'https://www.intechopen.com/books/[\\w-]+/[\\w-]+$'),
                deny=(
                    u'https://www.intechopen.com/books/editor/',
                    u'https://www.intechopen.com/books/mostdownloaded/')),
            callback='parse_item',
            follow=True)]
    items = [[Item(PortiaItem,
                   None,
                   u'.main-content:nth-child(3)',
                   [Field(u'collection_title',
                          '.lead > a:nth-last-child(2) *::text',
                          []),
                       Field(u'title',
                             'h1.chapterTitle *::text',
                             []),
                       Field(u'doi',
                             '.subtitle *::text',
                             [Regex(u'DOI: (\\S+)')]),
                       Field(u'author_field',
                             '.subtitle *::text',
                             [Regex(u'By (.*) DOI')]),
                       Field(u'author_affliication',
                             '#article-front .metadata-entry *::text',
                             []),
                       Field(u'author',
                             '#article-front > .authors-front *::text',
                             []),
                       Field(u'abstract',
                             '.abstract-front .first *::text',
                             []),
                       Field(u'keywords',
                             '.kwds-front *::text',
                             []),
                       Field(u'pdf_link',
                             '#reg_dow_button::attr(href)',
                             [])]),
              Item(PortiaItem,
                   None,
                   u'.main-content',
                   [Field(u'subject',
                          'h1:nth-child(4) *::text',
                          []),
                    Field(u'title',
                          'h1:nth-child(5) *::text',
                          []),
                    Field(u'doi',
                          '.subtitle *::text',
                          [Regex(u'DOI: (\\S+)')]),
                    Field(u'content',
                          '.subtitle *::text',
                          []),
                    Field(u'abstract',
                          'p:nth-child(7) *::text',
                          []),
                    Field(u'chapters',
                          '.chapter-title::attr(href)',
                          [])]),
              Item(PortiaItem,
                   None,
                   u'.book-listing > li:nth-child(1) > dl > dt',
                   [Field(u'book_link',
                          '.book-listing  dt > a::attr(href)',
                          [])])]]
