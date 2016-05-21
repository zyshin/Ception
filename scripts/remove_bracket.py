from ception.articles.models import ArticleVersion


def run():
    for v in ArticleVersion.objects.all():
        v.content = v.content.replace('class=\"current\"', '').replace('class="previous"', '')
        v.save()
