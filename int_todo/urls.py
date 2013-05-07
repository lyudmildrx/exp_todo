from django.conf.urls import patterns, include, url
from django.contrib import admin

# To support Django <= 1.2 and >= 1.3
# Try to import TemplateView (and use it if we can) and if not, fall back to direct_to_template.
try:
    from django.views.generic import TemplateView
    static_client = url(r'^$', TemplateView.as_view(template_name='todo_client/index.html'), name='client')
except ImportError:
    from django.views.generic.simple import direct_to_template
    static_client = url(r'^$', direct_to_template, {'template': 'todo_client/index.html'}, name='client'),

admin.autodiscover()

urlpatterns = patterns('',
    # Admin interface setup
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),

    # Delivery of the static client
    static_client,

    url(r'^todo/lists/', include('todo.urls', namespace='todo')),

    # REST API endpoints
    url(r'^rest/todo/', include('todo_api_piston.urls')),
    url(r'^rest-empty/todo/', include('todo_api.urls')),

    # User authentication
    url('^accounts/', include('django.contrib.auth.urls')),
)
