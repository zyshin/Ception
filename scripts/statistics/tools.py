from HTMLParser import HTMLParser

def stadardlize_text(text):
    return text.replace("&nbsp;", " ").replace("&#39;", "'")

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


def count_word(content):
    clean_text = CleanParser.get_clean_text(content)
    no_punc_text= clean_text.replace(',', ' ').replace('.', ' ')
    return len(no_punc_text.split())
