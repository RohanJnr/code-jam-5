import logging
import random

from pygame import Surface
from pygame.transform import flip, scale

from project.constants import HEIGHT, INDICATOR_WIDTH, WIDTH
from .tile import Tile


logger = logging.getLogger(__name__)


class Indicator:
    """Indicator to show the way towards task."""

    # Indicator arrow pulses (moving x coordinates)
    max_x_offset: int = 30  # max x pulse offset from initial position
    pulse_speed: int = 3

    def __init__(
        self, screen: Surface, tile: Tile, image: Surface, is_left: bool = True
    ):
        self.screen = screen
        self.tile = tile
        self.is_left = is_left  # Is facing left

        self.pulse_direction = int(self.is_left)
        self.current_offset = 0

        self.image = image
        scale_percent = INDICATOR_WIDTH / self.image.get_width()
        new_height = int(self.image.get_height() * scale_percent)
        self.image = scale(self.image, (INDICATOR_WIDTH, new_height))
        self.image = flip(self.image, not self.is_left, False)

        self.__update_pos()

    def update(self) -> None:
        """Update is called every game tick."""
        self.__pulse()

    def draw(self) -> None:
        """Draw is called every game tick."""
        offset = self.current_offset if self.is_left else -self.current_offset
        self.screen.blit(self.image, (self.position_x + offset, self.position_y))

    def flip(self, to_left: bool) -> None:
        """Set new position (left or right) for the indicator."""
        if self.is_left != to_left:
            self.is_left = to_left
            self.image = flip(self.image, True, False)
            self.__update_pos()

    def __update_pos(self) -> None:
        """Update/Set x and y positions of indicator."""
        self.position_x = 0 if self.is_left else WIDTH - self.image.get_width()
        self.position_y = random.randint(int(HEIGHT * 0.2), int(HEIGHT * 0.65))

    def __pulse(self) -> None:
        """Pulsing effect - moves indicator x position in and out."""
        # Limit pulse offset
        if self.current_offset >= self.max_x_offset:
            self.pulse_direction = -1
        elif self.current_offset <= 0:
            self.pulse_direction = 1

        self.current_offset += self.pulse_speed * self.pulse_direction
