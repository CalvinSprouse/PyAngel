from book_config import *
import asyncio
import json
import os


async def generate_list_from_json(filename: str):
    with open(filename, "rb") as file_reader:
        for line in file_reader.readlines():
            async for output in separate_combined_lists(json.loads(line.strip())):
                yield output


async def separate_combined_lists(post: dict):
    if any(char in post["threadmark"] for char in ["&", ",", "and"]):
        if post["base-thread"] == "the-last-angel":
            if "&" in post["threadmark"]:
                for item in post["threadmark"].split():
                    if item.isdigit():
                        yield {
                            "threadmark": f"Chapter {item}",
                            "post-id": post["post-id"],
                            "base-thread": post["base-thread"],
                            "url": post["url"],
                            "lines": post["lines"]}
            elif "," in post["threadmark"]:
                for item in post["threadmark"].split():
                    item = item.replace(",", "")
                    if item.isdigit():
                        yield {
                            "threadmark": f"Chapter {item}",
                            "post-id": post["post-id"],
                            "base-thread": post["base-thread"],
                            "url": post["url"],
                            "lines": post["lines"]}
                    elif item.lower() == "epilogue":
                        yield {
                            "threadmark": "Epilogue",
                            "post-id": post["post-id"],
                            "base-thread": post["base-thread"],
                            "url": post["url"],
                            "lines": post["lines"]}
    else:
        yield post


async def find_correct_chapter_class(post: dict, chapter_class_list: list = None):
    if not chapter_class_list:
        chapter_class_list = [LastAngelChapter, AngelsFireChapter]

    for chapter_class in chapter_class_list:
        new_chapter = chapter_class(post["lines"], post["threadmark"])
        if new_chapter.does_belong(post["base-thread"]):
            new_chapter.repair_chapter_title()
            return new_chapter


data_dir = os.path.join("last_angel", "last_angel", "spiders", "chapters")


async def get_library():
    async for post in generate_list_from_json(os.path.join(data_dir, "the-last-angel.jl")):
        post_chapter = await find_correct_chapter_class(post)
        print(post["threadmark"], post["post-id"], "=", post_chapter)

if __name__ == "__main__":
    asyncio.run(get_library())
