# creates PDF "books" of updated work for offline enjoyment
# imports

# class
# the book class contains a list of links (the main book class will expand on this function) and checks/formats to PDF
class ShortStoryBook:
    def __init__(self, link_list):
        self.link_list = link_list


class SideStoryBook:
    def __init__(self, link_list, keyword):
        self.link_list = link_list


# since main books have multiple links and are updated from the forum page their links must be acquired algorithmically
class MainBook:
    def __init__(self, story_page, keyword):
        # do a search for links based on keyword and convert that too link list
        story_links = []


# main
if __name__ == "__main__":
    pass
