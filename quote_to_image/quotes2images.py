#!/usr/bin/env python3
import html
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
    parser.add_argument('-height', help='image height', type=int, default=800)

    parsed = parser.parse_args()
    return vars(parsed)


class Quote2Image:
    PRECISION = 0.5  # precision of font size search

    def __init__(self, width: int, height: int, font="Sans", font_meta="", annotation_height=100):
        self.width = width
        self.height = height
        self.font = font
        self.font_meta = font_meta
        self.annotation_height = annotation_height

        self.surface = None
        self.context = None
        self.layout = None

    def _init_data(self):
        self.surface = cairocffi.ImageSurface(cairocffi.FORMAT_ARGB32, self.width, self.height)

        self.context = cairocffi.Context(self.surface)
        # fill background
        with self.context:
            self.context.set_source_rgb(1, 1, 1)  # white
            self.context.paint()

        self.layout = pangocairocffi.create_layout(self.context)
        self.layout.wrap = pangocffi.WrapMode.WORD
        self.layout.width = units_from_double(self.width)

    def add_quote(self, quote: str, timestr: str):
        self._init_data()
        length = len(quote)
        quote = html.escape(quote, quote=False)
        quote = quote.replace(timestr, f"<b>{timestr}</b>")

        font_size = self._find_font_size(quote, length)
        self.layout.apply_markup(self._get_markup(quote, font_size))
        pangocairocffi.show_layout(self.context, self.layout)

    def add_annotations(self, title: str, author: str):
        raise NotImplementedError()

    def _find_font_size(self, quote, length):
        # TODO: use a more advanced search approach
        max_height = self.height - self.annotation_height
        font_size = self._predict_font_size(length)
        height = self._get_height(quote, font_size)

        step = self.PRECISION if height < max_height else -self.PRECISION
        while True:
            font_size += step
            height = self._get_height(quote, font_size)
            if step < 0 and height <= max_height:
                return font_size
            if step > 0 and height > max_height:
                return font_size - step

    def _get_height(self, quote, font_size):
        self.layout.apply_markup(self._get_markup(quote, font_size))
        _, ext = self.layout.get_extents()
        return units_to_double(ext.height)

    def _get_markup(self, quote, font_size):
        return f"<span font_desc='{self.font} {font_size}'>{quote}</span>"

    @staticmethod
    def _predict_font_size(_length):
        # TODO: make a good prediction by learning from previous attempts
        return 40


def get_quotes(src_file):
    with open(src_file, newline='\n', encoding="utf8") as yaml_file:
        result = yaml.safe_load(yaml_file)

    expected_keys = ['author', 'quote', 'time', 'timestring', 'title']
    for dataset in result:
        for key in expected_keys:
            if key not in dataset:
                raise Exception(f"Error: missing key in {dataset} (expected {expected_keys})")

        timestring, quote = dataset['timestring'], dataset['quote']
        if timestring not in quote:
            raise Exception(f"Error: timestring '{timestring}' not found in quote '{quote}'")

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
    q2i = Quote2Image(args['width'], args['height'], args['text_font'], args['meta_font'])

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

        q2i.add_quote(data['quote'], data['timestring'])
        q2i.surface.write_to_png(str(dst / f'{basename}.png'))

        # q2i.add_annotations(data['title'], data['author'])
        # q2i.surface.write_to_png(str(meta_dst / f'{basename}_credits.png'))

    missing = counter.get_missing()
    if missing:
        print(f"{len(missing)} missing quotes: {missing}")
