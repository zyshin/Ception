from django.conf.urls import patterns, include, url
urlpatterns = patterns('ception.articles.views',
                       url(r'^$', 'articles', name='articles'),
                       url(r'^write/$', 'write', name='write'),
                       url(r'^preview/$', 'preview', name='preview'),
                       url(r'^drafts/$', 'drafts', name='drafts'),
                       url(r'^comment/$', 'comment', name='comment'),
                       url(r'^sentence_comment/$', 'sentence_comment', name='sentence_comment'),
                       url(r'^sentence_return/$', 'sentence_return', name='sentence_return'),
                       url(r'^sentence_vote/$', 'sentence_vote', name='sentence_vote'),
                       url(r'^tag/(?P<tag_name>.+)/$', 'tag', name='tag'),
                       url(r'^edit/(?P<id>\d+)/$', 'edit', name='edit_article'),
                       url(r'^edit_v/(?P<id>\d+)/$', 'edit_version', name='edit_version'),
                       url(r'^(?P<slug>[-\w]+)/$', 'article', name='article'),
                       )

