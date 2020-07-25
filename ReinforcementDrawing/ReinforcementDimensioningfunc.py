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


import math
from xml.etree import ElementTree

import FreeCAD
import DraftGeomUtils
import DraftVecUtils

from .ReinforcementDrawingfunc import (
    getProjectionToSVGPlane,
    getRebarsSpanAxis,
    getStirrupSVGPoints,
)
from SVGfunc import getSVGTextElement, getLinePathElement


def getPathMidPoint(points_list, return_left_right_points=False):
    """getPathMidPoint(PointsList, [ReturnLeftRightPoints]):
    Returns mid point of path defined by points_list.

    if return_left_right_points is True, then left and right points of mid_point
    are also returned: (left_point, mid_point, right_point)
    """
    import math

    points_dist = [
        math.hypot(p1[0] - p2[0], p1[1] - p2[1])
        for p1, p2 in zip(points_list, points_list[1:])
    ]
    path_length = sum(points_dist)

    for i, point in enumerate(points_list[1:], start=1):
        if int(sum(points_dist[:i])) == int(path_length / 2):
            if return_left_right_points:
                return (points_list[i - 1], point, points_list[i + 1])
            else:
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
            if return_left_right_points:
                return (p1, mid_point, p2)
            else:
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
        left_point, mid_point, right_point = getPathMidPoint(
            points_list, return_left_right_points=True
        )
        label_svg = getSVGTextElement(
            label,
            mid_point[0],
            mid_point[1] - line_stroke_width * 2,
            font_family,
            font_size,
            "middle",
        )
        if DraftVecUtils.isColinear(
            [
                FreeCAD.Vector(left_point[0], left_point[1], 0),
                FreeCAD.Vector(mid_point[0], mid_point[1], 0),
                FreeCAD.Vector(right_point[0], right_point[1], 0),
            ]
        ):
            label_svg.set(
                "transform",
                "rotate({} {} {})".format(
                    math.degrees(
                        math.atan(
                            (right_point[1] - left_point[1])
                            / (right_point[0] - left_point[0])
                        )
                    )
                    if right_point[0] - left_point[0] != 0
                    else -90,
                    mid_point[0],
                    mid_point[1],
                ),
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
                    p2[1] + font_size / 2,
                    font_family,
                    font_size,
                    "end",
                )
            else:
                # Line is from left to right
                label_svg = getSVGTextElement(
                    label,
                    p2[0],
                    p2[1] + font_size / 2,
                    font_family,
                    font_size,
                    "start",
                )
    label_svg.set("fill", label_color)
    dimension_svg.append(label_svg)
    return dimension_svg


def getRebarDimensionLabel(rebar, dimension_format):
    dimension_label = dimension_format.replace("%M", str(rebar.Mark))
    dimension_label = dimension_label.replace("%C", str(rebar.Amount))
    diameter = str(rebar.Diameter.Value)
    if "." in diameter:
        diameter = diameter.rstrip("0").rstrip(".")
    dimension_label = dimension_label.replace("%D", diameter).strip()
    return dimension_label


def getStirrupDimensionData(
    rebar,
    dimension_format,
    view_plane,
    dimension_left_offset_point,
    dimension_right_offset_point,
    dimension_top_offset_point,
    dimension_bottom_offset_point,
    svg_min_x,
    svg_min_y,
    svg_max_x,
    svg_max_y,
):
    drawing_plane_normal = view_plane.axis
    stirrup_span_axis = getRebarsSpanAxis(rebar)
    if round(drawing_plane_normal.cross(stirrup_span_axis).Length) == 0:
        import Part

        edges = Part.__sortEdges__(rebar.Base.Shape.Edges)
        mid_edge = edges[round(len(edges) / 2)]
        mid_point = getProjectionToSVGPlane(
            DraftGeomUtils.findMidpoint(mid_edge), view_plane
        )
        return [
            {
                "LabelPosition": mid_point,
                "LabelOnly": True,
                "DimensionLabel": getRebarDimensionLabel(
                    rebar, dimension_format
                ),
            }
        ]
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
                    "%M", str(rebar.Mark)
                )
                dimension_label = dimension_label.replace(
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
                        FreeCAD.Vector(start_p1.x, start_p1.y - 5),
                        FreeCAD.Vector(
                            start_p1.x, svg_min_y - dimension_top_offset_point.y
                        ),
                        FreeCAD.Vector(
                            end_p1.x, svg_min_y - dimension_top_offset_point.y
                        ),
                        FreeCAD.Vector(end_p1.x, end_p1.y - 5),
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
                        FreeCAD.Vector(start_p2.x, start_p2.y + 5),
                        FreeCAD.Vector(
                            start_p2.x,
                            svg_max_y + dimension_bottom_offset_point.y,
                        ),
                        FreeCAD.Vector(
                            end_p2.x,
                            svg_max_y + dimension_bottom_offset_point.y,
                        ),
                        FreeCAD.Vector(end_p2.x, end_p2.y + 5),
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
                        FreeCAD.Vector(start_p1.x - 5, start_p1.y),
                        FreeCAD.Vector(
                            svg_min_x - dimension_left_offset_point.x,
                            start_p1.y,
                        ),
                        FreeCAD.Vector(
                            svg_min_x - dimension_left_offset_point.x, end_p1.y
                        ),
                        FreeCAD.Vector(end_p1.x - 5, end_p1.y),
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
                        FreeCAD.Vector(start_p2.x + 5, start_p2.y),
                        FreeCAD.Vector(
                            svg_max_x + dimension_right_offset_point.x,
                            start_p2.y,
                        ),
                        FreeCAD.Vector(
                            svg_max_x + dimension_right_offset_point.x, end_p2.y
                        ),
                        FreeCAD.Vector(end_p2.x + 5, end_p2.y),
                    ]
                    dimension_data_list.append(
                        {
                            "WayPoints": dimension_points,
                            "DimensionLabel": dimension_labels[i],
                        }
                    )
        return dimension_data_list


def getStraightRebarDimensionData(
    rebar,
    dimension_format,
    view_plane,
    dimension_left_offset_point,
    dimension_right_offset_point,
    dimension_top_offset_point,
    dimension_bottom_offset_point,
    svg_min_x,
    svg_min_y,
    svg_max_x,
    svg_max_y,
):
    drawing_plane_normal = view_plane.axis
    rebar_span_axis = getRebarsSpanAxis(rebar)
    # Straight rebars span axis is parallel to drawing plane normal
    # Thus, only one rebar will be visible
    if round(drawing_plane_normal.cross(rebar_span_axis).Length) == 0:
        p1 = getProjectionToSVGPlane(
            rebar.Base.Shape.Wires[0].Vertexes[0].Point, view_plane
        )
        p2 = getProjectionToSVGPlane(
            rebar.Base.Shape.Wires[0].Vertexes[1].Point, view_plane
        )
        # Rebar is more horizontal, so dimension line will be vertical
        if abs(p2.y - p1.y) < abs(p2.x - p1.x):
            # Rebar is more closer to top of drawing
            if abs(svg_min_y - min(p1.y, p2.y)) < abs(
                svg_max_y - max(p1.y, p2.y)
            ):
                start_x = svg_min_x + dimension_top_offset_point.x
                start_y = svg_min_y - dimension_top_offset_point.y
            # Rebar is more closer to bottom of drawing
            else:
                start_x = svg_min_x + dimension_bottom_offset_point.x
                start_y = svg_max_y + dimension_bottom_offset_point.y

            min_x = min(p1.x, p2.x)
            max_x = max(p1.x, p2.x)
            # start_x is left to line
            if start_x < min_x:
                end_x = min_x + 10
            # start_x is right to line
            elif max_x < start_x:
                end_x = max_x - 10
            # start_x is between line min_x and max_x
            else:
                end_x = start_x
            end_y = (end_x - p1.x) * (p2.y - p1.y) / (p2.x - p1.x) + p1.y

        # Rebar is more vertical, so dimension line will be horizontal
        else:
            # Rebar is more closer to left of drawing
            if abs(svg_min_x - min(p1.x, p2.x)) < abs(
                svg_max_x - max(p1.x, p2.x)
            ):
                start_x = svg_min_x - dimension_left_offset_point.x
                start_y = svg_min_y + dimension_left_offset_point.y
            # Rebar is more closer to right of drawing
            else:
                start_x = svg_max_x + dimension_right_offset_point.x
                start_y = svg_min_y + dimension_right_offset_point.y

            min_y = min(p1.y, p2.y)
            max_y = max(p1.y, p2.y)
            # start_y is above line
            if start_y < min_y:
                end_y = min_y + 10
            # start_y is below line
            elif max_y < start_y:
                end_y = max_y - 10
            # start_y is between line min_y and max_y
            else:
                end_y = start_y
            end_x = (end_y - p1.y) * (p2.x - p1.x) / (p2.y - p1.y) + p1.x

        return [
            {
                "WayPoints": [
                    FreeCAD.Vector(start_x, start_y),
                    FreeCAD.Vector(end_x, end_y),
                ],
                "DimensionLabel": getRebarDimensionLabel(
                    rebar, dimension_format
                ),
                "LineStartSymbol": "None",
                "LineEndSymbol": "FilledArrow",
                "TextPositionType": "StartOfLine",
            }
        ]
    else:
        basewire = rebar.Base.Shape.Wires[0]
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
                start_p1 = getProjectionToSVGPlane(
                    startwire.Vertexes[0].Point, view_plane
                )
                start_p2 = getProjectionToSVGPlane(
                    startwire.Vertexes[1].Point, view_plane
                )

                if "@" in rebar_spacing_str:
                    rebars_count = int(rebar_spacing_str.split("@")[0])
                else:
                    rebars_count = 1

                endwire = basewire.copy()
                endwire.Placement = rebar.PlacementList[
                    start_rebar_index + rebars_count - 1
                ].multiply(basewire.Placement)
                end_p1 = getProjectionToSVGPlane(
                    endwire.Vertexes[0].Point, view_plane
                )
                end_p2 = getProjectionToSVGPlane(
                    endwire.Vertexes[1].Point, view_plane
                )
                start_rebar_index += rebars_count
                rebar_points.append((start_p1, start_p2, end_p1, end_p2))

                dimension_label = dimension_format.replace(
                    "%M", str(rebar.Mark)
                )
                dimension_label = dimension_label.replace(
                    "%C", str(rebars_count)
                )
                dimension_label = dimension_label.replace(
                    "%D", rebar_diameter
                ).strip()
                dimension_labels.append(dimension_label)
        else:
            basewire = rebar.Base.Shape.Wires[0]
            startwire = basewire.copy()
            startwire.Placement = rebar.PlacementList[0].multiply(
                basewire.Placement
            )
            start_p1 = getProjectionToSVGPlane(
                startwire.Vertexes[0].Point, view_plane
            )
            start_p2 = getProjectionToSVGPlane(
                startwire.Vertexes[1].Point, view_plane
            )

            endwire = basewire.copy()
            endwire.Placement = rebar.PlacementList[-1].multiply(
                basewire.Placement
            )
            end_p1 = getProjectionToSVGPlane(
                endwire.Vertexes[0].Point, view_plane
            )
            end_p2 = getProjectionToSVGPlane(
                endwire.Vertexes[1].Point, view_plane
            )

            rebar_points.append((start_p1, start_p2, end_p1, end_p2))
            dimension_labels.append(
                getRebarDimensionLabel(rebar, dimension_format)
            )

        dimension_data_list = []
        for i, (start_p1, start_p2, end_p1, end_p2) in enumerate(rebar_points):
            # Rebars span along x-axis, so dimension lines will be either on top
            # or bottom side
            if round(rebar_span_axis.cross(view_plane.u).Length) == 0:
                # Rebars end points are more closer to top of drawing
                if abs(svg_min_y - min(start_p1.y, start_p2.y)) < abs(
                    svg_max_y - max(start_p1.y, start_p2.y)
                ):
                    p1 = start_p1 if start_p1.y < start_p2.y else start_p2
                    p4 = end_p1 if end_p1.y < end_p2.y else end_p2
                    p2 = FreeCAD.Vector(
                        p1.x, svg_min_y - dimension_top_offset_point.y
                    )
                    p3 = FreeCAD.Vector(
                        p4.x, svg_min_y - dimension_top_offset_point.y
                    )
                # Rebars end points are more closer to bottom of drawing
                else:
                    p1 = start_p1 if start_p1.y > start_p2.y else start_p2
                    p4 = end_p1 if end_p1.y > end_p2.y else end_p2
                    p2 = FreeCAD.Vector(
                        p1.x, svg_max_y + dimension_bottom_offset_point.y
                    )
                    p3 = FreeCAD.Vector(
                        p4.x, svg_max_y + dimension_bottom_offset_point.y
                    )
            # Rebars span along y-axis, so dimension lines will be either on
            # left or right side
            else:
                # Rebars end points are more closer to left of drawing
                if abs(svg_min_x - min(start_p1.x, start_p2.x)) < abs(
                    svg_max_x - max(start_p1.x, start_p2.x)
                ):
                    p1 = start_p1 if start_p1.x < start_p2.x else start_p2
                    p4 = end_p1 if end_p1.x < end_p2.x else end_p2
                    p2 = FreeCAD.Vector(
                        svg_min_x - dimension_left_offset_point.x, p1.y
                    )
                    p3 = FreeCAD.Vector(
                        svg_min_x - dimension_left_offset_point.x, p4.y
                    )
                # Rebars end points are more closer to right of drawing
                else:
                    p1 = start_p1 if start_p1.x > start_p2.x else start_p2
                    p4 = end_p1 if end_p1.x > end_p2.x else end_p2
                    p2 = FreeCAD.Vector(
                        svg_max_x + dimension_right_offset_point.x, p1.y
                    )
                    p3 = FreeCAD.Vector(
                        svg_max_x + dimension_right_offset_point.x, p4.y
                    )
            if (
                round(p3.x - p2.x) == 0
                and round(p3.y - p2.y) == 0
                and round(p4.x - p1.x) == 0
                and round(p4.y - p1.y) == 0
            ):
                dimension_data_list.append(
                    {
                        "WayPoints": [p2, p1],
                        "DimensionLabel": dimension_labels[i],
                        "LineStartSymbol": "None",
                        "LineEndSymbol": "FilledArrow",
                        "TextPositionType": "StartOfLine",
                    }
                )
            else:
                dimension_data_list.append(
                    {
                        "WayPoints": [p1, p2, p3, p4],
                        "DimensionLabel": dimension_labels[i],
                        "TextPositionType": "MidOfLine",
                    }
                )
        return dimension_data_list


def getRebarDimensionData(
    rebar,
    dimension_format,
    view_plane,
    dimension_left_offset_point,
    dimension_right_offset_point,
    dimension_top_offset_point,
    dimension_bottom_offset_point,
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
            dimension_left_offset_point,
            dimension_right_offset_point,
            dimension_top_offset_point,
            dimension_bottom_offset_point,
            svg_min_x,
            svg_min_y,
            svg_max_x,
            svg_max_y,
        )
    if rebar.RebarShape == "StraightRebar":
        dimension_data = getStraightRebarDimensionData(
            rebar,
            dimension_format,
            view_plane,
            dimension_left_offset_point,
            dimension_right_offset_point,
            dimension_top_offset_point,
            dimension_bottom_offset_point,
            svg_min_x,
            svg_min_y,
            svg_max_x,
            svg_max_y,
        )
    return dimension_data
