#!/usr/bin/env python3
# requirements:  libcairo2-dev pkg-config python3-dev
from cairocffi import cairo
# import pango
import gi  # pygobject
gi.require_version('Pango', '1.0')
gi.require_version('PangoCairo', '1.0')
from gi.repository import Pango, PangoCairo

width, height = 800, 600

surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
context = cairo.Context(surface)
context.rectangle(0, 0, width, height)
# Darkblue
context.set_source_rgb(0,0,0.5)
context.fill()

layout = PangoCairo.create_layout(context)
layout.set_wrap(pango.PANGO_WRAP_WORD)
