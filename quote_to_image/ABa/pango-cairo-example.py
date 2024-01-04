#!/usr/bin/python

######################################################################
#  An example of how to draw text with pangocairo.
#
#  This script is in the public domain
#
#  Dov Grobgeld <dov.grobgeld@gmail.com>
#  2021-01-12 Tue
######################################################################

import cairocffi as cairo
import pangocairocffi as pangocairo
import pangocffi as pango

WIDTH,HEIGHT=256,256
surface = cairo.ImageSurface (cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
cr = cairo.Context (surface)

cr.rectangle(0,0,WIDTH,HEIGHT)
# Darkblue
cr.set_source_rgb(0,0,0.5)
cr.fill()

PANGO_SCALE = pango.units_from_double(1)

layout = pangocairo.create_layout(cr)
desc = pango.FontDescription()
desc.set_family('Serif')
desc.set_size(48*PANGO_SCALE)
layout.set_font_description(desc)

layout.set_markup('A <b>bold</b>\nidea')
layout.set_alignment(pango.Alignment.CENTER)
ink_box,log_box = layout.get_extents()

text_width,text_height = (1.0*log_box.width/PANGO_SCALE,
                          1.0*log_box.height/PANGO_SCALE)
cr.move_to(WIDTH/2-text_width/2, HEIGHT/2-text_height/2)
cr.set_source_rgb(1,1,1)
pangocairo.show_layout(cr,layout)
cr.fill()

surface.write_to_png ("example.png")
