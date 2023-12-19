from shiny import Inputs, Outputs, Session, App, render, req, ui
from shiny_validate import InputValidator, check

app_ui = ui.page_fluid(
    ui.input_text("email", "Email"),
    ui.input_text("name", "Name"),
    ui.output_text_verbatim("txt"),
)


def server(input: Inputs, output: Outputs, session: Session):
    val = InputValidator()
    val.add_rule("email", check.email())
    val.enable()

    @render.text
    def txt():
        if val.is_valid():
            return f"Hello {input.name()}!"


app = App(app_ui, server)
