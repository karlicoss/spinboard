#!/usr/bin/env python3

# TODO make these automatic too?... generate kibitzr config before running from manual and non-manual bits

from kython.scrape import scrape
from urllib.parse import quote

def cleanup_result(x):
    x.find('div', {'class': 'edit_links'}).extract()
    # remove relative timestamp
    x.find('a'  , {'class': 'when'}).clear()

def get_bookmarks(query: str):
    query = quote(query)
    # TODO count total number of pages?
    # TODO query page 980?

    soup = scrape(f'https://pinboard.in/search/?query={query}&all=Search+All') # TODO not sure about search all
    bookmarks = soup.find_all('div', {'class': 'bookmark '})

    for b in bookmarks:
        cleanup_result(b)
    return bookmarks


def main():
    import sys
    queries = sys.argv[1:]
    pages = [get_bookmarks(query) for query in queries]
    results = []
    for page in pages:
        for r in page:
            ss = r.prettify()
            if ss in results:
                continue # TODO maybe sort by time instead?..
            else:
                results.append(ss)

    for r in results:
        print("-----")
        print(r)
        print("-----")

if __name__ == '__main__':
    main()
