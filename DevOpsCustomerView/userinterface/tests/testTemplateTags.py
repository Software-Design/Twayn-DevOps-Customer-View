import datetime

from django.contrib.auth.models import User
from django.template.exceptions import TemplateDoesNotExist
from django.test import TestCase
from django.utils.translation import activate

from ..models import TeamMember
from ..templatetags.dates import dayssince, parse_date, parse_iso
from ..templatetags.embellish import getTeamMember, split, startswith
from ..templatetags.markdown import markdown
from ..templatetags.numbers import humanizeTime, intval
from ..templatetags.template import template


class TestTemplateTags(TestCase):
    """
    Tests the template tags
    """

    def setUp(self):
        """
        Sets up the database for the tests
        """

        user = User.objects.create(username="Darth", is_staff=True, is_active=True)
        teammember = TeamMember.objects.create(name='Luke', email='luke@skywalker.com', phone='', homepage='', username='@skywalker')


    def test_templatetags_template(self):
        """
        Testing the template tag that is named template
        """

        assert str(template('base'))
        # template: *exists*
        # The test: this is fine
        with self.assertRaises(TemplateDoesNotExist):
            template('notExistingTemplate')
        with self.assertRaises(TypeError):
            template()


    def test_templatetags_dates(self):
        """
        Testing the dates for the template tags
        """

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


    def test_templatetags_numbers(self):
        """
        Testing the numbers and the human readable time template tags
        """

        assert intval('1') == 1
        assert intval('h1') == 1
        assert intval('1.1') == 1
    
        assert humanizeTime(100) == '1m'
        assert humanizeTime(2*60) == '2m'
        assert humanizeTime(2*60*60) == '2h 0m'
        assert humanizeTime(2*60*60*24) == '2d 0h 0m'


    def test_templatetags_embellish(self):
        """
        Testing the embellish template tags
        """

        assert split("Grogu","o") == ['Gr', 'gu']
        assert split("Grogu","r") == ['G', 'ogu']

        assert startswith("Mandalorian","M") == True

        assert getTeamMember('@skywalker').email == 'luke@skywalker.com'
        assert getTeamMember('skywalker').email == 'luke@skywalker.com'

        activate('de')
        assert getTeamMember('@project_deathstar_bot')['name'] in 'Kunde'

        activate('en')
        assert getTeamMember('@project_deathstar_bot')['name'] in 'Customer'


    def test_templatetags_markdown(self):
        """
        Testing the markdown template tags
        """

        html = markdown('#Hi')
        assert html == '<h1>Hi</h1>'

        html = markdown('[x] @skywalker was here')
        assert html == '<input type="checkbox" checked disabled> Luke was here'
