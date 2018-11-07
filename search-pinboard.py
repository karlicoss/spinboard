#!/usr/bin/env python3

# TODO make these automatic too?... generate kibitzr config before running from manual and non-manual bits

from kython.scrape import scrape
from urllib.parse import quote

def cleanup_result(x):
    x.find('div', {'class': 'edit_links'}).extract()
    # remove relative timestamp
    x.find('a'  , {'class': 'when'}).clear()

def get_results(query: str):
    query = quote(query)
    # TODO count total number of pages?
    # TODO query page 980?

    soup = scrape(f'https://pinboard.in/search/?query={query}&all=Search+All')
    results = soup.find_all('div', {'class': 'bookmark '})

    for r in results:
        cleanup_result(r)
    return results


def main():
    import sys
    what = sys.argv[1]
    results = get_results(what)
    for r in results:
        print("-----")
        print(r.prettify())
        print("-----")

if __name__ == '__main__':
    main()
