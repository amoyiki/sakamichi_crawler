# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy import Field


class MemberItem(scrapy.Item):
    """
        成员model
    """
    _id = Field()
    name = Field()
    birthday = Field()
    blood_type = Field()
    constellation = Field()
    stature = Field()
    avatar = Field()



class SakamichiCrawlerItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass
