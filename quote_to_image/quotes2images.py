#!/usr/bin/env python3
from argparse import ArgumentParser
from collections import defaultdict
from pathlib import Path
import yaml
import cairocffi
import pangocffi
import pangocairocffi
from pangocffi import units_from_double, units_to_double


def get_arguments():
    parser = ArgumentParser(
        prog='quotes2images',
        description='Generate png images from literature quotes in yaml format.',
    )
    parser.add_argument('src', help='source file containing quotes in yaml format', type=Path)
    parser.add_argument('dst', help='destination folder', type=Path)
    parser.add_argument('-text_font', help='font for regular text', type=str, default="Sans")
    parser.add_argument('-meta_font', help='font for metadata', type=str, default="")
    parser.add_argument('-width', help='image width', type=int, default=600)
    parser.add_argument('-height', help='image height', type=int, default=600)

    parsed = parser.parse_args()
    return vars(parsed)


class Quote2Image:
    def __init__(self, width: int, height: int, borders=(0, 0, 0, 0), font="Sans", font_meta=""):

        self.font = font
        self.font_meta = font_meta
        self.borders = borders

        self.surface = cairocffi.ImageSurface(cairocffi.FORMAT_ARGB32, width, height)
        self.context = cairocffi.Context(self.surface)

    def add_quote(self, quote: str, timestr: str):
        raise NotImplementedError()

    def add_annotations(self, title: str, author: str):
        raise NotImplementedError()


def get_quotes(src_file):
    with open(src_file, newline='\n', encoding="utf8") as yaml_file:
        result = yaml.safe_load(yaml_file)

    return result


class TimeCounter:
    """ Counts how often a time has occurred """
    def __init__(self):
        self.recorded = defaultdict(lambda: 0)

    def count(self, timestr):
        minute = self.minute_from_timestr(timestr)
        self.recorded[minute] += 1
        return self.recorded[minute]

    @staticmethod
    def minute_from_timestr(timestr: str):
        hours, minutes = timestr.split(':')
        return int(hours) * 60 + int(minutes)

    @staticmethod
    def minute_to_timestr(minute: int):
        h, m = divmod(minute, 60)
        return f"{h:02d}:{m:02d}"

    def get_missing(self):
        return [self.minute_to_timestr(minute) for minute in range(0, 60 * 24 - 1) if self.recorded[minute] == 0]


if __name__ == "__main__":
    args = get_arguments()

    # prepare destination folders
    dst = args['dst']
    meta_dst = dst / 'metadata'
    for p in [dst, meta_dst]:
        p.mkdir(parents=True, exist_ok=True)

    counter = TimeCounter()
    quotes = get_quotes(args['src'])

    for data in quotes:
        current_time: str = data['time']
        count = counter.count(current_time)
        basename = f"quote_{current_time.replace(':', '')}_{count - 1}"
        q2i = Quote2Image(args['width'], args['height'], args['text_font'], args['meta_font'])

        q2i.add_quote(data['quote'], data['timestring'])
        q2i.surface.write_to_png(str(dst / f'{basename}.png'))

        q2i.add_annotations(data['title'], data['author'])
        q2i.surface.write_to_png(str(meta_dst / f'{basename}_credits.png'))

    missing = counter.get_missing()
    if missing:
        print(f"{len(missing)} missing quotes: {missing}")
