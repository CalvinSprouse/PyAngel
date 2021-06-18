from bs4 import BeautifulSoup
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import logging
import re
import scrapy


class LastAngelSpider(scrapy.Spider):
    """Parses the last angel forum to retrieve all messages pertaining to the story and saves the dict to a file"""

    name = "last_angel_spider"

    start_urls = [
        "https://forums.spacebattles.com/threads/the-last-angel.244209/reader/",
        "https://forums.spacebattles.com/threads/the-last-angel-ascension.346640/reader/",
        "https://forums.spacebattles.com/threads/the-last-angel-the-hungry-stars.868549/reader/"
    ]

    def __init__(self, scrapy_log_level: int = logging.WARNING, spider_log_level: int = logging.INFO, **kwargs):
        super().__init__(**kwargs)
        logging.getLogger("scrapy").setLevel(scrapy_log_level)
        self.logger.setLevel(spider_log_level)

    def start_requests(self):
        for link in self.start_urls:
            yield scrapy.Request(link, callback=self.parse, errback=self.errback, dont_filter=True)

    def parse(self, response, **kwargs):
        """
        Extracts messages from a thread link and from those messages extracts:
            threadmark = the threadmark appearing on the post
            post_id = the id of the post from data-content attribute
            base_thread = the name of the thread/the file its saved too
            url = a link to the specific message with scroll indicator
            lines = raw text lines from the message
        :param response: The default scrapy response from scrapy.Request
        :return: a dict containing the above data
        """
        self.logger.info(f"Next Url: {response}")
        for post in response.css("article.hasThreadmark"):
            post_id = re.search(r"post-(?P<id>(\d*))", post.css("[data-content]").get(), re.IGNORECASE).group("id")
            threadmark = post.css("div.message-cell--threadmark-header").css("span.threadmarkLabel::text").get()
            base_thread = re.search(r"https://forums.spacebattles.com/threads/(?P<base_thread>[^.]*)",
                                    response.request.url, re.IGNORECASE).group("base_thread")
            lines = list(filter(None,
                                BeautifulSoup(post.css("div.bbWrapper").extract()[0], "html.parser").get_text().split(
                                    "\n")))

            self.logger.debug(f"\tThreadmark:{threadmark}\tBase Thread:{base_thread}\tID:{post_id}\tLines:{len(lines)}")
            yield {"threadmark": threadmark,
                   "post-id": post_id,
                   "base-thread": base_thread,
                   "url": f"{response.request.url}/#post-{post_id}",
                   "lines": lines}
        next_page = response.css("a.pageNav-jump--next::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def errback(self, failure):
        self.logger.error(repr(failure))


if __name__ == "__main__":
    process = CrawlerProcess(get_project_settings())
    process.crawl("last_angel_spider")
    process.start()
