#!/bin/sh
BASEDIR=$(dirname "$(realpath "$0")")
CLOCK_IS_TICKING="$BASEDIR/clockisticking"

# if the Kindle is not being used as clock, then just quit
test -f "$CLOCK_IS_TICKING" || exit

# find the current minute of the day
# Note: the timezone can be adjusted by adding e.g. UMT+2 to the TZ file in BASEDIR
MinuteOTheDay="$(env TZ=$(cat "$BASEDIR/TZ" 2>/dev/null) date -R +"%H%M")";

# check if there is at least one image for this minute 
lines="$(find "$BASEDIR/images/quote_$MinuteOTheDay"* 2>/dev/null | wc -l)"
if [ "$lines" -eq 0 ]; then
	echo "no images found for $MinuteOTheDay"
	exit
else
	echo "$lines files found for $MinuteOTheDay"
fi

# randomly pick a png file for that minute (since we have multiple for some minutes)
ThisMinuteImage=$( find "$BASEDIR/images/quote_$MinuteOTheDay"* 2>/dev/null | python -c "import sys; import random; print(''.join(random.sample(sys.stdin.readlines(), int(sys.argv[1]))).rstrip())" 1)

echo "$ThisMinuteImage" > "$CLOCK_IS_TICKING"

# clear the screen every hour to avoid ghosting
minute=$(printf "%s" "$MinuteOTheDay" | tail -c 2)
if [ "$minute" = "00" ]; then 
	eips -c
fi

# show that image
eips -g "$ThisMinuteImage"
