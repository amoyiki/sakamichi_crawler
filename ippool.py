import os

import requests
from bs4 import BeautifulSoup
import lxml
from multiprocessing import Process, Queue
import random
import json
import time


class IPPool(object):
    """
        IP池维护类
    """

    def __init__(self, page=3):
        self.pool = []
        self.page = page
        self.headers = {'Accept': '*/*', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) ' +
                                                       'AppleWebKit/537.36 (KHTML, like Gecko)' +
                                                       ' Chrome/45.0.2454.101 Safari/537.36',
                        'Accept-Encoding': 'gzip, deflate, sdch', 'Accept-Language': 'zh-CN,zh;q=0.8'}

        self.get_ip(url='http://www.xicidaili.com/nt/{}')
        self.get_ip(url='http://www.xicidaili.com/nn/{}')

    def get_ip(self, url):
        page = random.randint(1, 10)
        page_stop = page + self.page
        while page < page_stop:
            url = url.format(page)
            html = requests.get(url, headers=self.headers).content
            soup = BeautifulSoup(html, 'lxml')
            ip_list = soup.find(id='ip_list')
            for odd in ip_list.find_all(class_='odd'):
                ip = '{}://{}'.format(odd.find_all('td')[5].get_text().lower(),
                                      ':'.join([x.get_text() for x in odd.find_all('td')[1:3]]))
                self.pool.append(ip)
            page += 1

    def verify(self):
        unverify_queue = Queue()
        verify_queue = Queue()
        print('verify the ip...')
        works = []
        for _ in range(15):
            works.append(Process(target=self.verify_ip, args=(unverify_queue, verify_queue)))
        for work in works:
            work.start()
        for ip in self.pool:
            unverify_queue.put(ip)
        for work in works:
            unverify_queue.put(0)
        for work in works:
            work.join()
        self.pool = []
        while 1:
            try:
                self.pool.append(verify_queue.get(timeout=1))
            except:
                break
        print('verify ip pool done!')

    def verify_ip(self, unverify_queue, verify_queue):
        while 1:
            ip = unverify_queue.get()
            if ip == 0:
                break
            protocol = 'https' if 'https' in ip else 'http'
            proxies = {protocol: ip}
            try:
                if requests.get('http://www.baidu.com', proxies=proxies, timeout=2).status_code == 200:
                    print('useful ip %s' % ip)
                    verify_queue.put(ip)
            except:
                print('fail ip %s' % ip)


if __name__ == '__main__':
    a = IPPool()
    a.verify()
    print(a.pool)
    with open('ip_list.txt', 'w') as f:
        for ip in a.pool:
            f.write(ip+'\n')
