# Mission: Hollywood — Cinema Room Prop

## Shopping List

### Electronics (Pi Setup)

| Item | Notes | Approx. Price |
|---|---|---|
| Raspberry Pi 3B+ | Main controller | ~35 EUR |
| MicroSD card (16GB+) | For Raspberry Pi OS + software | ~8 EUR |
| Pi power supply (5V 2.5A, micro USB) | Official recommended for reliability | ~10 EUR |
| Pi case | Clean look for professional setting | ~8 EUR |
| TSOP38238 IR receiver | 3 pins, no soldering needed with dupont wires | ~2 EUR |
| 433MHz TX+RX pair (FS1000A + MX-RM-5V) | Usually sold as a kit | ~3 EUR |
| Dupont jumper wires (female-to-female) | ~10 wires is plenty | ~3 EUR |
| CAT5 ethernet cable (~3m) | To run VCC/GND/DATA from Pi to RF transmitter placed near the screen | ~3 EUR |

**Subtotal electronics: ~72 EUR**

### AV Equipment

| Item | Notes | Approx. Price |
|---|---|---|
| Projector (HDMI input) | Standard throw ratio 1.2:1 to 1.5:1 for 3m distance, 3000+ lumens, LED lamp preferred, 720p is sufficient | 150-250 EUR |
| Motorized rollable projector screen (with 433MHz RF remote) | **Confirm 433MHz frequency before buying** | Varies |
| HDMI cable (~3m) | From Pi/projector at back of room to screen side | ~8 EUR |
| IR TV remote | Any cheap universal remote with power button + number keys (0-9) | ~5 EUR |

---

## Before Buying — Checklist

- [ ] **Motorized screen remote frequency**: Must be 433MHz (most are, but some use 315MHz or other). Check specs or ask the seller.
- [ ] **Projector throw ratio**: Look for 1.2:1 to 1.5:1 for a ~90-100" image at 3m distance.
- [ ] **Projector lamp type**: Prefer LED (20,000-30,000h lifespan) over traditional bulb (3,000-5,000h) for commercial daily use.
- [ ] **HDMI cable length**: Measure the exact distance from Pi to projector.
- [ ] **CAT5 cable length**: Measure the exact distance from Pi to where the RF transmitter will sit (next to the screen casing).
- [ ] **Room power outlets**: Ensure power is accessible for the Pi, projector, and motorized screen.

---

## How It All Connects

```
[Back of room]                                         [Screen side]

                         HDMI
  [Raspberry Pi 3B+] ─────────────→ [Projector]       [Motorized Rollable Screen]
       │    │                            │                    ↑ RF signal
       │    │ GPIO (3 wires)             │ projects onto      │
       │    │                            ↓                    │
       │    └→ [IR Receiver]         ┌────────────┐     [FS1000A RF TX]
       │                             │   Screen    │          ↑
       │                             │   Image     │          │
       └── CAT5 cable (~3m) ────────────────────────────────→─┘
           (VCC, GND, DATA)

  [IR TV Remote] ·····→ [IR Receiver]
  (held by players)
```

**Note:** The RF transmitter is placed right next to the screen's built-in RF receiver via the CAT5 cable, ensuring a strong and reliable signal with no interference issues.

---

## How It Works (Player Experience)

1. Screen is **down**, projector shows **white noise** (static)
2. Players find an **IR TV remote** somewhere in the room
3. They press **Power** on the remote
4. White noise stops, screen displays **"Enterez le code:"**
5. Players enter the correct **4-digit code** using the remote's number keys
6. The Pi sends the **RF "UP" signal** via the transmitter placed next to the screen
7. The screen **rolls up**, revealing the next part of the escape room

---

## Fallback Plan

If the 433MHz RF replay proves unreliable during testing:
- Open the screen's **RF remote** (not the screen casing itself)
- Solder 2 wires across the "UP" button contacts
- Connect to a relay module on the Pi (~5 EUR extra)
- Route via the same CAT5 cable already in place
- Same result, the screen hardware stays untouched
