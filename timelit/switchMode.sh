#!/bin/sh

BASEDIR=$(dirname "$(realpath "$0")")
CLOCK_IS_TICKING="$BASEDIR/clockisticking"

CURRENT="$BASEDIR/images"
OTHER="$BASEDIR/images_other"
SUFFIX=".switching"

while true; do
    # wait for left button
    /usr/bin/waitforkey 104

    # if the Kindle is not being used as clock, then just quit
    test -f "$CLOCK_IS_TICKING" || exit

    mv "$CURRENT" "$CURRENT$SUFFIX"
    mv "$OTHER" "$OTHER$SUFFIX"
    mv "$CURRENT$SUFFIX" "$OTHER"
    mv "$OTHER$SUFFIX" "$CURRENT"

    # see what image is shown at the moment
    current=$(cat "$CLOCK_IS_TICKING" 2>/dev/null)
    if [ -n "$current" ]; then
      eips -g "$current"
    fi
done
