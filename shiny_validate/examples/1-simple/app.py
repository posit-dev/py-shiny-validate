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
