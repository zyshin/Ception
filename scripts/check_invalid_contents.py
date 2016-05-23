import json
from django.contrib.auth.models import User
from ception.articles.models import Article, ArticleVersion

def run():
    for self in Article.objects.all():
        for user in User.objects.all():
            version_set = ArticleVersion.get_versions(self, user).exclude(edit_user=user)
            origin_sentences = self.get_sentences()
            version_info_array = []
            for v in version_set:
                # version_info_array.append(json.loads(v.info_array_json))
                try:
                    version_info_array.append(json.loads(v.info_array_json))
                except:
                    version_info_array.append([{'single': '', 'edited': ''}] * (self.sentence_count + 1))
            for i in version_info_array:
                for j in i[1:]:
                    if type(j) is dict and '\b' in j.get('sentence', ''):
                        print self, user
