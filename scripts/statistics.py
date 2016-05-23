from ception.articles.models import Article, ArticleVersion
from ception.articles.utils import stadardlize_text
from ception.articles.simple_parser import SimpleParser, CleanParser
import json

def count_word(content):
    clean_text = CleanParser.get_clean_text(content)
    no_punc_text= clean_text.replace(',', ' ').replace('.', ' ')
    return len(no_punc_text.split())


def run():
    infos = {}
    for article in Article.objects.all():
        article_info = {}
        origin_info = {}
        origin_info['title'] = article.title
        origin_info['content'] = article.content
        origin_info['word_count'] = count_word(article.content)
        origin_info['sentence_count'] = article.sentence_count
        origin_info['id'] = article.pk
        origin_info['editor'] = "origin"
        article_info["origin"] = origin_info

        for version in ArticleVersion.objects.filter(origin=article):
            version_info = {}
            version_info['content'] = version.content
            version_info['info'] = version.info_array_json
            version_info['word_count'] = count_word(version.content)
            version_info['user'] = version.edit_user.username
            version_info['diff_content'] = version.diff_content
            article_info[version.edit_user.username] = version_info
        infos[article.pk] = article_info
    file("scripts/statistics/info.json", "w").write(json.dumps(infos))
