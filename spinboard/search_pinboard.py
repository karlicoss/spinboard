#!/usr/bin/env python3

from datetime import datetime
from urllib.parse import quote
import time
from typing import NamedTuple, List

import backoff  # type: ignore
import requests

from kython.scrape import scrape

from .common import get_logger, Result, pinboard

def extract_result(x) -> Result:
    wh = x.find('a'  , {'class': 'when'})
    uid  = wh.get('href')
    whens = wh.get('title').replace('\xa0', '')
    when = datetime.strptime(whens, "%Y.%m.%d  %H:%M:%S")

    link = x.find('a', {'class': 'bookmark_title'}).get('href')
    title = x.find('a', {'class': 'bookmark_title'}).text.strip()
    dnode = x.find('div', {'class': 'description'})
    description = None if dnode is None else dnode.text.strip()
    user = [u.text for u in x.findAll('a') if u.get('href').startswith('/u:')][-1]
    tags = list(sorted([t.text for t in x.findAll('a', {'class': 'tag'})]))
    return Result(
        uid=uid,
        when=when,
        link=link,
        title=title,
        description=description,
        user=user,
        tags=tags,
    )

def on_backoff(args=None, **kwargs):
    logger = get_logger()
    self = args[0]
    self.logger.debug("Error! Backing off!")

def hdlr(delegate):
    def fun(details):
        return delegate(**details)
    return fun

@backoff.on_exception(
    backoff.expo,
    requests.exceptions.Timeout, # TODO connectionerror?
    max_tries=10,
    jitter=backoff.random_jitter,
    on_backoff=hdlr(on_backoff),
)
def fetch_results(query):
    furl = pinboard(query)
    soup = scrape(furl)
    bookmarks = soup.find_all('div', {'class': 'bookmark '})
    earlier = soup.find_all('a', text='« earlier')
    # more = soup.find_all('a', {'id': 'top_earlier'})
    more_link = None if len(earlier) == 0 else earlier[0].get('href')
    return ([extract_result(b) for b in bookmarks], more_link)

class Spinboard:
    def __init__(self):
        self.logger = get_logger()

    def by_(self, query: str, limit=1000):
        results: List[Result] = []
        # TODO should be set??
        more = query
        while more is not None and len(results) < limit: # TODO looks like it's givin back 20 bookmarks for tag search instead of 50 :(
            self.logger.debug("querying %s", more)
            bunch, more = fetch_results(more)
            results.extend(bunch)
            time.sleep(1)
        self.logger.debug("total results: %d", len(results))
        return results

    def by_tag(self, what: str, limit=1000):
        return self.by_(f'/t:{what}', limit=limit)

    def by_query(self, query: str, limit=1000):
        return self.by_(f'/search/?query={query}&all=Search+All', limit=limit)
