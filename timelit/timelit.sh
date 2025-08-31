#!/bin/sh
BASEDIR=$(dirname "$(realpath "$0")")
CLOCK_IS_TICKING="$BASEDIR/clockisticking"

# if the Kindle is not being used as clock, then just quit
test -f "$CLOCK_IS_TICKING" || exit

# find the current minute of the day
# Note: the timezone can be adjusted by an offset in the TZ file
OFFSET=$(cat "$BASEDIR/TZ")
TZ="UTC"
if [ "$OFFSET" -gt 0 ]; then
	TZ="$TIMEZONE+$OFFSET"
elif [ "$OFFSET" -lt 0 ]; then
	TZ="$TZ$OFFSET"
fi
MinuteOTheDay="$(env TZ=$TZ date -R +"%H%M")";

# check if there is at least one image for this minute 
lines="$(find "$BASEDIR/images/quote_$MinuteOTheDay"* 2>/dev/null | wc -l)"
if [ "$lines" -eq 0 ]; then
	echo "no images found for $MinuteOTheDay"
	exit
else
	echo "$lines files found for $MinuteOTheDay"
fi

# randomly pick a png file for that minute (since we have multiple for some minutes)
ThisMinuteImage=$( find "$BASEDIR/images/quote_$MinuteOTheDay"* 2>/dev/null | python -c "import sys; import random; print(random.sample(sys.stdin.readlines(), 1)[0].rstrip())")

echo "$ThisMinuteImage" > "$CLOCK_IS_TICKING"

# clear the screen every hour to avoid ghosting
minute=$(printf "%s" "$MinuteOTheDay" | tail -c 2)
if [ "$minute" = "00" ]; then 
	eips -c
fi

# show that image
eips -g "$ThisMinuteImage"
