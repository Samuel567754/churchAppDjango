from django.urls import path
from . import views as contact_views 
from .views import subscribe_newsletter, unsubscribe_newsletter, send_newsletter



app_name = 'contact'

urlpatterns = [
    path('contact/', contact_views.contact, name='contact'),
    path("subscribe/", subscribe_newsletter, name="subscribe_newsletter"),
    path("unsubscribe/", unsubscribe_newsletter, name="unsubscribe_newsletter"),
    path("send-newsletter/<int:newsletter_id>/", send_newsletter, name="send_newsletter"),
    path('dashboard/notifications/', contact_views.member_dashboard_notifications, name='member_dashboard_notifications'),
    path('dashboard/notifications/delete/<int:pk>/', contact_views.notification_delete, name='notification_delete'),
    path('dashboard/notifications/<int:notification_id>/', contact_views.notification_detail, name='detail'),
    path('dashboard/notifications/mark-all-read/', contact_views.mark_all_read, name='mark_all_read'),
    path('dashboard/notifications/mark-as-read/<int:notification_id>/', contact_views.mark_as_read, name="mark_as_read"),
]