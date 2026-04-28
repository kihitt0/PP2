"""Drawing tools and helpers for Paint – TSIS 2."""

import math
import datetime
import pygame

# ─── Tool identifiers ─────────────────────────────────────────────────────────

TOOL_PENCIL  = "pencil"
TOOL_LINE    = "line"
TOOL_RECT    = "rectangle"
TOOL_CIRCLE  = "circle"
TOOL_ERASER  = "eraser"
TOOL_FILL    = "fill"
TOOL_TEXT    = "text"
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

BRUSH_SIZES = [2, 5, 10]


# ─── Geometry helpers ─────────────────────────────────────────────────────────

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


# ─── Flood fill ───────────────────────────────────────────────────────────────

def flood_fill(surface: pygame.Surface, x: int, y: int, fill_color: tuple):
    """BFS flood fill on `surface` starting at (x, y)."""
    if not (0 <= x < surface.get_width() and 0 <= y < surface.get_height()):
        return
    target = surface.get_at((x, y))[:3]
    fill_c = fill_color[:3]
    if target == fill_c:
        return

    arr    = pygame.PixelArray(surface)
    mapped = surface.map_rgb(*fill_c)
    stack  = [(x, y)]
    visited = set()
    w, h   = surface.get_width(), surface.get_height()

    while stack:
        cx, cy = stack.pop()
        if (cx, cy) in visited:
            continue
        if not (0 <= cx < w and 0 <= cy < h):
            continue
        cur = surface.unmap_rgb(arr[cx, cy])[:3]
        if cur != target:
            continue
        visited.add((cx, cy))
        arr[cx, cy] = mapped
        stack.extend([(cx+1, cy), (cx-1, cy), (cx, cy+1), (cx, cy-1)])

    del arr


# ─── Canvas save ─────────────────────────────────────────────────────────────

def save_canvas(canvas: pygame.Surface) -> str:
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    fn = f"canvas_{ts}.png"
    pygame.image.save(canvas, fn)
    return fn


# ─── Shape draw / preview ────────────────────────────────────────────────────

def draw_preview(surface, tool, colour, brush, p1, p2):
    """Ghost outline preview drawn in screen coordinates."""
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


def commit_shape(canvas, tool, colour, p1, p2, line_w):
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
