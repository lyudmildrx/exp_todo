from django.conf.urls import patterns, include, url
from django.views.generic import DetailView, ListView
from todo.models import TodoItem, TodoList
from django.views.generic import TemplateView


urlpatterns = patterns('',
#    url('^$',
#        ListView.as_view(
#            queryset=TodoList.objects.all().order_by('title'),
#            context_object_name='todolists',
#            template_name='todo/list_index.html'),
#        name='list_index'),
    url(r'^$', 'todo.views.list_index', name='list_index'),
    url(r'^/create/$', 'todo.views.list_create', name='list_create'),
    url(r'^/delete/(?P<todolist_id>\d+)$', 'todo.views.list_delete', name='list_delete'),
    url(r'^/share/(?P<todolist_id>\d+)/$', 'todo.views.list_share', name='list_share'),
    url(r'^/(?P<todolist_id>\d+)/items/$', 'todo.views.item_index', name='item_index'),
    url(r'^items/(?P<pk>\d+)/$',
        DetailView.as_view(
            model=TodoItem,
            template_name='todo/item_detail.html'),
        name='item_detail'),
    url(r'^(?P<todolist_id>\d+)/items/create/$', 'todo.views.item_create', name='item_create'),
    url(r'^/items/(?P<todoitem_id>\d+)/update/$', 'todo.views.item_update', name='item_update'),
    url(r'^/items/(?P<todoitem_id>\d+)/delete/$', 'todo.views.item_delete', name='item_delete'),
    url(r'^/items/(?P<todoitem_id>\d+)/do/$', 'todo.views.item_do', name='item_do'),
    url(r'^/denied$', TemplateView.as_view(template_name='todo/permitions_denied.html'), name='permittions_denied'),
)
