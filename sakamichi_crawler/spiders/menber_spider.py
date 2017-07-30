import re
import scrapy

from sakamichi_crawler.items import MemberItem


class MemberSpider(scrapy.Spider):

    name = "sakamichi_crawler"
    allowed_domains = ["nogizaka46.com", "keyakizaka46.com"]

    start_urls = ['http://www.nogizaka46.com/smph/member/', 'http://www.keyakizaka46.com/s/k46o/search/artist?ima=0000']
    group = {'nogizaka46': {}, 'keyakizaka46': {}}

    def start_requests(self):
        for url in self.start_urls:

            yield scrapy.Request(url, callback=self.all_url)

    def all_url(self, response):
        sel = scrapy.Selector(response)

        if 'nogizaka46' in  response.url:
            self.group.get('nogizaka46')['xpath'] = "//div[@id='member']/ul[@class='clearfix']/li/a/@href"
            self.group.get('nogizaka46')['url'] = "http://www.nogizaka46.com/smph/member/detail/{}"
            group_name = 'nogizaka46'
        elif 'keyakizaka46' in response.url:
            self.group.get('keyakizaka46')['xpath'] = "//li/@data-member"
            self.group.get('keyakizaka46')['url'] = "http://www.keyakizaka46.com/s/k46o/artist/{}?ima=0000"
            group_name = 'keyakizaka46'
        member_name = sel.xpath(self.group.get(group_name)['xpath']).extract()
        member_name = set(member_name)

        for member in member_name:
            name = member.split('/')
            url = self.group.get(group_name)['url'].format(name[-1])
            yield scrapy.Request(url, callback=self.memeber_profile)

    def memeber_profile(self, response):
        sel = scrapy.Selector(response)
        item = MemberItem()
        if 'nogizaka46' in response.url:
            name = sel.xpath("//div[@id='member']/h3/text()").extract()[0].strip()
            avatar = sel.xpath("//div[@id='member']/div[@class='pic']/img/@src").extract()[0].strip()
            profile = sel.xpath("//div[@id='member']/dl/dd/text()").extract()
            birthday = profile[0].strip()
            blood_type = profile[1].strip()
            constellation = profile[2].strip()
            stature = profile[3].strip()
            link = sel.xpath("//link[@media='mixi-device-smartphone']/@href").extract()[0]
            r = re.findall('\/([^/]+)\.php', link)[0].strip()
            roomazi = r.strip()
            group = 'nogizaka46'
        elif 'keyakizaka46' in response.url:
            name = sel.xpath("//p[@class='name']/text()").extract()[0].strip()
            avatar = sel.xpath("//div[@class='box-profile_img']/img/@src").extract()[0].strip()
            profile = sel.xpath("//div[@class='box-info']/dl/dd/span/text()").extract()
            birthday = profile[0].strip()
            constellation = profile[1].strip()
            stature = profile[2].strip()
            blood_type = profile[4].strip()
            r = sel.xpath("//div[@class='box-profile_text']/span/text()").extract()[0].lower()
            roomazi = ''.join(r.replace('\u3000', ' ').split(' ')[::-1]).strip()
            group = 'keyakizaka46'

        item['name'] = str(name)
        item['birthday'] = str(birthday)
        item['blood_type'] = str(blood_type)
        item['constellation'] = str(constellation)
        item['stature'] = str(stature)
        item['avatar'] = str(avatar)
        item['roomazi'] = str(roomazi)
        item['group'] = group

        yield item
