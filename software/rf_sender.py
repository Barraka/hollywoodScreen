"""
433MHz RF transmitter using rpi-rf.
Replays a previously captured signal to control the motorized projector screen.
"""

from rpi_rf import RFDevice


class RFSender:
    def __init__(self, gpio_pin, rf_config):
        """
        gpio_pin:   BCM pin number connected to FS1000A data pin.
        rf_config:  Dict with "code", "protocol", "pulse_length" from config.
        """
        self.code = rf_config["code"]
        self.protocol = rf_config.get("protocol", 1)
        self.pulse_length = rf_config.get("pulse_length", 350)

        self.device = RFDevice(gpio_pin)
        self.device.enable_tx()
        self.device.tx_proto = self.protocol
        self.device.tx_pulselength = self.pulse_length

    def send(self, repeat=5):
        """Send the RF signal. Repeats multiple times for reliability."""
        for _ in range(repeat):
            self.device.tx_code(self.code, self.protocol, self.pulse_length)

    def cleanup(self):
        """Release RF device resources."""
        self.device.cleanup()
