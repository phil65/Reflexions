from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pydantic import BaseModel
import reflex as rx


if TYPE_CHECKING:
    from collections.abc import Callable


class TemplateItem(BaseModel):
    """Represents a template card with all necessary information."""

    icon: str
    title: str
    description: str
    color: str


def template_card(
    item: TemplateItem, on_click: Callable[[TemplateItem], Any] | None = None
) -> rx.Component:
    """Create a template card with the provided click handler.

    Args:
        item: The template item data
        on_click: Function that takes a TemplateItem and returns an event handler
    """
    return rx.el.button(
        rx.icon(tag=item.icon, color=rx.color(item.color, 9), size=16),
        rx.text(item.title, class_name="font-medium text-slate-11 text-sm"),
        rx.text(item.description, class_name="text-slate-10 text-xs"),
        class_name="relative align-top flex flex-col gap-2 border-slate-4 bg-slate-1 hover:bg-slate-3 shadow-sm px-3 pt-3 pb-4 border rounded-2xl text-[15px] text-start transition-colors",  # noqa: E501
        on_click=on_click(item)
        if on_click
        else None,  # Pass the entire item to the click handler
    )


style = rx.Style(
    animation="reveal 0.35s ease-out",
    keyframes={
        "reveal": {
            "0%": {"opacity": "0"},
            "100%": {"opacity": "1"},
        }
    },
)


def templates(
    items: list[TemplateItem],
    on_click: Callable[[TemplateItem], Any] | None = None,
    cols: int = 4,
) -> rx.Component:
    """Create a templates section with custom click handling."""
    return rx.box(
        rx.box(
            *[template_card(item, on_click) for item in items],
            class_name=f"gap-4 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-{cols} w-full",
        ),
        class_name="top-1/3 left-1/2 absolute flex flex-col justify-center items-center gap-10 w-full max-w-4xl transform -translate-x-1/2 -translate-y-1/2 px-6 z-50",  # noqa: E501
        style=style,
        display="flex",
    )
