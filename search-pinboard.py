#!/usr/bin/env python3
# pip3 install backoff

# TODO make these automatic too?... generate kibitzr config before running from manual and non-manual bits

from urllib.parse import quote
import logging
import time
from typing import NamedTuple, List

import backoff  # type: ignore
import requests

from kython.scrape import scrape


def get_logger():
    return logging.getLogger('pinboard-scraper')

def pinboard(rest):
    return 'https://pinboard.in' + rest

class Result(NamedTuple):
    uid: str
    when: str
    link: str
    text: str
    user: str
    tags: List[str]

    @property
    def repr(self):
        return f"{self.when} {self.link}  | by {self.user}\n  {self.text}\n  {self.tags}" # TODO user link?...

    @property
    def blink(self) -> str:
        return pinboard(self.uid)

def extract_result(x) -> Result:
    wh = x.find('a'  , {'class': 'when'})
    when = wh.get('title')
    uid  = wh.get('href')
    when = when.replace('\xa0', '')
    link = x.find('a', {'class': 'bookmark_title'}).get('href')
    text = x.find('a', {'class': 'bookmark_title'}).text.strip()
    user = [u.text for u in x.findAll('a') if u.get('href').startswith('/u:')][-1]
    tags = list(sorted([t.text for t in x.findAll('a', {'class': 'tag'})]))
    return Result(uid, when, link, text, user, tags)

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
    more = soup.find_all('a', {'id': 'top_earlier'})
    more_link = None if len(more) == 0 else more[0].get('href')
    return ([extract_result(b) for b in bookmarks], more_link)

class PinboardSearch:
    def __init__(self):
        self.logger = get_logger()

    def by_(self, query: str, limit=1000):
        results = []
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
        return self.by_(f'search/?query={query}&all=Search+All', limit=limit)

def main():
    logging.basicConfig(level=logging.INFO)
    get_logger().setLevel(logging.DEBUG)

    import sys
    queries = sys.argv[1:]
    tags = []
    rest = []
    for q in queries:
        if q.startswith('tag:'):
            tags.append(q[len('tag:'):])
        else:
            rest.append(q)

    psearch = PinboardSearch()

    results = []
    for tag in tags:
        results.extend(psearch.by_tag(tag))

    for query in rest:
        results.extend(psearch.by_query(query))

    map = {}
    for r in results:
        map[r.uid] = r

    for r in sorted(map.values(), key=lambda e: e.when, reverse=True):
        print(r.repr)

if __name__ == '__main__':
    main()
