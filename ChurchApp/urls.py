from django.contrib import admin
from django.urls import path, include
# from django.conf.urls import url

from django.conf import settings
from django.conf.urls.static import static
import os
from django.contrib.auth import views as auth_views

from django.conf.urls import handler404, handler500
from django.views.generic import TemplateView
# from settings.views import ServiceWorkerView  # Adjust 'your_app' to your actual app name

handler404 = 'settings.views.custom_404'
handler500 = 'settings.views.custom_500'

urlpatterns = [
    # path('admin/defender/', include('defender.urls')),
    # path('admin/', admin.site.urls),
    path('kumasi-central-kccofcoc-admin/', admin.site.urls),
    path('settings/', include('settings.urls', namespace='settings')), 
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
    # path('service-worker.js', ServiceWorkerView.as_view(), name='service-worker'),
    path("offline/", TemplateView.as_view(template_name="offline.html"), name="offline"),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


