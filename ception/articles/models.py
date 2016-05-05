from datetime import datetime

import markdown
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q
from django.template.defaultfilters import slugify
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

from ception.activities.models import Activity
from ception.articles.diff_parser import DiffParser
from ception.articles.simple_parser import SimpleParser


class Article(models.Model):
    DRAFT = 'D'
    PUBLISHED = 'P'
    STATUS = (
        (DRAFT, 'Draft'),
        (PUBLISHED, 'Published'),
    )
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, null=True, blank=True)
    content = models.TextField(max_length=60000)
    description = models.TextField(max_length=5000)
    status = models.CharField(max_length=1, choices=STATUS, default=DRAFT)
    sentence_count = models.IntegerField(default=-1)

    create_user = models.ForeignKey(User)
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(blank=True, null=True)
    update_user = models.ForeignKey(User, null=True, blank=True, related_name="+")

    class Meta:
        verbose_name = _("Article")
        verbose_name_plural = _("Articles")
        ordering = ("-create_date",)

    def __unicode__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.pk:
            super(Article, self).save(*args, **kwargs)
        else:
            self.update_date = datetime.now()
        if not self.slug:
            slug_str = "%s %s" % (self.pk, self.title.lower())
            self.slug = slugify(slug_str)
        super(Article, self).save(*args, **kwargs)

    def get_content_as_markdown(self):
        return markdown.markdown(self.content, safe_mode='escape')

    @staticmethod
    def get_published():
        articles = Article.objects.filter(status=Article.PUBLISHED)
        return articles

    def create_tags(self, tags):
        tags = tags.strip()
        tag_list = tags.split(' ')
        for tag in tag_list:
            if tag:
                t, created = Tag.objects.get_or_create(tag=tag.lower(), article=self)

    def get_tags(self):
        return Tag.objects.filter(article=self)

    def get_summary(self):
        if len(self.content) > 255:
            return u'{0}...'.format(self.content[:255])
        else:
            return self.content

    def get_summary_as_markdown(self):
        return markdown.markdown(self.get_summary(), safe_mode='escape')

    def get_comments(self):
        return ArticleComment.objects.filter(article=self)

    def get_sentences(self):
        parser = SimpleParser()
        parser.feed(self.content)
        return parser.sentence_array

    def get_or_create_version_by_user(self, user):
        version_set = ArticleVersion.objects.filter(edit_user=user, origin=self)
        if len(version_set) == 0:
            version = ArticleVersion()
            version.edit_user = user
            version.content = self.content
            version.origin = self
            version.save()
        else:
            version = version_set[0]
        return version

    def compute_summary(self):
        pass


class ArticleVersion(models.Model):
    origin = models.ForeignKey(Article)
    content = models.TextField(max_length=60000)
    edit_date = models.DateTimeField(auto_now_add=True)
    edit_user = models.ForeignKey(User)
    slug = models.SlugField(max_length=255, null=True, blank=True)

    class Meta:
        verbose_name = _("Version")
        verbose_name_plural = _("Versions")
        ordering = ("-edit_date",)

    def __unicode__(self):
        return self.origin.title + " Edited by " + self.edit_user.username

    def save(self, *args, **kwargs):
        if not self.pk:
            super(ArticleVersion, self).save(*args, **kwargs)
        else:
            self.edit_date = datetime.now()
        if not self.slug:
            slug_str = "%s %s Edited" % (self.pk, self.origin.title.lower())
            self.slug = slugify(slug_str)

        self.prepocess()
        print "Saved:", self.__unicode__()

        super(ArticleVersion, self).save(*args, **kwargs)

    def get_votes(self, sentence_id):
        up_votes = Activity.objects.filter(activity_type=Activity.UP_VOTE, version_id=self.pk,
                                           sentence_id=sentence_id).count()
        down_votes = Activity.objects.filter(activity_type=Activity.DOWN_VOTE, version_id=self.pk,
                                             sentence_id=sentence_id).count()
        return up_votes - down_votes

    def prepocess(self):
        sp = SimpleParser()
        sp.feed(self.origin.content)
        parser = DiffParser(sp.sentence_array)
        parser.feed(self.content)
        self.diff_content = parser.diff_content

    def get_sentence_comments(self):
        sentence_comments_array = [{'html': u'Error', 'count': -1}]
        for i in range(1, self.origin.sentence_count + 1):
            comment_dict = {
                'html': u'',
                'count': 0
            }
            for comment in ArticleSentenceComment.objects.filter(parent=self, sentence_id=i):
                comment_dict['html'] += render_to_string('articles/partial_sentence_comment.html', {'comment': comment})
                comment_dict['count'] += 1
            sentence_comments_array.append(comment_dict)
        return sentence_comments_array

    def get_sentence_vote(self, user):
        sentence_comment_array = [{'count': 0, 'state': "N"}]
        for i in range(1, self.origin.sentence_count + 1):
            activity = Activity.objects.filter(Q(activity_type=Activity.UP_VOTE) | Q(activity_type=Activity.DOWN_VOTE),
                                               user=user, sentence_id=i, version_id=self.pk)
            user_state = "N"
            if activity:
                user_state = activity.first().activity_type
            sentence_comment_array.append({'count': self.get_votes(i), 'state': user_state})
        return sentence_comment_array


    @staticmethod
    def get_versions(article):
        versions = ArticleVersion.objects.filter(origin=article)
        return versions

        # def get_comments(self):
    #     return ArticleComment.objects.filter(article=self)


class Tag(models.Model):
    tag = models.CharField(max_length=50)
    article = models.ForeignKey(Article)

    class Meta:
        verbose_name = _('Tag')
        verbose_name_plural = _('Tags')
        unique_together = (('tag', 'article'),)
        index_together = [['tag', 'article'],]

    def __unicode__(self):
        return self.tag

    @staticmethod
    def get_popular_tags():
        tags = Tag.objects.all()
        count = {}
        for tag in tags:
            if tag.article.status == Article.PUBLISHED:
                if tag.tag in count:
                    count[tag.tag] = count[tag.tag] + 1
                else:
                    count[tag.tag] = 1
        sorted_count = sorted(count.items(), key=lambda t: t[1], reverse=True)
        return sorted_count[:20]


class ArticleSentenceComment(models.Model):
    parent = models.ForeignKey(ArticleVersion)
    sentence_id = models.IntegerField(null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    comment = models.CharField(max_length=500, blank=False, null=False)
    user = models.ForeignKey(User)

    class Meta:
        verbose_name = _("Article Sentence Comment")
        verbose_name_plural = _("Article Sentence Comments")
        ordering = ("-date",)

    def __unicode__(self):
        return u'{0} - "{1}" - "{2}"'.format(self.user.username, self.parent, self.sentence_id)


class ArticleComment(models.Model):
    article = models.ForeignKey(Article)
    comment = models.CharField(max_length=500)
    date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User)

    class Meta:
        verbose_name = _("Article Comment")
        verbose_name_plural = _("Article Comments")
        ordering = ("-date",)

    def __unicode__(self):
        return u'{0} - {1}'.format(self.user.username, self.article.title)


class ArticleSentenceSummary(models.Model):
    article = models.ForeignKey(Article)
    sid = models.IntegerField(null=True, blank=True)
    content = models.TextField(max_length=60000)

    class Meta:
        verbose_name = _("Article Sentence Summary")
        verbose_name_plural = _("Article Sentence Summarys")

    def __unicode__(self):
        return u'{0} - {1}'.format(self.article.title, self.sid)


class VersionSentenceInfoDict(models.Model):
    version = models.ForeignKey(ArticleVersion)
    sid = models.IntegerField(null=True, blank=True)
    content = models.TextField(max_length=60000)
