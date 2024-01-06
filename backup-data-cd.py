#!/usr/bin/env python3

import sys
import os
import os.path as path
import fcntl
import time
import sh
import tempfile
from pathlib import Path

CDROM_DEVICE_PATH = '/dev/sr0'
CDROM_MOUNT_PATH = '/media/cdrom0'
CDROM_POLL_S = 5
DEBUG = False

# From /usr/include/linux/cdrom.h
CDROM_DRIVE_STATUS  = 0x5326  # Get tray position, etc.
CDROM_DISC_STATUS   = 0x5327  # Get disc type, etc.
CDS_NO_INFO         = 0
CDS_NO_DISC         = 1
CDS_TRAY_OPEN       = 2
CDS_DRIVE_NOT_READY = 3
CDS_DISC_OK         = 4
CDS_AUDIO           = 100
CDS_DATA_1          = 101
CDS_DATA_2          = 102
CDS_XA_2_1          = 103
CDS_XA_2_2          = 104
CDS_MIXED           = 105

def detect_disc():
    fd = os.open(CDROM_DEVICE_PATH, os.O_RDONLY | os.O_NONBLOCK)
    rv = fcntl.ioctl(fd, CDROM_DRIVE_STATUS, 0)
    os.close(fd)
    return rv == CDS_DISC_OK

def wait_disc():
    while not detect_disc():
        time.sleep(CDROM_POLL_S)

def disc_info():
    print(sh.setcd('-i', CDROM_DEVICE_PATH))
    iso_info = sh.Command('iso-info')
    info = iso_info('--no-header', CDROM_DEVICE_PATH)
    print(info)
    for line in info.split('\n'):
        words = line.split(maxsplit=2)
        if words[:2] == ['Volume', ':']:
            volume_name = words[2]
            break
    
    if DEBUG: print(f'Volume name is "{volume_name}".')
    return volume_name

def backup_disc(volume_name):
    sh.mount(CDROM_DEVICE_PATH)
    with tempfile.TemporaryDirectory(dir='.') as tmpdir:
        sh.gcp('-r', '--preserve=timestamps', CDROM_MOUNT_PATH, tmpdir, _fg=True)
        os.rename(path.join(tmpdir, path.basename(CDROM_MOUNT_PATH)), volume_name)

def cleanup():
    sh.eject(CDROM_DEVICE_PATH)

def main():
    while True:
        try:
            wait_disc()
            volume_name = disc_info()
            user_volume = input(f'Enter volume name to continue: [{volume_name}] ')
            if user_volume:
                volume_name = user_volume

            backup_disc(volume_name)
            input('Continue? ')
            cleanup()
            
        except KeyboardInterrupt:
            print('\nCleaning up.')
            cleanup()
            break

if __name__ == '__main__':
    main()
