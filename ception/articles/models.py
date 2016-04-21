from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from datetime import datetime
from django.template.defaultfilters import slugify
from ception.activities.models import Activity
import markdown
import diff_match_patch as dmp_module


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


class ArticleVersion(models.Model):
    origin = models.ForeignKey(Article)
    content = models.TextField(max_length=60000)
    edit_date = models.DateTimeField(auto_now_add=True)
    edit_user = models.ForeignKey(User)
    slug = models.SlugField(max_length=255, null=True, blank=True)
    dmp = dmp_module.diff_match_patch()

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
        super(ArticleVersion, self).save(*args, **kwargs)

    def get_votes(self, sentence_id):
        up_votes = Activity.objects.filter(activity_type=Activity.UP_VOTE, version_id=self.pk,
                                           sentence_id=sentence_id).count()
        down_votes = Activity.objects.filter(activity_type=Activity.DOWN_VOTE, version_id=self.pk,
                                             sentence_id=sentence_id).count()
        return up_votes - down_votes

    @classmethod
    def diff(cls, s1, s2):
        d = cls.dmp.diff_main(s1, s2)
        cls.dmp.diff_cleanupSemantic(d)
        return cls.dmp.diff_html(d)

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