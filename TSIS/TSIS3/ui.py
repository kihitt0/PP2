"""All non-gameplay screens for the Racer game."""

import sys
import pygame

import persistence as ps

W, H = 480, 640
WHITE  = (255, 255, 255)
BLACK  = (0,   0,   0)
GRAY   = (160, 160, 160)
DARK   = (20,  20,  40)
GOLD   = (255, 185,   0)
RED    = (220,  40,  40)
GREEN  = (0,   200,  80)
BLUE   = (0,   140, 255)

DIFFICULTIES = ["Easy", "Normal", "Hard"]

CAR_COLORS = [
    ([220, 60,  60],  "Red"),
    ([60,  120, 220], "Blue"),
    ([60,  200,  60], "Green"),
    ([220, 180,  20], "Yellow"),
    ([160,  60, 220], "Purple"),
    ([220, 140,  20], "Orange"),
]


def _bg(screen):
    screen.fill(DARK)


def _btn(screen, font, text, cx, cy, w=260, h=48, active=False):
    rx, ry = cx - w//2, cy - h//2
    clr  = (40, 40, 80) if not active else (50, 50, 110)
    bclr = BLUE if active else (70, 70, 120)
    pygame.draw.rect(screen, clr,  (rx, ry, w, h), border_radius=8)
    pygame.draw.rect(screen, bclr, (rx, ry, w, h), 2, border_radius=8)
    s = font.render(text, True, WHITE if active else GRAY)
    screen.blit(s, s.get_rect(center=(cx, cy)))


# ════════════════════════════════════════════
#  Main Menu
# ════════════════════════════════════════════

def main_menu(screen, clock, fonts):
    """Returns 'play', 'leaderboard', 'settings', or 'quit'."""
    font_large, font_medium, font_small = fonts
    options = ["Play", "Leaderboard", "Settings", "Quit"]
    sel = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    sel = (sel - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    sel = (sel + 1) % len(options)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    return options[sel].lower()
                elif event.key == pygame.K_ESCAPE:
                    return "quit"

        _bg(screen)

        title = font_large.render("RACER", True, (255, 80, 80))
        screen.blit(title, title.get_rect(center=(W//2, H//5)))

        sub = font_small.render("Arrow keys / WASD to drive", True, (100,100,130))
        screen.blit(sub, sub.get_rect(center=(W//2, H//5 + 58)))

        for i, opt in enumerate(options):
            _btn(screen, font_medium, opt,
                 W//2, H//2 - 20 + i*65, active=(i==sel))

        pygame.display.update()
        clock.tick(30)


# ════════════════════════════════════════════
#  Settings
# ════════════════════════════════════════════

def settings_screen(screen, clock, fonts, settings):
    """Edit and return updated settings dict."""
    font_large, font_medium, font_small = fonts
    s = dict(settings)

    cv  = [c[0] for c in CAR_COLORS]
    cn  = [c[1] for c in CAR_COLORS]
    ci  = next((i for i, v in enumerate(cv) if v == s["car_color"]), 0)
    di  = DIFFICULTIES.index(s.get("difficulty", "Normal"))

    options = ["car_color", "difficulty", "sound", "save"]
    sel = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    sel = (sel - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    sel = (sel + 1) % len(options)
                elif event.key in (pygame.K_LEFT, pygame.K_RIGHT,
                                   pygame.K_RETURN, pygame.K_SPACE):
                    d = -1 if event.key == pygame.K_LEFT else 1
                    if options[sel] == "car_color":
                        ci = (ci + d) % len(cv)
                        s["car_color"] = cv[ci]
                    elif options[sel] == "difficulty":
                        di = (di + d) % len(DIFFICULTIES)
                        s["difficulty"] = DIFFICULTIES[di]
                    elif options[sel] == "sound":
                        s["sound"] = not s["sound"]
                    elif options[sel] == "save":
                        ps.save_settings(s)
                        return s
                elif event.key in (pygame.K_ESCAPE, pygame.K_b):
                    ps.save_settings(s)
                    return s

        _bg(screen)
        title = font_large.render("SETTINGS", True, BLUE)
        screen.blit(title, title.get_rect(center=(W//2, 55)))

        rows = [
            ("Car Color",   cn[ci],                    tuple(cv[ci])),
            ("Difficulty",  DIFFICULTIES[di],           GOLD),
            ("Sound",       "ON" if s["sound"] else "OFF", WHITE),
            ("Save & Back", "",                         GREEN),
        ]
        for i, (label, val, vclr) in enumerate(rows):
            y   = H//2 - 80 + i*68
            act = (i == sel)
            bg  = (35, 35, 75) if act else (18, 18, 45)
            pygame.draw.rect(screen, bg, (40, y-6, W-80, 50), border_radius=7)
            if act:
                pygame.draw.rect(screen, BLUE, (40, y-6, W-80, 50), 2, border_radius=7)
            ls = font_medium.render(label, True, WHITE if act else GRAY)
            screen.blit(ls, (58, y+7))
            if val:
                vs = font_medium.render(val, True, vclr)
                screen.blit(vs, (W - 55 - vs.get_width(), y+7))

        hint = font_small.render("↑↓ Select   ←→/ENTER Change   ESC Save", True, (70,70,90))
        screen.blit(hint, hint.get_rect(center=(W//2, H-22)))
        pygame.display.update()
        clock.tick(30)


# ════════════════════════════════════════════
#  Game Over
# ════════════════════════════════════════════

def game_over_screen(screen, clock, fonts, score, distance):
    """Returns 'retry' or 'menu'."""
    font_large, font_medium, font_small = fonts

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_r, pygame.K_SPACE):
                    return "retry"
                if event.key in (pygame.K_m, pygame.K_ESCAPE):
                    return "menu"

        _bg(screen)
        title = font_large.render("GAME OVER", True, RED)
        screen.blit(title, title.get_rect(center=(W//2, H//5)))

        for i, (text, clr) in enumerate([
            (f"Score    : {score}", GOLD),
            (f"Distance : {distance} m", WHITE),
        ]):
            s = font_medium.render(text, True, clr)
            screen.blit(s, s.get_rect(center=(W//2, H//2 - 20 + i*55)))

        for i, line in enumerate([
            "[R / SPACE]  Retry",
            "[M / ESC]    Main Menu",
        ]):
            s = font_small.render(line, True, (110, 110, 130))
            screen.blit(s, s.get_rect(center=(W//2, H*3//4 + i*34)))

        pygame.display.update()
        clock.tick(30)


# ════════════════════════════════════════════
#  Leaderboard
# ════════════════════════════════════════════

def leaderboard_screen(screen, clock, fonts):
    font_large, font_medium, font_small = fonts
    lb = ps.load_leaderboard()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_b):
                    return

        _bg(screen)
        title = font_large.render("TOP  10", True, GOLD)
        screen.blit(title, title.get_rect(center=(W//2, 48)))

        hdr = font_small.render(f"{'#':<3}  {'Name':<14}  {'Score':>6}  {'Dist':>5}", True, (140,140,200))
        screen.blit(hdr, (28, 100))
        pygame.draw.line(screen, (60,60,110), (28, 122), (W-28, 122), 1)

        rank_clr = [(255,215,0),(192,192,192),(205,127,50)]
        for i, entry in enumerate(lb):
            clr  = rank_clr[i] if i < 3 else (170,170,170)
            line = f"{i+1:<3}  {entry['name'][:14]:<14}  {entry['score']:>6}  {entry['distance']:>4}m"
            s = font_small.render(line, True, clr)
            screen.blit(s, (28, 130 + i*34))

        if not lb:
            s = font_medium.render("No records yet!", True, (80,80,100))
            screen.blit(s, s.get_rect(center=(W//2, H//2)))

        back = font_small.render("[ESC / B]  Back", True, (80,80,100))
        screen.blit(back, back.get_rect(center=(W//2, H-22)))
        pygame.display.update()
        clock.tick(30)
