from django.conf.urls import patterns, url


urlpatterns = patterns('todo_api.views',
   url(r'^(?P<method>\w+)/(?P<id>\d+)/(?P<fmt>\w+)/$', 'handle_rest_call'),
   url(r'^(?P<method>\w+)/(?P<fmt>\w+)/$', 'handle_rest_call'),
#   url(r'^$', 'handle_rest_call'),
)
