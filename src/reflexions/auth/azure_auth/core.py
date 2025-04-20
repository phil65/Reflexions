"""Core authentication state and logic using MSAL."""

from __future__ import annotations

import contextlib
from typing import TYPE_CHECKING, Any

import msal
import reflex as rx

from reflexions.auth.azure_auth import config


if TYPE_CHECKING:
    from reflex.event import EventSpec


# In-memory cache for MSAL tokens. Consider a persistent cache for production.
# See MSAL documentation for persistent cache options (e.g., FileSystemTokenCache)
_token_cache = msal.TokenCache()


class SsoState(rx.State):
    """Manages Azure AD authentication state and flow."""

    # Store the raw token claims dictionary
    _token_claims: dict[str, Any] = {}
    # Store the access token (useful for calling APIs like Microsoft Graph)
    _access_token: str = ""
    # Store the MSAL flow details during the auth code exchange
    _flow: dict[str, Any] = {}

    _sso_app_instance: msal.ConfidentialClientApplication | None = None

    def _get_sso_app(self) -> msal.ConfidentialClientApplication:
        """Lazily initializes and returns the MSAL ConfidentialClientApplication."""
        if self._sso_app_instance is None:
            cfg = config.get_config()
            self._sso_app_instance = msal.ConfidentialClientApplication(
                client_id=cfg.client_id,
                client_credential=cfg.client_secret,
                authority=cfg.authority,
                token_cache=_token_cache,
            )
        return self._sso_app_instance

    # --- Public API ---

    @rx.var(cache=True)
    def is_authenticated(self) -> bool:
        """Returns True if the user has a valid ID token."""
        return bool(self._token_claims)

    @rx.var(cache=True)
    def token_claims(self) -> dict[str, Any]:
        """Returns the dictionary of claims from the ID token."""
        return self._token_claims

    @rx.var(cache=True)
    def access_token(self) -> str:
        """Returns the access token (if acquired)."""
        return self._access_token

    @rx.var
    def user_name(self) -> str:
        """Returns the user's display name from the token claims."""
        return self._token_claims.get("name", "")

    @rx.var
    def user_email(self) -> str:
        """Returns the user's email (or UPN) from the token claims."""
        # Common claims: 'preferred_username', 'upn', 'email'
        return self._token_claims.get("preferred_username", "")

    @rx.var
    def user_roles(self) -> list[str]:
        """Returns the user's roles from the token claims (if present)."""
        return self._token_claims.get("roles", [])

    # --- Authentication Flow Methods ---

    def require_auth(self) -> EventSpec | None:
        """Event handler to trigger auth flow if user is not authenticated.

        Use this in `on_load` for pages that require authentication.
        The `authenticated_page` decorator handles this automatically.
        """
        if not self.is_authenticated:
            return self._redirect_to_sso()
        return None  # Explicitly return None if already authenticated

    def _redirect_to_sso(self) -> EventSpec:
        """Initiates the Azure AD authorization code flow."""
        cfg = config.get_config()
        sso_app = self._get_sso_app()

        # Construct the full callback URL dynamically
        # Ensure router state is available (might need adjustment based on context)
        try:
            # Prefer request_url if available for accuracy behind proxies
            base_url = self.router.page.request_url.replace(self.router.page.path, "")
            if base_url.endswith("/"):
                base_url = base_url[:-1]
        except AttributeError:
            # Fallback for environments where request_url might not be populated yet
            # This might be less reliable behind reverse proxies
            base_url = f"{self.router.page.scheme}://{self.router.page.host}"

        callback_uri = f"{base_url}{cfg.callback_route}"
        flow_details = sso_app.initiate_auth_code_flow(
            scopes=cfg.scopes,
            redirect_uri=callback_uri,
        )
        self._flow = flow_details
        return rx.redirect(self._flow["auth_uri"])

    def handle_callback(self) -> EventSpec | None:
        """Handles the redirect back from Azure AD after authentication attempt.

        This should be the `on_load` handler for the callback page.
        The `add_azure_auth_routes` function sets this up automatically.
        """
        cfg = config.get_config()
        sso_app = self._get_sso_app()
        query_params = self.router.page.params
        # Check for errors from Azure AD
        if "error" in query_params:
            error = query_params.get("error")
            error_description = query_params.get("error_description", "Unknown error.")
            err_msg = f"Azure AD login error: {error} - {error_description}"
            print(err_msg)  # Log the error server-side
            # Optionally redirect to an error page or show a toast
            msg = f"Login failed: {error_description}"
            return rx.toast(msg, status="error", duration=5000)

        # Prepare the authorization response for MSAL
        auth_response = {
            "code": query_params.get("code"),
            "client_info": query_params.get("client_info"),
            "state": query_params.get("state"),
            "session_state": query_params.get("session_state"),
        }

        try:
            # Exchange the authorization code for tokens
            result = sso_app.acquire_token_by_auth_code_flow(
                auth_code_flow=self._flow,
                auth_response=auth_response,
                scopes=cfg.scopes,  # Use configured scopes
            )
        except ValueError as e:
            # MSAL often raises ValueError for flow issues (e.g., state mismatch)
            err_msg = f"MSAL token acquisition error: {e}"
            print(err_msg)
            msg = "Login callback error. Please try logging in again."
            return rx.toast(msg, status="error", duration=5000)
        except Exception as e:
            # Catch other potential exceptions during token acquisition
            err_msg = f"Unexpected error during token acquisition: {e}"
            print(err_msg)
            raise RuntimeError(err_msg) from e  # Re-raise for visibility

        # Check if tokens were successfully acquired
        if "error" in result:
            error = result.get("error")
            error_description = result.get(
                "error_description", "Token acquisition failed."
            )
            err_msg = f"Azure AD token error: {error} - {error_description}"
            print(err_msg)
            msg = f"Login failed: {error_description}"
            return rx.toast(msg, status="error", duration=5000)

        # Successfully acquired tokens
        self._access_token = result.get("access_token", "")
        self._token_claims = result.get("id_token_claims", {})
        self._flow = {}  # Clear the flow state
        # Redirect to the configured post-login page
        return rx.redirect(cfg.login_redirect_url)

    def perform_logout(self) -> EventSpec:
        """Clears local session and redirects to Azure AD logout endpoint.

        This should be the `on_load` handler for the logout page.
        The `add_azure_auth_routes` function sets this up automatically.
        """
        cfg = config.get_config()

        # Clear local state first
        self._token_claims = {}
        self._access_token = ""
        self._flow = {}
        # Clear MSAL cache for the current user (find account and remove)
        sso_app = self._get_sso_app()
        accounts = sso_app.get_accounts()
        if accounts:
            with contextlib.suppress(Exception):  # Avoid errors if account removal fails
                sso_app.remove_account(accounts[0])

        # Construct the Azure AD logout URL
        logout_url = f"{cfg.authority}/oauth2/v2.0/logout"
        if cfg.post_logout_redirect_uri:
            # If a post-logout redirect is configured, include it
            logout_url += f"?post_logout_redirect_uri={cfg.post_logout_redirect_uri}"

        return rx.redirect(logout_url)
