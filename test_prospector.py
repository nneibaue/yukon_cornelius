import unittest
import re

from bs4.element import Tag
from parameterized import parameterized

import constants
import prospector
import utils


class TestProspectorBase(unittest.TestCase):
    
    def test_instantiation_from_valid_website(self):
        p = prospector._ProspectorBase('sample_forum')
        self.assertIsInstance(p, prospector._ProspectorBase)

    @parameterized.expand([
        ('current_source', 'foobar.html'),
        ('current_tag', Tag(name='a')),
        ('current_page', 3)
    ])
    def test_set_state(self, var_name, value):
        p = prospector._ProspectorBase('sample_forum')
        p.set_state(var_name, value)
        self.assertEqual(p.state[var_name], value)

    @parameterized.expand([
        ('current_source', 4),
        ('current_tag', 1),
        ('current_page', 'foobar')
    ])
    def test_set_state_with_wrong_type_raises_exception(self, var_name, value):
        p = prospector._ProspectorBase('sample_forum')
        with self.assertRaisesRegex(TypeError, '.'):
            p.set_state(var_name, value)

        
    @parameterized.expand(['soup', 'is_finised', 'num_mines', 'num_ore'])
    def test_attempt_to_set_state_with_readonly_vars_raises_exception(self, var_name):
        p = prospector._ProspectorBase('sample_forum')
        with self.assertRaisesRegex(ValueError, f'Cannot set the state of {var_name}'):
            p.set_state(var_name, None)

            
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