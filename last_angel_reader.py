import asyncio
import json
import os
import re


async def read_chapters_json(filename: str):
    with open(os.path.join("last_angel", "last_angel", "spiders", "chapters", filename)) as file_reader:
        for line in file_reader.readlines():
            yield json.loads(line.strip())


async def main():
    async for chapter in read_chapters_json("the-last-angel.jl"):
        print(chapter)
        await asyncio.sleep(1)


# TODO: Sort each item from the jl lists into a class for its "book", that class can then handle parsing and shit
if __name__ == "__main__":
    asyncio.run(main())
