# Mission: Hollywood — Cinema Room Screen Prop

## Project Overview
Escape room prop for the "Mission: Hollywood" scenario. A Raspberry Pi 3B+ drives a projector showing white noise. Players find an IR remote, press power to reveal a code entry prompt ("Enterez le code:"), and enter a 4-digit code. On success, a 433MHz RF signal triggers a motorized projector screen to roll up, revealing the next part of the room.

## Architecture
- **Platform**: Raspberry Pi 3B+ (Python 3)
- **Display**: pygame + numpy (white noise, code entry UI) → HDMI → projector
- **IR input**: TSOP38238 IR receiver → pigpio (hash-based decoding, protocol-independent)
- **RF output**: FS1000A 433MHz transmitter → rpi-rf (signal replay)
- **RF transmitter placement**: 3m CAT5 cable from Pi to transmitter, placed next to the screen's RF receiver

## Project Structure
```
├── CLAUDE.md               # This file
├── Explanations.txt        # Project brief
├── ShoppingList.md         # Hardware shopping list with specs
├── InstallationSteps.md    # Step-by-step setup guide for the Pi
└── software/
    ├── config.json         # Configuration: secret code, GPIO pins, learned IR/RF codes
    ├── main.py             # Main app: display state machine + input handling
    ├── ir_receiver.py      # IR decoding module (pigpio, hash-based)
    ├── rf_sender.py        # RF signal replay module (rpi-rf)
    ├── capture_rf.py       # Setup utility: capture screen remote RF signal
    ├── learn_remote.py     # Setup utility: learn IR remote button codes
    ├── requirements.txt    # Python dependencies
    └── install.sh          # Pi setup script (deps, pigpio, systemd service)
```

## Key Design Decisions
- **Hash-based IR decoding**: Works with any remote brand/protocol — no need to identify the protocol
- **RF replay over relay**: No need to open the screen casing, keeps hardware clean
- **PC-testable**: main.py falls back to keyboard input when Pi libraries are unavailable (P=power, 0-9=digits, R=reset, U=manual screen up)
- **Auto-start**: systemd service (`screen-prop.service`) with auto-restart on failure

## Configuration
All runtime config lives in `software/config.json`:
- `secret_code`: the 4-digit code players must enter
- `gpio`: pin assignments (IR=17, RF TX=27, RF RX=22)
- `ir_codes`: learned IR remote hashes (populated by `learn_remote.py`)
- `rf_signal`: captured RF signal params (populated by `capture_rf.py`)

## Development Notes
- White noise uses a small numpy array scaled up 4x for retro TV look + performance on Pi
- IR receiver uses FNV-1a hashing of pulse timing ratios
- RF signal is sent 5 times on success for reliability
- Display runs at 15 FPS (sufficient for static noise effect)
