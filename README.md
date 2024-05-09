# shiny_validate

## Overview

This is a python implementation of [shinyvalidate](https://rstudio.github.io/shinyvalidate/), which provides input validation for [Shiny for Python](https://shiny.posit.co/py/) applications.

## Installation

Install from Pypi with:

```
pip install shiny_validate
```

Or, you can install the latest development version from GitHub using the `remotes` package.

```
pip install git+https://github.com/posit-dev/py-shiny-validate.git
```

## Basic usage

To add validation to your Shiny app, you need to:

1.  Create an InputValidator object: `iv <- InputValidator`

2.  Add one or more validation rules to the InputValidator: `iv.add_rule("title", check.required())`

3.  Turn the validator on: `iv$enable()`

That's all you need to do to get validation messages to show up.

```python
from shiny import App, ui, render, req
from shiny_validate import InputValidator, check

app_ui = ui.page_fluid(
    ui.input_text("name", "Name"),
    ui.input_text("email", "Email"),
    ui.output_text("greeting"),
)


def server(input, output, session):
    iv = InputValidator()

    iv.add_rule("name", check.required())
    iv.add_rule("email", check.required())
    iv.add_rule("email", check.email())
    iv.enable()

    @render.text
    def greeting():
        req(iv.is_valid())
        return f"Nice to meet you, {input.name()} <{input.email()}>!"


app = App(app_ui, server)
```
