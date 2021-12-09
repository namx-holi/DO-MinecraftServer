import os
import paramiko
import sys
import time
from pathlib import Path

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
droplets = api.droplets.list(tag_name=droplet_tags[0])["droplets"]
droplet_id = None

# Look for the right droplet by matching tag and region
for droplet in droplets:
	if droplet["name"] == droplet_name and droplet["region"]["slug"] == region:
		droplet_id = droplet["id"]
		break

# If the ID is None, there is no droplet to delete. We can stop here!
if droplet_id is None:
	print("No droplet found. Exiting")
	sys.exit(1)

droplet_ip = droplet["networks"]["v4"][0]["ip_address"]
print("  Droplet ID:", droplet["id"])
print("  Droplet IP:", droplet_ip)


# Shut down minecraft server
print("\nShutting down Minecraft server")
print("  Connecting to server via SSH")
key_path = Path(os.environ.get("DO_SSH_KEY")).expanduser()
with open(key_path, "r") as stream:
	k = paramiko.RSAKey.from_private_key(stream)

while True:
	try:
		ssh = paramiko.SSHClient()
		ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		ssh.connect(hostname=droplet_ip, username="root", pkey=k)
	except:
		print("  Failed to connect via SSH. Trying again in 10 seconds.")
		time.sleep(10)
		continue
	break

# Run command to get PID of minecraft server
print("  Getting PID of process")
cmd = """ps -ef | awk '$8=="/mnt/mc/jdk/bin/java" {print $2}'"""
stdin, stdout, stderr = ssh.exec_command(cmd)
pid = stdout.read().decode().strip()

if pid is not "":
	# Send a SIGTERM to server
	print("  Sending SIGTERM to process")
	cmd = f"kill -15 {pid}"
	stdin, stdout, stderr = ssh.exec_command(cmd)
	for line in stderr:
		print(line)

	# Ensure the server has stopped
	print("  Waiting until server has stopped")
	while pid is not "":
		time.sleep(3)
		get_pid_cmd = """ps -ef | awk '$8=="/mnt/mc/jdk/bin/java" {print $2}'"""
		stdin, stdout, stderr = ssh.exec_command(get_pid_cmd)
		pid = stdout.read().decode().strip()
else:
	print("  Server not running.")


# Unmount volume
print("\nDetaching volume")
api.volumes.attach_by_name(
	volume_name=volume_name,
	droplet_id=droplet_id,
	region=region)
print("  Volume detached")


# Delete the droplet!
print("\nDeleting Droplet")
api.droplets.delete(droplet_id)
print("  Droplet Deleted")

print("\nDone!")
