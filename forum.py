import requests
import bs4
import re

import constants

post_end_pattern = re.compile('No posts exist for this topic')


def is_post(tag):
    if not tag.name == 'table':
        return False
    
    def is_post_link(tag):
        print(tag.name)
        if not tag.has_attr('href'):
            print('no href found')
            return False
        elif not re.search(constants.POST_LINK_PATTERN, tag.attrs['href']):
            print('regex not matched')
            return False
        else:
            return True

    if not tag.find(is_post_link):
        print('post link not found')
        return False

    if not tag.find(attrs={'class': 'postdetails'}):
        return False

    return True


def get_forum_area(url):
    html = requests.get(url).text
    soup = bs4.BeautifulSoup(html, 'html.parser')
    return soup.find(attrs={'class', 'forumline'})
    
def get_all_pages(base_url):
    start = 0
    forums = []
    while True:
        this_forum = get_forum_area(base_url + f'&start={start}')
        print(base_url + f'&start={start}')
        if this_forum.find(lambda tag: re.search(post_end_pattern, tag.text)):
            break
        else:
            forums.append(this_forum)
            start += 10

    return forums

class AbstractPost:
    pass