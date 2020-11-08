import bs4
import requests
import re
import json

import constants

class InvalidSourceError(Exception):
    '''Raised if source is not valid.'''
    pass


def load_config():
    with open(constants.CONFIG, 'r') as f:
        config = json.load(f)

    return config


def make_soup(source, source_type):
    '''Makes soup from a source.'''
    
    if source_type not in constants.VALID_SOURCE_TYPES:
        raise InvalidSourceError(f'{source_type} not a valid source type. Valid types'
                                 f' are: {constants.VALID_SOURCE_TYPES}')
    
    if source_type == 'html_file':
        if not source.endswith('.html'):
            raise InvalidSourceError(f'Invalid {source_type}')
        with open(source, 'r') as f:
            html = f.read()
    
    elif source_type == 'https_url':
        if not source.startswith('https://www.'):
            raise InvalidSourceError(f'Invaid {source_type}')    
        html = requests.get(source).text

    return bs4.BeautifulSoup(html, features='lxml')


    
def validate_url(url):
    '''Returns True if url is valid and can send a response.'''
    if not isinstance(url, str):
        return False
    
    if not re.search(constants.Patterns.VALID_URL, url):
        return False
    
    return url
    
    
def check_class(tag, classname):
    '''Returns True if `tag` has a class `classname`.
    
    Args:
      tag: bs4.element.Tag
      classname: str
    '''
    if not tag.attrs:
        return False 

    elif 'class' not in tag.attrs:
        return False
    
    return classname in tag.attrs['class']
