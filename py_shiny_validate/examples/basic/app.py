from shiny import Inputs, Outputs, Session, App, render, req, ui
from py_shiny_validate import InputValidator, sv_email, html_deps, sv_required

app_ui = ui.page_fluid(
    html_deps,
    # ui.input_text("url", "URL"),
    ui.input_text("email", "Email"),
    ui.input_text("name", "Name"),
    ui.output_text_verbatim("txt"),
)


def server(input: Inputs, output: Outputs, session: Session):
    val = InputValidator(session=session)
    val.add_rule("email", sv_email())
    val.enable()

    @render.text
    def txt():
        if val.is_valid():
            return f"Hello {input.name()}!"


app = App(app_ui, server)
