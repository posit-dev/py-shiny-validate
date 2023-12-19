from shiny import Inputs, Outputs, Session, App, module, ui, reactive
from shiny_validate import InputValidator, check


@module.ui
def contact_us_ui():
    return ui.input_action_button("contact_us", "Contact us", class_="btn-sm")


@module.server
def contact_us_server(input: Inputs, output: Outputs, session: Session):
    iv = InputValidator()
    iv.add_rule("email", check.required())
    iv.add_rule("email", check.email())
    iv.add_rule("message", check.required())
    iv.add_rule(
        "message",
        lambda x: f"Maximum length exceeded by {len(x) - 140}"
        if len(x) > 140
        else None,
    )

    @reactive.effect
    @reactive.event(input.contact_us)
    def contact_modal():
        m = ui.modal(
            ui.input_text("email", "Your email"),
            ui.input_text_area("message", "Message", rows=4),
            ui.layout_columns(
                ui.input_action_button(
                    "send",
                    "Send Email",
                    class_="btn-primary",
                ),
            ),
            title="Contact form",
            easy_close=False,
        )
        ui.modal_show(m)

    @reactive.effect
    @reactive.event(input.send)
    def _():
        iv.enable()
        if iv.is_valid():
            ui.notification_show("Message (not really) sent", duration=2)


app_ui = ui.page_fluid(contact_us_ui("contact"))


def server(input: Inputs, output: Outputs, session: Session):
    contact_us_server("contact")


app = App(app_ui, server)
