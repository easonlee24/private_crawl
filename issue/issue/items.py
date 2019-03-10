from __future__ import absolute_import

import scrapy
from collections import defaultdict
from scrapy.loader.processors import Join, MapCompose, Identity
from w3lib.html import remove_tags
from .utils.processors import Text, Number, Price, Date, Url, Image, Doi, Abstracts, AuthorSup, AuthorAff


class PortiaItem(scrapy.Item):
    fields = defaultdict(
        lambda: scrapy.Field(
            input_processor=Identity(),
            output_processor=Identity()
        )
    )

    def __setitem__(self, key, value):
        self._values[key] = value

    def __repr__(self):
        data = str(self)
        if not data:
            return '%s' % self.__class__.__name__
        return '%s(%s)' % (self.__class__.__name__, data)

    def __str__(self):
        if not self._values:
            return ''
        string = super(PortiaItem, self).__repr__()
        return string


class IssueItem(PortiaItem):
    join_separator = ";"
    collection = scrapy.Field(
        input_processor=Text(),
        output_processor=Join(),
    )
    collection_url = scrapy.Field(
        input_processor=Url(),
        output_processor=Join(),
    )

    source = scrapy.Field(
        input_processor=Text(),
        output_processor=Join(),
    )
    source_url = scrapy.Field(
        input_processor=Url(),
        output_processor=Join(),
    )

    release_year = scrapy.Field(
        input_processor=Text(),
        output_processor=Join(),
    )
    release_date = scrapy.Field(
        input_processor=Date(),
        output_processor=Join(),
    )
    volumn = scrapy.Field(
        input_processor=Number(),
        output_processor=Join(),
    )
    issue = scrapy.Field(
        input_processor=Text(),
        output_processor=Join(),
    )
    publisher = scrapy.Field(
        input_processor=Text(),
        output_processor=Join(),
    )
    place_of_publication = scrapy.Field(
        input_processor=Text(),
        output_processor=Join(),
    )
    title = scrapy.Field(
        input_processor=Text(),
        output_processor=Join(),
    )
    subtitle = scrapy.Field(
        input_processor=Text(),
        output_processor=Join(),
    )
    dc_contributor = scrapy.Field(
        input_processor=Text(),
        output_processor=Join(separator = join_separator),
    )
    EISBN = scrapy.Field(
        input_processor=Text(),
        output_processor=Join(),
    )
    hardcover_PISBN = scrapy.Field(
        input_processor=Text(),
        output_processor=Join(),
    )
    ISSN = scrapy.Field(
        input_processor=Text(),
        output_processor=Join(),
    )
    EISSN = scrapy.Field(
        input_processor=Text(),
        output_processor=Join(),
    )
    DOI = scrapy.Field(
        input_processor=Doi(),
        output_processor=Join(),
    )
    keywords = scrapy.Field(
        input_processor=Text(),
        output_processor=Join(separator = join_separator),
    )
    abstracts = scrapy.Field(
        input_processor=Abstracts(),
        output_processor=Join(),
    )
    access_url = scrapy.Field(
        input_processor=Url(),
        output_processor=Join(),
    )
    pdf_url = scrapy.Field(
        input_processor=Url(),
        output_processor=Join(),
    )
    pages = scrapy.Field(
        input_processor=Text(),
        output_processor=Join(),
    )
    document_type = scrapy.Field(
        input_processor=Text(),
        output_processor=Join(),
    )
    acquisition_time = scrapy.Field(
        input_processor=Text(),
        output_processor=Join(),
    )

    author_affiliation = scrapy.Field(
        input_processor=AuthorAff(),
        output_processor=Identity(),
    )
    author_sup = scrapy.Field(
        input_processor=AuthorSup(),
        output_processor=Identity(),
    )
