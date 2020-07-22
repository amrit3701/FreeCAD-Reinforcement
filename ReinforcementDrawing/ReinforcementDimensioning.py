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

__title__ = "Rebar Dimensioning Object"
__author__ = "Suraj"
__url__ = "https://www.freecadweb.org"


from PySide2.QtCore import QT_TRANSLATE_NOOP
from xml.etree import ElementTree

import FreeCAD
from Draft import getrgb

from .ReinforcementDrawingfunc import getViewPlane, getDrawingMinMaxXY
from .ReinforcementDimensioningfunc import (
    getRebarDimensionLabel,
    getDimensionLineSVG,
    getRebarDimensionData,
)
from SVGfunc import getSVGRootElement


class ReinforcementDimensioning:
    "A Rebar Dimensioning SVG View object."

    def __init__(self, obj_name):
        """Initialize Rebars Dimensioning SVG View object."""
        reinforcement_dimensioning = FreeCAD.ActiveDocument.addObject(
            "TechDraw::DrawViewSymbolPython", obj_name
        )
        self.setProperties(reinforcement_dimensioning)
        self.Object = reinforcement_dimensioning
        reinforcement_dimensioning.Proxy = self

    def setProperties(self, obj):
        """Add properties to RebarDimensioning object."""
        self.Type = "ReinforcementDimensioning"

        if not hasattr(obj, "ParentDrawingView"):
            obj.addProperty(
                "App::PropertyLink",
                "ParentDrawingView",
                "ReinforcementDimensioning",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "The parent ReinforcementDrawingView object.",
                ),
            )

        if not hasattr(obj, "Rebar"):
            obj.addProperty(
                "App::PropertyLink",
                "Rebar",
                "ReinforcementDimensioning",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "The ArchRebar object to generate dimensioning.",
                ),
            )

        if not hasattr(obj, "WayPointsType"):
            obj.addProperty(
                "App::PropertyEnumeration",
                "WayPointsType",
                "ReinforcementDimensioning",
                QT_TRANSLATE_NOOP(
                    "App::Property", "The way points type of dimension line.",
                ),
            ).WayPointsType = ["Automatic", "Custom"]
            obj.WayPointsType = "Custom"

        if not hasattr(obj, "WayPoints"):
            obj.addProperty(
                "App::PropertyVectorList",
                "WayPoints",
                "ReinforcementDimensioning",
                QT_TRANSLATE_NOOP(
                    "App::Property", "The way points of dimension line.",
                ),
            )
            obj.WayPoints = [(0.00, 0.00, 0.00), (50.00, 0.00, 0.00)]

        if not hasattr(obj, "TextPositionType"):
            obj.addProperty(
                "App::PropertyEnumeration",
                "TextPositionType",
                "ReinforcementDimensioning",
                QT_TRANSLATE_NOOP(
                    "App::Property", "The position type of dimension text.",
                ),
            ).TextPositionType = [
                "MidOfLine",
                "StartOfLine",
                "EndOfLine",
            ]

        if not hasattr(obj, "DimensionFormat"):
            obj.addProperty(
                "App::PropertyString",
                "DimensionFormat",
                "ReinforcementDimensioning",
                QT_TRANSLATE_NOOP(
                    "App::Property", "The dimension label format.",
                ),
            )
            obj.DimensionFormat = "%C⌀%D"

        if not hasattr(obj, "Font"):
            obj.addProperty(
                "App::PropertyFont",
                "Font",
                "ReinforcementDimensioning",
                QT_TRANSLATE_NOOP(
                    "App::Property", "The font family of dimension text.",
                ),
            )
            obj.Font = "DejaVu Sans"

        if not hasattr(obj, "FontSize"):
            obj.addProperty(
                "App::PropertyLength",
                "FontSize",
                "ReinforcementDimensioning",
                QT_TRANSLATE_NOOP(
                    "App::Property", "The font size of dimension text.",
                ),
            )
            obj.FontSize = 3

        if not hasattr(obj, "StrokeWidth"):
            obj.addProperty(
                "App::PropertyLength",
                "StrokeWidth",
                "ReinforcementDimensioning",
                QT_TRANSLATE_NOOP(
                    "App::Property", "The stroke width of dimension line.",
                ),
            )
            obj.StrokeWidth = 0.25

        if not hasattr(obj, "LineStyle"):
            obj.addProperty(
                "App::PropertyEnumeration",
                "LineStyle",
                "ReinforcementDimensioning",
                QT_TRANSLATE_NOOP(
                    "App::Property", "The stroke style of dimension line.",
                ),
            ).LineStyle = [
                "Continuous",
                "Dash",
                "Dot",
                "DashDot",
                "DashDotDot",
            ]

        if not hasattr(obj, "LineColor"):
            obj.addProperty(
                "App::PropertyColor",
                "LineColor",
                "ReinforcementDimensioning",
                QT_TRANSLATE_NOOP(
                    "App::Property", "The color of dimension lines.",
                ),
            )
            obj.LineColor = (0.0, 0.0, 0.50)

        if not hasattr(obj, "TextColor"):
            obj.addProperty(
                "App::PropertyColor",
                "TextColor",
                "ReinforcementDimensioning",
                QT_TRANSLATE_NOOP(
                    "App::Property", "The color of dimension text.",
                ),
            )
            obj.TextColor = (0.0, 0.33, 0.0)

        if not hasattr(obj, "LineStartSymbol"):
            obj.addProperty(
                "App::PropertyEnumeration",
                "LineStartSymbol",
                "ReinforcementDimensioning",
                QT_TRANSLATE_NOOP(
                    "App::Property", "The start symbol of dimension line.",
                ),
            ).LineStartSymbol = [
                "FilledArrow",
                "Tick",
                "Dot",
                "None",
            ]
            # TODO: Implement "Open Arrow", "Open Circle" and "Fork"

        if not hasattr(obj, "LineEndSymbol"):
            obj.addProperty(
                "App::PropertyEnumeration",
                "LineEndSymbol",
                "ReinforcementDimensioning",
                QT_TRANSLATE_NOOP(
                    "App::Property", "The end symbol of dimension line.",
                ),
            ).LineEndSymbol = [
                "FilledArrow",
                "Tick",
                "Dot",
                "None",
            ]
            # TODO: Implement "Open Arrow", "Open Circle" and "Fork"

        if not hasattr(obj, "LineMidPointSymbol"):
            obj.addProperty(
                "App::PropertyEnumeration",
                "LineMidPointSymbol",
                "ReinforcementDimensioning",
                QT_TRANSLATE_NOOP(
                    "App::Property", "The mid points symbol of dimension line.",
                ),
            ).LineMidPointSymbol = [
                "Tick",
                "Dot",
                "None",
            ]
            obj.LineMidPointSymbol = "Dot"
            # TODO: Implement "Open Circle" and "Cross"

    def onDocumentRestored(self, obj):
        """Upgrade ReinforcementDimensioning object."""
        self.setProperties(obj)

    def execute(self, obj):
        """This function is executed to recompute ReinforcementDimensioning
        object."""
        if not obj.ParentDrawingView:
            FreeCAD.Console.PrintError(
                "No ParentDrawingView, return without a reinforcement "
                "dimensioning for {}.\n".format(obj.Name)
            )
            return

        if obj.WayPointsType == "Automatic":
            if not obj.Rebar:
                FreeCAD.Console.PrintError(
                    "No Rebar, return without a reinforcement dimensioning for "
                    "{}.\n".format(obj.Name)
                )
                return
            elif obj.Rebar not in obj.ParentDrawingView.Rebars:
                FreeCAD.Console.PrintError(
                    "Rebar is either not visible or not present in "
                    "reinforcement drawing.\n"
                )

        if obj.WayPointsType == "Custom" and len(obj.WayPoints) < 2:
            FreeCAD.Console.PrintError(
                "Empty WayPoints list, return without a reinforcement "
                "dimensioning for {}."
                "\n".format(obj.Name)
            )
            return

        obj.Scale = obj.ParentDrawingView.Scale
        obj.X = obj.ParentDrawingView.X
        obj.Y = obj.ParentDrawingView.Y
        root_svg = getSVGRootElement()

        view_plane = getViewPlane(obj.ParentDrawingView.View)
        min_x, min_y, max_x, max_y = getDrawingMinMaxXY(
            obj.ParentDrawingView.Structure,
            obj.ParentDrawingView.Rebars,
            view_plane,
        )

        if obj.WayPointsType == "Automatic":
            dimension_data_list = getRebarDimensionData(
                obj.Rebar,
                obj.DimensionFormat,
                view_plane,
                obj.ParentDrawingView.DimensionLeftOffset.Value / obj.Scale,
                obj.ParentDrawingView.DimensionRightOffset.Value / obj.Scale,
                obj.ParentDrawingView.DimensionTopOffset.Value / obj.Scale,
                obj.ParentDrawingView.DimensionBottomOffset.Value / obj.Scale,
                min_x,
                min_y,
                max_x,
                max_y,
            )
            for dimension_data in dimension_data_list:
                way_points = dimension_data["WayPoints"]
                dimension_label = dimension_data["DimensionLabel"]
                dimensions_svg = getDimensionLineSVG(
                    [(point.x, point.y) for point in way_points],
                    dimension_label,
                    obj.Font,
                    obj.FontSize.Value / obj.Scale,
                    getrgb(obj.TextColor),
                    obj.TextPositionType,
                    obj.StrokeWidth.Value / obj.Scale,
                    obj.LineStyle,
                    getrgb(obj.LineColor),
                    obj.LineStartSymbol,
                    obj.LineMidPointSymbol,
                    obj.LineEndSymbol,
                )
                # Apply translation so that (0,0) in dimensioning corresponds to
                # (0,0) in ParentDrawingView
                dimensions_svg.set(
                    "transform",
                    "translate({}, {})".format(
                        abs(min(min_x, 0)), abs(min(min_y, 0))
                    ),
                )
                root_svg.append(dimensions_svg)
        else:
            if obj.Rebar:
                dimension_label = getRebarDimensionLabel(
                    obj.Rebar, obj.DimensionFormat
                )
            else:
                dimension_label = obj.DimensionFormat
            dimensions_svg = getDimensionLineSVG(
                [(point.x, point.y) for point in obj.WayPoints],
                dimension_label,
                obj.Font,
                obj.FontSize.Value / obj.Scale,
                getrgb(obj.TextColor),
                obj.TextPositionType,
                obj.StrokeWidth.Value / obj.Scale,
                obj.LineStyle,
                getrgb(obj.LineColor),
                obj.LineStartSymbol,
                obj.LineMidPointSymbol,
                obj.LineEndSymbol,
            )
            # Apply translation so that (0,0) in dimensioning corresponds to
            # (0,0) in ParentDrawingView
            dimensions_svg.set(
                "transform",
                "translate({}, {})".format(
                    abs(min(min_x, 0)), abs(min(min_y, 0))
                ),
            )
            root_svg.append(dimensions_svg)

        # Set svg height and width same as ParentDrawingView
        root_svg.set("width", "{}mm".format(obj.ParentDrawingView.Width.Value))
        root_svg.set(
            "height", "{}mm".format(obj.ParentDrawingView.Height.Value)
        )
        root_svg.set(
            "viewBox",
            "0 0 {} {}".format(
                obj.ParentDrawingView.Width.Value,
                obj.ParentDrawingView.Height.Value,
            ),
        )

        obj.Symbol = ElementTree.tostring(root_svg, encoding="unicode")

        if FreeCAD.GuiUp:
            obj.ViewObject.update()

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None


def makeReinforcementDimensioningObject(parent_drawing_view, drawing_page=None):
    dimension_obj = ReinforcementDimensioning(
        "ReinforcementDimensioning"
    ).Object
    dimension_obj.ParentDrawingView = parent_drawing_view
    if drawing_page:
        drawing_page.addView(dimension_obj)
    return dimension_obj
