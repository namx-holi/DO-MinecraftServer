
import time
import traceback
from enum import Enum

from server_handler import ServerHandler


# Try import GPIO, and if it doesn't exist, define a stub for it.
try:
	import RPi.GPIO as GPIO
except ImportError:
	class GPIO_Stub:
		LOW = 0
		HIGH = 1
		def __getattr__(self, func_name):
			print(f"GPIO.{func_name} stub")
			def func(*args, **kwargs):
				print(f"  args={args}, kwargs={kwargs}")
				return None
			return func

	print("Using GPIO_Stub")
	GPIO = GPIO_Stub()


# Stub for ServerHandler to use for debugging. Useful to not start up
#  the actual server.
class Stub_ServerHandler:
	INTERNET_CONNECTIVITY_WAIT = 3 # seconds
	START_SERVER_WAIT = 10 # seconds
	POLL_SERVER_WAIT = 10 # seconds
	STOP_SERVER_WAIT = 10 # seconds

	@classmethod
	def wait_until_internet_connectivity(cls):
		print(f" [*] Stub for wait_until_internet_connectivity. Sleeping {cls.INTERNET_CONNECTIVITY_WAIT} seconds")
		time.sleep(cls.INTERNET_CONNECTIVITY_WAIT)
		print(f" [*] Done!")

	@classmethod
	def start_server(cls):
		print(f" [*] Stub for start_server. Sleeping {cls.START_SERVER_WAIT} seconds")
		time.sleep(cls.START_SERVER_WAIT)
		print(f" [*] Done!")
		return True

	@classmethod
	def poll_server(cls):
		print(f" [*] Stub for poll_server. Sleeping {cls.POLL_SERVER_WAIT} seconds")
		time.sleep(cls.POLL_SERVER_WAIT)
		print(f" [*] Done!")
		return None

	@classmethod
	def stop_server(cls):
		print(f" [*] Stub for stop_server. Sleeping {cls.STOP_SERVER_WAIT} seconds")
		time.sleep(cls.STOP_SERVER_WAIT)
		print(f" [*] Done!")
		return True
# Uncomment following line if debugging to not actually start up server
# ServerHandler = Stub_ServerHandler


# Time taken to supply a falling edge to light box
PIN_FALLING_EDGE_TIME = 0.1 # Seconds

# Minimum time until a falling edge can be given again
FALLING_EDGE_COOLDOWN = 0.5 # Seconds



class LightboxState(Enum):
	OFF = 0
	ON = 1
	FLASHING = 2



class LightboxInterface:

	def __init__(self):
		# Store the pins that will be used for each in/out
		self._button_pin = 22
		self._light_pin = 8

		# Set the start state.
		self._light_state = LightboxState.OFF

		# Clear any existing GPIO setup
		GPIO.cleanup()

		# Use the board numbers for the pins
		GPIO.setmode(GPIO.BOARD)

		# Set up pin numbers and modes with the rpi
		GPIO.setup(self._button_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
		GPIO.setup(self._light_pin, GPIO.OUT, initial=GPIO.LOW)


	def set_state(self, state):
		"""
		Will cycle through the lightbox states until the desired state
		is reached.
		"""
		print(f"Setting lightbox state to {state}")

		# If we are already in that state, no need to do anything
		if state == self._light_state:
			return

		# Otherwise, keep going to the next state until we reach the
		#  desired state.
		while self._light_state != state:
			self._to_next_light_state()


	def button_is_pressed(self):
		# Just checks if the button is currently pressed
		return GPIO.input(self._button_pin) == 1


	def close(self):
		"""
		Shuts down the interface
		"""
		GPIO.cleanup()


	def _to_next_light_state(self):
		"""
		Will simply simulate pressing the button for the normal
		lightbox. Will also update the state.
		"""
		if self._light_state == LightboxState.OFF:
			next_state = LightboxState.ON
		elif self._light_state == LightboxState.ON:
			next_state = LightboxState.FLASHING
		elif self._light_state == LightboxState.FLASHING:
			next_state = LightboxState.OFF

		# Pulse the light switch mode input
		GPIO.output(self._light_pin, GPIO.HIGH)
		time.sleep(PIN_FALLING_EDGE_TIME)
		GPIO.output(self._light_pin, GPIO.LOW)
		time.sleep(FALLING_EDGE_COOLDOWN)

		# Update internal state
		self._light_state = next_state



class App:
	# TODO: Docstring

	def __init__(self):
		# If the Minecraft server is currently running or not
		self.server_running = False

		# Handles starting, polling, and shutting down the Minecraft
		#  server
		self.server_handler = ServerHandler()

		# Handles button presses and the lights on lightbox
		self.lightbox_interface = LightboxInterface()

		# Check what state the Mincraft server is in already, and use
		#  that to update the lightbox
		self._update_current_server_state()


	def _update_current_server_state(self):
		"""
		Checks if the Minecraft server is running or not, and updates
		the lightbox.
		"""

		# Turn on flashing mode to show something's happening
		self.lightbox_interface.set_state(LightboxState.FLASHING)

		# Wait until we have an internet connection
		self.server_handler.wait_until_internet_connectivity()

		# Check what state the server is in (running or not running)
		droplet = self.server_handler.poll_server()
		if droplet:
			self.server_running = True
			self.lightbox_interface.set_state(LightboxState.ON)
		else:
			self.server_running = False
			self.lightbox_interface.set_state(LightboxState.OFF)


	def start_server(self):
		"""
		Starts up the Minecraft server
		"""
		if self.server_running:
			print("Server already running. Not starting again.")
			return

		# Turn on flashing mode to show something's happening
		self.lightbox_interface.set_state(LightboxState.FLASHING)

		# Start the Minecraft server
		self.server_handler.start_server()
		# TODO: Above line returns a bool for success. Handle this?

		# Turn on the lightbox fully to show Minecraft server has
		#  started
		self.lightbox_interface.set_state(LightboxState.ON)

		# Flag that the server has started
		self.server_running = True


	def stop_server(self):
		"""
		Stops the Minecraft server
		"""
		if not self.server_running:
			print("Server not running. Won't try stopping server.")
			return

		# Turn on flashing mode to show something's happening
		self.lightbox_interface.set_state(LightboxState.FLASHING)

		# Stop the Minecraft server
		self.server_handler.stop_server()
		# TODO: Above line returns a bool for success. Handle this?

		# Turn off lightbox to show no server is running
		self.lightbox_interface.set_state(LightboxState.OFF)

		# Flag that the server has stopped running
		self.server_running = False


	def loop(self):
		"""
		This runs constantly. Just keeps checking if the button is
		pressed
		"""
		while True:
			# If server start button is pressed, toggle the server
			#  state
			if self.lightbox_interface.button_is_pressed():
				print("Button has been pressed")

				# If server is already running, shut down. Otherwise,
				#  start the server.
				if self.server_running:
					self.stop_server()
				else:
					self.start_server()

			# Wait a little before checking if button is pressed yet
			time.sleep(0.1)


	def close(self):
		"""
		Stops anything being used by this app
		"""
		self.lightbox_interface.close()



# If this file is run as a script, start the app
if __name__ == "__main__":
	app = App()
	try:
		app.loop()
	except Exception:
		print(traceback.format_exc())
	app.close()
