import supervisor
import usb_hid
import usb_cdc
import storage

supervisor.set_next_stack_limit(4096 + 4096)

# storage.disable_usb_drive()
# usb_cdc.disable()
# usb_hid.enable(boot_device=1)
