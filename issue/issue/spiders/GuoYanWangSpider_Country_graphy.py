#!/usr/bin/env python
# -*- coding: utf-8 -*-
import scrapy
import re
import urlparse
import sys
from scrapy.http.request import Request
import requests

reload(sys)
sys.setdefaultencoding('utf8')


class GuoYanWangSpider_Country_graphy(scrapy.Spider):
    name = "GuoYanWangSpider_Country_graphy"
    countrysUrls = ['http://ydyl.drcnet.com.cn/www/ydyl/channel2.aspx?country=埃及',
                    'http://ydyl.drcnet.com.cn/www/ydyl/channel2.aspx?country=爱沙尼亚',
                    'http://ydyl.drcnet.com.cn/www/ydyl/channel2.aspx?country=阿塞拜疆',
                    'http://ydyl.drcnet.com.cn/www/ydyl/channel2.aspx?country=阿富汗',
                    'http://ydyl.drcnet.com.cn/www/ydyl/channel2.aspx?country=阿尔巴尼亚',
                    'http://ydyl.drcnet.com.cn/www/ydyl/channel2.aspx?country=阿曼',
                    'http://ydyl.drcnet.com.cn/www/ydyl/channel2.aspx?country=阿联酋',
                    'http://ydyl.drcnet.com.cn/www/ydyl/channel2.aspx?country=不丹',
                    'http://ydyl.drcnet.com.cn/www/ydyl/channel2.aspx?country=保加利亚',
                    'http://ydyl.drcnet.com.cn/www/ydyl/channel2.aspx?country=巴勒斯坦',
                    'http://ydyl.drcnet.com.cn/www/ydyl/channel2.aspx?country=巴基斯坦',
                    'http://ydyl.drcnet.com.cn/www/ydyl/channel2.aspx?country=巴林',
                    'http://ydyl.drcnet.com.cn/www/ydyl/channel2.aspx?country=波兰',
                    'http://ydyl.drcnet.com.cn/www/ydyl/channel2.aspx?country=波黑',
                    'http://ydyl.drcnet.com.cn/www/ydyl/channel2.aspx?country=白俄罗斯',
                    'http://ydyl.drcnet.com.cn/www/ydyl/channel2.aspx?country=东帝汶',
                    'http://ydyl.drcnet.com.cn/www/ydyl/channel2.aspx?country=俄罗斯',
                    'http://ydyl.drcnet.com.cn/www/ydyl/channel2.aspx?country=菲律宾',
                    'http://ydyl.drcnet.com.cn/www/ydyl/channel2.aspx?country=格鲁吉亚',
                    'http://ydyl.drcnet.com.cn/www/ydyl/channel2.aspx?country=哈萨克斯坦',
                    'http://ydyl.drcnet.com.cn/www/ydyl/channel2.aspx?country=黑山',
                    'http://ydyl.drcnet.com.cn/www/ydyl/channel2.aspx?country=吉尔吉斯斯坦',
                    'http://ydyl.drcnet.com.cn/www/ydyl/channel2.aspx?country=捷克',
                    'http://ydyl.drcnet.com.cn/www/ydyl/channel2.aspx?country=柬埔寨',
                    'http://ydyl.drcnet.com.cn/www/ydyl/channel2.aspx?country=克罗地亚',
                    'http://ydyl.drcnet.com.cn/www/ydyl/channel2.aspx?country=卡塔尔',
                    'http://ydyl.drcnet.com.cn/www/ydyl/channel2.aspx?country=科威特',
                    'http://ydyl.drcnet.com.cn/www/ydyl/channel2.aspx?country=拉脱维亚',
                    'http://ydyl.drcnet.com.cn/www/ydyl/channel2.aspx?country=立陶宛',
                    'http://ydyl.drcnet.com.cn/www/ydyl/channel2.aspx?country=罗马尼亚',
                    'http://ydyl.drcnet.com.cn/www/ydyl/channel2.aspx?country=老挝',
                    'http://ydyl.drcnet.com.cn/www/ydyl/channel2.aspx?country=黎巴嫩',
                    'http://ydyl.drcnet.com.cn/www/ydyl/channel2.aspx?country=孟加拉国',
                    'http://ydyl.drcnet.com.cn/www/ydyl/channel2.aspx?country=摩尔多瓦',
                    'http://ydyl.drcnet.com.cn/www/ydyl/channel2.aspx?country=缅甸',
                    'http://ydyl.drcnet.com.cn/www/ydyl/channel2.aspx?country=蒙古',
                    'http://ydyl.drcnet.com.cn/www/ydyl/channel2.aspx?country=马其顿',
                    'http://ydyl.drcnet.com.cn/www/ydyl/channel2.aspx?country=马尔代夫',
                    'http://ydyl.drcnet.com.cn/www/ydyl/channel2.aspx?country=马来西亚',
                    'http://ydyl.drcnet.com.cn/www/ydyl/channel2.aspx?country=尼泊尔',
                    'http://ydyl.drcnet.com.cn/www/ydyl/channel2.aspx?country=塞尔维亚',
                    'http://ydyl.drcnet.com.cn/www/ydyl/channel2.aspx?country=斯洛伐克',
                    'http://ydyl.drcnet.com.cn/www/ydyl/channel2.aspx?country=斯洛文尼亚',
                    'http://ydyl.drcnet.com.cn/www/ydyl/channel2.aspx?country=斯里兰卡',
                    'http://ydyl.drcnet.com.cn/www/ydyl/channel2.aspx?country=沙特',
                    'http://ydyl.drcnet.com.cn/www/ydyl/channel2.aspx?country=土库曼斯坦',
                    'http://ydyl.drcnet.com.cn/www/ydyl/channel2.aspx?country=土耳其',
                    'http://ydyl.drcnet.com.cn/www/ydyl/channel2.aspx?country=塔吉克斯坦',
                    'http://ydyl.drcnet.com.cn/www/ydyl/channel2.aspx?country=泰国',
                    'http://ydyl.drcnet.com.cn/www/ydyl/channel2.aspx?country=乌克兰',
                    'http://ydyl.drcnet.com.cn/www/ydyl/channel2.aspx?country=乌兹别克斯坦',
                    'http://ydyl.drcnet.com.cn/www/ydyl/channel2.aspx?country=文莱',
                    'http://ydyl.drcnet.com.cn/www/ydyl/channel2.aspx?country=匈牙利',
                    'http://ydyl.drcnet.com.cn/www/ydyl/channel2.aspx?country=叙利亚',
                    'http://ydyl.drcnet.com.cn/www/ydyl/channel2.aspx?country=新加坡',
                    'http://ydyl.drcnet.com.cn/www/ydyl/channel2.aspx?country=也门',
                    'http://ydyl.drcnet.com.cn/www/ydyl/channel2.aspx?country=亚美尼亚',
                    'http://ydyl.drcnet.com.cn/www/ydyl/channel2.aspx?country=以色列',
                    'http://ydyl.drcnet.com.cn/www/ydyl/channel2.aspx?country=伊拉克',
                    'http://ydyl.drcnet.com.cn/www/ydyl/channel2.aspx?country=伊朗',
                    'http://ydyl.drcnet.com.cn/www/ydyl/channel2.aspx?country=印度',
                    'http://ydyl.drcnet.com.cn/www/ydyl/channel2.aspx?country=印度尼西亚',
                    'http://ydyl.drcnet.com.cn/www/ydyl/channel2.aspx?country=约旦',
                    'http://ydyl.drcnet.com.cn/www/ydyl/channel2.aspx?country=越南']
    # subjects = {'项目': '8008', "法规": '8007', '图表': '8001', '咨迅': '8009', '机构': '8011'}
    subjects = {'图表': '8001'}

    def getUrls(self, url, pages):
        result = []
        for i in range(int(pages)):
            curpage = i + 1
            searchUrl = url + "&curpage=" + str(curpage)
            result.append(searchUrl)
        return result

    def start_requests(self):
        source = '国研网'
        source_url = 'http://www.drcnet.com.cn/'
        for url in self.countrysUrls:
            country = url.split("=")[1]
            for (k, v) in self.subjects.items():
                search_url = url + "&uid=" + v
                meta = {'source': source, 'source_url': source_url, 'search_url': search_url, 'subject': k,
                        'subject country': country}
                yield Request(search_url, self.parseUsefulUrl, meta=meta)

    def parseUsefulUrl(self, response):
        meta = {'source': response.meta['source'], 'source_url': response.meta['source_url'],
                'search_url': response.meta['search_url'], 'subject': response.meta['subject'],
                'subject country': response.meta['subject country']}
        pagesArr = response.xpath("//span[@id='ContentPlaceHolder1_WebPage1_span_totalpage']/text()")
        if len(pagesArr) == 0:
            pages = "0"
        else:
            pages = pagesArr.extract_first()
        meta['pages'] = pages
        all_urls = self.getUrls(response.meta['search_url'], pages)
        for item in all_urls:
            yield Request(item, self.parse, meta=meta)

    def parse(self, response):
        meta = {'source': response.meta['source'], 'source_url': response.meta['source_url'],
                'search_url': response.url, 'subject': response.meta['subject'],
                'subject country': response.meta['subject country'], 'pages': response.meta['pages']}
        searchresults = response.xpath("//ul[@id='ContentPlaceHolder1_WebPage1']/li[@class='tubiaoli']")
        for item in searchresults:
            image_url =  urlparse.urljoin(response.url, item.xpath(".//img/@src").extract_first())
            title=item.xpath(".//div[@class='box_top yahei f15  ']/text()").extract_first()
            desc=("").join(item.xpath(".//div[@class='yahei miaoshu']//text()").extract())
            filePath="/Users/chenlu/Downloads/wangting/guoyanwang/imge/"+title+".png"
            meta['pdf_url'] = image_url
            meta['title'] = title
            meta['describle'] = desc
            meta['filePath'] =filePath
            self.downloadPDF(image_url,filePath)

            # release_date = item.xpath(".//span[@class='date1 ']/text()").extract_first()
            # meta['release_date'] = release_date.replace('[ ', '').replace(' ]', '')
            yield meta

    def downloadPDF(self, pdf_url, filePath):
        # file_url = "http://ageconsearch.umn.edu/record/6074/files/454427.pdf"
        r = requests.get(pdf_url, stream=True)
        with open(filePath, "wb") as pdf:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    pdf.write(chunk)
            print filePath + " successful!!!"
