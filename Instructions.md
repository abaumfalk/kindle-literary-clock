# Instructions

These are step-by-step instructions how to turn a Kindle into a literary clock. Personally, I have tested 
the following procedure on a 3rd Generation Wifi device, but others might work in a similar fashion.

See:
https://wiki.mobileread.com/wiki/Kindle_Hacks_Information#Hacking_the_Device

## Step 1: Determine device type
The Kindle's device type can be determined from its serial number prefix.
The serial number is available from a sticker on the device and from some
device info menu.

A list can be found here: https://wiki.mobileread.com/wiki/Kindle_Serial_Numbers

For example, my serial number started with B008 -> Kindle 3 Wifi -> K3W


## Step 2: Jailbreak
In order to install custom software you must jailbreak it. 
NOTE: This might void your warranty and there is a small risk to render the
device unusable. Perform this at your own risk!

Download the kindle-jailbreak-0.13.N.zip from https://www.mobileread.com/forums/showthread.php?t=88004
The archive contains several jailbreak files for different devices. Connect via USB-Cable to a PC, find 
the one suitable for your device and copy it to its root folder.

Select software update from the menu, the device will reboot and install the jailbreak.


## Step 3: SSH connection
In order to execute commands and modify the device you need ssh access.
For this, the USBNetwork hack has been developed. Find the appropriate archive kindle-usbnetwork...zip 
archive from the denoted forum post and proceed like in step 2.

Note: The usbnetwork service offers two different ways to connect:
1. turn the USB-Port into a network port (disables the file-upload via USB)
2. using ssh over wifi

After installation and reboot connect the USB-Cable again. In the root folder you will find a folder
named usbnetwork. You have to edit the configuration in usbnetwork/etc/config. I changed: 
ip-addresses, activate ssh over wifi, disable ssh over usb.

(I have only tried the wifi-connection on my device.)

Use the Kindle's local search to start the usbnetwork service manually. Type and search:
;debugOn
~usbNetwork

You should be able to connect via
ssh root@<your.ip.address>

The password can be calculated from the device's serial number using the following
calculators: 
https://www.sven.de/kindle/
https://www.hardanswers.net/amazon-kindle-root-password

Make sure that you can log in. If this works fine, you might configure the usbnetwork so that it starts
automatically. To do this, rename the file DISABLED_auto in its root folder to auto.


## Step 4: Install python

## Step 5: Gerenate timelit images

## Step 6: Copy timelit to the device

### add crontab entry
An entry to crontab ensures that the timelit script is called every minute (regardless if it is activated or not).

### Activate timelit manually
For a first test timelit can be activated manually:
cd /mnt/us/timelit
rm -f clockisticking  # make sure that the script does not think it is running already 
sh ./startstoptimelit.sh  # start the clock


## Step 7: Install cronjob
