from shiny import Inputs, Outputs, Session, App, reactive, render, req, ui
from shiny_validate import InputValidator, check

app_ui = ui.page_fluid(
    ui.input_text("name", "Name:"),
    ui.input_text("email", "Email:"),
    ui.input_checkbox_group(
        "topics",
        "Topics (choose two or more): *",
        choices=[
            "Statistics",
            "Machine learning",
            "Visualization",
            "Programming",
        ],
    ),
    ui.input_checkbox("accept_terms", "I accept the terms and conditions"),
    ui.input_action_button("submit", "Submit", class_="btn-primary"),
    ui.input_action_button("reset", "Reset"),
)


def server(input: Inputs, output: Outputs, session: Session):
    iv = InputValidator()
    iv.add_rule("name", check.required())
    iv.add_rule("email", check.required())
    iv.add_rule("email", check.email())
    iv.add_rule(
        "topics", lambda x: "Please choose two or more topics" if len(x) < 2 else None
    )
    iv.add_rule("accept_terms", check.required())
    iv.add_rule(
        "accept_terms",
        lambda x: "The terms and conditions must be accepted" if not x else None,
    )

    @reactive.effect
    @reactive.event(input.submit)
    def submit_form():
        if iv.is_valid():
            reset_form()
            m = ui.modal(
                "Form submitted successfully", title="Success!", easy_close=True
            )
            ui.modal_show(m)
        else:
            iv.enable()
            ui.notification_show(
                "Please correct errors in the form and try again", duration=4
            )

    @reactive.effect
    @reactive.event(input.reset)
    def _():
        reset_form()

    def reset_form():
        iv.disable()
        ui.update_text("name", value="")
        ui.update_text("email", value="")
        ui.update_checkbox_group("topics", selected=[])
        ui.update_checkbox("accept_terms", value=False)


app = App(app_ui, server)
