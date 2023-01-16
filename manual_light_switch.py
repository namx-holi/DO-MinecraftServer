"""
Useful script to cycle the lightbox to what it should be before
rebooting
"""
from pi_app import LightboxState, LightboxInterface

interface = LightboxInterface()
interface._to_next_light_state()
interface.close()
