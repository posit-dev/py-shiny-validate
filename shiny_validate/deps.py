from htmltools import HTMLDependency
from pathlib import PurePath

html_deps = HTMLDependency(
    "shiny_validate",
    "1.0.0",
    source={
        "package": "shiny_validate",
        "subdir": str(PurePath(__file__).parent / "distjs"),
    },
    script={"src": "index.js", "type": "module"},
)
