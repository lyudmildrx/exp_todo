
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic.simple import direct_to_template

admin.autodiscover()

urlpatterns = patterns('',
    # Admin interface setup
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),

    # Delivery of the static client
    url(r'^$', direct_to_template,
        {'template': 'todo_client/index.html'}, name='client'),

    # REST API endpoints
    url(r'^rest/todo/', include('todo_api_piston.urls')),
    url(r'^rest-empty/todo/', include('todo_api.urls')),
)
