import bs4
import requests

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

    return True

    
def validate_url(url):
    '''Returns True if url is valid and can send a response.'''
    if not isinstance(url, str):
        return False
    
    return url
    
