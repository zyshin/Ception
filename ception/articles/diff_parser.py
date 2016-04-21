# author = scyue

from HTMLParser import HTMLParser
from utils import start_str, end_str, stadardlize_text
from new_parser import SentenceInfo
import diff_match_patch as dmp_module

class DiffParser(HTMLParser):
    """
    Some Constants from CKEDTIOR:
    CKEDITOR.SENTENCE_NEW = -10;
    CKEDITOR.SENTENCE_SPLIT = -9;
    CKEDITOR.SENTENCE_UNDEFINED = -1;

    Call get_info to acquire a info array which contains all the sentence info dicts
    """

    dmp = dmp_module.diff_match_patch()

    def __init__(self, origin_array):
        HTMLParser.__init__(self)
        self.origin_array = origin_array
        self.current = SentenceInfo()
        self.diff_content = ""
        self.in_pd = False
        self.in_pd_delete = False
        self.in_ins = False
        self.in_del = False
        self.pd_attr = None
        self.pd_content = ""


    def handle_starttag(self, tag, attrs):
        if tag == 'ins':
            self.in_ins = True
        elif tag == 'del':
            self.in_del = True
            if self.in_pd:
                self.in_pd_delete = True
        elif tag == 'pd':
            self.in_pd = True
            self.current.status = SentenceInfo.UNCHANGED
            self.current.process_attr(attrs)
            self.pd_attr = attrs

    def handle_endtag(self, tag):
        if tag == 'ins':
            self.in_ins = False
        elif tag == 'del':
            self.in_del = False
        elif tag == 'pd':
            self.in_pd = False
            if self.current.sid > 0 and self.current.status != SentenceInfo.REPLACE:
                self.diff_content += DiffParser.diff(self.origin_array[self.current.sid - 1], self.current.content)
                self.diff_content += start_str('pd', self.pd_attr)
                if self.in_pd_delete:
                    self.diff_content += start_str('del')
                self.diff_content += self.pd_content
                if self.in_pd_delete:
                    self.diff_content += end_str('del')
                self.diff_content += end_str('pd')
                self.current = SentenceInfo()
            elif not self.in_pd_delete:
                self.current.content += self.pd_content
            self.in_pd_delete = False

    def handle_data(self, data):
        if self.in_pd:
            self.pd_content = data
        elif self.in_del:
            pass
        else:
            self.current.content += data

    @classmethod
    def diff(cls, s1, s2):
        d = cls.dmp.diff_main(s1, s2)
        cls.dmp.diff_cleanupSemantic(d)
        return cls.dmp.diff_html(d)


if __name__ == '__main__':
    from ception.articles.simple_parser import SimpleParser

    origin = '<p>Sentence 1<pd sid="1">.</pd> Sentence 2<pd sid="2">.</pd> Sentence 3<pd sid="3">.</pd> Sentence 4<pd sid="4">.</pd>Sentence 5<pd sid="5">.</pd> Sentence 6<pd sid="6">.</pd> </p>'
    text = '<p>Sent<ins class="ice-ins ice-cts" data-cid="3"><pd replaced="true" sid="1">.</pd></ins>ence 1<pd sid="1"><del class="ice-del ice-cts" data-cid="2">.</del></pd> Sentence<del class="ice-del ice-cts" data-cid="4"> 2</del><pd rsid="[]" sid="2"><del class="ice-del ice-cts" data-cid="4">.</del></pd> Sentence 3<pd rsid="[2]" sid="3">.</pd> Sent<ins class="ice-ins ice-cts" data-cid="7"><pd sid="-9" tsid="4">.</pd></ins>ence 4<pd sid="4">.</pd> Sentence 5<pd sid="5">.</pd> Sentence 6<pd sid="6">.</pd></p>'
    sp = SimpleParser()
    sp.feed(origin)
    origin_array = sp.sentence_array
    parser = DiffParser(origin_array)
    parser.feed(text)
    print parser.diff_content
