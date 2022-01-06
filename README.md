DO-MinecraftServer


## How to resize volume
First, expand the size on DO.

Then, you need to expand the partition. This can be done using:
```sh
# Unmount
umount /mnt/mc

# Resize
e2fsck -y /dev/disk/by-id/scsi-0DO_Volume_{volume_name}
resize2fs /dev/disk/by-id/scsi-0DO_Volume_{volume_name}

# Remount
mount -o discard,defaults,noatime /dev/disk/by-id/scsi-0DO_Volume_{volume_name} /mnt/mc
```