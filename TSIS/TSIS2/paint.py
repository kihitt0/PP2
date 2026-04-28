"""
Paint Application – TSIS 2
Extends Practice 11 with:
  1. Straight-line tool with live drag preview
  2. Flood-fill (bucket) using pixel-level BFS
  3. Text tool — click to place, type, Enter to commit, Escape to cancel
  4. Ctrl+S saves the canvas as a timestamped PNG file
All brush sizes apply to every drawing tool.
"""

import pygame
import sys

import tools

pygame.init()

# ─── Screen dimensions ────────────────────────────────────────────────────────
CANVAS_W  = 900
CANVAS_H  = 600
TOOLBAR_H = 115
SCREEN_W  = CANVAS_W
SCREEN_H  = CANVAS_H + TOOLBAR_H

screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Paint – TSIS 2")

# ─── Colours ─────────────────────────────────────────────────────────────────
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

# ─── Fonts ────────────────────────────────────────────────────────────────────
font_btn  = pygame.font.SysFont("Arial",    13, bold=True)
font_text = pygame.font.SysFont("Arial",    22)
font_info = pygame.font.SysFont("Consolas", 13)

# ─── Toolbar layout ──────────────────────────────────────────────────────────
TOOL_BTN_W   = 76
TOOL_BTN_H   = 46
TOOL_BTN_GAP = 4
TOOL_ROW_Y   = 4

tool_buttons: dict[str, pygame.Rect] = {}
bx = 6
for t in tools.TOOLS:
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

brush_buttons: list[tuple[pygame.Rect, int]] = []
bsx = sx + 12
for bs in tools.BRUSH_SIZES:
    brush_buttons.append((pygame.Rect(bsx, SWATCH_ROW_Y, 36, SWATCH_SIZE), bs))
    bsx += 40

FILL_BTN_W = 50
fill_btn = pygame.Rect(bsx + 8, SWATCH_ROW_Y, FILL_BTN_W, SWATCH_SIZE)

# ─── Canvas ──────────────────────────────────────────────────────────────────
canvas = pygame.Surface((CANVAS_W, CANVAS_H))
canvas.fill(WHITE)


# ─── Toolbar drawing ─────────────────────────────────────────────────────────

def draw_toolbar(active_tool, active_colour, active_brush, fill_shapes):
    pygame.draw.rect(screen, TOOLBAR_BG, (0, 0, SCREEN_W, TOOLBAR_H))

    for name, rect in tool_buttons.items():
        bg = (90, 90, 200) if name == active_tool else (65, 65, 65)
        pygame.draw.rect(screen, bg, rect, border_radius=5)
        pygame.draw.rect(screen, WHITE, rect, 1, border_radius=5)
        lbl = font_btn.render(tools.TOOL_LABELS[name], True, WHITE)
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


def canvas_pos(sx: int, sy: int) -> tuple:
    return (sx, sy - TOOLBAR_H)


# ─── Main loop ───────────────────────────────────────────────────────────────

def main():
    clock = pygame.time.Clock()

    active_tool   = tools.TOOL_PENCIL
    active_colour = BLACK
    active_brush  = 5
    fill_shapes   = True

    dragging   = False
    drag_start = (0, 0)
    last_pos   = None

    text_mode   = False
    text_pos    = (0, 0)
    text_buffer = ""

    status_msg  = ""
    status_tick = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            # ── Keyboard ──────────────────────────────────────────────────────
            if event.type == pygame.KEYDOWN:

                if text_mode:
                    if event.key == pygame.K_RETURN:
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
                    elif event.unicode and event.unicode.isprintable():
                        text_buffer += event.unicode
                    continue

                if event.key == pygame.K_s and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                    fn = tools.save_canvas(canvas)
                    status_msg  = f"Saved: {fn}"
                    status_tick = pygame.time.get_ticks()
                    continue

                if event.key == pygame.K_ESCAPE:  pygame.quit(); sys.exit()
                if event.key == pygame.K_c:        canvas.fill(WHITE)
                if event.key == pygame.K_p:        active_tool = tools.TOOL_PENCIL
                if event.key == pygame.K_l:        active_tool = tools.TOOL_LINE
                if event.key == pygame.K_r:        active_tool = tools.TOOL_RECT
                if event.key == pygame.K_o:        active_tool = tools.TOOL_CIRCLE
                if event.key == pygame.K_e:        active_tool = tools.TOOL_ERASER
                if event.key == pygame.K_b:        active_tool = tools.TOOL_FILL
                if event.key == pygame.K_t:        active_tool = tools.TOOL_TEXT
                if event.key == pygame.K_q:        active_tool = tools.TOOL_SQUARE
                if event.key == pygame.K_i:        active_tool = tools.TOOL_RTRI
                if event.key == pygame.K_y:        active_tool = tools.TOOL_ETRI
                if event.key == pygame.K_d:        active_tool = tools.TOOL_RHOMBUS
                if event.key == pygame.K_f:        fill_shapes = not fill_shapes
                if event.key == pygame.K_1:        active_brush = tools.BRUSH_SIZES[0]
                if event.key == pygame.K_2:        active_brush = tools.BRUSH_SIZES[1]
                if event.key == pygame.K_3:        active_brush = tools.BRUSH_SIZES[2]

            # ── Mouse down ────────────────────────────────────────────────────
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos

                for name, rect in tool_buttons.items():
                    if rect.collidepoint(mx, my):
                        active_tool = name
                        text_mode   = False
                for rect, colour in swatches:
                    if rect.collidepoint(mx, my):
                        active_colour = colour
                        if active_tool == tools.TOOL_ERASER:
                            active_tool = tools.TOOL_PENCIL
                for rect, size in brush_buttons:
                    if rect.collidepoint(mx, my):
                        active_brush = size
                if fill_btn.collidepoint(mx, my):
                    fill_shapes = not fill_shapes

                if my > TOOLBAR_H:
                    cx, cy = canvas_pos(mx, my)

                    if active_tool == tools.TOOL_FILL:
                        tools.flood_fill(canvas, cx, cy, active_colour)
                    elif active_tool == tools.TOOL_TEXT:
                        text_mode   = True
                        text_pos    = (cx, cy)
                        text_buffer = ""
                    else:
                        dragging   = True
                        drag_start = (cx, cy)
                        last_pos   = (cx, cy)

            # ── Mouse up ──────────────────────────────────────────────────────
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if dragging:
                    mx, my   = event.pos
                    drag_end = canvas_pos(mx, my)
                    draw_c   = WHITE if active_tool == tools.TOOL_ERASER else active_colour
                    line_w   = 0 if (fill_shapes and active_tool != tools.TOOL_LINE) else active_brush
                    tools.commit_shape(canvas, active_tool, draw_c, drag_start, drag_end, line_w)
                dragging = False
                last_pos = None

            # ── Mouse motion ──────────────────────────────────────────────────
            if event.type == pygame.MOUSEMOTION and dragging:
                mx, my = pygame.mouse.get_pos()
                if my > TOOLBAR_H:
                    cx, cy = canvas_pos(mx, my)
                    if active_tool in (tools.TOOL_PENCIL, tools.TOOL_ERASER):
                        colour = WHITE if active_tool == tools.TOOL_ERASER else active_colour
                        prev   = last_pos if last_pos else (cx, cy)
                        pygame.draw.line(canvas, colour, prev, (cx, cy), active_brush)
                        pygame.draw.circle(canvas, colour, (cx, cy), active_brush // 2)
                        last_pos   = (cx, cy)
                        drag_start = (cx, cy)

        # ── Render ────────────────────────────────────────────────────────────
        screen.blit(canvas, (0, TOOLBAR_H))

        if dragging and active_tool in tools.SHAPE_TOOLS:
            mx, my = pygame.mouse.get_pos()
            end_c  = canvas_pos(mx, my)
            preview = screen.copy()
            p1_s = (drag_start[0], drag_start[1] + TOOLBAR_H)
            p2_s = (end_c[0],      end_c[1]      + TOOLBAR_H)
            colour = WHITE if active_tool == tools.TOOL_ERASER else active_colour
            tools.draw_preview(preview, active_tool, colour, active_brush, p1_s, p2_s)
            screen.blit(preview, (0, 0))

        if text_mode:
            tx, ty = text_pos[0], text_pos[1] + TOOLBAR_H
            preview_surf = font_text.render(text_buffer + "|", True, active_colour)
            bg_r = pygame.Rect(tx-2, ty-2, preview_surf.get_width()+4, preview_surf.get_height()+4)
            pygame.draw.rect(screen, (240, 240, 240), bg_r)
            screen.blit(preview_surf, (tx, ty))

        draw_toolbar(active_tool, active_colour, active_brush, fill_shapes)

        if status_msg and pygame.time.get_ticks() - status_tick < 3000:
            sm = font_info.render(status_msg, True, (0, 200, 0))
            screen.blit(sm, (10, TOOLBAR_H - 18))

        if not text_mode:
            mx, my = pygame.mouse.get_pos()
            if my > TOOLBAR_H:
                c_col = WHITE if active_tool == tools.TOOL_ERASER else active_colour
                pygame.draw.circle(screen, c_col, (mx, my), active_brush, 1)

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()
