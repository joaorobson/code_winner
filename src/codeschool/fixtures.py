"""
Functions that aids writing unit tests.
"""

import pprint
import factory
from faker import Factory as FakerFactory
from sulfur import Driver
import pytest
import pytest_selenium
import pytest_django
from pytest_factoryboy import register
from django.forms import model_to_dict
from codeschool.models import User


# Fake factory
fake = FakerFactory.create()


#
# Factory boy factories
#
@register
class UserFactory(factory.DjangoModelFactory):
    class Meta:
        model = User

    first_name = factory.LazyAttribute(lambda x: fake.first_name())
    last_name = factory.LazyAttribute(lambda x: fake.last_name())
    username = factory.LazyAttribute(lambda x: fake.user_name())
    email = factory.LazyAttribute(lambda x: fake.email())


#
# Fixtures
#
@pytest.fixture
def password():
    return fake.password()


@pytest.fixture
def user_with_password(password):
    """Create user with password"""

    user = UserFactory.create()
    user.set_password(password)
    user.save()
    return user


@pytest.fixture
def sulfur_wait():
    """The value that will be passed to the implicit wait parameter in
    selenium."""

    return 1


@pytest.fixture
def ui(selenium, live_server, sulfur_wait):
    """Return a initialized sulfur driver instance.

    The sulfur driver wraps selenium in a more convenient interface."""

    return Driver(selenium, base_url=live_server.url, wait=sulfur_wait)


@pytest.fixture
def dom(ui):
    """The dom attribute of a driver ui.

    It can be used to access elements in the page with defined ids. It is also
    userful for filling up forms as in the example::

        ... (open page)
        dom.formButton.click()      # clicks the button with id="formButton"
        dom.id_name = 'John'        # send the keys 'John' to the form element
        dom['send-button'].click()  # alternative API for element whose id's are
                                    # not valid python names.
    """

    return ui.dom


@pytest.fixture
def url_data(url_owner):
    return None


@pytest.fixture
def url_owner(user):
    return user


#
# Test helpers
#

def pytest_generate_tests(metafunc):
    cls = metafunc.cls
    if cls is not URLBaseTester and isinstance(cls, type) and issubclass(cls, URLBaseTester):
        if 'public_url' in metafunc.fixturenames:
            metafunc.parametrize('public_url', metafunc.cls.public_urls)
        if 'login_url' in metafunc.fixturenames:
            metafunc.parametrize('login_url', metafunc.cls.login_urls)
        if 'private_url' in metafunc.fixturenames:
            metafunc.parametrize('private_url', metafunc.cls.private_urls)


@pytest.fixture
def public_url(request):
    return request.param


@pytest.fixture
def login_url(request, user):
    return request.param.format(user=user)


class URLBaseTester:
    """
    Subclass this class naming it TestURLs or something similar and define the
    public_urls, login_urls and private_urls sequences.
    """
    public_urls = []
    login_urls = []
    private_urls = []

    def expect(self, a, b, response, url):
        try:
            assert a <= response.status_code < b
        except AssertionError:
            print('HEADERS')
            for k, v in response.items():
                print('    %s: %s' % (k, v))
            print('URL\n    %s' % url)
            print('RESPONSE\n    %r' % response)
            if response.status_code not in [404, 500]:
                print('BODY')
                data = (response.content.decode('utf8') or '<empty>')
                for line in data.splitlines():
                    print('    ' + line)
                raise

    @pytest.mark.django_db
    def test_public_url_accessible(self, client, public_url):
        response = client.get(public_url, follow=True)
        self.expect(200, 300, response, public_url)

    @pytest.mark.django_db
    def test_login_url_hidden_from_anonymous(self, client, login_url):
        response = client.get(login_url, follow=True)
        self.expect(400, 500, response, login_url)

    @pytest.mark.django_db
    def test_login_url_accessible(self, client, user, login_url):
        client.force_login(user)
        response = client.get(login_url, follow=True)
        self.expect(400, 500, response, login_url)

    @pytest.mark.django_db
    def test_private_urls_hidden_from_regular_users(self, client, user, private_url):
        response = client.get(private_url, follow=True)
        self.expect(400, 500, response, private_url)

    @pytest.mark.django_db
    def test_private_urls_visible_to_owner(self, client, user, private_user, private_url):
        client.force_login(private_user)
        response = client.get(private_url, follow=True)
        self.expect(400, 500, response, private_url)
