#!/bin/sh
BASEDIR=$(dirname "$(realpath "$0")")

# check if the clock 'app' is not running (by checking if the clockisticking file is there) 
clockrunning=1
test -f "$BASEDIR/clockisticking" || clockrunning=0

if [ $clockrunning -eq 0 ]; then
	/etc/init.d/powerd stop
	/etc/init.d/framework stop
	
	eips -c  # clear display

	# show initial image
	touch "$BASEDIR/clockisticking"
	"$BASEDIR/timelit.sh"

	# start event loop in background
	"$BASEDIR/eventloop.sh" &
else
	rm "$BASEDIR/clockisticking"

	eips -c  # clear display

	/etc/init.d/framework start
	/etc/init.d/powerd start
fi
