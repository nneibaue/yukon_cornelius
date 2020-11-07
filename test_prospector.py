import unittest
from bs4.element import Tag
import prospector
import utils


class SampleProspector(prospector.ProspectorBase):
    '''Prospector used for testing of sample_forum.html.'''

    def _is_id_tag(self, tag):
        return utils.check_class(tag, 'id')

    def _is_name_tag(self, tag):
        return utils.check_class(tag, 'name')

    def _is_date_tag(self, tag):
        return utils.check_class(tag, 'date')

    def _is_post_body_tag(self, tag):
        return utils.check_class(tag, 'postbody')

    def _is_forum_end(self, tag):
        return utils.check_class(tag, 'forumend')

    def _turn_page(self):
        self._is_finished = True


class TestProspectorBase(unittest.TestCase):

    def setUp(self):
        with open('sample_forum.html', 'r') as f:
            self.html = f.read()
            
    
    def test_instantiation_from_valid_html(self):
        p = prospector.ProspectorBase(self.html)
        self.assertIsInstance(p, prospector.ProspectorBase)

    def test_instantiation_from_valid_url(self):
        p = prospector.ProspectorBase('https://www.google.com')
        self.assertIsInstance(p, prospector.ProspectorBase)

    def test_instantiation_from_invalid_url_raises_exception(self):
        with self.assertRaises(prospector.InvalidSourceError):
            p = prospector.ProspectorBase(5)

    def test_instantiation_from_invalid_html_raises_exception(self):
        with self.assertRaises(prospector.InvalidSourceError):
            p = prospector.ProspectorBase(5)

    def test_cannot_mine_with_base_class(self):
        p = prospector.ProspectorBase(self.html)
        
        with self.assertRaises(NotImplementedError):
            p.mine()

class TestSampleProspector(unittest.TestCase):

    def setUp(self):
        with open('sample_forum.html', 'r') as f:
            self.html = f.read()

    def test_mine(self):
        p = SampleProspector(self.html)
        p.mine()
        self.assertEqual(len(p.ore_cart), 4)
        for ore in p.ore_cart:
            self.assertIsInstance(ore.id, Tag)
            self.assertIsInstance(ore.name, Tag)
            self.assertIsInstance(ore.date, Tag)
            self.assertIsInstance(ore.body, Tag)

    
if __name__ == '__main__':
    unittest.main()