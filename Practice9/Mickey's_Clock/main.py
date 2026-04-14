"""
main.py - Mickey Mouse Clock Application
Displays an analog clock using Mickey Mouse hand images as clock hands.
Right hand = minutes, Left hand = seconds.

Controls:
  Q or ESC = Quit
"""

import sys
import os
import pygame
from clock import get_current_time, get_minute_angle, get_second_angle, get_time_string

# ── Config ────────────────────────────────────────────────────────────────
WINDOW_WIDTH  = 600
WINDOW_HEIGHT = 600
FPS           = 30          # Frames per second
BG_COLOR      = (255, 248, 220)   # Cornsilk background (warm white)
TEXT_COLOR    = (50, 50, 50)
CENTER        = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)

# Clock face colours
FACE_COLOR    = (255, 255, 255)
FACE_BORDER   = (200, 160, 80)
TICK_COLOR    = (80, 60, 20)


def load_hand_image(path, fallback_size=(20, 120)):
    """
    Load a hand image from disk. If the file is missing, generate a
    simple coloured rectangle as a fallback so the app still runs.

    Args:
        path (str): Path to the image file
        fallback_size (tuple): (width, height) for the fallback surface

    Returns:
        pygame.Surface: The loaded (or generated) image
    """
    if os.path.exists(path):
        img = pygame.image.load(path).convert_alpha()
        return img
    else:
        # Fallback: draw a simple rounded rectangle hand
        surf = pygame.Surface(fallback_size, pygame.SRCALPHA)
        color = (255, 80, 0) if "right" in path else (0, 120, 255)
        pygame.draw.rect(surf, color, surf.get_rect(), border_radius=8)
        pygame.draw.rect(surf, (0, 0, 0), surf.get_rect(), 2, border_radius=8)
        return surf


def rotate_image(image, angle, pivot_offset=0):
    """
    Rotate an image around a custom pivot point (useful for clock hands).
    The pivot is placed near the bottom of the image so it swings from
    the clock center.

    Args:
        image (pygame.Surface): The original image
        angle (float): Rotation angle in degrees
        pivot_offset (int): Pixels from center of image toward bottom for pivot

    Returns:
        tuple: (rotated_surface, rect) positioned correctly on screen
    """
    # Rotate the image
    rotated = pygame.transform.rotate(image, angle)
    return rotated


def draw_clock_face(surface, center, radius):
    """
    Draw the clock face: circle, hour ticks, and minute ticks.

    Args:
        surface (pygame.Surface): Target surface
        center (tuple): (x, y) center of the clock
        radius (int): Radius of the clock face
    """
    cx, cy = center

    # Outer shadow
    pygame.draw.circle(surface, (180, 140, 60), (cx + 4, cy + 4), radius)
    # Main face
    pygame.draw.circle(surface, FACE_COLOR, center, radius)
    # Border
    pygame.draw.circle(surface, FACE_BORDER, center, radius, 6)

    # Draw 60 minute ticks and 12 hour ticks
    for i in range(60):
        angle_rad = math.radians(i * 6 - 90)  # Start from 12 o'clock
        if i % 5 == 0:
            # Hour tick: longer and thicker
            outer = radius - 2
            inner = radius - 20
            width = 4
            color = TICK_COLOR
        else:
            # Minute tick: shorter
            outer = radius - 2
            inner = radius - 10
            width = 2
            color = (150, 120, 60)

        x1 = cx + int(outer * math.cos(angle_rad))
        y1 = cy + int(outer * math.sin(angle_rad))
        x2 = cx + int(inner * math.cos(angle_rad))
        y2 = cy + int(inner * math.sin(angle_rad))
        pygame.draw.line(surface, color, (x1, y1), (x2, y2), width)

    # Center dot
    pygame.draw.circle(surface, TICK_COLOR, center, 10)
    pygame.draw.circle(surface, (255, 200, 50), center, 6)


def draw_hand(surface, image, angle_degrees, center, hand_length):
    """
    Draw a clock hand (Mickey's hand image) rotated to the correct angle.
    The image is scaled to hand_length and rotated around its base.

    Args:
        surface (pygame.Surface): Target surface
        image (pygame.Surface): The hand image
        angle_degrees (float): Angle in degrees (0 = pointing up)
        center (tuple): Clock center (x, y)
        hand_length (int): How long the hand should reach
    """
    # Scale hand to desired length while keeping aspect ratio
    orig_w, orig_h = image.get_size()
    scale = hand_length / max(orig_h, orig_w)
    new_w = int(orig_w * scale)
    new_h = int(orig_h * scale)
    scaled = pygame.transform.smoothscale(image, (new_w, new_h))

    # Rotate the scaled image
    rotated = pygame.transform.rotate(scaled, angle_degrees)
    rot_rect = rotated.get_rect()

    # Offset so the hand pivots from the clock center
    # The hand image tip should point outward; we position it so its
    # center is offset from the clock center in the direction of the angle
    angle_rad = math.radians(-angle_degrees - 90)  # Convert for trig
    offset_x = int((hand_length / 2) * math.cos(angle_rad))
    offset_y = int((hand_length / 2) * math.sin(angle_rad))

    rot_rect.center = (center[0] + offset_x, center[1] + offset_y)
    surface.blit(rotated, rot_rect)


def main():
    """Main entry point for Mickey's Clock application."""
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Mickey's Clock 🕐")
    clock_tick = pygame.time.Clock()

    # ── Load assets ──────────────────────────────────────────────────────────
    images_dir = os.path.join(os.path.dirname(__file__), "images")
    right_hand_path = os.path.join(images_dir, "mickey_hand_right.png")
    left_hand_path  = os.path.join(images_dir, "mickey_hand_left.png")
    # If a single hand image exists, use it for both
    single_hand_path = os.path.join(images_dir, "mickey_hand.png")

    if os.path.exists(single_hand_path):
        minute_img = pygame.image.load(single_hand_path).convert_alpha()
        second_img = minute_img.copy()
    else:
        minute_img = load_hand_image(right_hand_path)
        second_img = load_hand_image(left_hand_path)

    # ── Font ─────────────────────────────────────────────────────────────────
    font_large = pygame.font.SysFont("monospace", 42, bold=True)
    font_small = pygame.font.SysFont("monospace", 22)

    clock_radius = 220
    running = True

    while running:
        # ── Event Handling ────────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_q, pygame.K_ESCAPE):
                    running = False

        # ── Get current time ──────────────────────────────────────────────────
        now      = get_current_time()
        minutes  = now.minute
        seconds  = now.second
        time_str = get_time_string(now)

        min_angle = get_minute_angle(minutes, seconds)
        sec_angle = get_second_angle(seconds)

        # ── Draw ──────────────────────────────────────────────────────────────
        screen.fill(BG_COLOR)

        # Draw decorative background dots
        for i in range(0, WINDOW_WIDTH, 40):
            for j in range(0, WINDOW_HEIGHT, 40):
                pygame.draw.circle(screen, (230, 215, 180), (i, j), 2)

        # Draw clock face
        draw_clock_face(screen, CENTER, clock_radius)

        # Draw minute hand (right hand) — longer
        draw_hand(screen, minute_img, min_angle, CENTER, int(clock_radius * 0.75))

        # Draw second hand (left hand) — longer, reaches near edge
        draw_hand(screen, second_img, sec_angle, CENTER, int(clock_radius * 0.88))

        # Re-draw center dot on top
        pygame.draw.circle(screen, TICK_COLOR, CENTER, 10)
        pygame.draw.circle(screen, (255, 200, 50), CENTER, 6)

        # Draw digital time below clock
        time_surf = font_large.render(time_str, True, TEXT_COLOR)
        time_rect = time_surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 60))
        # Draw background box for readability
        box = time_rect.inflate(20, 10)
        pygame.draw.rect(screen, (255, 230, 150), box, border_radius=8)
        pygame.draw.rect(screen, FACE_BORDER, box, 2, border_radius=8)
        screen.blit(time_surf, time_rect)

        # Draw label
        label = font_small.render("Right=Minutes  Left=Seconds  [Q] Quit", True, (120, 100, 60))
        screen.blit(label, label.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 20)))

        pygame.display.flip()
        clock_tick.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
