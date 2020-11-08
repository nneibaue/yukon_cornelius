'''Collection of constants (urls, regex patterns, etc) used for scraping.'''


PAGE_END_CLASS = 'page-end'
CONFIG_FILE = 'website_config.json'

VALID_SOURCE_TYPES = ['html_file', 'https_url']
REQUIRED_CONFIG_KEYS = ['source', 'source_type', 'attributes']

MONTHS = {
    'jan': 1,
    'january': 1,
    'feb': 2,
    'february': 2,
    'mar': 3,
    'march': 3,
    'apr': 4,
    'april': 4,
    'may': 5,
    'jun': 6,
    'june': 6,
    'jul': 7,
    'july': 7,
    'aug': 8,
    'august': 8,
    'sep': 9,
    'september': 9,
    'oct': 10,
    'october': 10,
    'nov': 11,
    'november': 11,
    'dec': 12,
    'december': 12,
}


class Patterns:
    POST_LINK = 'viewtopic.php\?p=(?P<post_id>[0-9]*)&.*'
    POST_DATE = (
        'Posted: [a-zA-Z]{3} (?P<month>[a-zA-Z]{3}) (?P<day>[0-9]{1,2}), '
        '(?P<year>[0-9]{4}) (?P<hour>[0-9]{1,2}):(?P<minute>[0-9]{1,2}) (?P<ampm>am|pm)')
    VALID_HTML = '^<!doctype html>.*'
    VALID_URL = '^(http|https)://www.*'
    ID_TAG = '^[0-9]+$'
    POST_END = 'No posts exist for this topic'