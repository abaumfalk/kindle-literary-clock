#!/usr/bin/env python
from argparse import ArgumentParser
from pathlib import Path
import re

from common import write_yaml, get_quotes, minute_to_timestr


def get_args():
    parser = ArgumentParser(
        prog='merge_quotes',
        description='Merge Literature Clock quote files in yaml format.',
    )
    parser.add_argument('src1', help='source yaml', type=Path)
    parser.add_argument('src2', help='source yaml', type=Path)
    parser.add_argument('dst', help="destination yaml", type=Path)

    args = parser.parse_args()

    return args.src1, args.src2, args.dst


def normalize(s: str):
    # prepare quote for comparison
    # remove non-alphanumeric chars
    pattern = re.compile('[\W_]+')
    s = pattern.sub('', s)

    # make lowercase
    return s.lower()


def merge_quotes(qs1, qs2):
    for minute in range(0, 60 * 24):
        timestr = minute_to_timestr(minute)
        for q2 in qs2.get(timestr, []):
            text = normalize(q2['quote'])
            # check if already present
            for q1 in qs1.get(timestr, []):
                if text == normalize(q1['quote']):
                    break
            else:
                qs1.setdefault(timestr, []).append(q2)


if __name__ == '__main__':
    src1, src2, dst = get_args()
    quotes = get_quotes(src1)
    quotes2 = get_quotes(src2)

    merge_quotes(quotes, quotes2)

    write_yaml(quotes, dst)
