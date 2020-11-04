from collections import namedtuple
import requests
import bs4

import constants
import utils


class Prospector:

    # Data type to hold a collection of post tags. Ore will be sent out for
    # processing into (ingots? crystals? data?)
    PostOre = namedtuple('PostOre', ('id', 'name', 'date', 'body'))
    def __init__(self, html_or_url):
        if not isinstance(html_or_url, str):
            raise TypeError('Must pass in html string or url!')

        elif html_or_url.startswith('<!doctype html>'):
            self._url = None
        
        if utils.validate_html(html_or_url):
            self._html = html_or_url
            self._url = None
        
        elif utils.validate_url(html_or_url):
            self._url = html_or_url


        
        self.insidePost = False

        self._current_tag = None
        self._soup = None
        self._url = forum_url_root

        # make the first soup
        self._make_soup()

        self._ore_cart = []


    @property
    def url(self):
        return self._url

    @property
    def post_ore(self):
        return self._ore_cart

    def _make_soup(self):
        html = requests.get(self._url)
        self._soup = bs4.BeautifulSoup(html, 'html.parser')
        self._current_tag = self._soup.find('html')
            
            
    def _get_html(self):
        '''Retrieves html content from url, if exists.'''
        if self._url is not None:
            self._html = requests.get(self._url).text
    
    
    def mine(self):
        '''Walks through the forum and extracts post information.'''
        if _is_forum_end(self._current_tag):
            return

        elif _is_page_end(self._current_tag):
            self._turn_page()
            self._make_soup()

        elif _is_post_start(self._current_tag):
            self._mine_single_post()
            
        self._current_tag = self._current_tag.next
        self.mine()


    def _mine_single_post(self):
        '''Adds one piece of Ore to the cart.'''
        self.insidePost = True
        id_ = None
        name = None
        date = None
        body = None

        while not self._is_post_end(self._current_tag):
            if self._is_id_tag(self._current_tag):
                id_ = self._current_tag
            elif self._is_name_tag(self._current_tag):
                name = self._current_tag
            elif self._is_date_tag(self._current_tag):
                date = self._current_tag
            elif self._is_body_tag(self._current_tag):
                body = self._current_tag

            # Move one tag forward
            self._current_tag = self._current_tag.next
        
        self.posts.append(Prospector.PostOre(id_, name, date, body))
        self.insidePost = False
                

    def _is_post_start(self, tag):
        '''Returns True if `tag` is the start of a post.'''
        raise NotImplementedError('Base Prospector class cannot be used for mining')

    def _is_post_end(self, tag):
        '''Returns True if `tag` is the end of a post.'''
        raise NotImplementedError('Base Prospector class cannot be used for mining')

    def _is_id_tag(self, tag):
        '''Returns True if `tag` contains the post id.'''
        raise NotImplementedError('Base Prospector class cannot be used for mining')
    
    def _is_name_tag(self, tag):
        '''Returns True if `tag` contains the post author's name.'''
        raise NotImplementedError('Base Prospector class cannot be used for mining')

    def _is_date_tag(self, tag):
        '''Returns True if `tag` contains the post date.'''
        raise NotImplementedError('Base Prospector class cannot be used for mining')

    def is_post_body_tag(self, tag):
        '''Returns True if `tag` contains the post body.'''
        raise NotImplementedError('Base Prospector class cannot be used for mining')

    def _is_forum_end(self, tag):
        '''Returns True if `tag` is the end of the forum.'''
        raise NotImplementedError('Base Prospector class cannot be used for mining')

    def _is_page_end(self, tag):
        '''Returns True if `tag` signals the end of the page. Default is "html"'''
        if tag.name == 'html':
            return True

    def _turn_page(self):
        '''Modifies url to point to the next page. Default is no effect.'''
        pass