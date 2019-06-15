#!/usr/bin/env python3

from datetime import datetime
from urllib.parse import quote
import time
import re
from typing import NamedTuple, List, Dict, Iterator
import urllib.parse

import backoff  # type: ignore
import requests

from kython.scrape import scrape

from .common import get_logger, Result, pinboard

def extract_result(x) -> Result:
    # TODO hmm. could extract from JS?
    # var bmarks={};
    # bmarks[1134487226] = {"id":"1134487226","url":"https:\/\/pinboard.in\/u:hannahphi\/","url_id":"311762905","author":"deaduncledave","created":"2019-06-15 13:22:37","description":"","title":"Pinboard: public bookmarks for hannahphi","slug":"91677a0fc3b2","toread":"0","cached":null,"code":null,"private":"0","user_id":"189277","snapshot_id":null,"updated":"2019-06-15 13:22:37","in_collection":null,"sertags":",Hannah,food,recipes,database,","source":"9","tags":["Hannah","food","recipes","database"],"author_id":"189277","u
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

    # TODO also: <span class="bookmark_count">29</span>
    total = None
    # TODO total detection is a bit broken... wonder if I need to change user agent?
    qq = soup.find('div', {'id': 'bookmarks'})
    if qq is not None:
        for ww in qq.find_all('p'):
            mm = re.search(r'Found\s*(\d+)\s*results', ww.text)
            if mm is not None:
                total = int(mm.group(1))
                break
    bookmarks = soup.find_all('div', {'class': 'display'}) # TODO maybe search for parent of bookmark title?
    earlier = soup.find_all('a', text='« earlier')
    # more = soup.find_all('a', {'id': 'top_earlier'})
    more_link = None if len(earlier) == 0 else earlier[0].get('href')
    return (total, [extract_result(b) for b in bookmarks], more_link)

class Spinboard:
    def __init__(self):
        self.logger = get_logger()
        self.delay_s = 5

    def by_(self, query: str, limit=None) -> Iterator[Result]:
        if limit is None:
            self.logger.info('defaulting limit to 1000')
            limit = 1000

        total = None
        fetched = 0

        # TODO should make them unique via set?
        more = query
        while more is not None and fetched < limit: # TODO looks like it's givin back 20 bookmarks for tag search instead of 50 :(
            self.logger.debug("querying %s", more)
            tot, bunch, more = fetch_results(more)
            total = tot
            yield from bunch
            fetched += len(bunch)
            time.sleep(self.delay_s)
        self.logger.debug("total results: %d, expected %s", fetched, tot)

    def iter_by_tag(self, what: str, limit=None) -> Iterator[Result]:
        return self.by_(f'/t:{what}', limit=limit)

    def by_tag(self, what: str, limit=None) -> List[Result]:
        return list(self.iter_by_tag(what=what, limit=limit))

    def iter_by_query(self, query: str, limit=None) -> Iterator[Result]:
        q = urllib.parse.quote_plus(query)
        return self.by_(f'/search/?query={q}&all=Search+All', limit=limit)

    def by_query(self, query: str, limit=None) -> List[Result]:
        return list(self.iter_by_query(query=query, limit=limit))

    def search(self, query: str, limit=None) -> List[Result]:
        if query.startswith('tag:'):
            tt = query[len('tag:'):]
            return self.by_tag(tt, limit=limit)
        else:
            return self.by_query(query, limit=limit)

    def search_all(self, queries: List[str], limit=None) -> List[Result]:
        results: List[Result] = []
        for query in queries:
            results.extend(self.search(query, limit=limit))

        rr: Dict[str, Result] = {}
        for r in results:
            # TODO check if they are _exactly_ same? move it to library??
            prev = rr.get(r.uid)
            if prev is not None:
                self.logger.debug('Duplicate entry with uid %s', r.uid)
                if not prev.same(r):
                    self.logger.error('Entries are not matching: %s vs %s', prev, r)
                    raise AssertionError
            rr[r.uid] = r
        rlist = sorted(rr.values(), key=lambda e: e.when, reverse=True)
        return rlist
