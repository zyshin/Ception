# -*- coding: utf-8 -*-
from south.db import db
from south.v2 import SchemaMigration


class Migration(SchemaMigration):
    def forwards(self, orm):
        # Adding model 'ArticleSentenceSummary'
        db.create_table(u'articles_articlesentencesummary', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('article', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['articles.Article'])),
            ('sid', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('content', self.gf('django.db.models.fields.TextField')(max_length=60000)),
        ))
        db.send_create_signal(u'articles', ['ArticleSentenceSummary'])

        # Adding field 'ArticleVersion.info_array_json'
        db.add_column(u'articles_articleversion', 'info_array_json',
                      self.gf('django.db.models.fields.TextField')(max_length=100000, null=True),
                      keep_default=False)

        # Changing field 'ArticleVersion.diff_content'
        db.alter_column(u'articles_articleversion', 'diff_content',
                        self.gf('django.db.models.fields.TextField')(default='', max_length=60000))

    def backwards(self, orm):
        # Deleting model 'ArticleSentenceSummary'
        db.delete_table(u'articles_articlesentencesummary')

        # Deleting field 'ArticleVersion.info_array_json'
        db.delete_column(u'articles_articleversion', 'info_array_json')

        # Changing field 'ArticleVersion.diff_content'
        db.alter_column(u'articles_articleversion', 'diff_content',
                        self.gf('django.db.models.fields.TextField')(max_length=60000, null=True))

    models = {
        u'articles.article': {
            'Meta': {'ordering': "('-create_date',)", 'object_name': 'Article'},
            'content': ('django.db.models.fields.TextField', [], {'max_length': '60000'}),
            'create_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'create_user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'description': ('django.db.models.fields.TextField', [], {'max_length': '5000'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sentence_count': ('django.db.models.fields.IntegerField', [], {'default': '-1'}),
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
        u'articles.articlesentencesummary': {
            'Meta': {'object_name': 'ArticleSentenceSummary'},
            'article': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['articles.Article']"}),
            'content': ('django.db.models.fields.TextField', [], {'max_length': '60000'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sid': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        u'articles.articleversion': {
            'Meta': {'ordering': "('-edit_date',)", 'object_name': 'ArticleVersion'},
            'content': ('django.db.models.fields.TextField', [], {'max_length': '60000'}),
            'diff_content': ('django.db.models.fields.TextField', [], {'max_length': '60000'}),
            'edit_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'edit_user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'info_array_json': ('django.db.models.fields.TextField', [], {'max_length': '100000', 'null': 'True'}),
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
