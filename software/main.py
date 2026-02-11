"""
Mission: Hollywood — Cinema Room Screen Prop
Main application: white noise display, code entry via IR remote, RF screen trigger.

Can be tested on PC with keyboard:
  P or Space = Power    |    0-9 = Digit keys
  R = GM Reset           |    U = GM Manual screen up
  Escape = Quit
"""

import pygame
import numpy as np
import json
import sys
import os
import time

# --- States ---
WHITENOISE = "whitenoise"
CODE_ENTRY = "code_entry"
SUCCESS = "success"
ERROR = "error"

# --- Try importing Pi-specific modules ---
PI_AVAILABLE = False
try:
    from ir_receiver import IRReceiver
    from rf_sender import RFSender
    PI_AVAILABLE = True
except ImportError:
    pass


class App:
    def __init__(self):
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
        with open(config_path) as f:
            self.config = json.load(f)

        # Init pygame
        pygame.init()
        display_conf = self.config["display"]

        if display_conf.get("fullscreen", True) and PI_AVAILABLE:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            self.width, self.height = self.screen.get_size()
        else:
            self.width = display_conf.get("width", 1280)
            self.height = display_conf.get("height", 720)
            self.screen = pygame.display.set_mode((self.width, self.height))

        pygame.display.set_caption("Mission: Hollywood")
        pygame.mouse.set_visible(False)

        # Noise surface — smaller resolution scaled up for retro TV static look
        self.noise_scale = 4
        self.noise_w = self.width // self.noise_scale
        self.noise_h = self.height // self.noise_scale
        self.noise_surface = pygame.Surface((self.noise_w, self.noise_h))

        # Fonts
        self.font_large = pygame.font.Font(None, 80)
        self.font_code = pygame.font.Font(None, 120)
        self.font_error = pygame.font.Font(None, 70)

        # State
        self.state = WHITENOISE
        self.entered_code = ""
        self.secret_code = self.config["secret_code"]
        self.error_time = 0
        self.success_time = 0

        # IR receiver (Pi only)
        self.ir = None
        if PI_AVAILABLE:
            try:
                self.ir = IRReceiver(
                    self.config["gpio"]["ir_pin"],
                    self.config["ir_codes"]
                )
            except Exception as e:
                print(f"IR receiver init failed: {e}")

        # RF sender (Pi only)
        self.rf = None
        if PI_AVAILABLE:
            rf_conf = self.config["rf_signal"]
            if rf_conf.get("code"):
                try:
                    self.rf = RFSender(
                        self.config["gpio"]["rf_tx_pin"],
                        rf_conf
                    )
                except Exception as e:
                    print(f"RF sender init failed: {e}")

    # --- Input handling ---

    def handle_button(self, button):
        """Handle a decoded button press (from IR or keyboard)."""
        if self.state == WHITENOISE:
            if button == "power":
                self.state = CODE_ENTRY
                self.entered_code = ""

        elif self.state == CODE_ENTRY:
            if button == "power":
                self.state = WHITENOISE
                self.entered_code = ""
            elif button in "0123456789":
                self.entered_code += button
                if len(self.entered_code) == 4:
                    if self.entered_code == self.secret_code:
                        self.state = SUCCESS
                        self.success_time = time.time()
                        if self.rf:
                            self.rf.send()
                    else:
                        self.state = ERROR
                        self.error_time = time.time()

    def handle_keyboard(self, key):
        """Map keyboard keys to buttons for PC testing and GM controls."""
        # GM controls (always active)
        if key == pygame.K_r:
            self.state = WHITENOISE
            self.entered_code = ""
            print("[GM] Reset to white noise")
            return
        if key == pygame.K_u:
            print("[GM] Manual screen UP")
            if self.rf:
                self.rf.send()
            return

        # Player controls
        mapping = {
            pygame.K_p: "power",
            pygame.K_SPACE: "power",
            pygame.K_0: "0", pygame.K_KP0: "0",
            pygame.K_1: "1", pygame.K_KP1: "1",
            pygame.K_2: "2", pygame.K_KP2: "2",
            pygame.K_3: "3", pygame.K_KP3: "3",
            pygame.K_4: "4", pygame.K_KP4: "4",
            pygame.K_5: "5", pygame.K_KP5: "5",
            pygame.K_6: "6", pygame.K_KP6: "6",
            pygame.K_7: "7", pygame.K_KP7: "7",
            pygame.K_8: "8", pygame.K_KP8: "8",
            pygame.K_9: "9", pygame.K_KP9: "9",
        }
        button = mapping.get(key)
        if button:
            self.handle_button(button)

    # --- Rendering ---

    def render_whitenoise(self):
        """Render TV static noise."""
        noise = np.random.randint(0, 256, (self.noise_w, self.noise_h), dtype=np.uint8)
        noise_rgb = np.stack([noise, noise, noise], axis=-1)
        pygame.surfarray.blit_array(self.noise_surface, noise_rgb)
        scaled = pygame.transform.scale(self.noise_surface, (self.width, self.height))
        self.screen.blit(scaled, (0, 0))

    def render_code_entry(self):
        """Render code entry screen with prompt and input display."""
        self.screen.fill((0, 0, 0))

        # Prompt text
        text = self.font_large.render("Enterez le code:", True, (255, 255, 255))
        rect = text.get_rect(center=(self.width // 2, self.height // 2 - 60))
        self.screen.blit(text, rect)

        # Input display: show asterisks for entered digits, underscores for remaining
        display = ""
        for i in range(4):
            if i < len(self.entered_code):
                display += "* "
            else:
                display += "_ "

        code_text = self.font_code.render(display.strip(), True, (255, 255, 255))
        code_rect = code_text.get_rect(center=(self.width // 2, self.height // 2 + 60))
        self.screen.blit(code_text, code_rect)

    def render_error(self):
        """Render error message, then return to code entry after 2 seconds."""
        self.screen.fill((0, 0, 0))

        text = self.font_error.render("Code incorrect", True, (255, 50, 50))
        rect = text.get_rect(center=(self.width // 2, self.height // 2))
        self.screen.blit(text, rect)

        if time.time() - self.error_time > 2:
            self.state = CODE_ENTRY
            self.entered_code = ""

    def render_success(self):
        """Render black screen after correct code (screen is rolling up)."""
        self.screen.fill((0, 0, 0))

    # --- Main loop ---

    def run(self):
        clock = pygame.time.Clock()
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    else:
                        self.handle_keyboard(event.key)

            # Poll IR receiver
            if self.ir:
                button = self.ir.check()
                if button:
                    self.handle_button(button)

            # Render current state
            if self.state == WHITENOISE:
                self.render_whitenoise()
            elif self.state == CODE_ENTRY:
                self.render_code_entry()
            elif self.state == ERROR:
                self.render_error()
            elif self.state == SUCCESS:
                self.render_success()

            pygame.display.flip()
            clock.tick(15)

        # Cleanup handled by caller's try/finally


if __name__ == "__main__":
    app = App()
    try:
        app.run()
    finally:
        if app.ir:
            app.ir.cleanup()
        if app.rf:
            app.rf.cleanup()
        pygame.quit()
