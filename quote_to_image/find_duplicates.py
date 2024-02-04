#!/usr/bin/env python
from argparse import ArgumentParser
from collections import defaultdict
from difflib import SequenceMatcher
from pathlib import Path

from common import get_quotes, write_yaml


def get_args():
    parser = ArgumentParser(
        prog='find_duplicates',
        description='Find duplicates in Literature Clock quote file in yaml format.',
    )
    parser.add_argument('src', help='source yaml', type=Path)

    args = parser.parse_args()

    return args.src


if __name__ == '__main__':
    src = get_args()
    quotes = get_quotes(src, fix_timestring_case=True)
    duplicates = defaultdict(lambda: [])

    for time, records in quotes.items():
        seen_quotes = []
        for record in records:
            for seen in seen_quotes:
                for attr in ['timestring', 'author', 'title']:
                    if seen[attr] != record[attr]:
                        break
                else:
                    ratio = SequenceMatcher(None, record['quote'], seen['quote']).ratio()
                    if ratio > 0.5:
                        duplicates[time].append((record, seen))
            seen_quotes.append(record)

    count = 0
    for time, dups in duplicates.items():
        print(f"{time}:")
        for duplicate in dups:
            count += 1
            print(f"  {duplicate[0]}")
            print(f"  {duplicate[1]}")
            input("ENTER to continue")

    print(f"found {count} duplicates")
    # write_yaml(quotes, f"{src}.fixed")
