"""
IR remote receiver using pigpio.
Uses hash-based decoding — works with any remote brand and protocol.
Button codes are learned during setup with learn_remote.py.
"""

import pigpio
import time


class IRReceiver:
    def __init__(self, gpio_pin, ir_codes, glitch_filter=150, timeout_ms=50):
        """
        gpio_pin:       BCM pin number connected to IR receiver data pin.
        ir_codes:       Dict of {"button_name": hash_value} from config.
        glitch_filter:  Ignore edges shorter than this (microseconds).
        timeout_ms:     Signal end timeout (milliseconds).
        """
        self.gpio = gpio_pin
        self.timeout_ms = timeout_ms

        # Build reverse lookup: hash -> button name
        self.hash_to_button = {}
        for button, code in ir_codes.items():
            if code is not None:
                self.hash_to_button[code] = button

        # Connect to pigpio daemon
        self.pi = pigpio.pi()
        if not self.pi.connected:
            raise RuntimeError("Cannot connect to pigpio daemon. Run: sudo pigpiod")

        self.pi.set_mode(gpio_pin, pigpio.INPUT)
        self.pi.set_glitch_filter(gpio_pin, glitch_filter)

        # Internal state
        self._edges = []
        self._last_tick = 0
        self._last_hash = None
        self._last_hash_time = 0
        self._pending = None

        # Start listening
        self._cb = self.pi.callback(gpio_pin, pigpio.EITHER_EDGE, self._edge_callback)
        self.pi.set_watchdog(gpio_pin, timeout_ms)

    def _edge_callback(self, gpio, level, tick):
        """Called by pigpio on every edge change or watchdog timeout."""
        if level == pigpio.TIMEOUT:
            # No edges for timeout_ms — signal is complete
            if len(self._edges) > 10:
                h = self._compute_hash()
                now = time.time()
                # Debounce: ignore repeated signals within 300ms
                if h != self._last_hash or (now - self._last_hash_time) > 0.3:
                    self._pending = h
                    self._last_hash = h
                    self._last_hash_time = now
            self._edges = []
            self.pi.set_watchdog(self.gpio, 0)
        else:
            # Record edge timing
            if self._last_tick:
                self._edges.append(pigpio.tickDiff(self._last_tick, tick))
            self._last_tick = tick
            self.pi.set_watchdog(self.gpio, self.timeout_ms)

    def _compute_hash(self):
        """Compute a hash from pulse timing ratios — protocol independent."""
        if len(self._edges) < 4:
            return None

        h = 2166136261  # FNV-1a 32-bit offset basis

        for i in range(0, len(self._edges) - 2, 2):
            mark = self._edges[i]
            space = self._edges[i + 1]

            if space > 0:
                ratio = mark / space
                if ratio < 0.5:
                    bit = 0
                elif ratio < 1.5:
                    bit = 1
                else:
                    bit = 2
            else:
                bit = 1

            h = ((h ^ bit) * 16777619) & 0xFFFFFFFF

        return h

    def check(self):
        """Poll for decoded button press. Returns button name or None."""
        if self._pending is not None:
            h = self._pending
            self._pending = None
            return self.hash_to_button.get(h)
        return None

    def get_raw_hash(self):
        """Poll for raw hash value (used by learn_remote.py). Returns int or None."""
        if self._pending is not None:
            h = self._pending
            self._pending = None
            return h
        return None

    def cleanup(self):
        """Release pigpio resources."""
        self._cb.cancel()
        self.pi.set_watchdog(self.gpio, 0)
        self.pi.stop()
