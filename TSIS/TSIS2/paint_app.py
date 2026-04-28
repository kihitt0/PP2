"""
Paint Application – TSIS 2
Extends Practice 11 with:
  1. Straight-line tool with live drag preview
  2. Flood-fill (bucket) using pixel-level get_at / set_at
  3. Text tool – click to place, type, Enter to commit, Escape to cancel
  4. Ctrl+S saves the canvas as a timestamped PNG file
All brush sizes apply to every drawing tool.
"""

import pygame
import sys
import math
import datetime

pygame.init()

# ─────────────────────────────────────────────
# SCREEN DIMENSIONS
# ─────────────────────────────────────────────
CANVAS_W  = 900
CANVAS_H  = 600
TOOLBAR_H = 115
SCREEN_W  = CANVAS_W
SCREEN_H  = CANVAS_H + TOOLBAR_H

screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Paint – TSIS 2")

# ─────────────────────────────────────────────
# COLOURS
# ─────────────────────────────────────────────
WHITE             = (255, 255, 255)
BLACK             = (0,   0,   0)
TOOLBAR_BG        = (45,  45,  45)
SWATCH_BORDER_SEL = (255, 255,   0)
SWATCH_BORDER_NRM = (200, 200, 200)

PALETTE = [
    (0,   0,   0),   (255, 255, 255), (220, 30,  30),
    (30,  180, 30),  (30,  80,  220), (255, 200,   0),
    (255, 130,  0),  (180, 0,   180), (0,   200, 200),
    (180, 100,  50), (255, 150, 180), (100, 100, 100),
]

# ─────────────────────────────────────────────
# TOOL IDENTIFIERS
# ─────────────────────────────────────────────
TOOL_PENCIL  = "pencil"
TOOL_LINE    = "line"       # new: straight line with preview
TOOL_RECT    = "rectangle"
TOOL_CIRCLE  = "circle"
TOOL_ERASER  = "eraser"
TOOL_FILL    = "fill"       # new: flood fill
TOOL_TEXT    = "text"       # new: click-to-place text
TOOL_SQUARE  = "square"
TOOL_RTRI    = "r-tri"
TOOL_ETRI    = "eq-tri"
TOOL_RHOMBUS = "rhombus"

TOOLS = [
    TOOL_PENCIL, TOOL_LINE,    TOOL_RECT,   TOOL_CIRCLE,
    TOOL_ERASER, TOOL_FILL,    TOOL_TEXT,   TOOL_SQUARE,
    TOOL_RTRI,   TOOL_ETRI,    TOOL_RHOMBUS,
]

SHAPE_TOOLS = {
    TOOL_RECT, TOOL_CIRCLE, TOOL_LINE,
    TOOL_SQUARE, TOOL_RTRI, TOOL_ETRI, TOOL_RHOMBUS,
}

TOOL_LABELS = {
    TOOL_PENCIL:  "Pencil",
    TOOL_LINE:    "Line",
    TOOL_RECT:    "Rect",
    TOOL_CIRCLE:  "Circle",
    TOOL_ERASER:  "Eraser",
    TOOL_FILL:    "Fill",
    TOOL_TEXT:    "Text",
    TOOL_SQUARE:  "Square",
    TOOL_RTRI:    "R-Tri",
    TOOL_ETRI:    "Eq-Tri",
    TOOL_RHOMBUS: "Rhombus",
}

# ─────────────────────────────────────────────
# FONTS
# ─────────────────────────────────────────────
font_btn  = pygame.font.SysFont("Arial",    13, bold=True)
font_text = pygame.font.SysFont("Arial",    22)      # text tool preview + commit
font_info = pygame.font.SysFont("Consolas", 13)

# ─────────────────────────────────────────────
# TOOLBAR LAYOUT
# ─────────────────────────────────────────────
TOOL_BTN_W   = 76
TOOL_BTN_H   = 46
TOOL_BTN_GAP = 4
TOOL_ROW_Y   = 4

tool_buttons: dict[str, pygame.Rect] = {}
bx = 6
for t in TOOLS:
    tool_buttons[t] = pygame.Rect(bx, TOOL_ROW_Y, TOOL_BTN_W, TOOL_BTN_H)
    bx += TOOL_BTN_W + TOOL_BTN_GAP

SWATCH_SIZE  = 26
SWATCH_GAP   = 4
SWATCH_ROW_Y = 62

swatches: list[tuple[pygame.Rect, tuple]] = []
sx = 6
for colour in PALETTE:
    swatches.append((pygame.Rect(sx, SWATCH_ROW_Y, SWATCH_SIZE, SWATCH_SIZE), colour))
    sx += SWATCH_SIZE + SWATCH_GAP

BRUSH_SIZES = [2, 5, 10]
brush_buttons: list[tuple[pygame.Rect, int]] = []
bsx = sx + 12
for bs in BRUSH_SIZES:
    brush_buttons.append((pygame.Rect(bsx, SWATCH_ROW_Y, 36, SWATCH_SIZE), bs))
    bsx += 40

FILL_BTN_W = 50
fill_btn = pygame.Rect(bsx + 8, SWATCH_ROW_Y, FILL_BTN_W, SWATCH_SIZE)

# ─────────────────────────────────────────────
# CANVAS
# ─────────────────────────────────────────────
canvas = pygame.Surface((CANVAS_W, CANVAS_H))
canvas.fill(WHITE)


# ══════════════════════════════════════════════
#  GEOMETRY HELPERS  (same as Practice 11)
# ══════════════════════════════════════════════

def get_polygon_points(tool: str, p1: tuple, p2: tuple) -> list:
    x1, y1 = p1
    x2, y2 = p2

    if tool == TOOL_SQUARE:
        side = min(abs(x2-x1), abs(y2-y1))
        ox = 0 if x2 >= x1 else -side
        oy = 0 if y2 >= y1 else -side
        return [(x1+ox, y1+oy), (x1+ox+side, y1+oy),
                (x1+ox+side, y1+oy+side), (x1+ox, y1+oy+side)]

    elif tool == TOOL_RTRI:
        return [(x1, y1), (x2, y2), (x1, y2)]

    elif tool == TOOL_ETRI:
        bx1, bx2 = min(x1, x2), max(x1, x2)
        base = bx2 - bx1
        if base == 0:
            return []
        height   = int(base * math.sqrt(3) / 2)
        bottom_y = max(y1, y2)
        return [(bx1, bottom_y), (bx2, bottom_y),
                ((bx1+bx2)//2, bottom_y-height)]

    elif tool == TOOL_RHOMBUS:
        x, y = min(x1, x2), min(y1, y2)
        w, h = abs(x2-x1), abs(y2-y1)
        return [(x+w//2, y), (x+w, y+h//2),
                (x+w//2, y+h), (x, y+h//2)]
    return []


# ══════════════════════════════════════════════
#  FLOOD FILL
# ══════════════════════════════════════════════

def flood_fill(surface: pygame.Surface, x: int, y: int, fill_color: tuple):
    """BFS flood fill on `surface` starting at (x, y)."""
    if not (0 <= x < surface.get_width() and 0 <= y < surface.get_height()):
        return
    target = surface.get_at((x, y))[:3]   # ignore alpha
    fill_c = fill_color[:3]
    if target == fill_c:
        return

    # Use a pixel array for fast bulk writes
    arr = pygame.PixelArray(surface)
    mapped = surface.map_rgb(*fill_c)

    stack = [(x, y)]
    visited = set()
    w, h = surface.get_width(), surface.get_height()

    while stack:
        cx, cy = stack.pop()
        if (cx, cy) in visited:
            continue
        if not (0 <= cx < w and 0 <= cy < h):
            continue
        # Compare via PixelArray value → unmap to RGB
        raw = arr[cx, cy]
        cur = surface.unmap_rgb(raw)[:3]
        if cur != target:
            continue
        visited.add((cx, cy))
        arr[cx, cy] = mapped
        stack.extend([(cx+1, cy), (cx-1, cy), (cx, cy+1), (cx, cy-1)])

    del arr   # unlock surface


# ══════════════════════════════════════════════
#  CANVAS SAVE
# ══════════════════════════════════════════════

def save_canvas():
    ts  = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    fn  = f"canvas_{ts}.png"
    pygame.image.save(canvas, fn)
    return fn


# ══════════════════════════════════════════════
#  DRAWING HELPERS
# ══════════════════════════════════════════════

def canvas_pos(sx: int, sy: int) -> tuple:
    return (sx, sy - TOOLBAR_H)


def draw_toolbar(active_tool, active_colour, active_brush, fill_shapes):
    pygame.draw.rect(screen, TOOLBAR_BG, (0, 0, SCREEN_W, TOOLBAR_H))

    for name, rect in tool_buttons.items():
        bg = (90, 90, 200) if name == active_tool else (65, 65, 65)
        pygame.draw.rect(screen, bg, rect, border_radius=5)
        pygame.draw.rect(screen, WHITE, rect, 1, border_radius=5)
        lbl = font_btn.render(TOOL_LABELS[name], True, WHITE)
        screen.blit(lbl, lbl.get_rect(center=rect.center))

    for rect, colour in swatches:
        pygame.draw.rect(screen, colour, rect)
        border = SWATCH_BORDER_SEL if colour == active_colour else SWATCH_BORDER_NRM
        pygame.draw.rect(screen, border, rect, 2)

    for rect, size in brush_buttons:
        bg = (90, 90, 200) if size == active_brush else (65, 65, 65)
        pygame.draw.rect(screen, bg, rect, border_radius=4)
        pygame.draw.rect(screen, WHITE, rect, 1, border_radius=4)
        pygame.draw.circle(screen, WHITE, rect.center, min(size, 10))

    fb_bg = (50, 140, 60) if fill_shapes else (140, 50, 50)
    pygame.draw.rect(screen, fb_bg, fill_btn, border_radius=5)
    pygame.draw.rect(screen, WHITE, fill_btn, 1, border_radius=5)
    fl = font_btn.render("Fill" if fill_shapes else "Line", True, WHITE)
    screen.blit(fl, fl.get_rect(center=fill_btn.center))


def draw_preview(surface, tool, colour, brush, p1, p2):
    """Ghost outline preview in screen coordinates."""
    if tool == TOOL_LINE:
        if p1 != p2:
            pygame.draw.line(surface, colour, p1, p2, brush)
    elif tool == TOOL_RECT:
        x, y = min(p1[0], p2[0]), min(p1[1], p2[1])
        w, h = abs(p2[0]-p1[0]), abs(p2[1]-p1[1])
        if w and h:
            pygame.draw.rect(surface, colour, (x, y, w, h), brush)
    elif tool == TOOL_CIRCLE:
        cx = (p1[0]+p2[0])//2
        cy = (p1[1]+p2[1])//2
        r  = int(math.hypot(p2[0]-p1[0], p2[1]-p1[1]) / 2)
        if r:
            pygame.draw.circle(surface, colour, (cx, cy), r, brush)
    elif tool in (TOOL_SQUARE, TOOL_RTRI, TOOL_ETRI, TOOL_RHOMBUS):
        pts = get_polygon_points(tool, p1, p2)
        if len(pts) >= 3:
            pygame.draw.polygon(surface, colour, pts, brush)


def commit_shape(tool, colour, p1, p2, line_w):
    """Permanently draw shape on canvas in canvas coordinates."""
    if tool == TOOL_LINE:
        if p1 != p2:
            pygame.draw.line(canvas, colour, p1, p2, line_w if line_w else 2)
    elif tool == TOOL_RECT:
        x, y = min(p1[0], p2[0]), min(p1[1], p2[1])
        w, h = abs(p2[0]-p1[0]), abs(p2[1]-p1[1])
        if w and h:
            pygame.draw.rect(canvas, colour, (x, y, w, h), line_w)
    elif tool == TOOL_CIRCLE:
        cx = (p1[0]+p2[0])//2
        cy = (p1[1]+p2[1])//2
        r  = int(math.hypot(p2[0]-p1[0], p2[1]-p1[1]) / 2)
        if r:
            pygame.draw.circle(canvas, colour, (cx, cy), r, line_w)
    elif tool in (TOOL_SQUARE, TOOL_RTRI, TOOL_ETRI, TOOL_RHOMBUS):
        pts = get_polygon_points(tool, p1, p2)
        if len(pts) >= 3:
            pygame.draw.polygon(canvas, colour, pts, line_w)


# ══════════════════════════════════════════════
#  MAIN LOOP
# ══════════════════════════════════════════════

def main():
    clock = pygame.time.Clock()

    active_tool   = TOOL_PENCIL
    active_colour = BLACK
    active_brush  = 5
    fill_shapes   = True

    dragging   = False
    drag_start = (0, 0)

    # Text-tool state
    text_mode   = False
    text_pos    = (0, 0)   # canvas coordinates
    text_buffer = ""

    # Status bar message (shown briefly after save)
    status_msg  = ""
    status_tick = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            # ── Keyboard ──────────────────────
            if event.type == pygame.KEYDOWN:

                # Text-tool input
                if text_mode:
                    if event.key == pygame.K_RETURN:
                        # Commit typed text to canvas
                        if text_buffer:
                            surf = font_text.render(text_buffer, True, active_colour)
                            canvas.blit(surf, text_pos)
                        text_mode   = False
                        text_buffer = ""
                    elif event.key == pygame.K_ESCAPE:
                        text_mode   = False
                        text_buffer = ""
                    elif event.key == pygame.K_BACKSPACE:
                        text_buffer = text_buffer[:-1]
                    else:
                        if event.unicode and event.unicode.isprintable():
                            text_buffer += event.unicode
                    continue   # don't process hotkeys while typing

                # Ctrl+S – save canvas
                if event.key == pygame.K_s and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                    fn = save_canvas()
                    status_msg  = f"Saved: {fn}"
                    status_tick = pygame.time.get_ticks()
                    continue

                # Tool hotkeys
                if event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()
                if event.key == pygame.K_c:
                    canvas.fill(WHITE)
                if event.key == pygame.K_p:  active_tool = TOOL_PENCIL
                if event.key == pygame.K_l:  active_tool = TOOL_LINE
                if event.key == pygame.K_r:  active_tool = TOOL_RECT
                if event.key == pygame.K_o:  active_tool = TOOL_CIRCLE
                if event.key == pygame.K_e:  active_tool = TOOL_ERASER
                if event.key == pygame.K_b:  active_tool = TOOL_FILL
                if event.key == pygame.K_t:  active_tool = TOOL_TEXT
                if event.key == pygame.K_q:  active_tool = TOOL_SQUARE
                if event.key == pygame.K_i:  active_tool = TOOL_RTRI
                if event.key == pygame.K_y:  active_tool = TOOL_ETRI
                if event.key == pygame.K_d:  active_tool = TOOL_RHOMBUS
                if event.key == pygame.K_f:  fill_shapes = not fill_shapes
                # Brush size hotkeys 1/2/3
                if event.key == pygame.K_1:  active_brush = BRUSH_SIZES[0]
                if event.key == pygame.K_2:  active_brush = BRUSH_SIZES[1]
                if event.key == pygame.K_3:  active_brush = BRUSH_SIZES[2]

            # ── Mouse down ────────────────────
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos

                # Toolbar clicks
                for name, rect in tool_buttons.items():
                    if rect.collidepoint(mx, my):
                        active_tool = name
                        text_mode   = False   # cancel text on tool switch
                for rect, colour in swatches:
                    if rect.collidepoint(mx, my):
                        active_colour = colour
                        if active_tool == TOOL_ERASER:
                            active_tool = TOOL_PENCIL
                for rect, size in brush_buttons:
                    if rect.collidepoint(mx, my):
                        active_brush = size
                if fill_btn.collidepoint(mx, my):
                    fill_shapes = not fill_shapes

                # Canvas click
                if my > TOOLBAR_H:
                    cx, cy = canvas_pos(mx, my)

                    if active_tool == TOOL_FILL:
                        flood_fill(canvas, cx, cy, active_colour)

                    elif active_tool == TOOL_TEXT:
                        text_mode   = True
                        text_pos    = (cx, cy)
                        text_buffer = ""

                    else:
                        dragging   = True
                        drag_start = (cx, cy)

            # ── Mouse up ──────────────────────
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if dragging:
                    mx, my   = event.pos
                    drag_end = canvas_pos(mx, my)
                    draw_c   = WHITE if active_tool == TOOL_ERASER else active_colour
                    line_w   = 0 if (fill_shapes and active_tool != TOOL_LINE) else active_brush
                    commit_shape(active_tool, draw_c, drag_start, drag_end, line_w)
                dragging = False

            # ── Mouse motion ──────────────────
            if event.type == pygame.MOUSEMOTION and dragging:
                mx, my = pygame.mouse.get_pos()
                if my > TOOLBAR_H:
                    cx, cy = canvas_pos(mx, my)
                    if active_tool in (TOOL_PENCIL, TOOL_ERASER):
                        colour = WHITE if active_tool == TOOL_ERASER else active_colour
                        # Draw line segment from last point for smooth strokes
                        prev = drag_start if not hasattr(main, '_last') else main._last
                        pygame.draw.line(canvas, colour, prev, (cx, cy), active_brush)
                        pygame.draw.circle(canvas, colour, (cx, cy), active_brush // 2)
                        main._last = (cx, cy)
                        drag_start = (cx, cy)

        # ── Render ────────────────────────────
        screen.blit(canvas, (0, TOOLBAR_H))

        # Live shape preview while dragging
        if dragging and active_tool in SHAPE_TOOLS:
            mx, my = pygame.mouse.get_pos()
            end_c  = canvas_pos(mx, my)
            preview = screen.copy()
            p1_s = (drag_start[0], drag_start[1] + TOOLBAR_H)
            p2_s = (end_c[0],      end_c[1]      + TOOLBAR_H)
            colour = WHITE if active_tool == TOOL_ERASER else active_colour
            draw_preview(preview, active_tool, colour, active_brush, p1_s, p2_s)
            screen.blit(preview, (0, 0))

        # Text-tool cursor and preview
        if text_mode:
            mx, my   = pygame.mouse.get_pos()
            tx, ty   = text_pos[0], text_pos[1] + TOOLBAR_H
            preview_surf = font_text.render(text_buffer + "|", True, active_colour)
            # Light background behind preview text
            bg_r = pygame.Rect(tx-2, ty-2, preview_surf.get_width()+4, preview_surf.get_height()+4)
            pygame.draw.rect(screen, (240, 240, 240), bg_r)
            screen.blit(preview_surf, (tx, ty))

        draw_toolbar(active_tool, active_colour, active_brush, fill_shapes)

        # Status message
        if status_msg and pygame.time.get_ticks() - status_tick < 3000:
            sm = font_info.render(status_msg, True, (0, 200, 0))
            screen.blit(sm, (10, TOOLBAR_H - 18))

        # Cursor indicator (except during text mode)
        if not text_mode:
            mx, my = pygame.mouse.get_pos()
            if my > TOOLBAR_H:
                c_col = WHITE if active_tool == TOOL_ERASER else active_colour
                pygame.draw.circle(screen, c_col, (mx, my), active_brush, 1)

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()
