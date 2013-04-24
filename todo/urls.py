from django.conf.urls import patterns, include, url
from django.views.generic import DetailView, ListView
from todo.models import TodoItem

urlpatterns = patterns('',
    url('^$',
        ListView.as_view(
            queryset=TodoItem.objects.all().order_by('-order'),
            context_object_name='todos',
            template_name='todo/index.html'),
        name='index'),
    url(r'^(?P<pk>\d+)/$',
        DetailView.as_view(
            model=TodoItem,
            template_name='todo/detail.html'),
        name='detail'),
    url(r'^(?P<todoitem_id>\d+)/update/$', 'todo.views.update', name='update'),
    url(r'^/create/$', 'todo.views.create', name='create'),
    url(r'^(?P<todoitem_id>\d+)/delete/$', 'todo.views.delete', name='delete'),
    url(r'^(?P<todoitem_id>\d+)/do/$', 'todo.views.do', name='do'),
)
