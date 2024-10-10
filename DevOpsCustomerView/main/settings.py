"""
Django settings for GitlabCustomerView project.

Generated by 'django-admin startproject' using Django 4.1.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

ALLOWED_HOSTS = ["localhost"]

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Application definition

INSTALLED_APPS = [
    "jazzmin",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "userinterface",
    "ckeditor",
    "import_export",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "csp.middleware.CSPMiddleware",
]

ROOT_URLCONF = "main.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "userinterface.context_processors.settings",
            ],
        },
    },
]

WSGI_APPLICATION = "main.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# SevDesk API settings
SEVDESK_API_URL = "https://my.sevdesk.de/api/v1/"
SEVDESK_TOKEN = ""


# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

MEDIA_ROOT = BASE_DIR / "uploads"
MEDIA_ROOT = BASE_DIR / "uploads"
MEDIA_URL = "/uploads/"

STATIC_URL = "static/"
LOGIN_URL = "/"

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Content Security Policy (CSP)
# https://django-csp.readthedocs.io/en/latest/configuration.html

X_FRAME_OPTIONS = "SAMEORIGIN"

CSP_DEFAULT_SRC = "'none'"
CSP_IMG_SRC = "data: 'self' https://gitlab.com"
CSP_OBJECT_SRC = "blob: data: 'self'"
CSP_BASE_URI = "'none'"
CSP_INCLUDE_NONCE_IN = ["script-src"]
CSP_STYLE_SRC = "'self' 'unsafe-inline' https://software-design.de"
CSP_SCRIPT_SRC = "'self' 'unsafe-inline' https://software-design.de"
CSP_IMG_SRC = "'self' data: https://software-design.de"
CSP_FONT_SRC = "'self' https://software-design.de"

# set to True to use eMail System
SEND_MAIL = False
# email settings
EMAIL_BACKEND = ""
EMAIL_USE_TLS = True
EMAIL_HOST = ""
EMAIL_HOST_USER = ""
EMAIL_HOST_PASSWORD = ""
EMAIL_PORT = 587
# E-Mail sender from witch user gets notified if a new ticket is created by the customer
EMAIL_FROM = ""

JAZZMIN_SETTINGS = {
    "site_title": "Twayn Projekt Management Tool",
    "site_header": "Twayn",
    "site_brand": "Twayn PM Tool",
    "site_logo": "/img/logo.png",
    "login_logo": "/img/logo.png",
    "login_logo_dark": None,
    "site_logo_classes": "img-circle",
    "site_icon": None,
    "welcome_sign": "Willkommen im Twayn PM Tool",
    "copyright": "SD Software-Design GmbH",
    "user_avatar": None,
    "usermenu_links": [
        {
            "name": "Twayn Project Management Tool",
            "url": "https://twayn.com",
            "new_window": True,
        },
        {"model": "auth.user"},
    ],
    "custom_css": None,
    "custom_js": None,
    "use_google_fonts_cdn": False,
    "show_ui_builder": False,
    "topmenu_links": [
        {
            "name": "",
            "url": "/",
            "permissions": ["auth.view_user"],
            "icon": "fas fa-home",
        },
        {"name": "Nutzer", "model": "auth.User"},
        {
            "name": "Projekte",
            "url": "admin:userinterface_project_changelist",
            "permissions": ["auth.view_user"],
        },
        {"app": "userinterface"},
    ],
    "show_sidebar": True,
    "navigation_expanded": True,
    "hide_apps": [],
    "hide_models": [],
    "order_with_respect_to": [
        "userinterface.Company",
        "userinterface.CustomerUser",
        "userinterface.Project",
        "userinterface.UserProjectAssignment",
        "userinterface.Team",
        "userinterface.TeamMember",
        "auth",
    ],
    "custom_links": {
        "Unternehmen": [
            {
                "name": "Unternehmen",
                "url": "admin:userinterface_company_changelist",
                "icon": "fas fa-building",
            },
            {
                "name": "Kundenbenutzer",
                "url": "admin:userinterface_customeruser_changelist",
                "icon": "fas fa-user-tie",
            },
        ],
        "Projekte": [
            {
                "name": "Projekte",
                "url": "admin:userinterface_project_changelist",
                "icon": "fas fa-project-diagram",
            },
            {
                "name": "Projektezuweisung",
                "url": "admin:userinterface_userprojectassignment_changelist",
                "icon": "fas fa-tasks",
            },
        ],
        "Teams": [
            {
                "name": "Teams",
                "url": "admin:userinterface_team_changelist",
                "icon": "fas fa-users",
            },
            {
                "name": "Teammitglieder",
                "url": "admin:userinterface_teammember_changelist",
                "icon": "fas fa-user-friends",
            },
        ],
    },
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
        "userinterface.Company": "fas fa-building",
        "userinterface.CustomerUser": "fas fa-user-tie",
        "userinterface.DownloadableFile": "fas fa-file-download",
        "userinterface.Project": "fas fa-project-diagram",
        "userinterface.Team": "fas fa-users",
        "userinterface.TeamMember": "fas fa-user-friends",
        "userinterface.UserProjectAssignment": "fas fa-tasks",
    },
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",
    "related_modal_active": True,
    "changeform_format": "horizontal_tabs",
    "changeform_format_overrides": {
        "auth.user": "collapsible",
        "auth.group": "vertical_tabs",
    },
}


"""
=========================================================
LOCAL.PY ALWAYS OVERWRITES THESE SETTINGS
=========================================================
"""

NO_SECRET_KEY = ""
try:
    from .local import *
except ModuleNotFoundError:
    print("No local settings file")

VERIFICATION_SECRET = NO_SECRET_KEY
SECRET_KEY = NO_SECRET_KEY
# if VERIFICATION_KEY is not set set it to secret key
try:
    VERIFICATION_SECRET = ""
except NameError:
    VERIFICATION_SECRET = SECRET_KEY
