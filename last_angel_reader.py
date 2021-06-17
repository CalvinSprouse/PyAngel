import asyncio
import json
import os
import re


async def read_chapters_json(filename: str):
    with open(os.path.join("last_angel", "last_angel", "spiders", "chapters", filename)) as file_reader:
        for line in file_reader.readlines():
            async for clean_dict in clean_chapter_dict(json.loads(line.strip())):
                yield clean_dict


def get_chapter_names(threadmark: str) -> list:
    chapter_name = threadmark.strip()
    inter_chapter_search = re.search(r"(Chapter\s*(?P<chapter_num>(\d*\.?)*)\s*and\s*(?P<additional>(Inter)(.*)))",
                                     chapter_name, re.IGNORECASE)
    regular_chapter_search = re.search(r"(Chapter\s*(?P<chapter_num>(\d*\.?)*))$",
                                       chapter_name, re.IGNORECASE)

    # TODO: Make chapter specific searches for things like angels fire and side stories

    chapter_names = []
    if chapter_name.lower() == "prologue":
        chapter_names = ["Prologue"]
    elif inter_chapter_search:
        chapter_names = [f"Chapter {inter_chapter_search.group('chapter_num')} "
                         f"and {inter_chapter_search.group('additional')}"]
    elif regular_chapter_search:
        chapter_names = [f"Chapter {regular_chapter_search.group('chapter_num')}"]
    elif "chapters" in chapter_name.lower():
        for string in chapter_name.split():
            string_search = re.search(r"(?P<id>(\d+)|Epilogue|Prologue)", string, re.IGNORECASE)
            if string_search:
                if string_search.group("id").lower() == "prologue":
                    chapter_names.append("Prologue")
                elif string_search.group("id").lower() == "epilogue":
                    chapter_names.append("Epilogue")
                else:
                    chapter_names.append(f"Chapter {string_search.group('id')}")
    return chapter_names


def trim_chapter_lines(chapter_lines: list, chapter_keyword: str) -> list:
    new_lines = [line for line in chapter_lines if "" != line.strip()]
    index = next(line for line in new_lines if chapter_keyword.lower() in line.lower())
    return chapter_lines[new_lines.index(index):]


async def clean_chapter_dict(chapter_dict: dict):
    chapter_names = get_chapter_names(chapter_dict["threadmark"])
    for name in chapter_names:
        yield {
            "name": name,
            "threadmark": chapter_dict["threadmark"],
            "post-id": chapter_dict["post-id"],
            "base-thread": chapter_dict["base-thread"],
            "url": chapter_dict["url"],
            "lines": trim_chapter_lines(chapter_dict["lines"], name)
        }


async def main():
    async for chapter in read_chapters_json("the-last-angel.jl"):
        print(chapter)


if __name__ == "__main__":
    asyncio.run(main())
