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

DEFAULT_MARGIN = 26
ANNOTATION_MARGIN = 100
CREDIT_FONT_SIZE = 18


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
    parser.add_argument('-margin', help='margin around text in pixels', type=int, default=DEFAULT_MARGIN)

    parsed = parser.parse_args()
    return vars(parsed)


class Quote2Image:
    PRECISION = 0.5  # precision of font size search

    def __init__(self, width: int, height: int, font="Sans", margin=DEFAULT_MARGIN,
                 meta_font='', meta_margin=ANNOTATION_MARGIN, meta_width_ratio=0.7):
        self.width = width
        self.height = height
        self.font = font
        self.meta_font = meta_font
        self.margin = margin
        self.meta_margin = meta_margin
        self.meta_width_ratio = meta_width_ratio

        self.surface = None

    def add_quote(self, quote: str, timestr: str):
        self.surface = cairocffi.ImageSurface(cairocffi.FORMAT_ARGB32, self.width, self.height)

        context = cairocffi.Context(self.surface)
        # fill background
        with context:
            context.set_source_rgb(1, 1, 1)  # white
            context.paint()

        layout = pangocairocffi.create_layout(context)
        layout.wrap = pangocffi.WrapMode.WORD
        layout.width = units_from_double(self.width - 2 * self.margin)

        length = len(quote)
        quote = html.escape(quote, quote=False)
        quote = quote.replace(timestr, f"<b>{timestr}</b>")

        font_size = self._find_font_size(layout, quote, length)
        layout.apply_markup(self._get_markup(quote, font_size))

        context.move_to(self.margin, self.margin)
        pangocairocffi.show_layout(context, layout)

    def _find_font_size(self, layout, quote, length):
        # TODO: use a more advanced search approach
        max_height = self.height - self.margin - self.meta_margin
        max_width = self.width - 2 * self.margin
        font_size = self._predict_font_size(length)
        height, width = self._get_extents(layout, quote, font_size)

        step = self.PRECISION if height < max_height and width < max_width else -self.PRECISION
        while True:
            font_size += step
            height, width = self._get_extents(layout, quote, font_size)
            if step < 0 and height <= max_height and width <= max_width:
                return font_size
            if step > 0 and (height > max_height or width > max_width):
                return font_size - step

    def _get_extents(self, layout, quote, font_size):
        layout.apply_markup(self._get_markup(quote, font_size))
        _, ext = layout.get_extents()
        return units_to_double(ext.height), units_to_double(ext.width)

    def _get_markup(self, quote, font_size):
        return f"<span font_desc='{self.font} {font_size}'>{quote}</span>"

    @staticmethod
    def _predict_font_size(_length):
        # TODO: make a good prediction by learning from previous attempts
        return 40

    def add_annotations(self, title, author):
        title = html.escape(title)
        author = html.escape(author)

        context = cairocffi.Context(self.surface)

        layout = pangocairocffi.create_layout(context)
        layout.wrap = pangocffi.WrapMode.WORD
        layout.width = units_from_double(self.width * self.meta_width_ratio)
        layout.alignment = pangocffi.Alignment.RIGHT

        layout.apply_markup(f'<span font_desc="{CREDIT_FONT_SIZE} italic">—{title}, {author}</span>')
        _, ext = layout.get_extents()

        pos_x = self.width * (1 - self.meta_width_ratio) - self.margin
        pos_y = self.height - self.margin - units_to_double(ext.height)
        context.move_to(pos_x, pos_y)
        pangocairocffi.show_layout(context, layout)


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
    q2i = Quote2Image(args['width'], args['height'], font=args['text_font'], meta_font=args['meta_font'])

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

        q2i.add_annotations(data['title'], data['author'])
        q2i.surface.write_to_png(str(meta_dst / f'{basename}_credits.png'))

    missing = counter.get_missing()
    if missing:
        print(f"{len(missing)} missing quotes: {missing}")
