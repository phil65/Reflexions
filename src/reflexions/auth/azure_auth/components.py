"""Helper components for Azure AD authentication UI."""

from __future__ import annotations

from typing import Any

import reflex as rx

from reflexions.auth.azure_auth import config


def login_button(text: str = "Login with Microsoft", **props: Any) -> rx.Component:
    """Creates a button that initiates the Azure AD login flow.

    Args:
        text: The text displayed on the button.
        **props: Additional props passed to the rx.button component.

    Returns:
        A Reflex button component.
    """
    # Use _redirect_to_sso which returns an EventSpec
    # Need to ensure SsoState._redirect_to_sso is accessible or wrap it
    # Let's add a public method to SsoState for this.

    # Add to SsoState:
    # def trigger_login(self) -> rx.event.EventSpec:
    #     return self._redirect_to_sso()

    # Assuming trigger_login exists in SsoState:
    # return rx.button(
    #     text,
    #     on_click=SsoState.trigger_login, # Need to add trigger_login to SsoState
    #     **props,
    # )
    # --- Temporary workaround until trigger_login is added ---
    # Redirecting directly to the auth endpoint might lose state/flow details.
    # The best way is via SsoState.require_auth or a dedicated login trigger method.
    # For now, let's make it redirect to a protected page, which triggers require_auth.
    cfg = config.get_config()
    return rx.link(
        rx.button(text, **props),
        href=cfg.login_redirect_url,  # Go to home/dashboard which should be protected
        is_external=False,
    )


def logout_button(text: str = "Logout", **props: Any) -> rx.Component:
    """Creates a button that initiates the logout flow.

    Args:
        text: The text displayed on the button.
        **props: Additional props passed to the rx.button component.

    Returns:
        A Reflex button component.
    """
    cfg = config.get_config()
    return rx.link(
        rx.button(text, **props),
        href=cfg.logout_route,  # Link to the internal logout page route
        is_external=False,  # It's an internal route handled by Reflex
    )


# --- Default Views (used by authenticated_page decorator) ---


def _default_unauth_view() -> rx.Component:
    """Default component shown when user is not authenticated."""
    # Could include a login button here
    return rx.center(
        rx.vstack(
            rx.heading("Unauthorized"),
            rx.text("You need to log in to access this page."),
            login_button(),  # Add a login button for convenience
            padding="2em",
            align="center",
        ),
        height="80vh",  # Take up most of the viewport height
    )


def _default_loading_view() -> rx.Component:
    """Default component shown while checking authentication status."""
    # You could use reflexions.loading_icon here if desired
    return rx.center(
        rx.vstack(
            rx.spinner(size="3"),
            rx.text("Checking authentication..."),
            padding="2em",
            align="center",
        ),
        height="80vh",
    )
