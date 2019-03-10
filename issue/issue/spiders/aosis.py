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
from dateparser.date import DateDataParser


class Aosis(BasePortiaSpider):
    name = "aosis"
    allowed_domains = []
    f = open("/Users/baidu/work/private_crawl/issue/issue/OA_20180809/aosis_miss_url");
    start_urls = [url.strip() for url in f.readlines()]
    #start_urls = [
    #    u'http://www.satnt.ac.za/issue/archive',
    #    u'http://www.ve.org.za/index.php/VE/issue/archive',
    #    u'http://www.actacommercii.co.za/index.php/acta/issue/archive',
    #    u'http://www.aejonline.org/index.php/aej/issue/archive',
    #    u'http://www.ajod.org/index.php/ajod/issue/archive',
    #    u'http://www.ajlmonline.org/index.php/ajlm/issue/archive',
    #    u'http://www.phcfm.org/index.php/phcfm/issue/archive',
    #    u'http://www.avehjournal.org/index.php/aveh/issue/archive',
    #    u'http://www.curationis.org.za/index.php/curationis/issue/archive',
    #    u'http://www.hts.org.za/index.php/HTS/issue/archive',
    #    u'http://www.indieskriflig.org.za/index.php/skriflig/issue/archive',
    #    u'http://www.jtscm.co.za/index.php/jtscm/issue/archive',
    #    u'http://www.koedoe.co.za/index.php/koedoe/issue/archive',
    #    u'http://www.literator.org.za/index.php/literator/issue/archive',
    #    u'http://www.pythagoras.org.za/index.php/pythagoras/issue/archive',
    #    u'http://www.rw.org.za/index.php/rw/issue/archive',
    #    u'http://www.sajhrm.co.za/index.php/sajhrm/issue/archive',
    #    u'http://www.sajip.co.za/index.php/sajip/issue/archive',
    #    u'http://www.sajr.org.za/index.php/sajr/issue/archive',
    #    u'http://www.sajp.co.za/index.php/sajp/issue/archive']
    rules = [
        Rule(
            LinkExtractor(
                allow=(u"issue/view/\d+$"),
                deny=()
            ),
        ),
        Rule(
            LinkExtractor(
                allow=(u"article/view/\d+$"),
                deny=()
            ),
            callback='parse_item',
        )
    ]

    def extract_aff(response):
        try:
            elem = Utils.select_element_by_content(response, "//div[@id='content']/div", "About the author")
            affs = elem.xpath("./text()").extract()
        except Exception as e:
            return []

        return affs

    def extract_date(response):
        try:
            elem = Utils.select_element_by_content(response, "//div[@id='content']/div", "Published:")
            date = "".join(elem.xpath(".//text()").extract())
            date = Utils.regex_extract(date, "Published:(.*)").strip()
        except Exception as e:
            date = ""
        return date

    items = [[Item(PortiaItem,
                   None,
                   u'',
                   [Field(u'collection',
                          'h1 *::text',
                          []),
                       Field(u'volume',
                             '#breadcrumb a:nth-last-of-type(2) *::text',
                             [Regex(u'Vol (\\d+)')]),
                       Field(u'issue',
                             '#breadcrumb a:nth-last-of-type(2) *::text',
                             [Regex(u'No (\\d+)')]),
                       Field(u'title',
                             '#articleTitle *::text',
                             []),
                       Field(u'author',
                             '#authorString *::text',
                             []),
                       Field(u'release_date',
                             extract_date,
                             []),
                       Field(u'author_affiliation',
                             extract_aff,
                             []),
                       Field(u'doi',
                             '#pub-id\\:\\:doi::attr(href)',
                             []),
                       Field(u'pdf_link',
                             '#articleFullText a:nth-last-child(1)::attr(href)',
                             []),
                       Field(u'abstracts',
                             '#articleAbstract *::text',
                             []),
                       Field(u'keywords',
                             '#articleSubject *::text',
                             [])])]]
