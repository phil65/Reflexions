"""Decorators for simplifying authenticated page creation."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypeVar

import reflex as rx

from reflexions.auth.azure_auth import components
from reflexions.auth.azure_auth.core import SsoState


if TYPE_CHECKING:
    from collections.abc import Callable

    from reflex.event import EventType

    PageComponentCallable = Callable[[], rx.Component]

F = TypeVar("F", bound=PageComponentCallable)


def authenticated_page(
    route: str | None = None,
    title: str | None = None,
    on_load: EventType[()] | list[EventType[()]] | None = None,
    unauthenticated_view: PageComponentCallable | None = None,
    # loading_view: PageComponentCallable | None = None,
    image: str | None = None,
    description: str | None = None,
    meta: list[Any] | None = None,
    script_tags: list[Any] | None = None,
) -> Callable[[F], F]:
    """Decorator factory that creates a Reflex page requiring authentication.

    Combines @rx.page with authentication checks using SsoState. It
    automatically adds SsoState.require_auth to the on_load handlers and
    conditionally renders the provided page component, a loading view,
    or an unauthenticated view.

    Args:
        route: The route for the page (passed to rx.page).
        title: The title for the page (passed to rx.page).
        on_load: Optional existing on_load event handlers. SsoState.require_auth
            will be prepended.
        unauthenticated_view: Optional component function to display when
            the user is not authenticated (after the initial check).
            Defaults to a simple message.
        image: Optional image URL for the page (passed to rx.page).
        description: Optional description for the page (passed to rx.page).
        meta: Optional list of meta tags for the page (passed to rx.page).
        script_tags: Optional list of script tags for the page (passed to rx.page).

    Returns:
        A decorator that wraps the user's page component function.
    """

    def decorator(func: F) -> F:
        # Determine the views to render
        auth_view_func = func
        unauth_view_func = unauthenticated_view or components._default_unauth_view
        # load_view_func = loading_view or components._default_loading_view

        # Combine on_load handlers
        all_on_load: list[Any] = [SsoState.require_auth]  # Auth check always runs first
        if isinstance(on_load, list):
            all_on_load.extend(on_load)
        elif on_load:
            all_on_load.append(on_load)

        # Define the wrapper component that handles conditional rendering
        def page_wrapper() -> rx.Component:
            return rx.cond(
                SsoState.is_authenticated,
                auth_view_func(),
                unauth_view_func(),
            )

        # Apply the rx.page decorator to the wrapper function
        return rx.page(  # type: ignore
            route=route,
            title=title,
            on_load=all_on_load,
            image=image,
            description=description,
            meta=meta,
            script_tags=script_tags,
        )(page_wrapper)

    return decorator
