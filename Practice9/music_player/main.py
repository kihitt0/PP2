"""
main.py - Music Player Application
An interactive music player built with Pygame.

Keyboard Controls:
  P        = Play / Restart current track
  S        = Stop
  N        = Next track
  B        = Previous (Back) track
  UP/DOWN  = Volume up / down
  Q / ESC  = Quit
"""

import sys
import os
import pygame
from player import MusicPlayer

# ── Constants ────────────────────────────────────────────────────────────────
WINDOW_WIDTH  = 620
WINDOW_HEIGHT = 420
FPS           = 30
TITLE         = "🎵 Pygame Music Player"

# Colour palette
BG_COLOR      = (18, 18, 30)
PANEL_COLOR   = (30, 30, 50)
ACCENT        = (100, 200, 255)
TEXT_COLOR    = (230, 230, 255)
DIM_TEXT      = (120, 120, 160)
PLAYING_COLOR = (80, 255, 140)
STOPPED_COLOR = (255, 100, 100)
BAR_BG        = (50, 50, 80)
BAR_FG        = (100, 200, 255)

MUSIC_DIR     = os.path.join(os.path.dirname(__file__), "music")


def draw_rounded_rect(surface, color, rect, radius=12, border=0, border_color=None):
    """Draw a rounded rectangle, optionally with a border."""
    pygame.draw.rect(surface, color, rect, border_radius=radius)
    if border and border_color:
        pygame.draw.rect(surface, border_color, rect, border, border_radius=radius)


def draw_progress_bar(surface, x, y, w, h, fraction, bg, fg):
    """Draw a horizontal progress / volume bar."""
    draw_rounded_rect(surface, bg, pygame.Rect(x, y, w, h), radius=h // 2)
    if fraction > 0:
        filled_w = max(h, int(w * fraction))  # min width = height (round cap)
        draw_rounded_rect(surface, fg, pygame.Rect(x, y, filled_w, h), radius=h // 2)


def main():
    """Main entry point for the Music Player application."""
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()

    # ── Fonts ─────────────────────────────────────────────────────────────────
    font_title  = pygame.font.SysFont("monospace", 28, bold=True)
    font_track  = pygame.font.SysFont("monospace", 22, bold=True)
    font_info   = pygame.font.SysFont("monospace", 17)
    font_key    = pygame.font.SysFont("monospace", 15)

    # ── Player ────────────────────────────────────────────────────────────────
    player = MusicPlayer(MUSIC_DIR)

    # ── Key mapping for on-screen legend ─────────────────────────────────────
    key_legend = [
        ("[P]", "Play"),
        ("[S]", "Stop"),
        ("[N]", "Next"),
        ("[B]", "Back"),
        ("[↑/↓]", "Volume"),
        ("[Q]", "Quit"),
    ]

    running = True
    while running:
        # ── Events ───────────────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    player.play()
                elif event.key == pygame.K_s:
                    player.stop()
                elif event.key == pygame.K_n:
                    player.next_track()
                elif event.key == pygame.K_b:
                    player.prev_track()
                elif event.key == pygame.K_UP:
                    player.volume_up()
                elif event.key == pygame.K_DOWN:
                    player.volume_down()
                elif event.key in (pygame.K_q, pygame.K_ESCAPE):
                    running = False

        # ── Update ───────────────────────────────────────────────────────────
        player.update()   # Auto-advance when track ends

        # ── Draw background ───────────────────────────────────────────────────
        screen.fill(BG_COLOR)

        # Subtle grid background
        for x in range(0, WINDOW_WIDTH, 40):
            pygame.draw.line(screen, (28, 28, 45), (x, 0), (x, WINDOW_HEIGHT))
        for y in range(0, WINDOW_HEIGHT, 40):
            pygame.draw.line(screen, (28, 28, 45), (0, y), (WINDOW_WIDTH, y))

        # ── Main panel ────────────────────────────────────────────────────────
        panel = pygame.Rect(30, 20, WINDOW_WIDTH - 60, WINDOW_HEIGHT - 40)
        draw_rounded_rect(screen, PANEL_COLOR, panel, radius=20,
                          border=2, border_color=(60, 60, 100))

        # Title
        title_surf = font_title.render("♫ MUSIC PLAYER", True, ACCENT)
        screen.blit(title_surf, title_surf.get_rect(centerx=WINDOW_WIDTH // 2, top=38))

        # Divider
        pygame.draw.line(screen, (60, 60, 100),
                         (60, 82), (WINDOW_WIDTH - 60, 82), 1)

        # Status badge
        status_text = player.get_status()
        status_color = PLAYING_COLOR if player.is_playing else STOPPED_COLOR
        status_surf = font_info.render(status_text, True, status_color)
        screen.blit(status_surf, status_surf.get_rect(centerx=WINDOW_WIDTH // 2, top=92))

        # Track name
        track_name = player.get_track_name()
        # Truncate long names
        if len(track_name) > 36:
            track_name = track_name[:33] + "..."
        track_surf = font_track.render(track_name, True, TEXT_COLOR)
        screen.blit(track_surf, track_surf.get_rect(centerx=WINDOW_WIDTH // 2, top=128))

        # Playlist position
        pl_info = player.get_playlist_info()
        pl_surf = font_info.render(pl_info, True, DIM_TEXT)
        screen.blit(pl_surf, pl_surf.get_rect(centerx=WINDOW_WIDTH // 2, top=162))

        # ── Playback position bar ─────────────────────────────────────────────
        pos_ms = player.get_position_ms()
        # We don't know total length easily, so show elapsed seconds as rolling bar
        bar_x, bar_y, bar_w, bar_h = 70, 200, WINDOW_WIDTH - 140, 14
        # Use a 3-minute max (180 000 ms) as estimate; just shows progress aesthetically
        fraction = min(pos_ms / 180_000, 1.0) if player.is_playing else 0
        draw_progress_bar(screen, bar_x, bar_y, bar_w, bar_h, fraction, BAR_BG, BAR_FG)
        pos_label = font_key.render(
            f"Elapsed: {pos_ms // 60000:02d}:{(pos_ms // 1000) % 60:02d}", True, DIM_TEXT)
        screen.blit(pos_label, (bar_x, bar_y + 20))

        # ── Volume bar ────────────────────────────────────────────────────────
        vol_label = font_key.render(f"Volume: {int(player.volume * 100):3d}%", True, DIM_TEXT)
        screen.blit(vol_label, (bar_x, 254))
        draw_progress_bar(screen, bar_x, 274, bar_w, 10,
                          player.volume, BAR_BG, (255, 200, 80))

        # ── Keyboard legend ───────────────────────────────────────────────────
        pygame.draw.line(screen, (60, 60, 100),
                         (60, 300), (WINDOW_WIDTH - 60, 300), 1)

        legend_y = 312
        col_w    = (WINDOW_WIDTH - 120) // len(key_legend)
        for i, (key, action) in enumerate(key_legend):
            kx = 60 + i * col_w
            key_surf   = font_key.render(key, True, ACCENT)
            act_surf   = font_key.render(action, True, DIM_TEXT)
            screen.blit(key_surf,  (kx, legend_y))
            screen.blit(act_surf,  (kx, legend_y + 18))

        # No-tracks warning
        if not player.playlist:
            warn = font_info.render(
                " Add .mp3/.wav files to the music/ folder", True, (255, 180, 60))
            screen.blit(warn, warn.get_rect(centerx=WINDOW_WIDTH // 2, top=360))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
