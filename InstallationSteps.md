# Mission: Hollywood — Installation Steps

Step-by-step guide to set up the cinema room prop once you have all the hardware.

---

## Step 1: Prepare the Raspberry Pi

1. **Flash Raspberry Pi OS Lite** (no desktop needed) onto the MicroSD card
   - Download the [Raspberry Pi Imager](https://www.raspberrypi.com/software/)
   - Choose **Raspberry Pi OS Lite (32-bit)**
   - Before flashing, click the gear icon to:
     - Enable SSH
     - Set a username/password (e.g. `pi` / your password)
     - Configure Wi-Fi (so you can access the Pi remotely)
   - Flash to the MicroSD card and insert it into the Pi

2. **Boot the Pi** — plug in power and connect via HDMI to a monitor (or SSH in)

3. **Copy the software folder** onto the Pi:
   ```bash
   # From your laptop, copy via SCP (replace IP with your Pi's address):
   scp -r software/ pi@192.168.x.x:/home/pi/screen/
   ```

4. **Run the install script**:
   ```bash
   ssh pi@192.168.x.x
   cd /home/pi/screen
   chmod +x install.sh
   bash install.sh
   ```
   This installs all dependencies, enables the pigpio daemon, and creates the auto-start service.

---

## Step 2: Wire the Components

All connections go to the Pi's **GPIO header**. No soldering required — use female-to-female dupont jumper wires.

### IR Receiver (TSOP38238)

| IR Receiver Pin | Wire to Pi |
|---|---|
| VCC (left) | Pin 1 — 3.3V |
| GND (middle) | Pin 6 — Ground |
| DATA (right) | Pin 11 — GPIO 17 |

> **Note:** Pin layout may vary by TSOP model. Check your module's datasheet. The pin order above is for TSOP38238 when facing the bump side.

### 433MHz RF Transmitter (FS1000A)

This connects via the **CAT5 cable** (3 wires used out of 8).

| FS1000A Pin | Wire in CAT5 | Wire to Pi |
|---|---|---|
| VCC | Orange/white pair | Pin 2 — 5V |
| GND | Blue/white pair | Pin 9 — Ground |
| DATA | Green/white pair | Pin 13 — GPIO 27 |

> **Tip:** Label both ends of the CAT5 cable so you know which wire is which. Use a multimeter to verify continuity if unsure.

### 433MHz RF Receiver (MX-RM-5V) — Setup only

Only needed temporarily to capture the screen remote's signal. Can be disconnected after.

| MX-RM-5V Pin | Wire to Pi |
|---|---|
| VCC | Pin 4 — 5V |
| GND | Pin 14 — Ground |
| DATA | Pin 15 — GPIO 22 |

### GPIO Pin Summary

```
Pi 3B+ GPIO Header (relevant pins only):

Pin 1  [3.3V]  ← IR VCC          Pin 2  [5V]    ← RF TX VCC (via CAT5)
                                   Pin 4  [5V]    ← RF RX VCC (setup only)
Pin 6  [GND]   ← IR GND
                                   Pin 9  [GND]   ← RF TX GND (via CAT5)
Pin 11 [GPIO17] ← IR DATA
Pin 13 [GPIO27] ← RF TX DATA (via CAT5)
                                   Pin 14 [GND]   ← RF RX GND (setup only)
Pin 15 [GPIO22] ← RF RX DATA (setup only)
```

---

## Step 3: Learn the IR Remote Buttons

1. Make sure the IR receiver is wired up
2. SSH into the Pi (or connect keyboard):
   ```bash
   cd /home/pi/screen
   python3 learn_remote.py
   ```
3. The script will ask you to press each button one by one:
   - **POWER** — the power/standby button
   - **0** through **9** — the number keys
4. Point the remote at the IR receiver and press each button when prompted
5. Codes are saved to `config.json` automatically

---

## Step 4: Capture the Screen's RF Signal

1. Make sure the RF receiver (MX-RM-5V) is wired up
2. Have the motorized screen's remote in hand
3. Run:
   ```bash
   cd /home/pi/screen
   python3 capture_rf.py
   ```
4. Press the **UP** button on the screen's remote **3-5 times**
5. Press **Ctrl+C** to stop
6. The signal is saved to `config.json` automatically
7. **You can now disconnect the RF receiver** — it's no longer needed

---

## Step 5: Set the Secret Code

Edit `config.json` to set your 4-digit secret code:

```bash
nano /home/pi/screen/config.json
```

Change this line:
```json
"secret_code": "1234",
```

to your desired code, for example:
```json
"secret_code": "0731",
```

---

## Step 6: Test Everything

Run the app manually to verify:
```bash
cd /home/pi/screen
python3 main.py
```

**Test checklist:**
- [ ] White noise appears on the projector
- [ ] Pressing POWER on the IR remote switches to "Enterez le code:"
- [ ] Entering the wrong code shows "Code incorrect" for 2 seconds
- [ ] Entering the correct code triggers the screen to roll up
- [ ] Pressing POWER again from the code screen resets to white noise

**GM keyboard shortcuts** (if a keyboard is connected):
- **R** — Reset to white noise
- **U** — Manually trigger screen up

---

## Step 7: Enable Auto-Start

Once everything works:

```bash
sudo systemctl enable screen-prop
sudo reboot
```

The prop will now start automatically on every boot. No monitor, keyboard, or SSH needed.

**Useful commands:**
```bash
# Check if the service is running
sudo systemctl status screen-prop

# Restart the service
sudo systemctl restart screen-prop

# View logs
journalctl -u screen-prop -f

# Stop the service temporarily
sudo systemctl stop screen-prop
```

---

## Step 8: Install in the Room

1. **Mount the projector** at the back of the room, aimed at the screen
2. **Route the CAT5 cable** from the Pi to the screen — along the wall/ceiling, hidden
3. **Place the FS1000A transmitter** at the end of the CAT5 cable, right next to the screen's receiver (usually in the casing on one side)
4. **Hide the Pi** near the projector (in a ceiling void, behind furniture, etc.)
5. **Connect**: Pi → HDMI → Projector, Pi → CAT5 → RF Transmitter
6. **Power everything on** and verify the prop runs automatically
7. **Hide the IR remote** somewhere in the room for players to find

---

## Troubleshooting

| Problem | Solution |
|---|---|
| No white noise on projector | Check HDMI connection, make sure service is running (`systemctl status screen-prop`) |
| IR remote not responding | Re-run `learn_remote.py`, check IR receiver wiring, make sure pigpiod is running (`sudo systemctl status pigpiod`) |
| Screen doesn't roll up on correct code | Re-run `capture_rf.py`, move RF transmitter closer to screen receiver, check CAT5 wiring |
| App crashes on boot | Check logs with `journalctl -u screen-prop -f`, verify `config.json` has all learned codes |
| Screen blanks after a while | Run `sudo raspi-config` → Display Options → Screen Blanking → Off |
