# pyright: basic

from py_shiny_validate import py_shiny_validate

from shiny import App, render, ui

app_ui = ui.page_fluid(
    py_shiny_validate("myComponent"),
    ui.output_text("valueOut"),
)


def server(input, output, session):
    @render.text
    def valueOut():
        return f"Value from input is {input.myComponent()}"


app = App(app_ui, server)
