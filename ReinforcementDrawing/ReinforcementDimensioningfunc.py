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

__title__ = "Reinforcement Dimensioning Functions"
__author__ = "Suraj"
__url__ = "https://www.freecadweb.org"


from xml.etree import ElementTree

import FreeCAD
import DraftGeomUtils

from .ReinforcementDrawingfunc import getRebarsSpanAxis, getStirrupSVGPoints
from SVGfunc import getSVGTextElement, getLinePathElement


def getPathMidPoint(points_list):
    """getPathMidPoint(PointsList):
    Returns mid point of path defined by points_list.
    """
    import math

    points_dist = [
        math.hypot(p1[0] - p2[0], p1[1] - p2[1])
        for p1, p2 in zip(points_list, points_list[1:])
    ]
    path_length = sum(points_dist)

    for i, point in enumerate(points_list[1:], start=1):
        if int(sum(points_dist[:i])) == int(path_length / 2):
            return point
        elif int(sum(points_dist[:i])) > int(path_length / 2):
            p1 = points_list[i - 1]
            p2 = point
            segment_length = math.hypot(p2[0] - p1[0], p2[1] - p1[1])
            rem_dist = path_length / 2 - sum(points_dist[: i - 1])
            mid_point = (
                p1[0] + (p2[0] - p1[0]) * rem_dist / segment_length,
                p1[1] + (p2[1] - p1[1]) * rem_dist / segment_length,
            )
            return mid_point


def getDimensionLineSVG(
    points_list,
    label,
    font_family,
    font_size,
    label_color,
    label_position_type,
    line_stroke_width,
    line_style,
    line_color,
    line_start_symbol,
    line_mid_points_symbol,
    line_end_symbol,
):
    """getDimensionLineSVG(PointsList, DimensionLabel, FontFamily, FontSize,
    DimensionLabelColor, DimensionLabelPositionType, DimensionLineStrokeWidth,
    DimensionLineStyle, DimensionLineColor, DimensionLineStartSymbol,
    DimensionLineMidPointsSymbol, DimensionLineEndSymbol):
    Return dimension line and label svg.

    points_list is a list of points (x, y) defining line path.

    label_position_type can be "StartOfLine", "MidOfLine" or "EndOfLine".

    line_style can be "Continuous", "Dash", "Dot", "DashDot", "DashDotDot" OR
    stroke-dasharray value for dimension line stroke.

    line_start_symbol/line_end_symbol can be "FilledArrow", "Tick", "Dot" or
    "None".

    line_mid_points_symbol can be "Tick", "Dot" or "None".
    """
    dimension_svg = ElementTree.Element("g")
    line_svg = getLinePathElement(
        points_list,
        line_stroke_width,
        line_style,
        line_color,
        line_start_symbol,
        line_mid_points_symbol,
        line_end_symbol,
    )
    dimension_svg.append(line_svg)

    if label_position_type == "MidOfLine":
        mid_point = getPathMidPoint(points_list)
        label_svg = getSVGTextElement(
            label,
            mid_point[0],
            mid_point[1] - 1,
            font_family,
            font_size,
            "middle",
        )
    elif label_position_type in ("StartOfLine", "EndOfLine"):
        if label_position_type == "StartOfLine":
            p1 = points_list[1]
            p2 = points_list[0]
        else:
            p1 = points_list[-2]
            p2 = points_list[-1]

        if abs(p2[0] - p1[0]) <= abs(p2[1] - p1[1]):
            # Line is more vertical
            if p2[1] - p1[1] < 0:
                # Line is from downward to upward
                label_svg = getSVGTextElement(
                    label, p2[0], p2[1], font_family, font_size, "middle",
                )
            else:
                # Line is from upward to downward
                label_svg = getSVGTextElement(
                    label,
                    p2[0],
                    p2[1] + font_size / 2,
                    font_family,
                    font_size,
                    "middle",
                )
        else:
            # Line is more horizontal
            if p2[0] - p1[0] < 0:
                # Line is from right to left
                label_svg = getSVGTextElement(
                    label,
                    p2[0],
                    p2[1] - 1 + font_size / 2,
                    font_family,
                    font_size,
                    "end",
                )
            else:
                # Line is from left to right
                label_svg = getSVGTextElement(
                    label,
                    p2[0],
                    p2[1] - 1 + font_size / 2,
                    font_family,
                    font_size,
                    "start",
                )
    label_svg.set("fill", label_color)
    dimension_svg.append(label_svg)
    return dimension_svg


def getRebarDimensionLabel(rebar, dimension_format):
    dimension_label = dimension_format.replace("%C", str(rebar.Amount))
    diameter = str(rebar.Diameter.Value)
    if "." in diameter:
        diameter = diameter.rstrip("0").rstrip(".")
    dimension_label = dimension_label.replace("%D", diameter)
    return dimension_label


def getStirrupDimensionData(
    rebar,
    dimension_format,
    view_plane,
    dimension_left_offset,
    dimension_right_offset,
    dimension_top_offset,
    dimension_bottom_offset,
    svg_min_x,
    svg_min_y,
    svg_max_x,
    svg_max_y,
):
    drawing_plane_normal = view_plane.axis
    stirrup_span_axis = getRebarsSpanAxis(rebar)
    if round(drawing_plane_normal.cross(stirrup_span_axis).Length) == 0:
        # TODO: Implement this
        pass
    else:
        if round(stirrup_span_axis.cross(view_plane.u).Length) == 0:
            stirrup_alignment = "V"
        else:
            stirrup_alignment = "H"

        basewire = DraftGeomUtils.filletWire(
            rebar.Base.Shape.Wires[0], rebar.Rounding * rebar.Diameter.Value
        )
        rebar_points = []
        dimension_labels = []
        if rebar.CustomSpacing:
            rebar_diameter = str(rebar.Diameter.Value)
            if "." in rebar_diameter:
                rebar_diameter = rebar_diameter.rstrip("0").rstrip(".")

            start_rebar_index = 0
            for rebar_spacing_str in rebar.CustomSpacing.split("+"):
                startwire = basewire.copy()
                startwire.Placement = rebar.PlacementList[
                    start_rebar_index
                ].multiply(basewire.Placement)
                start_p1, start_p2 = getStirrupSVGPoints(
                    startwire, stirrup_alignment, view_plane
                )

                if "@" in rebar_spacing_str:
                    rebars_count = int(rebar_spacing_str.split("@")[0])
                else:
                    rebars_count = 1

                endwire = basewire.copy()
                endwire.Placement = rebar.PlacementList[
                    start_rebar_index + rebars_count - 1
                ].multiply(basewire.Placement)
                end_p1, end_p2 = getStirrupSVGPoints(
                    endwire, stirrup_alignment, view_plane
                )
                start_rebar_index += rebars_count
                rebar_points.append((start_p1, start_p2, end_p1, end_p2))

                dimension_label = dimension_format.replace(
                    "%C", str(rebars_count)
                )
                dimension_label = dimension_label.replace("%D", rebar_diameter)
                dimension_labels.append(dimension_label)
        else:
            basewire = DraftGeomUtils.filletWire(
                rebar.Base.Shape.Wires[0], rebar.Rounding * rebar.Diameter.Value
            )
            startwire = basewire.copy()
            startwire.Placement = rebar.PlacementList[0].multiply(
                basewire.Placement
            )
            start_p1, start_p2 = getStirrupSVGPoints(
                startwire, stirrup_alignment, view_plane
            )
            endwire = basewire.copy()
            endwire.Placement = rebar.PlacementList[-1].multiply(
                basewire.Placement
            )
            end_p1, end_p2 = getStirrupSVGPoints(
                endwire, stirrup_alignment, view_plane
            )
            rebar_points.append((start_p1, start_p2, end_p1, end_p2))
            dimension_labels.append(
                getRebarDimensionLabel(rebar, dimension_format)
            )

        dimension_data_list = []
        for i, (start_p1, start_p2, end_p1, end_p2) in enumerate(rebar_points):
            if stirrup_alignment == "V":
                if abs(svg_min_y - start_p1.y) < abs(svg_max_y - start_p2.y):
                    # Stirrup is more closer to top of drawing
                    dimension_points = [
                        FreeCAD.Vector(start_p1.x, start_p1.y - 1),
                        FreeCAD.Vector(
                            start_p1.x, svg_min_y - dimension_top_offset
                        ),
                        FreeCAD.Vector(
                            end_p1.x, svg_min_y - dimension_top_offset
                        ),
                        FreeCAD.Vector(end_p1.x, end_p1.y - 1),
                    ]
                    dimension_data_list.append(
                        {
                            "WayPoints": dimension_points,
                            "DimensionLabel": dimension_labels[i],
                        }
                    )
                else:
                    # Stirrup is more closer to bottom of drawing
                    dimension_points = [
                        FreeCAD.Vector(start_p2.x, start_p2.y + 1),
                        FreeCAD.Vector(
                            start_p2.x, svg_max_y + dimension_bottom_offset
                        ),
                        FreeCAD.Vector(
                            end_p2.x, svg_max_y + dimension_bottom_offset
                        ),
                        FreeCAD.Vector(end_p2.x, end_p2.y + 1),
                    ]
                    dimension_data_list.append(
                        {
                            "WayPoints": dimension_points,
                            "DimensionLabel": dimension_labels[i],
                        }
                    )
            else:
                if abs(svg_min_x - start_p1.x) < abs(svg_max_x - start_p2.x):
                    # Stirrup is more closer to left of drawing
                    dimension_points = [
                        FreeCAD.Vector(start_p1.x - 1, start_p1.y),
                        FreeCAD.Vector(
                            svg_min_x - dimension_left_offset, start_p1.y
                        ),
                        FreeCAD.Vector(
                            svg_min_x - dimension_left_offset, end_p1.y
                        ),
                        FreeCAD.Vector(end_p1.x - 1, end_p1.y),
                    ]
                    dimension_data_list.append(
                        {
                            "WayPoints": dimension_points,
                            "DimensionLabel": dimension_labels[i],
                        }
                    )
                else:
                    # Stirrup is more closer to right of drawing
                    dimension_points = [
                        FreeCAD.Vector(start_p2.x + 1, start_p2.y),
                        FreeCAD.Vector(
                            svg_max_x + dimension_right_offset, start_p2.y
                        ),
                        FreeCAD.Vector(
                            svg_max_x + dimension_right_offset, end_p2.y
                        ),
                        FreeCAD.Vector(end_p2.x + 1, end_p2.y),
                    ]
                    dimension_data_list.append(
                        {
                            "WayPoints": dimension_points,
                            "DimensionLabel": dimension_labels[i],
                        }
                    )
        return dimension_data_list


def getRebarDimensionData(
    rebar,
    dimension_format,
    view_plane,
    dimension_left_offset,
    dimension_right_offset,
    dimension_top_offset,
    dimension_bottom_offset,
    svg_min_x,
    svg_min_y,
    svg_max_x,
    svg_max_y,
):
    if rebar.RebarShape == "Stirrup":
        dimension_data = getStirrupDimensionData(
            rebar,
            dimension_format,
            view_plane,
            dimension_left_offset,
            dimension_right_offset,
            dimension_top_offset,
            dimension_bottom_offset,
            svg_min_x,
            svg_min_y,
            svg_max_x,
            svg_max_y,
        )
    return dimension_data
