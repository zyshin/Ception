import json
from HTMLParser import HTMLParser
from tools import count_word

TargetArticleList = ['3', '2']
AuthorList = ['yanyukang', 'fanlihua', 'SunKe', 'huangzirui', 'huyuan', 'liubin', 'zhangmeng', 'dunaixuan', 'macaicai', 'yaoyanan', 'lixiaoqing', 'hehaoqing']



class EditCountParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.ins_count = 0
        self.del_count = 0
        self.in_ins = False
        self.in_del = False

    def handle_starttag(self, tag, attrs):
        if tag == 'ins':
            self.in_ins = True
        if tag == 'del':
            self.in_del = True

    def handle_endtag(self, tag):
        if tag == 'ins':
            self.in_ins = False
        if tag == 'del':
            self.in_del = False

    def handle_data(self, data):
        if self.in_ins:
            self.ins_count += count_word(data)
        if self.in_del:
            self.del_count += count_word(data)


if __name__ == '__main__':
    info_dict = json.loads(file("info.json").read())
    for author in AuthorList:
        for article_id in TargetArticleList:
            parser = EditCountParser()
            parser.feed(info_dict[article_id][author]["diff_content"])
            print parser.ins_count, '\t', parser.del_count


