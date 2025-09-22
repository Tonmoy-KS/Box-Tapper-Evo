# Box tapper: Evo
import pygame
import random
import math
import os
import time
import json


# SETTINGS & CONSTANTS

# --- Display (change these if needed)---
WIDTH = 1280
HEIGHT = 720
FPS = 60

# --- Colors ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (150, 150, 150)
DARK_GRAY = (50, 50, 50)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
GOLD = (255, 215, 0)
NEBULA_BLUE = (50, 50, 200)
NEBULA_PURPLE = (150, 50, 200)
GALAXY_INDIGO = (75, 0, 130)
STARLIGHT_CYAN = (100, 200, 255)
COSMIC_MAGENTA = (200, 50, 200)
AURORA_GREEN = (50, 200, 150)

# --- Terminal Color Codes ---
XTERM_BLUE = "\033[94m"
XTERM_YELLOW = "\033[93m"
XTERM_RESET = "\033[0m"

# --- Game Mechanics ---
BASE_BOX_HEALTH = 1
BOSS_HEALTH_MULTIPLIER = 2
MAX_HIGH_SCORES = 5
MAX_LEVEL_CLASSIC = 100
ASTEROID_START_LEVEL = 30

# --- Cheat Codes---
CHEAT_SEQUENCES = {
    "INVINCIBILITY": ["hit_box", "hit_empty", "hit_box", "hit_box", "hit_empty", "hit_empty", "hit_box", "hit_box", "hit_empty"],
    "INSTANT_KILL": ["hit_box", "hit_box", "hit_empty", "hit_empty", "hit_box", "hit_box", "hit_box", "hit_empty", "hit_empty", "hit_box"],
    "DOUBLE_SCORE": ["hit_empty", "hit_box", "hit_empty", "hit_empty", "hit_box"],
    "LEVEL_SKIP": ["hit_empty", "hit_empty", "hit_box", "hit_box", "hit_empty", "hit_box", "hit_box"],
    "HUD_TOGGLE": ["hit_empty", "hit_empty", "hit_box", "hit_box", "hit_empty", "hit_empty", "hit_empty", "hit_box", "hit_box", "hit_empty"],
    "DEBUG_MODE": ["hit_box", "hit_empty", "hit_empty", "hit_box", "hit_empty","hit_box", "hit_empty", "hit_empty", "hit_box", "hit_empty"]
}


# INITIALIZATION
pygame.init()
pygame.mixer.init()
os.environ['SDL_VIDEO_CENTERED'] = '1'
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Box Tapper: Evolution V.1.8.0")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)
big_font = pygame.font.Font(None, 72)
button_font = pygame.font.Font(None, 48)
tutorial_font = pygame.font.Font(None, 42)
stats_font = pygame.font.Font(None, 48)

# --- Music 
# (Fully User Customizable Background Music) ---
music_loaded = False  # Flag to check if music is ready
try:
    pygame.mixer.music.load("background_music.wav")
    music_loaded = True  # Set flag to True on success
    print("Music file 'background_music.wav' loaded successfully.")
except pygame.error as e:
    # If the file is not found or there's another error, print a warning
    print(f"Warning: Could not load 'background_music.wav'. The game will be silent. Error: {e}")

# --- Difficulty Settings ---
DIFFICULTY_SETTINGS = {
    "easy":       {"lives": 100, "health_mod": 0.1, "speed_mod": 0.7, "spawn_mod": 0.5, "asteroid_mod": 0.1, "score_mod": 0.0, "dust_mod": 1.5},
    "beginner":   {"lives": 30, "health_mod": 0.8, "speed_mod": 0.9, "spawn_mod": 0.9, "asteroid_mod": 0.8, "score_mod": 0.75,  "dust_mod": 1.2},
    "casual":     {"lives": 10, "health_mod": 1.0, "speed_mod": 1.0, "spawn_mod": 1.0, "asteroid_mod": 1.0, "score_mod": 1.0,  "dust_mod": 1.0},
    "hardcore":   {"lives": 5,  "health_mod": 1.5, "speed_mod": 1.2, "spawn_mod": 1.2, "asteroid_mod": 1.3, "score_mod": 1.25, "dust_mod": 1.25},
    "insane":     {"lives": 3,  "health_mod": 2.0, "speed_mod": 1.5, "spawn_mod": 1.5, "asteroid_mod": 2.0, "score_mod": 2.0,  "dust_mod": 1.5},
    "demon":      {"lives": 1,  "health_mod": 3.0, "speed_mod": 2.0, "spawn_mod": 2.0, "asteroid_mod": 2.0, "score_mod": 20.0,  "dust_mod": 2.0},
}

DRAMATIC_QUOTES = ["Et tu, Brute?", "I'm melting!", "I am just in a Game!" "Rosebud...", "Tell my story!", "What's in the box?!", "I've seen things...", "Who am I? who created this?", "Farewell, cruel world!"]

# CLASSES

class Tool:
    """Represents a tapper tool with different abilities."""
    def __init__(self, id, level, damage, score_multiplier, is_dev):
        self.id = id
        self.level = level
        self.damage = damage
        self.score_multiplier = score_multiplier
        self.is_dev = is_dev

class Star:
    """A twinkling star in the background."""
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.radius = random.randint(1, 3)
        self.color = WHITE
        self.alpha = random.randint(50, 255)
        self.fade_speed = random.uniform(0.5, 2.0)

    def update(self):
        self.alpha += self.fade_speed
        if self.alpha >= 255 or self.alpha <= 50:
            self.fade_speed *= -1
        self.alpha = max(50, min(255, self.alpha))

    def draw(self, surface):
        star_surf = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(star_surf, (*self.color, int(self.alpha)), (self.radius, self.radius), self.radius)
        surface.blit(star_surf, (self.x - self.radius, self.y - self.radius))

class Nebula:
    """A pulsating nebula for background effects."""
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.radius = random.randint(100, 300)
        self.color = random.choice([NEBULA_BLUE, NEBULA_PURPLE, STARLIGHT_CYAN])
        self.alpha = random.randint(20, 50)
        self.pulse_speed = random.uniform(0.1, 0.5)

    def update(self):
        self.alpha += self.pulse_speed
        if self.alpha >= 50 or self.alpha <= 20:
            self.pulse_speed *= -1
        self.alpha = max(20, min(50, self.alpha))

    def draw(self, surface):
        nebula_surf = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        for r in range(int(self.radius), 0, -1):
            alpha = int(self.alpha * (r / self.radius))
            pygame.draw.circle(nebula_surf, (*self.color, alpha), (self.radius, self.radius), r)
        surface.blit(nebula_surf, (self.x - self.radius, self.y - self.radius))

class Particle:
    """A small particle for explosion effects."""
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-3, 3)
        self.lifespan = random.randint(20, 40)
        self.radius = random.randint(2, 5)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.lifespan -= 1
        self.radius -= 0.1
        return self.lifespan > 0 and self.radius > 0

    def draw(self, surface):
        if self.radius > 0:
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), int(self.radius))

class Asteroid:
    """A moving hazard that the player must avoid clicking."""
    def __init__(self, is_meteor=False):
        if is_meteor:
            self.x = random.randint(0, WIDTH)
            self.y = -20
            self.vx = random.uniform(-1, 1)
            self.vy = random.uniform(8, 12)
        else:
            start_side = random.choice(['left', 'right', 'top', 'bottom'])
            if start_side == 'left':
                self.x, self.y = -20, random.randint(0, HEIGHT)
                self.vx, self.vy = random.uniform(2, 4), random.uniform(-1, 1)
            elif start_side == 'right':
                self.x, self.y = WIDTH + 20, random.randint(0, HEIGHT)
                self.vx, self.vy = random.uniform(-4, -2), random.uniform(-1, 1)
            elif start_side == 'top':
                self.x, self.y = random.randint(0, WIDTH), -20
                self.vx, self.vy = random.uniform(-1, 1), random.uniform(2, 4)
            else: # bottom
                self.x, self.y = random.randint(0, WIDTH), HEIGHT + 20
                self.vx, self.vy = random.uniform(-1, 1), random.uniform(-4, -2)
        self.radius = random.randint(10, 25)
        self.rect = pygame.Rect(self.x-self.radius, self.y-self.radius, self.radius*2, self.radius*2)

    def move(self):
        self.x += self.vx
        self.y += self.vy
        self.rect.center = (self.x, self.y)

    def is_offscreen(self):
        return self.rect.right < 0 or self.rect.left > WIDTH or self.rect.bottom < 0 or self.rect.top > HEIGHT

    def draw(self, surface):
        pygame.draw.circle(surface, DARK_GRAY, self.rect.center, self.radius)
        pygame.draw.circle(surface, GRAY, self.rect.center, self.radius, 2)

class BlackHole:
    """A power-up effect that pulls and destroys boxes."""
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.radius, self.max_radius, self.pull_radius = 10, 80, 300
        self.pull_force, self.grow_speed, self.lifespan = 1.5, 0.5, 5
        self.start_time = time.time()

    def update(self, boxes):
        if self.radius < self.max_radius:
            self.radius += self.grow_speed
        for box in boxes[:]:
            dist_x, dist_y = self.x - box.rect.centerx, self.y - box.rect.centery
            distance = math.hypot(dist_x, dist_y)
            if distance < self.pull_radius:
                if distance < self.radius:
                    damage_box(box, is_black_hole=True)
                else:
                    angle = math.atan2(dist_y, dist_x)
                    box.rect.x += self.pull_force * math.cos(angle)
                    box.rect.y += self.pull_force * math.sin(angle)
        return time.time() - self.start_time < self.lifespan

    def draw(self, surface):
        pygame.draw.circle(surface, BLACK, (self.x, self.y), int(self.radius))
        for i in range(3):
            angle = (time.time() * (i+1) * 2) % (2 * math.pi)
            p_radius = self.radius + 10 + i * 5
            px, py = self.x + p_radius * math.cos(angle), self.y + p_radius * math.sin(angle)
            pygame.draw.circle(surface, NEBULA_PURPLE, (int(px), int(py)), 3)

class Snail:
    """A very slow, harmless creature for Chaos Mode."""
    def __init__(self):
        self.x = -30
        self.y = random.randint(HEIGHT - 100, HEIGHT - 50)
        self.speed = 0.5
        self.rect = pygame.Rect(self.x, self.y, 30, 15)

    def update(self):
        self.x += self.speed
        self.rect.x = self.x

    def draw(self, surface):
        pygame.draw.rect(surface, GOLD, self.rect)

class NyanCat:
    """A mythical creature that brings rainbow boxes."""
    def __init__(self):
        self.y = random.randint(50, HEIGHT - 50)
        self.x = -100
        self.speed = 10
        self.rect = pygame.Rect(self.x, self.y, 80, 50)
        self.trail = []

    def update(self, boxes):
        self.x += self.speed
        self.rect.x = self.x
        self.trail.append(self.rect.copy())
        if len(self.trail) > 20:
            self.trail.pop(0)

        for box in boxes:
            if self.rect.colliderect(box.rect) and box.special_type != "rainbow":
                box.special_type = "rainbow"
                box.color = (random.randint(100,255), random.randint(100,255), random.randint(100,255))

        return self.x < WIDTH + 100

    def draw(self, surface):
        for i, trail_rect in enumerate(self.trail):
            color = (random.randint(0,255), random.randint(0,255), random.randint(0,255))
            pygame.draw.rect(surface, color, trail_rect)
        pygame.draw.rect(surface, COSMIC_MAGENTA, self.rect)

class Box:
    """The main target object for the player to tap."""
    def __init__(self, x, y, width, height, color, health, is_child=False):
        self.rect = pygame.Rect(int(x), int(y), width, height)
        self.color, self.health, self.max_health = color, health, health
        speed_mod = DIFFICULTY_SETTINGS.get(gs.get("difficulty"), {}).get("speed_mod", 1.0)
        self.speed = (5 * speed_mod) * (1.5 if is_child else 1.0)
        self.direction = random.choice([-1, 1])
        self.special_type, self.alpha, self.fade_timer = None, 255, 0
        self.tap_count, self.tap_timer, self.taps_required = 0, 0, 0
        self.is_shrinking, self.shrink_rate, self.min_size = False, 0.25, 20
        self.is_dying, self.death_timer, self.death_quote = False, 0, ""
        self.teleport_timer = time.time() + random.uniform(2, 4)
        self.visible_timer = time.time() + random.uniform(1, 3) # For stealth mode
        self.is_child = is_child
        self.gravity_strength = 0.0  # For gravity box
        if not is_child:
            self.assign_special_type()

    def assign_special_type(self):
        game_mode = gs.get("game_mode", "classic")
        roll = random.random()

        if roll < 0.02:
            self.special_type, self.color, self.health, self.speed = "golden", GOLD, 3, 8
        elif roll < 0.25:
            if game_mode == "chaos":
                choices = ["explosive", "regen", "shrinking", "multi", "splitter", "dramatic", "teleporter", "gravity"]
            else:
                choices = ["explosive", "regen", "shrinking", "multi", "splitter", "gravity"]
            self.special_type = random.choice(choices)

            if self.special_type == "splitter": self.color = GREEN
            if self.special_type == "dramatic": self.color = WHITE
            if self.special_type == "teleporter": self.color = STARLIGHT_CYAN
            if self.special_type == "shrinking": self.is_shrinking = True
            if self.special_type == "multi": self.taps_required = min(1 + gs["level"] // 10, 5)
            if self.special_type == "gravity": self.color = NEBULA_PURPLE; self.gravity_strength = 1.0

    def update(self):
        if self.is_dying:
            if time.time() > self.death_timer:
                self.health = 0 # Mark for removal
            return

        if gs["game_mode"] == "stealth":
            if time.time() > self.visible_timer:
                if self.alpha < 255: self.alpha = 255 # Become fully visible
                elif self.alpha == 255: self.alpha = 10; self.visible_timer = time.time() + random.uniform(2, 5) # Hide again
            else:
                if self.alpha == 255: self.alpha = 10 # Hide it

        if self.special_type == "teleporter" and time.time() > self.teleport_timer:
            self.rect.x = random.randint(0, WIDTH - self.rect.width)
            self.rect.y = random.randint(0, HEIGHT - self.rect.height)
            self.teleport_timer = time.time() + random.uniform(1, 3)

        self.rect.x += self.speed * self.direction
        if self.rect.left <= 0 or self.rect.right >= WIDTH: self.direction *= -1
        if self.special_type == "regen" and self.health < self.max_health: self.health = min(self.health + 0.5/FPS, self.max_health)
        if self.is_shrinking and self.rect.width > self.min_size:
            center = self.rect.center
            self.rect.width = max(self.min_size, self.rect.width - self.shrink_rate)
            self.rect.height = max(self.min_size, self.rect.height - self.shrink_rate)
            self.rect.center = center

        if self.special_type == "gravity":
            for other_box in gs["boxes"]:
                if other_box != self and not other_box.is_dying:
                    dist_x, dist_y = self.rect.centerx - other_box.rect.centerx, self.rect.centery - other_box.rect.centery
                    distance = math.hypot(dist_x, dist_y)
                    if 0 < distance < 200:  # Gravity range
                        angle = math.atan2(dist_y, dist_x)
                        other_box.rect.x += self.gravity_strength * math.cos(angle)
                        other_box.rect.y += self.gravity_strength * math.sin(angle)

    def draw(self, surface):
        current_alpha = self.alpha
        if gs["game_mode"] == "stealth" and self.alpha < 255:
            # Create a brief flash just before becoming visible
            if time.time() > self.visible_timer - 0.2:
                 flash_alpha = max(0, 255 * (0.2 - (self.visible_timer - time.time() - 4.8)))
                 current_alpha = max(self.alpha, flash_alpha)

        box_surf = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        box_surf.fill((*self.color, int(current_alpha)))
        surface.blit(box_surf, self.rect.topleft)

        if self.max_health > 1:
            health_ratio = self.health / self.max_health
            health_bar_width = self.rect.width * health_ratio
            pygame.draw.rect(surface, AURORA_GREEN, (self.rect.x, self.rect.y - 10, health_bar_width, 5))
            pygame.draw.rect(surface, BLACK, (self.rect.x, self.rect.y - 10, self.rect.width, 5), 1)

        if self.special_type == "multi":
            taps_text = font.render(f"{self.tap_count}/{self.taps_required}", True, BLACK)
            surface.blit(taps_text, taps_text.get_rect(center=self.rect.center))

        if self.is_dying:
            quote_surf = font.render(self.death_quote, True, WHITE)
            surface.blit(quote_surf, quote_surf.get_rect(midbottom=self.rect.midtop))

        if self.special_type == "gravity":
            # Draw gravitational aura
            aura_radius = 50 + 10 * math.sin(time.time() * 2)
            pygame.draw.circle(surface, (*NEBULA_PURPLE, 80), self.rect.center, int(aura_radius), 2)

class Boss(Box):
    """A powerful enemy."""
    def __init__(self, x, y, width, height, color, health):
        super().__init__(x, y, width, height, color, health)
        self.dodge_chance = 0.3
        self.phase, self.minions = 1, []

    def update(self):
        super().update()
        for minion in self.minions[:]:
            minion.update()
            if minion.health <= 0:
                self.minions.remove(minion)

    def update_phase(self):
        health_ratio = self.health / self.max_health
        if health_ratio <= 0.5 and self.phase == 1:
            self.phase, self.color, self.dodge_chance = 2, RED, 0.6
        elif health_ratio <= 0.25 and self.phase == 2:
            self.phase, self.speed = 3, self.speed * 2
            for _ in range(3):
                minion_size = (int(self.rect.width * 0.7), int(self.rect.height * 0.7))
                minion = Box(self.rect.centerx, self.rect.centery, *minion_size, NEBULA_PURPLE, 1)
                minion.speed = 3
                self.minions.append(minion)

class Circle(Box):
    """A special target that awards extra lives."""
    def __init__(self, x, y, radius, speed):
        super().__init__(x-radius, y-radius, radius*2, radius*2, YELLOW, 1)
        self.radius, self.speed = radius, speed
        self.direction_x, self.direction_y = random.choice([-1, 1]), random.choice([-1, 1])

    def update(self):
        self.rect.x += self.speed * self.direction_x
        self.rect.y += self.speed * self.direction_y
        if self.rect.left <= 0 or self.rect.right >= WIDTH: self.direction_x *= -1
        if self.rect.top <= 0 or self.rect.bottom >= HEIGHT: self.direction_y *= -1

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, self.rect.center, self.radius)

class PowerUp:
    """A collectible that grants a temporary bonus."""
    def __init__(self, x, y, type):
        self.rect = pygame.Rect(x, y, 40, 40)
        self.type = type
        self.color = {"cosmic":NEBULA_PURPLE, "multi_tap":AURORA_GREEN, "black_hole":DARK_GRAY, "nyan":GRAY, "time_warp":STARLIGHT_CYAN}.get(type, YELLOW)
        self.vortex_angle = 0  # For time_warp animation

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
        char = {"cosmic":"C", "multi_tap":"M", "black_hole":"B", "speed":"S", "nyan":"N", "time_warp":"T"}.get(self.type, self.type[0].upper())
        text = font.render(char, True, WHITE)
        surface.blit(text, text.get_rect(center=self.rect.center))
        if self.type == "time_warp":
            # Draw swirling vortex effect
            for i in range(3):
                angle = (self.vortex_angle + i * 120) % 360
                rad = math.radians(angle)
                px, py = self.rect.centerx + 20 * math.cos(rad), self.rect.centery + 20 * math.sin(rad)
                pygame.draw.circle(surface, WHITE, (int(px), int(py)), 3)
            self.vortex_angle = (self.vortex_angle + 2) % 360

class Button:
    """A clickable UI button."""
    def __init__(self, x, y, width, height, text, color, text_color, hover_color=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text, self.color, self.text_color, self.hover_color = text, color, text_color, hover_color or color

    def draw(self, surface, is_hovered=False):
        if is_hovered:
            pygame.draw.rect(surface, DARK_GRAY, self.rect.inflate(8, 8), border_radius=12)
        pygame.draw.rect(surface, self.hover_color if is_hovered else self.color, self.rect, border_radius=8)
        text_surface = button_font.render(self.text, True, self.text_color)
        surface.blit(text_surface, text_surface.get_rect(center=self.rect.center))

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

# GAME STATE & VARIABLES
def setup_game_variables(difficulty="casual", game_mode="classic"):
    lives = DIFFICULTY_SETTINGS.get(difficulty, {}).get("lives", 10)
    state = {
        "game_state": "main_menu", "game_mode": game_mode, "difficulty": difficulty,
        "level": 1, "lives": lives, "max_lives": lives, "score": 0, "score_multiplier": 1,
        "boxes": [], "stars": [], "asteroids": [], "boss": None, "circle": None, "power_up": None,
        "power_up_active": None, "power_up_timer": 0, "last_boss_speed": 5, "combo": 0, "combo_timer": 0,
        "fog_active": False, "fog_timer": 0, "barrier": None, "hud_active": True, "debug_mode": False,
        "player_sequence": [], "active_cheats": set(), "cursor_pos": [WIDTH//2, HEIGHT//2],
        "high_scores": load_high_scores(), "box_colors": [NEBULA_BLUE, NEBULA_PURPLE, GALAXY_INDIGO, STARLIGHT_CYAN, COSMIC_MAGENTA, AURORA_GREEN, RED],
        "particles": [], "cosmic_dust": 0, "screen_shake": 0, "level_clear_timer": 0, "active_black_hole": None,
        "upgrades": {"damage": 0, "lives": 0, "dust_bonus": 0, "powerup_time": 0},
        "tutorial_stage": 0, "tutorial_objects": [], "tutorial_text": "", "stats": load_stats(),
        "meteor_shower_warning": 0, "meteor_shower_active": 0, "meteor_event_timer": time.time() + 30,
        "chaos_event_timer": time.time() + 15, "screen_flipped": False, "snail": None, "nyan_cat": None,
        "nebulae": [], "achievements": {
            "tap_100_boxes": {"unlocked": False, "condition": lambda stats: stats["boxes_tapped"] >= 100, "reward": 50, "description": "Tap 100 Boxes"},
            "collect_10_powerups": {"unlocked": False, "condition": lambda stats: stats["powerups_collected"] >= 10, "reward": 100, "description": "Collect 10 Power-ups"},
            "defeat_5_bosses": {"unlocked": False, "condition": lambda stats: stats["bosses_defeated"] >= 5, "reward": 200, "description": "Defeat 5 Bosses"},
            "score_10000": {"unlocked": False, "condition": lambda stats: stats["total_score"] >= 10000, "reward": 150, "description": "Score 10,000 Points"}
        }
    }
    state["basic_tapper"] = Tool("basic", 1, 1, 1, False)
    state["cheat_tapper"] = Tool("cheat", 99, 999999, 1000, True)
    state["equipped_tool"] = state["basic_tapper"]
    return state

# HELPER FUNCTIONS
def load_high_scores():
    try:
        with open("highscores.txt", "r") as f:
            return [int(line.strip()) for line in f if line.strip().isdigit()][:MAX_HIGH_SCORES]
    except FileNotFoundError:
        return [0] * MAX_HIGH_SCORES

def save_high_scores():
    gs["high_scores"].append(int(gs["score"]))
    gs["high_scores"] = sorted(list(set(gs["high_scores"])), reverse=True)[:MAX_HIGH_SCORES]
    with open("highscores.txt", "w") as f:
        for hs in gs["high_scores"]:
            f.write(f"{hs}\n")

def load_stats():
    try:
        with open("stats.json", "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"boxes_tapped": 0, "powerups_collected": 0, "snails_harmed": 0, "total_score": 0, "bosses_defeated": 0}

def save_stats():
    with open("stats.json", "w") as f:
        json.dump(gs["stats"], f, indent=4)
    # Check achievements
    for name, ach in gs["achievements"].items():
        if not ach["unlocked"] and ach["condition"](gs["stats"]):
            ach["unlocked"] = True
            gs["cosmic_dust"] += ach["reward"]
            print(f"{XTERM_YELLOW}Achievement Unlocked: {ach['description']} (+{ach['reward']} Dust){XTERM_RESET}")

def start_new_level():
    gs["game_state"] = "playing"
    if gs["game_mode"] == "classic" and gs["level"] > MAX_LEVEL_CLASSIC:
        gs["game_state"] = "victory"
        return
    gs["boxes"], gs["boss"], gs["circle"], gs["asteroids"], gs["snail"] = [], None, None, [], None
    gs["meteor_shower_warning"], gs["meteor_shower_active"] = 0, 0

    if gs["game_mode"] == "boss_rush":
        spawn_boss()
    elif gs["level"] % 10 == 0:
        spawn_circle()
    elif gs["level"] % 5 == 0:
        spawn_boss()
    else:
        spawn_boxes()
    spawn_power_up()
    if not gs["stars"]:
        spawn_stars()

def create_explosion(x, y, color):
    for _ in range(10):
        gs["particles"].append(Particle(x, y, color))

def trigger_screen_shake(intensity=10, duration=15):
    gs["screen_shake"], gs["shake_intensity"] = duration, intensity

# SPAWNING
def spawn_boxes():
    spawn_mod = DIFFICULTY_SETTINGS[gs["difficulty"]]["spawn_mod"]
    if gs["game_mode"] == "chaos":
        spawn_mod *= 3
    num_boxes = int((5 + gs["level"] // 10) * spawn_mod)
    for _ in range(num_boxes):
        size = random.randint(50, 100)
        x, y = random.randint(0, WIDTH - size), random.randint(0, HEIGHT - size)
        color = random.choice(gs["box_colors"])
        health = BASE_BOX_HEALTH * DIFFICULTY_SETTINGS[gs["difficulty"]]["health_mod"]
        gs["boxes"].append(Box(x, y, size, size, color, health))

def spawn_boss():
    level = gs["level"]
    base_size = 200
    size_multiplier = max(0.25, 1 - 0.15 * (level // 5)) if level < 50 else 0.1 + 0.10 * ((level - 50) // 5)
    size = (min(int(base_size * size_multiplier), WIDTH - 20), min(int(base_size * size_multiplier), HEIGHT - 20))
    pos = (WIDTH // 2 - size[0] // 2, HEIGHT // 2 - size[1] // 2)
    health = (BASE_BOX_HEALTH * (BOSS_HEALTH_MULTIPLIER ** (level // 5))) * DIFFICULTY_SETTINGS[gs["difficulty"]]["health_mod"]
    gs["boss"] = Boss(*pos, *size, NEBULA_PURPLE, health)
    gs["last_boss_speed"] = gs["boss"].speed

def spawn_circle():
    gs["circle"] = Circle(WIDTH//2, HEIGHT//2, 40, gs["last_boss_speed"])

def spawn_power_up():
    if random.random() < 0.2:
        x, y = random.randint(0, WIDTH - 40), random.randint(0, HEIGHT - 40)
        types = ["speed", "shield", "freeze", "cosmic", "multi_tap", "black_hole", "time_warp"]
        if gs["game_mode"] == "chaos":
            types.append("nyan")
        gs["power_up"] = PowerUp(x, y, random.choice(types))

def spawn_stars():
    gs["stars"] = [Star() for _ in range(100)]
    gs["nebulae"] = [Nebula() for _ in range(3)]

def spawn_asteroid():
    asteroid_chance = 0.02 * DIFFICULTY_SETTINGS[gs["difficulty"]]["asteroid_mod"]
    if gs["level"] >= ASTEROID_START_LEVEL and len(gs["asteroids"]) < (gs["level"] // 10) and random.random() < asteroid_chance:
        gs["asteroids"].append(Asteroid())

# CHEAT LOGIC
def check_cheat_code():
    seq = tuple(gs["player_sequence"])
    for name, code in CHEAT_SEQUENCES.items():
        if seq == tuple(code) and name not in gs["active_cheats"]:
            activate_cheat(name)
            gs["player_sequence"].clear()
            break

def activate_cheat(name):
    if name == "INVINCIBILITY": gs["active_cheats"].add(name)
    elif name == "INSTANT_KILL": gs["active_cheats"].add(name)
    elif name == "DOUBLE_SCORE": gs["active_cheats"].add(name); gs["score_multiplier"] = 2
    elif name == "LEVEL_SKIP": gs["level"] += 1; start_new_level()
    elif name == "HUD_TOGGLE": gs["hud_active"] = not gs["hud_active"]
    elif name == "DEBUG_MODE":
        gs["debug_mode"] = not gs["debug_mode"]
        gs["equipped_tool"] = gs["cheat_tapper"] if gs["debug_mode"] else gs["basic_tapper"]
    print(f"{XTERM_BLUE}Cheat Activated: {name}{XTERM_RESET}")

# TUTORIAL
def start_tutorial():
    gs["game_state"], gs["tutorial_stage"], gs["tutorial_objects"] = "tutorial", 0, []
    gs["tutorial_text"] = "Welcome to the 'Simple Tutorial' Centre! Click the stationary box to destroy it."
    box = Box(WIDTH//2-50, HEIGHT//2-50, 100, 100, STARLIGHT_CYAN, 1)
    box.speed = 0
    gs["tutorial_objects"].append(box)

def advance_tutorial():
    gs["tutorial_stage"] += 1
    gs["tutorial_objects"] = []
    stage = gs["tutorial_stage"]
    if stage == 1:
        gs["tutorial_text"] = "Good job! Some boxes move. Track and tap this one."
        box = Box(100, HEIGHT//2-50, 80, 80, COSMIC_MAGENTA, 1)
        box.speed = 3
        gs["tutorial_objects"].append(box)
    elif stage == 2:
        gs["tutorial_text"] = "Watch out! AVOID clicking on gray asteroids. They cost a life."
        asteroid = Asteroid()
        asteroid.x, asteroid.y, asteroid.vx, asteroid.vy = WIDTH+20, HEIGHT//2, -3, 0
        gs["tutorial_objects"].append(asteroid)
    elif stage == 3:
        gs["tutorial_text"] = "These are helpful! Collect colorful power-ups for temporary boosts."
        powerup = PowerUp(WIDTH//2-20, HEIGHT//2-20, "shield")
        gs["tutorial_objects"].append(powerup)
    elif stage == 4:
        gs["tutorial_text"] = "You're ready to play! Good luck."
    else:
        gs["game_state"] = "mode_select"

# GAME LOGIC
def update_game_state():
    state = gs["game_state"]
    if state == "tutorial":
        for obj in gs["tutorial_objects"]:
            if isinstance(obj, Box): obj.update()
            elif isinstance(obj, Asteroid): obj.move()
        if gs["tutorial_stage"] == 2 and not gs["tutorial_objects"]:
            advance_tutorial()
        return

    if state == "level_clear":
        if time.time() - gs["level_clear_timer"] > 2:
            gs["level"] += 1
            start_new_level()
        return

    if state != "playing":
        return

    speed_scale = 0.3 if gs["power_up_active"] == "time_warp" else 1.0

    if gs["meteor_shower_warning"] > 0 and time.time() > gs["meteor_shower_warning"]:
        gs["meteor_shower_warning"] = 0
        gs["meteor_shower_active"] = time.time() + 5
        for _ in range(25):
            gs["asteroids"].append(Asteroid(is_meteor=True))
    if gs["meteor_shower_active"] > 0 and time.time() > gs["meteor_shower_active"]:
        gs["meteor_shower_active"] = 0
    if time.time() > gs.get("meteor_event_timer", 0):
        if random.random() < 0.1: # 10% chance every 20-40 seconds
            gs["meteor_shower_warning"] = time.time() + 3
        gs["meteor_event_timer"] = time.time() + random.uniform(20, 40)

    if gs["game_mode"] == "chaos" and time.time() > gs["chaos_event_timer"]:
        event = random.choice(["flip", "snail", "nothing", "box_storm"])
        if event == "flip": gs["screen_flipped"] = not gs["screen_flipped"]
        elif event == "snail" and gs["snail"] is None: gs["snail"] = Snail()
        elif event == "box_storm":
            for _ in range(20):  # Spawn 20 small boxes
                size = random.randint(20, 40)
                x, y = random.randint(0, WIDTH - size), random.randint(0, HEIGHT - size)
                color = random.choice(gs["box_colors"])
                health = BASE_BOX_HEALTH * DIFFICULTY_SETTINGS[gs["difficulty"]]["health_mod"] * 0.5
                box = Box(x, y, size, size, color, health)
                box.speed *= 1.5  # Faster boxes
                gs["boxes"].append(box)
        gs["chaos_event_timer"] = time.time() + random.uniform(10, 20)

    for nebula in gs["nebulae"]:
        nebula.update()

    for obj in gs["boxes"] + gs["asteroids"] + [gs["boss"], gs["circle"], gs["snail"]]:
        if obj:
            if hasattr(obj, 'update'):
                original_speed = getattr(obj, 'speed', 0)
                obj.speed *= speed_scale
                obj.update()
                obj.speed = original_speed  # Restore original speed after update
            elif hasattr(obj, 'move'):
                original_vx, original_vy = getattr(obj, 'vx', 0), getattr(obj, 'vy', 0)
                obj.vx *= speed_scale
                obj.vy *= speed_scale
                obj.move()
                obj.vx, obj.vy = original_vx, original_vy
    if gs["nyan_cat"]:
        original_speed = gs["nyan_cat"].speed
        gs["nyan_cat"].speed *= speed_scale
        if not gs["nyan_cat"].update(gs["boxes"]): gs["nyan_cat"] = None
        gs["nyan_cat"].speed = original_speed
    for star in gs["stars"]: star.update()
    if gs["active_black_hole"] and not gs["active_black_hole"].update(gs["boxes"]): gs["active_black_hole"] = None
    for p in gs["particles"][:]:
        if not p.update(): gs["particles"].remove(p)
    spawn_asteroid()

    if gs["power_up_active"]:
        duration = (5 if gs["power_up_active"] in ["freeze", "time_warp"] else 10) + gs["upgrades"]["powerup_time"]
        if time.time() - gs["power_up_timer"] > duration:
            gs["power_up_active"] = None
            if "INVINCIBILITY" not in gs["active_cheats"]:
                gs["active_cheats"].discard("SHIELD_POWERUP")

    if gs["combo"] > 0 and time.time() - gs["combo_timer"] > 3: gs["combo"] = 0
    if not gs["boxes"] and not gs["boss"] and not gs["circle"]:
        gs["game_state"], gs["level_clear_timer"] = "level_clear", time.time()

# DRAWING FUNCTIONS
def draw_elements():
    surface_to_draw_on = screen.copy() if gs["screen_shake"] > 0 else screen
    surface_to_draw_on.fill(BLACK)
    state = gs["game_state"]

    if state == "main_menu": draw_main_menu(surface_to_draw_on)
    elif state == "mode_select": draw_mode_select_screen(surface_to_draw_on)
    elif state == "difficulty_select": draw_difficulty_select_screen(surface_to_draw_on)
    elif state == "stats": draw_stats_screen(surface_to_draw_on)
    elif state == "tutorial": draw_tutorial_screen(surface_to_draw_on)
    elif state == "shop": draw_shop_screen(surface_to_draw_on)
    elif state in ["playing", "paused", "game_over", "victory", "level_clear", "credits"]:
        if state != "credits": draw_game_screen(surface_to_draw_on)
        if state == "paused": draw_pause_screen(surface_to_draw_on)
        elif state == "game_over": draw_game_over_screen(surface_to_draw_on)
        elif state == "victory": draw_victory_screen(surface_to_draw_on)
        elif state == "level_clear": draw_level_clear_screen(surface_to_draw_on)
        elif state == "credits": draw_credits_screen(surface_to_draw_on)

    if gs["screen_flipped"]:
        surface_to_draw_on = pygame.transform.flip(surface_to_draw_on, False, True)

    if gs["screen_shake"] > 0:
        gs["screen_shake"] -= 1
        offset = (random.randint(-gs["shake_intensity"], gs["shake_intensity"]), random.randint(-gs["shake_intensity"], gs["shake_intensity"]))
        screen.blit(surface_to_draw_on, offset)
    else:
        screen.blit(surface_to_draw_on, (0,0))
    pygame.display.flip()

def draw_game_screen(surface):
    for nebula in gs["nebulae"]: nebula.draw(surface)
    for star in gs["stars"]: star.draw(surface)
    for obj in gs["boxes"] + gs["asteroids"] + [gs["boss"], gs["circle"], gs["power_up"], gs["snail"], gs["nyan_cat"]]:
        if obj: obj.draw(surface)
    if gs["active_black_hole"]: gs["active_black_hole"].draw(surface)
    for p in gs["particles"]: p.draw(surface)
    draw_cursor(surface)
    if gs["hud_active"]: draw_hud(surface)
    if gs["meteor_shower_warning"] > 0:
        alpha = 255 * (math.sin(time.time() * 5) * 0.5 + 0.5)
        warn_surf = big_font.render("METEOR SHOWER INBOUND!", True, (*RED, alpha))
        surface.blit(warn_surf, warn_surf.get_rect(center=(WIDTH//2, HEIGHT//2)))

def draw_cursor(surface):
    pos = tuple(map(int, gs["cursor_pos"]))
    is_shielded = "SHIELD_POWERUP" in gs["active_cheats"] or gs["power_up_active"] == "shield"
    if is_shielded:
        aura_radius = int(20 + 6 * math.sin(time.time() * 5))
        aura_surface = pygame.Surface((aura_radius*2, aura_radius*2), pygame.SRCALPHA)
        pygame.draw.circle(aura_surface, (*STARLIGHT_CYAN, 80), (aura_radius, aura_radius), aura_radius)
        surface.blit(aura_surface, (pos[0]-aura_radius, pos[1]-aura_radius))
    pygame.draw.circle(surface, STARLIGHT_CYAN, pos, 10)

def draw_hud(surface):
    mouse_pos = pygame.mouse.get_pos()
    hud_surface = pygame.Surface((300, 150), pygame.SRCALPHA)
    hud_surface.fill((*NEBULA_BLUE, 150))
    pygame.draw.rect(hud_surface, NEBULA_PURPLE, (0,0,300,150), 2)
    surface.blit(hud_surface, (10,60))
    surface.blit(font.render(f"Lives: {gs['lives']}/{gs['max_lives']}", True, WHITE), (20,70))
    surface.blit(font.render(f"Level: {gs['level']}", True, WHITE), (20,100))
    surface.blit(font.render(f"Score: {int(gs['score'])}", True, WHITE), (20,130))
    surface.blit(font.render(f"Dust: {gs['cosmic_dust']}", True, YELLOW), (20,160))
    for btn in hud_buttons.values():
        btn.draw(surface, btn.rect.collidepoint(mouse_pos))

def draw_main_menu(surface):
    for star in gs["stars"]: star.draw(surface)
    title_surf = big_font.render("Box Tapper: Evolution", True, WHITE)
    surface.blit(title_surf, title_surf.get_rect(center=(WIDTH//2, HEIGHT//3)))
    mouse_pos = pygame.mouse.get_pos()
    start_button.draw(surface, start_button.rect.collidepoint(mouse_pos))
    stats_button.draw(surface, stats_button.rect.collidepoint(mouse_pos))
    quit_button.draw(surface, quit_button.rect.collidepoint(mouse_pos))

def draw_mode_select_screen(surface):
    for star in gs["stars"]: star.draw(surface)
    title_surf = big_font.render("Select Game Mode", True, WHITE)
    surface.blit(title_surf, title_surf.get_rect(center=(WIDTH//2, 80)))
    mouse_pos = pygame.mouse.get_pos()
    for btn in mode_buttons.values():
        btn.draw(surface, btn.rect.collidepoint(mouse_pos))
    back_to_menu_button.draw(surface, back_to_menu_button.rect.collidepoint(mouse_pos))

def draw_difficulty_select_screen(surface):
    for star in gs["stars"]: star.draw(surface)
    title_surf = big_font.render("Select Difficulty", True, WHITE)
    surface.blit(title_surf, title_surf.get_rect(center=(WIDTH//2, 80)))
    mouse_pos = pygame.mouse.get_pos()
    for btn in difficulty_buttons:
        btn.draw(surface, btn.rect.collidepoint(mouse_pos))
    back_to_mode_button.draw(surface, back_to_mode_button.rect.collidepoint(mouse_pos))

def draw_stats_screen(surface):
    surface.fill(GALAXY_INDIGO)
    mouse_pos = pygame.mouse.get_pos()
    title_surf = big_font.render("Lifetime Stats & Achievements", True, WHITE)
    surface.blit(title_surf, title_surf.get_rect(center=(WIDTH//2, 80)))
    stats = gs["stats"]
    lines = [
        f"Boxes Tapped: {stats['boxes_tapped']:,}",
        f"Power-ups Collected: {stats['powerups_collected']:,}",
        f"Total Score Earned: {int(stats['total_score']):,}",
        f"Bosses Defeated: {stats['bosses_defeated']:,}",
        f"Snails Harmed: {stats['snails_harmed']:,}"
    ]
    for i, line in enumerate(lines):
        text_surf = stats_font.render(line, True, WHITE if "Snails" not in line else RED)
        surface.blit(text_surf, text_surf.get_rect(center=(WIDTH//2, 200 + i*60)))
    # Draw achievements
    ach_title = big_font.render("Achievements", True, WHITE)
    surface.blit(ach_title, ach_title.get_rect(center=(WIDTH//2, 500)))
    for i, (name, ach) in enumerate(gs["achievements"].items()):
        color = GOLD if ach["unlocked"] else GRAY
        text = f"{ach['description']} ({ach['reward']} Dust)"
        text_surf = font.render(text, True, color)
        surface.blit(text_surf, text_surf.get_rect(center=(WIDTH//2, 560 + i*40)))
    back_to_menu_button.draw(surface, back_to_menu_button.rect.collidepoint(mouse_pos))

def draw_tutorial_screen(surface):
    for star in gs["stars"]: star.draw(surface)
    for obj in gs["tutorial_objects"]: obj.draw(surface)
    text_surf = tutorial_font.render(gs["tutorial_text"], True, WHITE)
    text_rect = text_surf.get_rect(center=(WIDTH//2, 150))
    bg_rect = text_rect.inflate(40,20)
    bg_surf = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
    bg_surf.fill((*GALAXY_INDIGO, 200))
    surface.blit(bg_surf, bg_rect)
    surface.blit(text_surf, text_rect)

def draw_screen_overlay(surface, title_text):
    overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    overlay.fill((0,0,0,200))
    surface.blit(overlay, (0,0))
    if title_text:
        text_surf = big_font.render(title_text, True, WHITE)
        surface.blit(text_surf, text_surf.get_rect(center=(WIDTH//2, HEIGHT//2)))

def draw_pause_screen(surface):
    draw_screen_overlay(surface, "Paused")
    mouse_pos = pygame.mouse.get_pos()
    resume_button.draw(surface, resume_button.rect.collidepoint(mouse_pos))
    shop_button.draw(surface, shop_button.rect.collidepoint(mouse_pos))
    main_menu_button.draw(surface, main_menu_button.rect.collidepoint(mouse_pos))

def draw_game_over_screen(surface):
    draw_screen_overlay(surface, "Game Over!")
    score_display = font.render(f"Final Score: {int(gs['score'])}", True, WHITE)
    surface.blit(score_display, score_display.get_rect(center=(WIDTH//2, HEIGHT//2+60)))
    reset_button.draw(surface, reset_button.rect.collidepoint(pygame.mouse.get_pos()))

def draw_victory_screen(surface):
    draw_screen_overlay(surface, "")
    lines = [f"Congratulations! You've beaten Level {MAX_LEVEL_CLASSIC}!", f"Final Score: {int(gs['score'])}", "Thanks for playing!"]
    for i, line in enumerate(lines):
        text = font.render(line, True, WHITE)
        surface.blit(text, text.get_rect(center=(WIDTH//2, HEIGHT//2 - 100 + i*50)))
    continue_button.draw(surface, continue_button.rect.collidepoint(pygame.mouse.get_pos()))

def draw_credits_screen(surface):
    draw_screen_overlay(surface, "")
    credits_lines = ["ENDGAME CREDITS", "DESIGNER: TONMOY KS", "TASK MANAGER: TONMOY KS", "CONCEPT ARTIST: TONMOY KS", "PUBLISHER: TONMOY KS", "", "THE END"]
    for i, line in enumerate(credits_lines):
        text = font.render(line, True, WHITE)
        surface.blit(text, text.get_rect(center=(WIDTH//2, HEIGHT//2 - 150 + i*40)))
    exit_button.draw(surface, exit_button.rect.collidepoint(pygame.mouse.get_pos()))

def draw_level_clear_screen(surface):
    text_surf = big_font.render("Level Clear!", True, GOLD)
    surface.blit(text_surf, text_surf.get_rect(center=(WIDTH//2, HEIGHT//2)))

def draw_shop_screen(surface):
    surface.fill(GALAXY_INDIGO)
    mouse_pos = pygame.mouse.get_pos()
    title_surf = big_font.render("Upgrade Shop", True, WHITE)
    surface.blit(title_surf, title_surf.get_rect(center=(WIDTH//2, 80)))
    dust_surf = font.render(f"Cosmic Dust: {gs['cosmic_dust']}", True, YELLOW)
    surface.blit(dust_surf, dust_surf.get_rect(center=(WIDTH//2, 150)))
    for name, btn in shop_buttons.items():
        upgrade_level = gs["upgrades"][name]
        cost = UPGRADE_COSTS[name] * (2 ** upgrade_level)
        btn.text = f"{UPGRADE_NAMES[name]} ({upgrade_level}) - Cost: {cost}"
        btn.draw(surface, btn.rect.collidepoint(mouse_pos))
    back_button.draw(surface, back_button.rect.collidepoint(mouse_pos))

# EVENT HANDLING
def handle_input():
    global running, WIDTH, HEIGHT
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.VIDEORESIZE:
            WIDTH, HEIGHT = event.w, event.h
            pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            handle_mouse_click(event.pos)
        elif event.type == pygame.KEYDOWN:
            handle_keyboard_input(event)

def handle_mouse_click(pos):
    state = gs["game_state"]
    if state == "main_menu":
        if start_button.is_clicked(pos): gs["game_state"] = "mode_select"
        elif stats_button.is_clicked(pos): gs["game_state"] = "stats"
        elif quit_button.is_clicked(pos): global running; running = False
    elif state == "mode_select":
        if back_to_menu_button.is_clicked(pos): gs["game_state"] = "main_menu"
        for mode, btn in mode_buttons.items():
            if btn.is_clicked(pos):
                gs["game_mode"] = mode
                if mode in ["classic", "endless"]:
                    gs["game_state"] = "difficulty_select"
                else: # Modes with fixed difficulty
                    reset_game_state("casual", mode)
    elif state == "difficulty_select":
        if back_to_mode_button.is_clicked(pos): gs["game_state"] = "mode_select"
        for btn in difficulty_buttons:
            if btn.is_clicked(pos):
                diff = btn.text.lower()
                if diff == "tutorial": start_tutorial()
                else: reset_game_state(diff, gs["game_mode"])
    elif state == "stats":
        if back_to_menu_button.is_clicked(pos): gs["game_state"] = "main_menu"
    elif state == "tutorial":
        clicked_obj = None
        for obj in gs["tutorial_objects"][:]:
            if obj.rect.collidepoint(pos):
                if isinstance(obj, Asteroid): return
                gs["tutorial_objects"].remove(obj)
                clicked_obj = obj
                break
        if clicked_obj: advance_tutorial()
    elif state == "paused":
        if resume_button.is_clicked(pos): gs["game_state"] = "playing"
        elif shop_button.is_clicked(pos): gs["game_state"] = "shop"
        elif main_menu_button.is_clicked(pos): gs["game_state"] = "main_menu"
    elif state == "playing":
        gs["cursor_pos"] = list(pos)
        if gs["hud_active"] and handle_hud_button_clicks(pos): return
        handle_gameplay_click(pos)
    elif state == "game_over":
        if reset_button.is_clicked(pos): gs["game_state"] = "main_menu"
    elif state == "victory":
        if continue_button.is_clicked(pos): gs["game_state"] = "credits"
    elif state == "credits":
        if exit_button.is_clicked(pos): global running; running = False
    elif state == "shop":
        if back_button.is_clicked(pos): gs["game_state"] = "paused"
        for name, btn in shop_buttons.items():
            if btn.is_clicked(pos): purchase_upgrade(name)

def handle_hud_button_clicks(pos):
    if hud_buttons["hud"].is_clicked(pos): gs["hud_active"] = False
    elif hud_buttons["reset"].is_clicked(pos): gs["game_state"] = "main_menu"
    elif hud_buttons["debug"].is_clicked(pos): activate_cheat("DEBUG_MODE")
    else: return False
    return True

def handle_gameplay_click(pos):
    if gs["power_up_active"] == "black_hole":
        gs["active_black_hole"], gs["power_up_active"] = BlackHole(*pos), None
        return
    hit_something = False
    if gs["snail"] and gs["snail"].rect.collidepoint(pos):
        gs["score"] -= 5000
        gs["snail"] = None
        gs["stats"]["snails_harmed"] += 1
        hit_something = True
    for asteroid in gs["asteroids"][:]:
        if asteroid.rect.collidepoint(pos):
            if not ("INVINCIBILITY" in gs["active_cheats"] or "SHIELD_POWERUP" in gs["active_cheats"] or gs["power_up_active"] == "shield"):
                gs["lives"] -= 1
            gs["asteroids"].remove(asteroid)
            hit_something = True
            break
    if hit_something: return

    if gs["power_up_active"] == "multi_tap":
        hit_something = True
        radius = 75
        for box in gs["boxes"][:]:
            if math.hypot(box.rect.centerx - pos[0], box.rect.centery - pos[1]) < radius:
                damage_box(box)
    else:
        for box in gs["boxes"][:]:
            if box.rect.collidepoint(pos):
                hit_something = True
                damage_box(box)
                break

    if not hit_something:
        if gs["boss"] and gs["boss"].rect.collidepoint(pos): hit_something = True; handle_boss_hit()
        elif gs["circle"] and gs["circle"].rect.collidepoint(pos): hit_something = True; handle_circle_hit()
        elif gs["power_up"] and gs["power_up"].rect.collidepoint(pos): hit_something = True; handle_powerup_hit()

    if not hit_something:
        gs["player_sequence"].append("hit_empty")
        is_inv = "INVINCIBILITY" in gs["active_cheats"] or "SHIELD_POWERUP" in gs["active_cheats"] or gs["power_up_active"] == "shield"
        if not is_inv and not (gs.get("barrier") and gs["barrier"].rect.collidepoint(pos)):
            gs["lives"] -= 1
        gs["combo"] = 0

    if gs["lives"] <= 0:
        gs["game_state"] = "game_over"
        save_high_scores()
        save_stats()

    if len(gs["player_sequence"]) > 10:
        gs["player_sequence"].pop(0)

def damage_box(box, is_black_hole=False):
    if box.is_dying: return
    if not is_black_hole:
        gs["player_sequence"].append("hit_box")
        # Sound effect placeholder: if sound_effects["tap"]: sound_effects["tap"].play()
        if box.special_type == "multi":
            if box.tap_timer == 0 or time.time() - box.tap_timer > 1:
                box.tap_timer, box.tap_count = time.time(), 1
            else:
                box.tap_count += 1
            if box.tap_count >= box.taps_required:
                box.health = 0
                gs["score"] += 20 * gs["score_multiplier"]
        else:
            base_damage = gs["upgrades"]["damage"] + 1
            damage_dealt = gs["equipped_tool"].damage * base_damage if "INSTANT_KILL" not in gs["active_cheats"] else box.max_health
            box.health -= damage_dealt
    else:
        box.health = 0

    if box.health <= 0:
        if box.special_type == "dramatic":
            box.is_dying, box.death_timer, box.death_quote, box.speed = True, time.time() + 2, random.choice(DRAMATIC_QUOTES), 0
            return

        gs["stats"]["boxes_tapped"] += 1
        create_explosion(box.rect.centerx, box.rect.centery, box.color)
        # Sound effect placeholder: if sound_effects["explosion"]: sound_effects["explosion"].play()

        if box.special_type == "splitter":
            for _ in range(2):
                new_size = max(20, int(box.rect.width * 0.7))
                new_health = max(1, box.max_health * 0.5)
                child = Box(box.rect.centerx, box.rect.centery, new_size, new_size, GREEN, new_health, is_child=True)
                gs["boxes"].append(child)

        if box.special_type == "explosive":
            for b in gs["boxes"][:]:
                if b != box: b.health = 0
            if "INVINCIBILITY" not in gs["active_cheats"]: gs["lives"] -= 1
            trigger_screen_shake()

        if box.special_type == "golden": gs["score"] += 500
        if box.special_type == "rainbow": gs["score"] += 1000
        if box in gs["boxes"]: gs["boxes"].remove(box)

        diff_mods = DIFFICULTY_SETTINGS[gs["difficulty"]]
        dust_bonus = 1 + (gs["upgrades"]["dust_bonus"] * 0.2)
        gs["cosmic_dust"] += int(1 * dust_bonus * diff_mods["dust_mod"])
        score_gain = (10 * gs["score_multiplier"] * (1 + gs["combo"] * 0.5)) * diff_mods["score_mod"]
        gs["score"] += score_gain
        gs["stats"]["total_score"] += score_gain
        gs["combo"] += 1
        gs["combo_timer"] = time.time()

def handle_boss_hit():
    if random.random() > gs["boss"].dodge_chance:
        damage = (gs["equipped_tool"].damage + gs["upgrades"]["damage"])
        gs["boss"].health -= damage
        if gs["boss"].health <= 0:
            gs["score"] += 50 * (1 + gs["combo"] * 0.5)
            gs["boss"] = None
            gs["stats"]["bosses_defeated"] += 1
            gs["game_state"], gs["level_clear_timer"] = "level_clear", time.time()
        else:
            gs["boss"].update_phase()

def handle_circle_hit():
    gs["lives"] = min(gs["lives"] + 1, gs["max_lives"] + 1)
    gs["max_lives"] += 1
    gs["circle"] = None

def handle_powerup_hit():
    gs["power_up_active"] = gs["power_up"].type
    gs["power_up_timer"] = time.time()
    gs["stats"]["powerups_collected"] += 1
    # Sound effect placeholder: if sound_effects["powerup"]: sound_effects["powerup"].play()
    if gs["power_up_active"] == "nyan":
        gs["nyan_cat"] = NyanCat()
    elif gs["power_up_active"] == "shield":
        gs["active_cheats"].add("SHIELD_POWERUP")
    gs["power_up"] = None

def handle_keyboard_input(event):
    if event.key == pygame.K_p:
        if gs["game_state"] == "playing": gs["game_state"] = "paused"
        elif gs["game_state"] == "paused": gs["game_state"] = "playing"

# SHOP LOGIC
UPGRADE_COSTS = {"damage": 20, "lives": 50, "dust_bonus": 100, "powerup_time": 75}
UPGRADE_NAMES = {"damage": "Tap Power", "lives": "Max Lives", "dust_bonus": "Dust Bonus", "powerup_time": "Power-up Time"}
def purchase_upgrade(name):
    level = gs["upgrades"][name]
    cost = UPGRADE_COSTS[name] * (2 ** level)
    if gs["cosmic_dust"] >= cost:
        gs["cosmic_dust"] -= cost
        gs["upgrades"][name] += 1
        if name == "lives":
            gs["max_lives"] += 1
            gs["lives"] += 1

# MAIN GAME SETUP & LOOP
hud_buttons = {
    "hud": Button(10, 10, 100, 40, "HUD", STARLIGHT_CYAN, WHITE),
    "reset": Button(120, 10, 100, 40, "Menu", GRAY, WHITE),
    "debug": Button(230, 10, 100, 40, "Debug", COSMIC_MAGENTA, WHITE)
}
reset_button = Button(0,0,200,60,"To Menu",GRAY,WHITE); reset_button.rect.center=(WIDTH//2,HEIGHT//2+120)
continue_button = Button(0,0,200,60,"Continue",GRAY,WHITE); continue_button.rect.center=(WIDTH//2,HEIGHT//2+150)
exit_button = Button(0,0,200,60,"Exit",GRAY,WHITE); exit_button.rect.center=(WIDTH//2,HEIGHT//2+250)
start_button = Button(WIDTH//2-100, HEIGHT//2-40, 200, 60, "Start Game", AURORA_GREEN, WHITE)
stats_button = Button(WIDTH//2-100, HEIGHT//2+40, 200, 60, "Stats", STARLIGHT_CYAN, WHITE)
quit_button = Button(WIDTH//2-100, HEIGHT//2+120, 200, 60, "Quit", GRAY, WHITE)
resume_button = Button(WIDTH//2-150, HEIGHT//2-100, 300, 60, "Resume", AURORA_GREEN, WHITE)
shop_button = Button(WIDTH//2-150, HEIGHT//2, 300, 60, "Shop", STARLIGHT_CYAN, WHITE)
main_menu_button = Button(WIDTH//2-150, HEIGHT//2+100, 300, 60, "Main Menu", GRAY, WHITE)
back_button = Button(WIDTH//2-150, HEIGHT-100, 300, 60, "Back", GRAY, WHITE)
shop_buttons = {
    "damage": Button(WIDTH//2-250,200,500,60,"",AURORA_GREEN,WHITE),
    "lives": Button(WIDTH//2-250,280,500,60,"",STARLIGHT_CYAN,WHITE),
    "dust_bonus": Button(WIDTH//2-250,360,500,60,"",GOLD,BLACK),
    "powerup_time": Button(WIDTH//2-250,440,500,60,"",COSMIC_MAGENTA,WHITE)
}
mode_buttons = {
    "classic": Button(WIDTH//2-150, 150, 300, 60, "Classic", YELLOW, WHITE),
    "endless": Button(WIDTH//2-150, 230, 300, 60, "Endless", STARLIGHT_CYAN, WHITE),
    "boss_rush": Button(WIDTH//2-150, 310, 300, 60, "Boss Rush", RED, WHITE),
    "chaos": Button(WIDTH//2-150, 390, 300, 60, "Chaos", COSMIC_MAGENTA, WHITE),
    "stealth": Button(WIDTH//2-150, 470, 300, 60, "Stealth", DARK_GRAY, WHITE)
}
difficulty_buttons = [Button(WIDTH//2-150, 180+i*70, 300, 60, name, color, WHITE) for i, (name,color) in enumerate(zip(["Tutorial","Easy","Beginner","Casual","Hardcore","Insane","Demon"], [STARLIGHT_CYAN,AURORA_GREEN,AURORA_GREEN,YELLOW,RED,COSMIC_MAGENTA,NEBULA_PURPLE]))]
back_to_menu_button = Button(WIDTH // 2 - 150, HEIGHT - 100, 300, 60, "Back to Menu", GRAY, WHITE)
back_to_mode_button = Button(WIDTH//2-150, 180+7*70, 300, 60, "Back", GRAY, WHITE)

gs = setup_game_variables()

def reset_game_state(difficulty, game_mode):
    global gs
    old_upgrades, old_high_scores, old_stats = gs["upgrades"], gs["high_scores"], gs["stats"]
    gs = setup_game_variables(difficulty, game_mode)
    gs["upgrades"], gs["high_scores"], gs["stats"] = old_upgrades, old_high_scores, old_stats
    gs["max_lives"] += gs["upgrades"]["lives"]
    gs["lives"] = gs["max_lives"]
    gs["game_state"] = "playing"
    start_new_level()

spawn_stars()
running = True

if music_loaded:
    pygame.mixer.music.play(loops=-1) # The -1 makes the music loop forever

while running:
    handle_input()
    update_game_state()
    draw_elements()
    clock.tick(FPS)
save_stats()
pygame.quit()
