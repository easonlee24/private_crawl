#coding=utf-8
from scrapy.spiders import CrawlSpider
from scrapy.loader import ItemLoader
from scrapy.utils.response import get_base_url

from .starturls import FeedGenerator, FragmentGenerator
from ..spiders.utils import  Utils


class RequiredFieldMissing(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


class PortiaItemLoader(ItemLoader):
    def get_value(self, value, *processors, **kw):
        required = kw.pop('required', False)
        val = super(PortiaItemLoader, self).get_value(value, *processors, **kw)
        if required and not val:
            raise RequiredFieldMissing(
                'Missing required field "{value}" for "{item}"'.format(
                    value=value, item=self.item.__class__.__name__))
        return val

    #def add_css(self, field_name, css, *processors, **kw):
    #    values = self._get_cssvalues(css, **kw)
    #    print "values for field in add_css %s" % field_name
    #    print values
    #    return


class BasePortiaSpider(CrawlSpider):
    items = []

    def start_requests(self):
        for url in self.start_urls:
            if isinstance(url, dict):
                type_ = url['type']
                if type_ == 'generated':
                    for generated_url in FragmentGenerator()(url):
                        yield self.make_requests_from_url(generated_url)
                elif type_ == 'feed':
                    yield FeedGenerator(self.parse)(url)
            else:
                yield self.make_requests_from_url(url)

    def parse_item(self, response):
        for sample in self.items:
            items = []
            try:
                for definition in sample:
                    items.extend(
                        [i for i in self.load_item(definition, response)]
                    )
            except RequiredFieldMissing as exc:
                self.logger.warning(str(exc))
            if items:
                for item in items:
                    yield item
                break

    def load_item(self, definition, response):
        if definition.selector == "":
            selectors = [None]
        else:
            selectors = response.css(definition.selector)

        for selector in selectors:
            selector = selector if selector else None
            ld = PortiaItemLoader(
                item=definition.item(),
                selector=selector, #这个指定了某个固定的页面，后面的add_css()指定的selector的root。对于一个页面要爬取多个item，其实是有用的。
                response=response,
                baseurl=get_base_url(response)
            )
            for field in definition.fields:
                if hasattr(field, 'fields'): #表示嵌套的field？
                    if field.name is not None:
                        ld.add_value(field.name,
                                     self.load_item(field, selector))
                else:
                    #如果没填selector，表示此网页没有这个field
                    if field.selector == "":
                        continue

                    if callable(field.selector):
                       ld.add_value(field.name, field.selector(response))
                       continue

                    elif field.selector.find("::attr") == -1 and field.selector.find("::text") == -1:
                        #field.selector = field.selector + " *::text"  # 大部分的selector都是获取text
                        #selector里面没有指定获取啥内容, 那么默认就是获取全部content
                        elems = response.css(field.selector)
                        values = []
                        for elem in elems:
                            value = "".join(elem.xpath(".//text()").extract())
                            values.append(value)

                        if len(values) == 0:
                            ld.add_value(field.name, "")
                        #elif len(values) == 1:
                        #    ld.add_value(field.name, values[0])
                        else:
                            ld.add_value(field.name, values)

                        continue

                    try:
                        ld.add_css(field.name, field.selector, *field.processors,
                               required=field.required)

                    except Exception as e:
                        print "load selector: %s error" % field.selector
                        raise Exception(e)

                    #TODO 增加xpath的表示
                    """
                    如果field的selecotr没有匹配到，则强制把此field标记为空，否则输出的item
                    不会包含此字段.
                    """
                    if not field.required and ld.get_output_value(field.name) == "":
                        ld.add_value(field.name, "")

            #再添加一些必备的url
            ld.add_value("access_url", get_base_url(response))
            ld.add_value("acquisition_time", Utils.current_time())
            yield ld.load_item()
