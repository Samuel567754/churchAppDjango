# SEO Template Quick Reference Guide

## For Template Developers

This guide shows how to create SEO-optimized templates for the church website.

## Basic Page Template Structure

```django
{% extends 'base.html' %}
{% load static %}

{# ========== SEO META TAGS ========== #}

{% block title %}Your Specific Page Title - Kumasi Central CoC{% endblock %}

{% block meta_title %}Your Specific Page Title - Kumasi Central Church of Christ{% endblock %}

{% block meta_description %}
Write a compelling 150-160 character description that includes your main keyword and tells users what this page is about. Make it click-worthy!
{% endblock %}

{% block meta_keywords %}
your main keyword, secondary keyword, church kumasi, relevant terms
{% endblock %}

{# ========== OPEN GRAPH TAGS (Facebook) ========== #}

{% block og_type %}website{% endblock %}  {# Use 'article' for blog posts #}

{% block og_title %}Your Social Media Title{% endblock %}

{% block og_description %}
A catchy description for social media sharing (different from meta description if needed).
{% endblock %}

{% block og_image %}
{{ request.scheme }}://{{ request.get_host }}{% static 'images/your-feature-image.jpg' %}
{% endblock %}

{# ========== TWITTER CARD TAGS ========== #}

{% block twitter_title %}Your Twitter Title{% endblock %}

{% block twitter_description %}
Description optimized for Twitter (max 200 characters).
{% endblock %}

{% block twitter_image %}
{{ request.scheme }}://{{ request.get_host }}{% static 'images/your-twitter-image.jpg' %}
{% endblock %}

{# ========== CANONICAL URL ========== #}

{% block canonical_url %}
{{ request.scheme }}://{{ request.get_host }}{% url 'your:url:name' %}
{% endblock %}

{# ========== STRUCTURED DATA (if needed) ========== #}

{% block additional_structured_data %}
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "{{ article.title }}",
  "image": "{{ article.image.url }}",
  "datePublished": "{{ article.published_at|date:'c' }}",
  "dateModified": "{{ article.updated_at|date:'c' }}",
  "author": {
    "@type": "Person",
    "name": "{{ article.author.get_full_name }}"
  }
}
</script>
{% endblock %}

{# ========== MAIN CONTENT ========== #}

{% block content %}
<div class="container mx-auto px-4 py-8">
    {# Use semantic HTML #}
    <article>
        {# Only ONE H1 per page #}
        <h1 class="text-4xl font-bold mb-4">Your Main Heading</h1>
        
        {# Proper heading hierarchy #}
        <section>
            <h2 class="text-3xl font-semibold mb-3">Section Heading</h2>
            <p>Your content here...</p>
            
            <h3 class="text-2xl font-medium mb-2">Subsection</h3>
            <p>More content...</p>
        </section>
    </article>
</div>
{% endblock %}
```

## Blog Post Template Example

```django
{% extends 'base.html' %}
{% load static %}

{% block title %}{{ post.title }} - Blog - Kumasi Central CoC{% endblock %}

{% block meta_title %}{{ post.title }} - Kumasi Central Church of Christ{% endblock %}

{% block meta_description %}
{{ post.meta_description|default:post.content|striptags|truncatewords:25 }}
{% endblock %}

{% block meta_keywords %}
{{ post.tags.all|join:", " }}, church blog, kumasi, christian
{% endblock %}

{% block og_type %}article{% endblock %}

{% block og_title %}{{ post.title }}{% endblock %}

{% block og_description %}
{{ post.meta_description|default:post.content|striptags|truncatewords:30 }}
{% endblock %}

{% block og_image %}
{% if post.featured_image %}
{{ request.scheme }}://{{ request.get_host }}{{ post.featured_image.url }}
{% else %}
{{ request.scheme }}://{{ request.get_host }}{% static 'images/default-blog.jpg' %}
{% endif %}
{% endblock %}

{% block canonical_url %}
{{ request.scheme }}://{{ request.get_host }}{{ post.get_absolute_url }}
{% endblock %}

{% block additional_structured_data %}
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "BlogPosting",
  "headline": "{{ post.title }}",
  "image": "{% if post.featured_image %}{{ request.scheme }}://{{ request.get_host }}{{ post.featured_image.url }}{% endif %}",
  "datePublished": "{{ post.published_at|date:'c' }}",
  "dateModified": "{{ post.updated_at|date:'c' }}",
  "author": {
    "@type": "Person",
    "name": "{{ post.author.get_full_name|default:post.author.username }}"
  },
  "publisher": {
    "@type": "Organization",
    "name": "Kumasi Central Church of Christ",
    "logo": {
      "@type": "ImageObject",
      "url": "{{ request.scheme }}://{{ request.get_host }}{% static 'images/icons/churchPwaIcon.png' %}"
    }
  },
  "description": "{{ post.meta_description|default:post.content|striptags|truncatewords:30 }}"
}
</script>
{% endblock %}

{% block content %}
{# Your blog post content #}
{% endblock %}
```

## Event

 Template Example

```django
{% extends 'base.html' %}
{% load static %}

{% block title %}{{ event.title }} - Events - Kumasi Central CoC{% endblock %}

{% block additional_structured_data %}
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Event",
  "name": "{{ event.title }}",
  "startDate": "{{ event.start_datetime|date:'c' }}",
  "endDate": "{{ event.end_datetime|date:'c' }}",
  "eventStatus": "https://schema.org/EventScheduled",
  "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
  "location": {
    "@type": "Place",
    "name": "Kumasi Central Church of Christ",
    "address": {
      "@type": "PostalAddress",
      "streetAddress": "123 Abinkyi Street",
      "addressLocality": "Adum, Kumasi",
      "addressRegion": "Ashanti",
      "addressCountry": "GH"
    }
  },
  "image": "{% if event.image %}{{ request.scheme }}://{{ request.get_host }}{{ event.image.url }}{% endif %}",
  "description": "{{ event.description|striptags|truncatewords:50 }}",
  "organizer": {
    "@type": "Organization",
    "name": "Kumasi Central Church of Christ",
    "url": "{{ request.scheme }}://{{ request.get_host }}"
  }
}
</script>
{% endblock %}
```

## SEO Best Practices Checklist

### ✅ Content
- [ ] Unique, descriptive title (50-60 characters)
- [ ] Compelling meta description (150-160 characters)
- [ ] One H1 tag per page
- [ ] Proper heading hierarchy (H1 → H2 → H3)
- [ ] Keyword in first 100 words
- [ ] Alt text for all images
- [ ] Internal links to related content
- [ ] External links open in new tab (rel="noopener")

### ✅ Technical
- [ ] Canonical URL set
- [ ] Mobile responsive
- [ ] Fast loading time
- [ ] HTTPS enabled
- [ ] Proper URL structure (slugs)
- [ ] Breadcrumb navigation

### ✅ Social
- [ ] Open Graph tags complete
- [ ] Twitter Card tags complete
- [ ] Featured image (1200x630px recommended)
- [ ] Social sharing buttons

### ✅ Structured Data
- [ ] Appropriate schema type
- [ ] All required fields filled
- [ ] Valid JSON-LD syntax
- [ ] Tested with Google's Rich Results Test

## Common Schema Types

### Article/BlogPosting
- headline
- image
- datePublished
- dateModified
- author
- publisher
- description

### Event
- name
- startDate
- endDate
- location
- image
- description
- organizer

### FAQPage
```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [{
    "@type": "Question",
    "name": "Question text?",
    "acceptedAnswer": {
      "@type": "Answer",
      "text": "Answer text"
    }
  }]
}
```

### BreadcrumbList
```json
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [{
    "@type": "ListItem",
    "position": 1,
    "name": "Home",
    "item": "https://example.com/"
  },{
    "@type": "ListItem",
    "position": 2,
    "name": "Blog",
    "item": "https://example.com/blog/"
  }]
}
```

## Image Optimization

### Recommended Sizes
- Featured images: 1200x630px (Open Graph)
- Twitter images: 1200x675px (16:9)
- Square images: 1200x1200px
- Thumbnail: 400x300px

### Best Practices
- Use descriptive filenames (church-event-2024.jpg)
- Add alt text for accessibility and SEO
- Compress images (use WebP when possible)
- Lazy load images below fold
- Specify width and height attributes

## URLs Best Practices

### Good URLs ✅
- `/blog/post/inspiring-sermon-summary/`
- `/worship/sermons/sunday-service-john-316/`
- `/events/youth-gathering-2024/`

### Bad URLs ❌
- `/blog/post/123/`
- `/page?id=456`
- `/article.php?cat=2&post=789`

## Testing Your SEO

1. **View Page Source** (Ctrl+U)
   - Check meta tags are present
   - Verify canonical URL
   - Confirm structured data

2. **Google Rich Results Test**
   - https://search.google.com/test/rich-results
   - Paste your page URL
   - Fix any errors

3. **Facebook Debugger**
   - https://developers.facebook.com/tools/debug/
   - Check OG tags
   - Clear cache if needed

4. **Twitter Card Validator**
   - https://cards-dev.twitter.com/validator
   - Verify Twitter Cards

5. **Lighthouse (Chrome DevTools)**
   - F12 → Lighthouse tab
   - Run SEO audit
   - Follow recommendations

## Need Help?

- Review: `/SEO_IMPLEMENTATION.md`
- Test: Run `python test_seo.py`
- Validate: Use Google's testing tools
- Reference: Schema.org documentation
