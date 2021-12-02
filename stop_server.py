import os
from digitalocean import DigitalOceanAPI

# Droplet Config
d_name = "DO-MinecraftServer"
d_tags = ["DO-MinecraftServer"]


# Connect to API
access_token = os.environ.get("DO_ACCESS_TOKEN")
api = DigitalOceanAPI(access_token)


# Find the correct Minecraft droplet and delete it
print("Getting ID of Droplet")
d_list_resp = api.droplet.list(tag_name=d_tags[0])
d_id = None
for droplet in d_list_resp["droplets"]:
	if droplet["name"] == d_name:
		d_id = droplet["id"]
		break

print("Deleting Droplet")
d_delete_resp = api.droplet.delete(d_id)