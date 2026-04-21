"""
Car Game – Practice 11
Extends Practice 10 with:
  1. Three weighted coin types: Bronze (1 pt), Silver (3 pts), Gold (5 pts)
     spawned according to their probability weights.
  2. Enemy speed increases by 1 every SPEED_BOOST_EVERY coin-points earned.
  3. Full comments throughout.
"""

import pygame
import random
import sys

pygame.init()

# ─────────────────────────────────────────────
# SCREEN SETTINGS
# ─────────────────────────────────────────────
SCREEN_WIDTH  = 400
SCREEN_HEIGHT = 600
DISPLAYSURF   = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Car Game – Practice 11")

# ─────────────────────────────────────────────
# COLOURS
# ─────────────────────────────────────────────
WHITE  = (255, 255, 255)
BLACK  = (0,   0,   0)
RED    = (255, 0,   0)
GREEN  = (0,   200, 0)
GRAY   = (100, 100, 100)
YELLOW = (255, 220, 0)
GOLD   = (255, 185, 0)
SILVER = (192, 192, 192)
BRONZE = (205, 127, 50)

# ─────────────────────────────────────────────
# SPEED & CLOCK
# ─────────────────────────────────────────────
# Global speed used by all moving sprites; increased as the player earns coins.
SPEED = 5

clock = pygame.time.Clock()
FPS   = 60

# ─────────────────────────────────────────────
# FONTS
# ─────────────────────────────────────────────
font_small  = pygame.font.SysFont("Arial", 22, bold=True)
font_medium = pygame.font.SysFont("Arial", 36, bold=True)
font_large  = pygame.font.SysFont("Arial", 60, bold=True)

# ─────────────────────────────────────────────
# COIN CONFIGURATION
# ─────────────────────────────────────────────
# Each entry: (label, disc_colour, ring_colour, points_value, spawn_weight)
# spawn_weight controls how likely that type is; higher = more common.
COIN_TYPES = [
    ("B", BRONZE, (160, 90, 20),   1, 60),  # Bronze: common,  1 pt
    ("S", SILVER, (140, 140, 140), 3, 30),  # Silver: medium,  3 pts
    ("G", GOLD,   YELLOW,          5, 10),  # Gold:   rare,    5 pts
]
COIN_WEIGHTS = [ct[4] for ct in COIN_TYPES]   # extracted for random.choices()

# Enemy speed gets a +1 boost each time the player accumulates this many coin-pts
SPEED_BOOST_EVERY = 10


# ══════════════════════════════════════════════
#  SPRITE CLASSES
# ══════════════════════════════════════════════

class Player(pygame.sprite.Sprite):
    """Player car – moves left/right with the arrow keys."""

    def __init__(self):
        super().__init__()
        self.surf = pygame.Surface((40, 70))
        self.surf.fill(GREEN)
        pygame.draw.rect(self.surf, BLACK, pygame.Rect(5, 10, 30, 20))
        self.rect = self.surf.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 60)
        )

    def update(self, keys):
        """Move left/right and clamp to road boundaries (x: 60..340)."""
        if keys[pygame.K_LEFT]:
            self.rect.move_ip(-5, 0)
        if keys[pygame.K_RIGHT]:
            self.rect.move_ip(5, 0)
        self.rect.clamp_ip(pygame.Rect(60, 0, 280, SCREEN_HEIGHT))


class Enemy(pygame.sprite.Sprite):
    """An enemy car that scrolls downward at the current global SPEED."""

    CAR_COLOURS = [
        (200, 50,  50),
        (50,  50,  200),
        (200, 200, 50),
        (150, 50,  200),
    ]

    def __init__(self):
        super().__init__()
        self.surf = pygame.Surface((40, 70))
        self.surf.fill(random.choice(self.CAR_COLOURS))
        pygame.draw.rect(self.surf, BLACK, pygame.Rect(5, 40, 30, 20))
        self.rect = self.surf.get_rect(
            center=(
                random.randint(60, SCREEN_WIDTH - 60),
                random.randint(-200, -50),
            )
        )

    def update(self):
        """Move down by the global SPEED; remove when off the bottom."""
        self.rect.move_ip(0, SPEED)
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()


class Coin(pygame.sprite.Sprite):
    """
    A weighted coin with a label, colour, and point value.
    Constructed with one row from COIN_TYPES.
    The .points attribute is read by the game loop on collection.
    """

    def __init__(self, coin_type):
        super().__init__()
        label, disc_col, ring_col, self.points, _ = coin_type
        size = 28

        # Transparent surface so the round coin looks correct over the road
        self.surf = pygame.Surface((size, size), pygame.SRCALPHA)
        # Outer ring (darker shade of the coin colour)
        pygame.draw.circle(self.surf, ring_col, (size // 2, size // 2), size // 2)
        # Inner disc (main coin colour)
        pygame.draw.circle(self.surf, disc_col, (size // 2, size // 2), size // 2 - 4)
        # Single-character label centred on the coin
        lbl_font = pygame.font.SysFont("Arial", 13, bold=True)
        lbl_surf = lbl_font.render(label, True, BLACK)
        self.surf.blit(lbl_surf, lbl_surf.get_rect(center=(size // 2, size // 2)))

        self.rect = self.surf.get_rect(
            center=(
                random.randint(70, SCREEN_WIDTH - 70),
                random.randint(-300, -50),
            )
        )

    def update(self):
        """Scroll down; remove when off-screen."""
        self.rect.move_ip(0, SPEED)
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()


# ══════════════════════════════════════════════
#  HELPER FUNCTIONS
# ══════════════════════════════════════════════

def draw_road():
    """Draw grass, tarmac, and white lane-dash markings."""
    DISPLAYSURF.fill(GREEN)
    pygame.draw.rect(DISPLAYSURF, GRAY, pygame.Rect(60, 0, 280, SCREEN_HEIGHT))
    dash_h = 40
    for y in range(0, SCREEN_HEIGHT, dash_h * 2):
        pygame.draw.rect(DISPLAYSURF, WHITE,
                         pygame.Rect(SCREEN_WIDTH // 2 - 4, y, 8, dash_h))


def draw_hud(score, coin_pts, speed_lvl):
    """Render score (top-left), coin total (top-right), and current speed level."""
    # Score – top-left
    DISPLAYSURF.blit(font_small.render(f"Score: {score}", True, WHITE), (10, 10))

    # Coin points – top-right with a small coin icon
    coin_surf = font_small.render(f"Pts: {coin_pts}", True, GOLD)
    cx = SCREEN_WIDTH - coin_surf.get_width() - 10
    DISPLAYSURF.blit(coin_surf, (cx, 10))
    pygame.draw.circle(DISPLAYSURF, GOLD,   (cx - 18, 20), 12)
    pygame.draw.circle(DISPLAYSURF, YELLOW, (cx - 18, 20),  8)

    # Speed level – below the score
    DISPLAYSURF.blit(
        font_small.render(f"Spd: {speed_lvl}", True, (200, 200, 255)),
        (10, 36)
    )


def show_game_over(score, coin_pts):
    """Display the game-over screen and wait for Q (quit) or R (restart)."""
    DISPLAYSURF.fill(RED)
    lines = [
        (font_large.render("GAME OVER", True, WHITE),                     (SCREEN_WIDTH // 2, 220)),
        (font_medium.render(f"Score: {score}  Pts: {coin_pts}", True, WHITE), (SCREEN_WIDTH // 2, 310)),
        (font_small.render("Q = quit   R = restart", True, WHITE),        (SCREEN_WIDTH // 2, 380)),
    ]
    for surf, center in lines:
        DISPLAYSURF.blit(surf, surf.get_rect(center=center))
    pygame.display.update()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    pygame.quit(); sys.exit()
                if event.key == pygame.K_r:
                    return   # caller restarts game_loop


# ══════════════════════════════════════════════
#  MAIN GAME LOOP
# ══════════════════════════════════════════════

def game_loop():
    """Run one full game session."""
    global SPEED
    SPEED = 5   # reset speed at the start of each new game

    player      = Player()
    enemies     = pygame.sprite.Group()
    coins       = pygame.sprite.Group()
    all_sprites = pygame.sprite.Group()
    all_sprites.add(player)

    score      = 0      # survival score (time-based)
    coin_pts   = 0      # accumulated weighted coin points
    speed_lvl  = 1      # current speed level (increases with coin_pts)

    enemy_timer = pygame.time.get_ticks()
    coin_timer  = pygame.time.get_ticks()
    score_timer = pygame.time.get_ticks()

    while True:
        # ── Events ────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

        keys = pygame.key.get_pressed()
        player.update(keys)

        now = pygame.time.get_ticks()

        # Spawn a new enemy every 1.5 seconds
        if now - enemy_timer > 1500:
            e = Enemy()
            enemies.add(e)
            all_sprites.add(e)
            enemy_timer = now

        # Spawn a weighted coin every ~2.5 seconds (±400 ms variance)
        if now - coin_timer > 2500:
            ctype = random.choices(COIN_TYPES, weights=COIN_WEIGHTS, k=1)[0]
            c = Coin(ctype)
            coins.add(c)
            all_sprites.add(c)
            coin_timer = now + random.randint(-400, 400)

        # Increment survival score every 100 ms
        if now - score_timer > 100:
            score += 1
            score_timer = now

        enemies.update()
        coins.update()

        # ── Collision: player hit enemy → game over ──
        if pygame.sprite.spritecollideany(player, enemies):
            show_game_over(score, coin_pts)
            return   # outer loop will restart game_loop

        # ── Collision: player collects coins ──────────
        for coin in pygame.sprite.spritecollide(player, coins, dokill=True):
            coin_pts += coin.points   # add the weighted point value

        # ── Speed boost every SPEED_BOOST_EVERY coin-pts ──
        # Calculate which speed level we should be at based on total coin points
        new_lvl = coin_pts // SPEED_BOOST_EVERY + 1
        if new_lvl > speed_lvl:
            speed_lvl = new_lvl
            SPEED = 4 + speed_lvl   # 5, 6, 7, … as speed_lvl grows

        # ── Drawing ────────────────────────────
        draw_road()
        for sprite in all_sprites:
            DISPLAYSURF.blit(sprite.surf, sprite.rect)
        draw_hud(score, coin_pts, speed_lvl)

        pygame.display.update()
        clock.tick(FPS)


# ══════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════
if __name__ == "__main__":
    while True:
        game_loop()
