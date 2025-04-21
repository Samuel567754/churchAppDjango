from django.shortcuts import render
from community.models import CarouselItem
from event.models import GalleryImage
from membership.models import Ministry
from django.core.paginator import Paginator, EmptyPage
from .models import FAQ, Devotional, Announcement
from blog.models import Post
import random
from event.models import Event, ChurchCalendar, OutreachProgram, EVENT_CATEGORIES
from collections import defaultdict
from django.utils import timezone
from worship.models import Sermon, LiveStream
import calendar
from django import template
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.urls import reverse
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
import hashlib
from django.core.cache import cache
from django.views.decorators.cache import cache_page
from django.views.decorators.http import require_http_methods
import json
from django.template.loader import render_to_string
from datetime import timedelta






@require_GET
def events_json(request):
    # Read categories filter from GET parameters (if any)
    categories = request.GET.get('categories')
    search_query = request.GET.get('search', '').strip()
    
    events = ChurchCalendar.objects.all().order_by('start_datetime')
    
    if categories:
        category_list = categories.split(',')
        events = events.filter(category__in=category_list)
        
    if search_query:
        events = events.filter(
            Q(title__icontains=search_query) | Q(description__icontains=search_query)
        )
    
    event_list = []
    for event in events:
        event_list.append({
            'title': event.title,
            'start': event.start_datetime.isoformat(),
            'end': event.end_datetime.isoformat() if event.end_datetime else event.start_datetime.isoformat(),
            'allDay': event.all_day,
            'url': reverse('community:church_calendar_detail', args=[event.slug]),
            'className': f'category-{event.category}',  # Adds the category class
            'extendedProps': {
                'category': event.category,
                'location': event.location,
                'description': event.description,
                'featured': event.featured,
                'image': event.image.url if event.image else None,
                'external_image': event.image_url if event.image_url else None,
            }
        })
    return JsonResponse(event_list, safe=False)




def church_calendar_detail(request, slug):
    event = get_object_or_404(ChurchCalendar, slug=slug)
    return render(request, 'community/church_calendar_detail.html', {'event': event})


# def home(request):
#     carousel_items = CarouselItem.objects.filter(is_active=True).order_by('?')
#     gallery_images = GalleryImage.objects.order_by('?')[:7]  # Load 7 random gallery images

#     # Retrieve the 10 most recent published posts
#     latest_posts_queryset = Post.objects.filter(is_published=True).order_by('-created_at')[:10]
#     latest_posts_list = list(latest_posts_queryset)
#     # Randomly select 3 posts if available, else show what exists
#     latest_posts = random.sample(latest_posts_list, min(3, len(latest_posts_list)))
    
#     # Retrieve 3 random active ministries
#     ministries = Ministry.objects.filter(is_active=True).order_by('?')[:3]
    
#     # Retrieve 3 random upcoming events (events with a date in the future)
#     # upcoming_events = Event.objects.filter(date__gte=timezone.now()).order_by('?')[:3]
    
#       # Retrieve 3 random upcoming ChurchCalendar events (start_datetime in the future)
#     upcoming_events = ChurchCalendar.objects.filter(
#         start_datetime__gte=timezone.now()
#     ).order_by('?')[:3]
    
#     # Retrieve 1 random featured sermon
#     featured_sermon = Sermon.objects.filter(is_featured=True).order_by('?').first()
    
#     # Retrieve the latest sermon (most recent by sermon date)
#     latest_sermon = Sermon.objects.order_by('-date').first()
    
#     # Retrieve the currently live stream or the next scheduled stream
#     live_stream = LiveStream.objects.filter(is_live=True).first()
#     if not live_stream:
#         live_stream = LiveStream.objects.filter(scheduled_time__gte=timezone.now()).order_by('scheduled_time').first()


#     context = {
#         'carousel_items': carousel_items,
#         'gallery_images': gallery_images,
#         'latest_posts': latest_posts,
#         'ministries': ministries,
#         'upcoming_events': upcoming_events,
#         'featured_sermon': featured_sermon,
#         'latest_sermon': latest_sermon,
#         'live_stream': live_stream,  # Pass live stream to the template
#     }
#     return render(request, 'community/home.html', context)


def home(request):
    # Existing content
    carousel_items = CarouselItem.objects.filter(is_active=True).order_by('?')
    gallery_images = GalleryImage.objects.order_by('?')[:7]  # Load 7 random gallery images

    # Retrieve the 10 most recent published posts
    latest_posts_queryset = Post.objects.filter(is_published=True).order_by('-created_at')[:10]
    latest_posts_list = list(latest_posts_queryset)
    # Randomly select 3 posts if available, else show what exists
    latest_posts = random.sample(latest_posts_list, min(3, len(latest_posts_list)))
    
    # Retrieve 3 random active ministries
    ministries = Ministry.objects.filter(is_active=True).order_by('?')[:3]
    
    # Retrieve 3 random upcoming ChurchCalendar events (start_datetime in the future)
    upcoming_events = ChurchCalendar.objects.filter(
        start_datetime__gte=timezone.now()
    ).order_by('?')[:3]
    
    # Retrieve 1 random featured sermon
    featured_sermon = Sermon.objects.filter(featured=True).order_by('?').first()
    
    # Retrieve the latest sermon (most recent by sermon date)
    latest_sermon = Sermon.objects.order_by('-date').first()
    
    # Retrieve the currently live stream or the next scheduled stream
    live_stream = LiveStream.objects.filter(is_live=True).first()
    # ------------------------------
    # Daily Devotional Integration
    # ------------------------------
    today = timezone.localdate()
    cache_key = f"daily_devotional_{today.isoformat()}"
    daily_devotional = cache.get(cache_key)

    if daily_devotional is None:
        # First, try to get devotionals scheduled for today
        scheduled_devotionals = Devotional.objects.filter(date=today)
        if scheduled_devotionals.exists():
            daily_devotional = random.choice(list(scheduled_devotionals))
        else:
            total = Devotional.objects.count()
            if total > 0:
                # Use MD5 to create a deterministic index based on today's date.
                hash_value = int(hashlib.md5(str(today).encode()).hexdigest(), 16)
                index = hash_value % total
                daily_devotional = Devotional.objects.all()[index]
            else:
                daily_devotional = None

        # Cache the daily devotional until midnight
        now = timezone.now()
        tomorrow = now + timezone.timedelta(days=1)
        midnight = timezone.datetime.combine(tomorrow.date(), timezone.datetime.min.time(), tzinfo=now.tzinfo)
        seconds_until_midnight = int((midnight - now).total_seconds())
        cache.set(cache_key, daily_devotional, seconds_until_midnight)
    
    # Build the context with the daily devotional added
    context = {
        'carousel_items': carousel_items,
        'gallery_images': gallery_images,
        'latest_posts': latest_posts,
        'ministries': ministries,
        'upcoming_events': upcoming_events,
        'featured_sermon': featured_sermon,
        'latest_sermon': latest_sermon,
        'live_stream': live_stream,
        'daily_devotional': daily_devotional,  # Daily devotional added to the context
    }
    return render(request, 'community/home.html', context)




def faq_view(request):
    faqs = FAQ.objects.filter(is_active=True)
    context = {
        'faqs': faqs,
    }
    return render(request, 'community/faq.html', context)



def about(request):
    return render(request, 'community/about.html')




# def events(request):
#     now = timezone.now()
    
#     # Get selected year and month from query parameters; default to current year/month
#     try:
#         selected_year = int(request.GET.get('year', now.year))
#         selected_month = int(request.GET.get('month', now.month))
#     except ValueError:
#         selected_year, selected_month = now.year, now.month

#     # Build datetime objects for the first and last day of the selected month
#     first_day_of_month = timezone.datetime(selected_year, selected_month, 1, tzinfo=now.tzinfo)
#     last_day = calendar.monthrange(selected_year, selected_month)[1]
#     last_day_of_month = timezone.datetime(selected_year, selected_month, last_day, 23, 59, 59, 999999, tzinfo=now.tzinfo)

#     # Use ChurchCalendar model for the event list of the year
#     church_calendar_event_list_year = ChurchCalendar.objects.filter(
#         start_datetime__year=selected_year
#     ).order_by('start_datetime')

#     # The following context items remain unchanged using the Event model
#     outreach_program_list = OutreachProgram.objects.filter(is_active=True).order_by('-start_date')
#     upcoming_events = Event.objects.filter(date__gte=now).order_by('date')
#     monthly_events = Event.objects.filter(date__gte=first_day_of_month, date__lte=last_day_of_month).order_by('date')
#     featured_events = Event.objects.filter(featured=True, date__gte=now).order_by('date')

#     context = {
#         'event_categories': EVENT_CATEGORIES,
#         'church_calendar_event_list_year': church_calendar_event_list_year,
#         'selected_year': selected_year,
#         'outreach_program_list': outreach_program_list,
#         'upcoming_events': upcoming_events,
#         'monthly_events': monthly_events,
#         'featured_events': featured_events,
#     }

#     # If it's an AJAX request, return only the partial template; otherwise, load the full events page
#     if request.headers.get('x-requested-with') == 'XMLHttpRequest':
#         return render(request, 'community/calendar_partial.html', context)
#     else:
#         return render(request, 'community/events.html', context)

def devotional_detail_json(request, slug):
    devotional = get_object_or_404(Devotional, slug=slug, published=True)
    data = {
        'title': devotional.title,
        'content': devotional.content,
        'scripture_reference': devotional.scripture_reference,
        'image_url': devotional.image_url,
        'date': devotional.date.strftime("%B %d, %Y"),
    }
    return JsonResponse(data)




def events(request):
    now = timezone.now()

    # Get selected year and month from query parameters; default to current year/month
    try:
        selected_year = int(request.GET.get('year', now.year))
        selected_month = int(request.GET.get('month', now.month))
    except ValueError:
        selected_year, selected_month = now.year, now.month

    # Build datetime objects for the first and last day of the selected month
    first_day_of_month = timezone.datetime(
        selected_year, selected_month, 1, tzinfo=now.tzinfo
    )
    last_day = calendar.monthrange(selected_year, selected_month)[1]
    last_day_of_month = timezone.datetime(
        selected_year, selected_month, last_day, 23, 59, 59, 999999, tzinfo=now.tzinfo
    )

    # Use ChurchCalendar model for the event list of the year
    church_calendar_event_list_year = ChurchCalendar.objects.filter(
        start_datetime__year=selected_year
    ).order_by('start_datetime')

    # Use ChurchCalendar for upcoming, monthly, and featured events
    outreach_program_list = OutreachProgram.objects.filter(
        is_active=True
    ).order_by('-start_date')
    upcoming_events = ChurchCalendar.objects.filter(
        start_datetime__gte=now
    ).order_by('start_datetime')
    monthly_events = ChurchCalendar.objects.filter(
        start_datetime__gte=first_day_of_month,
        start_datetime__lte=last_day_of_month
    ).order_by('start_datetime')
    featured_events = ChurchCalendar.objects.filter(
        featured=True,
        start_datetime__gte=now
    ).order_by('start_datetime')

    context = {
        'event_categories': EVENT_CATEGORIES,
        'church_calendar_event_list_year': church_calendar_event_list_year,
        'selected_year': selected_year,
        'outreach_program_list': outreach_program_list,
        'upcoming_events': upcoming_events,
        'monthly_events': monthly_events,
        'featured_events': featured_events,
    }

    # If it's an AJAX request, return only the partial template; otherwise, load the full events page
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'community/calendar_partial.html', context)
    else:
        return render(request, 'community/events.html', context)


def services(request):
    return render(request, 'community/services.html')

# def live_streams(request):
#     live_stream = LiveStream.objects.filter(is_live=True).first()
#     archived_videos = LiveStream.objects.filter(is_live=False).order_by("-created_at")
#     # Get the latest sermon
#     context = {
#         'live_stream': live_stream,
#         'archived_videos': archived_videos,
#     }
#     return render(request, 'community/live_streams.html', context)



# def live_streams(request):
#     live_stream = LiveStream.objects.filter(is_live=True).first()
#     all_archived = LiveStream.objects.filter(is_live=False).order_by("-created_at")

#     # Pagination and search
#     query = request.GET.get('q', '')
#     page_number = request.GET.get('page', 1)
#     if query:
#         all_archived = all_archived.filter(title__icontains=query)

#     paginator = Paginator(all_archived, 1)  # 6 items per page
#     page = paginator.get_page(page_number)

#     # AJAX detection using header instead of removed is_ajax()
#     if request.headers.get('x-requested-with') == 'XMLHttpRequest':
#         videos_data = [
#             {'title': vid.title, 'video_url': vid.video_url}
#             for vid in page
#         ]
#         return JsonResponse({'videos': videos_data, 'has_next': page.has_next()})

#     context = {
#         'live_stream': live_stream,
#         'archived_videos': page,
#         'query': query,
#     }
#     return render(request, 'community/live_streams.html', context)


def live_streams(request):
    # Live stream (if any)
    live_stream = LiveStream.objects.filter(is_live=True).first()

    # Base queryset for archived
    archived_qs = LiveStream.objects.filter(is_live=False).order_by('-created_at')

    # Search
    query = request.GET.get('q', '').strip()
    if query:
        archived_qs = archived_qs.filter(title__icontains=query)

    # Pagination
    page_number = int(request.GET.get('page', 1))
    paginator = Paginator(archived_qs, 6)  # show 6 per page
    page = paginator.get_page(page_number)

    # Flag items older than 30 days (no YouTube URL) for migration
    thirty_days_ago = timezone.now() - timedelta(days=30)
    for vid in page:
        vid.needs_migration = (vid.created_at < thirty_days_ago and not getattr(vid, 'yt_url', None))

    context = {
        'live_stream':      live_stream,
        'archived_videos':  page,
        'query':            query,
    }

    # AJAX / Fetch: return JSON
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string(
            'community/partials/_archived_streams_list.html',
            context,
            request=request
        )
        return JsonResponse({
            'html':      html,
            'has_next':  page.has_next(),
            'next_page': page.next_page_number() if page.has_next() else None,
        })

    # Full page
    return render(request, 'community/live_streams.html', context)

# def live_streams(request):
#     # Live stream (if any)
#     live_stream = LiveStream.objects.filter(is_live=True).first()

#     # Base queryset for archived
#     archived_qs = LiveStream.objects.filter(is_live=False).order_by('-created_at')

#     # Search
#     query = request.GET.get('q', '').strip()
#     if query:
#         archived_qs = archived_qs.filter(title__icontains=query)

#     # Pagination
#     page_number = int(request.GET.get('page', 1))
#     paginator = Paginator(archived_qs, 6)  # show 6 per page
#     page = paginator.get_page(page_number)

#     context = {
#         'live_stream': live_stream,
#         'archived_videos': page,
#         'query': query,
#     }

#     # AJAX / Fetch: return JSON
#     if request.headers.get('x-requested-with') == 'XMLHttpRequest':
#         html = render_to_string('community/partials/_archived_streams_list.html', context, request=request)
#         return JsonResponse({
#             'html': html,
#             'has_next': page.has_next(),
#             'next_page': page.next_page_number() if page.has_next() else None,
#         })

#     # Full page
#     return render(request, 'community/live_streams.html', context)



def give(request):
    return render(request, 'community/give.html')



# def devotionals(request):
    
#       # Retrieve all published devotionals ordered by published_at descending
#     devotionals = Devotional.objects.filter(published=True).order_by('-published_at')
#      # ------------------------------
#     # Daily Devotional Integration
#     # ------------------------------
#     today = timezone.localdate()
#     cache_key = f"daily_devotional_{today.isoformat()}"
#     daily_devotional = cache.get(cache_key)

#     if daily_devotional is None:
#         # First, try to get devotionals scheduled for today
#         scheduled_devotionals = Devotional.objects.filter(date=today)
#         if scheduled_devotionals.exists():
#             daily_devotional = random.choice(list(scheduled_devotionals))
#         else:
#             total = Devotional.objects.count()
#             if total > 0:
#                 # Use MD5 to create a deterministic index based on today's date.
#                 hash_value = int(hashlib.md5(str(today).encode()).hexdigest(), 16)
#                 index = hash_value % total
#                 daily_devotional = Devotional.objects.all()[index]
#             else:
#                 daily_devotional = None

#         # Cache the daily devotional until midnight
#         now = timezone.now()
#         tomorrow = now + timezone.timedelta(days=1)
#         midnight = timezone.datetime.combine(tomorrow.date(), timezone.datetime.min.time(), tzinfo=now.tzinfo)
#         seconds_until_midnight = int((midnight - now).total_seconds())
#         cache.set(cache_key, daily_devotional, seconds_until_midnight)
        
#     context = {
#         'daily_devotional': daily_devotional,  # Daily devotional added to the context
#         'devotionals': devotionals,
#     }
    
#     return render(request, 'community/devotionals.html', context)


# def devotionals(request):
#     # Define today's date early for both queries.
#     today = timezone.localdate()
    
#     # Retrieve past devotionals (exclude those scheduled for today)
#     # The variable name 'all_devotionals' remains unchanged so that it doesn't affect the template.
#     all_devotionals = Devotional.objects.filter(published=True).exclude(date=today).order_by('-published_at')

#     # ------------------------------
#     # Daily Devotional Integration
#     # ------------------------------
#     cache_key = f"daily_devotional_{today.isoformat()}"
#     daily_devotional = cache.get(cache_key)

#     if daily_devotional is None:
#         # First, try to get devotionals scheduled for today
#         scheduled_devotionals = Devotional.objects.filter(date=today)
#         if scheduled_devotionals.exists():
#             daily_devotional = random.choice(list(scheduled_devotionals))
#         else:
#             total = Devotional.objects.count()
#             if total > 0:
#                 hash_value = int(hashlib.md5(str(today).encode()).hexdigest(), 16)
#                 index = hash_value % total
#                 daily_devotional = Devotional.objects.all()[index]
#             else:
#                 daily_devotional = None

#         # Cache the daily devotional until midnight
#         now = timezone.now()
#         tomorrow = now + timezone.timedelta(days=1)
#         midnight = timezone.datetime.combine(tomorrow.date(), timezone.datetime.min.time(), tzinfo=now.tzinfo)
#         seconds_until_midnight = int((midnight - now).total_seconds())
#         cache.set(cache_key, daily_devotional, seconds_until_midnight)

#     # Pagination: Display 9 devotionals per page (or 1 per your current setup)
#     paginator = Paginator(all_devotionals, 1)
#     page_number = request.GET.get('page') or 1
#     page_obj = paginator.get_page(page_number)

#     # If the request is AJAX, return just the devotionals items HTML (a partial)
#     if request.headers.get('x-requested-with') == 'XMLHttpRequest':
#          return render(request, 'community/partials/devotionals_list_partial.html', {'page_obj': page_obj})

#     context = {
#          'daily_devotional': daily_devotional,
#          'page_obj': page_obj,
#          'paginator': paginator,
#     }
    
#     return render(request, 'community/devotionals.html', context)


def devotionals(request):
    # Define today's date early for both queries.
    today = timezone.localdate()
    
    # Retrieve past devotionals (only those scheduled for dates before today)
    all_devotionals = Devotional.objects.filter(published=True, date__lt=today).order_by('-published_at')
    
    # AJAX Search: Filter based on query parameter "q"
    search_query = request.GET.get('q', '').strip()
    if search_query:
        # Update the queryset to include only devotionals whose title contains the search term.
        all_devotionals = all_devotionals.filter(title__icontains=search_query)
    
    # ------------------------------
    # Daily Devotional Integration
    # ------------------------------
    cache_key = f"daily_devotional_{today.isoformat()}"
    daily_devotional = cache.get(cache_key)

    if daily_devotional is None:
        # First, try to get devotionals scheduled for today
        scheduled_devotionals = Devotional.objects.filter(date=today)
        if scheduled_devotionals.exists():
            daily_devotional = random.choice(list(scheduled_devotionals))
        else:
            total = Devotional.objects.count()
            if total > 0:
                hash_value = int(hashlib.md5(str(today).encode()).hexdigest(), 16)
                index = hash_value % total
                daily_devotional = Devotional.objects.all()[index]
            else:
                daily_devotional = None

        # Cache the daily devotional until midnight
        now = timezone.now()
        tomorrow = now + timezone.timedelta(days=1)
        midnight = timezone.datetime.combine(tomorrow.date(), timezone.datetime.min.time(), tzinfo=now.tzinfo)
        seconds_until_midnight = int((midnight - now).total_seconds())
        cache.set(cache_key, daily_devotional, seconds_until_midnight)

    # Pagination: Display 9 devotionals per page (or 1 per your current setup)
    paginator = Paginator(all_devotionals, 3)
    page_number = request.GET.get('page') or 1
    page_obj = paginator.get_page(page_number)

    # If the request is AJAX, return just the devotionals items HTML (a partial)
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
         return render(request, 'community/partials/devotionals_list_partial.html', {'page_obj': page_obj})

    context = {
         'daily_devotional': daily_devotional,
         'page_obj': page_obj,
         'paginator': paginator,
    }
    
    return render(request, 'community/devotionals.html', context)






def ministries(request):
    # Get all Ministry instances.
    ministries = Ministry.objects.all()
    # Load active OutreachProgram instances ordered by start_date descending.
    outreach_program_list = OutreachProgram.objects.filter(is_active=True).order_by('-start_date')
    
    context = {
        'ministries': ministries,
        'outreach_program_list': outreach_program_list,
    }
    return render(request, 'community/ministries.html', context)





def gallery(request):
    # Get the category from the query parameter; default to 'all'
    category = request.GET.get('category', 'all')
    if category and category != 'all':
        # Case-insensitive filtering
        gallery_images = GalleryImage.objects.filter(category__iexact=category)
    else:
        gallery_images = GalleryImage.objects.all()
    
    # Pagination: show 3 images per page
    images_per_page = 10
    paginator = Paginator(gallery_images, images_per_page)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Get distinct non-empty categories in a case-insensitive way
    categories_qs = GalleryImage.objects.exclude(category='').values_list('category', flat=True)
    # Normalize category names to lowercase and remove duplicates
    categories = sorted({cat.strip().lower() for cat in categories_qs})
    
    context = {
        'gallery_images': page_obj,  # Passing the Page object for pagination details
        'selected_category': category,
        'categories': categories,
    }
    
    # If the request is AJAX, render only the gallery items partial
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'community/partials/gallery_items.html', context)
    
    return render(request, 'community/gallery.html', context)




@require_GET
def announcement_list_api(request):
    """
    AJAX endpoint that returns a paginated, filtered list of announcements as JSON.
    GET params:
      - status:         one or more of 'draft', 'published', 'archived'
      - importance:     one or more of 'urgent','high','medium','low'
      - is_active:      'true' or 'false'
      - page:           integer, defaults to 1
    Response JSON:
      {
        "announcements": [
          {"id": ..., "title": ..., "content": ..., "date_posted": "...", "status": "...", "importance_level": "..."},
          …
        ],
        "has_next": true|false
      }
    """
    qs = Announcement.objects.all()

    # --- filters ---
    statuses = request.GET.getlist('status')
    if statuses:
        qs = qs.filter(status__in=statuses)

    imps = request.GET.getlist('importance')
    if imps:
        qs = qs.filter(importance_level__in=imps)

    is_active = request.GET.get('is_active')
    if is_active in ('true', 'false'):
        qs = qs.filter(is_active=(is_active == 'true'))

    # order newest first
    qs = qs.order_by('-date_posted')

    # --- pagination / “load more” ---
    page_num = request.GET.get('page', 1)
    paginator = Paginator(qs, 10)  # 10 per page
    try:
        page = paginator.page(page_num)
    except EmptyPage:
        return JsonResponse({
            'announcements': [],
            'has_next': False
        })

    # serialize
    items = []
    for ann in page.object_list:
        items.append({
            'id': ann.id,
            'title': ann.title,
            'content': ann.content,
            'date_posted': ann.date_posted.isoformat(),
            'status': ann.status,
            'importance_level': ann.importance_level,
        })

    return JsonResponse({
        'announcements': items,
        'has_next': page.has_next(),
    })
    
    
def announcement_list(request):
    """
    Renders the HTML page that contains 
    the filters, empty state, grid, and JS loader.
    """
    return render(request, 'community/announcement_list.html')