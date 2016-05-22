from HTMLParser import HTMLParser

ContentDict = {
    '45': 'People that living in the modern world really cannot live without the social media sites like Twitter and Facebook. Almost all students and young adults possess the Facebook or Twitter account. It is true that social media makes people be able to connect one another more conveniently. However, it seems that, especially for some those, sharing some parts of their lives such as videos and photos on the social media sites become really necessary. An extremely interesting and ironic phenomenon was discovered that a group of friends met and sat around one table, but none of them were really chatting with one another. Instead, all of them were more interested in posting pictures of this "cheerful" meeting on their social media sites. Therefore, there is need to discuss the advantages and disadvantages of social media.',
    '46': 'As the development of the technology, social media becomes more and more significant role in the whole world. Everyone in the world cannot stop using it every day to express their feelings or ideas and a log of other stuff which helps their friends know their lives better. However, it also raised the concerns about whether it brings us more benefits or a human disaster. Although it helps to connect us with our friends wherever we are, it at the same time reduces the chance for us to talk to our friends face to face which may affect our interpersonal skills. Thus, whether there are more advantages or disadvantages becomes a tough question for every human being.'
}


class AnnotationParser(HTMLParser):
    def __init__(self, target):
        HTMLParser.__init__(self)
        self.edit_clean_list = []
        self.current_clean_sentence = ""
        self.current_index = 0
        self.edit_range = None
        self.mistake_type = ""
        self.in_type = False
        self.in_correction = False
        self.correction = ""
        self.origin = ContentDict[target]

    def handle_starttag(self, tag, attrs):
        if tag == 'mistake':
            self.edit_range = (int(attrs[1][1]), int(attrs[3][1]))
            self.mistake_type = ""
        if tag == 'type':
            self.in_type = True
        if tag == 'correction':
            self.in_correction = True

    def handle_endtag(self, tag):
        if tag == 'type':
            self.in_type = False
        if tag == 'correction':
            self.in_correction = False
        if tag == 'annotation':
            self.current_clean_sentence += self.origin[self.current_index:]
            self.edit_clean_list.append(self.current_clean_sentence)
            self.current_clean_sentence = ""
            self.current_index = 0
        if tag == 'mistake':
            self.current_clean_sentence += self.origin[self.current_index: self.edit_range[0]]
            self.current_clean_sentence += self.correction + "(" + self.mistake_type + ")"
            self.current_index = self.edit_range[1]

    def handle_data(self, data):
        if self.in_type:
            self.mistake_type = data
        if self.in_correction:
            self.correction = data


if __name__ == '__main__':
    target = "46"
    parser = AnnotationParser(target)
    parser.feed(file("stage_1/" + target + ".txt", "r").read())
    f = file("stage_3/" + target + ".txt", "w+")
    f.write(str(parser.edit_clean_list))
    # for text in parser.edit_clean_list:
    #     f.write(text + "\n")
