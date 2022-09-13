import pytest
from django.utils.translation import activate

from ..models import *
from ..context_processors import *
from ..templatetags.dates import *
from ..templatetags.numbers import *
from ..templatetags.prettify import *
from ..templatetags.template import *

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