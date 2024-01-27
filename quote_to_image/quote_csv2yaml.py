#!/usr/bin/env python
from argparse import ArgumentParser
from collections import defaultdict
from csv import DictReader
from pathlib import Path
import sys

from common import write_yaml


def get_args():
    parser = ArgumentParser(
        prog='quote_csv2yaml',
        description='Convert Literature Clock quotes from csv to yaml format.',
    )
    parser.add_argument('src', help='source csv', type=Path)
    parser.add_argument('dst', help="destination yaml (if omitted the source's .csv ending will be replaced with .yaml)",
                        nargs='?', type=Path)

    args = parser.parse_args()
    if args.dst is None:
        if args.src.suffix != '.csv':
            print("Error: cannot calculate dst (src has no .csv ending)")
            sys.exit(1)
        args.dst = args.src.with_suffix('.yaml')

    return args.src, args.dst


def read_csv(src_file):
    with open(src_file, newline='\n', encoding="utf8") as csvfile:
        reader = DictReader(csvfile, delimiter='|')
        result = list(reader)

    return result


if __name__ == '__main__':
    src, dst = get_args()
    quotes = read_csv(src)

    # transform from simple list of dicts to a dict with time as primary key and a list of quotes as elements
    quotes_dict = defaultdict(lambda: [])
    for quote in quotes:
        time = quote.pop('time')
        quotes_dict[time].append(quote)

    write_yaml(dict(quotes_dict), dst)
