from bs4 import BeautifulSoup
import os
import json


def generate_pdfs():
    # TODO: Clip chapter data to after the chapter name (remove header info)

    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chapters", "data")
    save_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chapters", "reader")

    for json_file in [jl for jl in os.listdir(data_dir) if jl.endswith(".jl")]:
        # get lines from the .jl file
        json_line_list = []
        with open(os.path.join(data_dir, json_file)) as reader:
            for line in reader.readlines():
                json_line_list.append(json.loads(line))
        file_line_list = list(reversed(json_line_list))

        # establish the save dir for that book
        chapter_save_dir = os.path.join(save_dir, json_line_list[0]["book_name"].lower().replace(" ", "_"))
        os.makedirs(chapter_save_dir)

        # extract and write the lines for each chapter
        chapter_lines = []
        for chapter in json_line_list:
            for line in chapter["raw_html"]:
                line_soup = BeautifulSoup(line.strip(), "html.parser")
                if line_soup.text.strip() != "":
                    chapter_lines.append(line_soup.text + "\n")
                # TODO: Fix encoding (currently windows 125 or something should be utf-8)
                # TODO: charmap cant encode character \u200b in pos 163
                with open(os.path.join(chapter_save_dir, chapter["content_name"].lower().replace(" ", "_")) + ".txt",
                          "w") as writer:
                    writer.writelines(chapter_lines)


generate_pdfs()
