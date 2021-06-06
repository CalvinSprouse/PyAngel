from bs4 import BeautifulSoup
import requests
import re

# TODO: Convert regex to labeled regex with ?P<label> for ease of use and elimination of key_num_index field


# link class
class ChapterLink:
    def __init__(self, chapter_link, chapter_title, chapter_number):
        self.chapter_link = chapter_link
        self.chapter_title = chapter_title
        self.chapter_number = chapter_number


class BookLink:
    def __init__(self, chapter_links):
        self.chapter_links = chapter_links


# link converter
def main_story_link_finder(main_link, chapter_key):
    return main_link


def side_story_link_finder(main_link, re_key=None, header_keyword=None, key_num_index=None):
    # if there is no supplied method to locate then it is assumed the link is the one and only link to the text
    if re_key is None and header_keyword is None:
        return main_link

    # else: get page content
    link_page = requests.get(main_link)
    soup = BeautifulSoup(link_page.content, "html.parser")

    # the re_key is easier to use than the header keyword
    if re_key:
        assert key_num_index is not None and key_num_index >= 0
        chapter_link_list = []
        for link in soup.find_all("a"):
            key_search = re_key.findall(link.text)
            if key_search:
                chapter_link_list.append(ChapterLink(link, key_search[0][0], key_search[0][key_num_index]))
        return BookLink(chapter_link_list)


# story links
the_last_angel = main_story_link_finder(main_link="https://forums.spacebattles.com/threads/the-last-angel.244209/",
                                        chapter_key=re.compile(r"((Chapter\s*(\d*.\d*))((\s*and\s*)(\s*(Interlude|Interrupt)\s*)([(]((\d.?)*)[)]))?|Prologue|Epilogue)"))
the_angels_fire = side_story_link_finder(main_link="https://forums.spacebattles.com/threads/the-last-angel.244209/",
                                         re_key=re.compile(r"((The Angel's Fire Pt.)(\s*)(\d*):(.*))"), key_num_index=3)

exit()

story_time = side_story_link_finder(main_link="https://forums.spacebattles.com/posts/50554450/")
uneasy_lie_the_heads = side_story_link_finder(main_link="https://forums.spacebattles.com/posts/40580693/")
buried_in_the_past = side_story_link_finder(main_link="https://forums.spacebattles.com/posts/51153448/")
test_run = None
snow = None
predator_prey = side_story_link_finder(main_link="https://forums.spacebattles.com/threads/the-last-angel-ascension.346640/",
                                       header_keyword=r"Predator, Prey (complete)")
names_of_the_demon = side_story_link_finder(main_link="https://forums.spacebattles.com/threads/the-last-angel-ascension.346640/",
                                            header_keyword=r"Names of the Demon (complete)")

ascension = side_story_link_finder(main_link="https://forums.spacebattles.com/threads/the-last-angel-ascension.346640/",
                                   re_key=re.compile(r"((Chapter\s*(\d*.\d*))((\s*and\s*)\s*(Interregnum|Intersection):\s*(.*))?|Prologue|Epilogue)"))
awakening = side_story_link_finder(main_link="https://forums.spacebattles.com/threads/the-last-angel-ascension.346640/",
                                   header_keyword=r"Awakening (complete)")

quiet = side_story_link_finder(main_link="https://forums.spacebattles.com/posts/36803929/")
stillness = side_story_link_finder(main_link="https://forums.spacebattles.com/posts/47584427/")
entomology = side_story_link_finder(main_link="https://forums.spacebattles.com/threads/the-last-angel-ascension.346640/post-64314240")
final_line = side_story_link_finder(main_link="https://forums.spacebattles.com/threads/the-last-angel-ascension.346640/post-64935675")

hungry_stars = main_story_link_finder(main_link="https://forums.spacebattles.com/threads/the-last-angel-the-hungry-stars.868549/",
                                      chapter_key=re.compile(r"((Chapter\s*(\d*))((\s*and\s*)(Interrupt):(.*))?|Prologue|Epilogue)"))