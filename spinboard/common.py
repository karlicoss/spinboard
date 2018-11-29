from datetime import datetime
from typing import List, Dict, NamedTuple, Optional
import logging

def pinboard(rest):
    return 'https://pinboard.in' + rest

def get_logger():
    return logging.getLogger('pinboard-scraper')

class Result(NamedTuple):
    uid: str
    when: datetime
    link: str
    title: str
    description: Optional[str]
    user: str
    tags: List[str]

    @property
    def repr(self):
        return f"{self.when} {self.link}  | by {self.user}\n  {self.title}\n  {self.tags}" # TODO user link?...

    @property
    def blink(self) -> str:
        return pinboard(self.uid)

    @property
    def json(self):
        res = self._asdict()
        res['when'] = res['when'].strftime('%Y%m%d%H%M%S')

        # make sure it's inverse
        tmp = Result.from_json(res)
        assert tmp == self

        return res

    @staticmethod
    def from_json(jdict):
        cp = {k: v for k, v in jdict.items()}
        cp['when'] = datetime.strptime(cp['when'], '%Y%m%d%H%M%S')
        return Result(**cp)

# TODO assert list of names here??