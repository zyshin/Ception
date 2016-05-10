from ception.articles.models import Article, ArticleVersion


def run():
    article_all = Article.objects.all()
    version_all = ArticleVersion.objects.all()
    article_array = []
    for a in Article.objects.all():
        version_array = []
        for v in ArticleVersion.objects.filter(origin=a):
            v.save()
