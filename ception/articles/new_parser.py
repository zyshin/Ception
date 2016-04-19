# author = scyue

from HTMLParser import HTMLParser
from utils import start_str, end_str, stadardlize_text
import types


class SentenceInfo(object):
    """
    Sentence Info Dict:
        sid: sentence id
        related: Array of pair: (related sentence id, relationship)
        content: pure sentence content
        status: Unchanged / Edited / Deleted / NEW / UNKNOWN
    """
    DELETED = 0
    EDITED = 1
    NEW = 2
    UNCHANGED = 3
    SPLIT = 4
    REPLACE = 5
    REMOVED = 6

    REVERT_DICT = [
        'Deleted',
        'Edited',
        'New',
        'Unchanged',
        'Split',
        'Replace',
        'Removed'
    ]

    def __init__(self):
        self.sid = 0
        self.origin_sid = 0
        self.related = []
        self.content = ""
        self.status = SentenceInfo.UNCHANGED

    def process_attr(self, attrs):
        attr_dict = {}
        for pair in attrs:
            attr_dict[pair[0]] = pair[1]
        self.sid = int(attr_dict["sid"])
        if attr_dict.has_key("tsid"):
            self.related.append((int(attr_dict["tsid"]), SentenceInfo.SPLIT))
        if attr_dict.has_key("replaced"):
            self.related.append((self.sid, SentenceInfo.REPLACE))
            self.status = SentenceInfo.REPLACE
        if self.sid < 0:
            self.status = SentenceInfo.NEW

    def to_dict(self):
        return {
            'sid': self.sid,
            'related': self.related,
            'content': self.content,
            'status': self.status
        }

    def __unicode__(self):
        related_str = ""
        for pair in self.related:
            related_str += '({0}, {1}) '.format(pair[0], SentenceInfo.REVERT_DICT[pair[1]])
        return '{sid: ' + str(self.sid) + \
               ', related: [ ' + related_str + ']' + \
               ', content: ' + self.content + \
               ', status: ' + SentenceInfo.REVERT_DICT[self.status] + \
               '};'

    def __str__(self):
        return self.__unicode__()


class ContentParser(HTMLParser):
    """
    Some Constants from CKEDTIOR:
    CKEDITOR.SENTENCE_NEW = -10;
    CKEDITOR.SENTENCE_SPLIT = -9;
    CKEDITOR.SENTENCE_UNDEFINED = -1;

    Call get_info to acquire a info array which contains all the sentence info dicts
    """

    def __init__(self):
        HTMLParser.__init__(self)
        self.info_array = []
        self.current = SentenceInfo()
        self.in_pd = False
        self.in_pd_delete = False
        self.in_ins = False

    def handle_starttag(self, tag, attrs):
        if tag == 'ins' or tag == 'del':
            self.current.content += start_str(tag)
            self.current.status = SentenceInfo.EDITED
        if tag == 'ins':
            self.in_ins = True
        elif tag == 'del':
            if self.in_pd:
                self.in_pd_delete = True
        elif tag == 'pd':
            self.in_pd = True
            self.current.process_attr(attrs)

    def handle_endtag(self, tag):
        if tag == 'ins' or tag == 'del':
            self.current.content += end_str(tag)
        if tag == 'ins':
            self.in_ins = False
        elif tag == 'del':
            self.in_delete = False
        elif tag == 'pd':
            self.in_pd = False
            if self.in_pd_delete:
                self.current.status = SentenceInfo.DELETED
            if self.in_ins:
                self.current.content += "</ins>"
            self.info_array.append(self.current)
            self.current = SentenceInfo()
            if self.in_ins:
                self.current.content += "<ins>"
                self.current.status = SentenceInfo.EDITED
            if self.in_pd_delete:
                self.current.status = SentenceInfo.EDITED
            self.in_pd_delete = False

    def handle_data(self, data):
        self.current.content += data

    @staticmethod
    def get_info(text):
        parser = ContentParser()
        parser.feed(stadardlize_text(text))
        return parser.info_array


def eliminate_replace(info_array):
    origin_count = 0
    replace_dict = [False]  # Start From 1
    replace_dict.extend([True if x.status == SentenceInfo.REPLACE else False for x in info_array])
    for i in range(len(info_array)):
        s = info_array[i]
        if s.sid > origin_count:
            origin_count = s.sid
        if s.sid > 0 and replace_dict[s.sid] and s.status == SentenceInfo.DELETED:
            info_array[i - 1].content += "<del>" + s.content + "</del>"
            info_array[i + 1].content = "<ins>" + s.content + "</ins>" + info_array[i + 1].content
            s.status = SentenceInfo.REMOVED
        if s.sid < 0:
            ii = i
            while ii < len(info_array) - 1 and info_array[ii].sid < 0:
                ii += 1
            s.origin_sid = info_array[ii].sid

    return origin_count


def set_mapping_array(info_array, origin_count):
    mapping_array = ["Error"]
    mapping_array.extend(["" for x in range(origin_count)])
    current_related_sid = []
    current_sentence_array = []
    former_sentence_array = []
    for j in range(len(info_array)):
        s = info_array[j]
        if s.status == SentenceInfo.REMOVED:
            continue
        current_sentence_array.append(s)
        current_related_sid.append(s.sid)
        if s.sid > 0 and s.status != SentenceInfo.DELETED:

            positive_sentence_count = 0
            for ss in current_sentence_array:
                if ss.sid > 0:
                    positive_sentence_count += 1

            former_content = "<span class='context'>"
            for ss in former_sentence_array:
                former_content += ss.content
            former_content += "</span>"

            latter_content = "<span class='context'>"
            for jj in range(j + 1, len(info_array)):
                latter_content += info_array[jj].content
            latter_content += "</span>"


            for i in current_related_sid:
                if i > 0:
                    content = "<span id='current'>"
                    for ss in current_sentence_array:
                        if positive_sentence_count > 1 and (ss.sid == i or (ss.sid < 0 and ss.origin_sid == i)):
                            content += "<span class='highlight'>" + ss.content + "</span>"
                        else:
                            content += ss.content
                    content += "</span>"
                    sentence_info_dict = {
                        'content': former_content + content + latter_content,
                        'id': s.sid,
                        'edited': not s.status == SentenceInfo.UNCHANGED
                    }
                    mapping_array[i] = sentence_info_dict
            former_sentence_array.extend(current_sentence_array)
            current_related_sid = []
            current_sentence_array = []
    return mapping_array


def get_mapping_array(text):
    info_array = ContentParser.get_info(text)
    origin_count = eliminate_replace(info_array)
    return set_mapping_array(info_array, origin_count)


if __name__ == '__main__':
    text = '<p>Sent<ins class="ice-ins ice-cts" data-cid="3"><pd replaced="true" sid="1">.</pd></ins>ence 1<pd sid="1"><del class="ice-del ice-cts" data-cid="2">.</del></pd> Sentence<del class="ice-del ice-cts" data-cid="4"> 2</del><pd rsid="[]" sid="2"><del class="ice-del ice-cts" data-cid="4">.</del></pd> Sentence 3<pd rsid="[2]" sid="3">.</pd> Sent<ins class="ice-ins ice-cts" data-cid="7"><pd sid="-9" tsid="4">.</pd></ins>ence 4<pd sid="4">.</pd> Sentence 5<pd sid="5">.</pd> Sentence 6<pd sid="6">.</pd></p>'
    info = get_mapping_array(text)
