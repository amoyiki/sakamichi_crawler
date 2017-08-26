# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import codecs
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
            'MySQLdb', db='sakamichi', user='root', passwd='root', host='127.0.0.1',
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
        if item.__table__ == 't_article':
            filters = "`author`='%s' and `datetime`='%s'" % (item['author'], item['datetime'])
        else:
            filters = "`roomazi`='%s' and `group`='%s'" % (item['roomazi'], item['group'])

        tx.execute("select id from %s where %s" % (item.__table__, filters))
        result = tx.fetchone()
        if result:
            log.msg("Item already stored in db: %s" % item, level=log.DEBUG)
        else:
            try:
                tx.execute("INSERT INTO %s (%s) VALUES(%s)" % (
                    item.__table__, ','.join(['`%s`' % x for x in fields]), ','.join([r'"%s"' % v for v in values])))
            except:
                with codecs.open('xxt.txt', 'a', encoding='utf-8') as f:
                    f.write("INSERT INTO %s (%s) VALUES(%s)" % (
                        item.__table__, ','.join(['`%s`' % x for x in fields]), ','.join([r'"%s"' % v for v in values])))
                    f.write('\n')

    def handle_error(self, e):
        log.err(e)


class SakamichiCrawlerPipeline(object):
    def __init__(self):
        db = MySQLdb.Connect(
            db='sakamichi', user='root', passwd='root', host='127.0.0.1', charset='utf8', use_unicode=True)
        cursor = db.cursor()
        self.db = db
        self.cursor = cursor

    def process_item(self, item, spider):
        fields = []
        values = []
        for k, v in item.items():
            fields.append(k)
            values.append(v)
        if item.__table__ == 't_article':
            filters = "`author`='%s' and `title`='%s'" % (item['author'], item['title'])
        else:
            filters = "`roomazi`='%s' and `group`='%s'" % (item['roomazi'], item['group'])

        # self.cursor.execute("select id from %s where %s" % (item.__table__, filters))
        # result = self.cursor.fetchone()
        # if result:
        #     log.msg("Item already stored in db: %s" % item, level=log.DEBUG)
        # else:
        try:
            self.cursor.execute("INSERT INTO %s (%s) VALUES(%s)" % (
                item.__table__, ','.join(['`%s`' % x for x in fields]), ','.join([r'"%s"' % v for v in values])))
        except:
            with codecs.open('xxt.txt', 'a', encoding='utf-8') as f:
                f.write("INSERT INTO %s (%s) VALUES(%s)" % (
                    item.__table__, ','.join(['`%s`' % x for x in fields]),
                    ','.join([r'"%s"' % v for v in values])))
                f.write('\n')
        self.db.commit()
        return item

    def __del__(self):

        self.cursor.close()
        self.db.close()