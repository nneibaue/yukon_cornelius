'''Sites-specific Prospectors.'''

import re

from . import utils

class ClassicCars(ProspectorBase):
    def _is_id_tag(self, tag):
        condition1 = tag.name == 'span'
        condition2 = utils.check_class(tag, 'name')
        return (condition1 and condition2)

    def _process_id(self, id_tag):
        return id_tag.find('a').attrs['name']

    def _is_name_tag(self, tag):
        # Same tag as id tag
        return self._is_id_tag(tag)

    def _process_name(self, name_tag):
        #return str(name_tag)
        return name_tag.find('b').text

    def _is_date_tag(self, tag):
        condition1 = tag.text.startswith('Posted')
        condition2 = tag.name == 'span'
        condition3 = utils.check_class(tag, 'postdetails')
        return (condition1 and condition2 and condition3)

    def _process_date(self, date_tag):
        '''Converts to datetime object and saves as iso format.'''
        try:
            s = re.search(self.constants.POST_DATE_PATTERN, date_tag.text)
            year = int(s['year'])
        except TypeError:
            breakpoint()

        month = self.constants.MONTHS[s['month'].lower()]
        hour = int(s['hour']) - 1
        if s['ampm'] == 'pm':
            hour += 12
        date = datetime(int(s['year']), month, int(s['day']), hour, int(s['minute']))
        return date.isoformat()

    def _is_body_tag(self, tag):
        condition1 = tag.name == 'span'
        condition2 = utils.check_class(tag, 'postbody')
        condition3 = tag.text != ''
        return (condition1 and condition2 and condition3)

    def _process_body(self, body_tag):
        return body_tag.text

    def _is_forum_end(self, tag):
        condition1 = re.search(self.constants.POST_END_PATTERN, tag.text)
        condition2 = tag.name == 'span'
        condition3 = utils.check_class(tag, 'gen')
        return (condition1 and condition2 and condition3)
    
    def _turn_page(self):
        current_page = self.state['current_page']
        self.log(f'Starting page {current_page + 1}')
        self.set_state('current_page', current_page + 1)
        self.set_state('current_source',
                       f'{self.root_source}&start={current_page * 15}')
        self.make_soup()