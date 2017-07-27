from scrapy.command import ScrapyCommand
from scrapy.utils.project import get_project_settings
from scrapy.crawler import Crawler, CrawlerProcess


class Command(ScrapyCommand):
    requires_project = True

    def syntax(self):
        return '[options]'

    def short_desc(self):
        return 'Runs all of the spiders'

    def run(self, args, opts):
        settings = get_project_settings()
        crawler_process = CrawlerProcess(settings)
        for spider_name in crawler_process.spiders.list():
            crawler = Crawler(settings)
            crawler.configure()
            spider = crawler.spiders.create(spider_name)
            crawler.crawl(spider)
            crawler.start()

        self.crawler.start()