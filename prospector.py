import requests
import bs4
import re

import constants
import utils

class InvalidSourceError(Exception):
    '''Raised when an invalid html or url string is passed to Propectors.'''
    pass


class OreProcessorBase:
    pass

class Ore:
    '''Class that holds raw html tags containing important attributes.'''
    def __init__(self):
        self.id = None
        self.name = None
        self.date = None
        self.body = None


    @property
    def complete(self):
        '''Returns True if all attributes have a non-None value.'''
        if all([self.id, self.name, self.date, self.body]):
            return True
        else:
            return False

    @property
    def bare(self):
        '''Returns true if all attributes are None.'''
        if not any([self.id, self.name, self.date, self.body]):
            return True
        else:
            return False

    def __repr__(self):
        return f'Ore(id={self.id}, name={self.name}, date={self.date}, body={self.body})'

    

class ProspectorBase:

    # Data type to hold a collection of post tags. Ore will be sent out for
    # processing into (ingots? crystals? data?)
    def __init__(self, html_or_url):
        
        if utils.validate_html(html_or_url):
            self._html = html_or_url
            self._url = None
        
        elif utils.validate_url(html_or_url):
            self._url = html_or_url

        else:
            raise InvalidSourceError('Must pass a valid url or html string!')
        

        self._current_tag = None
        self._current_ore = Ore()
        self._soup = None
        self._is_finished = False
        self._inside_post = False
        self._current_page = 0

        # make the first soup
        self._make_soup()
        self._move_to_next_tag()

        self._ore_cart = []
        self._num_mines = 0


    @property
    def url(self):
        return self._url

    @property
    def ore_cart(self):
        return self._ore_cart
    
    
    def mine(self):
        '''Walks through the forum and extracts post information.'''
        self._num_mines += 1

        # End condition
        if self._is_finished:
            return

        if self._current_tag is None or self._is_forum_end(self._current_tag):
            self.is_finished = True
            self.mine()

        # Turn the page
        elif self._is_page_end(self._current_tag):
            self._turn_page()
            self._make_soup()
            self.mine()

        # Mine a post, dumping the current ore if necessary
        if self._is_id_tag(self._current_tag):
            if not self._current_ore.bare:
                self._dump_ore()
            self._current_ore.id = self._current_tag

        if self._is_name_tag(self._current_tag):
            self._current_ore.name = self._current_tag

        if self._is_date_tag(self._current_tag):
            self._current_ore.date = self._current_tag

        if self._is_post_body_tag(self._current_tag):
            self._current_ore.body = self._current_tag
            
        # Dump the ore if complete
        if self._current_ore.complete:
            self._dump_ore()
                    
        # Move on
        self._move_to_next_tag()
        self.mine()

    def _dump_ore(self):
        '''Adds the current ore (post) to the ore cart and creates a bare ore.'''
        if not self._current_ore.bare:
            self._ore_cart.append(self._current_ore)
            self._current_ore = Ore()
        print('Ore Dumped')

    def _make_soup(self):
        '''Makes soup from the current url or html content.'''
        print(f'CURRENT PAGE: {self._current_page}')
        if self._url is not None:
            self._html = requests.get(self._url).text
        self._soup = bs4.BeautifulSoup(self._html, 'html.parser')

        # Make tag to mark the end of this page
        new_soup = bs4.BeautifulSoup()
        end_tag = new_soup.new_tag('div', attrs={'class': constants.PAGE_END_CLASS})
        self._soup.insert(-1, end_tag)
        
        self._current_tag = self._soup.find('html')


    def _move_to_next_tag(self):
        '''Moves forward until another Tag or None is found.'''
        self._current_tag = self._current_tag.next
        while not isinstance(self._current_tag, bs4.element.Tag):
            self._current_tag = self._current_tag.next
            if self._current_tag is None:
                break
                
                
    def _is_id_tag(self, tag):
        '''Returns True if `tag` contains the post id.'''
        raise NotImplementedError('ProspectorBase class cannot be used for mining')
    
    def _is_name_tag(self, tag):
        '''Returns True if `tag` contains the post author's name.'''
        raise NotImplementedError('ProspectorBase class cannot be used for mining')

    def _is_date_tag(self, tag):
        '''Returns True if `tag` contains the post date.'''
        raise NotImplementedError('ProspectorBase class cannot be used for mining')

    def is_post_body_tag(self, tag):
        '''Returns True if `tag` contains the post body.'''
        raise NotImplementedError('ProspectorBase class cannot be used for mining')

    def _is_forum_end(self, tag):
        '''Returns True if `tag` is the end of the forum.'''
        raise NotImplementedError('ProspectorBase class cannot be used for mining')

    def _is_page_end(self, tag):
        '''Returns True if `tag` signals the end of the page.'''
        return utils.check_class(tag, constants.PAGE_END_CLASS)

    def _turn_page(self):
        '''Modifies url or html to point to the next page. Default is no effect.'''
        pass

    
class ClassicCarsProspector(ProspectorBase):
    def _is_id_tag(self, tag):
        condition1 = tag.name == 'span'
        condition2 = utils.check_class(tag, 'name')
        return (condition1 and condition2)

    def _is_name_tag(self, tag):
        # Same tag as id tag
        return self._is_id_tag(tag)

    def _is_date_tag(self, tag):
        condition1 = re.search(constants.Patterns.POST_DATE, tag.text)
        condition2 = tag.name == 'span'
        condition3 = utils.check_class(tag, 'postdetails')
        return (condition1 and condition2 and condition3)

    def _is_post_body_tag(self, tag):
        condition1 = tag.name == 'span'
        condition2 = utils.check_class(tag, 'postbody')
        return (condition1 and condition2)

    def _is_forum_end(self, tag):
        condition1 = re.search(constants.Patterns.POST_END, tag.text)
        condition2 = tag.name == 'span'
        condition3 = utils.check_class(tag, 'gen')
        return (condition1 and condition2 and condition3)
    
    def _turn_page(self):
        print(f'TURNING TO PAGE {self._current_page}')
        self._current_page += 1
        self._url = f'{self._url}&start={self._current_page * 15}'
        self._make_soup()
    
    
    

    # def _mine_single_post(self):
    #     '''Adds one piece of Ore to the cart.'''
    #     print('INSIDE POST')
    #     self.insidePost = True
    #     id_ = None
    #     name = None
    #     date = None
    #     body = None

    #     while not self._is_post_end(self._current_tag):

    #         # Note: no 'elif' since one tag could contain multiple attributes
    #         if self._is_id_tag(self._current_tag):
    #             print('ID TAG FOUND')
    #             id_ = self._current_tag
    #         if self._is_name_tag(self._current_tag):
    #             print('NAME TAG FOUND')
    #             name = self._current_tag
    #         if self._is_date_tag(self._current_tag):
    #             print('DATE TAG FOUND')
    #             date = self._current_tag
    #         if self._is_post_body_tag(self._current_tag):
    #             print('BODY TAG FOUND')
    #             body = self._current_tag

    #         # Move one tag forward
    #         self._move_to_next_tag()
        
    #     self._ore_cart.append(ProspectorBase.Ore(id_, name, date, body))
    #     self.insidePost = False