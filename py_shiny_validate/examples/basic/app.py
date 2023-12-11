from shiny import Inputs, Outputs, Session, App, render, req, ui
from py_shiny_validate import InputValidator, sv_email, sv_url

app_ui = ui.page_fluid(
    ui.input_text("url", "URL"),
    ui.input_text("email", "Email"),
    ui.output_text_verbatim("txt"),
)


def server(input: Inputs, output: Outputs, session: Session):
    val = InputValidator()
    val.add_rule("url", sv_url())
    val.add_rule("email", sv_email())
    val.enable()

    @render.text
    def txt():
        return f"Hello {input.name()}!"


app = App(app_ui, server)
