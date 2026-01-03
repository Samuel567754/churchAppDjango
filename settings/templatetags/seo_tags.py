"""
SEO Template Tags
Provides reusable structured data (JSON-LD) generation for SEO optimization.
"""
import json
from django import template
from django.utils.safestring import mark_safe
from django.utils.html import escape

register = template.Library()


@register.simple_tag(takes_context=True)
def breadcrumb_schema(context, *breadcrumbs):
    """
    Generate BreadcrumbList JSON-LD schema.
    
    Usage:
        {% breadcrumb_schema "Home|/" "Blog|/blog/" "Post Title" %}
    
    Each breadcrumb is "Name|URL" format, or just "Name" for the current page.
    """
    request = context.get('request')
    base_url = f"{request.scheme}://{request.get_host()}" if request else ""
    
    items = []
    for i, crumb in enumerate(breadcrumbs, 1):
        if '|' in crumb:
            name, url = crumb.split('|', 1)
            item_url = base_url + url if url.startswith('/') else url
        else:
            name = crumb
            item_url = request.build_absolute_uri() if request else ""
        
        items.append({
            "@type": "ListItem",
            "position": i,
            "name": escape(name),
            "item": item_url
        })
    
    schema = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": items
    }
    
    return mark_safe(f'<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False)}</script>')


@register.simple_tag(takes_context=True)
def article_schema(context, title, description, author, date_published, date_modified=None, image_url=None):
    """
    Generate Article JSON-LD schema for blog posts.
    
    Usage:
        {% article_schema post.title post.meta_description post.author.get_full_name post.published_at post.updated_at post.featured_image.url %}
    """
    request = context.get('request')
    base_url = f"{request.scheme}://{request.get_host()}" if request else ""
    
    schema = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": escape(str(title)),
        "description": escape(str(description)) if description else "",
        "author": {
            "@type": "Person",
            "name": escape(str(author))
        },
        "publisher": {
            "@type": "Organization",
            "name": "Kumasi Central Church of Christ",
            "logo": {
                "@type": "ImageObject",
                "url": f"{base_url}/static/images/icons/churchPwaIcon.png"
            }
        },
        "datePublished": str(date_published.isoformat()) if hasattr(date_published, 'isoformat') else str(date_published),
        "mainEntityOfPage": {
            "@type": "WebPage",
            "@id": request.build_absolute_uri() if request else ""
        }
    }
    
    if date_modified:
        schema["dateModified"] = str(date_modified.isoformat()) if hasattr(date_modified, 'isoformat') else str(date_modified)
    
    if image_url:
        schema["image"] = {
            "@type": "ImageObject",
            "url": image_url if image_url.startswith('http') else f"{base_url}{image_url}"
        }
    
    return mark_safe(f'<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False)}</script>')


@register.simple_tag(takes_context=True)
def video_schema(context, title, description, upload_date, video_url, thumbnail_url=None, duration=None):
    """
    Generate VideoObject JSON-LD schema for sermons with video.
    
    Usage:
        {% video_schema sermon.title sermon.description sermon.date sermon.video_url sermon.image.url %}
    """
    request = context.get('request')
    base_url = f"{request.scheme}://{request.get_host()}" if request else ""
    
    schema = {
        "@context": "https://schema.org",
        "@type": "VideoObject",
        "name": escape(str(title)),
        "description": escape(str(description)) if description else "",
        "uploadDate": str(upload_date.isoformat()) if hasattr(upload_date, 'isoformat') else str(upload_date),
        "embedUrl": str(video_url)
    }
    
    if thumbnail_url:
        schema["thumbnailUrl"] = thumbnail_url if str(thumbnail_url).startswith('http') else f"{base_url}{thumbnail_url}"
    
    if duration:
        schema["duration"] = str(duration)
    
    return mark_safe(f'<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False)}</script>')


@register.simple_tag(takes_context=True)
def faq_schema(context, faqs):
    """
    Generate FAQPage JSON-LD schema.
    
    Usage:
        {% faq_schema faqs %}
    
    Where faqs is a queryset with 'question' and 'answer' fields.
    """
    if not faqs:
        return ""
    
    items = []
    for faq in faqs:
        items.append({
            "@type": "Question",
            "name": escape(str(faq.question)),
            "acceptedAnswer": {
                "@type": "Answer",
                "text": escape(str(faq.answer))
            }
        })
    
    schema = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": items
    }
    
    return mark_safe(f'<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False)}</script>')


@register.simple_tag(takes_context=True)
def event_schema(context, title, start_date, end_date=None, location=None, description=None, image_url=None):
    """
    Generate Event JSON-LD schema for church events.
    
    Usage:
        {% event_schema event.title event.start_datetime event.end_datetime event.location event.description %}
    """
    request = context.get('request')
    base_url = f"{request.scheme}://{request.get_host()}" if request else ""
    
    schema = {
        "@context": "https://schema.org",
        "@type": "Event",
        "name": escape(str(title)),
        "startDate": str(start_date.isoformat()) if hasattr(start_date, 'isoformat') else str(start_date),
        "organizer": {
            "@type": "Organization",
            "name": "Kumasi Central Church of Christ",
            "url": base_url
        }
    }
    
    if end_date:
        schema["endDate"] = str(end_date.isoformat()) if hasattr(end_date, 'isoformat') else str(end_date)
    
    if location:
        schema["location"] = {
            "@type": "Place",
            "name": escape(str(location)),
            "address": {
                "@type": "PostalAddress",
                "addressLocality": "Kumasi",
                "addressRegion": "Ashanti",
                "addressCountry": "GH"
            }
        }
    
    if description:
        schema["description"] = escape(str(description))
    
    if image_url:
        schema["image"] = image_url if str(image_url).startswith('http') else f"{base_url}{image_url}"
    
    return mark_safe(f'<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False)}</script>')


@register.simple_tag(takes_context=True)
def sermon_schema(context, title, description, date, preacher=None, scripture=None, audio_url=None, video_url=None):
    """
    Generate Sermon/Article schema for sermons.
    
    Usage:
        {% sermon_schema sermon.title sermon.description sermon.date sermon.preacher sermon.scripture_reference %}
    """
    request = context.get('request')
    base_url = f"{request.scheme}://{request.get_host()}" if request else ""
    
    schema = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": escape(str(title)),
        "description": escape(str(description)) if description else "",
        "datePublished": str(date.isoformat()) if hasattr(date, 'isoformat') else str(date),
        "publisher": {
            "@type": "Organization",
            "name": "Kumasi Central Church of Christ"
        },
        "mainEntityOfPage": {
            "@type": "WebPage",
            "@id": request.build_absolute_uri() if request else ""
        }
    }
    
    if preacher:
        schema["author"] = {
            "@type": "Person",
            "name": escape(str(preacher))
        }
    
    if scripture:
        schema["about"] = {
            "@type": "Thing",
            "name": f"Bible: {escape(str(scripture))}"
        }
    
    if video_url:
        schema["video"] = {
            "@type": "VideoObject",
            "name": escape(str(title)),
            "embedUrl": str(video_url)
        }
    
    if audio_url:
        schema["audio"] = {
            "@type": "AudioObject",
            "contentUrl": audio_url if str(audio_url).startswith('http') else f"{base_url}{audio_url}"
        }
    
    return mark_safe(f'<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False)}</script>')


@register.simple_tag
def website_schema(site_name="Kumasi Central Church of Christ", site_url="https://www.kumasicentralchurchofchrist.com"):
    """
    Generate WebSite JSON-LD schema with search action.
    """
    schema = {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": site_name,
        "url": site_url,
        "potentialAction": {
            "@type": "SearchAction",
            "target": {
                "@type": "EntryPoint",
                "urlTemplate": f"{site_url}/blog/?search={{search_term_string}}"
            },
            "query-input": "required name=search_term_string"
        }
    }
    
    return mark_safe(f'<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False)}</script>')
