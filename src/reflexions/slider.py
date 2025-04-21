from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import reflex as rx


if TYPE_CHECKING:
    from collections.abc import Callable


@dataclass
class SlideContent:
    """Represents content for a single slide in the card slider."""

    title: str
    description: str
    content: rx.Component

    # Optional custom height for this specific slide
    height: str | None = None


def create_view(
    slide: SlideContent, index: int, active_index_var: rx.Var
) -> rx.Component:
    """Create a view component for a single slide.

    Args:
        slide: The slide content to render
        index: Index of this slide
        active_index_var: Var reference to the active index

    Returns:
        A component representing a slide
    """
    return rx.vstack(
        rx.text(slide.title, size="1", weight="bold"),
        rx.text(slide.description, size="1"),
        slide.content,
        opacity=rx.cond(active_index_var == index, "1", "0"),
        transform=f"translateX({(index - active_index_var) * 100}%)",  # pyright: ignore
        transition="all 400ms ease",
        position="absolute",
        width="100%",
        display="flex",
        padding="1em",
    )


def card_slider(
    slides: list[SlideContent],
    *,
    initial_index: int = 0,
    default_height: str = "10em",
    on_change: Callable[[int], None] | None = None,
) -> rx.Component:
    """Create a card slider with configurable slides.

    This implementation creates a unique state for each slider instance,
    allowing multiple independent sliders on the same page.

    Args:
        slides: List of SlideContent objects defining each slide
        initial_index: Initial active slide index
        default_height: Default height for slides that don't specify custom height
        on_change: Optional callback when active index changes

    Returns:
        A card slider component
    """

    # Create a state for this specific slider instance
    class SliderState(rx.State):
        active_index: int = initial_index

        def next(self):
            if self.active_index < len(slides) - 1:
                self.active_index += 1
                if on_change:
                    on_change(self.active_index)

        def prev(self):
            if self.active_index > 0:
                self.active_index -= 1
                if on_change:
                    on_change(self.active_index)

        @rx.var
        def current_height(self) -> str:
            """Calculate the height for the current slide."""
            if 0 <= self.active_index < len(slides):
                current_slide = slides[self.active_index]
                return current_slide.height or default_height
            return default_height

    # Build the slider component
    return rx.vstack(
        rx.box(
            *[
                create_view(slide, i, SliderState.active_index)  # pyright: ignore
                for i, slide in enumerate(slides)
            ],
            position="relative",
            width="100%",
            height=SliderState.current_height,
            overflow="hidden",
            transition="height 450ms ease",
        ),
        rx.hstack(
            rx.button(
                "Back",
                variant="soft",
                cursor=rx.cond(SliderState.active_index == 0, "not-allowed", "pointer"),
                on_click=SliderState.prev,  # pyright: ignore
                disabled=rx.cond(SliderState.active_index == 0, True, False),
            ),
            rx.button(
                "Continue",
                cursor=rx.cond(
                    SliderState.active_index == len(slides) - 1,
                    "not-allowed",
                    "pointer",
                ),
                on_click=SliderState.next,  # pyright: ignore
                disabled=rx.cond(
                    SliderState.active_index == len(slides) - 1, True, False
                ),
            ),
            padding="1em",
            width="100%",
            justify="between",
        ),
        width="100%",
        max_width="30em",
        border=f"1px solid {rx.color('gray', 4)}",
        border_radius="6px",
        box_shadow="0px 4px 8px 0px rgba(0, 0, 0, 0.25)",
    )
