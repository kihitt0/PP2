"""
Paint Application – Extended from nerdparadise.com/programming/pygame/part6
Added features:
  1. Draw Rectangle  – click + drag to create filled rectangles
  2. Draw Circle     – click + drag to create filled circles
  3. Eraser          – paint over existing drawing with white
  4. Colour Selection – clickable colour swatches in the toolbar
  Full comments throughout the code.
"""

import pygame
import sys
import math

# ─────────────────────────────────────────────
# INITIALISATION
# ─────────────────────────────────────────────
pygame.init()

# ─────────────────────────────────────────────
# SCREEN DIMENSIONS
# ─────────────────────────────────────────────
CANVAS_W  = 900
CANVAS_H  = 650
TOOLBAR_H = 70       # height of the toolbar strip at the top

SCREEN_W  = CANVAS_W
SCREEN_H  = CANVAS_H + TOOLBAR_H

screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Paint – Pygame")

# ─────────────────────────────────────────────
# COLOURS
# ─────────────────────────────────────────────
WHITE       = (255, 255, 255)
BLACK       = (0,   0,   0)
TOOLBAR_BG  = (45,  45,  45)
SWATCH_BORDER_SEL = (255, 255,  0)   # yellow highlight for selected colour
SWATCH_BORDER_NRM = (200, 200, 200)  # normal swatch border

# Palette of available drawing colours
PALETTE = [
    (0,   0,   0),       # black
    (255, 255, 255),     # white
    (220, 30,  30),      # red
    (30,  180, 30),      # green
    (30,  80,  220),     # blue
    (255, 200, 0),       # yellow
    (255, 130, 0),       # orange
    (180, 0,   180),     # purple
    (0,   200, 200),     # cyan
    (180, 100, 50),      # brown
    (255, 150, 180),     # pink
    (100, 100, 100),     # dark gray
]

# ─────────────────────────────────────────────
# TOOL IDs
# ─────────────────────────────────────────────
TOOL_PENCIL    = "pencil"
TOOL_RECTANGLE = "rectangle"
TOOL_CIRCLE    = "circle"
TOOL_ERASER    = "eraser"
TOOLS = [TOOL_PENCIL, TOOL_RECTANGLE, TOOL_CIRCLE, TOOL_ERASER]

# ─────────────────────────────────────────────
# FONTS
# ─────────────────────────────────────────────
font = pygame.font.SysFont("Arial", 15, bold=True)


# ══════════════════════════════════════════════
#  TOOLBAR LAYOUT  (computed once at start-up)
# ══════════════════════════════════════════════

SWATCH_SIZE   = 30          # width and height of each colour swatch
SWATCH_GAP    = 6           # gap between swatches
TOOL_BTN_W    = 80          # width of each tool button
TOOL_BTN_H    = 40          # height of each tool button
TOOL_BTN_GAP  = 8

# Place tool buttons starting 10 px from the left
tool_buttons: dict[str, pygame.Rect] = {}
bx = 10
for tool_name in TOOLS:
    r = pygame.Rect(bx, (TOOLBAR_H - TOOL_BTN_H) // 2, TOOL_BTN_W, TOOL_BTN_H)
    tool_buttons[tool_name] = r
    bx += TOOL_BTN_W + TOOL_BTN_GAP

# Place colour swatches after the tool buttons, with a small gap
swatches: list[tuple[pygame.Rect, tuple]] = []   # (Rect, colour)
sx = bx + 20
sy = (TOOLBAR_H - SWATCH_SIZE) // 2
for colour in PALETTE:
    r = pygame.Rect(sx, sy, SWATCH_SIZE, SWATCH_SIZE)
    swatches.append((r, colour))
    sx += SWATCH_SIZE + SWATCH_GAP

# Brush-size indicator rects (three sizes: small, medium, large)
BRUSH_SIZES   = [2, 6, 12]
BRUSH_BTN_W   = 36
BRUSH_BTN_H   = 36
brush_buttons: list[tuple[pygame.Rect, int]] = []
bsx = sx + 20
for bs in BRUSH_SIZES:
    r = pygame.Rect(bsx, (TOOLBAR_H - BRUSH_BTN_H) // 2, BRUSH_BTN_W, BRUSH_BTN_H)
    brush_buttons.append((r, bs))
    bsx += BRUSH_BTN_W + 6


# ══════════════════════════════════════════════
#  CANVAS SURFACE
# ══════════════════════════════════════════════
# The canvas is a separate surface so we can blit shapes onto it permanently
canvas = pygame.Surface((CANVAS_W, CANVAS_H))
canvas.fill(WHITE)


# ══════════════════════════════════════════════
#  DRAWING HELPERS
# ══════════════════════════════════════════════

def draw_toolbar(active_tool: str, active_colour: tuple, active_brush: int):
    """Render the toolbar: tool buttons, colour swatches, brush-size buttons."""
    pygame.draw.rect(screen, TOOLBAR_BG, pygame.Rect(0, 0, SCREEN_W, TOOLBAR_H))

    # ── Tool buttons ──────────────────────────
    for name, rect in tool_buttons.items():
        # Highlight the active tool in a lighter shade
        bg = (120, 120, 180) if name == active_tool else (80, 80, 80)
        pygame.draw.rect(screen, bg, rect, border_radius=6)
        pygame.draw.rect(screen, WHITE, rect, 1, border_radius=6)
        label = font.render(name.capitalize(), True, WHITE)
        screen.blit(label, label.get_rect(center=rect.center))

    # ── Colour swatches ───────────────────────
    for rect, colour in swatches:
        pygame.draw.rect(screen, colour, rect)
        border = SWATCH_BORDER_SEL if colour == active_colour else SWATCH_BORDER_NRM
        pygame.draw.rect(screen, border, rect, 2)

    # ── Brush-size buttons ────────────────────
    for rect, size in brush_buttons:
        bg = (120, 120, 180) if size == active_brush else (80, 80, 80)
        pygame.draw.rect(screen, bg, rect, border_radius=5)
        pygame.draw.rect(screen, WHITE, rect, 1, border_radius=5)
        # Draw a small dot whose radius reflects the brush size
        dot_r = min(size, 10)
        pygame.draw.circle(screen, WHITE, rect.center, dot_r)


def canvas_pos(screen_x: int, screen_y: int) -> tuple:
    """Convert screen coordinates to canvas coordinates."""
    return (screen_x, screen_y - TOOLBAR_H)


def draw_preview(surface, tool: str, colour: tuple, brush: int,
                 start: tuple, end: tuple):
    """
    Draw a 'ghost' preview of the shape being dragged.
    Drawn directly on `surface` (not the canvas) so it doesn't stick.
    """
    if tool == TOOL_RECTANGLE:
        x = min(start[0], end[0])
        y = min(start[1], end[1])
        w = abs(end[0] - start[0])
        h = abs(end[1] - start[1])
        if w > 0 and h > 0:
            pygame.draw.rect(surface, colour, pygame.Rect(x, y, w, h), brush)
    elif tool == TOOL_CIRCLE:
        cx = (start[0] + end[0]) // 2
        cy = (start[1] + end[1]) // 2
        radius = int(math.hypot(end[0] - start[0], end[1] - start[1]) / 2)
        if radius > 0:
            pygame.draw.circle(surface, colour, (cx, cy), radius, brush)


# ══════════════════════════════════════════════
#  MAIN LOOP
# ══════════════════════════════════════════════

def main():
    clock = pygame.time.Clock()

    # ── Application state ─────────────────────
    active_tool   = TOOL_PENCIL
    active_colour = BLACK
    active_brush  = 6

    dragging     = False    # True while the mouse button is held
    drag_start   = (0, 0)   # canvas-space start of current drag

    while True:

        # ── Event loop ────────────────────────
        for event in pygame.event.get():

            # Close the application
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            # ── Keyboard shortcuts ─────────────
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()
                # Clear the canvas with C key
                if event.key == pygame.K_c:
                    canvas.fill(WHITE)
                # Tool shortcuts
                if event.key == pygame.K_p:  active_tool = TOOL_PENCIL
                if event.key == pygame.K_r:  active_tool = TOOL_RECTANGLE
                if event.key == pygame.K_o:  active_tool = TOOL_CIRCLE
                if event.key == pygame.K_e:  active_tool = TOOL_ERASER

            # ── Mouse button pressed ───────────
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos

                # Check tool buttons (in the toolbar)
                for name, rect in tool_buttons.items():
                    if rect.collidepoint(mx, my):
                        active_tool = name

                # Check colour swatches
                for rect, colour in swatches:
                    if rect.collidepoint(mx, my):
                        active_colour = colour
                        if active_tool == TOOL_ERASER:
                            active_tool = TOOL_PENCIL  # switch back from eraser

                # Check brush-size buttons
                for rect, size in brush_buttons:
                    if rect.collidepoint(mx, my):
                        active_brush = size

                # If the click is inside the canvas area, begin drawing
                if my > TOOLBAR_H:
                    dragging   = True
                    drag_start = canvas_pos(mx, my)

            # ── Mouse button released ──────────
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if dragging:
                    mx, my = event.pos
                    drag_end = canvas_pos(mx, my)

                    draw_colour = WHITE if active_tool == TOOL_ERASER else active_colour

                    # For shape tools: commit the final shape to the canvas
                    if active_tool == TOOL_RECTANGLE:
                        x = min(drag_start[0], drag_end[0])
                        y = min(drag_start[1], drag_end[1])
                        w = abs(drag_end[0] - drag_start[0])
                        h = abs(drag_end[1] - drag_start[1])
                        if w > 0 and h > 0:
                            pygame.draw.rect(canvas, draw_colour,
                                             pygame.Rect(x, y, w, h))

                    elif active_tool == TOOL_CIRCLE:
                        cx = (drag_start[0] + drag_end[0]) // 2
                        cy = (drag_start[1] + drag_end[1]) // 2
                        radius = int(math.hypot(drag_end[0] - drag_start[0],
                                                drag_end[1] - drag_start[1]) / 2)
                        if radius > 0:
                            pygame.draw.circle(canvas, draw_colour, (cx, cy), radius)

                dragging = False

            # ── Mouse motion – pencil / eraser ─
            if event.type == pygame.MOUSEMOTION:
                mx, my = event.pos
                if dragging and my > TOOLBAR_H:
                    cx, cy = canvas_pos(mx, my)

                    if active_tool in (TOOL_PENCIL, TOOL_ERASER):
                        # Pencil and eraser paint dots along the mouse path
                        colour = WHITE if active_tool == TOOL_ERASER else active_colour
                        pygame.draw.circle(canvas, colour, (cx, cy), active_brush)

        # ── Rendering ─────────────────────────
        # 1. Blit the canvas onto the screen (below the toolbar)
        screen.blit(canvas, (0, TOOLBAR_H))

        # 2. Draw a real-time preview for rectangle/circle while dragging
        if dragging and active_tool in (TOOL_RECTANGLE, TOOL_CIRCLE):
            mx, my = pygame.mouse.get_pos()
            drag_end_screen = canvas_pos(mx, my)
            # Work on a copy so the preview does not affect the canvas
            preview = screen.copy()
            start_screen = (drag_start[0], drag_start[1] + TOOLBAR_H)
            end_screen   = (drag_end_screen[0], drag_end_screen[1] + TOOLBAR_H)
            colour = WHITE if active_tool == TOOL_ERASER else active_colour
            draw_preview(preview, active_tool, colour, active_brush,
                         start_screen, end_screen)
            screen.blit(preview, (0, 0))

        # 3. Draw the toolbar on top
        draw_toolbar(active_tool, active_colour, active_brush)

        # 4. Show a cursor dot at the mouse position (inside the canvas)
        mx, my = pygame.mouse.get_pos()
        if my > TOOLBAR_H:
            cursor_colour = WHITE if active_tool == TOOL_ERASER else active_colour
            pygame.draw.circle(screen, cursor_colour, (mx, my), active_brush, 1)

        pygame.display.flip()
        clock.tick(60)


# ══════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════
if __name__ == "__main__":
    main()
