"""
ball.py - Ball Logic
Defines the Ball class with movement and boundary enforcement.
"""

import pygame


class Ball:
    """
    Represents a red ball that moves around the screen.

    Attributes:
        x (int): Current x-coordinate of the ball's center
        y (int): Current y-coordinate of the ball's center
        radius (int): Radius of the ball in pixels
        color (tuple): RGB colour of the ball
        step (int): Number of pixels moved per key press
        screen_w (int): Screen width for boundary checking
        screen_h (int): Screen height for boundary checking
    """

    def __init__(self, x: int, y: int, radius: int,
                 screen_w: int, screen_h: int,
                 color=(220, 40, 40), step=20):
        """
        Initialise the ball.

        Args:
            x (int): Starting x-coordinate (center)
            y (int): Starting y-coordinate (center)
            radius (int): Ball radius in pixels
            screen_w (int): Screen width
            screen_h (int): Screen height
            color (tuple): RGB colour tuple
            step (int): Pixels per key press
        """
        self.x        = x
        self.y        = y
        self.radius   = radius
        self.color    = color
        self.step     = step
        self.screen_w = screen_w
        self.screen_h = screen_h

    # ── Movement methods ──────────────────────────────────────────────────────

    def move_up(self):
        """Move the ball up by one step, if within bounds."""
        new_y = self.y - self.step
        if new_y - self.radius >= 0:          # Top boundary
            self.y = new_y

    def move_down(self):
        """Move the ball down by one step, if within bounds."""
        new_y = self.y + self.step
        if new_y + self.radius <= self.screen_h:   # Bottom boundary
            self.y = new_y

    def move_left(self):
        """Move the ball left by one step, if within bounds."""
        new_x = self.x - self.step
        if new_x - self.radius >= 0:          # Left boundary
            self.x = new_x

    def move_right(self):
        """Move the ball right by one step, if within bounds."""
        new_x = self.x + self.step
        if new_x + self.radius <= self.screen_w:   # Right boundary
            self.x = new_x

    # ── Drawing ───────────────────────────────────────────────────────────────

    def draw(self, surface: pygame.Surface):
        """
        Draw the ball onto the given surface with a shadow and highlight.

        Args:
            surface (pygame.Surface): Target surface to draw on
        """
        # Drop shadow
        shadow_color = (180, 160, 160)
        pygame.draw.circle(surface, shadow_color,
                           (self.x + 5, self.y + 5), self.radius)

        # Main ball body
        pygame.draw.circle(surface, self.color,
                           (self.x, self.y), self.radius)

        # Darker outline for definition
        outline = tuple(max(0, c - 60) for c in self.color)
        pygame.draw.circle(surface, outline,
                           (self.x, self.y), self.radius, 3)

        # Specular highlight (top-left quarter)
        highlight_x = self.x - self.radius // 4
        highlight_y = self.y - self.radius // 4
        pygame.draw.circle(surface, (255, 180, 180),
                           (highlight_x, highlight_y), self.radius // 5)

    # ── Accessors ─────────────────────────────────────────────────────────────

    def get_position(self):
        """Return the ball's (x, y) center as a tuple."""
        return (self.x, self.y)

    def is_at_boundary(self) -> dict:
        """
        Return a dict of which boundaries the ball is currently touching.

        Returns:
            dict: {'top': bool, 'bottom': bool, 'left': bool, 'right': bool}
        """
        return {
            "top":    self.y - self.radius <= 0,
            "bottom": self.y + self.radius >= self.screen_h,
            "left":   self.x - self.radius <= 0,
            "right":  self.x + self.radius >= self.screen_w,
        }
