import pytest
from django.utils.translation import activate
from django.core.cache import cache
from django.contrib.auth.models import AnonymousUser
from django.core.handlers.wsgi import WSGIRequest
from io import StringIO
from django.http import QueryDict


from ..models import *
from ..views import *
from ..context_processors import *
from ..templatetags.dates import *
from ..templatetags.numbers import *
from ..templatetags.prettify import *
from ..templatetags.markdown import *
from ..templatetags.template import *

from ..tools.wikiParser import parseStructure

# ===================================================================
#
# Test Helper
#
# ===================================================================



def fake_request(method=None, fake_user=False):
    '''Returns a fake `WSGIRequest` object that can be passed to viewss.
    If `fake_user` is `True`, we attach a random staff member to the request.
    Even if not set, you can still do this manually by setting the `user`
    attribute on the returned object.
    The `GET` and `POST` `QueryDict` objects are mutable::
        req = fake_request(mutable=True)
        req.GET['q'] = 'abc'
        my_view(req)
    '''
    request = WSGIRequest({
        'SERVER_NAME': 'localhost',
        'SERVER_PORT': '8000',
        'REQUEST_METHOD': method or 'GET',
        'wsgi.input': StringIO(),
    })

    if fake_user:
        request.user = User.objects.get_or_create(username="Darth",is_staff=True, is_active=True)[0]
    else:
        request.user = AnonymousUser()

    request.GET = QueryDict('', mutable=True)
    request.POST = QueryDict('', mutable=True)

    return request

class DictObj:
    def __init__(self, in_dict:dict):
        for key, val in in_dict.items():
            if isinstance(val, (list, tuple)):
               setattr(self, key, [DictObj(x) if isinstance(x, dict) else x for x in val])
            else:
               setattr(self, key, DictObj(val) if isinstance(val, dict) else val)


# ===================================================================
#
#  The actual tests
#
# ===================================================================

@pytest.mark.django_db
def test_views():
    cache.set('bestSaga','starwars')
    clearCache(fake_request('GET'))
    assert cache.get('bestSaga',None) == 'starwars'

    warmupCache(fake_request('GET'))
    clearCache(fake_request('GET', True))
    assert cache.get('bestSaga',None) == None

def test_tools_wikiParser():

    structure = parseStructure([
        DictObj({
            "content" : "We assume that X-Wings cannot have any damage on our giant death star. Nothing to worry about.",
            "format" : "markdown",
            "slug" : "x-wing",
            "title" : "X-Wings - a risk for our death star?",
            "encoding": "UTF-8"
        })
    ])
    
    print(structure)
    assert structure['/'][0]['title'] == "X-Wings - a risk for our death star?"

def test_contextprerpocessors():
    context = settings(None)    
    assert context['settings'].DEBUG == False

def test_templatetags_template():
    assert str(template('base'))

def test_templatetags_dates():
    assert parse_iso("2022-10-01T01:00:00.0000Z").year == 2022
    assert parse_iso("2022-10-01T01:00:00.0000Z").day == 1
    assert parse_iso("2022-10-01T01:00:00.0000Z").month == 10

    assert parse_iso("") == '?'
    assert parse_iso(2) == '?'
  
    assert parse_date("2022-01-01").year == 2022
    assert parse_date("2022-01-01").day == 1
    assert parse_date("2022-01-01").month == 1

    assert parse_date("") == '?'
    assert parse_date(2) == '?'

    assert dayssince(datetime.datetime.today()) == 1

def test_templatetags_numbers():
    assert intval('1') == 1
    assert intval('h1') == 1
    assert intval('1.1') == 1

    assert humanizeTime(100) == '1m'
    assert humanizeTime(2*60) == '2m'
    assert humanizeTime(2*60*60) == '2h 0m'
    assert humanizeTime(2*60*60*24) == '2d 0h 0m'

@pytest.mark.django_db
def test_templatetags_prettify():
    assert split("Grogu","o") == ['Gr', 'gu']
    assert split("Grogu","r") == ['G', 'ogu']

    assert startswith("Mandalorian","M") == True

    assert getTeamMember('@skywalker') == None
    assert getTeamMember('skywalker') == None

    TeamMember.objects.create(name='Luke', email='luke@skywalker.com', phone='', homepage='', username='@skywalker')

    assert getTeamMember('@skywalker').email == 'luke@skywalker.com'
    assert getTeamMember('skywalker').email == 'luke@skywalker.com'

    activate('de')
    assert getTeamMember('@project_deathstar_bot')['name'] in 'Kunde'

    activate('en')
    assert getTeamMember('@project_deathstar_bot')['name'] in 'Customer'

@pytest.mark.django_db
def test_templatetags_markdown():
    html = markdown('#Hi')    
    assert html == '<h1>Hi</h1>'

    TeamMember.objects.create(name='Luke', email='luke@skywalker.com', phone='', homepage='', username='@skywalker')

    html = markdown('[x] @skywalker was here')    
    assert html == '<input type="checkbox" checked disabled> Luke was here'