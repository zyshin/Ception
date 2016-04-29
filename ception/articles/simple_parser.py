# author = scyue

from HTMLParser import HTMLParser

from utils import stadardlize_text, start_str, end_str


class SimpleParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.sentence_array = [""]
        self.in_pd = False

    def handle_starttag(self, tag, attrs):
        if tag == 'pd':
            self.in_pd = True

    def handle_endtag(self, tag):
        if tag == 'pd':
            self.in_pd = False

    def handle_data(self, data):
        if not self.in_pd:
            self.sentence_array.append(data)

class CleanParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.clean_sentence = ""
        self.in_del = False

    def handle_starttag(self, tag, attrs):
        if tag == 'del':
            self.in_del = True

    def handle_endtag(self, tag):
        if tag == 'del':
            self.in_del = False

    def handle_data(self, data):
        if not self.in_del:
            self.clean_sentence += data

    @staticmethod
    def get_clean_text(data):
        parser = CleanParser()
        parser.feed(stadardlize_text(data))
        sentence = parser.clean_sentence
        return sentence.replace('.', '').replace('\n', '')


class FormalParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.formal_sentence = ""

    def handle_starttag(self, tag, attrs):
        if tag == 'ins':
            attrs.append(('class', 'ice-ins ice-cts'))
            attrs.append(('data-cid', '0'))
            self.formal_sentence += start_str(tag, attrs)
        elif tag == 'del':
            attrs.append(('class', 'ice-del ice-cts'))
            attrs.append(('data-cid', '0'))
            self.formal_sentence += start_str(tag, attrs)

    def handle_endtag(self, tag):
        if tag == 'ins' or tag == 'del':
            self.formal_sentence += end_str(tag)

    def handle_data(self, data):
        self.formal_sentence += data

    @staticmethod
    def get_formal_text(data):
        parser = FormalParser()
        parser.feed(stadardlize_text(data))
        return parser.formal_sentence

if __name__ == '__main__':
    # text = '<p>Sentence 1 <pd sid="1">.</pd> Sentence 2 <pd sid="2">.</pd> Sentence 3 <pd sid="3">.</pd> Sentence 4 <pd sid="4">.</pd> Sentence 5 <pd sid="5">.</pd> Sentence 6 <pd sid="6">.</pd></p>'
    text = ' <div class="replace" data-pk="1"><del>Users can switch between monolingual</del><ins>We provide the English only captions by default</ins></div> <ins>subtitle </ins>and<ins> the</ins> <del>bilingual</del><ins>dual</ins> <div class="replace" data-pk="0">subtitles<ins> are optional, and the user can switch between them</ins></div> by clicking the button on the bottom right'
    print FormalParser.get_formal_text(text)
