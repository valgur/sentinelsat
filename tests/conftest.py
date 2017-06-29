from os.path import abspath, dirname, join

import pytest

from .custom_serializer import BinaryContentSerializer


pytest_plugins = ["vcr", "socket"]


@pytest.fixture(scope='session')
def test_dir():
    return dirname(abspath(__file__))


@pytest.fixture(scope='session')
def fixtures_dir(test_dir):
    return join(test_dir, 'fixtures')


@pytest.fixture(scope='session')
def fixture_path(fixtures_dir):
    def make_fixture_path(filename):
        return join(fixtures_dir, filename)

    return make_fixture_path


@pytest.fixture(scope='session')
def cassette_dir(fixtures_dir):
    return join(fixtures_dir, 'vcr_cassettes')


@pytest.fixture
def vcr_cassette_path(vcr_cassette_name):
    return vcr_cassette_name


def scrub_response(response):
    for header in ("Authorization", "Set-Cookie", "Cookie", "Date", "Expires", "Transfer-Encoding"):
        if header in response["headers"]:
            del response["headers"][header]
    return response


def range_header_matcher(r1, r2):
    return r1.headers.get('Range', '') == r2.headers.get('Range', '')


@pytest.fixture(scope='session')
def vcr_config(cassette_dir):
    return dict(
        cassette_library_dir=cassette_dir,
        record_mode='none',
        filter_headers=['Authorization', 'Set-Cookie', 'Cookie'],
        before_record_response=scrub_response,
        decode_compressed_response=True,
        match_on=['uri', 'method', 'body', 'range_header']
    )


@pytest.fixture(scope='session')
def vcr(vcr, cassette_dir):
    vcr.register_serializer('custom', BinaryContentSerializer(cassette_dir))
    vcr.serializer = 'custom'
    vcr.register_matcher('range_header', range_header_matcher)
    return vcr


@pytest.fixture(autouse=True, scope='session')
def enable_autoblock(autoblock_network):
    return
