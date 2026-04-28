"""Racer game logic – TSIS 3."""

import pygame
import sys
import random

W, H = 480, 640

BLACK  = (0,   0,   0)
WHITE  = (255, 255, 255)
GRAY   = (80,  80,  80)
ROAD_C = (50,  50,  50)
LANE_C = (220, 220,  0)
DARK   = (20,  20,  40)
GOLD   = (255, 185,  0)
RED    = (220,  40,  40)
ORANGE = (255, 140,   0)
GREEN  = (0,   210,  80)
CYAN   = (0,   200, 220)

ROAD_LEFT  = 80
ROAD_RIGHT = W - 80
ROAD_W     = ROAD_RIGHT - ROAD_LEFT    # 320
LANE_W     = ROAD_W // 4               # 4 lanes, each 80px wide
HUD_H      = 0                         # minimum Y for player (top of road)

LANE_CENTERS = [ROAD_LEFT + LANE_W * i + LANE_W // 2 for i in range(4)]

PLAYER_W, PLAYER_H = 36, 64
ENEMY_W,  ENEMY_H  = 36, 64
HAZARD_W, HAZARD_H = 30, 30
PU_W,     PU_H     = 32, 32

POWERUP_TYPES = [
    {"name": "Nitro",  "color": (255, 220, 0),  "label": "N", "duration": 4000},
    {"name": "Shield", "color": (0,   220, 120), "label": "S", "duration": 6000},
    {"name": "Repair", "color": (80,  160, 255), "label": "R", "duration": 0},
]

DIFF_PARAMS = {
    "Easy":   {"enemy_speed": 3, "spawn_rate": 90, "hazard_rate": 120},
    "Normal": {"enemy_speed": 5, "spawn_rate": 60, "hazard_rate": 80},
    "Hard":   {"enemy_speed": 8, "spawn_rate": 35, "hazard_rate": 50},
}

ENEMY_COLORS = [
    (200, 80,  80),
    (80,  80,  200),
    (80,  180, 80),
    (200, 200, 80),
    (180, 80,  180),
]


# ════════════════════════════════════════════
#  Drawing helpers
# ════════════════════════════════════════════

def _draw_road(screen, road_offset):
    pygame.draw.rect(screen, ROAD_C, (ROAD_LEFT, 0, ROAD_W, H))
    # Moving lane dashes
    dash_h, gap = 40, 40
    period = dash_h + gap
    for lane in range(1, 4):
        lx = ROAD_LEFT + lane * LANE_W
        for y_base in range(-period, H + period, period):
            y = (y_base + road_offset) % (H + period) - period
            pygame.draw.rect(screen, LANE_C, (lx - 2, y, 4, dash_h))


def _draw_car(screen, cx, cy, w, h, color, is_player=False):
    rx, ry = cx - w//2, cy - h//2
    pygame.draw.rect(screen, color, (rx, ry, w, h), border_radius=6)
    # Windshield
    ww = int(w * 0.55)
    wh = int(h * 0.22)
    wx = cx - ww//2
    pygame.draw.rect(screen, (180, 220, 255),
                     (wx, ry + (4 if not is_player else h - wh - 6), ww, wh),
                     border_radius=3)
    # Wheels
    wheel_c = (30, 30, 30)
    wsize = 8
    for ox, oy in [(-w//2-1, -h//4), (w//2-wsize+1, -h//4),
                   (-w//2-1, h//4),  (w//2-wsize+1, h//4)]:
        pygame.draw.rect(screen, wheel_c, (rx+ox+w//2, ry+oy+h//2, wsize, 14), border_radius=2)


def _draw_hazard(screen, x, y):
    cx, cy = x + HAZARD_W//2, y + HAZARD_H//2
    pygame.draw.circle(screen, (200, 60, 20), (cx, cy), HAZARD_W//2)
    pygame.draw.circle(screen, (255, 120, 60), (cx, cy), HAZARD_W//2 - 4)
    # X mark
    pygame.draw.line(screen, WHITE, (cx-7, cy-7), (cx+7, cy+7), 3)
    pygame.draw.line(screen, WHITE, (cx+7, cy-7), (cx-7, cy+7), 3)


def _draw_powerup(screen, pu, font_small):
    x, y = pu["x"] + ROAD_LEFT, pu["y"]
    cx   = x + PU_W//2
    cy   = y + PU_H//2
    clr  = pu["ptype"]["color"]
    pygame.draw.circle(screen, clr, (cx, cy), PU_W//2)
    pygame.draw.circle(screen, WHITE, (cx, cy), PU_W//2, 2)
    lbl  = font_small.render(pu["ptype"]["label"], True, BLACK)
    screen.blit(lbl, lbl.get_rect(center=(cx, cy)))


def _draw_hud(screen, score, distance, active_pu, shield_on, coins, level, font_small):
    pygame.draw.rect(screen, (15, 15, 35), (0, 0, ROAD_LEFT, H))
    pygame.draw.rect(screen, (15, 15, 35), (ROAD_RIGHT, 0, W-ROAD_RIGHT, H))

    def _vtext(texts, x, start_y):
        for i, (text, clr) in enumerate(texts):
            s = font_small.render(text, True, clr)
            screen.blit(s, s.get_rect(center=(x, start_y + i*26)))

    _vtext([
        ("SCORE", (140,140,180)),
        (str(score), GOLD),
        ("", BLACK),
        ("DIST", (140,140,180)),
        (f"{distance}m", WHITE),
        ("", BLACK),
        ("COINS", (140,140,180)),
        (str(coins), (255,215,0)),
        ("", BLACK),
        ("LEVEL", (140,140,180)),
        (str(level), CYAN),
    ], ROAD_LEFT//2, 40)

    status_lines = []
    if shield_on:
        status_lines.append(("SHIELD", GREEN))
    elif active_pu:
        rem = max(0, (active_pu["end"] - pygame.time.get_ticks()) // 1000)
        status_lines.append((active_pu["name"], ORANGE))
        status_lines.append((f"{rem}s", WHITE))

    if status_lines:
        _vtext(status_lines, ROAD_RIGHT + (W-ROAD_RIGHT)//2, H//2)


def _draw_shield_effect(screen, px, py):
    cx = ROAD_LEFT + px + PLAYER_W//2
    cy = py + PLAYER_H//2
    pygame.draw.circle(screen, (0, 200, 100, 80), (cx, cy),
                       max(PLAYER_W, PLAYER_H)//2 + 10, 3)


# ════════════════════════════════════════════
#  Main game function
# ════════════════════════════════════════════

def run_game(screen, clock, settings, fonts, sounds=None):
    """Run one game session. Returns (score, distance, coins)."""
    font_small, font_medium, font_large = fonts
    car_color  = tuple(settings.get("car_color",  [220, 60, 60]))
    difficulty = settings.get("difficulty", "Normal")
    sound_on   = settings.get("sound", True)

    def _play(key):
        if sound_on and sounds and sounds.get(key):
            sounds[key].play()
    params     = DIFF_PARAMS[difficulty]

    # Player: x is relative to ROAD_LEFT, y is absolute
    px = ROAD_W//2 - PLAYER_W//2
    py = H - PLAYER_H - 20
    player_speed = 5

    road_offset = 0
    road_speed  = params["enemy_speed"]

    enemies  = []
    hazards  = []
    powerups = []

    active_pu  = None   # {"name":..., "end":...}
    shield_on  = False

    score    = 0
    distance = 0
    coins    = 0
    dist_acc = 0.0

    level          = 1
    level_up_until = 0   # timestamp until level-up banner is shown
    LEVEL_DIST     = 200  # metres per level

    enemy_timer  = 0
    hazard_timer = 0
    pu_timer     = 0
    PU_SPAWN     = 300

    frame = 0

    while True:
        frame += 1
        now = pygame.time.get_ticks()

        # ── Events ──────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return score, distance, coins

        keys = pygame.key.get_pressed()
        if (keys[pygame.K_LEFT] or keys[pygame.K_a])  and px > 0:
            px -= player_speed
        if (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and px < ROAD_W - PLAYER_W:
            px += player_speed
        if (keys[pygame.K_UP] or keys[pygame.K_w])    and py > HUD_H:
            py -= player_speed
        if (keys[pygame.K_DOWN] or keys[pygame.K_s])  and py < H - PLAYER_H:
            py += player_speed

        # Clamp player to road
        px = max(0, min(px, ROAD_W - PLAYER_W))

        # Expire power-up
        if active_pu and now >= active_pu["end"]:
            active_pu = None
            road_speed = params["enemy_speed"]  # restore after Nitro

        # ── Scrolling ────────────────────────────
        road_offset = (road_offset + road_speed) % (H + 80)
        dist_acc   += road_speed * 0.02
        distance    = int(dist_acc)

        # Score from distance + time bonus
        score = distance + coins * 10

        # ── Level progression ─────────────────────
        new_level = distance // LEVEL_DIST + 1
        if new_level > level:
            level          = new_level
            level_up_until = now + 2000
            road_speed     = params["enemy_speed"] + level - 1

        # ── Spawn enemies ─────────────────────────
        enemy_timer += 1
        # Scaling: more frequent as distance increases
        spawn_rate = max(20, params["spawn_rate"] - distance // 100)
        if enemy_timer >= spawn_rate:
            enemy_timer = 0
            lane = random.randint(0, 3)
            ex   = LANE_CENTERS[lane] - ROAD_LEFT - ENEMY_W//2
            # Don't spawn on top of existing enemies
            blocked = any(abs(e["x"] - ex) < ENEMY_W and e["y"] < ENEMY_H*2
                          for e in enemies)
            if not blocked:
                enemies.append({
                    "x": ex, "y": -ENEMY_H,
                    "speed": params["enemy_speed"] + random.randint(0, 2),
                    "color": random.choice(ENEMY_COLORS),
                })

        # ── Spawn hazards ─────────────────────────
        hazard_timer += 1
        if hazard_timer >= params["hazard_rate"]:
            hazard_timer = 0
            lane = random.randint(0, 3)
            hx   = LANE_CENTERS[lane] - ROAD_LEFT - HAZARD_W//2
            hazards.append({"x": hx, "y": -HAZARD_H})

        # ── Spawn power-up ────────────────────────
        pu_timer += 1
        if pu_timer >= PU_SPAWN and not powerups:
            pu_timer = 0
            lane  = random.randint(0, 3)
            pux   = LANE_CENTERS[lane] - ROAD_LEFT - PU_W//2
            ptype = random.choice(POWERUP_TYPES)
            powerups.append({"x": pux, "y": -PU_H, "ptype": ptype,
                             "expires": now + 8000})

        # Powerups disappear after timeout even if not collected
        powerups = [pu for pu in powerups
                    if pu["y"] < H + PU_H and now < pu["expires"]]

        # ── Move objects ──────────────────────────
        for e in enemies:
            e["y"] += road_speed + e["speed"] // 2
        for hz in hazards:
            hz["y"] += road_speed
        for pu in powerups:
            pu["y"] += road_speed

        enemies  = [e  for e  in enemies  if e["y"]  < H + ENEMY_H]
        hazards  = [hz for hz in hazards  if hz["y"] < H + HAZARD_H]

        # ── Collision helpers ─────────────────────
        pr = pygame.Rect(ROAD_LEFT + px, py, PLAYER_W, PLAYER_H)

        def _hit(ox, oy, ow, oh):
            return pr.colliderect(pygame.Rect(ROAD_LEFT + ox, oy, ow, oh))

        # ── Enemy collisions ──────────────────────
        for e in enemies[:]:
            if _hit(e["x"], e["y"], ENEMY_W, ENEMY_H):
                if shield_on:
                    shield_on = False
                    active_pu = None
                    enemies.remove(e)
                else:
                    _play("die")
                    return score, distance, coins

        # ── Hazard collisions ─────────────────────
        for hz in hazards[:]:
            if _hit(hz["x"], hz["y"], HAZARD_W, HAZARD_H):
                if shield_on:
                    shield_on = False
                    active_pu = None
                    hazards.remove(hz)
                else:
                    _play("die")
                    return score, distance, coins

        # ── Power-up collection ───────────────────
        for pu in powerups[:]:
            if _hit(pu["x"], pu["y"], PU_W, PU_H):
                powerups.remove(pu)
                name = pu["ptype"]["name"]
                coins += 1
                if name == "Nitro":
                    shield_on = False
                    active_pu = {"name": "Nitro",
                                 "end":  now + pu["ptype"]["duration"]}
                    road_speed = int(params["enemy_speed"] * 1.8)
                elif name == "Shield":
                    shield_on = True
                    active_pu = {"name": "Shield",
                                 "end":  now + pu["ptype"]["duration"]}
                elif name == "Repair":
                    # Clear all hazards visible on screen
                    hazards.clear()
                    active_pu = None

        # ── Draw ──────────────────────────────────
        screen.fill(BLACK)
        _draw_road(screen, road_offset)

        for e in enemies:
            _draw_car(screen, ROAD_LEFT + e["x"] + ENEMY_W//2,
                      e["y"] + ENEMY_H//2, ENEMY_W, ENEMY_H, e["color"])
        for hz in hazards:
            _draw_hazard(screen, ROAD_LEFT + hz["x"], hz["y"])
        for pu in powerups:
            _draw_powerup(screen, pu, font_small)

        _draw_car(screen, ROAD_LEFT + px + PLAYER_W//2,
                  py + PLAYER_H//2, PLAYER_W, PLAYER_H, car_color, is_player=True)
        if shield_on:
            _draw_shield_effect(screen, px, py)

        _draw_hud(screen, score, distance, active_pu, shield_on, coins, level, font_small)

        # Level-up banner
        if now < level_up_until:
            banner = font_medium.render(f"LEVEL {level}!", True, CYAN)
            bx = W // 2 - banner.get_width() // 2
            by = H // 2 - banner.get_height() // 2
            pygame.draw.rect(screen, (10, 10, 40),
                             (bx - 12, by - 8, banner.get_width() + 24, banner.get_height() + 16),
                             border_radius=8)
            screen.blit(banner, (bx, by))
        pygame.display.update()
        clock.tick(60)
