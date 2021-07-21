from bs4 import BeautifulSoup
from itemadapter import ItemAdapter
from scrapy.exporters import JsonLinesItemExporter
from scrapy.exceptions import DropItem
from scrapy.utils.project import get_project_settings
import os


class FileOutputPipeline:

    def __init__(self):
        self.thread_to_exporter = None
        self.post_ids_recorded = set()
        self.content_names_recorded = set()
        self.save_dir = None

    def open_spider(self, spider):
        self.thread_to_exporter = {}

        # loads project settings (possibly another way to do this)
        self.save_dir = get_project_settings().get("DATA_SAVE_DIR")

    def close_spider(self, spider):
        for exporter, json_lines_file in self.thread_to_exporter.values():
            exporter.finish_exporting()
            json_lines_file.close()

    def _exporter_for_item(self, item):
        adapter = ItemAdapter(item)
        # very misleading variable, thread does not refer to one of the 3 threads
        # but instead to the book chapter belongs too
        thread = adapter.get("book_name", default="other")

        # first time configuration of an exporter
        if thread not in self.thread_to_exporter:
            os.makedirs(os.path.abspath(self.save_dir), exist_ok=True)
            json_file = open(os.path.join(self.save_dir, f"{thread}.jl"), mode="wb")
            exporter = JsonLinesItemExporter(json_file)
            exporter.start_exporting()
            self.thread_to_exporter[thread] = (exporter, json_file)

        return self.thread_to_exporter[thread][0]

    def process_item(self, item, spider):
        """ Saves the item to a jl file matching its book_name """
        self._exporter_for_item(item).export_item(item)
        return item


class CheckDuplicatesPipeline:
    def __init__(self):
        self.unique_values_logged = set()

    def process_item(self, item, spider):
        """ Compares the post_id of incoming items to other posts already logged to prevent duplicate chapters"""
        unique_keys = getattr(item, "unique_key", None)

        if not unique_keys:
            return item

        keys = unique_keys if isinstance(unique_keys, (tuple, list)) else (unique_keys,)
        unique_value = None

        try:
            unique_value = "-".join(map(str, [item.get(k) for k in keys]))
        except KeyError:
            pass

        if unique_value in self.unique_values_logged:
            raise DropItem(f"Duplicate item {unique_value}")
        else:
            self.unique_values_logged.add(unique_value)
            return item


class MakeReadablePipeline:
    def __init__(self):
        self.save_dir = None

    def open_spider(self, spider):
        # loads project settings (possibly another way to do this)
        self.save_dir = get_project_settings().get("READER_SAVE_DIR")

    def close_spider(self, spider):
        # TODO: Run a function to combine all the seperate chapters into one
        pass

    def process_item(self, item, spider):
        """ Takes the raw_html from a passed item and converts it into something readable and saves it """
        adapter = ItemAdapter(item)

        # establish the save dir for this item (using its book-name)
        item_save_dir = os.path.join(self.save_dir, adapter.get("book_name"))
        os.makedirs(item_save_dir, exist_ok=True)

        # get the lines of the item
        chapter_soup_list = [BeautifulSoup(line, "html.parser") for line in adapter.get("raw_html")]
        chapter_lines_list = [soup.get_text().strip() for soup in chapter_soup_list if soup.get_text().strip() != ""]

        first_good_line = next(iter([i for i, v in enumerate(chapter_lines_list) if
                                     adapter.get("content_name").lower().strip() + ":" in v.lower().strip()]), 0)

        chapter_save_dir = os.path.join(self.save_dir, adapter.get("book_name"))
        os.makedirs(chapter_save_dir, exist_ok=True)
        # TODO: Normalize the conversion of content names to book names, specifically extract away the "and"
        chapter_save_file = os.path.join(chapter_save_dir, adapter.get("content_name").lower().strip()
                                         .replace(" ", "_").replace(":", "-") + ".txt")

        with open(chapter_save_file, "w", encoding="utf-8") as writer:
            for line in chapter_lines_list[first_good_line:]:
                writer.write(line + "\n")
