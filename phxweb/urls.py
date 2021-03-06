from django.conf.urls import include, url
from django.contrib import admin
from django.contrib import auth
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponseRedirect
from accounts.views import home
from django.views.static import serve
from django.conf.urls.static import static

urlpatterns = [
    # Examples:
    # url(r'^$', 'phxweb.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^home$', home),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/', include('accounts.urls')),
    url(r'^', include('monitor.urls')),
    url(r'^monitor/', include('monitor.urls')),
    url(r'^dns/', include('dns.urls')),
    url(r'^detect/', include('detect.urls')),
    url(r'^message/', include('detect.urls')),
    url(r'^saltstack/', include('saltstack.urls')),
    url(r'^servers/', include('servers.urls')),
    url(r'^upgrade/', include('upgrade.urls')),

    url(r'^favicon$', lambda x: HttpResponseRedirect(settings.STATIC_URL+'images/favicon.ico')),
    url(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
