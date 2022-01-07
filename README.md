# DO-MinecraftServer


## Setup

### Initialisation
TODO: Notes about what to set up on Digital Ocean, how to set up the Volume, etc.


### Environment Variables
TODO: Notes about each environment variable, what are required to be set, and what are optional/defaulted.



## Usage

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
