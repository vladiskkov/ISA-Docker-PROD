from django.contrib import admin
from django.urls import path, include, re_path
from main.views import staff_required
from django.conf.urls.i18n import i18n_patterns
from django.conf import settings

admin.autodiscover()

admin.site.login = staff_required(admin.site.login)

urlpatterns = [
    #path('', include('main.urls')),
    path('admin/', admin.site.urls, name='admin'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('oauth2/', include('django_auth_adfs.urls')),
]

urlpatterns += i18n_patterns(path('', include('main.urls')))

if 'rosetta' in settings.INSTALLED_APPS:
    urlpatterns += [
        re_path(r'^rosetta/', include('rosetta.urls'))
    ]
