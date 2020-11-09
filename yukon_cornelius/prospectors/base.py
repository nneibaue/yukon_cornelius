import requests
import bs4
import re
from datetime import datetime

from .. import constants
from .. import utils

class InvalidSourceError(Exception):
    '''Raised when an invalid html or url string is passed to Propectors.'''
    pass

class _Ore:
    '''Data structure for holding "mined" attributes.'''
    def __init__(self, attrs, site_name, attr_default=None):
        '''Create instance attributes from `attrs` and defaults to `default`.'''
        for attr in attrs:
            setattr(self, attr, attr_default)
        self._attr_names = attrs
        self.site_name = site_name

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

        # Load class specific constants if defined in `constants.py`
        if 'prospector_class' in config and \
            hasattr(constants,config['prospector_class']):
            self.constants = getattr(constants, config['prospector_class'])
        else:
            self.constants = None

        # Class-specific attributes
        self.config = config
        self.site_name = site_name
        self.root_source = self.config['source']
        self.attributes = self.config['attributes']

        # State variables
        self._current_source = self.config['source']
        self._current_tag = None
        self._current_ore = _Ore(self.attributes, self.site_name)
        self._soup = None
        self._is_finished = False
        self._current_page = 0

        # make the first soup
        self.make_soup()
        self._move_to_next_tag()

        # List to hold Ore objects
        self._ore_cart = []
        self._num_mines = 0

    @property
    def state(self):
        '''Returns the current value of all dynamic state variables.'''
        return {
            'current_source': self._current_source,
            'current_tag': self._current_tag,
            'current_ore': self._current_ore,
            'current_page': self._current_page,
            'soup': self._soup,
            'is_finished': self._is_finished,
            'num_mines': self._num_mines,
            'num_ore': len(self.ore_cart),
        }
    
    def set_state(self, var_name, value):
        '''Sets the state of `var_name` to `value`.
        
        The only state variables that can be set are:
          - 'current_source',
          - 'current_tag',
          - 'current_page'
        '''
        state_types = {'current_source': type('foobar'),
                       'current_tag': type(bs4.element.Tag(name='a')),
                       'current_page': type(5)}

        if var_name not in state_types:
            raise ValueError(f'Cannot set the state of {var_name}')
        
        if type(value) != state_types[var_name]:
            raise TypeError(f'{var_name} expected type {state_types[var_name]}. Got '
                            f'type {type(value)}')

        setattr(self, f'_{var_name}', value)

    @property
    def ore_cart(self):
        return self._ore_cart

    def log(self, s):
        '''Prints a string prepended with the site name.'''
        print(f'{self.site_name}: {s}')
    
    def mine(self):
        '''Walks through the forum and extracts post information.'''
        self.log('Mining started')
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
                self.make_soup()

            for i, attribute in enumerate(self.attributes):

                # Function that accepts a tag and returns a boolean
                tester = f'_is_{attribute}_tag'

                # Function that accedpts a tag and returns a string
                processor = f'_process_{attribute}'

                # Ensure proper methods are defined for tag testing
                if not hasattr(self, tester):
                    raise NotImplementedError(
                        f'Must implement `{tester}` for "{self.site_name}" website')

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
            self._current_ore = _Ore(self.attributes, self.site_name)

    def make_soup(self):
        '''Makes new soup from the current source.'''
        self._soup = utils.make_soup(self._current_source, self.config['source_type'])

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


        
        