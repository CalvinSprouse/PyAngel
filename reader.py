from data_repair import generate_lists_from_json
import asyncio


async def main():
    async for chapter in generate_lists_from_json("the-last-angel.jl"):
        print(chapter)
        await asyncio.sleep(1)


# TODO: Sort each item from the jl lists into a class for its "book", that class can then handle parsing and shit
if __name__ == "__main__":
    asyncio.run(main())
