#!/usr/bin/env python3
import html
import re
from argparse import ArgumentParser
from sortedcontainers import SortedDict
from pathlib import Path
import cairocffi
import pangocffi
import pangocairocffi
from pangocffi import units_from_double, units_to_double

from common import get_quotes, minute_to_timestr

DEFAULT_MARGIN = 26
ANNOTATION_MARGIN = 100
CREDIT_FONT_SIZE = 18
FONT_SIZE_MIN = 19
FONT_SIZE_MAX = None


def get_arguments():
    parser = ArgumentParser(
        prog='quotes2images',
        description='Generate png images from literature quotes in yaml format.',
    )
    parser.add_argument('src', help='source file containing quotes in yaml format', type=Path)
    parser.add_argument('dst', help='destination folder', type=Path)
    parser.add_argument('-text_font', help='font for regular text', type=str, default="")
    parser.add_argument('-meta_font', help='font for metadata', type=str, default="italic bold")
    parser.add_argument('-width', help='image width', type=int, default=600)
    parser.add_argument('-height', help='image height', type=int, default=800)
    parser.add_argument('-margin', help='margin around text in pixels', type=int, default=DEFAULT_MARGIN)
    parser.add_argument('--statistics', help='collect and show statistics', action='store_true')

    parsed = parser.parse_args()
    return vars(parsed)


class Quote2ImageException(Exception):
    pass


class Quote2Image:
    FONT_SIZE_PRECISION = 0.5  # precision of font size search
    FONT_SIZE_START = 40
    FONT_SIZE_STEPS = 3  # determines the initial step size of the search algorithm
    MAX_STEP = FONT_SIZE_PRECISION * 2 ** FONT_SIZE_STEPS

    def __init__(self, width: int, height: int, font="Sans", margin=DEFAULT_MARGIN,
                 meta_font='', meta_margin=ANNOTATION_MARGIN, meta_width_ratio=0.7):
        self.width = width
        self.height = height
        self.font = font
        self.meta_font = meta_font
        self.margin = margin
        self.meta_margin = meta_margin
        self.meta_width_ratio = meta_width_ratio

        self.layout = None
        self.surface = None

        self.iterations = {}
        self.quote_len = None
        self.quote = None
        self.timestr = None
        self.font_size = None

    def add_quote(self, quote: str, timestr: str):
        self.quote = quote
        self.timestr = timestr
        self.iterations = {}
        self.surface = cairocffi.ImageSurface(cairocffi.FORMAT_ARGB32, self.width, self.height)

        context = cairocffi.Context(self.surface)
        # fill background
        with context:
            context.set_source_rgb(1, 1, 1)  # white
            context.paint()

        self.layout = pangocairocffi.create_layout(context)
        self.layout.wrap = pangocffi.WrapMode.WORD
        self.layout.width = units_from_double(self.width - 2 * self.margin)

        self.quote = re.sub("<br\\s*(/)?>", '\n', self.quote)
        self.quote_len = len(quote)
        self.quote = self.quote.replace(timestr, f"<span foreground='black' font_desc='bold'>{timestr}</span>")

        self._find_font_size()
        self.layout.apply_markup(self._get_markup(self.quote, self.font_size))

        context.move_to(self.margin, self.margin)
        pangocairocffi.show_layout(context, self.layout)

    def _check_font_size(self, font_size, max_height, max_width):
        height, width = self._get_extents(font_size)
        return height <= max_height and width <= max_width

    def _find_font_size(self):
        max_height = self.height - self.margin - self.meta_margin
        max_width = self.width - 2 * self.margin
        iterations = {}

        # the initial guess decides if we iterate upwards or downwards
        font_size = self._predict_font_size()
        font_size_ok = self.iterations.setdefault(
            font_size, self._check_font_size(font_size, max_height, max_width))

        step = self.MAX_STEP * 1 if font_size_ok else -1
        best = font_size if font_size_ok else None

        while abs(step) >= self.FONT_SIZE_PRECISION:
            font_size += step
            while True:
                font_size_ok = self.iterations.setdefault(
                    font_size, self._check_font_size(font_size, max_height, max_width))
                if not font_size_ok:
                    if step > 0:
                        break
                else:
                    best = font_size
                    if step < 0:
                        break
                font_size += step

            # overstepped
            font_size -= step
            step /= 2

        if best is None:
            raise Quote2ImageException(f"Could not find font_size for {self.quote}")

        if FONT_SIZE_MIN and best < FONT_SIZE_MIN:
            raise Quote2ImageException(f"font size {best} too small for {self.quote}")

        if FONT_SIZE_MAX and best > FONT_SIZE_MAX:
            raise Quote2ImageException(f"font size {best} too large for {self.quote}")

        self.font_size = best

    def _predict_font_size(self):
        if self.width == 600 and self.height == 800:
            if self.quote_len < 50:
                return 70
            if self.quote_len < 100:
                return 50
            if self.quote_len < 200:
                return 40
            if self.quote_len < 400:
                return 30
            if self.quote_len < 600:
                return 25
            return 20
        return self.FONT_SIZE_START

    def _get_extents(self, font_size):
        self.layout.apply_markup(self._get_markup(self.quote, font_size))
        _, ext = self.layout.get_extents()
        return units_to_double(ext.height), units_to_double(ext.width)

    def _get_markup(self, quote, font_size):
        return f"<span foreground='grey' font_desc='{self.font} {font_size}'>{quote}</span>"

    def add_annotations(self, title, author):
        title = html.escape(title)
        author = html.escape(author)

        context = cairocffi.Context(self.surface)

        layout = pangocairocffi.create_layout(context)
        layout.wrap = pangocffi.WrapMode.WORD
        layout.width = units_from_double(self.width * self.meta_width_ratio)
        layout.alignment = pangocffi.Alignment.RIGHT

        layout.apply_markup(f'<span font_desc="{self.meta_font} {CREDIT_FONT_SIZE}">—{title}, {author}</span>')
        _, ext = layout.get_extents()

        pos_x = self.width * (1 - self.meta_width_ratio) - self.margin
        pos_y = self.height - self.margin - units_to_double(ext.height)
        context.move_to(pos_x, pos_y)
        pangocairocffi.show_layout(context, layout)


class Statistics:
    def __init__(self):
        self.iterations = 0
        self.statistics = []

    def add(self, q2i: Quote2Image, name):
        iter_count = len(q2i.iterations)
        self.statistics.append({
            'name': name,
            'timestr': q2i.timestr,
            'quote_start': f"{q2i.quote[0:15]}...",
            'quote_len': q2i.quote_len,
            'font_size': q2i.font_size,
            'iteration_count': count,
            'iterations': q2i.iterations,
        })
        self.iterations += iter_count

    def __del__(self):
        sort_key = 'font_size'
        print(f"statistics sorted by {sort_key}:")
        self.statistics = sorted(self.statistics, key=lambda x: x[sort_key])
        for record in self.statistics:
            print(record)

        print("\ncount of font sizes:")
        sizes = SortedDict()
        for record in self.statistics:
            font_size = record['font_size']
            sizes[font_size] = sizes.get(font_size, 0) + 1
        for s, c in sizes.items():
            print(f"{s}: {c}x")

        print("\nsummary:")
        quotes = len(self.statistics)
        print(f"  quotes: {quotes}")
        print(f"  iterations: {self.iterations}")
        if quotes > 0:
            print(f"  iterations per quote: {self.iterations / quotes}")


if __name__ == "__main__":
    args = get_arguments()

    # prepare destination folders
    dst = args['dst']
    meta_dst = dst / 'metadata'
    for p in [dst, meta_dst]:
        p.mkdir(parents=True, exist_ok=True)

    quotes_dict = get_quotes(args['src'])

    statistics = Statistics() if args['statistics'] else None

    missing = []
    for minute in range(0, 60 * 24):  # iterate through all minutes of the day
        current_time = minute_to_timestr(minute)
        print(f"{current_time}: ", end='')
        quotes = quotes_dict.get(current_time)

        if quotes is None:
            missing.append(current_time)
            print("missing!")
            continue

        for count, data in enumerate(quotes):
            print(".", end='', flush=True)
            basename = f"quote_{current_time.replace(':', '')}_{count}"

            q2i = Quote2Image(args['width'], args['height'], font=args['text_font'], meta_font=args['meta_font'])

            q2i.add_quote(data['quote'], data['timestring'])
            q2i.surface.write_to_png(str(dst / f'{basename}.png'))

            q2i.add_annotations(data['title'], data['author'])
            q2i.surface.write_to_png(str(meta_dst / f'{basename}_credits.png'))

            if statistics is not None:
                statistics.add(q2i, basename)

        print()

    if missing:
        print(f"{len(missing)} missing quotes: {missing}")
