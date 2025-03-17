from django.contrib import admin
from .models import Category, Tag, Post, Comment, Like
from django.utils.html import format_html


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    date_hierarchy = 'created_at'
    
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'description')
        }),
    )


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    
    fieldsets = (
         (None, {
             'fields': ('name', 'slug')
        }),
    )


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at', 'is_published', 'featured', 'views_count', 'image_preview')
    list_filter = ('is_published', 'featured', 'categories', 'tags', 'author')
    search_fields = ('title', 'content', 'author__username', 'meta_description')
    filter_horizontal = ('categories', 'tags')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'created_at'

    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'author', 'content')
        }),
        ('Associations', {
            'fields': ('categories', 'tags')
        }),
        ('Publishing Options', {
            'fields': ('is_published', 'published_at', 'featured', 'meta_description', 'views_count')
        }),
        ('Featured Image', {
            'fields': ('featured_image', )
         }),
    )

    def image_preview(self, obj):
        if obj.featured_image:
            return format_html('<img src="{}" style="width: 50px; height: 50px; border-radius:4px;" />', obj.featured_image.url)
        return "No Image"

    image_preview.short_description = "Image Preview"


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'post', 'created_at', 'is_approved')
    list_filter = ('is_approved', 'created_at')
    search_fields = ('author__username', 'content', 'post__title')
    date_hierarchy = 'created_at'

    fieldsets = (
        (None, {
            'fields': ('post', 'author', 'content', 'is_approved')
        }),
    )


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'liked_at')
    search_fields = ('user__username', 'post__title')
    date_hierarchy = 'liked_at'
    
    fieldsets = (
        (None, {
            'fields': ('post', 'user')
        }),
    )