from shiny import Inputs, Outputs, Session, module, reactive, ui, App
from shiny_validate import InputValidator, check
from typing import Optional, Callable

# ============================================================
# Module: password
# ============================================================


@module.ui
def password_ui(value=None):
    return [
        ui.input_password("pw1", "Password", value=value),
        ui.input_password("pw2", "Password (confirm)", value=value),
    ]


@module.server
def password_server(
    input: Inputs,
    output: Outputs,
    session: Session,
    required: bool = True,
    password_rule: Optional[Callable] = None,
):
    iv = InputValidator()
    if required:
        iv.add_rule("pw1", check.required())
    iv.add_rule("pw2", lambda x: "Passwords do not match" if x != input.pw1() else None)

    if password_rule is not None:
        iv.add_rule("pw1", password_rule)

    @reactive.Calc
    def val():
        if iv.is_valid():
            return input.pw1

    return (iv, val)


app_ui = ui.page_fluid(
    password_ui("password"),
    ui.input_action_button("submit", "Submit", class_="btn-primary"),
)


def server(input: Inputs, output: Outputs, session: Session):
    def password_validation(pw):
        if not any(char.isdigit() for char in pw) or not any(
            char.isupper() for char in pw
        ):
            return "Must include a number and an upper-case character"
        elif len(pw) < 8:
            return "Must be at least 8 characters"
        else:
            return None

    iv, value = password_server(
        "password",
        True,
        password_rule=password_validation,
    )

    @reactive.effect
    @reactive.event(input.submit)
    def handle_submit():
        iv.enable()
        if iv.is_valid():
            print(value())

    @reactive.Effect
    @reactive.event(input.reset)
    def _():
        print("foo")
        reset_pass()


app = App(app_ui, server)
