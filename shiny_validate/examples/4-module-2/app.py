from shiny import Inputs, Outputs, Session, App, reactive, render, ui, module
from shiny_validate import InputValidator, check


@module.ui
def email_ui(label: str = "Email"):
    return ui.input_text("email_address", label)


@module.server
def email_server(
    input: Inputs,
    output: Outputs,
    session: Session,
    required: bool = True,
):
    iv = InputValidator()
    if required:
        iv.add_rule("email_address", check.required())
    iv.add_rule("email_address", check.email())

    return (input.email_address, iv)


app_ui = ui.page_fluid(email_ui("email", "Email Adress"))


def server(input: Inputs, output: Outputs, session: Session):
    email_result, iv = email_server("email")
    iv.enable()


app = App(app_ui, server)
