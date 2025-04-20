"""Defines the Reflex page components for Azure AD callback and logout."""

from __future__ import annotations

import reflex as rx

from reflexions.auth.azure_auth import config
from reflexions.auth.azure_auth.core import SsoState


# --- Page Components ---


def callback_page() -> rx.Component:
    """Page component displayed during the authentication callback process.

    This page typically shows a loading indicator as the `on_load` handler
    (SsoState.handle_callback) processes the token exchange.
    """
    return rx.center(
        rx.vstack(
            rx.spinner(size="3"),
            rx.text("Processing login... Please wait."),
            padding="2em",
            align="center",
        ),
        height="80vh",
    )


def logout_page() -> rx.Component:
    """Page component displayed briefly during the logout process.

    The `on_load` handler (SsoState.perform_logout) redirects the user
    to the Azure AD logout endpoint.
    """
    return rx.center(
        rx.vstack(
            rx.spinner(size="3"),
            rx.text("Logging out..."),
            padding="2em",
            align="center",
        ),
        height="80vh",
    )


# --- Setup Function ---


def add_azure_auth_routes(app: rx.App) -> None:
    """Registers the necessary Azure AD callback and logout pages with the Reflex app.

    Call this function after creating your `rx.App` instance.

    Args:
        app: The `rx.App` instance.
    """
    cfg = config.get_config()  # Ensure config is loaded before adding routes
    app.add_page(
        callback_page,
        route=cfg.callback_route,
        title="Login Callback",  # Title usually not visible to user
        on_load=SsoState.handle_callback,  # pyright: ignore
    )
    app.add_page(
        logout_page,
        route=cfg.logout_route,
        title="Logging Out",  # Title usually not visible to user
        on_load=SsoState.perform_logout,  # pyright: ignore
    )
