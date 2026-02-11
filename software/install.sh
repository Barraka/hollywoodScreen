#!/bin/bash
# ==============================================
#  Mission: Hollywood — Screen Prop Setup
#  Run this once on a fresh Raspberry Pi 3B+
# ==============================================

set -e

echo ""
echo "=== Mission: Hollywood — Screen Prop Setup ==="
echo ""

# --- System packages ---
echo "[1/4] Installing system packages..."
sudo apt update
sudo apt install -y python3 python3-pip pigpio

# --- Enable pigpio daemon (needed for IR receiver) ---
echo "[2/4] Enabling pigpio daemon..."
sudo systemctl enable pigpiod
sudo systemctl start pigpiod

# --- Python dependencies ---
echo "[3/4] Installing Python dependencies..."
pip3 install pygame numpy rpi-rf pigpio

# --- Disable screen blanking (prevent HDMI going to sleep) ---
echo "[4/4] Disabling screen blanking..."
# For console mode
sudo raspi-config nonint do_blanking 1 2>/dev/null || true
# For X11 (if running desktop)
if [ -d "$HOME/.config/lxsession/LXDE-pi" ]; then
    AUTOSTART="$HOME/.config/lxsession/LXDE-pi/autostart"
    grep -q "xset s off" "$AUTOSTART" 2>/dev/null || {
        echo "@xset s off" >> "$AUTOSTART"
        echo "@xset -dpms" >> "$AUTOSTART"
        echo "@xset s noblank" >> "$AUTOSTART"
    }
fi

# --- Create systemd service for auto-start ---
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
sudo tee /etc/systemd/system/screen-prop.service > /dev/null <<EOF
[Unit]
Description=Mission Hollywood Screen Prop
After=multi-user.target pigpiod.service
Wants=pigpiod.service

[Service]
Type=simple
User=$USER
Environment=SDL_VIDEODRIVER=kmsdrm
WorkingDirectory=$SCRIPT_DIR
ExecStart=/usr/bin/python3 $SCRIPT_DIR/main.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

echo ""
echo "=== Setup complete! ==="
echo ""
echo "Next steps:"
echo "  1. python3 learn_remote.py    — Learn your IR remote buttons"
echo "  2. python3 capture_rf.py      — Capture screen's RF signal"
echo "  3. python3 main.py            — Test the application"
echo ""
echo "To enable auto-start on boot:"
echo "  sudo systemctl enable screen-prop"
echo "  sudo systemctl start screen-prop"
echo ""
echo "To check status:"
echo "  sudo systemctl status screen-prop"
echo ""
