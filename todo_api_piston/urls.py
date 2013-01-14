from django.conf.urls import patterns, url
from piston.resource import Resource

from .handlers import TodoItemHandler


todoitem_handler = Resource(TodoItemHandler)

urlpatterns = patterns('',
   url(r'^(?P<id>\d+)$', todoitem_handler),
   url(r'^$', todoitem_handler),
)
