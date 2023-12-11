from htmltools import HTMLDependency
from pathlib import PurePath

html_deps = HTMLDependency(
    "py_shiny_validate",
    "1.0.0",
    source={
        "package": "py_shiny_validate",
        "subdir": str(PurePath(__file__).parent / "distjs"),
    },
    script={"src": "index.js", "type": "module"},
)
