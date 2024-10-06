#!/bin/sh
BASEDIR=$(dirname "$(realpath "$0")")

# check if the clock 'app' is not running (by checking if the clockisticking file is there) 
clockrunning=1
test -f "$BASEDIR/clockisticking" || clockrunning=0

if [ $clockrunning -eq 0 ]; then
	/etc/init.d/powerd stop
	/etc/init.d/framework stop
	
	eips -c  # clear display

	# run showMetadata.sh to enable the keystrokes that will show the metadata
	"$BASEDIR/showMetadata.sh" &

	# run switchMode.sh to switch between dark/light mode on keystroke
	"$BASEDIR/switchMode.sh" &

	touch "$BASEDIR/clockisticking"

	"$BASEDIR/timelit.sh"
else
	rm "$BASEDIR/clockisticking"

	eips -c  # clear display

	# go to home screen
	# echo "send 102">/proc/keypad

	/etc/init.d/framework start
	/etc/init.d/powerd start
fi
