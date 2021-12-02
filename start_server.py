import os
from digitalocean import DigitalOceanAPI

# Droplet Config
d_name = "DO-MinecraftServer"
d_region = "sgp1"
d_size = "s-1vcpu-1gb"
d_image = "ubuntu-20-04-x64"
d_ssh_keys = [os.environ.get("DO_SSH_FINGERPRINT")]
d_tags = ["DO-MinecraftServer"]

# TODO: Volume config
v_name = "do-minecraft-server"


# Connect to API
access_token = os.environ.get("DO_ACCESS_TOKEN")
api = DigitalOceanAPI(access_token)


# Create Minecraft droplet
d_create_resp = api.droplet.create(
	name=d_name,
	region=d_region,
	size=d_size,
	image=d_image,
	ssh_keys=d_ssh_keys,
	tags=d_tags)
print(d_create_resp)
d_id = d_create_resp["droplet"]["id"]


# Create volume
...