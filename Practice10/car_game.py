"""
Car Game - Based on CodersLegacy Pygame Tutorial (Parts 1-3)
Extended with:
  - Randomly appearing coins on the road
  - Coin counter displayed in the top-right corner
  - Full comments throughout the code
"""

import pygame
import random
import time
import sys

# ─────────────────────────────────────────────
# INITIALISATION
# ─────────────────────────────────────────────
pygame.init()

# ─────────────────────────────────────────────
# SCREEN SETTINGS
# ─────────────────────────────────────────────
SCREEN_WIDTH  = 400
SCREEN_HEIGHT = 600
DISPLAYSURF   = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Car Game")

# ─────────────────────────────────────────────
# COLOURS  (R, G, B)
# ─────────────────────────────────────────────
WHITE  = (255, 255, 255)
BLACK  = (0,   0,   0)
RED    = (255, 0,   0)
GREEN  = (0,   200, 0)
GRAY   = (100, 100, 100)
YELLOW = (255, 220, 0)
GOLD   = (255, 185, 0)

# ─────────────────────────────────────────────
# GAME SPEED (increases over time)
# ─────────────────────────────────────────────
SPEED = 5          # pixels enemy/coin moves down per frame
clock = pygame.time.Clock()
FPS   = 60

# ─────────────────────────────────────────────
# FONTS
# ─────────────────────────────────────────────
font_small  = pygame.font.SysFont("Arial", 22, bold=True)
font_medium = pygame.font.SysFont("Arial", 36, bold=True)
font_large  = pygame.font.SysFont("Arial", 60, bold=True)


# ══════════════════════════════════════════════
#  SPRITE CLASSES
# ══════════════════════════════════════════════

class Player(pygame.sprite.Sprite):
    """The car the player controls – moves left and right."""

    def __init__(self):
        super().__init__()
        # Draw the player car as a coloured rectangle (no image required)
        self.surf = pygame.Surface((40, 70))
        self.surf.fill(GREEN)
        # Draw simple windscreen detail
        pygame.draw.rect(self.surf, BLACK, pygame.Rect(5, 10, 30, 20))
        # Create a rect and place it at the bottom-centre of the screen
        self.rect = self.surf.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 60)
        )

    def update(self, keys):
        """Move the player based on arrow-key input."""
        if keys[pygame.K_LEFT]:
            self.rect.move_ip(-5, 0)   # move 5 px left
        if keys[pygame.K_RIGHT]:
            self.rect.move_ip(5, 0)    # move 5 px right

        # Clamp the player inside the screen boundaries
        self.rect.clamp_ip(DISPLAYSURF.get_rect())


class Enemy(pygame.sprite.Sprite):
    """An enemy car that spawns at the top and scrolls downward."""

    # Different "car" colours for variety
    CAR_COLOURS = [
        (200, 50,  50),   # red
        (50,  50,  200),  # blue
        (200, 200, 50),   # yellow
        (150, 50,  200),  # purple
    ]

    def __init__(self):
        super().__init__()
        colour = random.choice(self.CAR_COLOURS)
        self.surf = pygame.Surface((40, 70))
        self.surf.fill(colour)
        # Draw a simple windscreen on the enemy car
        pygame.draw.rect(self.surf, BLACK, pygame.Rect(5, 40, 30, 20))
        # Spawn at a random x position, just above the visible screen
        self.rect = self.surf.get_rect(
            center=(
                random.randint(60, SCREEN_WIDTH - 60),
                random.randint(-200, -50),
            )
        )

    def update(self):
        """Move the enemy downward each frame."""
        self.rect.move_ip(0, SPEED)
        # Remove the sprite when it scrolls off the bottom
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()


class Coin(pygame.sprite.Sprite):
    """
    A golden coin that appears randomly on the road.
    The player earns +1 coin by driving over it.
    """

    def __init__(self):
        super().__init__()
        # Draw the coin as a filled yellow circle on a transparent surface
        size = 24
        self.surf = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(self.surf, GOLD,   (size // 2, size // 2), size // 2)
        pygame.draw.circle(self.surf, YELLOW, (size // 2, size // 2), size // 2 - 4)
        # Spawn above the screen at a random horizontal position
        self.rect = self.surf.get_rect(
            center=(
                random.randint(60, SCREEN_WIDTH - 60),
                random.randint(-300, -50),
            )
        )

    def update(self):
        """Scroll downward; remove when off-screen."""
        self.rect.move_ip(0, SPEED)
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()


# ══════════════════════════════════════════════
#  HELPER FUNCTIONS
# ══════════════════════════════════════════════

def draw_road():
    """Draw a simple road with lane markings."""
    DISPLAYSURF.fill(GREEN)                          # grass on the sides
    road_rect = pygame.Rect(60, 0, 280, SCREEN_HEIGHT)
    pygame.draw.rect(DISPLAYSURF, GRAY, road_rect)  # road surface

    # Dashed centre-line markings
    dash_h = 40
    for y in range(0, SCREEN_HEIGHT, dash_h * 2):
        pygame.draw.rect(DISPLAYSURF, WHITE, pygame.Rect(SCREEN_WIDTH // 2 - 4, y, 8, dash_h))


def draw_hud(score, coins):
    """Render the score (top-left) and coin counter (top-right)."""
    # Score – top-left
    score_surf = font_small.render(f"Score: {score}", True, WHITE)
    DISPLAYSURF.blit(score_surf, (10, 10))

    # Coin icon (small circle) + count – top-right
    coin_count_surf = font_small.render(f"Coins: {coins}", True, GOLD)
    # Right-align: place so the text ends 10 px from the right edge
    text_x = SCREEN_WIDTH - coin_count_surf.get_width() - 10
    DISPLAYSURF.blit(coin_count_surf, (text_x, 10))
    # Draw a small coin icon to the left of the text
    pygame.draw.circle(DISPLAYSURF, GOLD,   (text_x - 18, 20), 12)
    pygame.draw.circle(DISPLAYSURF, YELLOW, (text_x - 18, 20), 8)


def show_game_over(score, coins):
    """Freeze the screen and show a Game Over message."""
    DISPLAYSURF.fill(RED)
    go_surf   = font_large.render("GAME OVER", True, WHITE)
    sc_surf   = font_medium.render(f"Score: {score}  Coins: {coins}", True, WHITE)
    quit_surf = font_small.render("Press Q to quit or R to restart", True, WHITE)

    DISPLAYSURF.blit(go_surf,   go_surf.get_rect(center=(SCREEN_WIDTH // 2, 220)))
    DISPLAYSURF.blit(sc_surf,   sc_surf.get_rect(center=(SCREEN_WIDTH // 2, 310)))
    DISPLAYSURF.blit(quit_surf, quit_surf.get_rect(center=(SCREEN_WIDTH // 2, 380)))
    pygame.display.update()

    # Wait for the player to choose
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    pygame.quit(); sys.exit()
                if event.key == pygame.K_r:
                    return          # caller will restart the game loop


# ══════════════════════════════════════════════
#  MAIN GAME LOOP
# ══════════════════════════════════════════════

def game_loop():
    """Run one full game session and return when it ends."""

    global SPEED
    SPEED = 5           # reset speed at the start of each session

    # ── Sprite groups ──────────────────────────
    player   = Player()
    enemies  = pygame.sprite.Group()
    coins    = pygame.sprite.Group()
    # A group that holds every sprite (useful for batch drawing)
    all_sprites = pygame.sprite.Group()
    all_sprites.add(player)

    # ── Game-state variables ───────────────────
    score       = 0     # increases with time survived
    coin_count  = 0     # increases when a coin is collected

    # Timers (milliseconds) for spawning enemies and coins
    enemy_spawn_time = pygame.time.get_ticks()
    coin_spawn_time  = pygame.time.get_ticks()
    speed_up_time    = pygame.time.get_ticks()

    running = True
    while running:

        # ── Event handling ─────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

        # ── Player input ───────────────────────
        keys = pygame.key.get_pressed()
        player.update(keys)

        # ── Spawn enemy cars every ~1.5 seconds ─
        now = pygame.time.get_ticks()
        if now - enemy_spawn_time > 1500:
            enemy = Enemy()
            enemies.add(enemy)
            all_sprites.add(enemy)
            enemy_spawn_time = now

        # ── Spawn a coin every ~2.5 seconds ─────
        if now - coin_spawn_time > 2500:
            coin = Coin()
            coins.add(coin)
            all_sprites.add(coin)
            coin_spawn_time = now + random.randint(-500, 500)  # slight randomness

        # ── Increase speed every 10 seconds ─────
        if now - speed_up_time > 10_000:
            SPEED += 1
            speed_up_time = now

        # ── Update all moving sprites ──────────
        enemies.update()
        coins.update()

        # ── Collision: player ↔ enemy ──────────
        if pygame.sprite.spritecollideany(player, enemies):
            show_game_over(score, coin_count)
            return   # go back to outer loop which will restart

        # ── Collision: player ↔ coin ───────────
        collected = pygame.sprite.spritecollide(player, coins, dokill=True)
        coin_count += len(collected)   # add one for each coin collected

        # ── Increment score over time ──────────
        score += 1

        # ── Drawing ────────────────────────────
        draw_road()                    # background

        for sprite in all_sprites:     # draw every sprite onto the surface
            DISPLAYSURF.blit(sprite.surf, sprite.rect)

        draw_hud(score, coin_count)    # HUD on top

        pygame.display.update()        # flip buffer to screen
        clock.tick(FPS)                # cap at 60 FPS


# ══════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════
if __name__ == "__main__":
    while True:      # outer loop allows restarting after game over
        game_loop()
