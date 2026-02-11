"""
Utility: Learn IR remote button codes.

How to use:
  1. Connect the IR receiver (TSOP38238) to the Pi
  2. Run: python3 learn_remote.py
  3. Point the TV remote at the IR receiver
  4. Press each button when prompted
  5. Codes are saved to config.json automatically
"""

import json
import os
import time

CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

BUTTONS = ["power", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]


def main():
    with open(CONFIG_PATH) as f:
        config = json.load(f)

    from ir_receiver import IRReceiver

    ir_pin = config["gpio"]["ir_pin"]
    # Pass empty codes — we're in learning mode
    ir = IRReceiver(ir_pin, {})

    print("=" * 50)
    print("  IR Remote Learning")
    print("=" * 50)
    print()
    print("  Point the remote at the IR receiver.")
    print("  Press each button when prompted.")
    print()

    learned = {}

    for button in BUTTONS:
        print(f"  Press the [{button.upper()}] button...")

        while True:
            h = ir.get_raw_hash()
            if h is not None:
                learned[button] = h
                print(f"    -> Captured: {h}")
                time.sleep(0.5)
                # Flush any pending repeat signals
                ir.get_raw_hash()
                break
            time.sleep(0.01)

    ir.cleanup()

    config["ir_codes"] = learned
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=4)

    print()
    print("  All buttons learned! Saved to config.json.")
    print()
    print("  You can now run: python3 main.py")


if __name__ == "__main__":
    main()
