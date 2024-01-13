#!/usr/bin/env python
from argparse import ArgumentParser
from csv import DictReader
from pathlib import Path
import sys

import yaml


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


class Quote(str):
    pass


def write_yaml(content, dst_file):
    # mark quotes
    def mark_quote(d):
        d['quote'] = Quote(d['quote'])
        return d

    content = [mark_quote(item) for item in content]

    def quote_presenter(dumper, data):
        return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='>')

    yaml.add_representer(Quote, quote_presenter)

    with open(dst_file, 'w') as yaml_file:
        yaml.dump(content, yaml_file, allow_unicode=True)


if __name__ == '__main__':
    src, dst = get_args()
    quotes = read_csv(src)
    write_yaml(quotes, dst)
