#!/bin/sh
BASEDIR=$(dirname "$(realpath "$0")")
CLOCK_IS_TICKING="$BASEDIR/clockisticking"

# see what image is shown at the moment
current=$(cat "$CLOCK_IS_TICKING" 2>/dev/null)

# only if a filename is in the clockisticking file, then continue 
if [ -n "$current" ]; then

	# find the matching image with metadata
	currentCredit=$(echo "$current" | sed 's/.png//')_credits.png
	currentCredit=$(echo "$currentCredit" | sed 's/images/images\/metadata/')

	# show the image with metdata
	eips -g "$currentCredit"

fi

# wait for right button and restart
/usr/bin/waitforkey 191 && "$0" &
