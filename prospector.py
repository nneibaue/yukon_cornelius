import requests
import bs4
import re
from datetime import datetime

import constants
import utils

class InvalidSourceError(Exception):
    '''Raised when an invalid html or url string is passed to Propectors.'''
    pass



class Ore:
    '''Data structure for holding "mined" attributes.'''
    def __init__(self, attrs, default=None):
        '''Create instance attributes from `attrs` and defaults to `default`.'''
        for attr in attrs:
            setattr(self, attr, default)
        self._attr_names = attrs

    @property
    def attributes(self):
        '''Returns a dictionary of the current attributes and values.'''
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

    def __init__(self, site_name):
        config = utils.load_website_config(site_name)
        self._config = config
        self._site_name = site_name
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
                self._is_finished = True
                return

            # Turn the page
            elif self._is_page_end(self._current_tag):
                self._turn_page()
                self._make_soup()

            for i, attribute in enumerate(self._attributes):

                # Function that accepts a tag and returns a boolean
                tester = f'_is_{attribute}_tag'

                # Function that accedpts a tag and returns a string
                processor = f'_process_{attribute}'

                # Ensure proper methods are defined for tag testing
                if not hasattr(self, tester):
                    raise NotImplementedError(
                        f'Must implement `{tester}` for "{self._site_name}" website')

                tester = getattr(self, tester)

                if(tester(self._current_tag)):
                    if i == 0 and not self._current_ore.bare:
                        self._dump_ore

                    # Uses a processor if exists
                    if hasattr(self, processor):
                        processor = getattr(self, processor)
                        this_attribute = processor(self._current_tag)
                    else:
                        this_attribute = str(self._current_tag)
                        
                    setattr(self._current_ore, attribute, this_attribute)

            # Move on
            if self._current_ore.complete:
                self._dump_ore()
            self._move_to_next_tag()

    def _dump_ore(self):
        '''Adds the current ore (post) to the ore cart and creates a bare ore.'''
        if not self._current_ore.bare:
            self._ore_cart.append(self._current_ore)
            self._current_ore = Ore(self._attributes)

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

    def _process_id(self, id_tag):
        return id_tag.find('a').attrs['name']

    def _is_name_tag(self, tag):
        # Same tag as id tag
        return self._is_id_tag(tag)

    def _process_name(self, name_tag):
        #return str(name_tag)
        return name_tag.find('b').text

    def _is_date_tag(self, tag):
        condition1 = tag.text.startswith('Posted')
        condition2 = tag.name == 'span'
        condition3 = utils.check_class(tag, 'postdetails')
        return (condition1 and condition2 and condition3)

    def _process_date(self, date_tag):
        '''Converts to datetime object and saves as iso format.'''
        try:
            s = re.search(constants.ClassicCars.POST_DATE_PATTERN, date_tag.text)
            year = int(s['year'])
        except TypeError:
            breakpoint()

        month = constants.ClassicCars.MONTHS[s['month'].lower()]
        hour = int(s['hour']) - 1
        if s['ampm'] == 'pm':
            hour += 12
        date = datetime(int(s['year']), month, int(s['day']), hour, int(s['minute']))
        return date.isoformat()

    def _is_body_tag(self, tag):
        condition1 = tag.name == 'span'
        condition2 = utils.check_class(tag, 'postbody')
        condition3 = tag.text != ''
        return (condition1 and condition2 and condition3)

    def _process_body(self, body_tag):
        return body_tag.text

    def _is_forum_end(self, tag):
        condition1 = re.search(constants.ClassicCars.POST_END_PATTERN, tag.text)
        condition2 = tag.name == 'span'
        condition3 = utils.check_class(tag, 'gen')
        return (condition1 and condition2 and condition3)
    
    def _turn_page(self):
        print(f'TURNING TO PAGE {self._current_page}')
        self._current_page += 1
        self._current_source = f'{self._root_source}&start={self._current_page * 15}'
        self._make_soup()
    