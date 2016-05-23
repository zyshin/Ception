from HTMLParser import HTMLParser

from ception.articles.utils import start_str, end_str


class DocParser(HTMLParser):
    def __init__(self, target):
        HTMLParser.__init__(self)
        self.target = target
        self.ignore = True
        self.target_content = ""
        self.in_target_doc = False
        self.p_count = 0
        self.in_text = False
        self.value_edit = False

    def handle_starttag(self, tag, attrs):
        if tag == 'doc' and attrs[0][1] == self.target:
            self.in_target_doc = True
        if tag == 'text' and self.in_target_doc:
            self.in_text = True
        if tag == 'p' and self.in_target_doc:
            self.p_count += 1
        if tag == 'annotation' and self.in_target_doc:
            self.target_content += start_str(tag, attrs)
        if tag == 'mistake' and attrs[0][1] == '1' and attrs[2][1] == '1':
            self.value_edit = True
        if (not self.in_text) and self.in_target_doc and self.value_edit:
            self.target_content += start_str(tag, attrs)

    def handle_endtag(self, tag):
        if (not self.in_text) and self.in_target_doc and self.value_edit:
            self.target_content += end_str(tag)
        if tag == 'annotation' and self.in_target_doc:
            self.target_content += end_str(tag)
        if tag == 'text':
            self.in_text = False
        if tag == 'p':
            self.first_p = False
        if tag == 'doc':
            if self.in_target_doc:
                self.target_content += "\n\n"
            self.in_target_doc = False
        if tag == 'mistake':
            self.value_edit = False

    def handle_data(self, data):
        if self.in_text and self.p_count == 1 and self.in_target_doc:
            self.target_content += data
        elif (not self.in_text) and self.in_target_doc and self.value_edit:
            self.target_content += data


if __name__ == '__main__':
    target_nid = '45'
    doc_filter = DocParser(target_nid)
    for i in range(1, 11):
        text = file('stage_0/A' + str(i) + '.sgml', "r").read()
        doc_filter.feed(text)
    target_content = doc_filter.target_content
    output = file('stage_1/' + target_nid + ".txt", "w")
    output.write(target_content)
