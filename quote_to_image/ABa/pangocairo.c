/*
In working with Pango I found an oddity that I do not understand.
It may be a bug, or it might just be my misunderstanding.

As part of a table layout procedure for printing, my code wishes to find out the width of the longest word in a Pango layout, so it sets the width of the layout to 1, turns on word wrapping, and measures the width of the layout, something like this:

        pango_layout_set_width (layout, 1);
        pango_layout_set_wrap (layout, PANGO_WRAP_WORD);
        pango_layout_get_size (layout, &width, NULL);

Later on, the width of the table column might have been adjusted upward or downward for other reasons, so it renders it with PANGO_WRAP_WORD_CHAR to prevent overflowing the column boundary.  I was surprised to discover that, when the layout width is set to the same value returned by pango_layout_get_size(), this caused some words to wrap anyhow.

I'm enclosing a simple example program.  You can invoke it to measure the size of rendering "A string of text" with a width of
1 and word-wrapping, as above, e.g. showing input, output, and an ASCII rendering of the produced foo.pdf:

        # ./a.out "A string of text" 1 word
        size: width=47032
        extents: ink width=45416, logical width=47032
        pixel extents: ink width=45, logical width=46

        +------+
        |A     |
        |string|
        |of    |
        |text  |
        +------+

Then giving the exact width reported by this run, plus word-char,
yields:

        # ./a.out "A string of text" 47032 word-char
        size: width=36632
        extents: ink width=35112, logical width=36632
        pixel extents: ink width=35, logical width=36

        +-----+
        |A    |
        |strin|
        |g of |
        |text |
        +-----+

To get word-char to produce the results that I expect, I have to add 5208, which is the reported width of " ":

        # ./a.out "A string of text" 52240 word-char
        size: width=47032
        extents: ink width=45416, logical width=47032
        pixel extents: ink width=45, logical width=46

        +------+
        |A     |
        |string|
        |of    |
        |text  |
        +------+

Any guidance would be appreciated.  I can always add the width of a space myself, but I don't understand why it is necessary.

Here is my test program:
*/

#include <pango/pangocairo.h>
#include <cairo/cairo-pdf.h>
#include <cairo/cairo.h>
#include <stdlib.h>
#include <string.h>

int
main (int argc, char **argv)
{
  cairo_t *cr;
  char *filename;
  cairo_status_t status;
  cairo_surface_t *surface;
  PangoLayout *layout;
  PangoFontDescription *desc;
  PangoRectangle ink, logical;
  int width;

  if (argc != 4)
    {
      g_printerr ("Usage: pangocairo STRING WIDTH WRAP_MODE\n");
      return 1;
    }

  /* Create surface and clear to all-white. */
  surface = cairo_pdf_surface_create ("foo.pdf", 200, 200);
  cr = cairo_create (surface);
  cairo_set_source_rgb (cr, 1.0, 1.0, 1.0);
  cairo_paint (cr);

  /* Create Pango layout. */
  layout = pango_cairo_create_layout (cr);
  desc = pango_font_description_from_string ("Sans 12");
  pango_layout_set_font_description (layout, desc);
  pango_font_description_free (desc);
  pango_layout_set_text (layout, argv[1], -1);

  /* Set Pango options according to command line. */
  pango_layout_set_width (layout, atoi (argv[2]));
  if (!strcmp (argv[3], "word"))
    pango_layout_set_wrap (layout, PANGO_WRAP_WORD);
  else if (!strcmp (argv[3], "char"))
    pango_layout_set_wrap (layout, PANGO_WRAP_CHAR);
  else if (!strcmp (argv[3], "word-char"))
    pango_layout_set_wrap (layout, PANGO_WRAP_WORD_CHAR);
  else
    {
      g_printerr ("WRAP_MODE must be 'word' or 'char' or 'word-char'");
      return 1;
    }

  /* Draw layout. */
  cairo_set_source_rgb (cr, 0.0, 0.0, 0.0);
  cairo_move_to (cr, 0, 0);
  pango_cairo_show_layout (cr, layout);

  /* Print various sizes. */
  pango_layout_get_size (layout, &width, NULL);
  printf ("size: width=%d\n", width);

  pango_layout_get_extents (layout, &ink, &logical);
  printf ("extents: ink width=%d, logical width=%d\n",
          ink.width, logical.width);

  pango_layout_get_pixel_extents (layout, &ink, &logical);
  printf ("pixel extents: ink width=%d, logical width=%d\n",
          ink.width, logical.width);

  /* Clean up. */
  g_object_unref (layout);

  cairo_destroy (cr);

  cairo_surface_finish (surface);
  status = cairo_surface_status (surface);
  cairo_surface_destroy (surface);

  if (status != CAIRO_STATUS_SUCCESS)
    {
      g_printerr ("Could not save pdf to '%s'\n", filename);
      return 1;
    }

  return 0;
}

/*
--
Ben Pfaff
http://benpfaff.org
*/

/* EOF */
