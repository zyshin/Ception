# author = scyue

from HTMLParser import HTMLParser
from utils import start_str, end_str, stadardlize_text
import types


class ContentParser(HTMLParser):
    '''
    Some Constants from CKEDTIOR:
    CKEDITOR.SENTENCE_NEW = -10;
    CKEDITOR.SENTENCE_SPLIT = -9;
    CKEDITOR.SENTENCE_UNDEFINED = -1;

    Call get_info to acquire a info array which contains all the sentence info dicts
    Sentence Info Dict:
        sid: sentence id (ContentParser.New if new)
        related: Array of pair: (related sentence id, relationship)
        content: pure sentence content
        status: Unchanged / Edited / Deleted
    '''

    def __init__(self):
        HTMLParser.__init__(self)
        self.info_array = []
