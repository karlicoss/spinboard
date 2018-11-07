#!/usr/bin/env python3

# TODO make these automatic too?... generate kibitzr config before running from manual and non-manual bits

from kython.scrape import scrape
from urllib.parse import quote

from typing import NamedTuple, List

class Result(NamedTuple):
    when: str
    link: str
    text: str
    user: str
    tags: List[str]


    @property
    def repr(self):
        return f"{self.when} {self.link}  | by {self.user}\n  {self.text}\n  {self.tags}" # TODO user link?...

def extract_result(x) -> Result:
    when = x.find('a'  , {'class': 'when'}).get('title')
    link = x.find('a', {'class': 'bookmark_title'}).get('href')
    text = x.find('a', {'class': 'bookmark_title'}).text.strip()
    user = [u.text for u in x.findAll('a') if u.get('href').startswith('/u:')][-1]
    tags = list(sorted([t.text for t in x.findAll('a', {'class': 'tag'})]))
    return Result(when, link, text, user, tags)


def get_bookmarks(query: str):
    query = quote(query)
    # TODO count total number of pages?
    # TODO query page 980?

    soup = scrape(f'https://pinboard.in/search/?query={query}&all=Search+All') # TODO not sure about search all
    bookmarks = soup.find_all('div', {'class': 'bookmark '})
    return [extract_result(b) for b in bookmarks]


def main():
    import sys
    queries = sys.argv[1:]
    pages = [get_bookmarks(query) for query in queries]
    results = {}
    for page in pages:
        for r in page:
            results[r.link] = r

    for r in sorted(results.values(), key=lambda e: e.when, reverse=True):
        print(r.repr)

if __name__ == '__main__':
    main()
