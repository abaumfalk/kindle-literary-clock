#!/bin/sh

BASEDIR=$(dirname "$(realpath "$0")")
CLOCK_IS_TICKING="$BASEDIR/clockisticking"

CURRENT="$BASEDIR/images"
OTHER="$BASEDIR/images_other"
SUFFIX=".switching"

mv "$CURRENT" "$CURRENT$SUFFIX"
mv "$OTHER" "$OTHER$SUFFIX"
mv "$CURRENT$SUFFIX" "$OTHER"
mv "$OTHER$SUFFIX" "$CURRENT"

# see what image is shown at the moment
current=$(cat "$CLOCK_IS_TICKING" 2>/dev/null)
if [ -n "$current" ]; then
  eips -g "$current"
fi

# start waiting for new keystrokes
/usr/bin/waitforkey 104 && "$0" &
