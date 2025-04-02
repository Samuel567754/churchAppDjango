from django.contrib import admin
from django.urls import path, include
# from django.conf.urls import url

from django.conf import settings
from django.conf.urls.static import static
import os
from django.contrib.auth import views as auth_views


urlpatterns = [
    # path('admin/defender/', include('defender.urls')),
    path('admin/', admin.site.urls),
    path('settigs/', include('settings.urls', namespace='settings')), 
    path('ckeditor5/', include('django_ckeditor_5.urls')),  # Add this line
    path('', include('community.urls')), 
    path('blog/', include('blog.urls')),
    path('worship/', include('worship.urls', namespace="worship")), 
    path('contact/', include('contact.urls',namespace="contact")),
    # path('event/', include('event.urls')),
    # path('finance/', include('finance.urls')),
    path('account/', include('account.urls', namespace='account')),
    path('membership/', include('membership.urls', namespace='membership')),
    path('', include('pwa.urls')),  # This will serve the manifest and service worker files. 
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


