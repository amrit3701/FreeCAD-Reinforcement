import re
from PySide2.QtCore import QT_TRANSLATE_NOOP
import FreeCAD


class BOMContent:
    "A Rebars Bill of Material SVG Content object."

    def __init__(self, obj_name):
        """Initialize BOMContent object."""
        bom_content = FreeCAD.ActiveDocument.addObject(
            "TechDraw::DrawViewSymbolPython", obj_name
        )
        self.setProperties(bom_content)
        self.Object = bom_content
        bom_content.Proxy = self

    def setProperties(self, obj):
        """Add properties to BOMContent object."""
        self.Type = "BOMContent"
        pl = obj.PropertiesList

        if "Font" not in pl:
            obj.addProperty(
                "App::PropertyFont",
                "Font",
                "BOMContent",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "The font family of Bill of Material content.",
                ),
            )
            obj.Font = "DejaVu Sans"

        if "FontSize" not in pl:
            obj.addProperty(
                "App::PropertyLength",
                "FontSize",
                "BOMContent",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "The font size of Bill of Material content.",
                ),
            )
            obj.FontSize = 3

    def onDocumentRestored(self, obj):
        """Upgrade BOMContent object."""
        self.setProperties(obj)

    def execute(self, obj):
        """This function is executed to recompute BOMContent object."""
        if not obj.Symbol:
            return

        if hasattr(obj, "Font"):
            if obj.Font:
                obj.Symbol = re.sub(
                    'font-family="([^"]+)"',
                    'font-family="{}"'.format(obj.Font),
                    obj.Symbol,
                )
                obj.ViewObject.update()

        if hasattr(obj, "FontSize"):
            if obj.FontSize:
                obj.Symbol = re.sub(
                    'font-size="([^"]+)"',
                    'font-size="{}"'.format(obj.FontSize.Value),
                    obj.Symbol,
                )
                obj.ViewObject.update()

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None


def makeBOMObject(template_file=None):
    """Create BillOfMaterial object to store BOM svg."""
    bom_object = FreeCAD.ActiveDocument.addObject(
        "TechDraw::DrawPage", "BOM_object"
    )
    if template_file:
        template = FreeCAD.ActiveDocument.addObject(
            "TechDraw::DrawSVGTemplate", "Template"
        )
        template.Template = str(template_file)
        bom_object.Template = template
    bom_content = BOMContent("BOM_content").Object
    bom_object.addView(bom_content)
    FreeCAD.ActiveDocument.recompute()
    return bom_object
