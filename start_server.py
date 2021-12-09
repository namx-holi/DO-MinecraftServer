import os
import paramiko
import time
from pathlib import Path

from digitalocean import DigitalOceanAPI


# General config
region = "sgp1"

# Droplet Config
droplet_name = "DO-MinecraftServer"
droplet_size = "s-2vcpu-4gb"
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
print("Creating new Droplet")
droplet = api.droplets.create(
	name=droplet_name,
	region=region,
	size=droplet_size,
	image=droplet_image,
	ssh_keys=droplet_ssh_keys,
	tags=droplet_tags,
	monitoring=True)["droplet"]
print("  Droplet created.")

# Wait until droplet is created
print("  Waiting for Droplet to start...")
while droplet["status"] != "active":
	time.sleep(5)
	droplet = api.droplets.get(droplet["id"])["droplet"]
print("  Droplet is now active!")

# Get the details of the droplet once it's started so we can do networking
droplet = api.droplets.get(droplet["id"])["droplet"]
droplet_ip = droplet["networks"]["v4"][0]["ip_address"]
print("  Droplet ID:", droplet["id"])
print("  Droplet IP:", droplet_ip)


# Reconfigure the network
print("\nSetting up networking")
domain_record = api.domains.list_records(
	domain_name=domain,
	name=f"{subdomain}.{domain}",
	type="A")["domain_records"][0]

domain_update_resp = api.domains.update_record(
	domain_name=domain,
	domain_record_id=domain_record["id"],
	type="A",
	data=droplet_ip)

print(f"Domain Record added for {subdomain}.{domain}")


# Attach the volume
print("\nAttaching Volume")
api.volumes.attach_by_name(
	volume_name=volume_name,
	droplet_id=droplet["id"],
	region=region)
print("Volume attached!")


# Set up SSH connection
print("\nRunning setup commands")

print("  Waiting a little bit before we try connect via SSH")
time.sleep(10)

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

# Run command to mount volume
print("  Mounting Volume")
cmd = f"mkdir -p /mnt/mc && mount -o discard,defaults,noatime /dev/disk/by-id/scsi-0DO_Volume_{volume_name} /mnt/mc"
stdin, stdout, stderr = ssh.exec_command(cmd)
for line in stderr:
	print(line)

# Create swap space
print("  Setting up swapfile")
cmd = f"""
sudo fallocate -l 4G /swapfile
	&& sudo chmod 600 /swapfile
	&& sudo mkswap /swapfile
	&& sudo swapon /swapfile
	&& sudo sysctl vm.swappiness=10""".replace("\n"," ")
stdin, stdout, stderr = ssh.exec_command(cmd)
for line in stderr:
	print(line)

# Start Minecraft server!
print("  Starting Minecraft Server in background")
cmd = "nohup /mnt/mc/start.sh &"
stdin, stdout, stderr = ssh.exec_command(cmd)

# Run command to open firewall for Minecraft server
print("  Opening port 22 and 25565")
cmd = f"""
ufw allow OpenSSH
	&& ufw allow 25565/tcp
	&& ufw allow 25565/udp""".replace("\n", " ")
stdin, stdout, stderr = ssh.exec_command(cmd)
for line in stderr:
	print(line)

# Run command to enable firewall
print("  Enabling UFW firewall")
cmd = f"yes | ufw enable"
stdin, stdout, stderr = ssh.exec_command(cmd)
for line in stderr:
	print(line)

# Close SSH connection. We are done!
print("  Disconnecting from SSH")
ssh.close()
del stdin


print("\nDone!")
