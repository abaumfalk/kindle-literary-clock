# kindle-literary-clock
Use a kindle ebook-reader as literary clock:

- for every minute of the day a citation from a piece of literature is shown containing the current time (printed in **bold letters**)
- use Shift-C to toggle between clock-mode and ordinary mode of the device
- press key to reveal the origin of the current citation ("quiz-mode")
- press key to toggle between black and white mode


## Installation
... TODO ...

- Add a boot script to cleanup the clockisticking file... since it shouldn't be after a boot
```
mntroot rw
cp /mnt/us/timelit/clean-clock /etc/init.d/
cd /etc/rcS.d
ln -s ../init.d/clean-clock S77clean-clock
mntroot ro
```

## References
This repository has been published on: https://github.com/abaumfalk/kindle-literary-clock
It is based on the following work:
- tjaap's original project can be found on instructables: https://www.instructables.com/Literary-Clock-Made-From-E-reader/
- additional quotes from https://github.com/JohannesNE/literature-clock
- cleanup script from https://github.com/knobunc/kindle-clock
