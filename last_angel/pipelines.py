from itemadapter import ItemAdapter
from scrapy.exporters import JsonLinesItemExporter
from scrapy.exceptions import DropItem
import os


class FileOutputPipeline:
    # TODO: Find way to introduce custom settings (like save location) into settings.py
    save_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chapters", "data")

    def __init__(self):
        self.thread_to_exporter = None
        self.post_ids_recorded = set()
        self.content_names_recorded = set()

    def open_spider(self, spider):
        self.thread_to_exporter = {}

    def close_spider(self, spider):
        for exporter, json_lines_file in self.thread_to_exporter.values():
            exporter.finish_exporting()
            json_lines_file.close()
        # TODO: Run PDF generator from here

    def _exporter_for_item(self, item):
        adapter = ItemAdapter(item)
        thread = adapter.get("book_name", default="other")
        if thread not in self.thread_to_exporter:
            os.makedirs(os.path.abspath(self.save_dir), exist_ok=True)
            json_file = open(os.path.join(self.save_dir, f"{thread}.jl"), mode="wb")
            exporter = JsonLinesItemExporter(json_file)
            exporter.start_exporting()
            self.thread_to_exporter[thread] = (exporter, json_file)
        return self.thread_to_exporter[thread][0]

    def process_item(self, item, spider):
        self._exporter_for_item(item).export_item(item)
        return item


class CheckDuplicatesPipeline:
    def __init__(self):
        self.unique_values_logged = set()

    def process_item(self, item, spider):
        unique_keys = getattr(item, "unique_key", None)
        if not unique_keys:
            return item
        keys = convert_to_tuple(unique_keys)
        unique_value = None
        try:
            unique_value = "-".join(map(str, [item.get(k) for k in keys]))
        except KeyError:
            # TODO: Find way to access spider logger
            pass
        if unique_value in self.unique_values_logged:
            raise DropItem(f"Duplicate item {unique_value}")
        else:
            self.unique_values_logged.add(unique_value)
            return item


def convert_to_tuple(possible_tuple):
    return possible_tuple if isinstance(possible_tuple, (tuple, list)) else (possible_tuple,)
