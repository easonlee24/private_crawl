from __future__ import absolute_import

import scrapy
from collections import defaultdict
from scrapy.loader.processors import Join, MapCompose, Identity
from w3lib.html import remove_tags
from .utils.processors import Text, Number, Price, Date, Url, Image


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


class BookItemItem(PortiaItem):
    doi = scrapy.Field(
        input_processor=Text(),
        output_processor=Join(),
    )
    page = scrapy.Field(
        input_processor=Text(),
        output_processor=Join(),
    )
    content = scrapy.Field(
        input_processor=Text(),
        output_processor=Join(),
    )
    release_date = scrapy.Field(
        input_processor=Text(),
        output_processor=Join(),
    )
    chapters = scrapy.Field(
        input_processor=Url(),
        output_processor=Join(),
    )
    licence_type = scrapy.Field(
        input_processor=Text(),
        output_processor=Join(),
    )
    author = scrapy.Field(
        input_processor=Text(),
        output_processor=Join(),
    )
    publisher = scrapy.Field(
        input_processor=Text(),
        output_processor=Join(),
    )
    title = scrapy.Field(
        input_processor=Text(),
        output_processor=Join(),
    )
    PSIBN = scrapy.Field(
        input_processor=Text(),
        output_processor=Join(),
    )
    abstract = scrapy.Field(
        input_processor=Text(),
        output_processor=Join(),
    )
    subject = scrapy.Field(
        input_processor=Text(),
        output_processor=Join(),
    )
    EISBN = scrapy.Field(
        input_processor=Text(),
        output_processor=Join(),
    )


class BookResultItemItem(PortiaItem):
    book_link = scrapy.Field(
        input_processor=Url(),
        output_processor=Join(),
    )


class ChapterItemItem(PortiaItem):
    abstract = scrapy.Field(
        input_processor=Text(),
        output_processor=Join(),
    )
    title = scrapy.Field(
        input_processor=Text(),
        output_processor=Join(),
    )
    collection_title = scrapy.Field(
        input_processor=Text(),
        output_processor=Join(),
    )
    doi = scrapy.Field(
        input_processor=Text(),
        output_processor=Join(),
    )
    author_affliication = scrapy.Field(
        input_processor=Text(),
        output_processor=Join(),
    )
    author_field = scrapy.Field(
        input_processor=Text(),
        output_processor=Join(),
    )
    author = scrapy.Field(
        input_processor=Identity(),
        output_processor=Join(),
    )
    pdf_link = scrapy.Field(
        input_processor=Url(),
        output_processor=Join(),
    )
    keywords = scrapy.Field(
        input_processor=Text(),
        output_processor=Join(),
    )
