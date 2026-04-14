"""
main.py - Moving Ball Game
A red ball that moves around the screen in response to arrow key presses.
The ball cannot leave the screen boundaries.

Controls:
  ↑  Arrow Up    = Move ball up    (20 px)
  ↓  Arrow Down  = Move ball down  (20 px)
  ←  Arrow Left  = Move ball left  (20 px)
  →  Arrow Right = Move ball right (20 px)
  R              = Reset ball to center
  Q / ESC        = Quit
"""

import sys
import pygame
from ball import Ball

# ── Constants ────────────────────────────────────────────────────────────────
WINDOW_WIDTH  = 800
WINDOW_HEIGHT = 600
FPS           = 60
TITLE         = "Moving Ball 🔴"

BALL_RADIUS   = 25          # 25px radius → 50×50 bounding box
BALL_STEP     = 20          # Pixels per key press

# Colours
BG_COLOR      = (245, 245, 250)    # Off-white
GRID_COLOR    = (220, 220, 235)
TEXT_COLOR    = (60, 60, 80)
BORDER_COLOR  = (180, 60, 60)
ACCENT        = (100, 140, 255)

# Whether to show the grid background
SHOW_GRID = True


def draw_background(surface):
    """Draw a subtle grid pattern on the background."""
    surface.fill(BG_COLOR)
    if SHOW_GRID:
        for x in range(0, WINDOW_WIDTH, 40):
            pygame.draw.line(surface, GRID_COLOR, (x, 0), (x, WINDOW_HEIGHT))
        for y in range(0, WINDOW_HEIGHT, 40):
            pygame.draw.line(surface, GRID_COLOR, (0, y), (WINDOW_WIDTH, y))


def draw_boundary_flash(surface, ball, flash_color=(255, 120, 120)):
    """
    If the ball is touching a wall, highlight that edge in red.
    Provides visual feedback when movement is blocked.
    """
    boundaries = ball.is_at_boundary()
    thickness = 6
    w, h = WINDOW_WIDTH, WINDOW_HEIGHT

    if boundaries["top"]:
        pygame.draw.line(surface, flash_color, (0, 0), (w, 0), thickness)
    if boundaries["bottom"]:
        pygame.draw.line(surface, flash_color, (0, h - 1), (w, h - 1), thickness)
    if boundaries["left"]:
        pygame.draw.line(surface, flash_color, (0, 0), (0, h), thickness)
    if boundaries["right"]:
        pygame.draw.line(surface, flash_color, (w - 1, 0), (w - 1, h), thickness)


def draw_ui(surface, ball, font_info, font_small):
    """
    Draw the HUD: current position and key legend.

    Args:
        surface: Screen surface
        ball: Ball instance
        font_info: Larger font for position
        font_small: Smaller font for key legend
    """
    bx, by = ball.get_position()

    # Position display
    pos_text = font_info.render(f"Position: ({bx:4d}, {by:4d})", True, TEXT_COLOR)
    surface.blit(pos_text, (14, 10))

    # Key legend (bottom bar)
    legend = "[ ↑ ↓ ← → ] Move   [ R ] Reset   [ Q ] Quit"
    leg_surf = font_small.render(legend, True, (130, 130, 160))
    surface.blit(leg_surf, leg_surf.get_rect(centerx=WINDOW_WIDTH // 2,
                                              bottom=WINDOW_HEIGHT - 8))


def main():
    """Main entry point for the Moving Ball game."""
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()

    # ── Fonts ─────────────────────────────────────────────────────────────────
    font_info  = pygame.font.SysFont("monospace", 18, bold=True)
    font_small = pygame.font.SysFont("monospace", 15)

    # ── Ball (starts at center) ───────────────────────────────────────────────
    start_x = WINDOW_WIDTH  // 2
    start_y = WINDOW_HEIGHT // 2
    ball = Ball(start_x, start_y, BALL_RADIUS, WINDOW_WIDTH, WINDOW_HEIGHT, step=BALL_STEP)

    running = True
    while running:
        # ── Event Handling ────────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                # Movement keys
                if event.key == pygame.K_UP:
                    ball.move_up()
                elif event.key == pygame.K_DOWN:
                    ball.move_down()
                elif event.key == pygame.K_LEFT:
                    ball.move_left()
                elif event.key == pygame.K_RIGHT:
                    ball.move_right()

                # Reset to center
                elif event.key == pygame.K_r:
                    ball.x = start_x
                    ball.y = start_y

                # Quit
                elif event.key in (pygame.K_q, pygame.K_ESCAPE):
                    running = False

        # ── Draw ──────────────────────────────────────────────────────────────
        draw_background(screen)

        # Boundary flash feedback
        draw_boundary_flash(screen, ball)

        # Ball
        ball.draw(screen)

        # HUD
        draw_ui(screen, ball, font_info, font_small)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
