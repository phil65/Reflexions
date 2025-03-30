"""The main Chat app."""

from __future__ import annotations

import reflex as rx
import reflex_chakra as rc

from reflexions.cards import TemplateItem, cards
from reflexions.iconify import iconify


INTRO = """
# 🤖 Demo-Tool
"""

items = [
    TemplateItem(
        icon="message-circle",
        title="Create a Ticket",
        description="Create a Jira ticket with priority 'high'",
        color="grass",
    ),
    TemplateItem(
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
        rc.center(
            iconify("mdi:chat"),
            cards(items=items),
            padding_top="2em",
        ),
        padding="2em",
    )


theme = rx.theme(appearance="dark", accent_color="cyan", scaling="110%", radius="small")
app = rx.App(theme=theme)
app.add_page(welcome)
