# -*- coding: utf-8 -*-
# ***************************************************************************
# *                                                                         *
# *   Copyright (c) 2020 - Suraj <dadralj18@gmail.com>                      *
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the GNU Lesser General Public License (LGPL)    *
# *   as published by the Free Software Foundation; either version 2 of     *
# *   the License, or (at your option) any later version.                   *
# *   for detail see the LICENCE text file.                                 *
# *                                                                         *
# *   This program is distributed in the hope that it will be useful,       *
# *   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
# *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
# *   GNU Library General Public License for more details.                  *
# *                                                                         *
# *   You should have received a copy of the GNU Library General Public     *
# *   License along with this program; if not, write to the Free Software   *
# *   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
# *   USA                                                                   *
# *                                                                         *
# ***************************************************************************

__title__ = "Reinforcement Drawing Content Object"
__author__ = "Suraj"
__url__ = "https://www.freecadweb.org"


import re
from PySide2.QtCore import QT_TRANSLATE_NOOP
import FreeCAD

from SVGfunc import getTechdrawViewScalingFactor


class ReinforcementDrawingContent:
    "A Rebars Drawing SVG Content object."

    def __init__(self, obj_name):
        """Initialize ReinforcementDrawingContent object."""
        reinforcement_drawing_content = FreeCAD.ActiveDocument.addObject(
            "TechDraw::DrawViewSymbolPython", obj_name
        )
        self.setProperties(reinforcement_drawing_content)
        self.Object = reinforcement_drawing_content
        reinforcement_drawing_content.Proxy = self

    def setProperties(self, obj):
        """Add properties to ReinforcementDrawingContent object."""
        self.Type = "ReinforcementDrawingContent"

        if not hasattr(obj, "Font"):
            obj.addProperty(
                "App::PropertyFont",
                "Font",
                "ReinforcementDrawingContent",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "The font family of text in Reinforcement Drawing content.",
                ),
            )
            obj.Font = "DejaVu Sans"

        if not hasattr(obj, "FontSize"):
            obj.addProperty(
                "App::PropertyLength",
                "FontSize",
                "ReinforcementDrawingContent",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "The font size of text in Reinforcement Drawing content.",
                ),
            )
            obj.FontSize = 3

        if not hasattr(obj, "Template"):
            obj.addProperty(
                "App::PropertyLink",
                "Template",
                "ReinforcementDrawingContent",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "The template for Reinforcement Drawing content.",
                ),
            )

        if not hasattr(obj, "Width"):
            obj.addProperty(
                "App::PropertyLength",
                "Width",
                "ReinforcementDrawingContent",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "The width of Reinforcement Drawing content.",
                ),
            )
        obj.setEditorMode("Width", 2)

        if not hasattr(obj, "Height"):
            obj.addProperty(
                "App::PropertyLength",
                "Height",
                "ReinforcementDrawingContent",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "The height of Reinforcement Drawing content.",
                ),
            )
        obj.setEditorMode("Height", 2)

        if not hasattr(obj, "LeftOffset"):
            obj.addProperty(
                "App::PropertyLength",
                "LeftOffset",
                "ReinforcementDrawingContent",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "The left offset of Reinforcement Drawing content.",
                ),
            )
            obj.LeftOffset = 6

        if not hasattr(obj, "TopOffset"):
            obj.addProperty(
                "App::PropertyLength",
                "TopOffset",
                "ReinforcementDrawingContent",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "The top offset of Reinforcement Drawing content.",
                ),
            )
            obj.TopOffset = 6

        if not hasattr(obj, "MinRightOffset"):
            obj.addProperty(
                "App::PropertyLength",
                "MinRightOffset",
                "ReinforcementDrawingContent",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "The minimum right offset of Reinforcement Drawing "
                    "content.",
                ),
            )
            obj.MinRightOffset = 6

        if not hasattr(obj, "MinBottomOffset"):
            obj.addProperty(
                "App::PropertyLength",
                "MinBottomOffset",
                "ReinforcementDrawingContent",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "The minimum bottom offset of Reinforcement Drawing "
                    "content.",
                ),
            )
            obj.MinBottomOffset = 6

        if not hasattr(obj, "MaxWidth"):
            obj.addProperty(
                "App::PropertyLength",
                "MaxWidth",
                "ReinforcementDrawingContent",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "The maximum width of Reinforcement Drawing content.",
                ),
            )
            obj.MaxWidth = 190

        if not hasattr(obj, "MaxHeight"):
            obj.addProperty(
                "App::PropertyLength",
                "MaxHeight",
                "ReinforcementDrawingContent",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "The maximum height of Reinforcement Drawing content.",
                ),
            )
            obj.MaxHeight = 250

    def onDocumentRestored(self, obj):
        """Upgrade ReinforcementDrawing object."""
        self.setProperties(obj)

    def execute(self, obj):
        """This function is executed to recompute ReinforcementDrawing
        object."""
        if not obj.Symbol:
            return

        if obj.Font:
            obj.Symbol = re.sub(
                'font-family="([^"]+)"',
                'font-family="{}"'.format(obj.Font),
                obj.Symbol,
            )

        if obj.FontSize:
            obj.Symbol = re.sub(
                'font-size="([^"]+)"',
                'font-size="{}"'.format(obj.FontSize.Value),
                obj.Symbol,
            )

        if obj.Width and obj.Height and obj.Template:
            scaling_factor = getTechdrawViewScalingFactor(
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
        if FreeCAD.GuiUp:
            obj.ViewObject.update()

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None


def makeReinforcementDrawingObject(template_file):
    """makeReinforcementDrawingObject(TemplateFile):
    Returns ReinforcementDrawing_content object to store reinforcement drawing
    svg.
    """
    drawing_page = FreeCAD.ActiveDocument.addObject("TechDraw::DrawPage")
    template = FreeCAD.ActiveDocument.addObject(
        "TechDraw::DrawSVGTemplate", "Template"
    )
    template.Template = str(template_file)
    drawing_page.Template = template
    reinforcement_drawing_content = ReinforcementDrawingContent(
        "ReinforcementDrawing_content"
    ).Object
    drawing_page.addView(reinforcement_drawing_content)
    FreeCAD.ActiveDocument.recompute()
    return drawing_page
