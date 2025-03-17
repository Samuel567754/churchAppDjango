from django.urls import path
from . import views
from django.contrib.auth.views import LoginView, LogoutView
from .views import member_login, member_logout, member_register
from django.contrib.auth import views as auth_views
from .views import CustomPasswordResetView, CustomPasswordResetConfirmView
from .forms import CustomPasswordResetForm
from .views import check_username


app_name = 'account'

urlpatterns = [
    path('dashboard/profile/', views.member_dashboard_profile, name='member_dashboard_profile'),
    path('dashboard/profile/edit/', views.edit_profile, name='edit_profile'),
   
    path('api/check-username/', check_username, name='check_username'),
   
    path('member-action/<str:token>/', views.member_action, name='member-action'),
   
    path('dashboard/profile/change-password/', views.change_password, name='change_password'),
    path('login/', member_login, name='login'),
    path('logout/', member_logout, name='logout'),
    path('register/', member_register, name='register'),
    path('logout/', LogoutView.as_view(next_page='account:login'), name='logout'),
     # Password Reset
    path(
        'password-reset/',
        CustomPasswordResetView.as_view(
            form_class=CustomPasswordResetForm, 
            template_name='account/registration/password_reset.html',  # Form page template
            email_template_name='account/emails/password_reset_email.html',  # Custom email template
            subject_template_name='account/emails/password_reset_subject.txt'  # Optional custom subject
        ),
        name='password_reset'
    ),
    path(
        'password-reset/done/',
        auth_views.PasswordResetDoneView.as_view(template_name='account/registration/password_reset_done.html'),
        name='password_reset_done'
    ),
    # path(
    #     'password-reset-confirm/<uidb64>/<token>/',
    #     auth_views.PasswordResetConfirmView.as_view(template_name='membership/registration/password_reset_confirm.html'),
    #     name='password_reset_confirm'
    # ),
     path(
        'password-reset-confirm/<uidb64>/<token>/',
        CustomPasswordResetConfirmView.as_view(template_name='account/registration/password_reset_confirm.html'),  # Use your custom view
        name='password_reset_confirm'
    ),
    path(
        'password-reset-complete/',
        auth_views.PasswordResetCompleteView.as_view(template_name='account/registration/password_reset_complete.html'),
        name='password_reset_complete'
    ),
    
]