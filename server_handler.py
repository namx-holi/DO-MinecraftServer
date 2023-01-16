
import paramiko
import time
import urllib.request

from config import DigitalOceanConfig as Config
from digitalocean import DigitalOceanAPI


# Delay between checking if a droplet has fully started when starting up
#  the Minecraft server.
DROPLET_STARTUP_POLL_DELAY = 5 # seconds

# How long we wait after attaching the volume before we try SSH into the
#  Droplet.
SSH_CONNECT_INITIAL_DELAY = 10 # seconds

# How long to wait before retrying an SSH connection to Droplet if it
#  fails.
SSH_CONNECT_RETRY_DELAY = 10 # seconds

# Delay between checking if the Minecraft server process has stopped
#  when shutting down the server
MC_SERVER_POLL_DELAY = 3 # seconds

# Whether swap space will be set up on the Droplet
USE_SWAP = False
# TODO: Var for swap size. Defaults to 4 GB

# This URL is used to check if the RPi is connected to the internet.
#  This can be anything that has a really high uptime.
INTERNET_CONNECTIVITY_TEST_URL = "https://www.google.com"

# How long we wait to try to connect to the internet connectivity test
#  url again after failing.
INTERNET_CONNECTIVITY_RETRY_DELAY = 3 # seconds



class ServerHandler:

	@classmethod
	def wait_until_internet_connectivity(cls):
		"""
		Will block until we have an internet connection
		"""

		# Helper method to check if connected right now.
		def _is_connected():
			try:
				# Try connect to a website
				urllib.request.urlopen(INTERNET_CONNECTIVITY_TEST_URL)
				return True
			except Exception as e:
				print("Error was:", e)
				return False

		# Wait until we can connect to the internet
		print("Waiting on internet connectivity")
		while True:
			if _is_connected():
				return
			else:
				print(f"  Cannot connect to internet. Retrying in {INTERNET_CONNECTIVITY_RETRY_DELAY} seconds")
				time.sleep(INTERNET_CONNECTIVITY_RETRY_DELAY)
		print("")


	@classmethod
	def start_server(cls):
		# Connect to API
		api = DigitalOceanAPI(Config.ACCESS_TOKEN)

		# Create a new Minecraft droplet
		print("Creating new Droplet")
		droplet = api.droplets.create(
			name=Config.DROPLET_NAME,
			region=Config.REGION,
			size=Config.DROPLET_SIZE,
			image=Config.DROPLET_IMAGE,
			ssh_keys=Config.DROPLET_SSH_KEYS,
			tags=Config.DROPLET_TAGS,
			monitoring=True)["droplet"]
		print("  Droplet created.")

		# Wait until the droplet is created
		print("  Waiting for Droplet to start...")
		while droplet["status"] != "active":
			time.sleep(DROPLET_STARTUP_POLL_DELAY)
			droplet = api.droplets.get(droplet["id"])["droplet"]
		print("  Droplet is now active!")

		# Get the details of the droplet once it's started so we can
		#  do networking
		droplet = api.droplets.get(droplet["id"])["droplet"]
		droplet_ip = droplet["networks"]["v4"][0]["ip_address"]
		print("  Droplet ID:", droplet["id"])
		print("  Droplet IP:", droplet_ip)
		print("")


		# Set up a DNS A record for the new droplet
		print("Setting up networking")
		print("  Finding existing DNS address record")
		# TODO: What to do if there's no existing DNS record?
		domain_record = api.domains.list_records(
			domain_name=Config.NETWORK_DOMAIN,
			name=f"{Config.NETWORK_SUBDOMAIN}.{Config.NETWORK_DOMAIN}",
			type="A")["domain_records"][0]

		print("  Updating existing DNS address record to point to new Droplet")
		domain_update_resp = api.domains.update_record(
			domain_name=Config.NETWORK_DOMAIN,
			domain_record_id=domain_record["id"],
			type="A",
			data=droplet_ip)
		print(f"  DNS address record added for {Config.NETWORK_SUBDOMAIN}.{Config.NETWORK_DOMAIN}")
		print("")


		# Attach the volume
		print("Attaching Volume")
		api.volumes.attach_by_name(
			volume_name=Config.VOLUME_NAME,
			droplet_id=droplet["id"],
			region=Config.REGION)
		print("  Volume attached!")
		print("")


		# Set up SSH connection
		print("Running setup commands")
		print("  Waiting a little bit before we try connect via SSH")
		time.sleep(SSH_CONNECT_INITIAL_DELAY)

		# Connect to the droplet
		print("  Connecting to server via SSH")
		with open(Config.DROPLET_SSH_ACCESS_KEY_PATH, "r") as stream:
			ssh_key = paramiko.RSAKey.from_private_key(stream)
		while True:
			try:
				ssh = paramiko.SSHClient()
				ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
				ssh.connect(hostname=droplet_ip, username="root", pkey=ssh_key)
			except:
				print(f"  Failed to connect to droplet via SSH. Trying again in {SSH_CONNECT_RETRY_DELAY} seconds")
				time.sleep(SSH_CONNECT_RETRY_DELAY)
				continue
			break

		# Run command to mount volume
		print("  Mounting Volume")
		cmd = f"mkdir -p /mnt/mc && mount -o discard,defaults,noatime /dev/disk/by-id/scsi-0DO_Volume_{Config.VOLUME_NAME} /mnt/mc"
		stdin, stdout, stderr = ssh.exec_command(cmd)
		for line in stderr:
			print(line)

		# Set up swap space if desired
		if USE_SWAP:
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

		# Start the Minecraft server in background
		print("  Starting Minecraft server in background")
		cmd = "nohup /mnt/mc/start.sh 2>&1 > ~/minecraftserver.log &"
		stdin, stdout, stderr = ssh.exec_command(cmd)

		# Open up firewall for the Minecraft server
		print("  Opening port 22 and 25565")
		cmd = f"""
		ufw allow OpenSSH
			&& ufw allow 25565/tcp
			&& ufw allow 25565/udp""".replace("\n", " ")
		stdin, stdout, stderr = ssh.exec_command(cmd)
		for line in stderr:
			print(line)

		# Enable the firewall
		print("  Enabling UFW firewall")
		cmd = f"yes | ufw enable"
		stdin, stdout, stderr = ssh.exec_command(cmd)
		for line in stderr:
			print(line)

		# Close SSH connection. Server is noew set up!
		print("  Disconnecting from SSH")
		ssh.close()
		del stdin
		print("")

		# TODO: Why return anything?
		print("Done!")
		return True


	@classmethod
	def poll_server(cls):
		# Connect to API
		api = DigitalOceanAPI(Config.ACCESS_TOKEN)


		# Find the correct Minecraft droplet
		print("Polling server")
		print("  Getting ID of Droplet")
		droplets = api.droplets.list(tag_name=Config.DROPLET_TAGS[0])["droplets"]
		droplet_id = None

		# Look for the right droplet by matching tag and region
		for droplet in droplets:
			if droplet["name"] == Config.DROPLET_NAME and droplet["region"]["slug"] == Config.REGION:
				droplet_id = droplet["id"]
				break
		if droplet_id is None:
			print("No active droplet found")
			return None

		droplet_ip = droplet["networks"]["v4"][0]["ip_address"]
		print("  Droplet ID:", droplet["id"])
		print("  Droplet IP:", droplet_ip)
		print("Droplet found!")
		return droplet


	@classmethod
	def stop_server(cls):
		# Connect to API
		api = DigitalOceanAPI(Config.ACCESS_TOKEN)

		# Find the correct Minecraft droplet
		droplet = cls.poll_server()
		if droplet is None:
			# TODO: Why return anything?
			return False
		droplet_ip = droplet["networks"]["v4"][0]["ip_address"]
		print("")


		# Shut down the Minecraft server
		print("Shutting down Minecraft server")
		print("  Connecting to server via SSH")
		with open(Config.DROPLET_SSH_ACCESS_KEY_PATH, "r") as stream:
			ssh_key = paramiko.RSAKey.from_private_key(stream)
		while True:
			try:
				ssh = paramiko.SSHClient()
				ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
				ssh.connect(hostname=droplet_ip, username="root", pkey=ssh_key)
			except:
				print(f"  Failed to connect to droplet via SSH. Trying again in {SSH_CONNECT_RETRY_DELAY} seconds")
				time.sleep(SSH_CONNECT_RETRY_DELAY)
				continue
			break

		# Get the PID of the Minecraft server
		print("  Getting PID of server process")
		cmd = """ps -ef | awk '$8=="/mnt/mc/jdk/bin/java" {print $2}'"""
		stdin, stdout, stderr = ssh.exec_command(cmd)
		pid = stdout.read().decode().strip()

		# Attempt to shut down the server gracefully if given a PID
		if pid != "":
			print("  PID of server process is", pid)

			# Send a SIGTERM to server
			print("  Sending SIGTERM to process")
			cmd = f"kill -15 {pid}"
			stdin, stdout, stderr = ssh.exec_command(cmd)
			for line in stderr:
				print(line)

			# Ensure the server has stopped
			print("  Waiting until server has stopped")
			while pid != "":
				time.sleep(MC_SERVER_POLL_DELAY)
				get_pid_cmd = """ps -ef | awk '$8=="/mnt/mc/jdk/bin/java" {print $2}'"""
				stdin, stdout, stderr = ssh.exec_command(get_pid_cmd)
				pid = stdout.read().decode().strip()
		else:
			print("  Server not running.")
		print("")


		# Unmount Volume
		print("Detaching Volume")
		api.volumes.detach_by_name(
			volume_name=Config.VOLUME_NAME,
			droplet_id=droplet["id"],
			region=Config.REGION)
		print("  Volume detached")
		print("")


		# Delete the droplet!
		print("Deleting Droplet")
		api.droplets.delete(droplet["id"])
		print("  Droplet deleted")
		print("")


		# TODO: Why return anything?
		print("Done!")
		return True
