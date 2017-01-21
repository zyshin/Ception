from django.conf.urls import patterns, include, url
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin


admin.autodiscover()

urlpatterns = patterns('',
                       url(r'^admin/', include(admin.site.urls)),
                       url(r'^$', 'ception.core.views.home', name='home'),
                       url(r'^login', 'django.contrib.auth.views.login', {'template_name': 'core/cover.html'}, name='login'),
                       url(r'^logout', 'django.contrib.auth.views.logout', {'next_page': '/'}, name='logout'),
                       url(r'^signup/$', 'ception.auth.views.signup', name='signup'),
                       url(r'^settings/$', 'ception.core.views.settings', name='settings'),
                       url(r'^settings/picture/$', 'ception.core.views.picture', name='picture'),
                       url(r'^settings/upload_picture/$', 'ception.core.views.upload_picture', name='upload_picture'),
                       url(r'^settings/save_uploaded_picture/$', 'ception.core.views.save_uploaded_picture', name='save_uploaded_picture'),
                       url(r'^settings/password/$', 'ception.core.views.password', name='password'),
                       url(r'^network/$', 'ception.core.views.network', name='network'),
                       url(r'^feeds/', include('ception.feeds.urls')),
                       url(r'^questions/', include('ception.questions.urls')),
                       url(r'^articles/', include('ception.articles.urls')),
                       url(r'^messages/', include('ception.messages.urls')),
                       url(r'^notifications/$', 'ception.activities.views.notifications', name='notifications'),
                       url(r'^notifications/last/$', 'ception.activities.views.last_notifications', name='last_notifications'),
                       url(r'^notifications/check/$', 'ception.activities.views.check_notifications', name='check_notifications'),
                       url(r'^search/$', 'ception.search.views.search', name='search'),
                       url(r'^profile/(?P<username>[^/]*)/$', 'ception.core.views.profile', name='profile'),
                       url(r'^i18n/', include('django.conf.urls.i18n', namespace='i18n')),
                       )# + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
