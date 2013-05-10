from django.conf.urls import patterns, include, url
from django.views.generic import DetailView, ListView
from django.views.generic import TemplateView
from todo.models import TodoItem, TodoList
from todo.api import TodoListResource, UserResource
from tastypie.api import Api, NamespacedApi

v1_api = NamespacedApi(api_name='v1', urlconf_namespace='tastypie_api')
v1_api.register(UserResource())
v1_api.register(TodoListResource())

urlpatterns = patterns('',
    url(r'^$', 'todo.views.list_index', name='list_index'),
    url(r'^create/$', 'todo.views.list_create', name='list_create'),
    url(r'^delete/(?P<todolist_id>\d+)/$', 'todo.views.list_delete', name='list_delete'),
    url(r'^share/(?P<todolist_id>\d+)/$', 'todo.views.list_share', name='list_share'),
    url(r'^(?P<todolist_id>\d+)/items/$', 'todo.views.item_index', name='item_index'),
    url(r'^items/(?P<pk>\d+)/$',
        DetailView.as_view(
            model=TodoItem,
            template_name='todo/item_detail.html'),
        name='item_detail'),
    url(r'^(?P<todolist_id>\d+)/items/create/$', 'todo.views.item_create', name='item_create'),
    url(r'^items/(?P<todoitem_id>\d+)/update/$', 'todo.views.item_update', name='item_update'),
    url(r'^items/(?P<todoitem_id>\d+)/delete/$', 'todo.views.item_delete', name='item_delete'),
    url(r'^items/(?P<todoitem_id>\d+)/do/$', 'todo.views.item_do', name='item_do'),
    url(r'^denied$', TemplateView.as_view(template_name='todo/permitions_denied.html'), name='permitions_denied'),
    url(r'^api_tastypie/', include(v1_api.urls, namespace='tastypie_api')),
)
