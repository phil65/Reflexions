from __future__ import annotations

import reflex as rx


def menu_item_link(text: str, href: str):
    return rx.menu.item(
        rx.link(text, href=href, width="100%", color="inherit"),
        # _hover={
        #     "color": styles.accent_color,
        #     "background_color": styles.accent_text_color,
        # },
    )


def menu_button(links: dict[str, str] | None = None) -> rx.Component:
    """The menu button on the top right of the page.

    Args:
        links: A dictionary of links to display in the menu.

    Returns:
        The menu button component.
    """
    from reflex.page import get_decorated_pages

    link_dct = links or {}
    return rx.box(
        rx.menu.root(
            rx.menu.trigger(rx.button(rx.icon("menu"), variant="soft")),
            rx.menu.content(
                *[
                    menu_item_link(page.get("title", "Home"), page["route"])
                    for page in get_decorated_pages()
                ],
                rx.menu.separator(),
                *[menu_item_link(text, link) for text, link in link_dct.items()],
            ),
        ),
        position="fixed",
        right="2em",
        top="2em",
        z_index="500",
    )
