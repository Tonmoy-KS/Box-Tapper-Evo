# Box tapper: Evo
import pygame
import random
import math
import os
import time
import json


# SETTINGS & CONSTANTS

# --- Display (Initial size, now fully resizable)---
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
SHIELD_BLUE = (0, 191, 255)
CURSED_PURPLE = (138, 43, 226)


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

# --- Difficulty Settings ---
DIFFICULTY_SETTINGS = {
    "easy":       {"lives": 100, "health_mod": 0.1, "speed_mod": 0.7, "spawn_mod": 0.5, "asteroid_mod": 0.1, "score_mod": 0.0, "dust_mod": 1.5},
    "beginner":   {"lives": 30, "health_mod": 0.8, "speed_mod": 0.9, "spawn_mod": 0.9, "asteroid_mod": 0.8, "score_mod": 0.75,  "dust_mod": 1.2},
    "casual":     {"lives": 10, "health_mod": 1.0, "speed_mod": 1.0, "spawn_mod": 1.0, "asteroid_mod": 1.0, "score_mod": 1.0,  "dust_mod": 1.0},
    "hardcore":   {"lives": 5,  "health_mod": 1.5, "speed_mod": 1.2, "spawn_mod": 1.2, "asteroid_mod": 1.3, "score_mod": 1.25, "dust_mod": 1.25},
    "insane":     {"lives": 3,  "health_mod": 2.0, "speed_mod": 1.5, "spawn_mod": 1.5, "asteroid_mod": 2.0, "score_mod": 2.0,  "dust_mod": 1.5},
    "demon":      {"lives": 1,  "health_mod": 3.0, "speed_mod": 2.0, "spawn_mod": 2.0, "asteroid_mod": 2.0, "score_mod": 20.0,  "dust_mod": 2.0},
}

DRAMATIC_QUOTES = ["Et tu, Brute?", "I'm melting!", "I am just in a Game!", "Rosebud...", "Tell my story!", "What's in the box?!", "I've seen things...", "Who am I? who created this?", "Farewell, cruel world!"]

UPGRADE_COSTS = {"damage": 20, "lives": 50, "dust_bonus": 100, "powerup_time": 75}
UPGRADE_NAMES = {"damage": "Tap Power", "lives": "Max Lives", "dust_bonus": "Dust Bonus", "powerup_time": "Power-up Time"}

# --- CLASSES ---

class FloatingText:
    """Displays temporary text on screen, like score gains or status effects."""
    def __init__(self, x, y, text, color, font):
        self.x, self.y = x, y
        self.text = text
        self.color = color
        self.font = font
        self.alpha = 255
        self.lifespan = 60
        self.vy = -1

    def update(self):
        self.y += self.vy
        self.lifespan -= 1
        self.alpha = max(0, self.alpha - 4)
        return self.lifespan > 0

    def draw(self, surface):
        text_surf = self.font.render(self.text, True, self.color)
        text_surf.set_alpha(self.alpha)
        surface.blit(text_surf, text_surf.get_rect(center=(self.x, self.y)))

class Tool:
    """Represents a tapper tool with different abilities."""
    def __init__(self, id, level, damage, score_multiplier, is_dev):
        self.id, self.level, self.damage, self.score_multiplier, self.is_dev = id, level, damage, score_multiplier, is_dev

class Star:
    """A twinkling star in the background."""
    def __init__(self, width, height):
        self.x, self.y = random.randint(0, width), random.randint(0, height)
        self.radius = random.randint(1, 3)
        self.color, self.alpha = WHITE, random.randint(50, 255)
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
    def __init__(self, width, height):
        self.x, self.y = random.randint(0, width), random.randint(0, height)
        self.radius = random.randint(100, 300)
        self.color = random.choice([NEBULA_BLUE, NEBULA_PURPLE, STARLIGHT_CYAN])
        self.alpha, self.pulse_speed = random.randint(20, 50), random.uniform(0.1, 0.5)

    def update(self):
        self.alpha += self.pulse_speed
        if self.alpha >= 50 or self.alpha <= 20: self.pulse_speed *= -1
        self.alpha = max(20, min(50, self.alpha))

    def draw(self, surface):
        nebula_surf = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        for r in range(self.radius, 0, -5):
            alpha = int(self.alpha * (1 - r / self.radius)**2)
            pygame.draw.circle(nebula_surf, (*self.color, alpha), (self.radius, self.radius), r)
        surface.blit(nebula_surf, (self.x - self.radius, self.y - self.radius))

class Particle:
    """A small particle for explosion effects."""
    def __init__(self, x, y, color):
        self.x, self.y, self.color = x, y, color
        self.vx, self.vy = random.uniform(-3, 3), random.uniform(-3, 3)
        self.lifespan, self.radius = random.randint(20, 40), random.randint(2, 5)

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
    def __init__(self, game):
        self.game = game
        self.width, self.height = self.game.screen.get_size()
        start_side = random.choice(['left', 'right', 'top', 'bottom'])
        if start_side == 'left':
            self.x, self.y, self.vx, self.vy = -20, random.randint(0, self.height), random.uniform(2, 4), random.uniform(-1, 1)
        elif start_side == 'right':
            self.x, self.y, self.vx, self.vy = self.width + 20, random.randint(0, self.height), random.uniform(-4, -2), random.uniform(-1, 1)
        elif start_side == 'top':
            self.x, self.y, self.vx, self.vy = random.randint(0, self.width), -20, random.uniform(-1, 1), random.uniform(2, 4)
        else:
            self.x, self.y, self.vx, self.vy = random.randint(0, self.width), self.height + 20, random.uniform(-1, 1), random.uniform(-4, -2)
        self.radius = random.randint(10, 25)
        self.rect = pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)

    def move(self):
        self.x += self.vx
        self.y += self.vy
        self.rect.center = (self.x, self.y)

    def is_offscreen(self):
        return self.rect.right < 0 or self.rect.left > self.width or self.rect.bottom < 0 or self.rect.top > self.height

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
        if self.radius < self.max_radius: self.radius += self.grow_speed
        for box in boxes[:]:
            dist_x, dist_y = self.x - box.rect.centerx, self.y - box.rect.centery
            distance = math.hypot(dist_x, dist_y)
            if distance < self.pull_radius:
                if distance < self.radius:
                    box.take_damage(99999, is_black_hole=True)
                else:
                    angle = math.atan2(dist_y, dist_x)
                    box.rect.x += self.pull_force * math.cos(angle)
                    box.rect.y += self.pull_force * math.sin(angle)
        return time.time() - self.start_time < self.lifespan

    def draw(self, surface):
        pygame.draw.circle(surface, BLACK, (self.x, self.y), int(self.radius))
        for i in range(3):
            angle = (time.time() * (i + 1) * 2) % (2 * math.pi)
            p_radius = self.radius + 10 + i * 5
            px, py = self.x + p_radius * math.cos(angle), self.y + p_radius * math.sin(angle)
            pygame.draw.circle(surface, NEBULA_PURPLE, (int(px), int(py)), 3)

class Snail:
    """A very slow, harmless creature for Chaos Mode."""
    def __init__(self, game):
        self.game = game
        height = self.game.screen.get_height()
        self.x, self.y = -30, random.randint(height - 100, height - 50)
        self.speed, self.rect = 0.5, pygame.Rect(self.x, self.y, 30, 15)

    def update(self):
        self.x += self.speed
        self.rect.x = self.x

    def draw(self, surface):
        pygame.draw.rect(surface, GOLD, self.rect)

class NyanCat:
    """A mythical creature that brings rainbow boxes."""
    def __init__(self, game):
        self.game = game
        self.width, self.height = self.game.screen.get_size()
        self.y, self.x = random.randint(50, self.height - 50), -100
        self.speed, self.rect = 10, pygame.Rect(self.x, self.y, 80, 50)
        self.trail = []

    def update(self, boxes):
        self.x += self.speed
        self.rect.x = self.x
        self.trail.append(self.rect.copy())
        if len(self.trail) > 20: self.trail.pop(0)
        for box in boxes:
            if self.rect.colliderect(box.rect) and box.special_type != "rainbow":
                box.special_type, box.color = "rainbow", (random.randint(100,255), random.randint(100,255), random.randint(100,255))
                box.original_color = box.color
        return self.x < self.width + 100

    def draw(self, surface):
        for trail_rect in self.trail:
            color = (random.randint(0,255), random.randint(0,255), random.randint(0,255))
            pygame.draw.rect(surface, color, trail_rect)
        pygame.draw.rect(surface, COSMIC_MAGENTA, self.rect)

class Box:
    """The main target object for the player to tap."""
    def __init__(self, game, x, y, width, height, color, health, is_child=False):
        self.game, self.rect = game, pygame.Rect(int(x), int(y), width, height)
        self.original_color, self.color = color, color
        self.health, self.max_health = health, health
        speed_mod = DIFFICULTY_SETTINGS.get(self.game.difficulty, {}).get("speed_mod", 1.0)
        self.speed = (5 * speed_mod) * (1.5 if is_child else 1.0)
        self.direction, self.special_type, self.alpha = random.choice([-1, 1]), None, 255
        self.tap_count, self.tap_timer, self.taps_required = 0, 0, 0
        self.is_shrinking, self.shrink_rate, self.min_size = False, 0.25, 20
        self.is_dying, self.death_timer, self.death_quote = False, 0, ""
        self.teleport_timer = time.time() + random.uniform(2, 4)
        self.visible_timer = time.time() + random.uniform(1, 3)
        self.is_child, self.hit_feedback_timer = is_child, 0
        self.is_shielded, self.shield_timer = False, 0
        if not is_child: self.assign_special_type()

    def assign_special_type(self):
        roll = random.random()
        if roll < 0.02:
            self.special_type, self.color, self.health, self.speed = "golden", GOLD, 3, 8
        elif roll < 0.35:
            choices = ["explosive", "regen", "shrinking", "multi", "splitter", "gravity", "shield", "cursed", "dodging"]
            if self.game.game_mode == "chaos": choices.extend(["dramatic", "teleporter"])
            self.special_type = random.choice(choices)
            if self.special_type == "splitter": self.color = GREEN
            if self.special_type == "dramatic": self.color = WHITE
            if self.special_type == "teleporter": self.color = STARLIGHT_CYAN
            if self.special_type == "cursed": self.color = CURSED_PURPLE
            if self.special_type == "shrinking": self.is_shrinking = True
            if self.special_type == "multi": self.taps_required = min(1 + self.game.level // 10, 5)
            if self.special_type == "gravity": self.color = NEBULA_PURPLE
            if self.special_type == "shield":
                self.is_shielded, self.shield_timer = True, time.time() + 3
        self.original_color = self.color

    def update(self):
        screen_width, screen_height = self.game.screen.get_size()
        if self.is_dying:
            if time.time() > self.death_timer: self.health = 0
            return

        if self.hit_feedback_timer > 0:
            self.hit_feedback_timer -= 1
            if self.hit_feedback_timer == 0: self.color = self.original_color

        if self.special_type == "shield" and self.is_shielded and time.time() > self.shield_timer:
            self.is_shielded, self.color = False, self.original_color

        if self.special_type == "dodging":
            dist_to_cursor = math.hypot(self.rect.centerx - self.game.cursor_pos[0], self.rect.centery - self.game.cursor_pos[1])
            if dist_to_cursor < 100:
                angle = math.atan2(self.rect.centery - self.game.cursor_pos[1], self.rect.centerx - self.game.cursor_pos[0])
                self.rect.x += 3 * math.cos(angle)
                self.rect.y += 3 * math.sin(angle)

        if self.game.game_mode == "stealth" and time.time() > self.visible_timer:
            self.alpha = 10 if self.alpha == 255 else 255
            self.visible_timer = time.time() + random.uniform(2, 5 if self.alpha == 10 else 1)

        self.rect.x += self.speed * self.direction
        if self.rect.left <= 0 or self.rect.right >= screen_width: self.direction *= -1
        self.rect.clamp_ip(self.game.screen.get_rect())

        if self.special_type == "regen" and self.health < self.max_health: self.health = min(self.health + 0.5/FPS, self.max_health)
        if self.is_shrinking and self.rect.width > self.min_size:
            center = self.rect.center
            self.rect.width = max(self.min_size, self.rect.width - self.shrink_rate)
            self.rect.height = max(self.min_size, self.rect.height - self.shrink_rate)
            self.rect.center = center

    def draw(self, surface):
        box_surf = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        box_surf.fill((*self.color, int(self.alpha)))
        surface.blit(box_surf, self.rect.topleft)

        if self.is_shielded:
            shield_surf = pygame.Surface(self.rect.size, pygame.SRCALPHA)
            pygame.draw.rect(shield_surf, (*SHIELD_BLUE, 100), (0, 0, *self.rect.size), border_radius=8)
            surface.blit(shield_surf, self.rect.topleft)
            pygame.draw.rect(surface, SHIELD_BLUE, self.rect, 3, border_radius=8)

        if self.max_health > 1:
            health_ratio = self.health / self.max_health
            pygame.draw.rect(surface, AURORA_GREEN, (self.rect.x, self.rect.y - 10, self.rect.width * health_ratio, 5))
            pygame.draw.rect(surface, BLACK, (self.rect.x, self.rect.y - 10, self.rect.width, 5), 1)

        if self.special_type == "multi":
            taps_text = self.game.font.render(f"{self.tap_count}/{self.taps_required}", True, BLACK)
            surface.blit(taps_text, taps_text.get_rect(center=self.rect.center))

    def take_damage(self, damage, is_black_hole=False):
        if self.is_dying or (self.is_shielded and not is_black_hole): return False
        self.hit_feedback_timer, self.color = 5, WHITE
        if not is_black_hole:
            self.game.player_sequence.append("hit_box")
            if self.special_type == "multi":
                self.tap_count += 1
                if self.tap_count >= self.taps_required: self.health = 0
            else: self.health -= damage
        else: self.health = 0
        if self.health <= 0: self.on_destroy()
        return True

    def on_destroy(self):
        if self.special_type == "dramatic":
            self.is_dying, self.death_timer, self.death_quote, self.speed = True, time.time() + 2, random.choice(DRAMATIC_QUOTES), 0
            return
        self.game.stats["boxes_tapped"] += 1
        self.game.create_explosion(self.rect.centerx, self.rect.centery, self.original_color)

        if self.special_type == "splitter":
            for _ in range(2):
                new_size = max(20, int(self.rect.width * 0.7))
                child = Box(self.game, self.rect.centerx, self.rect.centery, new_size, new_size, GREEN, self.max_health * 0.5, is_child=True)
                self.game.boxes.append(child)
        if self.special_type == "explosive":
            for b in self.game.boxes[:]:
                if b != self: b.take_damage(9999)
            if "INVINCIBILITY" not in self.game.active_cheats: self.game.lives -= 1
            self.game.trigger_screen_shake(20, 20)
        if self.special_type == "cursed":
            self.game.score_multiplier_penalty_timer = time.time() + 5
            self.game.spawn_floating_text(self.rect.centerx, self.rect.y, "Cursed! Score x0.5", RED)

        score_gain = 0
        if self.special_type == "golden": score_gain += 500
        if self.special_type == "rainbow": score_gain += 1000
        diff_mods = DIFFICULTY_SETTINGS[self.game.difficulty]
        dust_bonus = 1 + (self.game.upgrades["dust_bonus"] * 0.2)
        self.game.cosmic_dust += int(1 * dust_bonus * diff_mods["dust_mod"])
        base_score = 10 * (1 + self.game.combo * 0.5)
        score_gain += base_score * self.game.get_current_score_multiplier() * diff_mods["score_mod"]
        self.game.score += score_gain
        self.game.stats["total_score"] += score_gain
        self.game.combo, self.game.combo_timer = self.game.combo + 1, time.time()
        self.game.spawn_floating_text(self.rect.centerx, self.rect.y, f"+{int(score_gain)}", GOLD)
        if self in self.game.boxes: self.game.boxes.remove(self)

class Boss(Box):
    def __init__(self, game, x, y, width, height, color, health):
        super().__init__(game, x, y, width, height, color, health)
        self.dodge_chance, self.phase, self.minions = 0.3, 1, []

    def update(self):
        super().update()
        for minion in self.minions[:]:
            minion.update()
            if minion.health <= 0: self.minions.remove(minion)

    def update_phase(self):
        health_ratio = self.health / self.max_health
        if health_ratio <= 0.5 and self.phase == 1:
            self.phase, self.color, self.original_color, self.dodge_chance = 2, RED, RED, 0.6
        elif health_ratio <= 0.25 and self.phase == 2:
            self.phase, self.speed = 3, self.speed * 2
            for _ in range(3):
                minion_size = (int(self.rect.width * 0.7), int(self.rect.height * 0.7))
                minion = Box(self.game, self.rect.centerx, self.rect.centery, *minion_size, NEBULA_PURPLE, 1)
                minion.speed = 3
                self.minions.append(minion)

class Circle(Box):
    def __init__(self, game, x, y, radius, speed):
        super().__init__(game, x - radius, y - radius, radius * 2, radius * 2, YELLOW, 1)
        self.radius, self.speed = radius, speed
        self.direction_x, self.direction_y = random.choice([-1, 1]), random.choice([-1, 1])

    def update(self):
        width, height = self.game.screen.get_size()
        self.rect.x += self.speed * self.direction_x
        self.rect.y += self.speed * self.direction_y
        if self.rect.left <= 0 or self.rect.right >= width: self.direction_x *= -1
        if self.rect.top <= 0 or self.rect.bottom >= height: self.direction_y *= -1

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, self.rect.center, self.radius)

class PowerUp:
    def __init__(self, x, y, type):
        self.rect = pygame.Rect(x, y, 40, 40)
        self.type = type
        self.color = {"dust_rush": GOLD, "multi_tap": AURORA_GREEN, "black_hole": DARK_GRAY, "nyan": GRAY, "time_warp": STARLIGHT_CYAN}.get(type, YELLOW)

    def draw(self, surface, font):
        pygame.draw.rect(surface, self.color, self.rect)
        char = {"dust_rush": "D", "multi_tap": "M", "black_hole": "B", "speed": "S", "nyan": "N", "time_warp": "T"}.get(self.type, self.type[0].upper())
        text = font.render(char, True, WHITE)
        surface.blit(text, text.get_rect(center=self.rect.center))

class Button:
    def __init__(self, rel_pos, size, text, color, text_color, font, hover_color=None):
        self.rel_pos, self.size, self.text = rel_pos, size, text
        self.color, self.text_color, self.font = color, text_color, font
        self.hover_color = hover_color or color
        self.rect = pygame.Rect(0, 0, *size)
        self.reposition(pygame.display.get_surface().get_size())

    def reposition(self, screen_size):
        width, height = screen_size
        self.rect.center = (int(width * self.rel_pos[0]), int(height * self.rel_pos[1]))

    def draw(self, surface, is_hovered=False):
        current_color = self.hover_color if is_hovered else self.color
        pygame.draw.rect(surface, current_color, self.rect, border_radius=8)
        text_surface = self.font.render(self.text, True, self.text_color)
        surface.blit(text_surface, text_surface.get_rect(center=self.rect.center))

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("Box Tapper: Evolution V.2.1.0")
        self.clock = pygame.time.Clock()
        self.running = True
        self.setup_fonts()
        self.load_music()
        self.create_ui()
        self.reset_game_state("casual", "classic")
        self.game_state = "main_menu"
        self.spawn_stars_and_nebulae()

    def setup_fonts(self):
        try:
            self.font = pygame.font.Font(None, 36)
            self.big_font = pygame.font.Font(None, 72)
            self.button_font = pygame.font.Font(None, 48)
            self.stats_font = pygame.font.Font(None, 48)
        except FileNotFoundError:
            self.font = pygame.font.SysFont("Arial", 24)
            self.big_font = pygame.font.SysFont("Arial", 60)
            self.button_font = pygame.font.SysFont("Arial", 36)
            self.stats_font = pygame.font.SysFont("Arial", 36)

    def load_music(self):
        try:
            pygame.mixer.music.load("background_music.wav")
            pygame.mixer.music.play(loops=-1)
        except pygame.error:
            print("Warning: Could not load 'background_music.wav'.")

    def create_ui(self):
        self.start_button = Button((0.5, 0.45), (200, 60), "Start Game", AURORA_GREEN, WHITE, self.button_font)
        self.stats_button = Button((0.5, 0.55), (200, 60), "Stats", STARLIGHT_CYAN, WHITE, self.button_font)
        self.quit_button = Button((0.5, 0.65), (200, 60), "Quit", GRAY, WHITE, self.button_font)
        self.resume_button = Button((0.5, 0.4), (300, 60), "Resume", AURORA_GREEN, WHITE, self.button_font)
        self.shop_button = Button((0.5, 0.55), (300, 60), "Shop", STARLIGHT_CYAN, WHITE, self.button_font)
        self.main_menu_button = Button((0.5, 0.7), (300, 60), "Main Menu", GRAY, WHITE, self.button_font)
        self.back_button = Button((0.5, 0.85), (300, 60), "Back", GRAY, WHITE, self.button_font)
        self.shop_buttons = {name: Button((0.5, 0.35 + i*0.1), (500,60),"",AURORA_GREEN,WHITE, self.button_font) for i, name in enumerate(UPGRADE_NAMES)}
        self.mode_buttons = {
            "classic": Button((0.5, 0.25), (300, 60), "Classic", YELLOW, WHITE, self.button_font),
            "endless": Button((0.5, 0.38), (300, 60), "Endless", STARLIGHT_CYAN, WHITE, self.button_font),
            "boss_rush": Button((0.5, 0.51), (300, 60), "Boss Rush", RED, WHITE, self.button_font),
            "chaos": Button((0.5, 0.64), (300, 60), "Chaos", COSMIC_MAGENTA, WHITE, self.button_font),
            "stealth": Button((0.5, 0.77), (300, 60), "Stealth", DARK_GRAY, WHITE, self.button_font)
        }
        self.difficulty_buttons = [Button((0.5, 0.3 + i*0.1), (300, 60), name, color, WHITE, self.button_font) for i, (name,color) in enumerate(zip(["Tutorial","Easy","Beginner","Casual","Hardcore","Insane","Demon"], [STARLIGHT_CYAN,AURORA_GREEN,AURORA_GREEN,YELLOW,RED,COSMIC_MAGENTA,NEBULA_PURPLE]))]
        self.back_to_menu_button = Button((0.5, 0.9), (300, 60), "Back to Menu", GRAY, WHITE, self.button_font)
        self.back_to_mode_button = Button((0.5, 0.3 + 7*0.1), (300, 60), "Back", GRAY, WHITE, self.button_font)
        self.reset_button = Button((0.5, 0.7), (200,60), "To Menu", GRAY, WHITE, self.button_font)
        self.continue_button = Button((0.5, 0.75), (200,60), "Continue", GRAY, WHITE, self.button_font)
        self.exit_button = Button((0.5, 0.85), (200,60), "Exit", GRAY, WHITE, self.button_font)
        self.all_ui_elements = [self.start_button, self.stats_button, self.quit_button, self.resume_button, self.shop_button, self.main_menu_button, self.back_button, self.back_to_menu_button, self.back_to_mode_button, self.reset_button, self.continue_button, self.exit_button] + list(self.shop_buttons.values()) + list(self.mode_buttons.values()) + self.difficulty_buttons

    def reposition_all_ui(self):
        screen_size = self.screen.get_size()
        for element in self.all_ui_elements: element.reposition(screen_size)

    def reset_game_state(self, difficulty, game_mode):
        old_upgrades = getattr(self, 'upgrades', {"damage": 0, "lives": 0, "dust_bonus": 0, "powerup_time": 0})
        old_stats = getattr(self, 'stats', self.load_stats())
        old_high_scores = getattr(self, 'high_scores', self.load_high_scores())
        old_cosmic_dust = getattr(self, 'cosmic_dust', 0)
        self.game_state, self.game_mode, self.difficulty, self.level = "playing", game_mode, difficulty, 1
        lives = DIFFICULTY_SETTINGS.get(difficulty, {}).get("lives", 10)
        self.max_lives, self.lives = lives + old_upgrades["lives"], lives + old_upgrades["lives"]
        self.score, self.score_multiplier_penalty_timer = 0, 0
        self.boxes, self.asteroids, self.particles, self.floating_texts = [], [], [], []
        self.boss, self.circle, self.power_up, self.active_black_hole, self.snail, self.nyan_cat = None, None, None, None, None, None
        self.power_up_active, self.power_up_timer, self.last_boss_speed = None, 0, 5
        self.combo, self.combo_timer, self.hud_active, self.player_sequence = 0, 0, True, []
        w, h = self.screen.get_size()
        self.cursor_pos = [w//2, h//2]
        self.screen_shake, self.shake_intensity, self.level_clear_timer = 0, 0, 0
        self.meteor_event_timer, self.chaos_event_timer, self.screen_flipped = time.time() + 30, time.time() + 15, False
        self.upgrades, self.stats, self.high_scores, self.cosmic_dust = old_upgrades, old_stats, old_high_scores, old_cosmic_dust
        self.box_colors = [NEBULA_BLUE, NEBULA_PURPLE, GALAXY_INDIGO, STARLIGHT_CYAN, COSMIC_MAGENTA, AURORA_GREEN, RED]
        self.basic_tapper, self.cheat_tapper = Tool("basic", 1, 1, 1, False), Tool("cheat", 99, 999999, 1000, True)
        self.equipped_tool = self.cheat_tapper if getattr(self, 'debug_mode', False) else self.basic_tapper
        self.start_new_level()

    def load_high_scores(self):
        try:
            with open("highscores.txt", "r") as f: return [int(line.strip()) for line in f if line.strip().isdigit()][:MAX_HIGH_SCORES]
        except FileNotFoundError: return [0] * MAX_HIGH_SCORES
    def save_high_scores(self):
        self.high_scores.append(int(self.score))
        self.high_scores = sorted(list(set(self.high_scores)), reverse=True)[:MAX_HIGH_SCORES]
        with open("highscores.txt", "w") as f:
            for hs in self.high_scores: f.write(f"{hs}\n")
    def load_stats(self):
        try:
            with open("stats.json", "r") as f: return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError): return {"boxes_tapped": 0, "powerups_collected": 0, "snails_harmed": 0, "total_score": 0, "bosses_defeated": 0}
    def save_stats(self):
        with open("stats.json", "w") as f: json.dump(self.stats, f, indent=4)

    def spawn_stars_and_nebulae(self):
        w, h = self.screen.get_size()
        self.stars = [Star(w, h) for _ in range(100)]
        self.nebulae = [Nebula(w, h) for _ in range(3)]

    def start_new_level(self):
        self.game_state = "playing"
        if self.game_mode == "classic" and self.level > MAX_LEVEL_CLASSIC:
            self.game_state = "victory"
            return
        self.boxes, self.boss, self.circle, self.asteroids, self.snail = [], None, None, [], None
        if self.game_mode == "boss_rush": self.spawn_boss()
        elif self.level % 10 == 0: self.spawn_circle()
        elif self.level % 5 == 0: self.spawn_boss()
        else: self.spawn_boxes()
        self.spawn_power_up()

    def create_explosion(self, x, y, color):
        for _ in range(10): self.particles.append(Particle(x, y, color))
    def trigger_screen_shake(self, intensity=10, duration=15):
        self.screen_shake, self.shake_intensity = duration, intensity
    def spawn_floating_text(self, x, y, text, color):
        self.floating_texts.append(FloatingText(x, y, text, color, self.font))
    def spawn_boxes(self):
        w, h = self.screen.get_size()
        spawn_mod = DIFFICULTY_SETTINGS[self.difficulty]["spawn_mod"]
        num_boxes = int((5 + self.level // 10) * spawn_mod)
        for _ in range(num_boxes):
            size = random.randint(50, 100)
            x, y = random.randint(0, w - size), random.randint(0, h - size)
            health = BASE_BOX_HEALTH * DIFFICULTY_SETTINGS[self.difficulty]["health_mod"]
            self.boxes.append(Box(self, x, y, size, size, random.choice(self.box_colors), health))
    def spawn_boss(self):
        w, h = self.screen.get_size()
        size = (min(200, w - 20), min(200, h - 20))
        pos = (w // 2 - size[0] // 2, h // 2 - size[1] // 2)
        health = (BASE_BOX_HEALTH * (BOSS_HEALTH_MULTIPLIER ** (self.level // 5))) * DIFFICULTY_SETTINGS[self.difficulty]["health_mod"]
        self.boss = Boss(self, *pos, *size, NEBULA_PURPLE, health)
        self.last_boss_speed = self.boss.speed
    def spawn_circle(self):
        w, h = self.screen.get_size()
        self.circle = Circle(self, w//2, h//2, 40, self.last_boss_speed)
    def spawn_power_up(self):
        if random.random() < 0.25:
            w, h = self.screen.get_size()
            x, y = random.randint(0, w - 40), random.randint(0, h - 40)
            types = ["speed", "shield", "freeze", "multi_tap", "black_hole", "time_warp", "dust_rush"]
            if self.game_mode == "chaos": types.append("nyan")
            self.power_up = PowerUp(x, y, random.choice(types))
    def spawn_asteroid(self):
        if self.level >= ASTEROID_START_LEVEL and len(self.asteroids) < (self.level // 10):
            if random.random() < 0.02 * DIFFICULTY_SETTINGS[self.difficulty]["asteroid_mod"]:
                self.asteroids.append(Asteroid(self))
    def get_current_score_multiplier(self):
        base = 2 if "DOUBLE_SCORE" in self.active_cheats else 1
        if self.score_multiplier_penalty_timer > 0 and time.time() < self.score_multiplier_penalty_timer: return base * 0.5
        return base

    def update(self):
        if self.game_state == "level_clear":
            if time.time() - self.level_clear_timer > 2: self.level += 1; self.start_new_level()
            return
        if self.game_state != "playing": return

        for item in self.stars + self.nebulae + self.particles[:]:
            if hasattr(item, 'update'):
                if item.update() == False: self.particles.remove(item)
            else: item.update()
        for text in self.floating_texts[:]:
            if not text.update(): self.floating_texts.remove(text)
        for obj in self.boxes[:] + self.asteroids[:] + [self.boss, self.circle, self.snail]:
            if obj:
                if hasattr(obj, 'update'): obj.update()
                elif hasattr(obj, 'move'): obj.move()
        if self.boss:
            for minion in self.boss.minions: minion.update()
        if self.nyan_cat and not self.nyan_cat.update(self.boxes): self.nyan_cat = None
        if self.active_black_hole and not self.active_black_hole.update(self.boxes): self.active_black_hole = None
        self.spawn_asteroid()
        if self.power_up_active:
            duration = (10 if self.power_up_active == "dust_rush" else 5) + self.upgrades["powerup_time"]
            if time.time() - self.power_up_timer > duration:
                self.power_up_active = None
                if "INVINCIBILITY" not in self.active_cheats: self.active_cheats.discard("SHIELD_POWERUP")
            elif self.power_up_active == "dust_rush": self.cosmic_dust += 0.1
        if self.combo > 0 and time.time() - self.combo_timer > 3: self.combo = 0
        if not self.boxes and not self.boss and not self.circle: self.game_state, self.level_clear_timer = "level_clear", time.time()

    def draw(self):
        surface_to_draw_on = self.screen.copy() if self.screen_shake > 0 else self.screen
        surface_to_draw_on.fill(BLACK)
        for nebula in self.nebulae: nebula.draw(surface_to_draw_on)
        for star in self.stars: star.draw(surface_to_draw_on)
        if self.game_state == "main_menu": self.draw_main_menu(surface_to_draw_on)
        elif self.game_state == "mode_select": self.draw_mode_select(surface_to_draw_on)
        elif self.game_state == "difficulty_select": self.draw_difficulty_select(surface_to_draw_on)
        elif self.game_state == "shop": self.draw_shop(surface_to_draw_on)
        elif self.game_state == "stats": self.draw_stats(surface_to_draw_on)
        elif self.game_state in ["playing", "paused", "game_over", "victory", "level_clear"]:
            self.draw_game_screen(surface_to_draw_on)
            if self.game_state == "paused": self.draw_pause_screen(surface_to_draw_on)
            elif self.game_state == "game_over": self.draw_game_over(surface_to_draw_on)
            elif self.game_state == "victory": self.draw_victory(surface_to_draw_on)
            elif self.game_state == "level_clear": self.draw_level_clear(surface_to_draw_on)
        if self.screen_shake > 0:
            self.screen_shake -= 1
            offset = (random.randint(-self.shake_intensity, self.shake_intensity), random.randint(-self.shake_intensity, self.shake_intensity))
            self.screen.blit(surface_to_draw_on, offset)
        pygame.display.flip()

    def draw_text(self, text, font, color, center_pos, surface, outline=False):
        text_surf = font.render(text, True, color)
        text_rect = text_surf.get_rect(center=center_pos)
        if outline:
            outline_surf = font.render(text, True, BLACK)
            for dx in [-2, 0, 2]:
                for dy in [-2, 0, 2]:
                    if dx != 0 or dy != 0: surface.blit(outline_surf, outline_surf.get_rect(center=(center_pos[0] + dx, center_pos[1] + dy)))
        surface.blit(text_surf, text_rect)

    def draw_main_menu(self, s): self.draw_text("Box Tapper: Evolution", self.big_font, WHITE, (s.get_width()//2, s.get_height()//3), s); [b.draw(s, b.is_clicked(pygame.mouse.get_pos())) for b in [self.start_button, self.stats_button, self.quit_button]]
    def draw_mode_select(self, s): self.draw_text("Select Game Mode", self.big_font, WHITE, (s.get_width()//2, 80), s); [b.draw(s, b.is_clicked(pygame.mouse.get_pos())) for b in list(self.mode_buttons.values()) + [self.back_to_menu_button]]
    def draw_difficulty_select(self, s): self.draw_text("Select Difficulty", self.big_font, WHITE, (s.get_width()//2, 80), s); [b.draw(s, b.is_clicked(pygame.mouse.get_pos())) for b in self.difficulty_buttons + [self.back_to_mode_button]]
    def draw_game_screen(self, s):
        for obj in self.boxes + self.asteroids + [self.boss, self.circle, self.power_up, self.snail, self.nyan_cat]:
            if obj: obj.draw(s, self.font) if isinstance(obj, PowerUp) else obj.draw(s)
        if self.boss:
            for minion in self.boss.minions: minion.draw(s)
        if self.active_black_hole: self.active_black_hole.draw(s)
        for p in self.particles: p.draw(s)
        for t in self.floating_texts: t.draw(s)
        if self.hud_active: self.draw_hud(s)
    def draw_hud(self, s):
        self.draw_text(f"Lives: {self.lives}/{self.max_lives}", self.font, WHITE, (100, 30), s, outline=True)
        self.draw_text(f"Level: {self.level}", self.font, WHITE, (100, 60), s, outline=True)
        self.draw_text(f"Score: {int(self.score)}", self.font, WHITE, (100, 90), s, outline=True)
        self.draw_text(f"Dust: {int(self.cosmic_dust)}", self.font, YELLOW, (100, 120), s, outline=True)
    def draw_screen_overlay(self, s, text):
        overlay = pygame.Surface(s.get_size(), pygame.SRCALPHA); overlay.fill((0,0,0,180)); s.blit(overlay, (0,0))
        self.draw_text(text, self.big_font, WHITE, (s.get_width()//2, s.get_height()//3), s)
    def draw_pause_screen(self, s): self.draw_screen_overlay(s, "Paused"); [b.draw(s, b.is_clicked(pygame.mouse.get_pos())) for b in [self.resume_button, self.shop_button, self.main_menu_button]]
    def draw_game_over(self, s): self.draw_screen_overlay(s, "Game Over!"); self.draw_text(f"Final Score: {int(self.score)}", self.font, WHITE, (s.get_width()//2, s.get_height()//2), s); self.reset_button.draw(s, self.reset_button.is_clicked(pygame.mouse.get_pos()))
    def draw_victory(self, s): self.draw_screen_overlay(s, "VICTORY!"); self.draw_text(f"Final Score: {int(self.score)}", self.font, WHITE, (s.get_width()//2, s.get_height()//2), s); self.continue_button.draw(s, self.continue_button.is_clicked(pygame.mouse.get_pos()))
    def draw_level_clear(self, s): self.draw_text("Level Clear!", self.big_font, GOLD, s.get_rect().center, s, outline=True)
    def draw_stats(self, s):
        s.fill(GALAXY_INDIGO)
        self.draw_text("Lifetime Stats", self.big_font, WHITE, (s.get_width()//2, 80), s)
        for i, (key, value) in enumerate(self.stats.items()): self.draw_text(f"{key.replace('_', ' ').title()}: {value:,}", self.stats_font, WHITE, (s.get_width()//2, 200 + i*60), s)
        self.back_to_menu_button.draw(s, self.back_to_menu_button.is_clicked(pygame.mouse.get_pos()))
    def draw_shop(self, s):
        s.fill(GALAXY_INDIGO)
        self.draw_text("Upgrade Shop", self.big_font, WHITE, (s.get_width()//2, 80), s)
        self.draw_text(f"Cosmic Dust: {int(self.cosmic_dust)}", self.font, YELLOW, (s.get_width()//2, 150), s)
        for name, btn in self.shop_buttons.items():
            level, cost = self.upgrades[name], UPGRADE_COSTS[name] * (2 ** self.upgrades[name])
            btn.text = f"{UPGRADE_NAMES[name]} (Lvl {level}) - Cost: {cost}"
            btn.draw(s, btn.is_clicked(pygame.mouse.get_pos()))
        self.back_button.draw(s, self.back_button.is_clicked(pygame.mouse.get_pos()))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT: self.running = False
            elif event.type == pygame.VIDEORESIZE: self.reposition_all_ui()
            elif event.type == pygame.MOUSEMOTION: self.cursor_pos = event.pos
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: self.handle_mouse_click(event.pos)
            elif event.type == pygame.KEYDOWN and (event.key == pygame.K_p or event.key == pygame.K_ESCAPE):
                if self.game_state == "playing": self.game_state = "paused"
                elif self.game_state == "paused": self.game_state = "playing"

    def handle_mouse_click(self, pos):
        if self.game_state == "main_menu":
            if self.start_button.is_clicked(pos): self.game_state = "mode_select"
            elif self.stats_button.is_clicked(pos): self.game_state = "stats"
            elif self.quit_button.is_clicked(pos): self.running = False
        elif self.game_state == "mode_select":
            if self.back_to_menu_button.is_clicked(pos): self.game_state = "main_menu"
            for mode, btn in self.mode_buttons.items():
                if btn.is_clicked(pos): self.game_mode, self.game_state = mode, "difficulty_select"
        elif self.game_state == "difficulty_select":
            if self.back_to_mode_button.is_clicked(pos): self.game_state = "mode_select"
            for btn in self.difficulty_buttons:
                if btn.is_clicked(pos): self.reset_game_state(btn.text.lower(), self.game_mode)
        elif self.game_state == "paused":
            if self.resume_button.is_clicked(pos): self.game_state = "playing"
            if self.shop_button.is_clicked(pos): self.game_state = "shop"
            if self.main_menu_button.is_clicked(pos): self.game_state = "main_menu"
        elif self.game_state == "shop":
            if self.back_button.is_clicked(pos): self.game_state = "paused"
            for name, btn in self.shop_buttons.items():
                if btn.is_clicked(pos): self.purchase_upgrade(name)
        elif self.game_state == "stats":
            if self.back_to_menu_button.is_clicked(pos): self.game_state = "main_menu"
        elif self.game_state == "playing": self.handle_gameplay_click(pos)
        elif self.game_state == "game_over":
            if self.reset_button.is_clicked(pos): self.game_state = "main_menu"
    
    def purchase_upgrade(self, name):
        level = self.upgrades[name]
        cost = UPGRADE_COSTS[name] * (2 ** level)
        if self.cosmic_dust >= cost:
            self.cosmic_dust -= cost
            self.upgrades[name] += 1
            if name == "lives": self.max_lives, self.lives = self.max_lives + 1, self.lives + 1

    def handle_gameplay_click(self, pos):
        hit_something, damage = False, self.equipped_tool.damage + self.upgrades["damage"]
        for asteroid in self.asteroids[:]:
            if asteroid.rect.collidepoint(pos):
                if "INVINCIBILITY" not in self.active_cheats: self.lives -=1
                self.asteroids.remove(asteroid); self.trigger_screen_shake(); return
        
        sorted_boxes = sorted(self.boxes, key=lambda b: b.rect.bottom, reverse=True)
        for box in sorted_boxes:
            if box.rect.collidepoint(pos):
                box.take_damage(damage); hit_something = True; break
        if not hit_something and self.boss and self.boss.rect.collidepoint(pos):
            self.boss.take_damage(damage); hit_something = True
        
        if not hit_something:
            self.player_sequence.append("hit_empty")
            if "INVINCIBILITY" not in self.active_cheats: self.lives -= 1
            self.combo = 0
        if self.lives <= 0: self.save_high_scores(); self.game_state = "game_over"

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        self.save_stats()
        pygame.quit()

if __name__ == '__main__':
    game = Game()
    game.run()
