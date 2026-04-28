"""Core game loop for Snake – TSIS 4."""

import pygame
import sys
import random
import math

import config as cfg

# ── Grid / screen ─────────────────────────────
CELL  = 20
COLS  = 30
ROWS  = 30
HUD_H = 50
W = COLS * CELL        # 600
H = ROWS * CELL + HUD_H  # 650

# ── Colours ───────────────────────────────────
BLACK      = (0,   0,   0)
WHITE      = (255, 255, 255)
DARK_GRAY  = (40,  40,  40)
WALL_CLR   = (80,  80,  80)
GOLD       = (255, 185,  0)
ORANGE     = (255, 140,  0)
RED        = (200,  30,  30)
POISON_C   = (180,   0, 180)
OBSTACLE_C = (120,  60,   0)
OBSTACLE_B = (80,   40,   0)

# ── Directions ────────────────────────────────
UP    = (0,  -1)
DOWN  = (0,   1)
LEFT  = (-1,  0)
RIGHT = (1,   0)

_REVERSE = {UP: DOWN, DOWN: UP, LEFT: RIGHT, RIGHT: LEFT}

# ── Gameplay constants ────────────────────────
BASE_FPS      = 8
FPS_PER_LEVEL = 2
FOODS_PER_LVL = 5
MAX_FOODS     = 3
FOOD_SPAWN_MS = 2000
PU_BOARD_MS   = 7000   # how long a power-up sits on the board
PU_SPAWN_MS   = 8000   # interval between power-up spawns

# ── Food types ────────────────────────────────
FOOD_TYPES = [
    {"name":"Apple",  "colour":(220,40,40),  "ring":(160,20,20),
     "pts":10, "life":8000, "weight":50, "label":"A"},
    {"name":"Cherry", "colour":(200,0,120),  "ring":(140,0,80),
     "pts":25, "life":6000, "weight":35, "label":"C"},
    {"name":"Star",   "colour":(255,210,0),  "ring":(180,140,0),
     "pts":50, "life":4000, "weight":15, "label":"*"},
]
FOOD_WEIGHTS = [ft["weight"] for ft in FOOD_TYPES]

# ── Power-up types ────────────────────────────
POWERUP_TYPES = [
    {"name":"Speed",  "colour":(255,220,0),   "ring":(200,160,0),
     "label":"S", "duration":5000},
    {"name":"Slow",   "colour":(80,180,255),  "ring":(40,120,200),
     "label":"~", "duration":5000},
    {"name":"Shield", "colour":(0,230,100),   "ring":(0,160,70),
     "label":"O", "duration":8000},
]


# ════════════════════════════════════════════
#  Helpers
# ════════════════════════════════════════════

def _rand_pos(exclude: set) -> tuple:
    while True:
        pos = (random.randint(1, COLS-2), random.randint(1, ROWS-2))
        if pos not in exclude:
            return pos


def _spawn_food(snake, foods, obstacles):
    occupied = set(snake) | {f["pos"] for f in foods} | obstacles
    pos   = _rand_pos(occupied)
    ftype = random.choices(FOOD_TYPES, weights=FOOD_WEIGHTS, k=1)[0]
    return {"kind":"normal", "pos":pos, "type":ftype,
            "born":pygame.time.get_ticks()}


def _spawn_poison(snake, foods, obstacles):
    occupied = set(snake) | {f["pos"] for f in foods} | obstacles
    return {"kind":"poison", "pos":_rand_pos(occupied),
            "born":pygame.time.get_ticks(), "life":6000}


def _spawn_board_pu(snake, foods, obstacles):
    occupied = set(snake) | {f["pos"] for f in foods} | obstacles
    ptype = random.choice(POWERUP_TYPES)
    return {"pos":_rand_pos(occupied), "type":ptype,
            "born":pygame.time.get_ticks()}


def _spawn_obstacles(n, snake, foods, obstacles):
    head = snake[0]
    # Don't block cells adjacent to the head
    safe_zone = {(head[0]+dc, head[1]+dr)
                 for dc, dr in [UP, DOWN, LEFT, RIGHT]} | {head}
    occupied = set(snake) | {f["pos"] for f in foods} | obstacles | safe_zone
    result, attempts = set(), 0
    while len(result) < n and attempts < 400:
        pos = (random.randint(1, COLS-2), random.randint(1, ROWS-2))
        if pos not in occupied and pos not in result:
            result.add(pos)
        attempts += 1
    return result


# ════════════════════════════════════════════
#  Drawing helpers
# ════════════════════════════════════════════

def _draw_grid(screen, settings):
    if settings.get("grid", True):
        for c in range(COLS):
            for r in range(ROWS):
                pygame.draw.rect(screen, DARK_GRAY,
                    (c*CELL, HUD_H+r*CELL, CELL, CELL), 1)


def _draw_walls(screen):
    for c in range(COLS):
        pygame.draw.rect(screen, WALL_CLR, (c*CELL, HUD_H, CELL, CELL))
        pygame.draw.rect(screen, WALL_CLR, (c*CELL, HUD_H+(ROWS-1)*CELL, CELL, CELL))
    for r in range(ROWS):
        pygame.draw.rect(screen, WALL_CLR, (0, HUD_H+r*CELL, CELL, CELL))
        pygame.draw.rect(screen, WALL_CLR, ((COLS-1)*CELL, HUD_H+r*CELL, CELL, CELL))


def _draw_snake(screen, body, color):
    head_c = tuple(min(v+60, 255) for v in color)
    for i, (c, r) in enumerate(body):
        clr = head_c if i == 0 else color
        pygame.draw.rect(screen, clr,
            (c*CELL+1, HUD_H+r*CELL+1, CELL-2, CELL-2), border_radius=4)


def _draw_arc_item(screen, pos, color, ring, label, font_tiny, life, born):
    """Draw a food/powerup circle with a shrinking countdown arc."""
    c, r = pos
    cx = c*CELL + CELL//2
    cy = HUD_H + r*CELL + CELL//2
    rad = CELL//2 - 1
    ratio = max(0.0, 1.0 - (pygame.time.get_ticks()-born) / life)
    pygame.draw.circle(screen, ring,  (cx, cy), rad)
    pygame.draw.circle(screen, color, (cx, cy), rad-3)
    lbl = font_tiny.render(label, True, BLACK)
    screen.blit(lbl, lbl.get_rect(center=(cx, cy)))
    if ratio > 0.02:
        arc_rect    = (cx-rad, cy-rad, rad*2, rad*2)
        stop_angle  = math.pi / 2
        start_angle = stop_angle - ratio * 2 * math.pi
        pygame.draw.arc(screen, WHITE, arc_rect, start_angle, stop_angle, 2)


def _draw_foods(screen, foods, font_tiny):
    for food in foods:
        if food["kind"] == "normal":
            ft = food["type"]
            _draw_arc_item(screen, food["pos"], ft["colour"], ft["ring"],
                           ft["label"], font_tiny, ft["life"], food["born"])
        else:
            _draw_arc_item(screen, food["pos"], POISON_C, (120,0,120),
                           "X", font_tiny, food["life"], food["born"])


def _draw_board_pu(screen, pu, font_tiny):
    if not pu:
        return
    pt = pu["type"]
    _draw_arc_item(screen, pu["pos"], pt["colour"], pt["ring"],
                   pt["label"], font_tiny, PU_BOARD_MS, pu["born"])


def _draw_obstacles(screen, obstacles):
    for c, r in obstacles:
        pygame.draw.rect(screen, OBSTACLE_C,
            (c*CELL+1, HUD_H+r*CELL+1, CELL-2, CELL-2), border_radius=2)
        pygame.draw.rect(screen, OBSTACLE_B,
            (c*CELL+1, HUD_H+r*CELL+1, CELL-2, CELL-2), 2, border_radius=2)


def _draw_hud(screen, score, level, fps, active_pu, shield, personal_best, font_small):
    pygame.draw.rect(screen, (20,20,20), (0, 0, W, HUD_H))
    screen.blit(font_small.render(f"Score: {score}", True, WHITE), (10, 14))
    lvl = font_small.render(f"Lv:{level}  {fps}fps", True, GOLD)
    screen.blit(lvl, (W//2 - lvl.get_width()//2, 14))
    pb = font_small.render(f"Best: {personal_best}", True, (180, 180, 100))
    screen.blit(pb, (W - pb.get_width() - 10, 32))

    status = ""
    if shield:
        status = "[SHIELD]"
    elif active_pu and pygame.time.get_ticks() < active_pu["end"]:
        secs = max(0, (active_pu["end"] - pygame.time.get_ticks()) // 1000)
        status = f"[{active_pu['name']} {secs}s]"
    if status:
        st = font_small.render(status, True, ORANGE)
        screen.blit(st, (W - st.get_width() - 10, 14))


def _flash_level(screen, level, font_large):
    overlay = pygame.Surface((W, H), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 110))
    screen.blit(overlay, (0, 0))
    s = font_large.render(f"Level {level}!", True, ORANGE)
    screen.blit(s, s.get_rect(center=(W//2, H//2)))
    pygame.display.update()
    pygame.time.delay(700)


# ════════════════════════════════════════════
#  Main game loop
# ════════════════════════════════════════════

def run_game(screen, clock, settings, fonts, sounds=None, personal_best=0):
    """Run one game session. Returns (score, level)."""
    font_small, font_medium, font_large, font_tiny = fonts
    snake_color  = tuple(settings.get("snake_color", [0, 200, 0]))
    sound_on     = settings.get("sound", True)

    def _play(key):
        if sound_on and sounds and sounds.get(key):
            sounds[key].play()

    snake     = [(COLS//2, ROWS//2),
                 (COLS//2-1, ROWS//2),
                 (COLS//2-2, ROWS//2)]
    direction = RIGHT
    next_dir  = RIGHT

    foods      = [_spawn_food(snake, [], set())]
    food_timer = pygame.time.get_ticks()
    poison_timer = pygame.time.get_ticks() + 12000  # first poison after 12s

    board_pu = None
    pu_timer = pygame.time.get_ticks()

    active_pu = None   # {"name":..., "end":timestamp}
    shield    = False

    obstacles = set()

    score     = 0
    level     = 1
    eaten_cnt = 0

    def base_fps():
        return BASE_FPS + (level - 1) * FPS_PER_LEVEL

    def eff_fps():
        if active_pu and pygame.time.get_ticks() < active_pu["end"]:
            if active_pu["name"] == "Speed":
                return base_fps() + 4
            if active_pu["name"] == "Slow":
                return max(2, base_fps() - 3)
        return base_fps()

    while True:
        # ── Events ──────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if   event.key == pygame.K_UP    and direction != DOWN:  next_dir = UP
                elif event.key == pygame.K_DOWN  and direction != UP:    next_dir = DOWN
                elif event.key == pygame.K_LEFT  and direction != RIGHT: next_dir = LEFT
                elif event.key == pygame.K_RIGHT and direction != LEFT:  next_dir = RIGHT
                elif event.key == pygame.K_ESCAPE:
                    return score, level

        direction = next_dir
        dc, dr = direction
        head = (snake[0][0]+dc, snake[0][1]+dr)
        now  = pygame.time.get_ticks()

        # Expire active power-up
        if active_pu and now >= active_pu["end"]:
            active_pu = None

        # ── Collision detection ─────────────────
        hit = (head[0] <= 0 or head[0] >= COLS-1 or
               head[1] <= 0 or head[1] >= ROWS-1 or
               head in obstacles or
               head in snake[:-1])

        if hit:
            if shield:
                shield    = False
                active_pu = None
                next_dir  = _REVERSE[direction]
                _play("poison")
            else:
                _play("die")
                return score, level
        else:
            snake.insert(0, head)

            # ── Food collection ─────────────────
            eaten = next((f for f in foods if f["pos"] == head), None)
            if eaten:
                if eaten["kind"] == "normal":
                    score     += eaten["type"]["pts"]
                    eaten_cnt += 1
                    _play("eat")
                    foods.remove(eaten)
                    if eaten_cnt >= FOODS_PER_LVL:
                        level     += 1
                        eaten_cnt  = 0
                        _play("levelup")
                        if level >= 3:
                            new_obs = _spawn_obstacles((level-2)*2, snake, foods, obstacles)
                            obstacles |= new_obs
                        _flash_level(screen, level, font_large)
                else:  # poison
                    _play("poison")
                    foods.remove(eaten)
                    for _ in range(2):
                        if len(snake) > 1:
                            snake.pop()
                        else:
                            _play("die")
                            return score, level
            else:
                snake.pop()

            # ── Power-up collection ─────────────
            if board_pu and board_pu["pos"] == head:
                pt = board_pu["type"]
                if pt["name"] == "Shield":
                    shield    = True
                    active_pu = None
                else:
                    shield    = False
                    active_pu = {"name": pt["name"],
                                 "end":  now + pt["duration"]}
                board_pu = None

        # ── Expire foods ─────────────────────────
        foods = [f for f in foods
                 if now - f["born"] < (f["type"]["life"] if f["kind"]=="normal"
                                       else f["life"])]

        # ── Spawn regular food ───────────────────
        if len(foods) < MAX_FOODS and now - food_timer > FOOD_SPAWN_MS:
            foods.append(_spawn_food(snake, foods, obstacles))
            food_timer = now

        # ── Spawn poison food ────────────────────
        if now >= poison_timer:
            if not any(f["kind"] == "poison" for f in foods):
                foods.append(_spawn_poison(snake, foods, obstacles))
            poison_timer = now + random.randint(14000, 22000)

        # ── Power-up on board ────────────────────
        if board_pu is None and now - pu_timer > PU_SPAWN_MS:
            board_pu = _spawn_board_pu(snake, foods, obstacles)
            pu_timer = now
        if board_pu and now - board_pu["born"] > PU_BOARD_MS:
            board_pu = None
            pu_timer = now

        # ── Draw ─────────────────────────────────
        screen.fill(BLACK)
        _draw_grid(screen, settings)
        _draw_walls(screen)
        _draw_obstacles(screen, obstacles)
        _draw_foods(screen, foods, font_tiny)
        _draw_board_pu(screen, board_pu, font_tiny)
        _draw_snake(screen, snake, snake_color)
        _draw_hud(screen, score, level, eff_fps(), active_pu, shield, personal_best, font_small)
        pygame.display.update()
        clock.tick(eff_fps())
