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



OUTPUT_PIN_MAP = {
	"server_indicator": 8
}

OUTPUT_PIN_INITIAL_STATE = GPIO.LOW



class PiIndicator:

	def __init__(self, input_pin_map={}, output_pin_map={}):
		print("Initialising indicator pins")

		# Save state of all pins in pin map
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
		for pin in self.output_pin_map.values():
			print(f"Setting up pin {pin} as output")
			GPIO.setup(pin, GPIO.OUT, initial=OUTPUT_PIN_INITIAL_STATE)


	def turn_on_output(self, tag):
		if tag not in self.output_pins:
			raise Exception("Given output pin tag not in output pin map")

		print(self.output_state_map)

		self.output_state_map[tag] = GPIO.HIGH
		GPIO.output(self.output_pin_map[tag], GPIO.HIGH)


	def turn_off_output(self, tag):
		if tag not in self.output_pins:
			raise Exception("Given output pin tag not in output pin map")

		print(self.output_state_map)

		self.output_state_map[tag] = GPIO.LOW
		GPIO.output(self.output_pin_map[tag], GPIO.LOW)


	def toggle_output(self, tag):
		if tag not in self.output_pins:
			raise Exception("Given output pin tag not in output pin map")

		print(self.output_state_map)

		# If they go low, we go high
		if self.output_state_map[tag] == GPIO.LOW:
			self.turn_on_output(tag)
		else:
			self.turn_off_output(tag)
