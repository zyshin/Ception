# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):
    def forwards(self, orm):
        # Adding model 'Article'
        db.create_table(u'articles_article', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=255, null=True, blank=True)),
            ('content', self.gf('django.db.models.fields.TextField')(max_length=60000)),
            ('description', self.gf('django.db.models.fields.TextField')(max_length=5000)),
            ('status', self.gf('django.db.models.fields.CharField')(default='D', max_length=1)),
            ('create_user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('create_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('update_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('update_user',
             self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='+', null=True,
                                                                   to=orm['auth.User'])),
        ))
        db.send_create_signal(u'articles', ['Article'])

        # Adding model 'ArticleVersion'
        db.create_table(u'articles_articleversion', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('origin', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['articles.Article'])),
            ('content', self.gf('django.db.models.fields.TextField')(max_length=60000)),
            ('edit_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('edit_user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=255, null=True, blank=True)),
        ))
        db.send_create_signal(u'articles', ['ArticleVersion'])

        # Adding model 'Tag'
        db.create_table(u'articles_tag', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('tag', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('article', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['articles.Article'])),
        ))
        db.send_create_signal(u'articles', ['Tag'])

        # Adding unique constraint on 'Tag', fields ['tag', 'article']
        db.create_unique(u'articles_tag', ['tag', 'article_id'])

        # Adding index on 'Tag', fields ['tag', 'article']
        db.create_index(u'articles_tag', ['tag', 'article_id'])

        # Adding model 'ArticleSentenceComment'
        db.create_table(u'articles_articlesentencecomment', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['articles.ArticleVersion'])),
            ('sentence_id', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('comment', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
        ))
        db.send_create_signal(u'articles', ['ArticleSentenceComment'])

        # Adding model 'ArticleComment'
        db.create_table(u'articles_articlecomment', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('article', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['articles.Article'])),
            ('comment', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
        ))
        db.send_create_signal(u'articles', ['ArticleComment'])

    def backwards(self, orm):
        # Removing index on 'Tag', fields ['tag', 'article']
        db.delete_index(u'articles_tag', ['tag', 'article_id'])

        # Removing unique constraint on 'Tag', fields ['tag', 'article']
        db.delete_unique(u'articles_tag', ['tag', 'article_id'])

        # Deleting model 'Article'
        db.delete_table(u'articles_article')

        # Deleting model 'ArticleVersion'
        db.delete_table(u'articles_articleversion')

        # Deleting model 'Tag'
        db.delete_table(u'articles_tag')

        # Deleting model 'ArticleSentenceComment'
        db.delete_table(u'articles_articlesentencecomment')

        # Deleting model 'ArticleComment'
        db.delete_table(u'articles_articlecomment')

    models = {
        u'articles.article': {
            'Meta': {'ordering': "('-create_date',)", 'object_name': 'Article'},
            'content': ('django.db.models.fields.TextField', [], {'max_length': '60000'}),
            'create_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'create_user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'description': ('django.db.models.fields.TextField', [], {'max_length': '5000'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'D'", 'max_length': '1'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'update_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'update_user': ('django.db.models.fields.related.ForeignKey', [],
                            {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': u"orm['auth.User']"})
        },
        u'articles.articlecomment': {
            'Meta': {'ordering': "('-date',)", 'object_name': 'ArticleComment'},
            'article': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['articles.Article']"}),
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'articles.articlesentencecomment': {
            'Meta': {'ordering': "('-date',)", 'object_name': 'ArticleSentenceComment'},
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['articles.ArticleVersion']"}),
            'sentence_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'articles.articleversion': {
            'Meta': {'ordering': "('-edit_date',)", 'object_name': 'ArticleVersion'},
            'content': ('django.db.models.fields.TextField', [], {'max_length': '60000'}),
            'edit_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'edit_user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'origin': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['articles.Article']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        u'articles.tag': {
            'Meta': {'unique_together': "(('tag', 'article'),)", 'object_name': 'Tag',
                     'index_together': "[['tag', 'article']]"},
            'article': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['articles.Article']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'tag': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [],
                            {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')",
                     'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': (
            'django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [],
                       {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True',
                        'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [],
                                 {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True',
                                  'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)",
                     'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['articles']
