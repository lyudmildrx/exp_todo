from django.conf.urls import patterns, url
from piston.resource import Resource
from todo.handlers import TodoItemHandler

todoitem_handler = Resource(TodoItemHandler)

urlpatterns = patterns('',
   url(r'^todo/(?P<id>\d+)$', todoitem_handler),
   url(r'^todo/$', todoitem_handler),
)
