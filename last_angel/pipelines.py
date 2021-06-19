from itemadapter import ItemAdapter
from scrapy.exporters import JsonLinesItemExporter
from scrapy.exceptions import DropItem
import os


class LastAngelPipeline:
    save_dir = "chapters"

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
        adapter = ItemAdapter(item)
        self._exporter_for_item(item).export_item(item)
        self.post_ids_recorded.add(adapter.get("post_id"))
        self.content_names_recorded.add(adapter.get("content_name"))
        return item
