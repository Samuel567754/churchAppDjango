"""
SEO Testing Script
Test sitemap generation and SEO configurations
"""
import os
import sys
import django

# Setup Django environment
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ChurchApp.settings')
django.setup()

from django.urls import reverse
from ChurchApp.sitemaps import StaticViewSitemap, BlogSitemap, SermonSitemap, EventSitemap

def test_sitemaps():
    """Test sitemap generation"""
    print("=" * 50)
    print("TESTING SITEMAP GENERATION")
    print("=" * 50)
    
    # Test Static Sitemap
    print("\n1. Static Pages Sitemap:")
    static_sitemap = StaticViewSitemap()
    static_items = static_sitemap.items()
    print(f"   Found {len(static_items)} static pages")
    for item in static_items:
        try:
            location = static_sitemap.location(item)
            print(f"   ✓ {item}: {location}")
        except Exception as e:
            print(f"   ✗ {item}: ERROR - {e}")
    
    # Test Blog Sitemap
    print("\n2. Blog Sitemap:")
    blog_sitemap = BlogSitemap()
    try:
        blog_items = blog_sitemap.items()
        print(f"   Found {blog_items.count()} published blog posts")
        for post in blog_items[:5]:  # Show first 5
            print(f"   ✓ {post.title} - {post.get_absolute_url()}")
        if blog_items.count() > 5:
            print(f"   ... and {blog_items.count() - 5} more")
    except Exception as e:
        print(f"   Note: {e}")
    
    # Test Sermon Sitemap
    print("\n3. Sermon Sitemap:")
    sermon_sitemap = SermonSitemap()
    try:
        sermon_items = sermon_sitemap.items()
        print(f"   Found {sermon_items.count()} sermons")
        for sermon in sermon_items[:5]:  # Show first 5
            print(f"   ✓ {sermon.title} - {sermon.get_absolute_url()}")
        if sermon_items.count() > 5:
            print(f"   ... and {sermon_items.count() - 5} more")
    except Exception as e:
        print(f"   Note: {e}")
    
    # Test Event Sitemap
    print("\n4. Event Sitemap:")
    event_sitemap = EventSitemap()
    try:
        event_items = event_sitemap.items()
        print(f"   Found {event_items.count()} events")
        for event in event_items[:5]:  # Show first 5
            print(f"   ✓ {event.title} - {event.get_absolute_url()}")
        if event_items.count() > 5:
            print(f"   ... and {event_items.count() - 5} more")
    except Exception as e:
        print(f"   Note: {e}")

def test_model_urls():
    """Test get_absolute_url methods"""
    print("\n" + "=" * 50)
    print("TESTING MODEL get_absolute_url METHODS")
    print("=" * 50)
    
    from blog.models import Post
    from worship.models import Sermon
    from event.models import ChurchCalendar
    
    # Test Post model
    print("\n1. Blog Post Model:")
    try:
        post = Post.objects.filter(is_published=True).first()
        if post:
            print(f"   ✓ Sample post URL: {post.get_absolute_url()}")
        else:
            print("   Note: No published posts found")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test Sermon model
    print("\n2. Sermon Model:")
    try:
        sermon = Sermon.objects.first()
        if sermon:
            print(f"   ✓ Sample sermon URL: {sermon.get_absolute_url()}")
        else:
            print("   Note: No sermons found")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test ChurchCalendar model
    print("\n3. Church Calendar Model:")
    try:
        event = ChurchCalendar.objects.first()
        if event:
            print(f"   ✓ Sample event URL: {event.get_absolute_url()}")
        else:
            print("   Note: No events found")
    except Exception as e:
        print(f"   Error: {e}")

def test_settings():
    """Test SEO-related settings"""
    print("\n" + "=" * 50)
    print("TESTING SEO SETTINGS")
    print("=" * 50)
    
    from django.conf import settings
    
    print("\n1. Sites Framework:")
    if 'django.contrib.sites' in settings.INSTALLED_APPS:
        print(f"   ✓ Sites app installed")
        print(f"   ✓ SITE_ID: {getattr(settings, 'SITE_ID', 'Not set')}")
    else:
        print("   ✗ Sites app not installed")
    
    print("\n2. Sitemaps Framework:")
    if 'django.contrib.sitemaps' in settings.INSTALLED_APPS:
        print("   ✓ Sitemaps app installed")
    else:
        print("   ✗ Sitemaps app not installed")
    
    print("\n3. Domain Configuration:")
    print(f"   Production: {getattr(settings, 'SITE_DOMAIN', 'Not set')}")
    print(f"   Debug mode: {settings.DEBUG}")

if __name__ == "__main__":
    print("\n" + "🔍 " + "=" * 48)
    print("   SEO CONFIGURATION TEST SUITE")
    print("   " + "=" * 48)
    
    try:
        test_settings()
        test_sitemaps()
        test_model_urls()
        
        print("\n" + "=" * 50)
        print("✅ SEO TEST SUITE COMPLETED")
        print("=" * 50)
        print("\nNext Steps:")
        print("1. Visit http://127.0.0.1:8000/sitemap.xml to view the sitemap")
        print("2. Visit http://127.0.0.1:8000/robots.txt to view robots.txt")
        print("3. Test meta tags by viewing page source on any page")
        print("4. Validate structured data at https://search.google.com/test/rich-results")
        print("5. Submit sitemap to Google Search Console")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
