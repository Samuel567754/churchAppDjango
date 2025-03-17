from django.urls import path
from . import views


app_name = 'blog'


urlpatterns = [
    path('post/home', views.post_list, name='post_list'),  # Blog homepage
    path('post/<slug:slug>/', views.post_detail, name='post_detail'),  # Post detail page
    path('category/<slug:slug>/', views.posts_by_category, name='posts_by_category'),  # Filter by category
    path('tag/<slug:slug>/', views.posts_by_tag, name='posts_by_tag'),  # Filter by tag
]
