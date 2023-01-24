import supervisor
import usb_hid
import usb_cdc
import storage

from board import GP3, GP19
from digitalio import DigitalInOut, Direction, Pull

supervisor.set_next_stack_limit(4096 + 4096)

# if B1 is pressed, don't disable cdc
c = DigitalInOut(GP3)
r = DigitalInOut(GP19)

c.switch_to_output(value=True)
r.switch_to_input(pull=Pull.DOWN)

if not r.value:
    storage.disable_usb_drive()
    usb_cdc.disable()

usb_hid.enable(boot_device=1)

r.deinit()
c.deinit()
