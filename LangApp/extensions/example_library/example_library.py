
from taipy.gui.extension import Element, ElementLibrary, ElementProperty, PropertyType


class ExampleLibrary(ElementLibrary):
    def __init__(self) -> None:
        # Initialize the set of visual elements for this extension library
        self.elements = {
            "label": Element(
                default_property = "textbody",
                properties = {"textbody": ElementProperty(PropertyType.dynamic_string),
                              "sessionid": ElementProperty(PropertyType.dynamic_string),
                              },
                react_component = "WordSelector",
            ),
        }

    def get_name(self) -> str:
        return "example"

    def get_elements(self) -> dict:
        return self.elements

    def get_scripts(self) -> list[str]:
        # Only one JavaScript bundle for this library.
        return ["front-end/dist/exampleLibrary.js"]
