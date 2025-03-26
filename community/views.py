from django.shortcuts import render
from community.models import CarouselItem
from event.models import GalleryImage
from membership.models import Ministry
from django.core.paginator import Paginator
from .models import FAQ
from blog.models import Post
import random
from event.models import Event, ChurchCalendar, OutreachProgram
from collections import defaultdict
from django.utils import timezone
from worship.models import Sermon, LiveStream
import calendar
from django import template


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
    upcoming_events = Event.objects.filter(date__gte=timezone.now()).order_by('?')[:3]
    
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
    
#     # Upcoming events: events starting from now onward
#     upcoming_events = Event.objects.filter(date__gte=now).order_by('date')
    
#     # Calculate first and last day of the current month
#     first_day_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
#     last_day = calendar.monthrange(now.year, now.month)[1]
#     last_day_of_month = now.replace(day=last_day, hour=23, minute=59, second=59, microsecond=999999)
    
#     # Monthly events: events happening in the current month
#     monthly_events = Event.objects.filter(
#         date__gte=first_day_of_month,
#         date__lte=last_day_of_month
#     ).order_by('date')
    
#     # Featured events: events marked as featured (requires BooleanField 'featured' in your Event model)
#     featured_events = Event.objects.filter(featured=True, date__gte=now).order_by('date')
    
#     # ChurchCalendar Events: upcoming church calendar events (ChurchCalendar.date is a DateField)
#     church_calendar_events = ChurchCalendar.objects.filter(date__gte=now.date()).order_by('date', 'time')
    
#     # Group ChurchCalendar events by day of the month for calendar display
#     events_by_day = defaultdict(list)
#     for event in church_calendar_events:
#         events_by_day[event.date.day].append(event)
    
#     # Custom HTMLCalendar that highlights days with ChurchCalendar events
#     class ChurchEventCalendar(calendar.HTMLCalendar):
#         def formatday(self, day, weekday):
#             if day == 0:
#                 return '<td class="noday">&nbsp;</td>'
#             cssclass = self.cssclasses[weekday]
#             day_html = f'<span class="day-number">{day}</span>'
#             if day in events_by_day:
#                 cssclass += ' event-day'
#                 # Render each event's title and time in the day cell
#                 events_html = ''.join(
#                     f'<div class="event">{e.title} at {e.time.strftime("%I:%M %p")}</div>'
#                     for e in events_by_day[day]
#                 )
#                 day_html += f'<div class="events">{events_html}</div>'
#             return f'<td class="{cssclass}">{day_html}</td>'
    
#     # Generate the HTML calendar for the current month for ChurchCalendar events
#     church_cal = ChurchEventCalendar()
#     church_html_calendar = church_cal.formatmonth(now.year, now.month)
    
#     context = {
#         'upcoming_events': upcoming_events,
#         'monthly_events': monthly_events,
#         'featured_events': featured_events,
#         'church_calendar_events': church_calendar_events,
#         'church_html_calendar': church_html_calendar,
#     }
    
#     return render(request, 'community/events.html', context)

# def events(request):
    now = timezone.now()

    # Get selected month and year from query parameters; default to current month/year
    try:
        selected_year = int(request.GET.get('year', now.year))
        selected_month = int(request.GET.get('month', now.month))
    except ValueError:
        selected_year, selected_month = now.year, now.month

    # Build datetime objects for the first and last day of the selected month
    first_day_of_month = timezone.datetime(selected_year, selected_month, 1, tzinfo=now.tzinfo)
    last_day = calendar.monthrange(selected_year, selected_month)[1]
    last_day_of_month = timezone.datetime(selected_year, selected_month, last_day, 23, 59, 59, 999999, tzinfo=now.tzinfo)

    # Filter monthly events (if needed)
    monthly_events = Event.objects.filter(
        date__gte=first_day_of_month,
        date__lte=last_day_of_month
    ).order_by('date')

    # Filter ChurchCalendar events for the selected month
    church_calendar_events = ChurchCalendar.objects.filter(
        date__gte=first_day_of_month.date(),
        date__lte=last_day_of_month.date()
    ).order_by('date', 'time')

    # Group ChurchCalendar events by day (using the day number)
    events_by_day = defaultdict(list)
    for event in church_calendar_events:
        events_by_day[event.date.day].append(event)

    # Custom HTMLCalendar subclass that adds a hover/click popup for events
    class ChurchEventCalendar(calendar.HTMLCalendar):
        def formatday(self, day, weekday):
            if day == 0:
                # Empty cell padding
                return '<td class="noday">&nbsp;</td>'
            cssclass = self.cssclasses[weekday]
            # Create the day number element
            day_html = f'<span class="day-number">{day}</span>'
            if day in events_by_day:
                cssclass += ' event-day'
                # Build popup content with details for each event
                events_html = ''
                for e in events_by_day[day]:
                    events_html += (
                        f'<div class="popup-item">'
                        f'<strong>{e.title}</strong><br>'
                        f'{e.time.strftime("%I:%M %p")}<br>'
                        f'{(e.description[:50] + "...") if e.description and len(e.description) > 50 else e.description}'
                        f'</div>'
                    )
                # Wrap the day number in a container that shows a popup on hover/click
                day_html = f'<div class="popup-container">{day_html}<div class="popup">{events_html}</div></div>'
            return f'<td class="{cssclass}">{day_html}</td>'

        def formatmonth(self, theyear, themonth, withyear=True):
            return super().formatmonth(theyear, themonth, withyear)

    cal = ChurchEventCalendar()
    html_calendar = cal.formatmonth(selected_year, selected_month)

    # Build navigation links for previous and next months
    if selected_month == 1:
        prev_year = selected_year - 1
        prev_month = 12
    else:
        prev_year = selected_year
        prev_month = selected_month - 1

    if selected_month == 12:
        next_year = selected_year + 1
        next_month = 1
    else:
        next_year = selected_year
        next_month = selected_month + 1

    prev_url = f"?year={prev_year}&month={prev_month}"
    next_url = f"?year={next_year}&month={next_month}"

    context = {
        'upcoming_events': Event.objects.filter(date__gte=now).order_by('date'),
        'monthly_events': monthly_events,
        'featured_events': Event.objects.filter(featured=True, date__gte=now).order_by('date'),
        'church_html_calendar': html_calendar,
        'prev_url': prev_url,
        'next_url': next_url,
        'selected_year': selected_year,
        'selected_month': selected_month,
    }
    return render(request, 'community/events.html', context)


# def events(request):
#     now = timezone.now()

#     # Get selected month and year from query parameters; default to current month/year
#     try:
#         selected_year = int(request.GET.get('year', now.year))
#         selected_month = int(request.GET.get('month', now.month))
#     except ValueError:
#         selected_year, selected_month = now.year, now.month

#     # Build datetime objects for the first and last day of the selected month
#     first_day_of_month = timezone.datetime(selected_year, selected_month, 1, tzinfo=now.tzinfo)
#     last_day = calendar.monthrange(selected_year, selected_month)[1]
#     last_day_of_month = timezone.datetime(selected_year, selected_month, last_day, 23, 59, 59, 999999, tzinfo=now.tzinfo)

#     # Filter ChurchCalendar events for the selected month
#     church_calendar_events = ChurchCalendar.objects.filter(
#         date__gte=first_day_of_month.date(),
#         date__lte=last_day_of_month.date()
#     ).order_by('date', 'time')

#     # Group ChurchCalendar events by day (using day number)
#     events_by_day = defaultdict(list)
#     for event in church_calendar_events:
#         events_by_day[event.date.day].append(event)

#     # Custom HTMLCalendar subclass that outputs events as clickable elements with data attributes
#     class ChurchEventCalendar(calendar.HTMLCalendar):
#         def formatday(self, day, weekday):
#             if day == 0:
#                 # Empty cell padding
#                 return '<td class="noday">&nbsp;</td>'
#             cssclass = self.cssclasses[weekday]
#             day_html = f'<span class="day-number">{day}</span>'
#             if day in events_by_day:
#                 cssclass += ' event-day'
#                 events_html = ''
#                 for e in events_by_day[day]:
#                     events_html += (
#                         f'<div class="modal-event" '
#                         f'data-title="{e.title}" '
#                         f'data-date="{e.date.strftime("%B %d, %Y")}" '
#                         f'data-time="{e.time.strftime("%I:%M %p")}" '
#                         f'data-description="{(e.description[:100] + " ...") if e.description and len(e.description) > 100 else (e.description or "")}">'
#                         f'<strong>{e.title}</strong> - {e.time.strftime("%I:%M %p")}'
#                         f'</div>'
#                     )
#                 # Wrap the day number and events in a container.
#                 day_html = f'<div class="popup-container">{day_html}<div class="popup">{events_html}</div></div>'
#             return f'<td class="{cssclass}">{day_html}</td>'

#         def formatmonth(self, theyear, themonth, withyear=True):
#             return super().formatmonth(theyear, themonth, withyear)

#     cal = ChurchEventCalendar()
#     html_calendar = cal.formatmonth(selected_year, selected_month)

#     # Build navigation links for previous and next months
#     if selected_month == 1:
#         prev_year = selected_year - 1
#         prev_month = 12
#     else:
#         prev_year = selected_year
#         prev_month = selected_month - 1

#     if selected_month == 12:
#         next_year = selected_year + 1
#         next_month = 1
#     else:
#         next_year = selected_year
#         next_month = selected_month + 1

#     prev_url = f"?year={prev_year}&month={prev_month}"
#     next_url = f"?year={next_year}&month={next_month}"

#     context = {
#         'church_html_calendar': html_calendar,
#         'prev_url': prev_url,
#         'next_url': next_url,
#         'selected_year': selected_year,
#         'selected_month': selected_month,
#         'upcoming_events': Event.objects.filter(date__gte=now).order_by('date'),
#         'monthly_events': Event.objects.filter(date__gte=first_day_of_month, date__lte=last_day_of_month).order_by('date'),
#         'featured_events': Event.objects.filter(featured=True, date__gte=now).order_by('date'),
#     }
#     return render(request, 'community/events.html', context)


# def events(request):
    now = timezone.now()

    # Get selected year and month from query parameters; default to current year/month
    try:
        selected_year = int(request.GET.get('year', now.year))
        selected_month = int(request.GET.get('month', now.month))
    except ValueError:
        selected_year, selected_month = now.year, now.month

    # Build datetime objects for the first and last day of the selected month
    first_day_of_month = timezone.datetime(selected_year, selected_month, 1, tzinfo=now.tzinfo)
    last_day = calendar.monthrange(selected_year, selected_month)[1]
    last_day_of_month = timezone.datetime(selected_year, selected_month, last_day, 23, 59, 59, 999999, tzinfo=now.tzinfo)

    # Filter ChurchCalendar events for the selected month
    church_calendar_events = ChurchCalendar.objects.filter(
        date__gte=first_day_of_month.date(),
        date__lte=last_day_of_month.date()
    ).order_by('date', 'time')

    # Also, get all ChurchCalendar events for the entire selected year
    church_calendar_event_list_year = ChurchCalendar.objects.filter(
        date__year=selected_year
    ).order_by('date', 'time')

    # Group events by day (using the day number) for the monthly calendar
    events_by_day = defaultdict(list)
    for event in church_calendar_events:
        events_by_day[event.date.day].append(event)

    # Custom HTMLCalendar subclass that outputs each event as a clickable element with data attributes.
    # It also assigns classes for past, present, and future days.
    class ChurchEventCalendar(calendar.HTMLCalendar):
        def formatday(self, day, weekday):
            if day == 0:
                return '<td class="noday">&nbsp;</td>'
            cssclass = self.cssclasses[weekday]
            # Determine the current date for this day
            current_date = timezone.datetime(selected_year, selected_month, day, tzinfo=now.tzinfo).date()
            today = now.date()
            if current_date < today:
                cssclass += ' past-event'
            elif current_date == today:
                cssclass += ' present-event'
            else:
                cssclass += ' future-event'
            day_html = f'<span class="day-number">{day}</span>'
            if day in events_by_day:
                cssclass += ' event-day'
                events_html = ''
                for e in events_by_day[day]:
                    events_html += (
                        f'<div class="modal-event" '
                        f'data-title="{e.title}" '
                        f'data-date="{e.date.strftime("%B %d, %Y")}" '
                        f'data-time="{e.time.strftime("%I:%M %p")}" '
                        f'data-description="{(e.description[:100] + " ...") if e.description and len(e.description) > 100 else (e.description or "")}">'
                        f'<strong>{e.title}</strong> - {e.time.strftime("%I:%M %p")}'
                        f'</div>'
                    )
                day_html = f'<div class="popup-container">{day_html}<div class="popup">{events_html}</div></div>'
            return f'<td class="{cssclass}">{day_html}</td>'

        def formatmonth(self, theyear, themonth, withyear=True):
            return super().formatmonth(theyear, themonth, withyear)

    cal = ChurchEventCalendar()
    html_calendar = cal.formatmonth(selected_year, selected_month)

    # Build navigation links for previous and next months
    if selected_month == 1:
        prev_year = selected_year - 1
        prev_month = 12
    else:
        prev_year = selected_year
        prev_month = selected_month - 1

    if selected_month == 12:
        next_year = selected_year + 1
        next_month = 1
    else:
        next_year = selected_year
        next_month = selected_month + 1

    prev_url = f"?year={prev_year}&month={prev_month}"
    next_url = f"?year={next_year}&month={next_month}"

    # Load Outreach Programs list (active programs ordered by start_date descending)
    outreach_program_list = OutreachProgram.objects.filter(is_active=True).order_by('-start_date')

    context = {
        'church_html_calendar': html_calendar,
        'prev_url': prev_url,
        'next_url': next_url,
        'selected_year': selected_year,
        'selected_month': selected_month,
        'church_calendar_event_list_year': church_calendar_event_list_year,
        'outreach_program_list': outreach_program_list,
        'upcoming_events': Event.objects.filter(date__gte=now).order_by('date'),
        'monthly_events': Event.objects.filter(date__gte=first_day_of_month, date__lte=last_day_of_month).order_by('date'),
        'featured_events': Event.objects.filter(featured=True, date__gte=now).order_by('date'),
    }

    # If AJAX request, return the calendar partial template only
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'community/calendar_partial.html', context)
    else:
        return render(request, 'community/events.html', context)



def events(request):
    now = timezone.now()

    # Get selected year and month from query parameters; default to current year/month
    try:
        selected_year = int(request.GET.get('year', now.year))
        selected_month = int(request.GET.get('month', now.month))
    except ValueError:
        selected_year, selected_month = now.year, now.month

    # Build datetime objects for the first and last day of the selected month
    first_day_of_month = timezone.datetime(selected_year, selected_month, 1, tzinfo=now.tzinfo)
    last_day = calendar.monthrange(selected_year, selected_month)[1]
    last_day_of_month = timezone.datetime(selected_year, selected_month, last_day, 23, 59, 59, 999999, tzinfo=now.tzinfo)

    # Filter ChurchCalendar events for the selected month
    church_calendar_events = ChurchCalendar.objects.filter(
        date__gte=first_day_of_month.date(),
        date__lte=last_day_of_month.date()
    ).order_by('date', 'time')

    # Also, get all ChurchCalendar events for the entire selected year
    church_calendar_event_list_year = ChurchCalendar.objects.filter(
        date__year=selected_year
    ).order_by('date', 'time')

    # Group events by day (using the day number) for the monthly calendar
    events_by_day = defaultdict(list)
    for event in church_calendar_events:
        events_by_day[event.date.day].append(event)

    # Custom HTMLCalendar subclass that outputs each event as a clickable element with data attributes.
    # It also assigns classes for past, present, and future days.
    class ChurchEventCalendar(calendar.HTMLCalendar):
        def formatday(self, day, weekday):
            if day == 0:
                return '<td class="noday">&nbsp;</td>'
            cssclass = self.cssclasses[weekday]
            # Determine the current date for this day
            current_date = timezone.datetime(selected_year, selected_month, day, tzinfo=now.tzinfo).date()
            today = now.date()
            if current_date < today:
                cssclass += ' past-event'
            elif current_date == today:
                cssclass += ' present-event'
            else:
                cssclass += ' future-event'
            day_html = f'<span class="day-number">{day}</span>'
            if day in events_by_day:
                cssclass += ' event-day'
                events_html = ''
                for e in events_by_day[day]:
                    events_html += (
                        f'<div class="modal-event" '
                        f'data-title="{e.title}" '
                        f'data-date="{e.date.strftime("%B %d, %Y")}" '
                        f'data-time="{e.time.strftime("%I:%M %p")}" '
                        f'data-description="{(e.description[:100] + " ...") if e.description and len(e.description) > 100 else (e.description or "")}">'
                        f'<strong>{e.title}</strong> - {e.time.strftime("%I:%M %p")}'
                        f'</div>'
                    )
                day_html = f'<div class="popup-container">{day_html}<div class="popup">{events_html}</div></div>'
            return f'<td class="{cssclass}">{day_html}</td>'

        def formatmonth(self, theyear, themonth, withyear=True):
            return super().formatmonth(theyear, themonth, withyear)

    cal = ChurchEventCalendar()
    html_calendar = cal.formatmonth(selected_year, selected_month)

    # Build navigation links for previous and next months
    if selected_month == 1:
        prev_year = selected_year - 1
        prev_month = 12
    else:
        prev_year = selected_year
        prev_month = selected_month - 1

    if selected_month == 12:
        next_year = selected_year + 1
        next_month = 1
    else:
        next_year = selected_year
        next_month = selected_month + 1

    prev_url = f"?year={prev_year}&month={prev_month}"
    next_url = f"?year={next_year}&month={next_month}"

    # Load Outreach Programs list (active programs ordered by start_date descending)
    outreach_program_list = OutreachProgram.objects.filter(is_active=True).order_by('-start_date')

    context = {
        'church_html_calendar': html_calendar,
        'prev_url': prev_url,
        'next_url': next_url,
        'selected_year': selected_year,
        'selected_month': selected_month,
        'church_calendar_event_list_year': church_calendar_event_list_year,
        'outreach_program_list': outreach_program_list,
        'upcoming_events': Event.objects.filter(date__gte=now).order_by('date'),
        'monthly_events': Event.objects.filter(date__gte=first_day_of_month, date__lte=last_day_of_month).order_by('date'),
        'featured_events': Event.objects.filter(featured=True, date__gte=now).order_by('date'),
    }

    # If AJAX request, return the calendar partial template only
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