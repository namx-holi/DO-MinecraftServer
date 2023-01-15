import os
from dotenv import load_dotenv
from pathlib import Path

# TODO: Have a method for a user to set this via environ vars
RAISE_EXCEPTION_IF_VALIDATION_ERROR = True

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, ".env"))


def safe_environ_get(name):
	val = os.environ.get(name)
	if val is None:
		return ""
	return val

def ignore_empty_string_split(s, splitting_string):
	if not s:
		return []
	return s.split(splitting_string)


class DigitalOceanConfig:
	ACCESS_TOKEN = os.environ.get("DO_ACCESS_TOKEN")
	REGION = os.environ.get("DO_REGION") or "sgp1"

	DROPLET_NAME = os.environ.get("DO_DROPLET_NAME") or "DO-MinecraftServer"
	DROPLET_SIZE = os.environ.get("DO_DROPLET_SIZE") or "s-2vcpu-4gb"
	DROPLET_IMAGE = os.environ.get("DO_DROPLET_IMAGE") or "ubuntu-20-04-x64"
	DROPLET_SSH_KEYS = ignore_empty_string_split(safe_environ_get("DO_SSH_KEY_FINGERPRINTS"), ",")
	DROPLET_TAGS = ignore_empty_string_split(safe_environ_get("DO_DROPLET_TAGS"), ",") or ["DO-MinecraftServer"]
	DROPLET_SSH_ACCESS_KEY_REL_PATH = safe_environ_get("DO_DROPLET_SSH_ACCESS_KEY")
	DROPLET_SSH_ACCESS_KEY_PATH = Path(DROPLET_SSH_ACCESS_KEY_REL_PATH).expanduser()
	# NOTE: Path is used to expand the

	NETWORK_DOMAIN = os.environ.get("DO_NETWORK_DOMAIN")
	NETWORK_SUBDOMAIN = os.environ.get("DO_NETWORK_SUBDOMAIN")
	
	VOLUME_NAME = os.environ.get("DO_VOLUME_NAME")


	@classmethod
	def validate(cls):
		error = False

		if not cls.ACCESS_TOKEN:
			print("DO_ACCESS_TOKEN environment variable not set")
			error = True

		if not cls.REGION:
			print("DO_REGION environment variable not set")
			error = True

		if not cls.DROPLET_NAME:
			print("DO_DROPLET_NAME environment variable not set")
			error = True
		if not cls.DROPLET_SIZE:
			print("DO_DROPLET_SIZE environment variable not set")
			error = True
		if not cls.DROPLET_IMAGE:
			print("DO_DROPLET_SIZE environment variable not set")
			error = True
		if not cls.DROPLET_SSH_KEYS:
			print("DO_SSH_KEY_FINGERPRINTS environment variable not set")
			error = True
		if not cls.DROPLET_TAGS:
			print("DO_DROPLET_TAGS environment variable not set")
			error = True
		if not cls.DROPLET_SSH_ACCESS_KEY_REL_PATH:
			print("DO_DROPLET_SSH_ACCESS_KEY environment variable not set")
			error = True

		if not cls.NETWORK_DOMAIN:
			print("DO_NETWORK_DOMAIN environment variable not set")
			error = True
		if not cls.NETWORK_SUBDOMAIN:
			print("DO_NETWORK_SUBDOMAIN environment variable not set")
			error = True

		if not cls.VOLUME_NAME:
			print("DO_VOLUME_NAME environment variable not set")
			error = True

		if error and RAISE_EXCEPTION_IF_VALIDATION_ERROR:
			raise Exception("DigitalOceanConfig not fully set up")


# Validate config
DigitalOceanConfig.validate()
