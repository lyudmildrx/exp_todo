
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic.simple import direct_to_template

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),

    url(r'^$', direct_to_template,
        {'template': 'todo_client/index.html'}, name='client'),

    url(r'^rest/todo/', include('todo_api_piston.urls')),
)
