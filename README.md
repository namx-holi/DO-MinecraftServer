# DO-MinecraftServer
TODO: Description of project


## Setup


### Raspberry Pi
TODO: Notes about what to install on RPi

Install required packages on the RPi
```sh
sudo apt update
```

Update pip to the latest version. Also install RPi GPIO packages.
```sh
pip install --upgrade pip setuptools
pip install wheel

pip install gpiozero RPi.GPIO
```

TODO: Note about generating an ssh access key on the pi.


### DigitalOcean
TODO: Note about setting up API personal access token.

TODO: Note about setting up Volume

TODO: Note about adding the pi ssh key to ssh keys


### Lightbox
You'll want to open up the lightbox and find the wires that goe from the button on the side to the long circuit board. Splice these two wires and add four connectors for GPIO pins.

Connect one battery wire to the 3.3V DC power pin on the RPi, and the other wire to pin 22 (GPIO 25). Find which wire from the lightbox circuit board is ground, and connect that to a ground pin, and connect the other wire to pin 8 (GPIO 14).

NOTE: On testing, the board expects very low current, and about 4.18 V, but the RPi's regular GPIO 3.3 V pins do the job.


### Cloning the project
TODO: Notes about cloning project


### Environment variables
Many environment variables need to be set, and are outlined in `.env_example`. Copy this file and name it `.env`.

#### Required
- DO_ACCESS_TOKEN can be found in the API page on DigitalOcean when generating a personal access token.

- DO_SSH_KEY_FINGERPRINTS is a comma separated list of SSH keys fingerprints. These can be found on the Settings page on DigitalOcean, under security.

- DO_DROPLET_SSH_ACCESS_KEY is the location of the generated SSH key for DigitalOcean on the Raspberry Pi.

- DO_NETWORK_DOMAIN is the domain that will be used for the running Minecraft Server, e.g. `example.org`

- DO_NETWORK_SUBDOMAIN is the subdomain of the domain being used, i.e. `mc` for `mc.example.org`

- DO_VOLUME_NAME is the name of the volume created to store the Minecraft server files

#### Optional
- DO_REGION is the region used to set up the Droplet. This defaults to Singapore datacenter 1. The codes for these can be found [here](https://slugs.do-api.dev/) under Regions.

- DO_DROPLET_NAME is the name that will be given to the Droplet that runs the Minecraft server. This defaults to `DO-MinecraftServer`, but can be set to pretty much any valid name.

- DO_DROPLET_SIZE is the identifier for what type of droplet will be set up. The default is a 2 CPU, 4 GB RAM droplet. The codes for these can be found [here](https://slugs.do-api.dev/) under Droplet Sizes.

- DO_DROPLET_IMAGE is the image that will be used when setting up a Droplet to run the Minecraft server. The default is Ubuntu 20.04 (LTS) x64. The codes for these can be found [here](https://slugs.do-api.dev/) under Distro Images.

- DO_DROPLET_TAGS is a comma separated list of tags to give to the Droplet on setup. The default is no tags.



### Virtual environment
Create a virtual environment, and install the requirements. Also install some Pi specific libraries for the GPIO pins
```sh
py -m venv ./venv
source venv/bin/activate
pip install -r requirements.txt

pip install gpiozero
pip install RPi.GPIO
```


### Start app on RPi boot
To have this run on boot, add the following lines to `/etc/rc.local`
```sh
# Start Digital Ocean Minecraft server starter
sudo \
	/home/pi/DO-MinecraftServer/venv/bin/python \
	/home/pi/DO-MinecraftServer/pi_app.py &
exit 0
```
To stop this from happening, just comment out those lines in `/etc/rc.local`.


TODO: Unsure if these are important or not
```sh
sudo systemctl disable avahi-daemon
sudo systemctl stop avahi-daemon.service
sudo systemctl stop avahi-daemon.socket
```


## Maintenance

### Resizing Volume
At some point, the storage size of the Volume you set up will get a bit too small.

To resize the Volume, first start up the Minecraft server. You will then need to navigate to where your Volume is on `cloud.digitalocean`, and expand the Volume to the desired new size.

You will then need to SSH into the running Minecraft server Droplet, and stop the currently running Minecraft server on it. The easiest way to do this is to login with a Minecraft client and use the `/stop` command, but it can also be stopped by ending the process.

Then run the following commands to actually use the full Volume's space
```sh
# Ensure the server.jar is not running before running these!

# Unmount the volume
unmount /mnt/mc

# Resize the volume to take the full space
e2fsck -y /dev/disk/by-id/scsi-0DO_Volume_{volume_name}
resize2fs /dev/disk/by-id/scsi-0DO_Volume_{volume_name}

# Remount the volume
mount -o discard,defaults,noatime /dev/disk/by-id/scsi-0DO_Volume_{volume_name} /mnt/mc
```
You can now manually start up the server.jar on the Droplet again if you wish by using
```sh
nohup /mnt/mc/start.sh 2>&1 > ~/minecraftserver.log &
```


### Updating Minecraft server version
TODO: Write this. It's super easy


## TODO
- Important
	- Write the full documentation
	- Wiring details for the KMart Minecraft lightbox
		- https://www.kmart.com.au/product/minecraft-logo-light-43183579/

- Minor
	- Either use the new official Digital Ocean API, or rewrite ours to use objects
