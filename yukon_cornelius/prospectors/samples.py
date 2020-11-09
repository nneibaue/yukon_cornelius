'''Sample Prospectors used for testing.'''

from .. import utils
from .base import ProspectorBase

class SampleNoProcessors(ProspectorBase):
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


class SampleWithDateProcessor(SampleNoProcessors):
    def _process_date(self, tag):
        return tag.text