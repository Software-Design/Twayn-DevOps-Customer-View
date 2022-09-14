# When using this projekct in production set DEBUG to false or simple delete this line in your production environment
DEBUG = True

# Nome of the project
INTERFACE_NAME = 'Software-Design Projects'

# Add the hosts name you want to server your project from
ALLOWED_HOSTS = ['localhost']
INTERFACE_URL = 'http://localhost:8000'


# change to your local instance if not using the GitLab SaaS instance
GITLAB_URL = "https://gitlab.com"

# define your custom theme path
TEMPLATE = 'base'

LANGUAGE_CODE = 'de'

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'dbcache',
    }
}

CACHE_PROJECTS = 60 * 60 * 24
CACHE_MILESTONES = 60 * 60
CACHE_ISSUES = 60 * 10
CACHE_WIKI = 60 * 60 * 4


DATETIME_FORMAT = "d.m.y H:i"
DATE_FORMAT = "d.m.Y"

