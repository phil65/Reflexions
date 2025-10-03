# Reflexions

[![PyPI License](https://img.shields.io/pypi/l/reflexions.svg)](https://pypi.org/project/reflexions/)
[![Package status](https://img.shields.io/pypi/status/reflexions.svg)](https://pypi.org/project/reflexions/)
[![Monthly downloads](https://img.shields.io/pypi/dm/reflexions.svg)](https://pypi.org/project/reflexions/)
[![Distribution format](https://img.shields.io/pypi/format/reflexions.svg)](https://pypi.org/project/reflexions/)
[![Wheel availability](https://img.shields.io/pypi/wheel/reflexions.svg)](https://pypi.org/project/reflexions/)
[![Python version](https://img.shields.io/pypi/pyversions/reflexions.svg)](https://pypi.org/project/reflexions/)
[![Implementation](https://img.shields.io/pypi/implementation/reflexions.svg)](https://pypi.org/project/reflexions/)
[![Releases](https://img.shields.io/github/downloads/phil65/reflexions/total.svg)](https://github.com/phil65/reflexions/releases)
[![Github Contributors](https://img.shields.io/github/contributors/phil65/reflexions)](https://github.com/phil65/reflexions/graphs/contributors)
[![Github Discussions](https://img.shields.io/github/discussions/phil65/reflexions)](https://github.com/phil65/reflexions/discussions)
[![Github Forks](https://img.shields.io/github/forks/phil65/reflexions)](https://github.com/phil65/reflexions/forks)
[![Github Issues](https://img.shields.io/github/issues/phil65/reflexions)](https://github.com/phil65/reflexions/issues)
[![Github Issues](https://img.shields.io/github/issues-pr/phil65/reflexions)](https://github.com/phil65/reflexions/pulls)
[![Github Watchers](https://img.shields.io/github/watchers/phil65/reflexions)](https://github.com/phil65/reflexions/watchers)
[![Github Stars](https://img.shields.io/github/stars/phil65/reflexions)](https://github.com/phil65/reflexions/stars)
[![Github Repository size](https://img.shields.io/github/repo-size/phil65/reflexions)](https://github.com/phil65/reflexions)
[![Github last commit](https://img.shields.io/github/last-commit/phil65/reflexions)](https://github.com/phil65/reflexions/commits)
[![Github release date](https://img.shields.io/github/release-date/phil65/reflexions)](https://github.com/phil65/reflexions/releases)
[![Github language count](https://img.shields.io/github/languages/count/phil65/reflexions)](https://github.com/phil65/reflexions)
[![Github commits this month](https://img.shields.io/github/commit-activity/m/phil65/reflexions)](https://github.com/phil65/reflexions)
[![Package status](https://codecov.io/gh/phil65/reflexions/branch/main/graph/badge.svg)](https://codecov.io/gh/phil65/reflexions/)
[![PyUp](https://pyup.io/repos/github/phil65/reflexions/shield.svg)](https://pyup.io/repos/github/phil65/reflexions/)

[Read the documentation!](https://phil65.github.io/reflexions/)


A collection of ready-to-use components for Reflex applications.

## Components

### Icons
```python
from reflexions import iconify

# Create an icon with customizable properties
iconify("mdi:bell", color="blue", size=24)
iconify("mdi:account", color="red", rotate=90, flip="horizontal")
```

### Loading Animation
```python
from reflexions import loading_icon

# Add a spinning circle loading animation
loading_icon(stroke="#3182CE", speed="0.75")
```

### Template Cards
```python
from reflexions import cards, CardItem

# Create template cards for selection interfaces
templates = [
    CardItem(
        icon="mdi:web",
        title="Website Template",
        description="Basic website with header and footer",
        color="blue",
    ),
    # Add more templates...
]

# Create a responsive grid of cards with an optional click handler
cards(templates, on_click=lambda item: handle_selection(item), cols=3)
```

### Pydantic Forms
```python
from reflexions import pydantic_form
from pydantic import BaseModel, Field

class UserProfile(BaseModel):
    name: str = Field(..., description="Your full name")
    age: int = Field(..., gt=0, description="Your age in years")
    bio: str | None = Field(None, description="Tell us about yourself")

# Generate a complete form with validation from your model
form = pydantic_form(
    UserProfile,
    on_submit=handle_submission,
    submit_label="Save Profile",
)
```
