import codecs
import datetime
import html
import re

import MySQLdb
import scrapy
import time
import cgi
from scrapy.extensions.closespider import CloseSpider

from sakamichi_crawler.items import MemberItem, ArticleItem
from utils import sankisei, datetime_offset_by_month


class KeyakizakaSpider(scrapy.Spider):
    name = "keyakizaka_crawler"
    allowed_domains = ["keyakizaka46.com"]
    start_urls = ['http://www.keyakizaka46.com/s/k46o/diary/member/list?ima=0000&page=0&cd=member']

    def parse(self, response):
        sel = scrapy.Selector(response)
        item = ArticleItem()

        title = sel.xpath("//article/div[@class='innerHead']/div[@class='box-ttl']/h3/a").extract()
        datetime = sel.xpath("//article/div[@class='box-bottom']/ul/li[1]/text()").extract()
        author = sel.xpath("//article/div[@class='innerHead']/div[@class='box-ttl']/p/text()").extract()
        content = sel.xpath("//article/div[@class='box-article']").extract()

        for index, element in enumerate(datetime):
            item['title'] = re.sub(r"\n", '', title[index]).strip()
            t = item['title'].replace('\\', r"\\")
            # 去除空格
            item['title'] = ''.join(re.split(r'[\s]', t))
            # 去除html标签
            item['title'] = re.sub(r"<[^>]*>", '', item['title'])
            # 转义
            # item['title'] = html.escape(item['title'])
            item['title'] = re.sub(r'"', r"\"", item['title'])
            item['datetime'] = re.sub(r"\n", '', datetime[index]).strip()
            item['author'] = re.sub(r"\n", '', author[index]).strip()
            c = content[index]
            c = re.sub(r"<[^img][^>]*>", '<br>', c)
            c = re.sub(r"\n", '', c)
            c = re.sub(r'\"', "\'", c)
            c_split = c.split("<br>")
            new_c = []
            for x in c_split:
                if x and x != '\xa0' and x != '\n':
                    new_c.append(x.replace('\xa0', ''))

            item['content'] = '<br>'.join(new_c)
            item['content'] = ''.join(re.split(r'[\s]', item['content']))
            # 转义
            # item['content'] = html.escape(item['content'])
            item['content'] = item['content'].replace('\\', r"\\")
            item['content'] = re.sub(r'"', "'", item['content'])
            item['group'] = 'keyakizaka46'

            yield item
        try:
            nextPage = sel.xpath("//div[@class='pager']/ul/li[last()]/a/@href").extract()[0].strip()
            if nextPage:
                next_url = 'http://www.keyakizaka46.com{}'.format(nextPage)
                yield scrapy.http.Request(next_url, callback=self.article)
        except:
            print('========= end ========')
