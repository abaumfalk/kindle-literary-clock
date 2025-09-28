#!/usr/bin/env python
from argparse import ArgumentParser
from pathlib import Path

from common import get_quotes, minute_to_timestr


def get_args():
    parser = ArgumentParser(
        prog='check_quotes',
        description='Check Literature Clock quote files in yaml format.',
    )
    parser.add_argument('src', help='source yaml', type=Path)
    parser.add_argument('--statistics', help='show statistics', action='store_true')

    return vars(parser.parse_args())


if __name__ == '__main__':
    args = get_args()
    quotes = get_quotes(args['src'], collect_errors=True)
    print("all quotes ok")
    
    if args['statistics']:
        missing = []
        for minute in range(0, 24 * 60):  # iterate through given minutes of the day
            current_time = minute_to_timestr(minute)
            count = len(quotes.get(current_time, []))
            if count == 0:
                missing.append(current_time)
            print(f"{current_time}: {count} quotes")
            
        if missing:
            print(f"missing: {missing})")


