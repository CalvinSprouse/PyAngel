from bs4 import BeautifulSoup
import requests
import re


# link class
class ChapterLink:
    def __init__(self, chapter_link, chapter_title, chapter_number):
        self.chapter_link = chapter_link
        self.chapter_title = chapter_title
        self.chapter_number = chapter_number

    def get_num(self):
        return self.chapter_number

    def get_link(self):
        return self.chapter_link


class BookLink:
    def __init__(self, chapter_links):
        self.chapter_links = chapter_links


# link converter
def get_links_below_header(raw_html: str, header):
    link_list = []
    found_header = False
    basic_re = re.compile(r"(?P<chapter>Chapter\s*(?P<num>\d*)(\s*(-)\s*(.*))?|Prologue|Epilogue)")

    for line in raw_html.split("\n"):
        if header in line:
            found_header = True
        elif found_header:
            if "href" in line:
                link_list.append(line)
            elif basic_re.search(line) is None:
                break
    return link_list


def main_story_link_finder(main_link, chapter_key):
    return main_link


def side_story_link_finder(main_link, re_key=None, header_keyword=None):
    # if there is no supplied method to locate then it is assumed the link is the one and only link to the text
    if re_key is None and header_keyword is None:
        return main_link

    # variables
    chapter_link_list = []
    basic_re = re.compile(r"(?P<chapter>Chapter\s*(?P<num>\d*)(\s*(-)\s*(.*))?|Prologue|Epilogue)")

    # else: get page content
    link_page = requests.get(main_link)
    soup = BeautifulSoup(link_page.content, "html.parser")

    # the re_key is easier to use than the header keyword
    if re_key:
        for link in soup.find_all("a"):
            key_search = re_key.search(link.text)
            if key_search:
                print(key_search.group("chapter"), key_search.group("num"), link["href"])
                chapter_link_list.append(ChapterLink(link["href"], key_search.group("chapter"), key_search.group("num")))
    # if the header_keyword is used then the post must be parsed for the header, then subsequent links parsed like above
    elif header_keyword:
        found_header = False

        # print the links as one line of text
        for link in BeautifulSoup(("\n".join(get_links_below_header(link_page.text, header_keyword))), "html.parser"):
            try:
                link_search = basic_re.search(link.text)
                if link_search:
                    chapter_link_list.append(ChapterLink(link["href"], link_search.group("chapter"), link_search.group("num")))
                    print(link_search.group("chapter"), link_search.group("num"), link["href"])
            except AttributeError:
                pass
    return BookLink(chapter_link_list)


# story links
print("> The Last Angel")
the_last_angel = main_story_link_finder(main_link="https://forums.spacebattles.com/threads/the-last-angel.244209/",
                                        chapter_key=re.compile(r"(?P<chapter>(Chapter\s*(?P<num>\d*.\d*))((\s*and\s*)(\s*(Interlude|Interrupt)\s*)([(]((\d.?)*)[)]))?|Prologue|Epilogue)"))
print("> The Angels Fire")
the_angels_fire = side_story_link_finder(main_link="https://forums.spacebattles.com/threads/the-last-angel.244209/",
                                         re_key=re.compile(r"(?P<chapter>(The Angel's Fire Pt.)(\s*)(?P<num>\d*):(.*))"))

print("> Story Time")
story_time = side_story_link_finder(main_link="https://forums.spacebattles.com/posts/50554450/")
print("> Uneasy Lie The Heads")
uneasy_lie_the_heads = side_story_link_finder(main_link="https://forums.spacebattles.com/posts/40580693/")
print("> Buried in the Past")
buried_in_the_past = side_story_link_finder(main_link="https://forums.spacebattles.com/posts/51153448/")
print("> Test Run")
test_run = None
print("> Snow")
snow = None
print("> Predator, Prey")
predator_prey = side_story_link_finder(main_link="https://forums.spacebattles.com/threads/the-last-angel-ascension.346640/",
                                       header_keyword=r"Predator, Prey (complete)")

print("> Names of the Demon")
names_of_the_demon = side_story_link_finder(main_link="https://forums.spacebattles.com/threads/the-last-angel-ascension.346640/",
                                            header_keyword=r"Names of the Demon (complete)")

print("> Ascension")
ascension = main_story_link_finder(main_link="https://forums.spacebattles.com/threads/the-last-angel-ascension.346640/",
                                   chapter_key=re.compile(r"(?P<chapter>(Chapter\s*(?P<num>\d*.\d*))((\s*and\s*)\s*(Interregnum|Intersection):\s*(.*))?|Prologue|Epilogue)"))
print("> Awakening")
awakening = side_story_link_finder(main_link="https://forums.spacebattles.com/threads/the-last-angel-ascension.346640/",
                                   header_keyword=r"Awakening (complete)")

print("> Quiet")
quiet = side_story_link_finder(main_link="https://forums.spacebattles.com/posts/36803929/")
print("> Stillness")
stillness = side_story_link_finder(main_link="https://forums.spacebattles.com/posts/47584427/")
print("> Entomology")
entomology = side_story_link_finder(main_link="https://forums.spacebattles.com/threads/the-last-angel-ascension.346640/post-64314240")
print("> Final Line")
final_line = side_story_link_finder(main_link="https://forums.spacebattles.com/threads/the-last-angel-ascension.346640/post-64935675")

print("> Hungry Stars")
hungry_stars = main_story_link_finder(main_link="https://forums.spacebattles.com/threads/the-last-angel-the-hungry-stars.868549/",
                                      chapter_key=re.compile(r"(?P<chapter>(Chapter\s*(?P<num>\d*))((\s*and\s*)(Interrupt):(.*))?|Prologue|Epilogue)"))