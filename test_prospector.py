import unittest
from bs4.element import Tag
import utils
import re

import constants
import prospector


class SampleProspector(prospector.ProspectorBase):
    '''Prospector used for testing of sample_forum.html.'''

    def _is_id_tag(self, tag):
        return utils.check_class(tag, 'id')
    
    def _process_id(self, tag):
        return tag

    def _is_name_tag(self, tag):
        return utils.check_class(tag, 'name')

    def _process_name(self, tag):
        return tag

    def _is_date_tag(self, tag):
        return utils.check_class(tag, 'date')

    def _process_date(self, tag):
        return tag

    def _is_body_tag(self, tag):
        return utils.check_class(tag, 'postbody')

    def _process_body(self, tag):
        return tag

    def _is_forum_end(self, tag):
        return utils.check_class(tag, 'forumend')

    def _turn_page(self):
        self._is_finished = True


class SampleProspectorProcessDate(SampleProspector):
    def _process_date(self, tag):
        return tag.text


class TestProspectorBase(unittest.TestCase):
    
    def test_instantiation_from_valid_website(self):
        p = prospector.ProspectorBase('sample_forum')
        self.assertIsInstance(p, prospector.ProspectorBase)

    def test_instantiation_from_invalid_website(self):
        with self.assertRaises(NameError):
            p = prospector.ProspectorBase('google')

    def test_cannot_mine_with_base_class(self):
        p = prospector.ProspectorBase('sample_forum')
        
        with self.assertRaises(NotImplementedError):
            p.mine()


class TestSampleProspector(unittest.TestCase):

    def test_mine(self):
        p = SampleProspector('sample_forum')
        p.mine()
        self.assertEqual(len(p.ore_cart), 4)
        for ore in p.ore_cart:
            self.assertIsInstance(ore.id, Tag)
            self.assertIsInstance(ore.name, Tag)
            self.assertIsInstance(ore.date, Tag)
            self.assertIsInstance(ore.body, Tag)

p = SampleProspector('sample_forum')
p.mine()

if __name__ == '__main__':
    unittest.main()