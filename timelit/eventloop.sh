#!/bin/sh
set -e

BASEDIR=$(dirname "$(realpath "$0")")
CLOCK_IS_TICKING="$BASEDIR/clockisticking"


timeZone() {
	TZFILE="$BASEDIR/TZ"
	CURRENT=$(cat "$TZFILE")
	NEW=$((CURRENT+$1))
	echo "$NEW" > "$TZFILE"

	"$BASEDIR/timelit.sh"
}

showMeta() {
    if [ -n "$current" ]; then
        # find the matching image with metadata
        currentCredit=$(echo "$current" | sed 's/.png//')_credits.png
        currentCredit=$(echo "$currentCredit" | sed 's/images/images\/metadata/')

        # show the image with metadata
        eips -g "$currentCredit"
    fi
}

switchMode() {
	CURRENT="$BASEDIR/images"
	OTHER="$BASEDIR/images_other"
	SUFFIX=".switching"
	if [ -n "$OTHER" ]; then
		mv "$CURRENT" "$CURRENT$SUFFIX"
		mv "$OTHER" "$OTHER$SUFFIX"
		mv "$CURRENT$SUFFIX" "$OTHER"
		mv "$OTHER$SUFFIX" "$CURRENT"

		if [ -n "$current" ]; then
		  eips -g "$current"
		fi
	fi
}


while true; do
    KEY=$(/usr/bin/waitforkey)

    # if the Kindle is not being used as clock, then just quit
    test -f "$CLOCK_IS_TICKING" || exit

    # see what image is shown at the moment
    current=$(cat "$CLOCK_IS_TICKING" 2>/dev/null)

    case "$KEY" in
		"191 1")  # right lower >
			showMeta
			;;
		"109 1")  # right upper <
			timeZone -1
			;;
		"104 1")  # left lower >
			switchMode
			;;
		"193 1")  # left upper >
			timeZone 1
			;;
	esac
done
