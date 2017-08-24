# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import datetime

import copy
import requests
import MySQLdb
import MySQLdb.cursors
from twisted.enterprise import adbapi

from sakamichi_crawler import settings
import os
from scrapy import log
from sakamichi_crawler.items import MemberItem, ArticleItem
from scrapy.conf import settings


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


class MongoDBPipeline(object):
    def __init__(self):
        self.dbpool = adbapi.ConnectionPool(
            'MySQLdb', db='sakamichi', user='root', passwd='mysqlpasswd', host='112.74.54.144',
            cursorclass=MySQLdb.cursors.DictCursor, charset='utf8', use_unicode=True)
        # db = connection[settings['MONGODB_DB']]
        # self.profile = db[settings['MONGODB_PROFILE']]
        # self.blog = db[settings['MONGODB_BLOG']]

    def process_item(self, item, spider):
        if isinstance(item, MemberItem):
            asynItem = copy.deepcopy(item)
            query = self.dbpool.runInteraction(self._conditional_insert, asynItem)
            query.addErrback(self.handle_error)

        elif isinstance(item, ArticleItem):
            asynItem = copy.deepcopy(item)
            query = self.dbpool.runInteraction(self._conditional_insert, asynItem)
            query.addErrback(self.handle_error)

        return item

    def _conditional_insert(self, tx, item):
        # create record if doesn't exist.
        # all this block run on it's own thread
        fields = []
        values = []
        for k, v in item.items():
            fields.append(k)
            values.append(v)

        # tx.execute("select * from %s where link = %s" % (item.__table__, item['link'][0],))
        # result = tx.fetchone()
        # if result:
        #     log.msg("Item already stored in db: %s" % item, level=log.DEBUG)
        # else:
        # try:

        tx.execute("INSERT INTO %s (%s) VALUES(%s)" % (
            item.__table__, ','.join(['`%s`' % x for x in fields]), ','.join(["'%s'" % v for v in values])))
        #     # log.msg("Item stored in db: %s" % item, level=log.DEBUG)


    def handle_error(self, e):
        log.err(e)


class SakamichiCrawlerPipeline(object):
    def process_item(self, item, spider):
        return item
