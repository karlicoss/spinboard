import logging

from spinboard import Spinboard, get_logger


def setup():
    # TODO how to enable logging properly?..
    logging.basicConfig(level=logging.DEBUG)


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
