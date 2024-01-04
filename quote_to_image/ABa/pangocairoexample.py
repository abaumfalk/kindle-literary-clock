#!/usr/bin/python3
#-*- coding:utf8 -*-

import cairo
import gi
gi.require_version('Pango', '1.0')
gi.require_version('PangoCairo', '1.0')
from gi.repository import Pango, PangoCairo

surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 600, 100)
context = cairo.Context(surface)
layout = PangoCairo.create_layout(context)
layout.set_font_description(Pango.font_description_from_string('Serif Normal 12'))
layout.set_alignment(Pango.Alignment.CENTER)
layout.set_markup('Normal <b>Bold</b> <i>Italic</i> <small>Small</small> <big>Big</big>', -1)

# centering
width, height = surface.get_width(), surface.get_height()
_, extents = layout.get_pixel_extents()
tw, th = extents.width, extents.height
context.move_to(width/2 - tw/2, height/2 - th/2)

PangoCairo.show_layout(context, layout)
surface.write_to_png('pangocairo.png')
