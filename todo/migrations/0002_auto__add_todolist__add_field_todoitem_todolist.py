# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'TodoList'
        db.create_table(u'todo_todolist', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.TextField')()),
            ('description', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'todo', ['TodoList'])

        # Adding field 'TodoItem.todolist'
        db.add_column(u'todo_todoitem', 'todolist',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=0, to=orm['todo.TodoList']),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting model 'TodoList'
        db.delete_table(u'todo_todolist')

        # Deleting field 'TodoItem.todolist'
        db.delete_column(u'todo_todoitem', 'todolist_id')


    models = {
        u'todo.todoitem': {
            'Meta': {'object_name': 'TodoItem'},
            'done': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.TextField', [], {}),
            'todolist': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['todo.TodoList']"})
        },
        u'todo.todolist': {
            'Meta': {'object_name': 'TodoList'},
            'description': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.TextField', [], {})
        }
    }

    complete_apps = ['todo']