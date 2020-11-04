import unittest
import prospector


class TestProspectorBase(unittest.TestCase):

    def setUp(self):
        with open('sample_forum.html', 'r') as f:
            self.html = f.read()
            self.p = prospector.Prospector(self.html)
            
    
    def test_instantiation_from_url(self):
        p = prospector.Prospector(self.html)

    def test_instantiation_from_invalid_url(self):
        pass

    def test_instantiation_from_valid_html(self):
        pass

    def test_instantiation_from_invalid_html(self):
        pass
