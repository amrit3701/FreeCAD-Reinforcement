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


from xml.etree import ElementTree

import FreeCAD
QT_TRANSLATE_NOOP = FreeCAD.Qt.QT_TRANSLATE_NOOP
from Draft import getrgb

from RebarData import RebarTypes
from .ReinforcementDrawingfunc import getViewPlane, getDrawingMinMaxXY
from .ReinforcementDimensioningfunc import (
    getRebarDimensionLabel,
    getDimensionLineSVG,
    getRebarDimensionData,
)
from SVGfunc import getSVGRootElement, getSVGTextElement
from .config import (
    DIMENSION_LABEL_FORMAT,
    DIMENSION_FONT_FAMILY,
    DIMENSION_FONT_SIZE,
    DIMENSION_STROKE_WIDTH,
    DIMENSION_LINE_STYLE,
    DIMENSION_LINE_COLOR,
    DIMENSION_TEXT_COLOR,
    DIMENSION_SINGLE_REBAR_LINE_START_SYMBOL,
    DIMENSION_SINGLE_REBAR_LINE_END_SYMBOL,
    DIMENSION_MULTI_REBAR_LINE_START_SYMBOL,
    DIMENSION_LINE_MID_POINT_SYMBOL,
    DIMENSION_MULTI_REBAR_LINE_END_SYMBOL,
    DIMENSION_LEFT_OFFSET_INCREMENT,
    DIMENSION_RIGHT_OFFSET_INCREMENT,
    DIMENSION_TOP_OFFSET_INCREMENT,
    DIMENSION_BOTTOM_OFFSET_INCREMENT,
    DIMENSION_SINGLE_REBAR_OUTER_DIM,
    DIMENSION_MULTI_REBAR_OUTER_DIM,
    DIMENSION_SINGLE_REBAR_TEXT_POSITION_TYPE,
    DIMENSION_MULTI_REBAR_TEXT_POSITION_TYPE,
)


class ReinforcementDimensioning:
    """A Rebar Dimensioning SVG View object."""

    def __init__(
        self,
        rebar,
        parent_drawing_view,
        dimension_left_offset_increment,
        dimension_right_offset_increment,
        dimension_top_offset_increment,
        dimension_bottom_offset_increment,
        obj_name="ReinforcementDimensioning",
    ):
        """Initialize Rebars Dimensioning SVG View object."""
        reinforcement_dimensioning = FreeCAD.ActiveDocument.addObject(
            "TechDraw::DrawViewSymbolPython", obj_name
        )
        self.setProperties(reinforcement_dimensioning)
        self.Object = reinforcement_dimensioning
        reinforcement_dimensioning.Proxy = self

        reinforcement_dimensioning.Rebar = rebar
        reinforcement_dimensioning.ParentDrawingView = parent_drawing_view

        # Set dimension MinMax values from parent ReinforcementDrawingView
        # object
        reinforcement_dimensioning.DimensionLeftOffset = (
            parent_drawing_view.DimensionLeftOffset
        )
        reinforcement_dimensioning.DimensionRightOffset = (
            parent_drawing_view.DimensionRightOffset
        )
        reinforcement_dimensioning.DimensionTopOffset = (
            parent_drawing_view.DimensionTopOffset
        )
        reinforcement_dimensioning.DimensionBottomOffset = (
            parent_drawing_view.DimensionBottomOffset
        )

        # This will be used to increment
        # ParentDrawing.DimensionLeft/Right/Top/Bottom offset as required only
        # first time when object is being recomputed
        self.FirstExecute = True
        self.DimensionLeftOffsetIncrement = dimension_left_offset_increment
        self.DimensionRightOffsetIncrement = dimension_right_offset_increment
        self.DimensionTopOffsetIncrement = dimension_top_offset_increment
        self.DimensionBottomOffsetIncrement = dimension_bottom_offset_increment
        reinforcement_dimensioning.recompute(True)
        parent_drawing_view.recompute(True)

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
                    "The parent ReinforcementDrawingView object",
                ),
            )

        if not hasattr(obj, "Rebar"):
            obj.addProperty(
                "App::PropertyLink",
                "Rebar",
                "ReinforcementDimensioning",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "The ArchRebar object to generate dimensioning",
                ),
            )

        if not hasattr(obj, "WayPointsType"):
            obj.addProperty(
                "App::PropertyEnumeration",
                "WayPointsType",
                "ReinforcementDimensioning",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "The way points type of dimension line",
                ),
            ).WayPointsType = ["Automatic", "Custom"]

        if not hasattr(obj, "WayPoints"):
            obj.addProperty(
                "App::PropertyVectorList",
                "WayPoints",
                "ReinforcementDimensioning",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "The way points of dimension line",
                ),
            )
            obj.WayPoints = [(0.00, 0.00, 0.00), (50.00, 0.00, 0.00)]

        if not hasattr(obj, "TextPositionType"):
            obj.addProperty(
                "App::PropertyEnumeration",
                "TextPositionType",
                "ReinforcementDimensioning",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "The position type of dimension text",
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
                    "App::Property",
                    "The dimension label format",
                ),
            )
            obj.DimensionFormat = DIMENSION_LABEL_FORMAT

        if not hasattr(obj, "Font"):
            obj.addProperty(
                "App::PropertyFont",
                "Font",
                "ReinforcementDimensioning",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "The font family of dimension text",
                ),
            )
            obj.Font = DIMENSION_FONT_FAMILY

        if not hasattr(obj, "FontSize"):
            obj.addProperty(
                "App::PropertyLength",
                "FontSize",
                "ReinforcementDimensioning",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "The font size of dimension text",
                ),
            )
            obj.FontSize = DIMENSION_FONT_SIZE

        if not hasattr(obj, "StrokeWidth"):
            obj.addProperty(
                "App::PropertyLength",
                "StrokeWidth",
                "ReinforcementDimensioning",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "The stroke width of dimension line",
                ),
            )
            obj.StrokeWidth = DIMENSION_STROKE_WIDTH

        if not hasattr(obj, "LineStyle"):
            obj.addProperty(
                "App::PropertyEnumeration",
                "LineStyle",
                "ReinforcementDimensioning",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "The stroke style of dimension line",
                ),
            ).LineStyle = [
                "Continuous",
                "Dash",
                "Dot",
                "DashDot",
                "DashDotDot",
            ]
            obj.LineStyle = DIMENSION_LINE_STYLE

        if not hasattr(obj, "LineColor"):
            obj.addProperty(
                "App::PropertyColor",
                "LineColor",
                "ReinforcementDimensioning",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "The color of dimension line",
                ),
            )
            obj.LineColor = DIMENSION_LINE_COLOR

        if not hasattr(obj, "TextColor"):
            obj.addProperty(
                "App::PropertyColor",
                "TextColor",
                "ReinforcementDimensioning",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "The color of dimension text",
                ),
            )
            obj.TextColor = DIMENSION_TEXT_COLOR

        if not hasattr(obj, "LineStartSymbol"):
            obj.addProperty(
                "App::PropertyEnumeration",
                "LineStartSymbol",
                "ReinforcementDimensioning",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "The start symbol of dimension line",
                ),
            ).LineStartSymbol = [
                "FilledArrow",
                "Tick",
                "Dot",
                "None",
            ]
            # TODO: Implement "Open Arrow", "Open Circle" and "Fork"
            obj.LineStartSymbol = DIMENSION_SINGLE_REBAR_LINE_START_SYMBOL

        if not hasattr(obj, "LineEndSymbol"):
            obj.addProperty(
                "App::PropertyEnumeration",
                "LineEndSymbol",
                "ReinforcementDimensioning",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "The end symbol of dimension line",
                ),
            ).LineEndSymbol = [
                "FilledArrow",
                "Tick",
                "Dot",
                "None",
            ]
            # TODO: Implement "Open Arrow", "Open Circle" and "Fork"
            obj.LineEndSymbol = DIMENSION_SINGLE_REBAR_LINE_END_SYMBOL

        if not hasattr(obj, "LineMidPointSymbol"):
            obj.addProperty(
                "App::PropertyEnumeration",
                "LineMidPointSymbol",
                "ReinforcementDimensioning",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "The mid points symbol of dimension line",
                ),
            ).LineMidPointSymbol = [
                "Tick",
                "Dot",
                "None",
            ]
            obj.LineMidPointSymbol = DIMENSION_LINE_MID_POINT_SYMBOL
            # TODO: Implement "Open Circle" and "Cross"

        if not hasattr(obj, "DimensionLeftOffset"):
            obj.addProperty(
                "App::PropertyLength",
                "DimensionLeftOffset",
                "AutomaticDimensioning",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "The left offset for automated reinforcement dimensioning",
                ),
            )

        if not hasattr(obj, "DimensionRightOffset"):
            obj.addProperty(
                "App::PropertyLength",
                "DimensionRightOffset",
                "AutomaticDimensioning",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "The right offset for automated reinforcement "
                    "dimensioning",
                ),
            )

        if not hasattr(obj, "DimensionTopOffset"):
            obj.addProperty(
                "App::PropertyLength",
                "DimensionTopOffset",
                "AutomaticDimensioning",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "The top offset for automated reinforcement dimensioning",
                ),
            )

        if not hasattr(obj, "DimensionBottomOffset"):
            obj.addProperty(
                "App::PropertyLength",
                "DimensionBottomOffset",
                "AutomaticDimensioning",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "The bottom offset for automated reinforcement "
                    "dimensioning",
                ),
            )

        if not hasattr(obj, "SingleRebar_LineStartSymbol"):
            obj.addProperty(
                "App::PropertyEnumeration",
                "SingleRebar_LineStartSymbol",
                "AutomaticDimensioning",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "The dimension line start symbol, in case of single rebar "
                    "is visible",
                ),
            ).SingleRebar_LineStartSymbol = [
                "FilledArrow",
                "Tick",
                "Dot",
                "None",
            ]
            obj.SingleRebar_LineStartSymbol = (
                DIMENSION_SINGLE_REBAR_LINE_START_SYMBOL
            )

        if not hasattr(obj, "SingleRebar_LineEndSymbol"):
            obj.addProperty(
                "App::PropertyEnumeration",
                "SingleRebar_LineEndSymbol",
                "AutomaticDimensioning",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "The dimension line end symbol, in case of single rebar is "
                    "visible",
                ),
            ).SingleRebar_LineEndSymbol = [
                "FilledArrow",
                "Tick",
                "Dot",
                "None",
            ]
            obj.SingleRebar_LineEndSymbol = (
                DIMENSION_SINGLE_REBAR_LINE_END_SYMBOL
            )

        if not hasattr(obj, "MultiRebar_LineStartSymbol"):
            obj.addProperty(
                "App::PropertyEnumeration",
                "MultiRebar_LineStartSymbol",
                "AutomaticDimensioning",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "The dimension line start symbol, in case of multiple "
                    "rebars are visible",
                ),
            ).MultiRebar_LineStartSymbol = [
                "FilledArrow",
                "Tick",
                "Dot",
                "None",
            ]
            obj.MultiRebar_LineStartSymbol = (
                DIMENSION_MULTI_REBAR_LINE_START_SYMBOL
            )

        if not hasattr(obj, "MultiRebar_LineEndSymbol"):
            obj.addProperty(
                "App::PropertyEnumeration",
                "MultiRebar_LineEndSymbol",
                "AutomaticDimensioning",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "The dimension line end symbol, in case of multiple rebars "
                    "are visible",
                ),
            ).MultiRebar_LineEndSymbol = [
                "FilledArrow",
                "Tick",
                "Dot",
                "None",
            ]
            obj.MultiRebar_LineEndSymbol = DIMENSION_MULTI_REBAR_LINE_END_SYMBOL

        if not hasattr(obj, "SingleRebar_OuterDimension"):
            obj.addProperty(
                "App::PropertyBool",
                "SingleRebar_OuterDimension",
                "AutomaticDimensioning",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "True if dimension lines to be outside of reinforcement "
                    "drawing for automated reinforcement dimensioning, "
                    "in case of single rebar is visible",
                ),
            )
            obj.SingleRebar_OuterDimension = DIMENSION_SINGLE_REBAR_OUTER_DIM

        if not hasattr(obj, "MultiRebar_OuterDimension"):
            obj.addProperty(
                "App::PropertyBool",
                "MultiRebar_OuterDimension",
                "AutomaticDimensioning",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "True if dimension lines to be outside of reinforcement "
                    "drawing for automated reinforcement dimensioning, "
                    "in case of multiple rebars are visible",
                ),
            )
            obj.MultiRebar_OuterDimension = DIMENSION_MULTI_REBAR_OUTER_DIM

        if not hasattr(obj, "SingleRebar_TextPositionType"):
            obj.addProperty(
                "App::PropertyEnumeration",
                "SingleRebar_TextPositionType",
                "AutomaticDimensioning",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "The position type of dimension text, in case of single "
                    "rebar is visible",
                ),
            ).SingleRebar_TextPositionType = [
                "MidOfLine",
                "StartOfLine",
                "EndOfLine",
            ]
            obj.SingleRebar_TextPositionType = (
                DIMENSION_SINGLE_REBAR_TEXT_POSITION_TYPE
            )

        if not hasattr(obj, "MultiRebar_TextPositionType"):
            obj.addProperty(
                "App::PropertyEnumeration",
                "MultiRebar_TextPositionType",
                "AutomaticDimensioning",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "The position type of dimension text, in case of multiple "
                    "rebars are visible",
                ),
            ).MultiRebar_TextPositionType = [
                "MidOfLine",
                "StartOfLine",
                "EndOfLine",
            ]
            obj.MultiRebar_TextPositionType = (
                DIMENSION_MULTI_REBAR_TEXT_POSITION_TYPE
            )

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
            elif obj.Rebar not in obj.ParentDrawingView.VisibleRebars:
                FreeCAD.Console.PrintError(
                    "Rebar is either not visible or not present in "
                    "reinforcement drawing.\n"
                )
                return
            elif not hasattr(obj.Rebar, "RebarShape"):
                FreeCAD.Console.PrintError(
                    "Unable to find rebar shape type. Automatic dimensioning "
                    "is not supported for custom rebars.\n"
                )
                return
            elif obj.Rebar.RebarShape not in RebarTypes.tolist():
                FreeCAD.Console.PrintError(
                    "Unsupported rebar type {}. Automatic dimensioning is only "
                    "supported for: {}\n".format(
                        obj.Rebar.RebarShape, ", ".join(RebarTypes.tolist())
                    )
                )
                return

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
            dimension_data_list, dimension_align = getRebarDimensionData(
                obj.Rebar,
                obj.DimensionFormat,
                view_plane,
                obj.DimensionLeftOffset.Value / obj.Scale,
                obj.DimensionRightOffset.Value / obj.Scale,
                obj.DimensionTopOffset.Value / obj.Scale,
                obj.DimensionBottomOffset.Value / obj.Scale,
                min_x,
                min_y,
                max_x,
                max_y,
                obj.Scale,
                obj.SingleRebar_OuterDimension,
                obj.MultiRebar_OuterDimension,
            )
            if hasattr(self, "FirstExecute") and self.FirstExecute is True:
                self.FirstExecute = False
                parent_drawing = obj.ParentDrawingView
                if dimension_align == "Left":
                    parent_drawing.DimensionLeftOffset.Value += (
                        self.DimensionLeftOffsetIncrement
                    )
                elif dimension_align == "Right":
                    parent_drawing.DimensionRightOffset.Value += (
                        self.DimensionRightOffsetIncrement
                    )
                elif dimension_align == "Top":
                    parent_drawing.DimensionTopOffset.Value += (
                        self.DimensionTopOffsetIncrement
                    )
                elif dimension_align == "Bottom":
                    parent_drawing.DimensionBottomOffset.Value += (
                        self.DimensionBottomOffsetIncrement
                    )
            for dimension_data in dimension_data_list:
                if (
                    "LabelOnly" in dimension_data
                    and dimension_data["LabelOnly"] is True
                ):
                    dimensions_svg = getSVGTextElement(
                        dimension_data["DimensionLabel"],
                        dimension_data["LabelPosition"].x,
                        dimension_data["LabelPosition"].y,
                        obj.Font,
                        obj.FontSize.Value / obj.Scale,
                        "middle",
                    )
                    dimensions_svg.set("fill", getrgb(obj.TextColor))
                else:
                    way_points = dimension_data["WayPoints"]
                    dimension_label = dimension_data["DimensionLabel"]
                    if dimension_data["VisibleRebars"] == "Single":
                        line_start_symbol = obj.SingleRebar_LineStartSymbol
                        line_end_symbol = obj.SingleRebar_LineEndSymbol
                        text_position_type = obj.SingleRebar_TextPositionType
                    elif dimension_data["VisibleRebars"] == "Multiple":
                        line_start_symbol = obj.MultiRebar_LineStartSymbol
                        line_end_symbol = obj.MultiRebar_LineEndSymbol
                        text_position_type = obj.MultiRebar_TextPositionType

                    dimensions_svg = getDimensionLineSVG(
                        [(point.x, point.y) for point in way_points],
                        dimension_label,
                        obj.Font,
                        obj.FontSize.Value / obj.Scale,
                        getrgb(obj.TextColor),
                        text_position_type,
                        obj.StrokeWidth.Value / obj.Scale,
                        obj.LineStyle,
                        getrgb(obj.LineColor),
                        line_start_symbol,
                        obj.LineMidPointSymbol,
                        line_end_symbol,
                    )

                # Apply translation so that (0,0) in dimensioning corresponds to
                # (0,0) in ParentDrawingView
                dimensions_svg.set(
                    "transform",
                    "translate({}, {})".format(-min_x, -min_y),
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
                "translate({}, {})".format(-min_x, -min_y),
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


def makeReinforcementDimensioningObject(
    rebar,
    parent_drawing_view,
    drawing_page=None,
    dimension_label_format=DIMENSION_LABEL_FORMAT,
    dimension_font_family=DIMENSION_FONT_FAMILY,
    dimension_font_size=DIMENSION_FONT_SIZE,
    dimension_stroke_width=DIMENSION_STROKE_WIDTH,
    dimension_line_style=DIMENSION_LINE_STYLE,
    dimension_line_color=DIMENSION_LINE_COLOR,
    dimension_text_color=DIMENSION_TEXT_COLOR,
    dimension_single_rebar_line_start_symbol=(
        DIMENSION_SINGLE_REBAR_LINE_START_SYMBOL
    ),
    dimension_single_rebar_line_end_symbol=(
        DIMENSION_SINGLE_REBAR_LINE_END_SYMBOL
    ),
    dimension_multi_rebar_line_start_symbol=(
        DIMENSION_MULTI_REBAR_LINE_START_SYMBOL
    ),
    dimension_multi_rebar_line_end_symbol=(
        DIMENSION_MULTI_REBAR_LINE_END_SYMBOL
    ),
    dimension_line_mid_point_symbol=DIMENSION_LINE_MID_POINT_SYMBOL,
    dimension_left_offset_increment=DIMENSION_LEFT_OFFSET_INCREMENT,
    dimension_right_offset_increment=DIMENSION_RIGHT_OFFSET_INCREMENT,
    dimension_top_offset_increment=DIMENSION_TOP_OFFSET_INCREMENT,
    dimension_bottom_offset_increment=DIMENSION_BOTTOM_OFFSET_INCREMENT,
    dimension_single_rebar_outer_dim=DIMENSION_SINGLE_REBAR_OUTER_DIM,
    dimension_multi_rebar_outer_dim=DIMENSION_MULTI_REBAR_OUTER_DIM,
    dimension_single_rebar_text_position_type=(
        DIMENSION_SINGLE_REBAR_TEXT_POSITION_TYPE
    ),
    dimension_multi_rebar_text_position_type=(
        DIMENSION_MULTI_REBAR_TEXT_POSITION_TYPE
    ),
):
    dimension_obj = ReinforcementDimensioning(
        rebar,
        parent_drawing_view,
        dimension_left_offset_increment,
        dimension_right_offset_increment,
        dimension_top_offset_increment,
        dimension_bottom_offset_increment,
        "ReinforcementDimensioning",
    ).Object
    dimension_obj.Label = ""
    dimension_obj.DimensionFormat = dimension_label_format
    dimension_obj.Font = dimension_font_family
    dimension_obj.FontSize = dimension_font_size
    dimension_obj.StrokeWidth = dimension_stroke_width
    dimension_obj.LineStyle = dimension_line_style
    dimension_obj.LineColor = dimension_line_color
    dimension_obj.TextColor = dimension_text_color
    dimension_obj.SingleRebar_LineStartSymbol = (
        dimension_single_rebar_line_start_symbol
    )
    dimension_obj.SingleRebar_LineEndSymbol = (
        dimension_single_rebar_line_end_symbol
    )
    dimension_obj.MultiRebar_LineStartSymbol = (
        dimension_multi_rebar_line_start_symbol
    )
    dimension_obj.MultiRebar_LineEndSymbol = (
        dimension_multi_rebar_line_end_symbol
    )
    dimension_obj.LineMidPointSymbol = dimension_line_mid_point_symbol
    dimension_obj.SingleRebar_OuterDimension = dimension_single_rebar_outer_dim
    dimension_obj.MultiRebar_OuterDimension = dimension_multi_rebar_outer_dim
    dimension_obj.SingleRebar_TextPositionType = (
        dimension_single_rebar_text_position_type
    )
    dimension_obj.MultiRebar_TextPositionType = (
        dimension_multi_rebar_text_position_type
    )
    if drawing_page:
        drawing_page.addView(dimension_obj)
        drawing_page.recompute(True)
    return dimension_obj
