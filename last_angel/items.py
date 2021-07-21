from itemloaders.processors import TakeFirst, Identity
from scrapy.loader import ItemLoader
import scrapy


class ScrapedChapter(scrapy.Item):
    content_name = scrapy.Field()
    post_id = scrapy.Field()
    book_name = scrapy.Field()
    url = scrapy.Field()
    raw_html = scrapy.Field()

    unique_key = ("content_name", "post_id")

    def __repr__(self):
        return str(
            f"{{content_name={self['content_name']}, post_id={self['post_id']}, "
            f"book_name={self['book_name']}, url={self['url']}, raw_html={len(self['raw_html'])} lines}}")


class ScrapedChapterLoader(ItemLoader):
    default_output_processor = TakeFirst()

    raw_html_out = Identity()
