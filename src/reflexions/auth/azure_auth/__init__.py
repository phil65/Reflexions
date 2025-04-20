"""Reflexions Azure AD Authentication Helper Library."""

from __future__ import annotations

from .components import login_button, logout_button
from .config import configure_azure_auth
from .core import SsoState
from .decorators import authenticated_page
from .routes import add_azure_auth_routes


__all__ = [
    "SsoState",
    "add_azure_auth_routes",
    "authenticated_page",
    "configure_azure_auth",
    "login_button",
    "logout_button",
]
