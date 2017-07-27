import re
import scrapy
import time

from sakamichi_crawler.items import MemberItem


class MemberSpider(scrapy.Spider):
    name = "sakamichi_crawler"
    allowed_domains = ["nogizaka46.com"]
    start_urls = [u'http://www.nogizaka46.com/smph/member/',]
    count = 0
    def start_requests(self):

        yield scrapy.Request(self.start_urls[0], callback=self.all_url)

    def all_url(self, response):
        member_url = []
        sel = scrapy.Selector(response)
        member_name = sel.xpath("//div[@id='member']/ul[@class='clearfix']/li/a/@href").extract()

        for member in member_name:
            name = member.split('/')
            url = r'http://www.nogizaka46.com/smph/member/detail/{}'.format(name[-1])
            yield scrapy.Request(url, callback=self.memeber_profile)

    def memeber_profile(self, response):
        sel = scrapy.Selector(response)
        item = MemberItem()
        name = sel.xpath("//div[@id='member']/h3/text()").extract()[0]
        avatar = sel.xpath("//div[@id='member']/div[@class='pic']/img/@src").extract()[0]
        profile = sel.xpath("//div[@id='member']/dl/dd/text()").extract()
        birthday = profile[0]
        blood_type = profile[1]
        constellation = profile[2]
        stature = profile[3]
        link = sel.xpath("//link[@media='mixi-device-smartphone']/@href").extract()[0]
        r = re.findall('\/([^/]+)\.php', link)[0]
        roomazi = r

        item['name'] = str(name)
        item['birthday'] = str(birthday)
        item['blood_type'] = str(blood_type)
        item['constellation'] = str(constellation)
        item['stature'] = str(stature)
        item['avatar'] = str(avatar)
        item['roomazi'] = str(roomazi)

        yield item
