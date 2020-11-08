import bs4
import requests
import re
import json

import constants

class InvalidSourceError(Exception):
    '''Raised if source is not valid.'''
    pass

class InvalidConfigError(Exception):
    '''Rasied if config file is not valid.'''
    pass

def load_website_config(site_name):
    with open(constants.CONFIG_FILE, 'r') as f:
        config = json.load(f)

    if site_name not in config.keys():
        raise InvalidConfigError(f'{site_name} not found in config!')

    # Make sure each website has required keys
    missing_keys = []
    keys = config[site_name]
    for req_key in constants.REQUIRED_CONFIG_KEYS:
        if req_key not in keys:
            missing_keys.append(req_key)
    if missing_keys:
        raise InvalidConfigError(f'Website {site_name} is missing the following'
                                    f'keys: {missing_keys}') 

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
