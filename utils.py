import bs4
import requests
import re

import constants

class InvalidHtmlError(Exception):
    '''Raised if html is not valid.'''
    pass


class InvalidUrlError(Exception):
    '''Raised if html is not valid.'''
    pass


def validate_html(html):
    '''Returns True if `html` is valid.
    
    Args:
      html: str. HTML page'''
    
    if not isinstance(html, str):
        return False

    if not re.search(constants.Patterns.VALID_HTML, html):
        return False

    return True

    
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