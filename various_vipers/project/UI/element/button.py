"""Contains a function for generating new main menu buttons and button model."""

from typing import List

import pygame as pg
from pygame import Rect

from project.constants import HEIGHT, WIDTH


def generate_main_buttons(
    screen: pg.Surface, btn_w: int, btn_h: int, btn_count: int, gap: int, images: list
) -> List["Button"]:
    """
    Generates new buttons in main menu pattern.

    Pattern:
        Buttons have gaps between them so this function
        calculates what space to left at the top and the bottom
        to allign them properly.
    """
    # store the buttons in a list
    buttons = list()

    # calculate the button length
    btn_len = btn_h * btn_count
    # calculate the gap length
    gap_len = (btn_count - 1) * gap

    # calculate the margin on the sides
    margin_x = (WIDTH - btn_w) / 2
    # calculate the margin on top and bottom
    margin_y = (HEIGHT - (btn_len + gap_len)) / 2

    # iterate every position
    for pos in range(1, btn_count + 1):
        # the most left point of the button
        left = margin_x
        # the top point of the button
        top = margin_y + (gap * (pos - 1)) + (btn_h * (pos - 1))

        # create new button and add it to the list
        new_button = Button(
            screen=screen,
            x=left,
            y=top,
            width=btn_w,
            height=btn_h,
            image=images[pos - 1][0],
            image_hover=images[pos - 1][1],
        )
        buttons.append(new_button)
    return buttons


class Button:
    """Represents a button."""

    def __init__(
        self,
        screen: pg.Surface,
        x: int,
        y: int,
        width: int,
        height: int,
        image: pg.image,
        image_hover: pg.image = None,
    ):
        """Sets rectangle object for the button."""
        self.screen = screen
        self.image = image
        self.image_hover = image_hover

        self.image = pg.transform.scale(self.image, (width, height))
        self.image_hover = pg.transform.scale(self.image_hover, (width, height))
        self.rect = Rect(x, y, width, height)

    def draw(self, hover: bool = False) -> None:
        """Draws the button on the screen."""
        if hover:
            self.screen.blit(self.image_hover, self.rect)
        else:
            self.screen.blit(self.image, self.rect)
