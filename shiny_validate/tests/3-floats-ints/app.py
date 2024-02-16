from shiny_validate import InputValidator, check

from shiny import App, ui

app_ui = ui.page_fixed(ui.input_numeric("age", "Age", 1))


def server(input, output, session):
    iv = InputValidator()
    iv.add_rule("age", check.required())
    iv.enable()


app = App(app_ui, server)
