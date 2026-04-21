"""
Paint Application – Practice 11
Extends Practice 10 with four new shape tools:
  1. Square       – click-drag to draw a filled square (equal sides)
  2. R-Tri        – right triangle; right angle at bottom-left of drag area
  3. Eq-Tri       – equilateral triangle; base = horizontal drag width
  4. Rhombus      – diamond (midpoints of bounding-box sides)
All new shapes support the live preview while dragging and are committed
to the canvas (filled) on mouse release.  Full comments throughout.
"""

import pygame
import sys
import math

pygame.init()

# ─────────────────────────────────────────────
# SCREEN DIMENSIONS
# ─────────────────────────────────────────────
CANVAS_W  = 900
CANVAS_H  = 600
# Two-row toolbar:
#   Row 1  (y  5 .. 55) : tool buttons
#   Row 2  (y 65 ..100) : colour swatches + brush-size buttons
TOOLBAR_H = 115

SCREEN_W = CANVAS_W
SCREEN_H = CANVAS_H + TOOLBAR_H

screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Paint – Practice 11")

# ─────────────────────────────────────────────
# COLOURS
# ─────────────────────────────────────────────
WHITE             = (255, 255, 255)
BLACK             = (0,   0,   0)
TOOLBAR_BG        = (45,  45,  45)
SWATCH_BORDER_SEL = (255, 255,  0)   # yellow border on the selected colour
SWATCH_BORDER_NRM = (200, 200, 200)

PALETTE = [
    (0,   0,   0),
    (255, 255, 255),
    (220, 30,  30),
    (30,  180, 30),
    (30,  80,  220),
    (255, 200, 0),
    (255, 130, 0),
    (180, 0,   180),
    (0,   200, 200),
    (180, 100, 50),
    (255, 150, 180),
    (100, 100, 100),
]

# ─────────────────────────────────────────────
# TOOL IDENTIFIERS
# ─────────────────────────────────────────────
TOOL_PENCIL  = "pencil"
TOOL_RECT    = "rectangle"
TOOL_CIRCLE  = "circle"
TOOL_ERASER  = "eraser"
TOOL_SQUARE  = "square"    # new: locked-aspect rectangle
TOOL_RTRI    = "r-tri"     # new: right triangle
TOOL_ETRI    = "eq-tri"    # new: equilateral triangle
TOOL_RHOMBUS = "rhombus"   # new: diamond / rhombus

TOOLS = [
    TOOL_PENCIL, TOOL_RECT, TOOL_CIRCLE, TOOL_ERASER,
    TOOL_SQUARE, TOOL_RTRI, TOOL_ETRI,  TOOL_RHOMBUS,
]

# Tools that need a click-drag-release workflow (not freehand)
SHAPE_TOOLS = {TOOL_RECT, TOOL_CIRCLE, TOOL_SQUARE, TOOL_RTRI, TOOL_ETRI, TOOL_RHOMBUS}

# Human-readable labels for the toolbar buttons
TOOL_LABELS = {
    TOOL_PENCIL:  "Pencil",
    TOOL_RECT:    "Rect",
    TOOL_CIRCLE:  "Circle",
    TOOL_ERASER:  "Eraser",
    TOOL_SQUARE:  "Square",
    TOOL_RTRI:    "R-Tri",
    TOOL_ETRI:    "Eq-Tri",
    TOOL_RHOMBUS: "Rhombus",
}

# ─────────────────────────────────────────────
# FONTS
# ─────────────────────────────────────────────
font_btn = pygame.font.SysFont("Arial", 13, bold=True)

# ─────────────────────────────────────────────
# TOOLBAR LAYOUT  (computed once at start-up)
# ─────────────────────────────────────────────
# ── Row 1: tool buttons ────────────────────────────────────────────────
TOOL_BTN_W   = 103
TOOL_BTN_H   = 48
TOOL_BTN_GAP = 5
TOOL_ROW_Y   = 5      # top y of tool buttons inside the toolbar

tool_buttons: dict[str, pygame.Rect] = {}
bx = 8
for t in TOOLS:
    tool_buttons[t] = pygame.Rect(bx, TOOL_ROW_Y, TOOL_BTN_W, TOOL_BTN_H)
    bx += TOOL_BTN_W + TOOL_BTN_GAP

# ── Row 2: colour swatches ─────────────────────────────────────────────
SWATCH_SIZE = 28
SWATCH_GAP  = 4
SWATCH_ROW_Y = 67     # top y of colour swatches inside the toolbar

swatches: list[tuple[pygame.Rect, tuple]] = []
sx = 8
for colour in PALETTE:
    swatches.append((pygame.Rect(sx, SWATCH_ROW_Y, SWATCH_SIZE, SWATCH_SIZE), colour))
    sx += SWATCH_SIZE + SWATCH_GAP

# ── Row 2: brush-size buttons (placed right of the swatches) ──────────
BRUSH_SIZES = [2, 6, 12]
brush_buttons: list[tuple[pygame.Rect, int]] = []
bsx = sx + 14   # small gap after the last swatch
for bs in BRUSH_SIZES:
    brush_buttons.append(
        (pygame.Rect(bsx, SWATCH_ROW_Y, 36, SWATCH_SIZE), bs)
    )
    bsx += 36 + 5

# ── Row 2: fill / outline toggle (placed right of brush buttons) ──────
FILL_BTN_W = 52
FILL_BTN_H = SWATCH_SIZE
fill_btn = pygame.Rect(bsx + 10, SWATCH_ROW_Y, FILL_BTN_W, FILL_BTN_H)

# ─────────────────────────────────────────────
# CANVAS SURFACE
# ─────────────────────────────────────────────
# Drawing is done on a separate surface so shapes are permanently stored.
canvas = pygame.Surface((CANVAS_W, CANVAS_H))
canvas.fill(WHITE)


# ══════════════════════════════════════════════
#  GEOMETRY HELPERS
# ══════════════════════════════════════════════

def get_polygon_points(tool: str, p1: tuple, p2: tuple) -> list:
    """
    Return a list of (x, y) polygon vertices for the given shape tool.

    p1 and p2 are the two drag-corner points in the same coordinate space
    (either both canvas-space or both screen-space).

    Rules per shape:
      square   – side = min(|dx|, |dy|), anchored at p1
      r-tri    – right angle at (p1.x, p2.y); other corners at p1 and p2
      eq-tri   – base is the horizontal extent; height = sqrt(3)/2 * base
      rhombus  – four vertices at midpoints of the bounding-box sides
    """
    x1, y1 = p1
    x2, y2 = p2

    if tool == TOOL_SQUARE:
        # Lock the smaller dimension so all four sides are equal
        side = min(abs(x2 - x1), abs(y2 - y1))
        # Determine direction of drag so the square follows the cursor
        ox = 0 if x2 >= x1 else -side
        oy = 0 if y2 >= y1 else -side
        return [
            (x1 + ox,        y1 + oy),
            (x1 + ox + side, y1 + oy),
            (x1 + ox + side, y1 + oy + side),
            (x1 + ox,        y1 + oy + side),
        ]

    elif tool == TOOL_RTRI:
        # Right angle at the corner that shares x with p1 and y with p2.
        # The two legs are axis-aligned (one vertical, one horizontal).
        return [(x1, y1), (x2, y2), (x1, y2)]

    elif tool == TOOL_ETRI:
        # Use the horizontal span as the base.
        # Height = sqrt(3)/2 * base  (equilateral triangle property).
        bx1, bx2 = min(x1, x2), max(x1, x2)
        base = bx2 - bx1
        if base == 0:
            return []
        height   = int(base * math.sqrt(3) / 2)
        # Place the base at the bottom of the drag bounding box
        bottom_y = max(y1, y2)
        apex_y   = bottom_y - height
        return [
            (bx1,              bottom_y),
            (bx2,              bottom_y),
            ((bx1 + bx2) // 2, apex_y),
        ]

    elif tool == TOOL_RHOMBUS:
        # Vertices sit at the midpoints of each side of the bounding box,
        # creating a diamond that exactly fits the drag area.
        x, y = min(x1, x2), min(y1, y2)
        w, h = abs(x2 - x1), abs(y2 - y1)
        return [
            (x + w // 2, y),         # top
            (x + w,      y + h // 2),  # right
            (x + w // 2, y + h),     # bottom
            (x,          y + h // 2),  # left
        ]

    return []   # unknown tool


# ══════════════════════════════════════════════
#  DRAWING HELPERS
# ══════════════════════════════════════════════

def canvas_pos(sx: int, sy: int) -> tuple:
    """Convert a screen coordinate to canvas-relative coordinates."""
    return (sx, sy - TOOLBAR_H)


def draw_toolbar(active_tool: str, active_colour: tuple, active_brush: int,
                 fill_shapes: bool):
    """Render the full toolbar: tool buttons, colour swatches, brush buttons, fill toggle."""
    pygame.draw.rect(screen, TOOLBAR_BG, pygame.Rect(0, 0, SCREEN_W, TOOLBAR_H))

    # Tool buttons
    for name, rect in tool_buttons.items():
        bg = (100, 100, 200) if name == active_tool else (70, 70, 70)
        pygame.draw.rect(screen, bg, rect, border_radius=6)
        pygame.draw.rect(screen, WHITE, rect, 1, border_radius=6)
        label = font_btn.render(TOOL_LABELS[name], True, WHITE)
        screen.blit(label, label.get_rect(center=rect.center))

    # Colour swatches
    for rect, colour in swatches:
        pygame.draw.rect(screen, colour, rect)
        border = SWATCH_BORDER_SEL if colour == active_colour else SWATCH_BORDER_NRM
        pygame.draw.rect(screen, border, rect, 2)

    # Brush-size buttons (show a dot whose radius represents the brush)
    for rect, size in brush_buttons:
        bg = (100, 100, 200) if size == active_brush else (70, 70, 70)
        pygame.draw.rect(screen, bg, rect, border_radius=5)
        pygame.draw.rect(screen, WHITE, rect, 1, border_radius=5)
        pygame.draw.circle(screen, WHITE, rect.center, min(size, 10))

    # Fill / Outline toggle button: green = filled, red = outline
    fill_bg  = (50, 150, 60) if fill_shapes else (150, 50, 50)
    fill_txt = "Fill" if fill_shapes else "Line"
    pygame.draw.rect(screen, fill_bg, fill_btn, border_radius=6)
    pygame.draw.rect(screen, WHITE,   fill_btn, 1, border_radius=6)
    fl = font_btn.render(fill_txt, True, WHITE)
    screen.blit(fl, fl.get_rect(center=fill_btn.center))


def draw_preview(surface, tool: str, colour: tuple, brush: int,
                 p1: tuple, p2: tuple):
    """
    Draw a ghost (outline) preview of the shape being dragged onto `surface`.
    p1 and p2 are in screen coordinates.  The outline width equals `brush`
    so the preview is clearly non-destructive.
    """
    if tool == TOOL_RECT:
        x = min(p1[0], p2[0]); y = min(p1[1], p2[1])
        w = abs(p2[0] - p1[0]); h = abs(p2[1] - p1[1])
        if w > 0 and h > 0:
            pygame.draw.rect(surface, colour, pygame.Rect(x, y, w, h), brush)

    elif tool == TOOL_CIRCLE:
        cx = (p1[0] + p2[0]) // 2
        cy = (p1[1] + p2[1]) // 2
        radius = int(math.hypot(p2[0] - p1[0], p2[1] - p1[1]) / 2)
        if radius > 0:
            pygame.draw.circle(surface, colour, (cx, cy), radius, brush)

    elif tool in (TOOL_SQUARE, TOOL_RTRI, TOOL_ETRI, TOOL_RHOMBUS):
        pts = get_polygon_points(tool, p1, p2)
        if len(pts) >= 3:
            pygame.draw.polygon(surface, colour, pts, brush)


def commit_shape(tool: str, draw_colour: tuple, p1: tuple, p2: tuple,
                 line_w: int):
    """
    Draw the final shape permanently onto the canvas.
    p1 and p2 are in canvas coordinates.
    line_w=0 draws a filled shape; line_w>0 draws an outline of that thickness.
    """
    if tool == TOOL_RECT:
        x = min(p1[0], p2[0]); y = min(p1[1], p2[1])
        w = abs(p2[0] - p1[0]); h = abs(p2[1] - p1[1])
        if w > 0 and h > 0:
            pygame.draw.rect(canvas, draw_colour, pygame.Rect(x, y, w, h), line_w)

    elif tool == TOOL_CIRCLE:
        cx = (p1[0] + p2[0]) // 2
        cy = (p1[1] + p2[1]) // 2
        radius = int(math.hypot(p2[0] - p1[0], p2[1] - p1[1]) / 2)
        if radius > 0:
            pygame.draw.circle(canvas, draw_colour, (cx, cy), radius, line_w)

    elif tool in (TOOL_SQUARE, TOOL_RTRI, TOOL_ETRI, TOOL_RHOMBUS):
        pts = get_polygon_points(tool, p1, p2)
        if len(pts) >= 3:
            pygame.draw.polygon(canvas, draw_colour, pts, line_w)


# ══════════════════════════════════════════════
#  MAIN LOOP
# ══════════════════════════════════════════════

def main():
    clock = pygame.time.Clock()

    # Application state
    active_tool   = TOOL_PENCIL
    active_colour = BLACK
    active_brush  = 6
    fill_shapes   = True   # True = filled shapes, False = outline only

    dragging   = False   # True while left mouse button is held inside the canvas
    drag_start = (0, 0)  # canvas-space start of the current drag

    while True:
        # ── Event handling ────────────────────
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            # Keyboard shortcuts
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()
                if event.key == pygame.K_c:
                    canvas.fill(WHITE)          # clear canvas
                if event.key == pygame.K_p:  active_tool = TOOL_PENCIL
                if event.key == pygame.K_r:  active_tool = TOOL_RECT
                if event.key == pygame.K_o:  active_tool = TOOL_CIRCLE
                if event.key == pygame.K_e:  active_tool = TOOL_ERASER
                if event.key == pygame.K_s:  active_tool = TOOL_SQUARE
                if event.key == pygame.K_t:  active_tool = TOOL_RTRI
                if event.key == pygame.K_y:  active_tool = TOOL_ETRI
                if event.key == pygame.K_d:  active_tool = TOOL_RHOMBUS
                if event.key == pygame.K_f:  fill_shapes = not fill_shapes

            # Mouse button pressed
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos

                # Check toolbar row 1: tool buttons
                for name, rect in tool_buttons.items():
                    if rect.collidepoint(mx, my):
                        active_tool = name

                # Check toolbar row 2: colour swatches
                for rect, colour in swatches:
                    if rect.collidepoint(mx, my):
                        active_colour = colour
                        # Clicking a colour while erasing switches back to pencil
                        if active_tool == TOOL_ERASER:
                            active_tool = TOOL_PENCIL

                # Check toolbar row 2: brush-size buttons
                for rect, size in brush_buttons:
                    if rect.collidepoint(mx, my):
                        active_brush = size

                # Fill/Outline toggle button
                if fill_btn.collidepoint(mx, my):
                    fill_shapes = not fill_shapes

                # Start a drag if the click is inside the canvas area
                if my > TOOLBAR_H:
                    dragging   = True
                    drag_start = canvas_pos(mx, my)

            # Mouse button released – commit shape tools to canvas
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if dragging:
                    mx, my    = event.pos
                    drag_end  = canvas_pos(mx, my)
                    # Eraser draws white; all other tools use the active colour
                    draw_colour = WHITE if active_tool == TOOL_ERASER else active_colour
                    # 0 = filled, active_brush = outline thickness
                    line_w = 0 if fill_shapes else active_brush
                    commit_shape(active_tool, draw_colour, drag_start, drag_end, line_w)
                dragging = False

            # Mouse motion – freehand tools paint continuously
            if event.type == pygame.MOUSEMOTION:
                if dragging:
                    mx, my = pygame.mouse.get_pos()
                    if my > TOOLBAR_H:
                        cx, cy = canvas_pos(mx, my)
                        if active_tool in (TOOL_PENCIL, TOOL_ERASER):
                            colour = WHITE if active_tool == TOOL_ERASER else active_colour
                            pygame.draw.circle(canvas, colour, (cx, cy), active_brush)

        # ── Rendering ─────────────────────────
        # 1. Blit the permanent canvas below the toolbar
        screen.blit(canvas, (0, TOOLBAR_H))

        # 2. Draw a live preview for shape tools while dragging
        if dragging and active_tool in SHAPE_TOOLS:
            mx, my = pygame.mouse.get_pos()
            end_c  = canvas_pos(mx, my)
            # Work on a copy to avoid permanently marking the screen
            preview = screen.copy()
            # Convert both endpoints to screen-space for the preview draw call
            p1_s = (drag_start[0], drag_start[1] + TOOLBAR_H)
            p2_s = (end_c[0],      end_c[1]      + TOOLBAR_H)
            colour = WHITE if active_tool == TOOL_ERASER else active_colour
            draw_preview(preview, active_tool, colour, active_brush, p1_s, p2_s)
            screen.blit(preview, (0, 0))

        # 3. Redraw the toolbar on top of everything
        draw_toolbar(active_tool, active_colour, active_brush, fill_shapes)

        # 4. Custom cursor: a small circle that matches the active brush size
        mx, my = pygame.mouse.get_pos()
        if my > TOOLBAR_H:
            c_col = WHITE if active_tool == TOOL_ERASER else active_colour
            pygame.draw.circle(screen, c_col, (mx, my), active_brush, 1)

        pygame.display.flip()
        clock.tick(60)


# ══════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════
if __name__ == "__main__":
    main()
