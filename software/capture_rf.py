"""
Utility: Capture the motorized screen remote's RF signal.

How to use:
  1. Connect the 433MHz RF receiver (MX-RM-5V) to the Pi
  2. Run: python3 capture_rf.py
  3. Press the UP button on the screen's remote several times
  4. Press Ctrl+C to stop
  5. The signal is saved to config.json automatically
"""

import json
import os
import time
from rpi_rf import RFDevice

CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")


def main():
    with open(CONFIG_PATH) as f:
        config = json.load(f)

    rx_pin = config["gpio"]["rf_rx_pin"]

    print("=" * 50)
    print("  RF Signal Capture")
    print("=" * 50)
    print()
    print(f"  Listening on GPIO {rx_pin}...")
    print("  Press the UP button on the screen's remote.")
    print("  Press it 3-5 times for reliable capture.")
    print("  Press Ctrl+C when done.")
    print()

    device = RFDevice(rx_pin)
    device.enable_rx()

    last_time = 0
    signals = []

    try:
        while True:
            if device.rx_code_timestamp != last_time:
                last_time = device.rx_code_timestamp
                code = device.rx_code
                protocol = device.rx_proto
                pulse_length = device.rx_pulselength

                print(f"  Received: code={code}, protocol={protocol}, pulse_length={pulse_length}")
                signals.append({
                    "code": code,
                    "protocol": protocol,
                    "pulse_length": pulse_length
                })
            time.sleep(0.01)
    except KeyboardInterrupt:
        pass

    device.cleanup()

    if not signals:
        print("\n  No signals captured. Check wiring and try again.")
        return

    # Use the most frequently received code (pressing multiple times filters noise)
    codes = [s["code"] for s in signals]
    most_common = max(set(codes), key=codes.count)
    signal = next(s for s in signals if s["code"] == most_common)

    print()
    print(f"  Saving signal: code={signal['code']}, protocol={signal['protocol']}, pulse_length={signal['pulse_length']}")

    config["rf_signal"] = signal
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=4)

    print("  Saved to config.json!")


if __name__ == "__main__":
    main()
