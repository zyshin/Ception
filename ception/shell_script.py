from ception.articles.models import Article, Tag, ArticleComment, ArticleVersion, ArticleSentenceComment

all_articles = Article.objects.all()
for a in all_articles:
    a.content = a.content.replace("id=\"s", "sid=\"")
    a.save()
