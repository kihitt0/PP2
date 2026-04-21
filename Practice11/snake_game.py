"""
Snake Game – Practice 11
Extends Practice 10 with:
  1. Weighted food types – Apple (10 pts), Cherry (25 pts), Star (50 pts)
     each with its own spawn probability, colour, and lifetime.
  2. Food items disappear after a timed duration; a white countdown arc
     drawn around each food shows how much time remains.
  3. Up to MAX_FOODS items are visible on the board simultaneously.
  4. Full comments throughout.
"""

import pygame
import random
import sys
import math

pygame.init()

# ─────────────────────────────────────────────
# SCREEN & GRID SETTINGS
# ─────────────────────────────────────────────
CELL   = 20
COLS   = 30
ROWS   = 30
HUD_H  = 50

SCREEN_W = COLS * CELL
SCREEN_H = ROWS * CELL + HUD_H

screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Snake – Practice 11")

# ─────────────────────────────────────────────
# COLOURS
# ─────────────────────────────────────────────
BLACK       = (0,   0,   0)
WHITE       = (255, 255, 255)
DARK_GREEN  = (0,   150, 0)
LIGHT_GREEN = (0,   200, 0)
RED         = (200, 30,  30)
DARK_GRAY   = (40,  40,  40)
GOLD        = (255, 185, 0)
ORANGE      = (255, 140, 0)

# ─────────────────────────────────────────────
# FONTS
# ─────────────────────────────────────────────
font_small  = pygame.font.SysFont("Consolas", 20, bold=True)
font_medium = pygame.font.SysFont("Consolas", 32, bold=True)
font_large  = pygame.font.SysFont("Consolas", 52, bold=True)
font_tiny   = pygame.font.SysFont("Arial",    10, bold=True)

# ─────────────────────────────────────────────
# LEVEL CONFIGURATION
# ─────────────────────────────────────────────
BASE_FPS      = 8    # starting speed
FPS_PER_LEVEL = 2    # extra FPS per level
FOODS_PER_LVL = 3    # foods to eat before levelling up

# ─────────────────────────────────────────────
# DIRECTION CONSTANTS  (delta_col, delta_row)
# ─────────────────────────────────────────────
UP    = (0,  -1)
DOWN  = (0,   1)
LEFT  = (-1,  0)
RIGHT = (1,   0)

# ─────────────────────────────────────────────
# FOOD TYPE DEFINITIONS
# ─────────────────────────────────────────────
# Each dict describes one food variant:
#   colour   – main disc colour
#   ring     – outer ring colour
#   pts      – points awarded on collection
#   life     – milliseconds before the food vanishes if not eaten
#   weight   – relative spawn probability (higher = more common)
#   label    – single character drawn inside the disc
FOOD_TYPES = [
    {
        "name":   "Apple",
        "colour": (220, 40,  40),
        "ring":   (160, 20,  20),
        "pts":    10,
        "life":   8000,   # 8 seconds
        "weight": 50,     # 50 % chance
        "label":  "A",
    },
    {
        "name":   "Cherry",
        "colour": (200, 0,   120),
        "ring":   (140, 0,   80),
        "pts":    25,
        "life":   6000,   # 6 seconds
        "weight": 35,     # 35 % chance
        "label":  "C",
    },
    {
        "name":   "Star",
        "colour": (255, 210, 0),
        "ring":   (180, 140, 0),
        "pts":    50,
        "life":   4000,   # 4 seconds – rarest and fastest to expire
        "weight": 15,     # 15 % chance
        "label":  "*",
    },
]
FOOD_WEIGHTS = [ft["weight"] for ft in FOOD_TYPES]

# Maximum number of food items visible on the board at the same time
MAX_FOODS = 3
# Minimum interval (ms) between automatic food spawns
FOOD_SPAWN_INTERVAL = 2000


# ══════════════════════════════════════════════
#  HELPER FUNCTIONS
# ══════════════════════════════════════════════

def spawn_food(snake_body: list, existing_foods: list) -> dict:
    """
    Create a new food item at a random valid position:
      - Not on the border wall
      - Not on the snake's body
      - Not on an existing food item
    Chooses the food type according to FOOD_WEIGHTS.
    Returns a dict with keys: pos, type, born.
    """
    occupied = set(snake_body) | {f["pos"] for f in existing_foods}
    while True:
        pos = (random.randint(1, COLS - 2), random.randint(1, ROWS - 2))
        if pos not in occupied:
            ftype = random.choices(FOOD_TYPES, weights=FOOD_WEIGHTS, k=1)[0]
            return {
                "pos":  pos,
                "type": ftype,
                "born": pygame.time.get_ticks(),   # spawn timestamp
            }


def draw_grid():
    """Draw a faint grid over the play area."""
    for c in range(COLS):
        for r in range(ROWS):
            pygame.draw.rect(
                screen, DARK_GRAY,
                pygame.Rect(c * CELL, HUD_H + r * CELL, CELL, CELL), 1
            )


def draw_walls():
    """Shade the border cells to make the walls visible."""
    wc = (80, 80, 80)
    for c in range(COLS):
        pygame.draw.rect(screen, wc, pygame.Rect(c * CELL, HUD_H, CELL, CELL))
        pygame.draw.rect(screen, wc, pygame.Rect(c * CELL,
                                                  HUD_H + (ROWS - 1) * CELL, CELL, CELL))
    for r in range(ROWS):
        pygame.draw.rect(screen, wc, pygame.Rect(0, HUD_H + r * CELL, CELL, CELL))
        pygame.draw.rect(screen, wc, pygame.Rect((COLS - 1) * CELL,
                                                  HUD_H + r * CELL, CELL, CELL))


def draw_snake(body: list):
    """Draw the snake body; head is brighter than the rest."""
    for i, (c, r) in enumerate(body):
        colour = LIGHT_GREEN if i == 0 else DARK_GREEN
        pygame.draw.rect(
            screen, colour,
            pygame.Rect(c * CELL + 1, HUD_H + r * CELL + 1, CELL - 2, CELL - 2),
            border_radius=4
        )


def draw_foods(foods: list):
    """
    Draw each food item with its colour scheme and a countdown arc.

    The arc is drawn counterclockwise from the bottom of the circle, which
    appears clockwise on screen (due to pygame's inverted Y axis).  It starts
    as a full circle when the food is fresh and shrinks to nothing as the food
    is about to expire, giving the player a clear visual warning.
    """
    now = pygame.time.get_ticks()

    for food in foods:
        c, r  = food["pos"]
        ft    = food["type"]
        age   = now - food["born"]
        # ratio: 1.0 = just spawned, 0.0 = about to disappear
        ratio = max(0.0, 1.0 - age / ft["life"])

        cx  = c * CELL + CELL // 2
        cy  = HUD_H + r * CELL + CELL // 2
        rad = CELL // 2 - 1

        # Outer ring then inner disc
        pygame.draw.circle(screen, ft["ring"],   (cx, cy), rad)
        pygame.draw.circle(screen, ft["colour"], (cx, cy), rad - 3)

        # Single-character label so the player knows what food type it is
        lbl = font_tiny.render(ft["label"], True, BLACK)
        screen.blit(lbl, lbl.get_rect(center=(cx, cy)))

        # Countdown arc: sweeps clockwise from 12 o'clock as time passes
        if ratio > 0.02:
            arc_rect    = pygame.Rect(cx - rad, cy - rad, rad * 2, rad * 2)
            stop_angle  = math.pi / 2                        # top of circle
            start_angle = stop_angle - ratio * 2 * math.pi  # shrinks as ratio falls
            pygame.draw.arc(screen, WHITE, arc_rect, start_angle, stop_angle, 2)


def draw_hud(score: int, level: int, fps: int):
    """Draw the HUD bar: score on the left, level + speed on the right."""
    pygame.draw.rect(screen, (20, 20, 20), pygame.Rect(0, 0, SCREEN_W, HUD_H))
    screen.blit(font_small.render(f"Score: {score}", True, WHITE), (10, 14))
    lvl_s = font_small.render(f"Level: {level}  {fps} FPS", True, GOLD)
    screen.blit(lvl_s, (SCREEN_W - lvl_s.get_width() - 10, 14))


def show_message(title: str, sub: str):
    """Show a centred overlay and wait for SPACE/R (restart) or Q (quit)."""
    overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    screen.blit(overlay, (0, 0))

    for surf, cy in [
        (font_large.render(title, True, RED),                              SCREEN_H // 2 - 60),
        (font_medium.render(sub,   True, WHITE),                           SCREEN_H // 2 + 10),
        (font_small.render("SPACE / R – restart   Q – quit",
                           True, (180, 180, 180)),                         SCREEN_H // 2 + 70),
    ]:
        screen.blit(surf, surf.get_rect(center=(SCREEN_W // 2, cy)))

    pygame.display.update()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_SPACE, pygame.K_r):
                    return
                if event.key == pygame.K_q:
                    pygame.quit(); sys.exit()


def show_level_up(level: int):
    """Flash a level-up banner for 700 ms."""
    overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 100))
    screen.blit(overlay, (0, 0))
    s = font_large.render(f"Level {level}!", True, ORANGE)
    screen.blit(s, s.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2)))
    pygame.display.update()
    pygame.time.delay(700)


# ══════════════════════════════════════════════
#  MAIN GAME LOOP
# ══════════════════════════════════════════════

def game_loop():
    """Run one complete snake session and return when the player dies."""
    clock = pygame.time.Clock()

    # Initial snake: three cells moving right from the centre
    snake  = [(COLS // 2, ROWS // 2),
              (COLS // 2 - 1, ROWS // 2),
              (COLS // 2 - 2, ROWS // 2)]
    direction  = RIGHT
    next_dir   = RIGHT

    # Start with one food item on the board
    foods      = [spawn_food(snake, [])]
    food_timer = pygame.time.get_ticks()   # tracks when to add more food

    score      = 0
    level      = 1
    eaten_cnt  = 0    # foods eaten in the current level
    cur_fps    = BASE_FPS

    while True:
        # ── Events ────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                # Queue the new direction; prevent 180° reversal
                if   event.key == pygame.K_UP    and direction != DOWN:  next_dir = UP
                elif event.key == pygame.K_DOWN  and direction != UP:    next_dir = DOWN
                elif event.key == pygame.K_LEFT  and direction != RIGHT: next_dir = LEFT
                elif event.key == pygame.K_RIGHT and direction != LEFT:  next_dir = RIGHT
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()

        # Apply the queued direction and advance the head
        direction = next_dir
        dc, dr    = direction
        head      = (snake[0][0] + dc, snake[0][1] + dr)

        # ── 1. Wall/border collision ───────────
        if head[0] <= 0 or head[0] >= COLS - 1 or head[1] <= 0 or head[1] >= ROWS - 1:
            show_message("GAME OVER", f"Hit the wall!   Score: {score}")
            return

        # ── 2. Self collision ──────────────────
        # Exclude the tail (snake[:-1]) because it moves away this same tick,
        # so stepping onto the tail cell is legal.
        if head in snake[:-1]:
            show_message("GAME OVER", f"Bit yourself!   Score: {score}")
            return

        snake.insert(0, head)   # prepend the new head

        # ── 3. Food collection ─────────────────
        eaten = next((f for f in foods if f["pos"] == head), None)
        if eaten:
            score     += eaten["type"]["pts"]
            eaten_cnt += 1
            foods.remove(eaten)

            # Level-up check
            if eaten_cnt >= FOODS_PER_LVL:
                level     += 1
                eaten_cnt  = 0
                cur_fps    = BASE_FPS + (level - 1) * FPS_PER_LEVEL
                show_level_up(level)
        else:
            # No food eaten this tick – remove the tail to keep length constant
            snake.pop()

        # ── 4. Remove expired food items ───────
        now   = pygame.time.get_ticks()
        foods = [f for f in foods if now - f["born"] < f["type"]["life"]]

        # ── 5. Spawn new food periodically ─────
        # Keep the board populated up to MAX_FOODS items
        if len(foods) < MAX_FOODS and now - food_timer > FOOD_SPAWN_INTERVAL:
            foods.append(spawn_food(snake, foods))
            food_timer = now

        # ── Drawing ────────────────────────────
        screen.fill(BLACK)
        draw_grid()
        draw_walls()
        draw_snake(snake)
        draw_foods(foods)
        draw_hud(score, level, cur_fps)

        pygame.display.update()
        clock.tick(cur_fps)


# ══════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════
if __name__ == "__main__":
    show_message("SNAKE", "Arrow keys to move")
    while True:
        game_loop()
