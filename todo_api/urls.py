from django.conf.urls import patterns, url


urlpatterns = patterns('todo_api.views',
   url(r'^(?P<id>\d+)$', 'handle_rest_call'),
   url(r'^$', 'handle_rest_call'),
)
