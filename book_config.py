from abc import abstractmethod

import re


class Library:
    def __init__(self, book_list: list, series_name: str):
        self.book_list = book_list
        self.series_name = series_name

    def get_series_name(self):
        return self.series_name

    def get_book_list(self):
        return self.book_list

    def __repr__(self):
        return f"Series {self.get_series_name()} Books: {len(self.get_book_list())}"


class BaseBook:
    def __init__(self, chapter_list: list, title: str):
        self.chapter_dict = {}
        self.chapter_list = chapter_list
        self.order_chapters()

        self.title = title

    def order_chapters(self, chapter_num_re: re.Pattern = None):
        self.chapter_dict = {}
        if not chapter_num_re:
            chapter_num_re = re.compile(r"Chapter\s*(?P<chapter_num>(\d*[.]?)*)")
        for chapter in self.chapter_list:
            chapter_search = chapter_num_re.search(chapter.get_name())
            if chapter_search:
                self.chapter_dict[f"chapter-{chapter_search.groups('chapter_num')}"] = chapter

    def get_title(self):
        return self.title

    def get_chapter_dict(self):
        return self.chapter_dict

    def __repr__(self):
        return f"Title: {self.get_title()} Chapters: {len(self.get_chapter_dict().values())}"


class BaseChapter:
    def __init__(self, line_list: list, title: str):
        self.line_list = line_list
        self.title = title.strip()

    def clean_data(self):
        self.repair_chapter_title()
        self.trim_line_list()

    def repair_chapter_title(self, chapter_re: re.Pattern = None):
        """Remove things like extra spaces"""
        if not chapter_re:
            chapter_re = re.compile(r"^(?P<chapter_name>Chapter)\s+(?P<chapter_num>\d+)$", re.IGNORECASE)
        standard_chapter_search = chapter_re.search(self.title)
        if standard_chapter_search:
            self.title = f"{standard_chapter_search.group('chapter_name')} {standard_chapter_search.group('chapter_num')}"

    def trim_line_list(self, chapter_re: re.Pattern = None):
        """Cut off the lines before the chapter title appears"""
        if not chapter_re:
            chapter_re = re.compile(f"\\s*{self.title}\\s*", re.IGNORECASE)

        for index, line in enumerate(self.line_list, start=0):
            if chapter_re.search(line):
                self.line_list = self.line_list[index:]
                return

    @abstractmethod
    def does_belong(self, base_thread: str):
        """Determines if the threadmark will result in a chapter that belongs to this type"""

    def get_title(self):
        return self.title

    def get_line_list(self):
        return self.line_list

    def __repr__(self):
        return f"Title: {self.get_title()} Lines: {len(self.get_line_list())}"


class LastAngelBook(BaseBook):
    def __init__(self, chapter_dict: list, title: str):
        super().__init__(chapter_dict, title)


class LastAngelChapter(BaseChapter):
    def __init__(self, line_list: list, title: str):
        super().__init__(line_list, title)
        self.repair_chapter_title()
        self.trim_line_list()

    def does_belong(self, base_thread: str):
        return base_thread == "the-last-angel" and re.search("^(Chapter|Prologue|Epilogue)", self.title, re.IGNORECASE)


class AngelsFireBook(BaseBook):
    def __init__(self, chapter_dict: list, title: str):
        super().__init__(chapter_dict, title)


class AngelsFireChapter(BaseChapter):
    def __init__(self, line_list: list, title: str):
        super().__init__(line_list, title)
        self.repair_chapter_title(chapter_re=re.compile(
            r"^(?P<chapter_name>The\s*Angel's\s*Fire\s*Chapter)\s+(?P<chapter_num>\d+)$", re.IGNORECASE))
        self.trim_line_list(chapter_re=re.compile(
            r"^((Part\s*One:)|(Pt[.]?\s*\d+:))\s*(\w*\s?)", re.IGNORECASE))

    def does_belong(self, base_thread: str):
        return base_thread == "the-last-angel" and re.search(r"^The\s*Angel's\s*Fire\s*Chapter", self.title,
                                                             re.IGNORECASE)
