#!/usr/bin/env python
from argparse import ArgumentParser
from pathlib import Path

from common import get_quotes


def get_args():
    parser = ArgumentParser(
        prog='check_quotes',
        description='Check Literature Clock quote files in yaml format.',
    )
    parser.add_argument('src', help='source yaml', type=Path)

    args = parser.parse_args()

    return args.src


if __name__ == '__main__':
    src = get_args()
    quotes = get_quotes(src, collect_errors=True)
    print("all quotes ok")
