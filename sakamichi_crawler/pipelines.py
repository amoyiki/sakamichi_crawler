# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import requests
from sakamichi_crawler import settings
import os


class ImageDownloadPipeline(object):
    def process_item(self, item, spider):

        dir_path = r"{}/{}".format(settings.IMAGE_FILE, 'avatar')
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        if item.get('avatar') and item.get('roomazi'):
            file_path = '{}/{}.jpg'.format(dir_path, item.get('roomazi'))
            if not os.path.exists(file_path):
                with open(file_path, 'wb') as f:
                    resp = requests.get(item.get('avatar'))
                    if resp.status_code == 200:
                        f.write(resp.content)

        return item

class SakamichiCrawlerPipeline(object):
    def process_item(self, item, spider):
        return item
