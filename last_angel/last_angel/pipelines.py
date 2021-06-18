from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
from scrapy.exporters import JsonLinesItemExporter
import os


class LastAngelPipeline:
    remove_names_list = [
        "Table of Contents",
        "Re: Spoilers"
    ]

    remove_contains_list = [
        "preview",
        "teaser"
    ]

    save_dir = "chapters"

    def __init__(self):
        self.thread_to_exporter = None

    def open_spider(self, spider):
        self.thread_to_exporter = {}

    def close_spider(self, spider):
        for exporter, json_lines_file in self.thread_to_exporter.values():
            exporter.finish_exporting()
            json_lines_file.close()

    def _exporter_for_item(self, item):
        """
        Gets an exporter ready for an item passed from process_item
        :param item: an item (dict) passed from the spider
        :return: an exporter object JsonLinesItemExporter
        """
        adapter = ItemAdapter(item)
        thread = adapter.get("base-thread")
        if thread not in self.thread_to_exporter:
            os.makedirs(os.path.abspath(self.save_dir), exist_ok=True)
            json_file = open(os.path.join(self.save_dir, f"{thread}.jl"), mode="wb")
            exporter = JsonLinesItemExporter(json_file)
            exporter.start_exporting()
            self.thread_to_exporter[thread] = (exporter, json_file)
        return self.thread_to_exporter[thread][0]

    def process_item(self, item, spider):
        """
        Takes a yielded bit of data from the spider as input and decides weather or not to keep it, if so then
        gets an exporter from the _exporter_for_item func and exports the data
        :param item: an item (dict) passed from the spider
        :param spider: a ref to the spider
        :return: the item for logging purposes i think
        """
        adapter = ItemAdapter(item)
        if adapter.get("threadmark") in self.remove_names_list:
            raise DropItem(f"Unwanted item found from remove_names_list "
                           f"{adapter.get('threadmark')} for post #{adapter.get('post-id')}")
        elif any([adapter.get("threadmark") in item for item in self.remove_names_list]):
            raise DropItem(f"Unwanted item found from remove_contains_list "
                           f"{adapter.get('threadmark')} for post #{adapter.get('post-id')}")

        self._exporter_for_item(item).export_item(item)
        return item


