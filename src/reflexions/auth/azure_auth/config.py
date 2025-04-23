"""Configuration for Azure AD authentication.

Prioritizes environment variables for settings. Use `configure_azure_auth`
for explicit overrides or if environment variables are not set.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import os


# Define standard environment variable names
ENV_CLIENT_ID = "AZURE_CLIENT_ID"
ENV_CLIENT_SECRET = "AZURE_CLIENT_SECRET"
ENV_TENANT_ID = "AZURE_TENANT_ID"
ENV_SCOPES = "AZURE_AUTH_SCOPES"  # Comma-separated
ENV_LOGIN_REDIRECT_URL = "AZURE_AUTH_LOGIN_REDIRECT_URL"
ENV_POST_LOGOUT_REDIRECT_URI = "AZURE_AUTH_POST_LOGOUT_REDIRECT_URI"
ENV_LOGOUT_ROUTE = "AZURE_AUTH_LOGOUT_ROUTE"
ENV_CALLBACK_ROUTE = "AZURE_AUTH_CALLBACK_ROUTE"

# Default internal routes if not specified
DEFAULT_LOGOUT_ROUTE = "/logout"
DEFAULT_CALLBACK_ROUTE = "/callback"
DEFAULT_LOGIN_REDIRECT = "/"


def _parse_scopes(scopes_str: str | None) -> list[str]:
    """Parses a comma-separated scope string into a list."""
    if not scopes_str:
        return []
    return [scope.strip() for scope in scopes_str.split(",") if scope.strip()]


@dataclass
class AzureAuthConfig:
    """Holds Azure AD application configuration.

    Loads initial values from environment variables.
    """

    client_id: str = field(default_factory=lambda: os.environ.get(ENV_CLIENT_ID, ""))
    client_secret: str = field(
        default_factory=lambda: os.environ.get(ENV_CLIENT_SECRET, "")
    )
    tenant_id: str = field(default_factory=lambda: os.environ.get(ENV_TENANT_ID, ""))
    scopes: list[str] = field(
        default_factory=lambda: _parse_scopes(os.environ.get(ENV_SCOPES))
    )
    login_redirect_url: str = field(
        default_factory=lambda: os.environ.get(
            ENV_LOGIN_REDIRECT_URL, DEFAULT_LOGIN_REDIRECT
        )
    )
    post_logout_redirect_uri: str | None = field(
        default_factory=lambda: os.environ.get(ENV_POST_LOGOUT_REDIRECT_URI)
    )
    logout_route: str = field(
        default_factory=lambda: os.environ.get(ENV_LOGOUT_ROUTE, DEFAULT_LOGOUT_ROUTE)
    )
    callback_route: str = field(
        default_factory=lambda: os.environ.get(ENV_CALLBACK_ROUTE, DEFAULT_CALLBACK_ROUTE)
    )

    # Computed properties
    @property
    def authority(self) -> str:
        """Construct the authority URL from the tenant ID."""
        if not self.tenant_id:
            msg = (
                f"Azure AD Tenant ID is not configured. Set the {ENV_TENANT_ID} "
                "environment variable or call configure_azure_auth()."
            )
            raise ValueError(msg)
        return f"https://login.microsoftonline.com/{self.tenant_id}"

    def is_configured(self) -> bool:
        """Check if essential configuration (ID, Secret, Tenant) is set."""
        return bool(self.client_id and self.client_secret and self.tenant_id)


# --- Module-level Configuration Instance ---
# Initialize the config instance by attempting to load from environment variables
_config = AzureAuthConfig()


# --- Configuration Function (now acts as override) ---
def configure_azure_auth(
    *,
    client_id: str | None = None,
    client_secret: str | None = None,
    tenant_id: str | None = None,
    scopes: list[str] | None = None,
    login_redirect_url: str | None = None,
    post_logout_redirect_uri: str | None = None,
    logout_route: str | None = None,
    callback_route: str | None = None,
):
    """Overrides Azure AD authentication settings loaded from environment variables.

    Call this function during application setup if you need to provide
    configuration programmatically instead of, or in addition to,
    environment variables. Passed values take precedence.

    Environment Variables Used:
        - AZURE_CLIENT_ID: The application (client) ID. (Required)
        - AZURE_CLIENT_SECRET: The application client secret. (Required)
        - AZURE_TENANT_ID: The Azure AD tenant ID. (Required)
        - AZURE_AUTH_SCOPES: Comma-separated list of scopes (e.g., "User.Read,Mail.Read").
        - AZURE_AUTH_LOGIN_REDIRECT_URL: Internal path after login (default: "/").
        - AZURE_AUTH_POST_LOGOUT_REDIRECT_URI: Full URL for Azure AD post-logout redirect.
        - AZURE_AUTH_LOGOUT_ROUTE: Internal path for logout component (default: "/logout")
        - AZURE_AUTH_CALLBACK_ROUTE: Internal path for callback component
                                     (default: "/callback").

    Args:
        client_id: Override AZURE_CLIENT_ID.
        client_secret: Override AZURE_CLIENT_SECRET.
        tenant_id: Override AZURE_TENANT_ID.
        scopes: Override AZURE_AUTH_SCOPES.
        login_redirect_url: Override AZURE_AUTH_LOGIN_REDIRECT_URL.
        post_logout_redirect_uri: Override AZURE_AUTH_POST_LOGOUT_REDIRECT_URI.
        logout_route: Override AZURE_AUTH_LOGOUT_ROUTE.
        callback_route: Override AZURE_AUTH_CALLBACK_ROUTE.
    """
    global _config

    # Update the existing _config instance, prioritizing passed arguments
    if client_id is not None:
        _config.client_id = client_id
    if client_secret is not None:
        _config.client_secret = client_secret
    if tenant_id is not None:
        _config.tenant_id = tenant_id
    if scopes is not None:
        _config.scopes = scopes
    if login_redirect_url is not None:
        _config.login_redirect_url = login_redirect_url
    if post_logout_redirect_uri is not None:
        _config.post_logout_redirect_uri = post_logout_redirect_uri
    if logout_route is not None:
        _config.logout_route = logout_route
    if callback_route is not None:
        _config.callback_route = callback_route


def get_config() -> AzureAuthConfig:
    """Returns the current Azure AD configuration.

    Ensures essential configuration (ID, Secret, Tenant) is present,
    whether loaded from environment variables or set via `configure_azure_auth`.

    Raises:
        RuntimeError: If essential configuration is missing.

    Returns:
        The AzureAuthConfig instance.
    """
    if not _config.is_configured():
        msg = (
            "Azure AD authentication essentials (Client ID, Client Secret, Tenant ID) "
            f"are not configured. Set environment variables ({ENV_CLIENT_ID}, "
            f"{ENV_CLIENT_SECRET}, {ENV_TENANT_ID}) or call "
            "reflexions.azure_auth.configure_azure_auth() before use."
        )
        raise RuntimeError(msg)
    return _config
