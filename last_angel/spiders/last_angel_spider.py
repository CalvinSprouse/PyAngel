from bs4 import BeautifulSoup
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from last_angel.items import ScrapedChapter, ScrapedChapterLoader
import json
import logging
import os
import re
import requests
import scrapy


class LastAngelSpider(scrapy.Spider):
    """Parses the last angel forum to retrieve all messages pertaining to the story and saves the dict to a file"""

    name = "last_angel_spider"

    # Add additional threads (if more are created) here
    start_urls = [
        "https://forums.spacebattles.com/threads/the-last-angel.244209/reader/",
        "https://forums.spacebattles.com/threads/the-last-angel-ascension.346640/reader/",
        "https://forums.spacebattles.com/threads/the-last-angel-the-hungry-stars.868549/reader/",
    ]

    # a regular expression for finding the book name from the threadmarks
    book_name_re_dict = {
        "the-last-angel": None,
        "the-angels-fire": re.compile(r"The\s*Angel's\s*Fire\s*", re.IGNORECASE),
        "the-last-angel-ascension": None,
        "buried-in-the-past": re.compile(r"Buried\s*in\s*the\s*Past$", re.IGNORECASE),
        "entomology": re.compile(r"Entomology", re.IGNORECASE),
        "quiet": re.compile(r"Quiet\s*\(full\)", re.IGNORECASE),
        "stillness": re.compile(r"Stillness", re.IGNORECASE),
        "story-time": re.compile(r"Story\s*Time", re.IGNORECASE),
        "the-final-line": re.compile(r"The\s*Final\s*Line", re.IGNORECASE),
        "uneasy-lie-the-heads": re.compile(r"Uneasy\s*Lie\s*the\s*Heads", re.IGNORECASE),
        "predator-prey": re.compile(r"Predator,\s*(Prey|Predator)", re.IGNORECASE),
        "names-of-the-demons": re.compile(r"Names\s*of\s*the\s*Demon[:,]", re.IGNORECASE),
        "awakening": re.compile(r"Awakening,\s*Chapter", re.IGNORECASE),
        "hungry-stars": None,
        "sirens-song": re.compile(r"Siren's\s*Song,", re.IGNORECASE)
    }

    # a simple exclusion regular expression to capture anything that tends to fall through
    exclude_threadmarks = [
        re.compile(r"(map\s*of\s*galhemna\s*system)", re.IGNORECASE),
    ]

    # TODO: Change force_run for deploy
    def __init__(self, log_level: int = logging.INFO, force_run: bool = True, **kwargs):
        super().__init__(**kwargs)

        logging.getLogger("scrapy").setLevel(log_level)
        logging.getLogger("urllib3.connectionpool").setLevel(log_level)
        self.logger.setLevel(log_level)
        self.force_run = force_run

    def start_requests(self):
        # create the json file which saves line counts to check for changes
        toc_line_length_file = os.path.join(get_project_settings().get("DATA_SAVE_DIR"), "toc_line_length.json")
        os.makedirs(os.path.dirname(toc_line_length_file), exist_ok=True)
        if not os.path.isfile(toc_line_length_file):
            json.dump({}, open(toc_line_length_file, "w"), indent=4)

        # load from the json file a dict containing the line lengths of urls to check against their current line length
        toc_line_length_dict = json.load(open(toc_line_length_file))

        # check each link against the dict to see if we should run it or not
        for link in self.start_urls:
            self.logger.debug(f"Check Url: {link}")

            # finds how many urls are in the table of contents page
            link_length = len(BeautifulSoup(requests.get(link).content, "html.parser")
                              .find("article", {"class", "hasThreadmark"})
                              .find("div", {"class": "bbWrapper"})
                              .find_all("a"))
            self.logger.debug(f"Link Length ({link})={link_length}")

            # the url count is used to determine if a new chapter was added
            if toc_line_length_dict.get(link, 0) < link_length or self.force_run:
                self.logger.info(f"Start Url: {link}")
                yield scrapy.Request(link, callback=self.parse, errback=self.errback, dont_filter=True)
            toc_line_length_dict[link] = link_length

        # save dict to file for future reference
        json.dump(toc_line_length_dict, open(toc_line_length_file, "w"))

    def parse(self, response, **kwargs):
        """ The first parser takes a link and sends it off to be parsed by
        parse_contents_href and parse_table_contents_page"""
        self.logger.debug(f"Extracting links for starter url: {response.request.url}")
        toc_post_id = re.search(r"post-(?P<id>(\d*))", response.css("article.hasThreadmark")
                                .css("[data-content]").get(), re.IGNORECASE).group("id")
        base_thread = re.search(r"https://forums.spacebattles.com/threads/(?P<base_thread>[^.]*)", response.request.url,
                                re.IGNORECASE).group("base_thread")
        message_lines = response.css("article.hasThreadmark").css("div.bbWrapper").extract()[0].split("\n")
        link_re = re.compile(r"post[s]?[-/](?P<post_id>\d+)[/]?$", re.IGNORECASE)
        meta_dict = {"toc_post_id": toc_post_id,
                     "base_thread": base_thread,
                     "link_re": link_re,
                     "message_lines": message_lines}

        # double parses each url to ensure all posts are captured, even those listed in the same link
        yield response.follow(response.request.url, callback=self.parse_table_contents_page, errback=self.errback,
                              meta=meta_dict, dont_filter=True)
        yield response.follow(response.request.url, callback=self.parse_contents_href, errback=self.errback,
                              meta=meta_dict, dont_filter=True)

    def parse_contents_href(self, response):
        """ Uses the links found in the table of contents post to reveal more posts to follow"""
        for tag in BeautifulSoup("\n".join(response.meta["message_lines"]), "html.parser").find_all("a"):
            # looks for multiple chapters in one link (Chapter 13 and Chapter 14) but split by a newline and splits them
            for content_name in tag.get_text().strip().split("\n"):
                post_id_search = response.meta["link_re"].search(tag["href"])
                if post_id_search:
                    self.logger.debug(
                        f"Following href {post_id_search.group('post_id')} {content_name} {tag['href']}")
                    yield response.follow(tag["href"], callback=self.parse_post, errback=self.errback, dont_filter=True,
                                          meta={"post_id": post_id_search.group("post_id"),
                                                "content_name": content_name,
                                                "base_thread": response.meta["base_thread"],
                                                "source": "parse_contents_href"})

    def parse_table_contents_page(self, response):
        """
        Gets the content of the table of contents post (first posts of a thread)
        :return: dict of
            :content_name: the posts threadmark
            :post_id: the unique id of the post
            :book_name: the name of the thread it belongs to, extracted from the url
            :url: the url used to find the post
            :raw_html: the html data of the div.bbWrapper that held the post
        """
        # checks for any chapters embedded within the table of contents page
        for post in response.css("article.hasThreadmark"):
            post_id = re.search(r"post-(?P<id>(\d*))", post.css("[data-content]").get(), re.IGNORECASE).group("id")

            # ensures the following code only applies to the table of contents post
            if post_id == response.meta["toc_post_id"]:
                toc_threadmark = str(post.css("div.message-cell--threadmark-header").css("span::text").get()).strip()

                # checks for multiple chapters listed in table of contents post (table of contents and prologue)
                for chapter in toc_threadmark.split("and"):
                    # ensures the table of contents specifically isn't counted as a chapter
                    if not re.search(r"table\s*of\s*content(s?)\s*", chapter.strip(), re.IGNORECASE):
                        chapter_l = ScrapedChapterLoader(item=ScrapedChapter(), response=response)
                        chapter_l.add_value("content_name", chapter.strip())
                        chapter_l.add_value("post_id", post_id)
                        chapter_l.add_value("book_name", self.get_book_name(chapter, response.meta["base_thread"]))
                        chapter_l.add_value("url", response.request.url)
                        chapter_l.add_value("raw_html", post.css("div.bbWrapper").extract()[0].split("\n"))
                        chapter_item = chapter_l.load_item()
                        self.logger.debug(f"Extracted ChapterItem Source={response.meta.get('source')} {chapter_item}")
                        yield chapter_item

    def parse_post(self, response):
        """
        Gets the content of a specific post
        :return: dict of
            :content_name: the posts threadmark
            :post_id: the unique id of the post
            :book_name: the name of the thread it belongs to, extracted from the url
            :url: the url used to find the post
            :raw_html: the html data of the div.bbWrapper that held the post
        """
        for post in response.css("article.hasThreadmark"):
            # a specific post is listed in the meta of the response but more posts appear on the same page

            post_id = re.search(r"post-(?P<id>(\d*))", post.css("[data-content]").get(), re.IGNORECASE).group("id")
            if post_id == response.meta["post_id"]:
                threadmark = post.css("div.message-cell--threadmark-header").css("span.threadmarkLabel::text").get()
                book_name = self.get_book_name(threadmark, response.meta["base_thread"])

                # ensures a book name is present
                if book_name:
                    chapter_l = ScrapedChapterLoader(item=ScrapedChapter(), response=response)
                    chapter_l.add_value("content_name", response.meta["content_name"])
                    chapter_l.add_value("post_id", post_id)
                    chapter_l.add_value("book_name", book_name)
                    chapter_l.add_value("url", response.request.url)
                    chapter_l.add_value("raw_html", post.css("div.bbWrapper").extract()[0].split("\n"))
                    chapter_item = chapter_l.load_item()
                    self.logger.debug(f"Extracted ChapterItem Source={response.meta.get('source')} {chapter_item}")
                    return chapter_l.load_item()

    def get_book_name(self, threadmark: str, default: str = None):
        """ Checks the regex dict for a matching type of regex and uses it to find the book name from the link """
        for exclude_re in self.exclude_threadmarks:
            if exclude_re.search(threadmark):
                return None
        for key, val in self.book_name_re_dict.items():
            if val:
                search = val.search(threadmark)
                if search:
                    return key
        return default

    def errback(self, failure):
        """ Logs errors """
        self.logger.error(repr(failure))


if __name__ == "__main__":
    # TODO: Figure out how to do this from a different file
    process = CrawlerProcess(get_project_settings())
    process.crawl("last_angel_spider")
    process.start()
