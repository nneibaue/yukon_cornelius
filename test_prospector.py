import unittest
from bs4.element import Tag
import utils
import re

import constants
import prospector


class SampleProspectorNoProcessors(prospector.ProspectorBase):
    '''Prospector used for testing of sample_forum.html.'''

    def _is_id_tag(self, tag):
        return utils.check_class(tag, 'id')
    
    def _is_name_tag(self, tag):
        return utils.check_class(tag, 'name')

    def _is_date_tag(self, tag):
        return utils.check_class(tag, 'date')

    def _is_body_tag(self, tag):
        return utils.check_class(tag, 'postbody')

    def _is_forum_end(self, tag):
        return utils.check_class(tag, 'forumend')

    def _turn_page(self):
        self._is_finished = True

class SampleProspectorDateProcessor(SampleProspectorNoProcessors):
    def _process_date(self, tag):
        return tag.text


class TestProspectorBase(unittest.TestCase):
    
    def test_instantiation_from_valid_website(self):
        p = prospector.ProspectorBase('sample_forum')
        self.assertIsInstance(p, prospector.ProspectorBase)

    def test_cannot_mine_with_base_class(self):
        p = prospector.ProspectorBase('sample_forum')
        
        with self.assertRaises(NotImplementedError):
            p.mine()


class TestSampleProspectorNoProcesors(unittest.TestCase):

    def test_mine_all_attributes(self):
        p = SampleProspectorNoProcessors('sample_forum')
        p.mine()
        self.assertEqual(len(p.ore_cart), 4)
        for ore in p.ore_cart:
            self.assertIsInstance(ore.id, str)
            self.assertIsInstance(ore.name, str)
            self.assertIsInstance(ore.date, str)
            self.assertIsInstance(ore.body, str)


class TestSampleProspectorDateProcessor(unittest.TestCase):

    def test_date_is_processed(self):
        p = SampleProspectorDateProcessor('sample_forum')
        p.mine()
        dates = [ore.date for ore in p.ore_cart]

        self.assertEqual(dates, ['10/1/2000',
                                 '10/1/2000',
                                 '10/1/2000',
                                 '10/1/2000'])
    

if __name__ == '__main__':
    unittest.main()