# DO-MinecraftServer


## Setup

### Initialisation
TODO: Notes about what to set up on Digital Ocean, how to set up the Volume, etc.


### Environment Variables
TODO: Notes about each environment variable, what are required to be set, and what are optional/defaulted.



## Usage

### Raspberry Pi
https://raspberrytips.com/install-latest-python-raspberry-pi/
https://www.dexterindustries.com/howto/run-a-program-on-your-raspberry-pi-at-startup/



Install some Pi specific libraries
```sh
py -m venv ./venv
source venv/bin/activate
pip install -r requirements.txt

# Pi specific
pip install gpiozero
pip install RPi.GPIO --pre # RPi.GPIO not released for py3.9 as of writing.
```

TODO: Write this
Add this into `/etc/rc.local`
```sh
# Send stdout and stderr from rc.local to log file
exec 1>/tmp/rc.local.log 2>&1
# Tell sh to display commands before execution
set -x

# Start Minecraft Digital Ocean server starter
sudo \
  /home/pi/DO-MinecraftServer/venv/bin/python \
  /home/pi/DO-MinecraftServer/pi_app.py &
```


### Starting server
TODO


### Stopping server
TODO



## Maintenance

### Resizing Volume
At some point, the space set up on the volume will get a bit too small.

To resize the Volume, first start up the server. Then expand the Volume on `cloud.digitalocean`.

Finally, expand the partition by SSHing into the server and running the following commands:
```sh
# Unmount
umount /mnt/mc

# Resize
e2fsck -y /dev/disk/by-id/scsi-0DO_Volume_{volume_name}
resize2fs /dev/disk/by-id/scsi-0DO_Volume_{volume_name}

# Remount
mount -o discard,defaults,noatime /dev/disk/by-id/scsi-0DO_Volume_{volume_name} /mnt/mc
```
