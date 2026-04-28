"""Snake TSIS-4 – entry point and screen management."""

import sys
import pygame

import config
import db
import game

W = game.W
H = game.H

WHITE = (255, 255, 255)
BLACK = (0,   0,   0)
GOLD  = (255, 185,  0)

SNAKE_COLORS = [
    ([0,   200,   0], "Green"),
    ([0,   100, 255], "Blue"),
    ([255, 165,   0], "Orange"),
    ([220,  20,  60], "Crimson"),
    ([148,   0, 211], "Purple"),
    ([0,   200, 200], "Cyan"),
]


# ════════════════════════════════════════════
#  Helper: dark background with title
# ════════════════════════════════════════════

def _bg(screen):
    screen.fill((10, 10, 30))


# ════════════════════════════════════════════
#  Main Menu – username input
# ════════════════════════════════════════════

def screen_main_menu(screen, clock, fonts):
    """Show title + username input. Returns username, '!leaderboard', or '!settings'."""
    font_large, font_medium, font_small = fonts
    username = ""
    cursor_on = True
    cursor_tick = pygame.time.get_ticks()

    while True:
        now = pygame.time.get_ticks()
        if now - cursor_tick > 500:
            cursor_on  = not cursor_on
            cursor_tick = now

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if username.strip():
                        return username.strip()
                elif event.key == pygame.K_BACKSPACE:
                    username = username[:-1]
                elif event.key == pygame.K_l:
                    return "!leaderboard"
                elif event.key == pygame.K_s:
                    return "!settings"
                elif event.unicode and len(username) < 20:
                    if event.unicode.isprintable() and event.unicode != " " or username:
                        username += event.unicode

        _bg(screen)

        title = font_large.render("SNAKE", True, (0, 220, 0))
        screen.blit(title, title.get_rect(center=(W//2, H//5)))

        sub = font_small.render("Enter your name to play:", True, (180, 180, 180))
        screen.blit(sub, sub.get_rect(center=(W//2, H//2 - 55)))

        # Input box
        bw, bh = 320, 46
        bx, by = W//2 - bw//2, H//2 - bh//2
        pygame.draw.rect(screen, (35, 35, 60), (bx, by, bw, bh), border_radius=7)
        border_clr = (0, 200, 0) if username else (80, 80, 120)
        pygame.draw.rect(screen, border_clr, (bx, by, bw, bh), 2, border_radius=7)
        display = username + ("|" if cursor_on else " ")
        ts = font_medium.render(display, True, WHITE)
        screen.blit(ts, ts.get_rect(center=(W//2, H//2)))

        for i, line in enumerate([
            "ENTER – start",
            "[L] Leaderboard   [S] Settings",
        ]):
            s = font_small.render(line, True, (110, 110, 130))
            screen.blit(s, s.get_rect(center=(W//2, H//2 + 60 + i*32)))

        pygame.display.update()
        clock.tick(30)


# ════════════════════════════════════════════
#  Game Over
# ════════════════════════════════════════════

def screen_game_over(screen, clock, fonts, username, score, level):
    """Returns 'retry', 'menu', or 'quit'."""
    font_large, font_medium, font_small = fonts

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_r, pygame.K_SPACE):
                    return "retry"
                if event.key == pygame.K_m:
                    return "menu"
                if event.key == pygame.K_q:
                    return "quit"

        _bg(screen)

        title = font_large.render("GAME OVER", True, (220, 40, 40))
        screen.blit(title, title.get_rect(center=(W//2, H//5)))

        lines = [
            (f"Player : {username}", GOLD,          font_medium),
            (f"Score  : {score}",    (255,255,255), font_medium),
            (f"Level  : {level}",    (200,200,200), font_medium),
        ]
        for i, (text, clr, fnt) in enumerate(lines):
            s = fnt.render(text, True, clr)
            screen.blit(s, s.get_rect(center=(W//2, H//2 - 30 + i*50)))

        for i, line in enumerate([
            "[R / SPACE] Retry",
            "[M] Main Menu",
            "[Q] Quit",
        ]):
            s = font_small.render(line, True, (120, 120, 140))
            screen.blit(s, s.get_rect(center=(W//2, H*3//4 + i*30)))

        pygame.display.update()
        clock.tick(30)


# ════════════════════════════════════════════
#  Leaderboard
# ════════════════════════════════════════════

def screen_leaderboard(screen, clock, fonts, top10):
    font_large, font_medium, font_small, font_tiny = fonts

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

        hdr = font_small.render(f"{'#':<3}  {'Name':<16}  {'Score':>6}  {'Lv':>2}  {'Date'}", True, (140, 140, 200))
        screen.blit(hdr, (28, 100))
        pygame.draw.line(screen, (60, 60, 110), (28, 124), (W-28, 124), 1)

        rank_colors = [(255,215,0), (192,192,192), (205,127,50)]
        for i, row in enumerate(top10):
            name, score_v, lv, dt = row
            clr = rank_colors[i] if i < 3 else (170, 170, 170)
            line = f"{i+1:<3}  {name[:16]:<16}  {score_v:>6}  {lv:>2}  {dt}"
            s = font_small.render(line, True, clr)
            screen.blit(s, (28, 132 + i*33))

        if not top10:
            s = font_medium.render("No records yet!", True, (80, 80, 100))
            screen.blit(s, s.get_rect(center=(W//2, H//2)))

        back = font_small.render("[ESC / B]  Back", True, (80, 80, 100))
        screen.blit(back, back.get_rect(center=(W//2, H-24)))

        pygame.display.update()
        clock.tick(30)


# ════════════════════════════════════════════
#  Settings
# ════════════════════════════════════════════

def screen_settings(screen, clock, fonts, settings):
    font_large, font_medium, font_small = fonts
    s = dict(settings)

    color_vals  = [c[0] for c in SNAKE_COLORS]
    color_names = [c[1] for c in SNAKE_COLORS]
    cur_ci = next((i for i, cv in enumerate(color_vals) if cv == s["snake_color"]), 0)

    options = ["color", "grid", "sound", "save"]
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
                    if options[sel] == "color":
                        cur_ci = (cur_ci + d) % len(color_vals)
                        s["snake_color"] = color_vals[cur_ci]
                    elif options[sel] == "grid":
                        s["grid"] = not s["grid"]
                    elif options[sel] == "sound":
                        s["sound"] = not s["sound"]
                    elif options[sel] == "save":
                        config.save(s)
                        return s
                elif event.key in (pygame.K_ESCAPE, pygame.K_b):
                    config.save(s)
                    return s

        _bg(screen)

        title = font_large.render("SETTINGS", True, (0, 180, 255))
        screen.blit(title, title.get_rect(center=(W//2, 55)))

        items = [
            ("Snake Color", color_names[cur_ci], tuple(color_vals[cur_ci])),
            ("Grid",  "ON"  if s["grid"]  else "OFF", WHITE),
            ("Sound", "ON"  if s["sound"] else "OFF", WHITE),
            ("Save & Back",  "",                       (0, 220, 0)),
        ]

        for i, (label, val, val_clr) in enumerate(items):
            y   = H//2 - 80 + i*65
            sel_i = (i == sel)
            bg  = (30, 30, 65) if sel_i else (15, 15, 40)
            pygame.draw.rect(screen, bg, (50, y-6, W-100, 48), border_radius=7)
            if sel_i:
                pygame.draw.rect(screen, (0,180,255), (50, y-6, W-100, 48), 2, border_radius=7)
            lbl_s = font_medium.render(label, True, WHITE if sel_i else (160,160,160))
            screen.blit(lbl_s, (70, y+6))
            if val:
                v_s = font_medium.render(val, True, val_clr)
                screen.blit(v_s, (W - 70 - v_s.get_width(), y+6))

        hint = font_small.render("↑↓ Select   ←→/ENTER Change   ESC Save & Exit", True, (70,70,90))
        screen.blit(hint, hint.get_rect(center=(W//2, H-24)))

        pygame.display.update()
        clock.tick(30)


# ════════════════════════════════════════════
#  Entry point
# ════════════════════════════════════════════

def main():
    pygame.init()
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("Snake – TSIS 4")
    clock = pygame.time.Clock()

    font_large  = pygame.font.SysFont("Consolas", 52, bold=True)
    font_medium = pygame.font.SysFont("Consolas", 32, bold=True)
    font_small  = pygame.font.SysFont("Consolas", 20, bold=True)
    font_tiny   = pygame.font.SysFont("Arial",    10, bold=True)
    fonts = (font_large, font_medium, font_small, font_tiny)

    settings = config.load()

    db_ok = False
    try:
        db.init_db()
        db_ok = True
    except Exception as e:
        print(f"[DB] Not available: {e}")

    username  = ""
    player_id = None
    state     = "menu"
    last_score, last_level = 0, 1

    while True:
        if state == "menu":
            result = screen_main_menu(screen, clock, fonts[:3])
            if result == "!leaderboard":
                state = "leaderboard"
            elif result == "!settings":
                state = "settings"
            else:
                username = result
                if db_ok:
                    try:
                        player_id = db.get_or_create_player(username)
                    except Exception:
                        player_id = None
                state = "game"

        elif state == "game":
            last_score, last_level = game.run_game(screen, clock, settings, fonts)
            if db_ok and player_id is not None:
                try:
                    db.save_session(player_id, last_score, last_level)
                except Exception:
                    pass
            state = "gameover"

        elif state == "gameover":
            action = screen_game_over(screen, clock, fonts[:3],
                                      username, last_score, last_level)
            if action == "retry":
                state = "game"
            elif action == "menu":
                state = "menu"
            else:
                pygame.quit()
                sys.exit()

        elif state == "leaderboard":
            top10 = db.get_top10() if db_ok else []
            screen_leaderboard(screen, clock, fonts, top10)
            state = "menu"

        elif state == "settings":
            settings = screen_settings(screen, clock, fonts[:3], settings)
            state = "menu"


if __name__ == "__main__":
    main()
