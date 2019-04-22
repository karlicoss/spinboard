from datetime import datetime
from typing import List, Dict, NamedTuple, Optional
import logging

def pinboard(rest):
    return 'https://pinboard.in' + rest

def get_logger():
    return logging.getLogger('spinboard')

class Result(NamedTuple):
    uid: str
    when: datetime
    link: str
    title: str
    description: Optional[str]
    user: str
    tags: List[str]

    @property
    def ntags(self) -> List[str]:
        return list(sorted({t.lower() for t in self.tags}))

    @property
    def repr(self):
        return f"{self.when} {self.link}  | by {self.user}\n  {self.title}\n  {self.tags}" # TODO user link?...

    @property
    def blink(self) -> str:
        return pinboard(self.uid)

    @property
    def _key(self):
        # pylint: disable=no-member
        rr = self._asdict()
        del rr['description']
        return rr

    def same(self, other: 'Result') -> bool:
        # ugh, sometimes description is not matching since it depends on where we got the result from...
        return self._key == other._key
