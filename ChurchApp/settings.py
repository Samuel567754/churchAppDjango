from pathlib import Path
import os
from decouple import config
import dj_database_url
import cloudinary
import cloudinary.uploader
import cloudinary.api
from celery.schedules import crontab

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool)

# Static files settings
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
COMPRESS_ROOT = STATIC_ROOT

if DEBUG:
    # Enable WhiteNoise for production
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

ALLOWED_HOSTS = [
    'church-app-oukg.onrender.com',
    '127.0.0.1',
    'localhost'
]

# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # During development

CRISPY_ALLOWED_TEMPLATE_PACKS = "tailwind"
CRISPY_TEMPLATE_PACK = "tailwind"


VERSATILEIMAGEFIELD_SETTINGS = {
    'variations': {
        '1200x1200': (1200, 1200),  # instead of 'fullsize'
        '400x600': (400, 600),      # instead of 'thumbnail'
        'webp': {
            'size': (400, 600),
            'crop': True,
            'format': 'WEBP',
        },
    },
}


# Celery Configuration
# CELERY_BROKER_URL = "redis://127.0.0.1:6379/0"
# CELERY_ACCEPT_CONTENT = ["json"]
# CELERY_TASK_SERIALIZER = "json"
# CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'
# CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
# CELERY_TIMEZONE = 'Africa/Accra'

# # Django Time Zone Configuration
# TIME_ZONE = 'Africa/Accra'
# USE_TZ = True

# CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True


# Use the Redis URL from environment if available, otherwise default to localhost.
CELERY_BROKER_URL = os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/0')
CELERY_RESULT_BACKEND = os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/0')

CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
CELERY_TIMEZONE = 'Africa/Accra'

# Django Time Zone Configuration
TIME_ZONE = 'Africa/Accra'
USE_TZ = True



CELERY_BEAT_SCHEDULE = {
    'send-bible-verse-notification': {
        'task': 'worship.tasks.send_bible_verse_notification',
        'schedule': crontab(hour=9, minute=0),  # Executes daily at 9:00 AM
    },
    'send-appointment-reminders': {
        'task': 'worship.tasks.send_appointment_reminders',
        'schedule': crontab(hour=7, minute=0, day_of_month='1-31/2'),  # Executes every 2 days at 7:00 AM
    },
     'archive-old-appointments': {
        'task': 'worship.tasks.archive_old_appointments',
        'schedule': crontab(hour=0, minute=0, day_of_week='sunday'),  # Executes every Sunday at midnight
    },
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

if DEBUG:
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True


INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'compressor',
    "phonenumber_field",
    'sweetify',
    'crispy_forms',
    'crispy_tailwind',
    'widget_tweaks',
    'django_ckeditor_5',
    'contact',
    'membership',
    'blog',
    'finance',
    'event',
    'community',
    'worship',
    'account',
    'settings',
    'django_celery_beat',
    'imagekit',
    'versatileimagefield',
    'storages',
    'cloudinary',
    'cloudinary_storage',
    'defender',
]


# Number of failed login attempts allowed before blocking (default is 3)
DEFENDER_LOGIN_FAILURE_LIMIT = 3

# How long (in hours) to keep login attempt records (default is 24)
DEFENDER_ACCESS_ATTEMPT_EXPIRATION = 24

# If using Redis, you can also set:
# DEFENDER_REDIS_URL = 'redis://127.0.0.1:6379/0'
# Instead of using a Redis URL, configure django‑defender to use your Django cache:
DEFENDER_REDIS_NAME = 'default'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # 'csp.middleware.CSPMiddleware', # then add CSP middleware
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'defender.middleware.FailedLoginMiddleware',
]



if DEBUG:
    CSP_DEFAULT_SRC = ("'none'",)

    CSP_REPORT_ONLY = True
    # CSP_REPORT_URI = ["/csp-report/"]

    # Allow scripts from your domain and external providers.
    CSP_SCRIPT_SRC = (
        "'self'",
        "https://cdn.tailwindcss.com",           # Tailwind CSS config
        "https://cdn.jsdelivr.net",               # Flowbite, Alpine.js, Flatpickr JS, etc.
        "https://cdnjs.cloudflare.com",            # Font Awesome, GSAP, Lucide, Tailwind JS, etc.
        "https://ajax.googleapis.com",             # Google APIs (if needed)
        "https://code.jquery.com",                 # jQuery (if used)
        "https://cdn.ckeditor.com",                # CKEditor JS if any
        "https://www.googletagmanager.com",          # Google Tag Manager
        "https://maps.googleapis.com",             # Google Maps
        "https://www.google-analytics.com",
        "https://www.googletagmanager.com",         # Google Analytics
        "https://www.google.com",                   # Google APIs
        "https://www.gstatic.com",                  # Google APIs
        "https://unpkg.com",                        # SweetAlert and others
    )

    # Allow styles from your domain and trusted CDNs.
    CSP_STYLE_SRC = (
        "'self'",
        "'unsafe-inline'",                         # Needed if you have inline style blocks (attribute styles are not covered by nonce)
        "https://unpkg.com",                        # Boxicons, SweetAlert CSS if needed
        "https://cdn.jsdelivr.net",                # Flowbite, Tailwind CSS files, etc.
        "https://cdnjs.cloudflare.com",             # Font Awesome CSS, etc.
        "https://fonts.googleapis.com",             # Google Fonts CSS
        "https://cdn.ckeditor.com",                # CKEditor CSS
        "https://cdn.jsdelivr.net/npm/flatpickr/dist/flatpickr.min.css",
        "https://cdn.jsdelivr.net/npm/flatpickr/dist/themes/material_blue.css",
        "https://cdn.jsdelivr.net/npm/flatpickr/dist/themes/material_green.css",
        "https://cdn.jsdelivr.net/npm/flatpickr/dist/themes/material_red.css",
    )

    # Allow images from your domain and external hosts.
    CSP_IMG_SRC = (
        "'self'",
        "https://res.cloudinary.com",              # Cloudinary
        "https://*.supabase.co",                    # Supabase storage
        "https://images.unsplash.com",              # Unsplash images
        "https://www.googleadservices.com",         # Google Ads images
        "https://pbs.twimg.com",
        "https://platform-lookaside.fbsbx.com",
        "https://twitter.com",
        "https://i.ytimg.com",
        "https://lh3.googleusercontent.com",
        "https://via.placeholder.com",
        "https://platform-lookaside.fbsbx.com",     # Twitter images
        "https://maps.gstatic.com",
        "data:",
    )

    # Allow fonts from your domain and common font hosts.
    CSP_FONT_SRC = (
        "'self'",
        "https://cdnjs.cloudflare.com",
        "https://fonts.gstatic.com",                # Google Fonts
        "https://fonts.googleapis.com",             # Google Fonts
        "https://unpkg.com",                        # Boxicons, etc.
        "https://cdn.jsdelivr.net",                 # Flowbite, Tailwind CSS files, etc.
    )

    # Allow connections for AJAX, API calls, etc.
    CSP_CONNECT_SRC = (
        "'self'",
        "https://*.supabase.co",                    # Supabase APIs
        "https://www.google-analytics.com",         # Google Analytics
        "wss://",                                   # Secure WebSocket connections (if needed)
    )

    # Allow iframes from your domain and common providers.
    CSP_FRAME_SRC = (
        "'self'",
        "https://docs.google.com",                  # Google Docs embeds
        "https://www.youtube.com",                  # YouTube embeds
        "https://player.vimeo.com",                 # Vimeo embeds
        "https://www.facebook.com",                 # Facebook embeds
        "https://platform.twitter.com",             # Twitter embeds
        "https://www.google.com",                   # Google APIs
        "https://www.gstatic.com",                  # Google APIs 
        "https://*.google.com"
    )

    # Block plugin content.
    CSP_OBJECT_SRC = ("'none'",)

    # Restrict base URI and form actions.
    CSP_BASE_URI = ("'self'",)
    CSP_FORM_ACTION = ("'self'",)

    # Enable nonce support for inline <script> and <style> tags.
    CSP_INCLUDE_NONCE_IN = ['script-src', 'style-src']




# Compression settings
COMPRESS_ENABLED = True
COMPRESS_ROOT = STATIC_ROOT
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',  # Add this line
]


EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', cast=int, default=587)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', cast=bool, default=True)
EMAIL_USE_SSL = config('EMAIL_USE_SSL', cast=bool, default=False)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='samytest777@gmail.com')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='otofemmjngoviemj')


# settings.py
ADMIN_EMAIL = 'chilljohn682@gmail.com'  # Or use a list of emails if needed
DEFAULT_FROM_EMAIL = 'samytest777@gmail.com'  # Or your app's default email address

# LOGIN_URL = 'login'
LOGIN_URL = 'account:login'
LOGIN_REDIRECT_URL = 'membership:member_dashboard_home'
LOGOUT_REDIRECT_URL = 'community:home'


PASSWORD_RESET_REDIRECT_URL = 'password_reset_done'


OPENAI_API_KEY = config('OPENAI_API_KEY')

# settings.py
PAYSTACK_SECRET_KEY = config('PAYSTACK_SECRET_KEY')
PAYSTACK_PUBLIC_KEY = config('PAYSTACK_PUBLIC_KEY')


ROOT_URLCONF = 'ChurchApp.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'membership.context_processors.member_profile',
                'membership.context_processors.notification_context',
                'account.context_processors.church_info',
                # 'notifications.context_processors.notifications',
                "csp.context_processors.nonce",  # Required for nonce support
            ],
        },
    },
]

WSGI_APPLICATION = 'ChurchApp.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases
# Database configuration
if not DEBUG:
    DATABASES = {
         'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    DATABASES = {
        'default': dj_database_url.config(
            default=os.getenv("DATABASE_URL"),
            conn_max_age=600,
            ssl_require=True
        )
    }


# settings.py
SESSION_ENGINE = 'django.contrib.sessions.backends.db'  # Default: database-backed sessions


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# if  DEBUG:
#     # SUPABASE_URL = config("SUPABASE_URL")
#     # SUPABASE_KEY = config("SUPABASE_KEY")
#     # SUPABASE_STORAGE_BUCKET = "mediafiles"  # e.g., "media-files"

#     # STORAGES = {
#     #     "default": {
#     #         "BACKEND": "ChurchApp.storage.SupabaseMediaStorage",
#     #     },
#     #     "staticfiles": {
#     #         "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
#     #     },
#     # }
    
#     STORAGES = {
#     "default": {
#         "BACKEND": "settings.storage_backends.combined_storage.CombinedDynamicStorage",
#     },
#     "staticfiles": {
#         "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
#     },
#         }

#         # Also add your Cloudinary and Supabase settings:
#     CLOUDINARY_CLOUD_NAME = config("CLOUDINARY_CLOUD_NAME")
#     CLOUDINARY_API_KEY = config("CLOUDINARY_API_KEY")
#     CLOUDINARY_API_SECRET = config("CLOUDINARY_API_SECRET")
#     CLOUDINARY_FOLDER = "media"  # or another folder name you wish to use
#     DEFAULT_IMAGE_URL = "https://ehoromymaeqciokbytfm.supabase.co/storage/v1/object/public/mediafiles/church_logos/Adum_20250320_064910_0000.png"

#     SUPABASE_URL = config("SUPABASE_URL")
#     SUPABASE_KEY = config("SUPABASE_KEY")
#     SUPABASE_STORAGE_BUCKET = "mediafiles"  # e.g., "media-files"

# else:
#     MEDIA_URL = '/media/'
#     MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


if DEBUG:   
    # For production, storage is set explicitly on model fields.
    # Optionally, you could set DEFAULT_FILE_STORAGE to one of your custom backends.
    STORAGES = {
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    }

    # Cloudinary settings (for production)
    CLOUDINARY_CLOUD_NAME = config("CLOUDINARY_CLOUD_NAME")
    CLOUDINARY_API_KEY = config("CLOUDINARY_API_KEY")
    CLOUDINARY_API_SECRET = config("CLOUDINARY_API_SECRET")
    CLOUDINARY_FOLDER = "media"

    DEFAULT_IMAGE_URL = "https://ehoromymaeqciokbytfm.supabase.co/storage/v1/object/public/mediafiles/church_logos/Adum_20250320_064910_0000.png"

    # Supabase settings (for production)
    SUPABASE_URL = config("SUPABASE_URL")
    SUPABASE_KEY = config("SUPABASE_KEY")
    SUPABASE_STORAGE_BUCKET = "mediafiles"
else:
    # Use local filesystem storage for media.
    DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
    STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
    MEDIA_URL = '/media/'
   


customColorPalette = [
    {
        'color': 'hsl(4, 90%, 58%)',
        'label': 'Red'
    },
    {
        'color': 'hsl(340, 82%, 52%)',
        'label': 'Pink'
    },
    {
        'color': 'hsl(291, 64%, 42%)',
        'label': 'Purple'
    },
    {
        'color': 'hsl(262, 52%, 47%)',
        'label': 'Deep Purple'
    },
    {
        'color': 'hsl(231, 48%, 48%)',
        'label': 'Indigo'
    },
    {
        'color': 'hsl(207, 90%, 54%)',
        'label': 'Blue'
    },
]


CKEDITOR_5_ALLOW_ALL_FILE_TYPES = True
# CKEDITOR_5_UPLOAD_FILE_TYPES = ['jpeg', 'pdf', 'png'] # optional
CKEDITOR_5_CUSTOM_CSS = 'path_to.css' # optional
# CKEDITOR_5_MAX_FILE_SIZE = 5 # Max size in MBs
CKEDITOR_5_FILE_STORAGE = "django.core.files.storage.FileSystemStorage" # optional
CKEDITOR_5_CONFIGS = {
    'default': {
        'toolbar': {
            'items': ['heading', '|', 'bold', 'italic', 'link',
                      'bulletedList', 'numberedList', 'blockQuote', 'imageUpload', 'alignment', ],
        }
    },
    'extends': {
        'blockToolbar': [
            'paragraph', 'heading1', 'heading2', 'heading3',
            '|',
            'bulletedList', 'numberedList',
            '|',
            'blockQuote',
        ],
        'toolbar': {
            'items': ['heading', '|', 'outdent', 'indent', '|', 'bold', 'italic', 'link', 'underline', 'strikethrough',
                      'code', 'subscript', 'superscript', 'highlight', '|', 'codeBlock', 'sourceEditing', 'insertImage',
                      'bulletedList', 'numberedList', 'todoList', '|', 'blockQuote', 'imageUpload', 'alignment', '|',
                      'fontSize', 'fontFamily', 'fontColor', 'fontBackgroundColor', 'mediaEmbed', 'removeFormat',
                      'insertTable',
                      ],
            'shouldNotGroupWhenFull': True
        },
        'image': {
            'toolbar': ['imageTextAlternative', '|', 'imageStyle:alignLeft',
                        'imageStyle:alignRight', 'imageStyle:alignCenter', 'imageStyle:side', '|'],
            'styles': [
                'full',
                'side',
                'alignLeft',
                'alignRight',
                'alignCenter',
            ]
        },
        'table': {
            'contentToolbar': ['tableColumn', 'tableRow', 'mergeTableCells',
                            'tableProperties', 'tableCellProperties'],
            'tableProperties': {
                'borderColors': customColorPalette,
                'backgroundColors': customColorPalette
            },
            'tableCellProperties': {
                'borderColors': customColorPalette,
                'backgroundColors': customColorPalette
            }
        },
        'heading': {
            'options': [
                {'model': 'paragraph', 'title': 'Paragraph', 'class': 'ck-heading_paragraph'},
                {'model': 'heading1', 'view': 'h1', 'title': 'Heading 1', 'class': 'ck-heading_heading1'},
                {'model': 'heading2', 'view': 'h2', 'title': 'Heading 2', 'class': 'ck-heading_heading2'},
                {'model': 'heading3', 'view': 'h3', 'title': 'Heading 3', 'class': 'ck-heading_heading3'}
            ]
        }
    },
    'list': {
        'properties': {
            'styles': 'true',
            'startIndex': 'true',
            'reversed': 'true',
        }
    }
}

# Define a constant in settings.py to specify file upload permissions
CKEDITOR_5_FILE_UPLOAD_PERMISSION = "staff"  # Possible values: "staff", "authenticated", "any"



JAZZMIN_SETTINGS = {
     # title of the window (Will default to current_admin_site.site_title if absent or None)
    "site_title": "Church Admin",
    
    
    "user_avatar": "user.photo",  # Path to user profile image field
    
     # Title on the login screen (19 chars max) (defaults to current_admin_site.site_header if absent or None)
    "site_header": "Church Admin",

    # Title on the brand (19 chars max) (defaults to current_admin_site.site_header if absent or None)
    "site_brand": "Church Admin",
    
      # Welcome text on the login screen
    "welcome_sign": "Welcome to the Kumasi Central CoC Admin",
    
    
      # Copyright on the footer
    "copyright": "Kumasi Central Church of Christ 2025",
    
    
    #  # Logo to use for your site, must be present in static files, used for brand on top left
    "site_logo": "images/coc-logo.png",

    # # Logo to use for your site, must be present in static files, used for login form logo (defaults to site_logo)
    "login_logo": "images/coc-logo.png",
    # "custom_css": "css/custom_admin.css",  # Add custom CSS

    # # Logo to use for login form in dark themes (defaults to login_logo)
    "login_logo_dark": "images/coc-logo.png",

    # # CSS classes that are applied to the logo above
    # "site_logo_classes": "custom-admin-logo", 
    
    "custom_css": "css/custom_admin.css",
 
    # # Relative path to a favicon for your site, will default to site_logo if absent (ideally 32x32 px)
    # "site_icon": None,
    
    
     # Links to put along the top menu
    "topmenu_links": [
          # App with dropdown menu to all its models pages (Permissions checked against models)
        {"app": "event"},
        {"app": "finance"},
        {"app": "membership"},
        {"app": "user"},
        {"app": "contact"},
        {"app": "community"},
        {"app": "worship"},
        {"app": "blog"},
        {'name': 'visit site', 'url': 'http://127.0.0.1:8000', 'new_window': True},
    ],
    
    
     # List of model admins to search from the search bar, search bar omitted if excluded
    # If you want to use a single search field you dont need to use a list, you can use a simple string 
    # "search_model": ["auth.User", "catalog.Book"],
    
    
     "show_ui_builder": True,
     
     
     
     
      # Custom icons for side menu apps/models See https://fontawesome.com/icons?d=gallery&m=free&v=5.0.0,5.0.1,5.0.10,5.0.11,5.0.12,5.0.13,5.0.2,5.0.3,5.0.4,5.0.5,5.0.6,5.0.7,5.0.8,5.0.9,5.1.0,5.1.1,5.2.0,5.3.0,5.3.1,5.4.0,5.4.1,5.4.2,5.13.0,5.12.0,5.11.2,5.11.1,5.10.0,5.9.0,5.8.2,5.8.1,5.7.2,5.7.1,5.7.0,5.6.3,5.5.0,5.4.2
    # for the full list of 5.13.0 free icon classes
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
        
        "account.Church": "fas fa-church",
        
        "settings.MemberSettings": "fas fa-cogs",
        
        "blog.Category": "fas fa-folder",
        "blog.Post": "fas fa-newspaper",
        "blog.Comment": "fas fa-comment",
        "blog.Tag": "fas fa-tags",
        "blog.Like": "fas fa-thumbs-up", 
        
        
        "community.VolunteerOpportunity": "fas fa-handshake", 
        "community.VolunteerApplication": "fas fa-handshake",
        "community.Testimonial": "fas fa-comment",
        "community.fAQ": "fas fa-question",
        "community.Survey": "fas fa-poll",
        "community.SurveyResponse": "fas fa-poll",
        # "community.OutreachProgram": "fas fa-handshake",
        "community.Poll": "fas fa-poll",
        "community.PollOption": "fas fa-poll",
        "community.PollVote": "fas fa-poll",
        "community.Announcement": "fas fa-bullhorn",
        "community.CarouselItem": "fas fa-images",
        
        
        "contact.Contact": "fas fa-address-book",
        "contact.Staff": "fas fa-user",
        "contact.Notification": "fas fa-bell",
        "contact.Newsletter": "fas fa-newspaper",
        "contact.NewsletterSubscription": "fas fa-newspaper",
        
        
        "event.Event": "fas fa-calendar",
        "event.EventRegistration": "fas fa-calendar",
        "event.OutreachProgram": "fas fa-handshake",
        "event.ChurchCalendar": "fas fa-calendar",
        "event.GalleryImage": "fas fa-images",
        
        
        "finance.Donation": "fas fa-wallet",
        "finance.Asset": "fas fa-dollar-sign",
  
        "membership.Member": "fas fa-user",
        "membership.Family": "fas fa-users",
        "membership.Ministry": "fas fa-user",
        "membership.Attendance": "fas fa-user",
        "membership.Membership": "fas fa-user",
        
        

        "worship.Service": "fas fa-calendar",
        "worship.ServiceAttendance": "fas fa-calendar",
        "worship.Role": "fas fa-user",
        "worship.Day": "fas fa-calendar",
        "worship.Appointment": "fas fa-calendar",
        "worship.Sermon": "fas fa-bible",
        "worship.SermonSeries": "fas fa-bible",
        "worship.SermonTag": "fas fa-bible",
        "worship.ServiceSchedule": "fas fa-calendar",
        "worship.Schedule": "fas fa-calendar",
        "worship.Resource": "fas fa-bible",
        "worship.PrayerRequest": "fas fa-pray",
        "worship.LiveStream": "fas fa-video",
    },
    # Icons that are used when one is not manually specified
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",
    
     ###############
    # Change view #
    ###############
    # Render out the change view as a single form, or in tabs, current options are
    # - single
    # - horizontal_tabs (default)
    # - vertical_tabs
    # - collapsible
    # - carousel
    "changeform_format": "horizontal_tabs",
    
    
    # "changeform_format": "horizontal_tabs",
    # # override change forms on a per modeladmin basis
    # "changeform_format_overrides": {"auth.user": "collapsible", "auth.group": "vertical_tabs"},
    
    
    "related_modal_active": True
}



# JAZZMIN_UI_TWEAKS = {
#     "navbar_small_text": False,
#     "footer_small_text": False,
#     "body_small_text": False,
#     "brand_small_text": False,
#     "brand_colour": False,
#     "accent": "accent-primary",
#     "navbar": "navbar-dark",
#     "no_navbar_border": False,
#     "navbar_fixed": False,
#     "layout_boxed": False,
#     "footer_fixed": False,
#     "sidebar_fixed": False,
#     "sidebar": "sidebar-dark-primary",
#     "sidebar_nav_small_text": False,
#     "sidebar_disable_expand": False,
#     "sidebar_nav_child_indent": False,
#     "sidebar_nav_compact_style": False,
#     "sidebar_nav_legacy_style": False,
#     "sidebar_nav_flat_style": False,
#     "theme": "superhero",
#     "dark_mode_theme": "superhero",
#     "button_classes": {
#         "primary": "btn-primary",
#         "secondary": "btn-secondary",
#         "info": "btn-info",
#         "warning": "btn-warning",
#         "danger": "btn-danger",
#         "success": "btn-success"
#     }
# }


JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": False,
    "accent": "accent-primary",
    "navbar": "navbar-dark",
    "no_navbar_border": False,
    "navbar_fixed": False,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": False,
    "sidebar": "sidebar-dark-primary",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": False,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
    "theme": "superhero",
    "dark_mode_theme": "solar",
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success"
    }
}


# JAZZMIN_UI_TWEAKS = {
#     "navbar_small_text": False,
#     "footer_small_text": False,
#     "body_small_text": False,
#     "brand_small_text": False,
#     "brand_colour": False,
#     "accent": "accent-primary",
#     "navbar": "navbar-white navbar-light",
#     "no_navbar_border": False,
#     "navbar_fixed": False,
#     "layout_boxed": False,
#     "footer_fixed": False,
#     "sidebar_fixed": False,
#     "sidebar": "sidebar-dark-primary",
#     "sidebar_nav_small_text": False,
#     "sidebar_disable_expand": False,
#     "sidebar_nav_child_indent": False,
#     "sidebar_nav_compact_style": False,
#     "sidebar_nav_legacy_style": False,
#     "sidebar_nav_flat_style": False,
#     "theme": "default",
#     "dark_mode_theme": None,
#     "button_classes": {
#         "primary": "btn-outline-primary",
#         "secondary": "btn-outline-secondary",
#         "info": "btn-info",
#         "warning": "btn-warning",
#         "danger": "btn-danger",
#         "success": "btn-success"
#     }
# }










