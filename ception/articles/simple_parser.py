# author = scyue

from HTMLParser import HTMLParser
from utils import stadardlize_text


class SimpleParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.sentence_array = []
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
    def get_clean_test(data):
        parser = CleanParser()
        parser.feed(stadardlize_text(data))
        return parser.clean_sentence


if __name__ == '__main__':
    text = '<p>Sentence 1 <pd sid="1">.</pd> Sentence 2 <pd sid="2">.</pd> Sentence 3 <pd sid="3">.</pd> Sentence 4 <pd sid="4">.</pd> Sentence 5 <pd sid="5">.</pd> Sentence 6 <pd sid="6">.</pd></p>'
    parser = SimpleParser()
    parser.feed(text)
