from __future__ import annotations

from contextlib import contextmanager
from typing import TYPE_CHECKING, Self
import uuid

import reflex as rx


if TYPE_CHECKING:
    from collections.abc import Generator


class MultiTabsState(rx.State):
    """State for multiple independent tab groups."""

    active_tabs: dict[str, str] = {}

    @rx.event
    def switch_tab(self, group_id: str, tab_id: str) -> None:
        """Switch the active tab for a specific tab group."""
        self.active_tabs[group_id] = tab_id

    @rx.event
    def ensure_default_tab(self, group_id: str, default_tab_id: str):
        """Sets the default tab only if the group doesn't exist in the state yet."""
        if group_id not in self.active_tabs:
            self.active_tabs[group_id] = default_tab_id


class TabGroup:
    """Represents a group of tabs with Streamlit-like API."""

    def __init__(self, flow_instance: ReflexFlow, tab_names: list[str]):
        """Initialize a new tab group with a unique ID."""
        self.id = str(uuid.uuid4())
        self.flow = flow_instance
        self.tab_names: list[str] = tab_names
        self.tab_contents: dict[str, list[rx.Component]] = {
            name: [] for name in tab_names
        }
        self._current_defining_tab: str | None = None

        # Ensure the default active tab exists in the state
        if self.tab_names:
            MultiTabsState.ensure_default_tab(self.id, self.tab_names[0])

    @contextmanager
    def tab(self, tab_name: str) -> Generator[None, None, None]:
        """Context manager to define content for a specific tab."""
        if tab_name not in self.tab_names:
            msg = f"Tab '{tab_name}' is not defined in this group."
            raise ValueError(msg)
        original_tab = self._current_defining_tab
        self._current_defining_tab = tab_name
        self.flow._set_current_tab_group(self)
        yield
        self._current_defining_tab = original_tab
        self.flow._set_current_tab_group(None)

    def add_component(self, component: rx.Component) -> None:
        """Add a component to the tab currently being defined."""
        if self._current_defining_tab is None:
            msg = "Cannot add component outside of a 'with tab_group.tab(...):' block."
            raise RuntimeError(msg)
        self.tab_contents[self._current_defining_tab].append(component)

    def render(self) -> rx.Component:
        """Render the tab group as a Reflex component."""
        tab_triggers = []
        group_id_local = self.id
        for name in self.tab_names:
            # Use default argument capture for the lambda
            trigger = rx.tabs.trigger(
                name,
                value=name,
                on_click=lambda captured_name=name: MultiTabsState.switch_tab(
                    group_id_local, captured_name
                ),
            )
            tab_triggers.append(trigger)

        tab_panels = []
        for name in self.tab_names:
            content_list = self.tab_contents.get(name, [])
            panel_content = (
                rx.vstack(*content_list, align_items="start", spacing="3")
                if content_list
                else rx.fragment()
            )
            tab_panels.append(rx.tabs.content(panel_content, value=name))

        default_value = self.tab_names[0] if self.tab_names else ""
        active_tab_value_var = MultiTabsState.active_tabs.get(self.id, default_value)

        return rx.tabs.root(
            rx.tabs.list(*tab_triggers),
            *tab_panels,
            value=active_tab_value_var,
            default_value=default_value,
            # on_value_change=...,
        )


class ReflexFlow:
    """Provides a Streamlit-like flow API for Reflex."""

    def __init__(self):
        self._current_tab_group: TabGroup | None = None

    def _set_current_tab_group(self, tab_group: TabGroup | None):
        self._current_tab_group = tab_group

    def create_tab_group(self, tab_names: list[str]) -> TabGroup:
        return TabGroup(self, tab_names)

    def __iadd__(self, component: rx.Component) -> Self:
        self.add_component(component)
        return self

    def add_component(self, component: rx.Component):
        if self._current_tab_group is None:
            msg = "Component added outside of a 'with tab_group.tab(...):' context."
            raise RuntimeError(msg)
        self._current_tab_group.add_component(component)


flow = ReflexFlow()
