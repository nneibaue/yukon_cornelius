import bs4
import requests
import re
import json
import pandas as pd
import os

import constants

class InvalidSourceError(Exception):
    '''Raised if source is not valid.'''
    pass

class InvalidConfigError(Exception):
    '''Rasied if config file is not valid.'''
    pass

def load_website_config(site_name):
    '''Loads the configuration for a specific website.
    
    Args:
      site_name: str. A website defined in the config file `constants.CONFIG_FILE.`
      
    '''
    with open(constants.CONFIG_FILE, 'r') as f:
        config = json.load(f)

    if site_name not in config.keys():
        raise InvalidConfigError(f'{site_name} not found in config!')

    # Make sure each website has required keys
    missing_keys = []
    keys = config[site_name].keys()
    for req_key in constants.REQUIRED_CONFIG_KEYS:
        if req_key not in keys:
            missing_keys.append(req_key)
    if missing_keys:
        raise InvalidConfigError(f'Website {site_name} is missing the following'
                                    f'keys: {missing_keys}') 

    return config[site_name]


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

def refine_ore(ore_list, export_filetype='csv'):
    '''Returns DataFrame of content in `ore_list`, optionally exporting.
    
    Args:
      ore_list. list of Ore objects. All Ores in this list must have the same value
        for `Ore.site_name`. It is very unlikely that any other scenario would occur.
      export_filetype: str. Filetype for export. Valid filetypes are defined in
        `constants.VALID_ORE_EXPORT_TYPES`
       '''
    
    if not isinstance(ore_list, list):
        raise ValueError(f'Expected list, got {type(ore_list)}')

    site_name = ore_list[0].site_name

    ore_dicts = []
    for i, ore in enumerate(ore_list):
        if ore.site_name != site_name:
            raise ValueError(f'All Ore should come from {site_name}. Found Ore from '
                             f'{ore.site_name}')
        ore_dicts.append(ore.attributes)

    df = pd.DataFrame(ore_dicts)

    # Make export directory if it doesn't exist
    if not os.path.isdir(constants.EXPORT_DIR):
        os.makedirs(constants.EXPORT_DIR)

    exporter = getattr(df, f'to_{export_filetype}')
    filepath = os.path.join(constants.EXPORT_DIR, f'{site_name}.{export_filetype}')
    exporter(filepath)
    return df
