"""Model selector component for Reflex applications."""

from __future__ import annotations

from collections.abc import Callable, Sequence  # noqa: TC003
from typing import Any

import reflex as rx
import reflex_chakra as rc
from tokonomics.model_discovery import ModelInfo, ProviderType, get_all_models


ModelName = str


# --- State Class (Corrected Syntax) ---
class ModelSelectorState(rx.State):
    """State for the model selector component."""

    models: list[Any] = []
    available_providers: list[str] = []
    provider_models: list[Any] = []
    model_names: list[str] = []
    selected_provider: str = ""
    selected_model_name: str = ""
    selected_model: ModelInfo | None = None
    is_expanded: bool = True
    is_loading: bool = False
    _external_on_model_change: Callable[[str], None] | None = None

    @rx.var
    def selected_model_formatted(self) -> str:
        """Return the formatted string for the selected model, or empty."""
        if self.selected_model:
            return self.selected_model.format()
        return ""

    @rx.var
    def show_provider_selector(self) -> bool:
        """Determine if the provider selector should be shown."""
        return len(self.available_providers) > 1

    @rx.var
    def show_model_selector(self) -> bool:
        """Determine if the model selector should be shown."""
        return len(self.models) > 0 and not self.is_loading

    @rx.var
    def show_no_models_message(self) -> bool:
        """Determine if the 'no models' message should be shown."""
        return (
            self.selected_provider != ""
            and len(self.model_names) == 0
            and not self.is_loading
        )

    @rx.var
    def show_details_expander(self) -> bool:
        """Determine if the details expander should be shown."""
        return self.selected_model_name != ""

    @rx.event(background=True)
    async def load_initial_data(
        self,
        initial_model_id: str | None,
        providers: Sequence[ProviderType] | None = None,
        expanded: bool = True,
        on_model_change_callback: Callable[[str], None] | None = None,
    ):
        """Load models asynchronously and initialize state."""
        if self.is_loading:
            return

        async with self:
            self.is_loading = True
            self.models = []
            self.available_providers = []
            self.provider_models = []
            self.model_names = []
            self.selected_provider = ""
            self.selected_model_name = ""
            self.selected_model = None
            self.is_expanded = expanded
            self._external_on_model_change = on_model_change_callback

        try:
            fetched_models = await get_all_models(providers=providers)

            async with self:
                self.models = fetched_models
                self.available_providers = sorted({m.provider for m in self.models})

                current_model_id = initial_model_id
                current_model = None
                current_provider = None

                if current_model_id:
                    current_model = next(
                        (m for m in self.models if m.pydantic_ai_id == current_model_id),
                        None,
                    )
                    if current_model:
                        current_provider = current_model.provider

                # Determine initial provider
                if self.available_providers:
                    if current_provider in self.available_providers:
                        self.selected_provider = current_provider
                    else:
                        self.selected_provider = self.available_providers[0]
                    self._update_provider_models()
                elif self.models:
                    self.selected_provider = self.models[0].provider
                    self._update_provider_models()

                # Determine initial model selection
                if current_model and current_model.provider == self.selected_provider:
                    self.selected_model_name = current_model.name
                    self._update_selected_model()
                elif self.model_names:
                    self.selected_model_name = self.model_names[0]
                    self._update_selected_model()
                    if (
                        self.selected_model
                        and self._external_on_model_change
                        and self.selected_model.pydantic_ai_id != initial_model_id
                    ):
                        self._external_on_model_change(self.selected_model.pydantic_ai_id)
                else:
                    self.selected_model_name = ""
                    self.selected_model = None

        except Exception as e:  # noqa: BLE001
            # Corrected formatting
            print(f"Error loading models: {e}")
            async with self:
                self.models = []
                self.available_providers = []
                self.provider_models = []
                self.model_names = []
                self.selected_provider = ""
                self.selected_model_name = ""
                self.selected_model = None
        finally:
            # Corrected formatting
            async with self:
                self.is_loading = False

    def on_provider_change(self, provider: str):
        """Handle provider change."""
        # Corrected formatting
        self.selected_provider = provider
        self._update_provider_models()

        selected_model_id: str | None = None
        if self.model_names:
            self.selected_model_name = self.model_names[0]
            self._update_selected_model()
            if self.selected_model:
                selected_model_id = self.selected_model.pydantic_ai_id
        else:
            self.selected_model_name = ""
            self.selected_model = None

        if selected_model_id and self._external_on_model_change:
            self._external_on_model_change(selected_model_id)

    def on_model_change(self, model_name: str):
        """Handle model change."""
        # Corrected formatting
        self.selected_model_name = model_name
        self._update_selected_model()

        if self.selected_model and self._external_on_model_change:
            self._external_on_model_change(self.selected_model.pydantic_ai_id)

    def toggle_expanded(self):
        """Toggle expanded state."""
        self.is_expanded = not self.is_expanded

    def _update_provider_models(self):
        """Update models based on selected provider."""
        self.provider_models = [
            m for m in self.models if m.provider == self.selected_provider
        ]
        self.model_names = sorted([m.name for m in self.provider_models])

    def _update_selected_model(self):
        """Update selected model based on selected name."""
        self.selected_model = next(
            (m for m in self.provider_models if m.name == self.selected_model_name), None
        )


# --- Component Function (Grid approach - unchanged from last attempt) ---
def model_selector(
    *,
    initial_model_id: ModelName | None = None,
    providers: Sequence[ProviderType] | None = None,
    expanded: bool = True,
    on_model_change: Callable[[ModelName], None] | None = None,
) -> rx.Component:
    """Render a model selector widget in a 2x2 grid layout.

    Ensures dropdowns expand to fill available space.

    Args:
        initial_model_id: The pydantic_ai_id of the initially selected model.
        providers: List of providers to show models from.
        expanded: Whether to expand the model details by default.
        on_model_change: Callback triggered with the selected model's
                         pydantic_ai_id when the selection changes.

    Returns:
        Reflex component for model selection.
    """
    return rx.card(
        rx.vstack(
            # Heading
            rx.hstack(
                rx.heading("Model Selection", size="4"),
                rx.cond(ModelSelectorState.is_loading, rx.spinner(size="2")),
                align_items="center",
                width="100%",
                justify_content="space-between",
                mb="3",
            ),
            # Explicit 2-Column Grid
            rx.grid(
                # --- Row 1 ---
                # Provider Label Cell
                rx.cond(
                    ModelSelectorState.show_provider_selector,
                    rc.form_label(
                        "Provider:",
                        align_self="center",
                        justify_self="start",
                        html_for="provider-select",
                        white_space="nowrap",
                    ),
                    rx.box(),  # Placeholder if provider selector hidden
                ),
                # Provider Select Cell
                rx.cond(
                    ModelSelectorState.show_provider_selector,
                    rx.select(
                        ModelSelectorState.available_providers,
                        value=ModelSelectorState.selected_provider,
                        on_change=ModelSelectorState.on_provider_change,  # type: ignore
                        placeholder="Select provider",
                        is_disabled=ModelSelectorState.is_loading,
                        id="provider-select",
                        width="100%",  # Crucial: Make select fill its grid cell
                    ),
                    rx.box(),  # Placeholder if provider selector hidden
                ),
                # --- Row 2 ---
                # Model Label Cell
                rx.cond(
                    ModelSelectorState.show_model_selector,
                    rc.form_label(
                        "Model:",
                        align_self="center",
                        justify_self="start",
                        html_for="model-select",
                        white_space="nowrap",
                    ),
                    rx.box(),  # Placeholder if model selector hidden
                ),
                # Model Select Cell
                rx.cond(
                    ModelSelectorState.show_model_selector,
                    rx.select(
                        ModelSelectorState.model_names,
                        value=ModelSelectorState.selected_model_name,
                        on_change=ModelSelectorState.on_model_change,  # type: ignore
                        placeholder="Select model",
                        is_disabled=ModelSelectorState.is_loading,
                        id="model-select",
                        width="100%",  # Crucial: Make select fill its grid cell
                    ),
                    rx.box(),  # Placeholder if model selector hidden generally
                ),
                # Grid configuration
                template_columns="auto 1fr",  # Label width auto, select takes rest (1fr)
                row_gap=2,
                column_gap=3,  # Space between label and select
                align_items="center",
                width="100%",  # Ensure grid itself takes full width
                mb="2",
            ),
            # Message if no models
            rx.cond(
                ModelSelectorState.show_no_models_message,
                rx.text(
                    "No models available for this provider.",
                    size="2",
                    color_scheme="gray",
                    mt="1",
                    padding_left="calc(var(--chakra-sizes-20) + var(--chakra-space-3))",
                ),
            ),
            # Model details expander (remains the same)
            rx.cond(
                ModelSelectorState.show_details_expander,
                rx.vstack(
                    rx.hstack(
                        rx.heading("Model Details", size="2", color_scheme="gray"),
                        rx.spacer(),
                        rx.button(
                            rx.cond(
                                ModelSelectorState.is_expanded,
                                rx.icon(tag="chevron-up"),
                                rx.icon(tag="chevron-down"),
                            ),
                            variant="ghost",
                            size="2",
                            on_click=ModelSelectorState.toggle_expanded,  # type: ignore
                            is_disabled=ModelSelectorState.is_loading,
                        ),
                        width="100%",
                        align_items="center",
                        py="1",
                    ),
                    rx.cond(
                        ModelSelectorState.is_expanded,
                        rx.box(
                            rx.markdown(ModelSelectorState.selected_model_formatted),
                            background_color=rx.color("mauve", 2),
                            padding="3",
                            border_radius="md",
                            width="100%",
                        ),
                    ),
                    padding_top="2",
                    width="100%",
                    align_items="stretch",
                ),
            ),
            # on_mount etc.
            on_mount=lambda: ModelSelectorState.load_initial_data(
                initial_model_id, providers, expanded, on_model_change
            ),
            width="100%",
            align_items="stretch",
            spacing="2",
        ),
        width="100%",
        size="2",
    )
