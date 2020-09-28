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

__title__ = "Reinforcement Drawing View Object"
__author__ = "Suraj"
__url__ = "https://www.freecadweb.org"


from xml.etree import ElementTree
from PySide2.QtCore import QT_TRANSLATE_NOOP

import FreeCAD
from Draft import getrgb

from .ReinforcementDrawingfunc import (
    getViewPlane,
    getSVGWidthHeight,
    getReinforcementDrawingSVGData,
)
from SVGfunc import getTechdrawViewScalingFactor
from .config import (
    DIMENSION_LEFT_OFFSET,
    DIMENSION_RIGHT_OFFSET,
    DIMENSION_TOP_OFFSET,
    DIMENSION_BOTTOM_OFFSET,
)


class ReinforcementDrawingView:
    "A Rebars Drawing SVG View object."

    def __init__(self, obj_name):
        """Initialize ReinforcementDrawingView object."""
        reinforcement_drawing_view = FreeCAD.ActiveDocument.addObject(
            "TechDraw::DrawViewSymbolPython", obj_name
        )
        self.setProperties(reinforcement_drawing_view)
        self.Object = reinforcement_drawing_view
        reinforcement_drawing_view.Proxy = self

    def setProperties(self, obj):
        """Add properties to ReinforcementDrawingView object."""
        self.Type = "ReinforcementDrawingView"

        if not hasattr(obj, "Structure"):
            obj.addProperty(
                "App::PropertyLink",
                "Structure",
                "ReinforcementDrawingView",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "The structure object acting as Host for rebars",
                ),
            )

        if not hasattr(obj, "Rebars"):
            obj.addProperty(
                "App::PropertyLinkList",
                "Rebars",
                "ReinforcementDrawingView",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "The list of rebar objects to be included in drawing",
                ),
            )

        if not hasattr(obj, "View"):
            obj.addProperty(
                "App::PropertyEnumeration",
                "View",
                "ReinforcementDrawingView",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "The reinforcement drawing view",
                ),
            ).View = ["Front", "Rear", "Left", "Right", "Top", "Bottom"]

        if not hasattr(obj, "PositionType"):
            obj.addProperty(
                "App::PropertyEnumeration",
                "PositionType",
                "Base",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "The position type of Reinforcement Drawing on Template",
                ),
            ).PositionType = ["Automatic", "Custom"]
            obj.PositionType = "Automatic"

        if not hasattr(obj, "RebarsStrokeWidth"):
            obj.addProperty(
                "App::PropertyLength",
                "RebarsStrokeWidth",
                "ReinforcementDrawingView",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "The stroke width of rebars in Reinforcement Drawing svg",
                ),
            )
            obj.RebarsStrokeWidth = 0.35

        if not hasattr(obj, "RebarsColorStyle"):
            obj.addProperty(
                "App::PropertyEnumeration",
                "RebarsColorStyle",
                "ReinforcementDrawingView",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "The color style of rebars in Reinforcement Drawing svg",
                ),
            ).RebarsColorStyle = ["Automatic", "Custom"]
            obj.RebarsColorStyle = "Automatic"

        if not hasattr(obj, "RebarsColor"):
            obj.addProperty(
                "App::PropertyColor",
                "RebarsColor",
                "ReinforcementDrawingView",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "The color of rebars in Reinforcement Drawing svg",
                ),
            )
            obj.RebarsColor = (0.67, 0.0, 0.0)

        if not hasattr(obj, "StructureStrokeWidth"):
            obj.addProperty(
                "App::PropertyLength",
                "StructureStrokeWidth",
                "ReinforcementDrawingView",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "The stroke width of structure in Reinforcement Drawing "
                    "svg",
                ),
            )
            obj.StructureStrokeWidth = 0.35

        if not hasattr(obj, "StructureColorStyle"):
            obj.addProperty(
                "App::PropertyEnumeration",
                "StructureColorStyle",
                "ReinforcementDrawingView",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "The color style of structure in Reinforcement Drawing svg",
                ),
            ).StructureColorStyle = ["Automatic", "Custom", "None"]
            obj.StructureColorStyle = "Automatic"

        if not hasattr(obj, "StructureColor"):
            obj.addProperty(
                "App::PropertyColor",
                "StructureColor",
                "ReinforcementDrawingView",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "The color of structure in Reinforcement Drawing svg",
                ),
            )
            obj.StructureColor = (0.3, 0.9, 0.91)

        if not hasattr(obj, "Template"):
            obj.addProperty(
                "App::PropertyLink",
                "Template",
                "ReinforcementDrawingView",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "The template for Reinforcement Drawing view",
                ),
            )

        if not hasattr(obj, "Width"):
            obj.addProperty(
                "App::PropertyLength",
                "Width",
                "ReinforcementDrawingView",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "The width of Reinforcement Drawing view svg",
                ),
                8,
            )
        obj.setEditorMode("Width", 2)

        if not hasattr(obj, "Height"):
            obj.addProperty(
                "App::PropertyLength",
                "Height",
                "ReinforcementDrawingView",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "The height of Reinforcement Drawing view svg",
                ),
                8,
            )
        obj.setEditorMode("Height", 2)

        if not hasattr(obj, "LeftOffset"):
            obj.addProperty(
                "App::PropertyLength",
                "LeftOffset",
                "ReinforcementDrawingView",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "The left offset of Reinforcement Drawing view",
                ),
            )
            obj.LeftOffset = 6

        if not hasattr(obj, "TopOffset"):
            obj.addProperty(
                "App::PropertyLength",
                "TopOffset",
                "ReinforcementDrawingView",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "The top offset of Reinforcement Drawing view",
                ),
            )
            obj.TopOffset = 6

        if not hasattr(obj, "MinRightOffset"):
            obj.addProperty(
                "App::PropertyLength",
                "MinRightOffset",
                "ReinforcementDrawingView",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "The minimum right offset of Reinforcement Drawing view",
                ),
            )
            obj.MinRightOffset = 6

        if not hasattr(obj, "MinBottomOffset"):
            obj.addProperty(
                "App::PropertyLength",
                "MinBottomOffset",
                "ReinforcementDrawingView",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "The minimum bottom offset of Reinforcement Drawing view",
                ),
            )
            obj.MinBottomOffset = 6

        if not hasattr(obj, "MaxWidth"):
            obj.addProperty(
                "App::PropertyLength",
                "MaxWidth",
                "ReinforcementDrawingView",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "The maximum width of Reinforcement Drawing view",
                ),
            )
            obj.MaxWidth = 190

        if not hasattr(obj, "MaxHeight"):
            obj.addProperty(
                "App::PropertyLength",
                "MaxHeight",
                "ReinforcementDrawingView",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "The maximum height of Reinforcement Drawing view",
                ),
            )
            obj.MaxHeight = 250

        if not hasattr(obj, "VisibleRebars"):
            obj.addProperty(
                "App::PropertyLinkList",
                "VisibleRebars",
                "ReinforcementDrawingView",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "The list of visible rebar objects in drawing",
                ),
                8,
            )
        obj.setEditorMode("VisibleRebars", 2)

        # These offsets are used by ReinforcementDimensioning objects to
        # auto-calculate rebars dimension points to align dimension text to
        # left, right, top or bottom line
        if not hasattr(obj, "DimensionLeftOffset"):
            obj.addProperty(
                "App::PropertyLength",
                "DimensionLeftOffset",
                "ReinforcementDimensioning",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "The left offset for each new ReinforcementDimensioning "
                    "object",
                ),
                8,
            )
            obj.DimensionLeftOffset = DIMENSION_LEFT_OFFSET
        obj.setEditorMode("DimensionLeftOffset", 2)

        if not hasattr(obj, "DimensionRightOffset"):
            obj.addProperty(
                "App::PropertyLength",
                "DimensionRightOffset",
                "ReinforcementDimensioning",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "The right offset for each new ReinforcementDimensioning "
                    "object",
                ),
                8,
            )
            obj.DimensionRightOffset = DIMENSION_RIGHT_OFFSET
        obj.setEditorMode("DimensionRightOffset", 2)

        if not hasattr(obj, "DimensionTopOffset"):
            obj.addProperty(
                "App::PropertyLength",
                "DimensionTopOffset",
                "ReinforcementDimensioning",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "The top offset for each new ReinforcementDimensioning "
                    "object",
                ),
                8,
            )
            obj.DimensionTopOffset = DIMENSION_TOP_OFFSET
        obj.setEditorMode("DimensionTopOffset", 2)

        if not hasattr(obj, "DimensionBottomOffset"):
            obj.addProperty(
                "App::PropertyLength",
                "DimensionBottomOffset",
                "ReinforcementDimensioning",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "The bottom offset for each new ReinforcementDimensioning "
                    "object",
                ),
                8,
            )
            obj.DimensionBottomOffset = DIMENSION_BOTTOM_OFFSET
        obj.setEditorMode("DimensionBottomOffset", 2)

    def onDocumentRestored(self, obj):
        """Upgrade ReinforcementDrawing object."""
        self.setProperties(obj)

    def execute(self, obj):
        """This function is executed to recompute ReinforcementDrawing
        object."""
        if not obj.Structure:
            FreeCAD.Console.PrintError(
                "No structure, return without a reinforcement drawing for "
                "{}.\n".format(obj.Name)
            )
            return

        if not obj.Rebars:
            FreeCAD.Console.PrintError(
                "Empty rebars list, return without a reinforcement drawing for "
                "{}.\n".format(obj.Name)
            )
            return

        if obj.PositionType == "Automatic":
            obj.setEditorMode("X", 1)
            obj.setEditorMode("Y", 1)
        else:
            obj.setEditorMode("X", 0)
            obj.setEditorMode("Y", 0)

        view_plane = getViewPlane(obj.View)
        obj.Width, obj.Height = getSVGWidthHeight(
            obj.Structure, obj.Rebars, view_plane
        )

        if obj.ScaleType == "Automatic":
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
            obj.Scale = scaling_factor

        if obj.PositionType == "Automatic":
            obj.X = obj.Width.Value * obj.Scale / 2 + obj.LeftOffset.Value
            obj.Y = (
                obj.Template.Height.Value
                - obj.Height.Value * obj.Scale / 2
                - obj.TopOffset.Value
            )

        if obj.StructureColorStyle == "Automatic":
            if FreeCAD.GuiUp:
                struct_fill_style = "shape color"
            else:
                struct_fill_style = getrgb(obj.StructureColor)
        elif obj.StructureColorStyle == "Custom":
            struct_fill_style = getrgb(obj.StructureColor)
        else:
            struct_fill_style = "none"

        if obj.RebarsColorStyle == "Automatic" and FreeCAD.GuiUp:
            rebars_color_style = "shape color"
        else:
            rebars_color_style = getrgb(obj.RebarsColor)

        reinforcement_drawing_data = getReinforcementDrawingSVGData(
            obj.Structure,
            obj.Rebars,
            view_plane,
            obj.RebarsStrokeWidth.Value / obj.Scale,
            rebars_color_style,
            obj.StructureStrokeWidth.Value / obj.Scale,
            struct_fill_style,
        )
        obj.Symbol = ElementTree.tostring(
            reinforcement_drawing_data["svg"], encoding="unicode"
        )
        obj.VisibleRebars = reinforcement_drawing_data["rebars"]

        if FreeCAD.GuiUp:
            obj.ViewObject.update()

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None


def makeReinforcementDrawingObject(template_file):
    """makeReinforcementDrawingObject(TemplateFile):
    Returns ReinforcementDrawingView object to store reinforcement drawing
    svg.
    """
    drawing_page = FreeCAD.ActiveDocument.addObject("TechDraw::DrawPage")
    template = FreeCAD.ActiveDocument.addObject(
        "TechDraw::DrawSVGTemplate", "Template"
    )
    template.Template = str(template_file)
    drawing_page.Template = template
    reinforcement_drawing_view = ReinforcementDrawingView(
        "ReinforcementDrawingView"
    ).Object
    drawing_page.addView(reinforcement_drawing_view)
    return drawing_page
