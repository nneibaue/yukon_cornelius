import unittest
from parameterized import parameterized
from bs4 import BeautifulSoup
from pandas import DataFrame
import os

from ..prospectors import samples
from .. import constants
from .. import utils
    

class TestLoadConfig(unittest.TestCase):
    def test_load_sample_forum_config(self):
        config = utils.load_website_config('sample_forum')
        self.assertIsInstance(config, dict)

    def test_load_site_with_missing_keys_raises_exception(self):
        with self.assertRaisesRegex(utils.InvalidConfigError, 'missing the following'):
            config = utils.load_website_config('test_website_with_missing_keys')

    def test_attempt_to_load_missing_site_raises_exception(self):
        with self.assertRaisesRegex(utils.InvalidConfigError, 'google not found'):
            config = utils.load_website_config('google')


class TestMakeSoup(unittest.TestCase):

    def test_make_soup_from_valid_url(self):
        soup = utils.make_soup('https://www.google.com', 'https_url')
        self.assertIsInstance(soup, BeautifulSoup)

    def test_make_soup_from_invalid_url(self):
        with self.assertRaisesRegex(utils.InvalidSourceError, 'https_url'):
            soup = utils.make_soup('thiswebsite.com', 'https_url')

    def test_make_soup_from_valid_html_file(self):
        soup = utils.make_soup('/Users/nate/flashpoint/yukon_cornelius/'
                               'tests/sample_forum.html', 'html_file')
        self.assertIsInstance(soup, BeautifulSoup)

    def test_make_soup_from_invalid_html_file(self):
        with self.assertRaisesRegex(utils.InvalidSourceError, 'html_file'):
            soup = utils.make_soup('thiswebsite.txt', 'html_file')

    def test_make_soup_with_invalid_source_type(self):
        with self.assertRaisesRegex(utils.InvalidSourceError,
                                     'not a valid source type'):
            soup = utils.make_soup('sample_forum.html', 'html')


class TestCheckClass(unittest.TestCase):

    def setUp(self):
        soup = BeautifulSoup()
        self.tag = soup.new_tag('div', attrs={'class': 'foobar'})
        self.tag_noclasses = soup.new_tag('div')

    def test_valid_class_returns_true(self):
        self.assertTrue(utils.check_class(self.tag, 'foobar'))

    def test_invalid_class_returns_false(self):
        self.assertFalse(utils.check_class(self.tag, 'barfoo'))

    def test_no_classes_returns_false(self):
        self.assertFalse(utils.check_class(self.tag_noclasses, 'classname'))
        

class TestRefineOre(unittest.TestCase):
    
    def setUp(self):
       self.p = samples.SampleNoProcessors('sample_forum')
       self.p.mine()

    # Test all export types dynamically. This ensures that when a new export type is
    # added, the test should not have to be updated
    @parameterized.expand(constants.VALID_ORE_EXPORT_TYPES)
    def test_refine_valid_ore_(self, export_type):
        df = utils.refine_ore(self.p.ore_cart, export_type)
        self.assertIsInstance(df, DataFrame)
        path = os.path.join(constants.EXPORT_DIR, f'sample_forum.{export_type}')
        self.assertTrue(os.path.exists(path))

    def tearDown(self):
        for f in os.listdir(constants.EXPORT_DIR):
            if f.startswith('sample_forum'):
                fullpath = os.path.join(constants.EXPORT_DIR, f)
                os.remove(fullpath)

if __name__ == '__main__':
    unittest.main()