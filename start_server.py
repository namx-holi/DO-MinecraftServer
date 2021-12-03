import os
import time
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


# Create Minecraft droplet
droplet = api.droplets.create(
	name=droplet_name,
	region=region,
	size=droplet_size,
	image=droplet_image,
	ssh_keys=droplet_ssh_keys,
	tags=droplet_tags)["droplet"]
print("Droplet ID:", droplet["id"])


# Wait until droplet is created
while droplet["status"] != "active":
	time.sleep(10)
	print("Polling Droplet...")
	droplet = api.droplets.get(droplet["id"])["droplet"]
print("Droplet is now active!")


# Get the details of the droplet once it's started so we can do networking
droplet = api.droplets.get(droplet["id"])["droplet"]
droplet_ip = droplet["networks"]["v4"][0]["ip_address"]
print("Droplet IP:", droplet_ip)


# Reconfigure the network
print("Setting up networking")
domain_record = api.domains.list_records(
	domain_name=domain,
	name=f"{subdomain}.{domain}",
	type="A")["domain_records"][0]

domain_update_resp = api.domains.update_record(
	domain_name=domain,
	domain_record_id=domain_record["id"],
	type="A",
	data=droplet_ip)

print("Network configured!")


# Attach the volume
print("Attaching Volume")
api.volumes.attach_by_name(
	volume_name=volume_name,
	droplet_id=droplet["id"],
	region=region)
