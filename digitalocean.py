import requests



class DigitalOceanAPI:

	ROOT_PATH = "https://api.digitalocean.com"

	@property
	def headers(self):
		return {
			"Authorization": f"Bearer {self._token}"
		}
	

	def __init__(self, token):
		self._token = token

		# Register API subsets
		self.droplet = DropletAPI(self)


	def _make_get(self, url, query):
		r = requests.get(
			url=f"{self.ROOT_PATH}{url}",
			headers=self.headers, params=query)
		return r.json()


	def _make_post(self, url, payload):
		r = requests.post(
			url=f"{self.ROOT_PATH}{url}",
			headers=self.headers, json=payload)
		return r.json()


	def _make_delete(self, url, query, no_resp_on_success=False):
		r = requests.delete(
			url=f"{self.ROOT_PATH}{url}",
			headers=self.headers, params=query)

		if no_resp_on_success and r.ok:
			return None
		return r.json()



class DropletAPI:

	def __init__(self, api):
		self._api = api


	def list(self, **kwargs):
		"""
		per_page - integer [1 .. 200]
		Default: 20
			Number of items returned per page

		page - integer [>=1]
		Default: 1
			Which 'page' of paginated results to return.

		tag_name - string
			Used to filter Droplets ny a specific tag.
		"""
		path = "/v2/droplets"

		# Required and optional with defaults
		query = {
			"per_page": kwargs.get("per_page", 20),
			"page": kwargs.get("page", 1)
		}

		# Optional with no defaults
		tag_name = kwargs.get("tag_name", None)
		if tag_name is not None:
			query.update({"tag_name": tag_name})

		# Make request
		return self._api._make_get(path, query)


	def create(self, name, region, size, image, **kwargs):
		"""
		name (required) - string
			The human-readable string you wish to use when displaying
			the Droplet name. The name, if set to a domain name managed
			in the DigitalOcean DNS management system, will configure a
			PTR record for the Droplet. The name set during creation
			will also determine the hostname for the Droplet in its
			internal configuration.

		region (required) - string
			The slug identifier for the region that you wish to deploy
			the Droplet in.

		size (required) - string
			The slug identifier for the size that you wish to select for
			this Droplet.

		image (required) - string or integer
			The image ID of a public or private image or the slug
			identifier for a public image. This image will be the base
			image for your Droplet.

		ssh_keys - Array of strings or integers
		Default: []
			An array containing the IDs or fingerprints of the SSH keys
			that you wish to embed in the Droplet's root account upon
			creation.

		backups - boolean
		Default: false
			A boolean indicating whether automated backups should be
			enabled for the Droplet.

		ipv6 - boolean
		Default: false
			A boolean indicating whether to enable IPv6 on the Droplet.

		monitoring - boolean
		Default: false
			A boolean indicating whether to install the DigitalOcean
			agent for monitoring.

		tags - Array of strings, Nullable
		Default: []
			A flat array of tag names as strings to apply to the Droplet
			after it is created. Tag names can either be existing or new
			tags.

		user_data - string
			A string containing 'user data' which may be used to
			configure the Droplet on first boot, often a 'cloud-config'
			file or Bash script. It must be plain text and may not
			exceed 64 KiB in size.

		vpc_uuid - string
			A string specifying the UUID of the VPC to which the Droplet
			will be assigned. If excluded, the Droplet will be assigned
			to your account's default VPC for the region.

		with_droplet_agent - boolean
			A boolean indicating whether to install the DigitalOcean
			agent used for providing access to the Droplet web console
			in the control panel. By default, the agent is installed on
			new Droplets but installation errors (i.e. OS not supported)
			are ignored. To prevent it from being installed, set to
			`false`. To make installation errors fatal, explicitly set
			it to `true`.
		"""
		path = "/v2/droplets"

		# Required and optional with defaults
		payload = {
			"name": name,
			"region": region,
			"size": size,
			"image": image,
			"ssh_keys": kwargs.get("ssh_keys", []),
			"backups": kwargs.get("backups", False),
			"ipv6": kwargs.get("ipv6", False),
			"monitoring": kwargs.get("monitoring", False),
			"tags": kwargs.get("tags", [])
		}

		# Optional with no defaults
		user_data = kwargs.get("user_data", None)
		if user_data is not None:
			payload.update({"user_data": user_data})
		vpc_uuid = kwargs.get("vpc_uuid", None)
		if vpc_uuid is not None:
			payload.update({"vpc_uuid": vpc_uuid})
		with_droplet_agent = kwargs.get("with_droplet_agent", None)
		if with_droplet_agent is not None:
			payload.update({"with_droplet_agent": with_droplet_agent})

		# Make request
		return self._api._make_post(path, payload)


	def delete_by_tag(self, tag_name):
		"""
		tag_name (required) - string
			Specifies Droplets to be deleted by tag.
		"""
		path = "/v2/droplets"

		# Required and optional with defaults
		query = {
			"tag_name": tag_name
		}

		# Make request
		return self._api._make_delete(path, query, no_resp_on_success=True)


	def delete(self, droplet_id):
		"""
		droplet_id (required) - integer [>= 1]
			A unique identifier for a Droplet instance.
		"""
		path = f"/v2/droplets/{droplet_id}"

		# Make request
		return self._api._make_delete(path, None, no_resp_on_success=True)



# TODO: API for creating a droplet


# TODO: API for attaching a volume


# TODO: API for adding DNS AAAA record


# TODO: API for running something?
