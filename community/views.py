from django.shortcuts import render
from community.models import CarouselItem
from event.models import GalleryImage
from membership.models import Ministry
from django.core.paginator import Paginator
from .models import FAQ
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


# @require_GET
# def events_json(request):
#     # Read categories filter from GET parameters (if any)
#     categories = request.GET.get('categories')
#     search_query = request.GET.get('search', '').strip()
    
#     events = ChurchCalendar.objects.all().order_by('start_datetime')
    
#     if categories:
#         category_list = categories.split(',')
#         events = events.filter(category__in=category_list)
        
#     if search_query:
#         events = events.filter(
#             Q(title__icontains=search_query) | Q(description__icontains=search_query)
#         )
    
#     event_list = []
#     for event in events:
#         event_list.append({
#             'title': event.title,
#             'start': event.start_datetime.isoformat(),
#             'end': event.end_datetime.isoformat() if event.end_datetime else event.start_datetime.isoformat(),
#             'allDay': event.all_day,
#             'url': reverse('community:church_calendar_detail', args=[event.slug]),
#             'className': f'category-{event.category}',  # Adds the category class
#             'extendedProps': {
#                 'category': event.category,
#                 'location': event.location,
#                 'description': event.description,
#                 'featured': event.featured,
#             }
#         })
#     return JsonResponse(event_list, safe=False)



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


# @require_GET
# def events_json(request):
#     # Read categories filter from the GET parameters (if any)
#     categories = request.GET.get('categories')
#     events = ChurchCalendar.objects.all().order_by('start_datetime')
#     if categories:
#         category_list = categories.split(',')
#         events = events.filter(category__in=category_list)
    
#     event_list = []
#     for event in events:
#         event_list.append({
#             'title': event.title,
#             'start': event.start_datetime.isoformat(),
#             'end': event.end_datetime.isoformat() if event.end_datetime else event.start_datetime.isoformat(),
#             'allDay': event.all_day,
#             'url': reverse('community:church_calendar_detail', args=[event.slug]),
#             'className': f'category-{event.category}',  # This adds the category class to the event element
#             'extendedProps': {
#                 'category': event.category,
#                 'location': event.location,
#                 'description': event.description,
#                 'featured': event.featured,
#             }
#         })
#     return JsonResponse(event_list, safe=False)




# @require_GET
# def events_json(request):
#     """
#     JSON endpoint for FullCalendar. Returns all events as JSON.
#     """
#     # Optionally, you can filter events by a date range provided by FullCalendar via GET params
#     events = ChurchCalendar.objects.all().order_by('start_datetime')
#     event_list = []
#     for event in events:
#         event_list.append({
#             'title': event.title,
#             'start': event.start_datetime.isoformat(),
#             'end': event.end_datetime.isoformat() if event.end_datetime else event.start_datetime.isoformat(),
#             'allDay': event.all_day,
#             'url': reverse('community:church_calendar_detail', args=[event.slug]),
#             'extendedProps': {
#                 'category': event.category,
#                 'location': event.location,
#                 'description': event.description,
#                 'featured': event.featured,
#             }
#         })
#     return JsonResponse(event_list, safe=False)

def church_calendar_detail(request, slug):
    event = get_object_or_404(ChurchCalendar, slug=slug)
    return render(request, 'community/church_calendar_detail.html', {'event': event})


def home(request):
    carousel_items = CarouselItem.objects.filter(is_active=True).order_by('?')
    gallery_images = GalleryImage.objects.order_by('?')[:7]  # Load 7 random gallery images

    # Retrieve the 10 most recent published posts
    latest_posts_queryset = Post.objects.filter(is_published=True).order_by('-created_at')[:10]
    latest_posts_list = list(latest_posts_queryset)
    # Randomly select 3 posts if available, else show what exists
    latest_posts = random.sample(latest_posts_list, min(3, len(latest_posts_list)))
    
    # Retrieve 3 random active ministries
    ministries = Ministry.objects.filter(is_active=True).order_by('?')[:3]
    
    # Retrieve 3 random upcoming events (events with a date in the future)
    # upcoming_events = Event.objects.filter(date__gte=timezone.now()).order_by('?')[:3]
    
      # Retrieve 3 random upcoming ChurchCalendar events (start_datetime in the future)
    upcoming_events = ChurchCalendar.objects.filter(
        start_datetime__gte=timezone.now()
    ).order_by('?')[:3]
    
    # Retrieve 1 random featured sermon
    featured_sermon = Sermon.objects.filter(is_featured=True).order_by('?').first()
    
    # Retrieve the latest sermon (most recent by sermon date)
    latest_sermon = Sermon.objects.order_by('-date').first()
    
    # Retrieve the currently live stream or the next scheduled stream
    live_stream = LiveStream.objects.filter(is_live=True).first()
    if not live_stream:
        live_stream = LiveStream.objects.filter(scheduled_time__gte=timezone.now()).order_by('scheduled_time').first()


    context = {
        'carousel_items': carousel_items,
        'gallery_images': gallery_images,
        'latest_posts': latest_posts,
        'ministries': ministries,
        'upcoming_events': upcoming_events,
        'featured_sermon': featured_sermon,
        'latest_sermon': latest_sermon,
        'live_stream': live_stream,  # Pass live stream to the template
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
    live_streams_list = LiveStream.objects.all().order_by('-scheduled_time')
    paginator = Paginator(live_streams_list, 10)  # Display 10 live streams per page
    page_number = request.GET.get('page')
    live_streams = paginator.get_page(page_number)
    
    context = {
        'live_streams': live_streams,
    }
    return render(request, 'community/services.html', context)




def give(request):
    return render(request, 'community/give.html')



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




# def gallery(request):
#      # Pagination setup for gallery images
#     images_per_page = 3  # Number of images to show per page
#     gallery_images = GalleryImage.objects.all()
#     paginator = Paginator(gallery_images, images_per_page)
#     page_number = request.GET.get('page', 1)  # Current page number
#     page_obj = paginator.get_page(page_number)

#     context = {
#         'gallery_images': page_obj.object_list,  # Current page of images
#         'has_next': page_obj.has_next(),  # Check if more pages exist
#         'next_page_number': page_obj.next_page_number() if page_obj.has_next() else None,
#     }
#     return render(request, 'community/gallery.html', context)



# def gallery(request):
#     # Get category from query parameter; default to 'all'
#     category = request.GET.get('category', 'all')
#     if category and category != 'all':
#         gallery_images = GalleryImage.objects.filter(category=category)
#     else:
#         gallery_images = GalleryImage.objects.all()
    
#     # Pagination: show 3 images per page
#     images_per_page = 3
#     paginator = Paginator(gallery_images, images_per_page)
#     page_number = request.GET.get('page', 1)
#     page_obj = paginator.get_page(page_number)
    
#     # Get distinct non-empty categories for filter buttons
#     categories = GalleryImage.objects.exclude(category='').values_list('category', flat=True).distinct()

#     context = {
#         'gallery_images': page_obj,  # Passing the Page object
#         'selected_category': category,
#         'categories': categories,
#     }
#     # If AJAX request, return only the gallery items partial
#     if request.headers.get('x-requested-with') == 'XMLHttpRequest':
#         return render(request, 'community/partials/gallery_items.html', context)
#     return render(request, 'community/gallery.html', context)

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