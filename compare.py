#!/usr/bin/env python3
import argparse
from json import loads
from subprocess import check_call, check_output

from deepdiff import DeepDiff # type: ignore



class RepoHandle:
    def __init__(self, repo: str):
        self.repo = repo

    def check_output(self, *args):
        return check_output([
            'git', f'--git-dir={self.repo}/.git', *args
        ])

    def get_revisions(self):
        return list(reversed(self.check_output(
            'log',
            '--pretty=format:%h',
            '--no-patch',
        ).decode('utf8').splitlines()))

    def get_content(self, rev: str) -> str:
        return self.check_output(
            'show',
            rev + ':content.json',
        ).decode('utf8')

    def get_all_versions(self):
        revs = self.get_revisions()
        jsons = []
        for rev in revs[1:]:
            cc = self.get_content(rev)
            if len(cc.strip()) == 0:
                j = {}
            else:
                j = loads(cc)
            jsons.append((rev, j))
        return jsons

    # pass
    # return [
    #     [
    #         {'link': 'hi.org'},
    #         {'link': 'alalal.org'},
    #     ],
    #     [
    #         {'link': 'alalal.org'},
    #     ],
    # ]

from spinboard.common import Result
def diffference(before, after):
    db = {x.uid: x for x in before}
    da = {x.uid: x for x in after}
    removed = []
    added = []
    for x in {*db.keys(), *da.keys()}:
        if x in db and x not in da:
            removed.append(db[x])
        elif x not in db and x in da:
            added.append(da[x])
        elif x in db and x in da:
            pass # TODO compare??
        else:
            raise AssertionError
    return removed, added

class Collector:
    def __init__(self):
        self.items = {}

    def register(self, batch):
        added = []
        for i in batch:
            if i.uid in self.items:
                pass # TODO FIXME compare? if description or tags changed, report it?
            else:
                added.append(i)
                self.items[i.uid] = i
        return added

def tabulate(text: str):
    if text is None:
        return "   "
    return '\n'.join('   ' + t for t in text.splitlines())

# TODO html mode??
def print_all_diffs(repo: str):
    from pprint import pprint
    rh = RepoHandle(repo)
    cc = Collector()
    jsons = rh.get_all_versions()
    for jj in jsons:
        rev, j = jj
        items = list(map(Result.from_json, j))
        added = cc.register(items)
        print(f'revision {rev}: total {len(cc.items)}')
        if len(added) > 0:
            print('added')
            for r in sorted(added, key=lambda r: r.uid):
                # TODO link to bookmark
                # TODO actually chould even generate html here...
                # TODO highlight interesting users
                # TODO how to track which ones were already notified??
                # TODO I guess keep latest revision in a state??
                BB = f""">>>>>>>>>
{r.title}  {r.link}
{tabulate(r.description)}
tags: {' '.join(r.tags)}
{r.when} by {r.user} {r.blink}
<<<<<<<<<
"""
                print(BB)
                
# TODO search is a bit of flaky: initially I was getting
# so like exact opposites
# I guess removed links are basically not interesting, so we want to track whatever new was added
"""
revision 7da4116->d20b6d2: total 755, removed 26, added 24
removed
  /u:haschek/b:3e0b2d8abd54
  /u:haschek/b:44216e702952
  /u:haschek/b:5eddb0b9e263
  /u:haschek/b:7e7fd2b28d2d
  /u:haschek/b:b22ce37dc312
  /u:haschek/b:b61abb30a538
  /u:haschek/b:be87ff513cdc
  /u:haschek/b:df57fe3f09c1
  /u:iansari/b:605d5d8c7317
  /u:knodalyte/b:b3004e738486
  /u:markgould13/b:2ff621e1e56a
  /u:markgould13/b:b2b567ec2fc5
  /u:markgould13/b:b418cac6fd5f
  /u:matthiasfromm/b:d18d9cfdec80
  /u:meryn/b:85ebfd3313b5
  /u:monkeymagic/b:fe89ea36c564
  /u:myheartforever/b:5e56382c5b0d
  /u:nicknikolov/b:767760a5acc7
  /u:nicknikolov/b:9d286a135711
  /u:patrickdidomenico/b:41052e32ec91
  /u:piersyoung/b:6c743acbca96
  /u:pkeane/b:131df4ac5cdd
  /u:tsuomela/b:2eca7aef93e0
  /u:tsuomela/b:7e6234f2eb6d
  /u:urbansheep/b:89f19e7b1b37
  /u:urbansheep/b:e7a9c4876ab0
added
  /u:Juha_Antero/b:24990796d9b6
  /u:caravanstudios/b:89f7960395bb
  /u:caravanstudios/b:8ea2678f4d81
  /u:donturn/b:6f49a2856a94
  /u:donturn/b:d49a6b74f59a
  /u:donturn/b:dbef3c7a3a24
  /u:haschek/b:5f44f32f3e02
  /u:haschek/b:67e976500406
  /u:haschek/b:8ec58ce0878d
  /u:haschek/b:b09c39051fc7
  /u:jesusgollonet/b:60ed1d936ffa
  /u:jimmcgee/b:820ddfbacc67
  /u:knodalyte/b:2a4ac5d996ca
  /u:knodalyte/b:3ed1d2c0665d
  /u:markgould13/b:0cc7f31b9e45
  /u:markgould13/b:d948bf01bb70
  /u:meryn/b:47fea148dd0e
  /u:meryn/b:6adb69f1c2a6
  /u:pkeane/b:46ac99e52998
  /u:pkeane/b:ad84f52d63d1
  /u:socialreporter/b:d719c9fda3ee
  /u:tonyyet/b:083a71cc8576
  /u:tonyyet/b:40151ce7a328
  /u:tsuomela/b:89ad85e286ce
revision d20b6d2->81811f6: total 757, removed 24, added 26
removed
  /u:Juha_Antero/b:24990796d9b6
  /u:caravanstudios/b:89f7960395bb
  /u:caravanstudios/b:8ea2678f4d81
  /u:donturn/b:6f49a2856a94
  /u:donturn/b:d49a6b74f59a
  /u:donturn/b:dbef3c7a3a24
  /u:haschek/b:5f44f32f3e02
  /u:haschek/b:67e976500406
  /u:haschek/b:8ec58ce0878d
  /u:haschek/b:b09c39051fc7
  /u:jesusgollonet/b:60ed1d936ffa
  /u:jimmcgee/b:820ddfbacc67
  /u:knodalyte/b:2a4ac5d996ca
  /u:knodalyte/b:3ed1d2c0665d
  /u:markgould13/b:0cc7f31b9e45
  /u:markgould13/b:d948bf01bb70
  /u:meryn/b:47fea148dd0e
  /u:meryn/b:6adb69f1c2a6
  /u:pkeane/b:46ac99e52998
  /u:pkeane/b:ad84f52d63d1
  /u:socialreporter/b:d719c9fda3ee
  /u:tonyyet/b:083a71cc8576
  /u:tonyyet/b:40151ce7a328
  /u:tsuomela/b:89ad85e286ce
added
  /u:haschek/b:3e0b2d8abd54
  /u:haschek/b:44216e702952
  /u:haschek/b:5eddb0b9e263
  /u:haschek/b:7e7fd2b28d2d
  /u:haschek/b:b22ce37dc312
  /u:haschek/b:b61abb30a538
  /u:haschek/b:be87ff513cdc
  /u:haschek/b:df57fe3f09c1
  /u:iansari/b:605d5d8c7317
  /u:knodalyte/b:b3004e738486
  /u:markgould13/b:2ff621e1e56a
  /u:markgould13/b:b2b567ec2fc5
  /u:markgould13/b:b418cac6fd5f
  /u:matthiasfromm/b:d18d9cfdec80
  /u:meryn/b:85ebfd3313b5
  /u:monkeymagic/b:fe89ea36c564
  /u:myheartforever/b:5e56382c5b0d
  /u:nicknikolov/b:767760a5acc7
  /u:nicknikolov/b:9d286a135711
  /u:patrickdidomenico/b:41052e32ec91
  /u:piersyoung/b:6c743acbca96
  /u:pkeane/b:131df4ac5cdd
  /u:tsuomela/b:2eca7aef93e0
  /u:tsuomela/b:7e6234f2eb6d
  /u:urbansheep/b:89f19e7b1b37
  /u:urbansheep/b:e7a9c4876ab0
"""

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('repo')
    args = parser.parse_args()
    repo = args.repo
    print_all_diffs(repo)


if __name__ == '__main__':
    main()
