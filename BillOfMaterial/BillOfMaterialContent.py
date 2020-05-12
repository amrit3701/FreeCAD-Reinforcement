import re
from PySide2.QtCore import QT_TRANSLATE_NOOP
import FreeCAD

from .BOMfunc import getBOMScalingFactor


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

        if "Template" not in pl:
            obj.addProperty(
                "App::PropertyLink",
                "Template",
                "BOMContent",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "The template for Bill of Material content.",
                ),
            )

        if "Width" not in pl:
            obj.addProperty(
                "App::PropertyLength",
                "Width",
                "BOMContent",
                QT_TRANSLATE_NOOP(
                    "App::Property", "The width of Bill of Material content.",
                ),
            )
        obj.setEditorMode("Width", 2)

        if "Height" not in pl:
            obj.addProperty(
                "App::PropertyLength",
                "Height",
                "BOMContent",
                QT_TRANSLATE_NOOP(
                    "App::Property", "The height of Bill of Material content.",
                ),
            )
        obj.setEditorMode("Height", 2)

        if "LeftOffset" not in pl:
            obj.addProperty(
                "App::PropertyLength",
                "LeftOffset",
                "BOMContent",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "The left offset of Bill of Material content.",
                ),
            )
            obj.LeftOffset = 6

        if "TopOffset" not in pl:
            obj.addProperty(
                "App::PropertyLength",
                "TopOffset",
                "BOMContent",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "The top offset of Bill of Material content.",
                ),
            )
            obj.TopOffset = 6

        if "MinRightOffset" not in pl:
            obj.addProperty(
                "App::PropertyLength",
                "MinRightOffset",
                "BOMContent",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "The minimum right offset of Bill of Material content.",
                ),
            )
            obj.MinRightOffset = 6

        if "MinBottomOffset" not in pl:
            obj.addProperty(
                "App::PropertyLength",
                "MinBottomOffset",
                "BOMContent",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "The minimum bottom offset of Bill of Material content.",
                ),
            )
            obj.MinBottomOffset = 6

        if "MaxWidth" not in pl:
            obj.addProperty(
                "App::PropertyLength",
                "MaxWidth",
                "BOMContent",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "The maximum width of Bill of Material content.",
                ),
            )
            obj.MaxWidth = 190

        if "MaxHeight" not in pl:
            obj.addProperty(
                "App::PropertyLength",
                "MaxHeight",
                "BOMContent",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "The maximum height of Bill of Material content.",
                ),
            )
            obj.MaxHeight = 250

    def onDocumentRestored(self, obj):
        """Upgrade BOMContent object."""
        self.setProperties(obj)

    def execute(self, obj):
        """This function is executed to recompute BOMContent object."""
        if not obj.Symbol:
            return

        if obj.Font:
            obj.Symbol = re.sub(
                'font-family="([^"]+)"',
                'font-family="{}"'.format(obj.Font),
                obj.Symbol,
            )
            obj.ViewObject.update()

        if obj.FontSize:
            obj.Symbol = re.sub(
                'font-size="([^"]+)"',
                'font-size="{}"'.format(obj.FontSize.Value),
                obj.Symbol,
            )
            obj.ViewObject.update()

        if obj.Width and obj.Height and obj.Template:
            scaling_factor = getBOMScalingFactor(
                obj.Width.Value,
                obj.Height.Value,
                obj.LeftOffset.Value,
                obj.TopOffset.Value,
                obj.Template.Width.Value,
                obj.Template.Height.Value,
                obj.MinRightOffset.Value,
                obj.MinBottomOffset.Value,
                obj.MaxWidth.Value,
                obj.MaxHeight.Value,
            )
            obj.X = obj.Width.Value * scaling_factor / 2 + obj.LeftOffset.Value
            obj.Y = (
                obj.Template.Height.Value
                - obj.Height.Value * scaling_factor / 2
                - obj.TopOffset.Value
            )
            obj.Scale = scaling_factor
            obj.ViewObject.update()

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None


def makeBOMObject(template_file):
    """Create BillOfMaterial object to store BOM svg."""
    bom_object = FreeCAD.ActiveDocument.addObject(
        "TechDraw::DrawPage", "BOM_object"
    )
    template = FreeCAD.ActiveDocument.addObject(
        "TechDraw::DrawSVGTemplate", "Template"
    )
    template.Template = str(template_file)
    bom_object.Template = template
    bom_content = BOMContent("BOM_content").Object
    bom_object.addView(bom_content)
    FreeCAD.ActiveDocument.recompute()
    return bom_object
