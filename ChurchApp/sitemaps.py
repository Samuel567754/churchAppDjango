from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from blog.models import Post
from worship.models import Sermon
from event.models import ChurchCalendar

class StaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = 'weekly'

    def items(self):
        return [
            'community:home',
            'community:about',
            'community:services',
            'community:events',
            'community:ministries',
            'community:give',
            'community:faq',
            'community:gallery',
            'community:devotionals',
            'community:live_streams',
            'contact:contact',
            'blog:post_list',
            'worship:sermons',
        ]

    def location(self, item):
        return reverse(item)

class BlogSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return Post.objects.filter(is_published=True)

    def lastmod(self, obj):
        return obj.updated_at

class SermonSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return Sermon.objects.all()

    def lastmod(self, obj):
        return obj.date

class EventSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.6

    def items(self):
        return ChurchCalendar.objects.all()

    def lastmod(self, obj):
        return obj.updated_at
