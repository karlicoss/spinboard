import argparse
import json
import logging
import sys

from spinboard import Spinboard, get_logger

def main():
    logging.basicConfig(level=logging.INFO)
    logger = get_logger()
    logger.setLevel(logging.DEBUG)

    p = argparse.ArgumentParser()
    p.add_argument('--limit', type=int, default=1000)
    p.add_argument('--json', action='store_true', default=False)
    p.add_argument('queries', nargs=argparse.REMAINDER)
    # TODO specify which kind of search? e.g. --tag or --all etc
    args = p.parse_args()
    limit = args.limit
    queries = args.queries

    assert len(queries) > 0

    psearch = Spinboard()
    rlist = psearch.search_all(queries)
    if args.json:
        json.dump([r.json for r in rlist], sys.stdout, ensure_ascii=False, indent=1, sort_keys=True)
    else:
        for r in rlist:
            print(r.repr)


if __name__ == '__main__':
    main()


# TODO I guess should still could keep json states under kibitzr? but then post-process and go throught git history? not sure.
# for starters, just collect jsons daily..

# TODO merge results so they are unique? maybe store how did we find it as well; not sure if useful?
