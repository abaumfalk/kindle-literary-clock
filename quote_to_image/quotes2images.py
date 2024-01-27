#!/usr/bin/env python3
import html
from argparse import ArgumentParser
from pathlib import Path
import cairocffi
import pangocffi
import pangocairocffi
from pangocffi import units_from_double, units_to_double

from common import get_quotes, minute_to_timestr

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
    FONT_SIZE_PRECISION = 0.5  # precision of font size search
    FONT_SIZE_START = 40
    FONT_SIZE_STEPS = 3  # determines the initial step size of the search algorithm

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

        self.iterations = 0
        self.quotes = 0

    def add_quote(self, quote: str, timestr: str):
        self.quotes += 1
        self.surface = cairocffi.ImageSurface(cairocffi.FORMAT_ARGB32, self.width, self.height)

        context = cairocffi.Context(self.surface)
        # fill background
        with context:
            context.set_source_rgb(1, 1, 1)  # white
            context.paint()

        layout = pangocairocffi.create_layout(context)
        layout.wrap = pangocffi.WrapMode.WORD
        layout.width = units_from_double(self.width - 2 * self.margin)

        quote_len = len(quote)
        quote = html.escape(quote, quote=False)
        quote = quote.replace(timestr, f"<span foreground='black' font_desc='bold'>{timestr}</span>")

        font_size = self._find_font_size(layout, quote, quote_len)
        layout.apply_markup(self._get_markup(quote, font_size))

        context.move_to(self.margin, self.margin)
        pangocairocffi.show_layout(context, layout)

    def _find_font_size(self, layout, quote, quote_len):
        max_height = self.height - self.margin - self.meta_margin
        max_width = self.width - 2 * self.margin

        # the initial guess decides if we iterate upwards or downwards
        font_size = self._predict_font_size(quote_len)
        height, width = self._get_extents(layout, quote, font_size)

        step = self._get_step(max_height - height)
        best = None if height > max_height or width > max_width else font_size

        while abs(step) >= self.FONT_SIZE_PRECISION:
            font_size += step
            while True:
                height, width = self._get_extents(layout, quote, font_size)
                delta = abs(height - max_height)
                if height > max_height or width > max_width:
                    if step > 0:
                        font_size -= step
                        break
                    else:
                        font_size += step
                else:
                    best = font_size
                    if step > 0:
                        font_size += step
                    else:
                        font_size -= step
                        break

            # overstepped
            step = self._get_step(delta, step)

        return best

    def _predict_font_size(self, _length):
        # TODO: make a good prediction by learning from previous attempts
        return self.FONT_SIZE_START

    def _get_step(self, delta, step=None):
        # TODO: use current delta to find a better step size
        if step is None:
            return self.FONT_SIZE_PRECISION * 2 ** self.FONT_SIZE_STEPS * (1 if delta > 0 else -1)
        return step / 2

    def _get_extents(self, layout, quote, font_size):
        self.iterations += 1
        layout.apply_markup(self._get_markup(quote, font_size))
        _, ext = layout.get_extents()
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

        layout.apply_markup(f'<span font_desc="{CREDIT_FONT_SIZE} italic">—{title}, {author}</span>')
        _, ext = layout.get_extents()

        pos_x = self.width * (1 - self.meta_width_ratio) - self.margin
        pos_y = self.height - self.margin - units_to_double(ext.height)
        context.move_to(pos_x, pos_y)
        pangocairocffi.show_layout(context, layout)

    def __del__(self):
        print(f"quotes: {self.quotes}")
        print(f"iterations: {self.iterations}")
        print(f"iterations per quote: {self.iterations / self.quotes}")


if __name__ == "__main__":
    args = get_arguments()
    q2i = Quote2Image(args['width'], args['height'], font=args['text_font'], meta_font=args['meta_font'])

    # prepare destination folders
    dst = args['dst']
    meta_dst = dst / 'metadata'
    for p in [dst, meta_dst]:
        p.mkdir(parents=True, exist_ok=True)

    quotes_dict = get_quotes(args['src'])

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
            basename = f"quote_{current_time.replace(':', '')}_{count - 1}"

            q2i.add_quote(data['quote'], data['timestring'])
            q2i.surface.write_to_png(str(dst / f'{basename}.png'))

            q2i.add_annotations(data['title'], data['author'])
            q2i.surface.write_to_png(str(meta_dst / f'{basename}_credits.png'))
        print()

    if missing:
        print(f"{len(missing)} missing quotes: {missing}")
