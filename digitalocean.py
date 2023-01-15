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
		self.volumes = BlockStorageAPI(self)
		self.domains = DomainAPI(self)
		self.droplets = DropletAPI(self)


	def _make_get(self, url, params):
		r = requests.get(
			url=f"{self.ROOT_PATH}{url}",
			headers=self.headers, params=params)
		return r.json()


	def _make_post(self, url, payload):
		r = requests.post(
			url=f"{self.ROOT_PATH}{url}",
			headers=self.headers, json=payload)
		return r.json()


	def _make_delete(self, url, params, no_resp_on_success=False):
		r = requests.delete(
			url=f"{self.ROOT_PATH}{url}",
			headers=self.headers, params=params)

		if no_resp_on_success and r.ok:
			return None
		return r.json()


	def _make_put(self, url, payload):
		r = requests.put(
			url=f"{self.ROOT_PATH}{url}",
			headers=self.headers, json=payload)
		return r.json()



class BlockStorageAPI:

	def __init__(self, api):
		self._api = api


	def list(self, **kwargs):
		"""
		name - string
			The block storage volume's name.

		region - string
			The slug identifier for the region where the resource is
			available.

		per_page - integer [1 .. 200]
		Default: 20
			Number of items returned per page

		page - integer [>=1]
		Default: 1
			Which 'page' of paginated results to return.
		"""
		path = "/v2/volumes"

		# Required and optional with defaults
		params = {
			"per_page": kwargs.get("per_page", 20),
			"page": kwargs.get("page", 1)
		}

		# Optional with no defaults
		name = kwargs.get("name", None)
		if name is not None:
			params.update({"name": name})
		region = kwargs.get("region", None)
		if region is not None:
			params.update({"region": region})

		return self._api._make_get(path, params)


	def action(self, type, volume_id, droplet_id, **kwargs):
		"""
		type (required) - string
			The volume action to initiate

		volume_id (required) - int
			The id of the block storage volume

		region - string
			The slug identifier for the region where the resource will
			initially be available.

		droplet_id (required) - integer
			The unique identifier for the Droplet the volume will be
			attached or detached from.

		tags - Array of strings, Nullable
			A flat array of tag names as strings to be applied to the
			resource. Tag names may be for either existing or new tags
		"""
		path = f"/v2/volumes/{volume_id}/actions"

		# Required and optional with defaults
		payload = {
			"type": type,
			"droplet_id": droplet_id
		}

		# Optional with no defaults
		region = kwargs.get("region", None)
		if region is not None:
			payload.update({"region": region})
		tags = kwargs.get("tags", None)
		if tags is not None:
			payload.update({"tags": tags})

		# Make request
		return self._api._make_post(path, payload)


	def attach(self, volume_id, droplet_id, **kwargs):
		"""
		Wrapper for action
		"""
		return self.action("attach", volume_id, droplet_id, **kwargs)


	def detach(self, volume_id, droplet_id, **kwargs):
		"""
		Wrapper for action
		"""
		return self.action("detach", volume_id, droplet_id, **kwargs)


	def action_by_name(self, type, volume_name, droplet_id, **kwargs):
		"""
		type (required) - string
			The volume action to initiate

		volume_name (required) - string
			The name of the block storage volume

		region - string
			The slug identifier for the region where the resource will
			initially be available.

		droplet_id (required) - integer
			The unique identifier for the Droplet the volume will be
			attached or detached from.

		tags - Array of strings, Nullable
			A flat array of tag names as strings to be applied to the
			resource. Tag names may be for either existing or new tags
		"""
		path = "/v2/volumes/actions"

		# Required and optional with defaults
		payload = {
			"volume_name": volume_name,
			"type": type,
			"droplet_id": droplet_id
		}

		# Optional with no defaults
		region = kwargs.get("region", None)
		if region is not None:
			payload.update({"region": region})
		tags = kwargs.get("tags", None)
		if tags is not None:
			payload.update({"tags": tags})

		# Make request
		return self._api._make_post(path, payload)


	def attach_by_name(self, volume_name, droplet_id, **kwargs):
		"""
		Wrapper for action_by_name
		"""
		return self.action_by_name("attach", volume_name, droplet_id, **kwargs)


	def detach_by_name(self, volume_name, droplet_id, **kwargs):
		"""
		Wrapper for action_by_name
		"""
		return self.action_by_name("detach", volume_name, droplet_id, **kwargs)
	


class DomainAPI:
	
	def __init__(self, api):
		self._api = api


	def list_records(self, domain_name, **kwargs):
		"""
		domain_name (required) - string
			The name of the domain itself.

		name - string
			A fully qualified record name. For example, to only include
			records matching sub.example.com, send a GET request to
			`/v2/domains/$DOMAIN_NAME/records?name=sub.example.com`.

		type - string ["A", "AAAA", "CAA", "CNAME", "MX", "NS", "SOA", "SRV", "TXT"]
			The type of the DNS record. For example, A, CNAME, TXT, ...
		"""
		path = f"/v2/domains/{domain_name}/records"

		# Required and optional with defaults
		params = {
		}

		# Optional with no defaults
		name = kwargs.get("name", None)
		if name is not None:
			params.update({"name": name})
		type = kwargs.get("type", None)
		if type is not None:
			params.update({"type": type})

		# Make request
		return self._api._make_get(path, params)


	def create_record(self, domain_name, type, name, data, **kwargs):
		"""
		domain_name (required) - string
			The name of the domain itself

		type (required) - string
			The type of the DNS record. For example: A, CNAME, TXT, ...

		data (required) - string
			Variable data depending on record type. For example, the
			"data" value for an A record would be the IPv4 address to
			which the domain will be mapped. For a CAA record, it would
			contain the domain name of the CA being granted permission
			to issue cretificates.

		priority - integer, Nullable
			The priority for SRV and MX records.

		port - integer, Nullable
			The port for SRV records.

		ttl - integer
			This value is the time to live for the record, in seconds.
			This defines the time frame that clients can cache queried
			information before a refresh should be requested.

		weight - integer, Nullable
			The weight for SRV records.

		flags - integer, Nullable
			An unsigned integer between 0-255 used for CAA records.

		tag - string, Nullable
			The parameter tag for CAA records. Valid values are "issue",
			"issuewild", or "iodef".
		"""
		path = f"/v2/domains/{domain_name}/records"

		# Required and optional with defaults
		payload = {
			"type": type,
			"name": name,
			"data": data
		}

		# Optional with no defaults
		priority = kwargs.get("priority", None)
		if priority is not None:
			payload.update({"priority": priority})
		port = kwargs.get("port", None)
		if port is not None:
			payload.update({"port": port})
		ttl = kwargs.get("ttl", None)
		if ttl is not None:
			payload.update({"ttl": ttl})
		weight = kwargs.get("weight", None)
		if weight is not None:
			payload.update({"weight": weight})
		flags = kwargs.get("flags", None)
		if flags is not None:
			payload.update({"flags": flags})
		tag = kwargs.get("tag", None)
		if tag is not None:
			payload.update({"tag": tag})


		# Make request
		return self._api._make_post(path, payload)


	def get_record(self, domain_name, domain_record_id):
		"""
		domain_name (required) - string
			The name of the domain itself.

		domain_record_id (required) - integer
			The unique identifier of the domain record.
		"""
		path = f"/v2/domains/{domain_name}/records/{domain_record_id}"

		# Make request
		return self._api._make_get(path, None)


	def update_record(self, domain_name, domain_record_id, type, **kwargs):
		"""
		domain_name (required) - string
			The name of the domain itself.

		domain_record_id (required) - integer
			The unique identifier of the domain record.

		type (required) - string
			The type of the DNS record. For eaxmple, A, CNAME, TXT, ...

		name - string
			The host name, alias, or service being defined by the
			record.

		data - string
			Variable data depending on record type. For example, the
			"data" value for an A record would be the IPv4 address to
			which the domain will be mapped. For a CAA record, it would
			contain the domain name of the CA being granted permission
			to issue cretificates.

		priority - integer, Nullable
			The priority for SRV and MX records.

		port - integer, Nullable
			The port for SRV records.

		ttl - integer
			This value is the time to live for the record, in seconds.
			This defines the time frame that clients can cache queried
			information before a refresh should be requested.

		weight - integer, Nullable
			The weight for SRV records.

		flags - integer, Nullable
			An unsigned integer between 0-255 used for CAA records.

		tag - string, Nullable
			The parameter tag for CAA records. Valid values are "issue",
			"issuewild", or "iodef".
		"""
		path = f"/v2/domains/{domain_name}/records/{domain_record_id}"

		# Required and optional with defaults
		payload = {
			"type": type
		}

		# Optional with no defaults
		name = kwargs.get("name", None)
		if name is not None:
			payload.update({"name": name})
		data = kwargs.get("data", None)
		if data is not None:
			payload.update({"data": data})
		priority = kwargs.get("priority", None)
		if priority is not None:
			payload.update({"priority": priority})
		port = kwargs.get("port", None)
		if port is not None:
			payload.update({"port": port})
		ttl = kwargs.get("ttl", None)
		if ttl is not None:
			payload.update({"ttl": ttl})
		weight = kwargs.get("weight", None)
		if weight is not None:
			payload.update({"weight": weight})
		flags = kwargs.get("flags", None)
		if flags is not None:
			payload.update({"flags": flags})
		tag = kwargs.get("tag", None)
		if tag is not None:
			payload.update({"tag": tag})

		# Make request
		return self._api._make_put(path, payload)


	def delete_record(self, domain_name, domain_record_id):
		"""
		domain_name (required) - string
			The name of the domain itself.

		domain_record_id (required) - integer
			The unique identifier of the domain record.
		"""
		path = f"/v2/domains/{domain_name}/records/{domain_record_id}"

		# Make request
		return self._api._make_delete(path, None)



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
		params = {
			"per_page": kwargs.get("per_page", 20),
			"page": kwargs.get("page", 1)
		}

		# Optional with no defaults
		tag_name = kwargs.get("tag_name", None)
		if tag_name is not None:
			params.update({"tag_name": tag_name})

		# Make request
		return self._api._make_get(path, params)


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


	def create_multiple(self, **kwargs):
		...


	def delete_by_tag(self, tag_name):
		"""
		tag_name (required) - string
			Specifies Droplets to be deleted by tag.
		"""
		path = "/v2/droplets"

		# Required and optional with defaults
		params = {
			"tag_name": tag_name
		}

		# Make request
		return self._api._make_delete(path, params, no_resp_on_success=True)


	def get(self, droplet_id):
		"""
		droplet_id (required) - integer [>=1]
			A unique identifier for a Droplet instance.
		"""
		path = f"/v2/droplets/{droplet_id}"

		# Make request
		return self._api._make_get(path, None)


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
