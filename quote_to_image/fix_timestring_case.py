#!/usr/bin/env python
from argparse import ArgumentParser
from pathlib import Path

from common import get_quotes, write_yaml


def get_args():
    parser = ArgumentParser(
        prog='fix_timestrings',
        description='Fix upper/lowercase errors in Literature Clock quote files in yaml format.',
    )
    parser.add_argument('src', help='source yaml', type=Path)

    args = parser.parse_args()

    return args.src


if __name__ == '__main__':
    src = get_args()
    quotes = get_quotes(src, fix_timestring_case=True)

    write_yaml(quotes, f"{src}.fixed")
