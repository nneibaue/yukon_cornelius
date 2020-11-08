import unittest
from bs4.element import Tag
import utils
import re

import constants
import prospector


class TestProspectorBase(unittest.TestCase):
    
    def test_instantiation_from_valid_website(self):
        p = prospector._ProspectorBase('sample_forum')
        self.assertIsInstance(p, prospector._ProspectorBase)

    def test_cannot_mine_with_base_class(self):
        p = prospector._ProspectorBase('sample_forum')
        
        with self.assertRaises(NotImplementedError):
            p.mine()


class TestSampleNoProcesors(unittest.TestCase):

    def test_mine_all_attributes(self):
        p = prospector.SampleNoProcessors('sample_forum')
        p.mine()
        self.assertEqual(len(p.ore_cart), 4)
        for ore in p.ore_cart:
            self.assertIsInstance(ore.id, str)
            self.assertIsInstance(ore.name, str)
            self.assertIsInstance(ore.date, str)
            self.assertIsInstance(ore.body, str)


class TestSampleWithDateProcessor(unittest.TestCase):

    def test_date_is_processed(self):
        p = prospector.SampleWithDateProcessor('sample_forum')
        p.mine()
        dates = [ore.date for ore in p.ore_cart]

        self.assertEqual(dates, ['10/1/2000',
                                 '10/1/2000',
                                 '10/1/2000',
                                 '10/1/2000'])
    
p = prospector.SampleWithDateProcessor('sample_forum')
p.mine()

if __name__ == '__main__':
    unittest.main()