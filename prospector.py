import requests
import bs4
import re

import constants
import utils

class InvalidSourceError(Exception):
    '''Raised when an invalid html or url string is passed to Propectors.'''
    pass



class Ore:
    '''Class that holds raw html tags containing important attributes.'''
    def __init__(self, attrs):
        for attr in attrs:
            setattr(self, attr, None)

        self._attr_names = attrs

    @property
    def attributes(self):
        return {name: getattr(self, name) for name in self._attr_names}


    @property
    def complete(self):
        '''Returns True if all attributes have a non-None value.'''
        if all(self.attributes.values()):
            return True
        else:
            return False

    @property
    def bare(self):
        '''Returns true if all attributes are None.'''
        if not any(self.attributes.values()):
            return True
        else:
            return False

    def __repr__(self):
        val_list = ', '.join([f'{name}={self.attributes[name]}'
                              for name in self.attributes]) 
        return f'Ore({val_list})'

        

class ProspectorBase:

    # Data type to hold a collection of post tags. Ore will be sent out for
    # processing into (ingots? crystals? data?)
    def __init__(self, site_name):
        config = utils.load_config()
        if site_name not in config:
            raise NameError(f'{site_name} not found! Please check configuration file')

        self._config = config[site_name]
        self._root_source = self._config['source']
        self._attributes = self._config['attributes']

        self._current_source = self._config['source']
        self._current_tag = None
        self._current_ore = Ore(['id', 'name', 'date', 'body'])
        self._soup = None

        self._is_finished = False
        self._current_page = 0

        # make the first soup
        self._make_soup()
        self._move_to_next_tag()

        # List to hold Ore objects
        self._ore_cart = []
        self._num_mines = 0


    @property
    def ore_cart(self):
        return self._ore_cart
    
    def mine(self):
        '''Walks through the forum and extracts post information.'''
        while True:
            #self._num_mines += 1
            # End condition
            if self._is_finished:
                return

            if self._current_tag is None or self._is_forum_end(self._current_tag):
                self.is_finished = True

            # Turn the page
            elif self._is_page_end(self._current_tag):
                self._turn_page()
                self._make_soup()

            # Mine tags that match, dumping the current ore if necessary
            for i, attribute in enumerate(self._attributes):
                tester = getattr(self, f'_is_{attribute}_tag')
                processor = getattr(self, f'_process_{attribute}')

                if(tester(self._current_tag)):
                    # Dump the current ore if it's not bare
                    if i == i and not self._current_ore.bare:
                        self._dump_ore
                    setattr(self._current_ore, attribute, processor(self._current_tag))
                
                
            # Dump the ore if complete
            if self._current_ore.complete:
                self._dump_ore()
                        
            # Move on
            self._move_to_next_tag()

    def _dump_ore(self):
        '''Adds the current ore (post) to the ore cart and creates a bare ore.'''
        if not self._current_ore.bare:
            self._ore_cart.append(self._current_ore)
            self._current_ore = Ore(['id', 'name', 'date', 'body'])
        print('Ore Dumped')

    def _make_soup(self):
        '''Makes new soup.'''
        self._soup = utils.make_soup(self._current_source, self._config['source_type'])

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
                
    def _is_forum_end(self, tag):
        raise NotImplementedError

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