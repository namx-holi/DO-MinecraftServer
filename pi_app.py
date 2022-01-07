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

# Normal imports
import time
from server_handler import ServerHandler


# Name of the indicator that will be used to say server is on
SERVER_ON_INDICATOR_NAME = "server_indicator"
SERVER_TOGGLE_BUTTON_NAME = "server_toggle_btn"


# Output pin map
INPUT_PIN_MAP = {
	SERVER_TOGGLE_BUTTON_NAME: 22
}
OUTPUT_PIN_MAP = {
	SERVER_ON_INDICATOR_NAME: 8
}

# Default state that output pins will start in
OUTPUT_PIN_INITIAL_STATE = GPIO.LOW



class IO_Handler:

	def __init__(self, input_pin_map={}, output_pin_map={}):
		print("Initialising indicator pins")

		# Save state of all pins in pin map
		self.input_pin_map = input_pin_map
		self.input_state_map = {
			x:0
			for x in input_pin_map.keys()}

		self.output_pin_map = output_pin_map
		self.output_state_map = {
			x:OUTPUT_PIN_INITIAL_STATE
			for x in output_pin_map.keys()}

		# Set up pins on the Pi side
		self._setup_pi()


	def _setup_pi(self):
		print("  Setting up GPIO pins")

		# Just make sure nothing is already set up
		GPIO.cleanup()

		# Use board numbers
		GPIO.setmode(GPIO.BOARD)

		# Set up pin numbers and modes
		for pin in self.input_pin_map.values():
			print(f"Setting up pin {pin} as input")
			GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

		for pin in self.output_pin_map.values():
			print(f"Setting up pin {pin} as output")
			GPIO.setup(pin, GPIO.OUT, initial=OUTPUT_PIN_INITIAL_STATE)


	def update_inputs(self):
		for tag in self.input_state_map.keys():
			self.input_state_map[tag] = GPIO.input(self.input_pin_map[tag])


	def check_input(self, tag):
		if tag not in self.input_state_map:
			raise Exception("Given input pin tag not in input pin map")

		return self.input_state_map[tag] == 1


	def turn_on_output(self, tag):
		if tag not in self.output_state_map:
			raise Exception("Given output pin tag not in output pin map")

		self.output_state_map[tag] = GPIO.HIGH
		GPIO.output(self.output_pin_map[tag], GPIO.HIGH)


	def turn_off_output(self, tag):
		if tag not in self.output_state_map:
			raise Exception("Given output pin tag not in output pin map")

		self.output_state_map[tag] = GPIO.LOW
		GPIO.output(self.output_pin_map[tag], GPIO.LOW)


	def toggle_output(self, tag):
		if tag not in self.output_state_map:
			raise Exception("Given output pin tag not in output pin map")

		# If they go low, we go high
		if self.output_state_map[tag] == GPIO.LOW:
			self.turn_on_output(tag)
		else:
			self.turn_off_output(tag)


	def close(self):
		GPIO.cleanup()



class App:

	def __init__(self):
		# Handles starting/stopping server
		self.server_handler = ServerHandler()

		# Handles showing state of server
		self.io_handler = IO_Handler(
			input_pin_map=INPUT_PIN_MAP,
			output_pin_map=OUTPUT_PIN_MAP
		)

		# Check what state the Minecraft server is in already
		droplet = self.server_handler.poll_server()
		if droplet:
			self.server_running = True
			self.io_handler.turn_on_output(SERVER_ON_INDICATOR_NAME)
		else:
			self.server_running = False
			self.io_handler.turn_off_output(SERVER_ON_INDICATOR_NAME)


	def start_server(self):
		if self.server_running:
			print("Server already running. Not starting again.")
			return

		# TODO: Have some sort of indicator showing work.
		...

		start_success = self.server_handler.start_server()
		if start_success:
			self.server_running = True
			self.io_handler.turn_on_output(SERVER_ON_INDICATOR_NAME)
		else:
			# TODO: Have an error LED?
			...


	def stop_server(self):
		if not self.server_running:
			print("Server not running. Won't try stopping server.")
			return

		# TODO: Have some sort of indicator showing work.
		...

		stop_success = self.server_handler.stop_server()
		if stop_success:
			self.server_running = False
			self.io_handler.turn_off_output(SERVER_ON_INDICATOR_NAME)
		else:
			# TODO: Have an error LED?
			...


	def loop(self):
		while True:
			# Update all input states
			self.io_handler.update_inputs()

			# If server toggle button pressed, toggle server state
			if self.io_handler.check_input(SERVER_TOGGLE_BUTTON_NAME):

				# If server already running, shut down. Otherwise, start it!
				if self.server_running:
					# self.stop_server()
					print("stop server")
					time.sleep(3)
					self.server_running = False
				else:
					# self.start_server()
					print("start server")
					time.sleep(3)
					self.server_running = True

			time.sleep(0.1)
