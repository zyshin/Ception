from django.conf.urls import patterns, include, url


urlpatterns = patterns('ception.articles.views',
                       url(r'^$', 'articles', name='articles'),
                       url(r'^write/$', 'write', name='write'),
                       url(r'^preview/$', 'preview', name='preview'),
                       url(r'^drafts/$', 'drafts', name='drafts'),
                       url(r'^comment/$', 'comment', name='comment'),
                       url(r'^sentence_comments/$', 'sentence_comments', name='sentence_comments'),
                       url(r'^sentence_vote/$', 'sentence_vote', name='sentence_vote'),
                       url(r'^tag/(?P<tag_name>.+)/$', 'tag', name='tag'),
                       url(r'^edit/(?P<id>\d+)/$', 'edit', name='edit'),
                       url(r'^edit_compare/(?P<id>\d+)/$', 'edit_compare', name='edit_compare'),
                       url(r'^diff/$', 'diff_test', name='diff_test'),
                       url(r'^cherry_pick_api/$', 'cherry_pick_api', name='cherry_pick_api'),
                       # url(r'^(?P<slug>[-\w]+)/$', 'article', name='article'),
                       )

