"""
Snake Game – Extended with:
  1. Border (wall) collision detection
  2. Random food placement that avoids walls and the snake's body
  3. Levels – advance every 3 foods eaten
  4. Speed increases on each new level
  5. Score and level counter displayed on screen
  6. Full comments throughout
"""

import pygame
import random
import sys

# ─────────────────────────────────────────────
# INITIALISATION
# ─────────────────────────────────────────────
pygame.init()

# ─────────────────────────────────────────────
# SCREEN & GRID SETTINGS
# ─────────────────────────────────────────────
CELL   = 20           # size of each grid cell in pixels
COLS   = 30           # number of columns in the grid
ROWS   = 30           # number of rows in the grid
HUD_H  = 50           # height of the HUD strip at the top (pixels)

SCREEN_W = COLS * CELL
SCREEN_H = ROWS * CELL + HUD_H

screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Snake")

# ─────────────────────────────────────────────
# COLOURS  (R, G, B)
# ─────────────────────────────────────────────
BLACK      = (0,   0,   0)
WHITE      = (255, 255, 255)
DARK_GREEN = (0,   150, 0)
LIGHT_GREEN= (0,   200, 0)
RED        = (200, 30,  30)
DARK_GRAY  = (40,  40,  40)
GOLD       = (255, 185, 0)
ORANGE     = (255, 140, 0)
BLUE       = (30,  80,  220)

# ─────────────────────────────────────────────
# FONTS
# ─────────────────────────────────────────────
font_small  = pygame.font.SysFont("Consolas", 20, bold=True)
font_medium = pygame.font.SysFont("Consolas", 32, bold=True)
font_large  = pygame.font.SysFont("Consolas", 52, bold=True)

# ─────────────────────────────────────────────
# LEVEL CONFIGURATION
# ─────────────────────────────────────────────
BASE_FPS          = 8    # frames per second at level 1
FPS_PER_LEVEL     = 2    # additional FPS gained per level
FOODS_PER_LEVEL   = 3    # number of foods to eat to reach next level

# ─────────────────────────────────────────────
# DIRECTION CONSTANTS  (delta column, delta row)
# ─────────────────────────────────────────────
UP    = (0,  -1)
DOWN  = (0,   1)
LEFT  = (-1,  0)
RIGHT = (1,   0)


# ══════════════════════════════════════════════
#  HELPER FUNCTIONS
# ══════════════════════════════════════════════

def random_food(snake_body: list) -> tuple:
    """
    Return a (col, row) position for new food.
    The position must:
      - Not be in the snake's body
      - Not be on the border wall (col/row 0 or max)
    Keeps sampling until a valid cell is found.
    """
    while True:
        col = random.randint(1, COLS - 2)   # avoid column 0 and COLS-1
        row = random.randint(1, ROWS - 2)   # avoid row 0 and ROWS-1
        if (col, row) not in snake_body:
            return (col, row)


def draw_grid():
    """Draw a subtle grid over the play area (below the HUD)."""
    for c in range(COLS):
        for r in range(ROWS):
            rect = pygame.Rect(c * CELL, HUD_H + r * CELL, CELL, CELL)
            pygame.draw.rect(screen, DARK_GRAY, rect, 1)


def draw_walls():
    """
    Shade the border cells darker so the player can see the walls.
    Hitting any of these cells ends the game.
    """
    wall_colour = (80, 80, 80)
    # Top and bottom rows
    for c in range(COLS):
        pygame.draw.rect(screen, wall_colour,
                         pygame.Rect(c * CELL, HUD_H, CELL, CELL))
        pygame.draw.rect(screen, wall_colour,
                         pygame.Rect(c * CELL, HUD_H + (ROWS - 1) * CELL, CELL, CELL))
    # Left and right columns
    for r in range(ROWS):
        pygame.draw.rect(screen, wall_colour,
                         pygame.Rect(0, HUD_H + r * CELL, CELL, CELL))
        pygame.draw.rect(screen, wall_colour,
                         pygame.Rect((COLS - 1) * CELL, HUD_H + r * CELL, CELL, CELL))


def draw_snake(snake_body: list):
    """Draw each segment of the snake; head is a different shade."""
    for i, (c, r) in enumerate(snake_body):
        colour = LIGHT_GREEN if i == 0 else DARK_GREEN   # head vs body
        rect = pygame.Rect(c * CELL + 1, HUD_H + r * CELL + 1, CELL - 2, CELL - 2)
        pygame.draw.rect(screen, colour, rect, border_radius=4)


def draw_food(food_pos: tuple):
    """Draw the food as a red circle."""
    c, r = food_pos
    cx = c * CELL + CELL // 2
    cy = HUD_H + r * CELL + CELL // 2
    pygame.draw.circle(screen, RED, (cx, cy), CELL // 2 - 2)


def draw_hud(score: int, level: int, fps: int):
    """Render the HUD bar: score on the left, level on the right."""
    pygame.draw.rect(screen, (20, 20, 20), pygame.Rect(0, 0, SCREEN_W, HUD_H))
    score_surf = font_small.render(f"Score: {score}", True, WHITE)
    level_surf = font_small.render(f"Level: {level}  Speed: {fps} FPS", True, GOLD)
    screen.blit(score_surf, (10, 14))
    screen.blit(level_surf, (SCREEN_W - level_surf.get_width() - 10, 14))


def show_message(title: str, sub: str):
    """
    Show a centred overlay with title and sub-text.
    Returns when the player presses SPACE or R.
    """
    overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))   # semi-transparent black
    screen.blit(overlay, (0, 0))

    t_surf = font_large.render(title, True, RED)
    s_surf = font_medium.render(sub,  True, WHITE)
    h_surf = font_small.render("Press SPACE / R to restart  |  Q to quit", True, (180, 180, 180))

    screen.blit(t_surf, t_surf.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 - 60)))
    screen.blit(s_surf, s_surf.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 + 10)))
    screen.blit(h_surf, h_surf.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 + 70)))
    pygame.display.update()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_SPACE, pygame.K_r):
                    return   # restart
                if event.key == pygame.K_q:
                    pygame.quit(); sys.exit()


def show_level_up(level: int):
    """Briefly flash "Level Up!" on screen."""
    overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 100))
    screen.blit(overlay, (0, 0))
    lu_surf = font_large.render(f"Level {level}!", True, ORANGE)
    screen.blit(lu_surf, lu_surf.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2)))
    pygame.display.update()
    pygame.time.delay(700)   # show for 700 ms


# ══════════════════════════════════════════════
#  MAIN GAME LOOP
# ══════════════════════════════════════════════

def game_loop():
    """Run one full snake session."""

    clock = pygame.time.Clock()

    # ── Initial snake state ────────────────────
    # Snake is a list of (col, row) tuples; index 0 is the head
    snake  = [(COLS // 2, ROWS // 2),
              (COLS // 2 - 1, ROWS // 2),
              (COLS // 2 - 2, ROWS // 2)]
    direction     = RIGHT         # current movement direction
    next_direction = RIGHT        # queued direction (applied once per tick)

    # ── Food ───────────────────────────────────
    food = random_food(snake)

    # ── Score / level state ────────────────────
    score          = 0
    level          = 1
    foods_eaten    = 0     # counts food eaten within the current level
    current_fps    = BASE_FPS

    running = True
    while running:

        # ── Event handling ─────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if event.type == pygame.KEYDOWN:
                # Change direction – prevent 180° reversal
                if event.key == pygame.K_UP    and direction != DOWN:
                    next_direction = UP
                elif event.key == pygame.K_DOWN  and direction != UP:
                    next_direction = DOWN
                elif event.key == pygame.K_LEFT  and direction != RIGHT:
                    next_direction = LEFT
                elif event.key == pygame.K_RIGHT and direction != LEFT:
                    next_direction = RIGHT
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()

        # ── Apply the queued direction ─────────
        direction = next_direction

        # ── Move: compute new head position ───
        dc, dr = direction
        new_head = (snake[0][0] + dc, snake[0][1] + dr)

        # ── 1. Border / wall collision ─────────
        # The border is col 0, col COLS-1, row 0, row ROWS-1
        nc, nr = new_head
        if nc <= 0 or nc >= COLS - 1 or nr <= 0 or nr >= ROWS - 1:
            show_message("GAME OVER", f"Hit the wall!  Score: {score}")
            return    # restart

        # ── 2. Self-collision ──────────────────
        if new_head in snake:
            show_message("GAME OVER", f"Bit yourself!  Score: {score}")
            return

        # ── 3. Update snake body ───────────────
        snake.insert(0, new_head)   # prepend new head

        # ── 4. Food collision ──────────────────
        if new_head == food:
            score       += 10
            foods_eaten += 1
            food = random_food(snake)   # spawn new food

            # ── 5. Level-up check ──────────────
            if foods_eaten >= FOODS_PER_LEVEL:
                level       += 1
                foods_eaten  = 0
                current_fps  = BASE_FPS + (level - 1) * FPS_PER_LEVEL
                show_level_up(level)
        else:
            # No food eaten – remove the tail to keep length constant
            snake.pop()

        # ── Drawing ────────────────────────────
        screen.fill(BLACK)
        draw_grid()
        draw_walls()
        draw_snake(snake)
        draw_food(food)
        draw_hud(score, level, current_fps)

        pygame.display.update()
        clock.tick(current_fps)   # game speed tied to the current level


# ══════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════
if __name__ == "__main__":
    # Show a welcome screen before the first game
    screen.fill(BLACK)
    t = font_large.render("SNAKE", True, LIGHT_GREEN)
    s = font_small.render("Arrow keys to move  |  SPACE to start", True, WHITE)
    screen.blit(t, t.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 - 40)))
    screen.blit(s, s.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 + 30)))
    pygame.display.update()
    show_message("SNAKE", "Arrow keys to move")

    while True:          # outer loop handles restarts
        game_loop()
