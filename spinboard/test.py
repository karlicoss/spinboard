import logging

from spinboard import Spinboard, get_logger

from kython.klogging import setup_logzero


def setup():
    setup_logzero(logging.getLogger('backoff'), level=logging.DEBUG)
    setup_logzero(get_logger(), level=logging.DEBUG)


def test_query():
    setup()
    ps = Spinboard()
    results = list(ps.iter_by_query('minds are weird', limit=20))
    assert len(results) >= 20


def test_tag():
    setup()
    ps = Spinboard()
    results = list(ps.iter_by_tag('database', limit=20))
    assert len(results) >= 20
