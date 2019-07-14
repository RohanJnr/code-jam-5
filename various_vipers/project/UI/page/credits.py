"""
Credits page.

Handling input and making changes.
"""
import logging

import pygame as pg

from project.UI.element.button import Button
from project.UI.fx.sound import Sound
from project.constants import (
    BUTTONS as BTN,
    ButtonProperties,
    HEIGHT,
    PATH_CREDITS,
    PATH_CREDITS_BG,
    WIDTH,
    WindowState,
)
from project.utils.helpers import draw_infinity_bg, load_img


logger = logging.getLogger(__name__)


class Credits:
    """Represents Credits page."""

    def __init__(self, screen: pg.Surface):
        self.screen = screen

        # images of the back button and its hover state
        back_btn_img = load_img(BTN["back-btn"])
        back_btn_img_h = load_img(BTN["back-btn-hover"])

        # layout of the credits and background image
        self.credits = load_img(PATH_CREDITS)
        self.background = load_img(PATH_CREDITS_BG)

        # rectangles for infinity looping the backgroud image
        self.bg_rect_1 = pg.Rect(0, 0, WIDTH, HEIGHT)
        self.bg_rect_2 = pg.Rect(-WIDTH, 0, WIDTH, HEIGHT)

        # create an instance of a back button
        self.back_btn = Button(
            screen=self.screen,
            x=ButtonProperties.back_btn_x,
            y=ButtonProperties.back_btn_y,
            width=ButtonProperties.back_btn_w,
            height=ButtonProperties.back_btn_h,
            image=back_btn_img,
            image_hover=back_btn_img_h,
        )

    def draw(self, mouse_x: int, mouse_y: int, event: pg.event) -> None:
        """Hadle all options events and draw elements."""
        # draw the infinity background and credits layout
        draw_infinity_bg(self.screen, self.background, self.bg_rect_1, self.bg_rect_2)
        self.screen.blit(self.credits, (0, 0, WIDTH, HEIGHT))

        # check if back buttn is hovered
        if self.back_btn.rect.collidepoint(mouse_x, mouse_y):
            # draw its hover state
            self.back_btn.draw(hover=True)

            # if the back button is clicked play click sound and
            # return to the main menu
            if event.type == pg.MOUSEBUTTONDOWN:
                Sound.click.play()
                return WindowState.main_menu
        else:
            # if it is not hover draw its normal state
            self.back_btn.draw()
        return WindowState.credit
