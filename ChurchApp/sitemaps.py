from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from django.utils import timezone
from blog.models import Post, Category as BlogCategory
from worship.models import Sermon, SermonTag
from event.models import ChurchCalendar


class StaticViewSitemap(Sitemap):
    """Sitemap for static pages with optimized priorities"""
    changefreq = 'weekly'
    protocol = 'https'

    # Define priorities for different page types
    PRIORITY_MAP = {
        'community:home': 1.0,
        'community:about': 0.9,
        'community:services': 0.9,
        'community:events': 0.8,
        'community:ministries': 0.8,
        'blog:post_list': 0.8,
        'worship:sermons': 0.8,
        'community:give': 0.7,
        'community:faq': 0.7,
        'community:gallery': 0.6,
        'community:devotionals': 0.7,
        'community:live_streams': 0.7,
        'community:announcement_list': 0.6,
        'contact:contact': 0.8,
    }

    def items(self):
        return list(self.PRIORITY_MAP.keys())

    def location(self, item):
        return reverse(item)

    def priority(self, item):
        return self.PRIORITY_MAP.get(item, 0.5)

    def lastmod(self, item):
        """Return current date for static pages as they're always current"""
        return timezone.now()


class BlogSitemap(Sitemap):
    """Sitemap for blog posts with high priority"""
    changefreq = "weekly"
    priority = 0.8
    protocol = 'https'

    def items(self):
        return Post.objects.filter(is_published=True).order_by('-published_at')

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return obj.get_absolute_url()


class BlogCategorySitemap(Sitemap):
    """Sitemap for blog categories"""
    changefreq = "weekly"
    priority = 0.6
    protocol = 'https'

    def items(self):
        return BlogCategory.objects.all()

    def location(self, obj):
        return reverse('blog:posts_by_category', kwargs={'slug': obj.slug})

    def lastmod(self, obj):
        return obj.updated_at


class SermonSitemap(Sitemap):
    """Sitemap for sermons"""
    changefreq = "weekly"
    priority = 0.8
    protocol = 'https'

    def items(self):
        return Sermon.objects.all().order_by('-date')

    def lastmod(self, obj):
        return obj.date

    def location(self, obj):
        return obj.get_absolute_url()


class SermonTagSitemap(Sitemap):
    """Sitemap for sermon tags"""
    changefreq = "monthly"
    priority = 0.5
    protocol = 'https'

    def items(self):
        return SermonTag.objects.all()

    def location(self, obj):
        return reverse('worship:tag_detail', kwargs={'slug': obj.slug})


class EventSitemap(Sitemap):
    """Sitemap for church calendar events"""
    changefreq = "daily"
    priority = 0.7
    protocol = 'https'

    def items(self):
        return ChurchCalendar.objects.all().order_by('-start_datetime')

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return obj.get_absolute_url()
