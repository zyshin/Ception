from django.contrib import admin
from .models import Article, ArticleVersion, Tag, ArticleSentenceComment, ArticleComment


admin.site.register(Article)
admin.site.register(ArticleVersion)
admin.site.register(Tag)
admin.site.register(ArticleSentenceComment)
admin.site.register(ArticleComment)
