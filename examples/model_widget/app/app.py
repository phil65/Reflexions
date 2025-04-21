"""The main Chat app."""

from __future__ import annotations

import reflex as rx
import reflex_chakra as rc

from reflexions import model_selector
from reflexions.buttons import menu_button
from reflexions.cards import CardItem
from reflexions.slider import SlideContent, card_slider


slides = [
    SlideContent(
        title="Step One",
        description="First step description",
        content=rx.vstack(
            rx.skeleton(width="45%", height="0.75em", border_radius="6px"),
            rx.skeleton(width="55%", height="0.75em", border_radius="6px"),
            width="100%",
        ),
    ),
    SlideContent(
        title="Step Two",
        description="Second step description",
        content=rx.skeleton(width="100%", height="6em", border_radius="6px"),
        height="12em",  # Custom height for this slide
    ),
    # More slides...
]

INTRO = """
# 🤖 Demo-Tool
"""

items = [
    CardItem(
        icon="message-circle",
        title="Create a Ticket",
        description="Create a Jira ticket with priority 'high'",
        color="grass",
    ),
    CardItem(
        icon="calculator",
        title="Search Tickets",
        description="Which tickets with priority 'Medium' are in the system?",
        color="tomato",
    ),
]


@rx.page(route="/")
def welcome() -> rx.Component:
    """Welcome page showing introductory content."""
    return rc.container(
        rc.box(
            rx.markdown(INTRO),
            padding="2em",
            background_color=rx.color("mauve", 2),
            border_radius="md",
            max_width="800px",
            margin="0 auto",
            box_shadow="lg",
        ),
        # rc.center(iconify("mdi:chat"), cards(items=items), padding_top="2em"),
        menu_button(),
        card_slider(slides),
        model_selector.model_selector(),
        padding="2em",
    )


theme = rx.theme(appearance="dark", accent_color="cyan", scaling="110%", radius="small")
app = rx.App(theme=theme)
app.add_page(welcome)
