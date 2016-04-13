from HTMLParser import HTMLParser
import types


NO_TAG = "Text"


def start_str(tag, attrs=None):
    if not attrs:
        attrs = {}
    if tag == NO_TAG:
        return ""
    attr_str = ""
    if type(attrs) == types.ListType:
        for attr in attrs:
            if not (tag == "ins" or tag == "del") or attr[0] != "class":
                attr_str += attr[0] + "=" + "\"" + attr[1] + "\" "
    elif type(attrs) == types.DictionaryType:
        for (key, value) in attrs.items():
            if not (tag == "ins" or tag == "del") or key[0] != "class":
                attr_str += key + "=" + "\"" + value + "\" "
    return "<" + tag + " " + attr_str + ">"


def end_str(tag):
    if tag == NO_TAG:
        return ""
    return "</" + tag + ">"


class PDAdder(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.counter = 0
        self.text = ""

    def handle_starttag(self, tag, attrs):
        if tag == "pd":
            self.counter += 1
            attrs.append(('sid', str(self.counter)))
        self.text += start_str(tag, attrs)

    def handle_endtag(self, tag):
        self.text += end_str(tag)

    def handle_data(self, data):
        self.text += data


def convert_period_to_pd (content):
    content = content.replace('.', '<pd>.</pd>').replace('?', '<pd>?</pd>').replace('!', '<pd>!</pd>')
    parser = PDAdder()
    parser.feed(content)
    return parser.text, parser.counter


def stadardlize_text(text):
    return text.replace("&nbsp;", " ").replace("&#39;", "'")


class ContentParser(HTMLParser):
    def __init__(self, max_sentence=50):
        HTMLParser.__init__(self)
        self.json = {
            'sentence': [],
            'counter': 0,
        }
        self.current_sentence = {
            'content': "",
            'id': -1
        }
        self.is_deleted = False
        self.inside_pd_deleted = False
        self.current_edited = False
        self.current_id = -1
        self.edit_count = [False for x in xrange(max_sentence)]
        self.delete_count = [False for x in range(max_sentence)]


    def handle_starttag(self, tag, attrs):
        if tag == "ins" or tag == "del":
            self.current_sentence["content"] += start_str(tag, {})
            self.current_edited = True
        if tag == "pd":
            if not self.is_deleted:
                for pair in attrs:
                    self.current_sentence[pair[0]] = pair[1]
                current_id = int(self.current_sentence["sid"])
                self.current_id = current_id
                self.current_sentence["sid"] = current_id
                if self.json["counter"] <= current_id:
                    self.json["counter"] = current_id + 1
                self.inside_pd_deleted = False
            else:
                if not self.current_sentence.has_key("deleted"):
                    self.current_sentence["deleted"] = []
                pd_dict = {}
                for pair in attrs:
                    pd_dict[pair[0]] = pair[1]
                pd_dict["sid"] = int(pd_dict["sid"])
                self.current_sentence["deleted"].push(pd_dict)
        elif tag == "del":
            self.is_deleted = True
            self.inside_pd_deleted = True


    def handle_endtag(self, tag):
        if tag == "ins" or tag == "del":
            self.current_sentence["content"] += end_str(tag)
        if tag == "pd":
            if not self.inside_pd_deleted:
                self.current_sentence["related"] = []
                # for s in self.current_sentence["deleted"]:
                # self.current_sentence["related"].push(s["sid"])
                # TODO: aaa
                self.edit_count[self.current_id] = self.current_edited
                self.json['sentence'].append(self.current_sentence)
                self.current_sentence = {
                    'content': "",
                    'id': -1
                }
            else:
                self.delete_count[self.current_id] = True
            self.current_edited = False
        elif tag == "del":
            self.is_deleted = False

    def handle_data(self, data):
        # if not self.is_deleted:
        self.current_sentence["content"] += data

    @staticmethod
    def get_info(content):
        parser = ContentParser()
        parser.feed(stadardlize_text(content))
        return parser.json, parser.edit_count, parser.delete_count
