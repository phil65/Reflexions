from __future__ import annotations

import reflex as rx


class SlidingViewsState(rx.State):
    active_index: int = 0
    height: str = "10em"
    views: list[list[str]] = [  # noqa: RUF012
        ["This is Step One", "Blabla"],
        ["This is Step Two", "Blabla"],
        ["This is Step Three", "Blabla"],
    ]

    def next(self):
        if self.active_index < len(self.views) - 1:
            self.active_index += 1

        self.height = "12em" if self.active_index == 1 else "10em"

    def back(self):
        if self.active_index > 0:
            self.active_index -= 1

        self.height = "12em" if self.active_index == 1 else "10em"


def create_view(content: list[str], index: int):
    return rx.vstack(
        rx.text(content[0], size="1", weight="bold"),
        rx.text(content[1], size="1"),
        rx.vstack(
            rx.cond(
                index == 1,
                rx.skeleton(width="100%", height="6em", border_radius="6px"),
                rx.vstack(
                    rx.skeleton(width="45%", height="0.75em", border_radius="6px"),
                    rx.skeleton(width="55%", height="0.75em", border_radius="6px"),
                    rx.skeleton(width="65%", height="0.75em", border_radius="6px"),
                    width="100%",
                ),
            ),
            width="100%",
        ),
        opacity=rx.cond(SlidingViewsState.active_index == index, "1", "0"),
        transform=f"translateX({(index - SlidingViewsState.active_index) * 100}%)",
        transition="all 400ms ease",
        position="absolute",
        width="100%",
        display="flex",
        padding="1em",
    )


def card_v3():
    return rx.vstack(
        rx.box(
            rx.foreach(
                SlidingViewsState.views,
                lambda content, i: create_view(content, i),
            ),
            position="relative",
            width="100%",
            height=SlidingViewsState.height,
            overflow="hidden",
            transition="height 450ms ease",
        ),
        rx.hstack(
            rx.button(
                "Back",
                variant="soft",
                cursor=rx.cond(
                    SlidingViewsState.active_index == 0, "not-allowed", "pointer"
                ),
                on_click=SlidingViewsState.back,  # type: ignore
                disabled=rx.cond(SlidingViewsState.active_index == 0, True, False),
            ),
            rx.button(
                "Continue",
                cursor=rx.cond(
                    SlidingViewsState.active_index == 2,  # noqa: PLR2004
                    "not-allowed",
                    "pointer",
                ),
                on_click=SlidingViewsState.next,  # type: ignore
                disabled=rx.cond(SlidingViewsState.active_index == 2, True, False),  # noqa: PLR2004
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
