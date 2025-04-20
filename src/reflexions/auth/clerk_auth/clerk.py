from __future__ import annotations

import os

import reflex as rx
import reflex_clerk_api as clerk


def index() -> rx.Component:
    return clerk.clerk_provider(
        clerk.clerk_loading(rx.spinner()),
        clerk.clerk_loaded(
            clerk.signed_in(clerk.sign_out_button(rx.button("Sign out"))),
            clerk.signed_out(clerk.sign_in_button(rx.button("Sign in"))),
        ),
        publishable_key=os.environ["CLERK_PUBLISHABLE_KEY"],
        secret_key=os.environ["CLERK_SECRET_KEY"],
        register_user_state=True,
    )


def register_pages(app: rx.App):
    app.add_page(index)
    clerk.add_sign_in_page(app)
    clerk.add_sign_up_page(app)
