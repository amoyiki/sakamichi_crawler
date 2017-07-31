import datetime
import re
import scrapy
import time

from scrapy.extensions.closespider import CloseSpider

from sakamichi_crawler.items import MemberItem, ArticleItem
from utils import sankisei, datetime_offset_by_month


class ArticleSpider(scrapy.Spider):
    name = "article_crawler"
    allowed_domains = ["nogizaka46.com", "keyakizaka46.com"]
    start_urls = ['http://www.keyakizaka46.com/s/k46o/diary/member/list?ima=0000&cd=member&dy=201511']
                  # start_urls = ['http://blog.nogizaka46.com/', 'http://www.keyakizaka46.com/s/k46o/search/artist?ima=0000']
    group = {'nogizaka46': {}, 'keyakizaka46': {}}

    def start_requests(self):
        for url in self.start_urls:

            yield scrapy.Request(url, callback=self.all_url)

    def all_url(self, response):
        sel = scrapy.Selector(response)

        if 'nogizaka46' in response.url:
            self.group.get('nogizaka46')['xpath'] = "//div[@id='sidearchives']/select/option/@value"
            self.group.get('nogizaka46')['url'] = "http://www.nogizaka46.com/smph/member/detail/{}"
            group_name = 'nogizaka46'
            all_article_url = sel.xpath(self.group.get(group_name)['xpath']).extract()

        elif 'keyakizaka46' in response.url:
            self.group.get('keyakizaka46')['xpath'] = "//div[@class='pager']/ul/li[last()]/a/@href"
            self.group.get('keyakizaka46')[
                'url'] = "http://www.keyakizaka46.com/s/k46o/diary/member/list?ima=0000&cd=member&dy={}"
            group_name = 'keyakizaka46'
            start_day = datetime.datetime(2015, 11, 1)
            NOW = datetime.datetime.now()
            all_article_url = []
            while True:
                month = ''.join(str(start_day.date())[:-3].split('-'))
                all_article_url.append(self.group.get('keyakizaka46')['url'].format(month))
                if month == ''.join(str(NOW.date())[:-3].split('-')):
                    break

                start_day = datetime_offset_by_month(start_day, 1)

        for url in all_article_url:
            yield scrapy.Request(url, callback=self.month_article)

    def month_article(self, response):
        sel = scrapy.Selector(response)

        if 'nogizaka46' in response.url:
            self.group.get('nogizaka46')['xpath'] = "//div[@class='right2in']/div[1]/a/@href"
            self.group.get('nogizaka46')['url'] = "http://blog.nogizaka46.com/{}"
            group_name = 'nogizaka46'
        elif 'keyakizaka46' in response.url:
            self.group.get('keyakizaka46')['xpath'] = ""
            self.group.get('keyakizaka46')[
                'url'] = ""
            group_name = 'keyakizaka46'

        all_month_url = sel.xpath(self.group.get(group_name)['xpath']).extract()
        url_list = [response.url]
        for url in all_month_url:
            url = self.group.get(group_name)['url'].format(url)
            url_list.append(url)

        for url in url_list:
            yield scrapy.Request(url, callback=self.article)

    def article(self, response):
        sel = scrapy.Selector(response)
        item = ArticleItem()

        if 'nogizaka46' in response.url:
            title = sel.xpath("//span[@class='entrytitle']/a/text()").extract()
            datetime = sel.xpath("//div[@class='entrybottom']/text()[1]").extract()
            author = sel.xpath("//span[@class='author']/text()").extract()
            content = sel.xpath("//div[@class='entrybody']").extract()
            for index, element in enumerate(author):
                item['title'] = title[index]
                item['datetime'] = datetime[index].strip().replace(r'｜', '')
                if element != '３期生':
                    item['author'] = element
                else:
                    for k, v in sankisei.items():
                        if re.search(sankisei[k], item['title']) is not None:
                            item['author'] = sankisei[k]
                            break
                        else:
                            item['author'] = element

                c = content[index]
                c = re.sub(r"<[^img|a][^a][^>]*>", '<br>', c)
                c_split = c.split("<br>")

                new_c = []
                for x in c_split:
                    if x and x != '\xa0' and x != '\n':
                        new_c.append(x.replace('\xa0', ''))

                item['content'] = '<br>'.join(new_c)
                item['group'] = 'nogizaka46'
                yield item
        elif 'keyakizaka46' in response.url:
            # todo
            item['group'] = 'keyakizaka46'
            yield item


