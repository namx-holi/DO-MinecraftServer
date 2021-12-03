import os
import sys
from digitalocean import DigitalOceanAPI

# General config
region = "sgp1"

# Droplet Config
droplet_name = "DO-MinecraftServer"
droplet_size = "s-1vcpu-1gb"
droplet_image = "ubuntu-20-04-x64"
droplet_ssh_keys = [os.environ.get("DO_SSH_FINGERPRINT")]
droplet_tags = ["DO-MinecraftServer"]

# Network config
domain = os.environ.get("DO_DOMAIN")
subdomain = os.environ.get("DO_SUBDOMAIN")

# Volume config
volume_name = "do-minecraft-server"


# Connect to API
access_token = os.environ.get("DO_ACCESS_TOKEN")
api = DigitalOceanAPI(access_token)


# Find the correct Minecraft droplet
print("Getting ID of Droplet")
droplet_list_resp = api.droplets.list(tag_name=droplet_tags[0])
droplet_id = None

# Look for the right droplet by matching tag and region
for droplet in d_list_resp["droplets"]:
	if droplet["name"] == droplet_name and droplet["region"]["slug"] == region:
		droplet_id = droplet["id"]
		break

# If the ID is None, there is no droplet to delete. We can stop here!
if droplet_id is None:
	print("No droplet found. Exiting")
	sys.exit(1)


# Unmount volume
print("Detaching volume")
api.volumes.attach_by_name(
	volume_name=volume_name,
	droplet_id=droplet_id,
	region=region)


# Delete the droplet!
print("Deleting Droplet")
api.droplets.delete(droplet_id)
