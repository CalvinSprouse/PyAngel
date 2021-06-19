from bs4 import BeautifulSoup
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from last_angel.items import ScrapedChapter, ScrapedChapterLoader
import logging
import re
import scrapy


class LastAngelSpider(scrapy.Spider):
    """Parses the last angel forum to retrieve all messages pertaining to the story and saves the dict to a file"""

    name = "last_angel_spider"

    start_urls = [
        "https://forums.spacebattles.com/threads/the-last-angel.244209/reader/",
        # "https://forums.spacebattles.com/threads/the-last-angel-ascension.346640/reader/",
        # "https://forums.spacebattles.com/threads/the-last-angel-the-hungry-stars.868549/reader/"
    ]

    book_name_re_dict = {
        "the-last-angel": None,
        "the-angels-fire": re.compile(r"The\s*Angel's\s*Fire\s*", re.IGNORECASE),
        "the-last-angel-ascension": None,
        "buried-in-the-past": re.compile(r"Buried\s*in\s*the\s*Past$", re.IGNORECASE),
        "entomology": re.compile(r"Entomology", re.IGNORECASE),
        "quiet": re.compile(r"Quiet\s*(full)", re.IGNORECASE),
        "stillness": re.compile(r"Stillness", re.IGNORECASE),
        "story-time": re.compile(r"Story\s*Time", re.IGNORECASE),
        "the-final-line": re.compile(r"The\s*Final\s*Line", re.IGNORECASE),
        "uneasy-lie-the-heads": re.compile(r"Uneasy\s*Lie\s*the\s*Heads", re.IGNORECASE),
        "predator-prey": re.compile(r"Predator,\s*(Prey|Predator)", re.IGNORECASE),
        "names-of-the-demons": re.compile(r"Names\s*of\s*the\s*Demon:", re.IGNORECASE),
        "awakening": re.compile(r"Awakening,\s*Chapter", re.IGNORECASE),
        "hungry-stars": None,
        "sirens-song": re.compile(r"Siren's\s*Song,", re.IGNORECASE)
    }

    def __init__(self, scrapy_log_level: int = logging.WARNING, spider_log_level: int = logging.DEBUG, **kwargs):
        super().__init__(**kwargs)
        logging.getLogger("scrapy").setLevel(scrapy_log_level)
        self.logger.setLevel(spider_log_level)

    def start_requests(self):
        for link in self.start_urls:
            self.logger.info(f"Start Url: {link}")
            yield scrapy.Request(link, callback=self.parse, errback=self.errback, dont_filter=True)

    def parse(self, response, **kwargs):
        self.logger.info(f"Extracting links for starter url: {response.request.url}")
        toc_post_id = re.search(r"post-(?P<id>(\d*))",
                                response.css("article.hasThreadmark").css("[data-content]").get(), re.IGNORECASE).group(
            "id")
        base_thread = re.search(r"https://forums.spacebattles.com/threads/(?P<base_thread>[^.]*)", response.request.url,
                                re.IGNORECASE).group("base_thread")
        message_lines = response.css("article.hasThreadmark").css("div.bbWrapper").extract()[0].split("\n")
        link_re = re.compile(r"post[s]?[-/](?P<post_id>\d+)[/]?$", re.IGNORECASE)
        meta_dict = {"toc_post_id": toc_post_id,
                     "base_thread": base_thread,
                     "link_re": link_re,
                     "message_lines": message_lines}

        yield response.follow(response.request.url, callback=self.parse_contents_href, errback=self.errback,
                              meta=meta_dict)
        # yield response.follow(response.request.url, callback=self.parse_contents_string, errback=self.errback,
        #                       meta=meta_dict)

    def parse_contents_string(self, response):
        for line in response.meta["message_lines"]:
            soup = BeautifulSoup(line, "html.parser")
            link = soup.find("a")
            text = soup.get_text()
            if link:
                link_id_search = response.meta["link_re"].search(link.get("href"))
                if link_id_search:
                    self.logger.debug(f"Following link {link_id_search.group('post_id')} {text} {link.get('href')}")
                    yield response.follow(link.get("href"), callback=self.parse_post, errback=self.errback,
                                          meta={"post_id": link_id_search.group("post_id"),
                                                "content_name": text,
                                                "base_thread": response.meta["base_thread"],
                                                "source": "parse_contents_string link id"})
            elif "below" in text.lower():
                content_name_search = re.search(r"^(?P<content_name>\w*(\s+\d*)\s*)[(]?below[)]?$", text, re.IGNORECASE)
                if content_name_search:
                    self.logger.debug(f"Following TOC {response.meta['toc_post_id']} {text} {response.request.url}")
                    yield response.follow(response.request.url, callback=self.parse_post, errback=self.errback,
                                          meta={"post_id": response.meta["toc_post_id"],
                                                "content_name": content_name_search.group("content_name").strip(),
                                                "base_thread": response.meta["base_thread"],
                                                "source": "parse_contents_string 'below' id"})

    def parse_contents_href(self, response):
        # parse based on the href list from the table of contents message
        for tag in BeautifulSoup("\n".join(response.meta["message_lines"]), "html.parser").find_all("a"):
            for content_name in tag.get_text().strip().split("\n"):
                post_id_search = response.meta["link_re"].search(tag["href"])
                if post_id_search:
                    self.logger.debug(f"Following href {post_id_search.group('post_id')} {content_name} {tag['href']}")
                    yield response.follow(tag["href"], callback=self.parse_post, errback=self.errback,
                                          meta={"post_id": post_id_search.group("post_id"),
                                                "content_name": content_name,
                                                "base_thread": response.meta["base_thread"],
                                                "source": "parse_contents_href"})

    def parse_post(self, response):
        print(response.meta["content_name"])
        for post in response.css("article.hasThreadmark"):
            post_id = re.search(r"post-(?P<id>(\d*))", post.css("[data-content]").get(), re.IGNORECASE).group("id")
            if post_id == response.meta["post_id"]:
                threadmark = post.css("div.message-cell--threadmark-header").css("span.threadmarkLabel::text").get()
                chapter_l = ScrapedChapterLoader(item=ScrapedChapter(), response=response)
                chapter_l.add_value("content_name", response.meta["content_name"])
                chapter_l.add_value("post_id", post_id)
                chapter_l.add_value("book_name", self.get_book_name(threadmark, response.meta["base_thread"]))
                chapter_l.add_value("url", response.request.url)
                chapter_l.add_value("raw_html", post.css("div.bbWrapper").extract()[0].split("\n"))
                chapter_item = chapter_l.load_item()
                self.logger.debug(f"Extracted ChapterItem Source={response.meta.get('source')} {chapter_item}")
                return chapter_l.load_item()

    def get_book_name(self, threadmark: str, default: str = None):
        for key, val in self.book_name_re_dict.items():
            if val:
                search = val.search(threadmark)
                if search:
                    return key
        return default

    def errback(self, failure):
        self.logger.error(repr(failure))


if __name__ == "__main__":
    process = CrawlerProcess(get_project_settings())
    process.crawl("last_angel_spider")
    process.start()
