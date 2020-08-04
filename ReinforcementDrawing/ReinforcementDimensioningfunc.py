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
import random

import FreeCAD
import DraftGeomUtils
import DraftVecUtils
import Part

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
                return points_list[i - 1], point, points_list[i + 1]
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
                return p1, mid_point, p2
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
    # Set diameter
    diameter = str(rebar.Diameter.Value).strip()
    if "." in diameter:
        diameter = diameter.rstrip("0").rstrip(".")
    dimension_label = dimension_label.replace("%D", diameter)
    # Set rebars span length
    if hasattr(rebar, "RebarShape") and rebar.RebarShape == "HelicalRebar":
        span_length = str(
            round(
                DraftVecUtils.dist(
                    rebar.Base.Shape.Wires[0].Vertexes[0].Point,
                    rebar.Base.Shape.Wires[0].Vertexes[-1].Point,
                )
            )
        ).strip()
    else:
        span_length = str(
            round(
                DraftVecUtils.dist(
                    rebar.PlacementList[0].Base, rebar.PlacementList[-1].Base
                )
            )
        ).strip()
    if "." in span_length:
        span_length = span_length.rstrip("0").rstrip(".")
    dimension_label = dimension_label.replace("%S", span_length).strip()
    return dimension_label


def getStirrupDimensionData(
    rebar,
    dimension_format,
    view_plane,
    dimension_left_point_x,
    dimension_right_point_x,
    dimension_top_point_y,
    dimension_bottom_point_y,
    svg_min_x,
    svg_min_y,
    svg_max_x,
    svg_max_y,
    scale,
    single_rebar_outer_dimension,
    multi_rebar_outer_dimension,
):
    drawing_plane_normal = view_plane.axis
    stirrup_span_axis = getRebarsSpanAxis(rebar)
    if round(drawing_plane_normal.cross(stirrup_span_axis).Length) == 0:
        edges = Part.__sortEdges__(rebar.Base.Shape.Edges)
        mid_edge = edges[int(len(edges) / 2)]
        mid_point = getProjectionToSVGPlane(
            DraftGeomUtils.findMidpoint(mid_edge), view_plane
        )
        return (
            [
                {
                    "LabelPosition": mid_point,
                    "LabelOnly": True,
                    "DimensionLabel": getRebarDimensionLabel(
                        rebar, dimension_format
                    ),
                    "VisibleRebars": "Single",
                }
            ],
            "Center",
        )
    else:
        if round(stirrup_span_axis.cross(view_plane.u).Length) == 0:
            stirrup_alignment = "V"
        else:
            stirrup_alignment = "H"

        basewire = DraftGeomUtils.filletWire(
            rebar.Base.Shape.Wires[0], rebar.Rounding * rebar.Diameter.Value
        )
        rebar_start_end_points = []
        rebar_mid_points = []
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
                    rebars_span_length = str(
                        round(
                            rebars_count
                            * float(rebar_spacing_str.split("@")[1])
                        )
                    )
                    if "." in rebars_span_length:
                        rebars_span_length = rebars_span_length.rstrip(
                            "0"
                        ).rstrip(".")
                else:
                    rebars_count = 1
                    rebars_span_length = ""

                rebar_mid_points.append([])
                for placement in rebar.PlacementList[
                    start_rebar_index + 1 : start_rebar_index + rebars_count - 1
                ]:
                    mid_wire = basewire.copy()
                    mid_wire.Placement = placement.multiply(basewire.Placement)
                    mid_p1, mid_p2 = getStirrupSVGPoints(
                        mid_wire, stirrup_alignment, view_plane
                    )
                    rebar_mid_points[-1].append((mid_p1, mid_p2))

                endwire = basewire.copy()
                endwire.Placement = rebar.PlacementList[
                    start_rebar_index + rebars_count - 1
                ].multiply(basewire.Placement)
                end_p1, end_p2 = getStirrupSVGPoints(
                    endwire, stirrup_alignment, view_plane
                )
                start_rebar_index += rebars_count
                rebar_start_end_points.append(
                    (start_p1, start_p2, end_p1, end_p2)
                )

                dimension_label = dimension_format.replace(
                    "%M", str(rebar.Mark)
                )
                dimension_label = dimension_label.replace(
                    "%C", str(rebars_count)
                )
                dimension_label = dimension_label.replace("%D", rebar_diameter)
                dimension_label = dimension_label.replace(
                    "%S", rebars_span_length
                ).strip()
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

            rebar_mid_points.append([])
            for placement in rebar.PlacementList[1:-1]:
                mid_wire = basewire.copy()
                mid_wire.Placement = placement.multiply(basewire.Placement)
                mid_p1, mid_p2 = getStirrupSVGPoints(
                    mid_wire, stirrup_alignment, view_plane
                )
                rebar_mid_points[-1].append((mid_p1, mid_p2))

            rebar_start_end_points.append((start_p1, start_p2, end_p1, end_p2))
            dimension_labels.append(
                getRebarDimensionLabel(rebar, dimension_format)
            )

        dimension_data_list = []
        start_p1, start_p2, end_p1, end_p2 = rebar_start_end_points[0]
        if stirrup_alignment == "V":
            # Stirrup is more closer to top of drawing
            if abs(svg_min_y - start_p1.y) < abs(svg_max_y - start_p2.y):
                dimension_align = "Top"
                for i, (start_p1, start_p2, end_p1, end_p2) in enumerate(
                    rebar_start_end_points
                ):
                    if multi_rebar_outer_dimension:
                        dimension_points_start = [
                            FreeCAD.Vector(
                                start_p1.x, dimension_top_point_y + 5 / scale
                            ),
                            FreeCAD.Vector(start_p1.x, dimension_top_point_y),
                        ]
                        dimension_points_end = [
                            FreeCAD.Vector(end_p1.x, dimension_top_point_y),
                            FreeCAD.Vector(
                                end_p1.x, dimension_top_point_y + 5 / scale
                            ),
                        ]
                    else:
                        dimension_points_start = [
                            FreeCAD.Vector(start_p1.x, start_p1.y - 5),
                            FreeCAD.Vector(start_p1.x, dimension_top_point_y),
                        ]
                        dimension_points_end = [
                            FreeCAD.Vector(end_p1.x, dimension_top_point_y),
                            FreeCAD.Vector(end_p1.x, end_p1.y - 5),
                        ]

                    dimension_points = []
                    dimension_points.extend(dimension_points_start)
                    for mid_points in rebar_mid_points[i]:
                        dimension_points.append(
                            FreeCAD.Vector(
                                mid_points[0].x, dimension_top_point_y
                            )
                        )
                    dimension_points.extend(dimension_points_end)

                    dimension_data_list.append(
                        {
                            "WayPoints": dimension_points,
                            "DimensionLabel": dimension_labels[i],
                            "VisibleRebars": "Multiple",
                        }
                    )
            # Stirrup is more closer to bottom of drawing
            else:
                dimension_align = "Bottom"
                for i, (start_p1, start_p2, end_p1, end_p2) in enumerate(
                    rebar_start_end_points
                ):
                    if multi_rebar_outer_dimension:
                        dimension_points_start = [
                            FreeCAD.Vector(
                                start_p2.x, dimension_bottom_point_y - 5 / scale
                            ),
                            FreeCAD.Vector(
                                start_p2.x, dimension_bottom_point_y
                            ),
                        ]
                        dimension_points_end = [
                            FreeCAD.Vector(end_p2.x, dimension_bottom_point_y),
                            FreeCAD.Vector(
                                end_p2.x, dimension_bottom_point_y - 5 / scale
                            ),
                        ]
                    else:
                        dimension_points_start = [
                            FreeCAD.Vector(start_p2.x, start_p2.y + 5),
                            FreeCAD.Vector(
                                start_p2.x, dimension_bottom_point_y,
                            ),
                        ]
                        dimension_points_end = [
                            FreeCAD.Vector(end_p2.x, dimension_bottom_point_y),
                            FreeCAD.Vector(end_p2.x, end_p2.y + 5),
                        ]

                    dimension_points = []
                    dimension_points.extend(dimension_points_start)
                    for mid_points in rebar_mid_points[i]:
                        dimension_points.append(
                            FreeCAD.Vector(
                                mid_points[1].x, dimension_bottom_point_y
                            )
                        )
                    dimension_points.extend(dimension_points_end)

                    dimension_data_list.append(
                        {
                            "WayPoints": dimension_points,
                            "DimensionLabel": dimension_labels[i],
                            "VisibleRebars": "Multiple",
                        }
                    )
        else:
            # Stirrup is more closer to left of drawing
            if abs(svg_min_x - start_p1.x) < abs(svg_max_x - start_p2.x):
                dimension_align = "Left"
                for i, (start_p1, start_p2, end_p1, end_p2) in enumerate(
                    rebar_start_end_points
                ):
                    if multi_rebar_outer_dimension:
                        dimension_points_start = [
                            FreeCAD.Vector(
                                dimension_left_point_x + 5 / scale, start_p1.y
                            ),
                            FreeCAD.Vector(dimension_left_point_x, start_p1.y),
                        ]
                        dimension_points_end = [
                            FreeCAD.Vector(dimension_left_point_x, end_p1.y),
                            FreeCAD.Vector(
                                dimension_left_point_x + 5 / scale, end_p1.y
                            ),
                        ]
                    else:
                        dimension_points_start = [
                            FreeCAD.Vector(start_p1.x - 5, start_p1.y),
                            FreeCAD.Vector(dimension_left_point_x, start_p1.y),
                        ]
                        dimension_points_end = [
                            FreeCAD.Vector(dimension_left_point_x, end_p1.y),
                            FreeCAD.Vector(end_p1.x - 5, end_p1.y),
                        ]

                    dimension_points = []
                    dimension_points.extend(dimension_points_start)
                    for mid_points in rebar_mid_points[i]:
                        dimension_points.append(
                            FreeCAD.Vector(
                                dimension_left_point_x, mid_points[0].y
                            )
                        )
                    dimension_points.extend(dimension_points_end)

                    dimension_data_list.append(
                        {
                            "WayPoints": dimension_points,
                            "DimensionLabel": dimension_labels[i],
                            "VisibleRebars": "Multiple",
                        }
                    )
            # Stirrup is more closer to right of drawing
            else:
                dimension_align = "Right"
                for i, (start_p1, start_p2, end_p1, end_p2) in enumerate(
                    rebar_start_end_points
                ):
                    if multi_rebar_outer_dimension:
                        dimension_points_start = [
                            FreeCAD.Vector(
                                dimension_right_point_x - 5 / scale, start_p2.y
                            ),
                            FreeCAD.Vector(
                                dimension_right_point_x, start_p2.y,
                            ),
                        ]
                        dimension_points_end = [
                            FreeCAD.Vector(dimension_right_point_x, end_p2.y),
                            FreeCAD.Vector(
                                dimension_right_point_x - 5 / scale, end_p2.y
                            ),
                        ]
                    else:
                        dimension_points_start = [
                            FreeCAD.Vector(start_p2.x + 5, start_p2.y),
                            FreeCAD.Vector(
                                dimension_right_point_x, start_p2.y,
                            ),
                        ]
                        dimension_points_end = [
                            FreeCAD.Vector(dimension_right_point_x, end_p2.y),
                            FreeCAD.Vector(end_p2.x + 5, end_p2.y),
                        ]

                    dimension_points = []
                    dimension_points.extend(dimension_points_start)
                    for mid_points in rebar_mid_points[i]:
                        dimension_points.append(
                            FreeCAD.Vector(
                                dimension_right_point_x, mid_points[1].y
                            )
                        )
                    dimension_points.extend(dimension_points_end)

                    dimension_data_list.append(
                        {
                            "WayPoints": dimension_points,
                            "DimensionLabel": dimension_labels[i],
                            "VisibleRebars": "Multiple",
                        }
                    )
        return dimension_data_list, dimension_align


def getStraightRebarDimensionData(
    rebar,
    dimension_format,
    view_plane,
    dimension_left_point_x,
    dimension_right_point_x,
    dimension_top_point_y,
    dimension_bottom_point_y,
    svg_min_x,
    svg_min_y,
    svg_max_x,
    svg_max_y,
    scale,
    single_rebar_outer_dimension,
    multi_rebar_outer_dimension,
):
    drawing_plane_normal = view_plane.axis
    rebar_span_axis = getRebarsSpanAxis(rebar)
    # Straight rebars span axis is parallel to drawing plane normal
    # Thus, only one rebar will be visible
    if (
        round(drawing_plane_normal.cross(rebar_span_axis).Length) == 0
        or rebar.Amount == 1
    ):
        basewire = rebar.Base.Shape.Wires[0].copy()
        basewire.Placement = rebar.PlacementList[0].multiply(basewire.Placement)
        p1 = getProjectionToSVGPlane(basewire.Vertexes[0].Point, view_plane)
        p2 = getProjectionToSVGPlane(basewire.Vertexes[1].Point, view_plane)

        # Rebar is more horizontal, so dimension line will be vertical
        if abs(p2.y - p1.y) <= abs(p2.x - p1.x):
            start_x = end_x = random.randint(
                int(min(p1.x, p2.x)), int(max(p1.x, p2.x))
            )
            # Rebar is more closer to top of drawing
            if abs(svg_min_y - min(p1.y, p2.y)) < abs(
                svg_max_y - max(p1.y, p2.y)
            ):
                dimension_align = "Top"
                start_y = dimension_top_point_y
            # Rebar is more closer to bottom of drawing
            else:
                dimension_align = "Bottom"
                start_y = dimension_bottom_point_y

            if single_rebar_outer_dimension:
                if dimension_align == "Top":
                    end_y = dimension_top_point_y + 5 / scale
                else:
                    end_y = dimension_bottom_point_y - 5 / scale
            else:
                end_y = (
                    (end_x - p1.x) * (p2.y - p1.y) / (p2.x - p1.x) + p1.y
                    if (p2.x - p1.x) != 0
                    else p1.y
                )

        # Rebar is more vertical, so dimension line will be horizontal
        else:
            start_y = end_y = random.randint(
                int(min(p1.y, p2.y)), int(max(p1.y, p2.y))
            )
            # Rebar is more closer to left of drawing
            if abs(svg_min_x - min(p1.x, p2.x)) < abs(
                svg_max_x - max(p1.x, p2.x)
            ):
                dimension_align = "Left"
                start_x = dimension_left_point_x
            # Rebar is more closer to right of drawing
            else:
                dimension_align = "Right"
                start_x = dimension_right_point_x

            if single_rebar_outer_dimension:
                if dimension_align == "Left":
                    end_x = dimension_left_point_x + 5 / scale
                else:
                    end_x = dimension_right_point_x - 5 / scale
            else:
                end_x = (end_y - p1.y) * (p2.x - p1.x) / (p2.y - p1.y) + p1.x

        return (
            [
                {
                    "WayPoints": [
                        FreeCAD.Vector(start_x, start_y),
                        FreeCAD.Vector(end_x, end_y),
                    ],
                    "DimensionLabel": getRebarDimensionLabel(
                        rebar, dimension_format
                    ),
                    "VisibleRebars": "Single",
                }
            ],
            dimension_align,
        )
    else:
        basewire = rebar.Base.Shape.Wires[0]
        rebar_start_end_points = []
        rebar_mid_points = []
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
                    rebars_span_length = str(
                        round(
                            rebars_count
                            * float(rebar_spacing_str.split("@")[1])
                        )
                    )
                    if "." in rebars_span_length:
                        rebars_span_length = rebars_span_length.rstrip(
                            "0"
                        ).rstrip(".")
                else:
                    rebars_count = 1
                    rebars_span_length = ""

                rebar_mid_points.append([])
                for placement in rebar.PlacementList[
                    start_rebar_index + 1 : start_rebar_index + rebars_count - 1
                ]:
                    mid_wire = basewire.copy()
                    mid_wire.Placement = placement.multiply(basewire.Placement)
                    mid_p1 = getProjectionToSVGPlane(
                        mid_wire.Vertexes[0].Point, view_plane
                    )
                    mid_p2 = getProjectionToSVGPlane(
                        mid_wire.Vertexes[1].Point, view_plane
                    )
                    rebar_mid_points[-1].append((mid_p1, mid_p2))

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
                rebar_start_end_points.append(
                    (start_p1, start_p2, end_p1, end_p2)
                )

                dimension_label = dimension_format.replace(
                    "%M", str(rebar.Mark)
                )
                dimension_label = dimension_label.replace(
                    "%C", str(rebars_count)
                )
                dimension_label = dimension_label.replace("%D", rebar_diameter)
                dimension_label = dimension_label.replace(
                    "%S", rebars_span_length
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

            rebar_mid_points.append([])
            for placement in rebar.PlacementList[1:-1]:
                mid_wire = basewire.copy()
                mid_wire.Placement = placement.multiply(basewire.Placement)
                mid_p1 = getProjectionToSVGPlane(
                    mid_wire.Vertexes[0].Point, view_plane
                )
                mid_p2 = getProjectionToSVGPlane(
                    mid_wire.Vertexes[1].Point, view_plane
                )
                rebar_mid_points[-1].append((mid_p1, mid_p2))

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

            rebar_start_end_points.append((start_p1, start_p2, end_p1, end_p2))
            dimension_labels.append(
                getRebarDimensionLabel(rebar, dimension_format)
            )

        dimension_data_list = []
        for i, (start_p1, start_p2, end_p1, end_p2) in enumerate(
            rebar_start_end_points
        ):
            dimension_mid_points = []
            # Rebars span along x-axis, so dimension lines will be either on top
            # or bottom side
            if round(rebar_span_axis.cross(view_plane.u).Length) == 0:
                # Rebars end points are more closer to top of drawing
                if abs(svg_min_y - min(start_p1.y, start_p2.y)) < abs(
                    svg_max_y - max(start_p1.y, start_p2.y)
                ):
                    dimension_align = "Top"
                    p1 = start_p1 if start_p1.y < start_p2.y else start_p2
                    p4 = end_p1 if end_p1.y < end_p2.y else end_p2
                    if round(p4.x - p1.x) == 0 and round(p4.y - p1.y) == 0:
                        if single_rebar_outer_dimension:
                            p1 = FreeCAD.Vector(
                                p1.x, dimension_top_point_y + 5 / scale
                            )
                            p4 = FreeCAD.Vector(
                                p4.x, dimension_top_point_y + 5 / scale
                            )
                    elif multi_rebar_outer_dimension:
                        p1 = FreeCAD.Vector(
                            p1.x, dimension_top_point_y + 5 / scale
                        )
                        p4 = FreeCAD.Vector(
                            p4.x, dimension_top_point_y + 5 / scale
                        )
                    p2 = FreeCAD.Vector(p1.x, dimension_top_point_y)
                    p3 = FreeCAD.Vector(p4.x, dimension_top_point_y)
                    for mid_points in rebar_mid_points[i]:
                        dimension_mid_points.append(
                            FreeCAD.Vector(
                                min(mid_points, key=lambda p: p.y).x,
                                dimension_top_point_y,
                            )
                        )
                # Rebars end points are more closer to bottom of drawing
                else:
                    dimension_align = "Bottom"
                    p1 = start_p1 if start_p1.y > start_p2.y else start_p2
                    p4 = end_p1 if end_p1.y > end_p2.y else end_p2
                    if round(p4.x - p1.x) == 0 and round(p4.y - p1.y) == 0:
                        if single_rebar_outer_dimension:
                            p1 = FreeCAD.Vector(
                                p1.x, dimension_bottom_point_y - 5 / scale
                            )
                            p4 = FreeCAD.Vector(
                                p4.x, dimension_bottom_point_y - 5 / scale
                            )
                    elif multi_rebar_outer_dimension:
                        p1 = FreeCAD.Vector(
                            p1.x, dimension_bottom_point_y - 5 / scale
                        )
                        p4 = FreeCAD.Vector(
                            p4.x, dimension_bottom_point_y - 5 / scale
                        )
                    p2 = FreeCAD.Vector(p1.x, dimension_bottom_point_y)
                    p3 = FreeCAD.Vector(p4.x, dimension_bottom_point_y)
                    for mid_points in rebar_mid_points[i]:
                        dimension_mid_points.append(
                            FreeCAD.Vector(
                                max(mid_points, key=lambda p: p.y).x,
                                dimension_bottom_point_y,
                            )
                        )
            # Rebars span along y-axis, so dimension lines will be either on
            # left or right side
            else:
                # Rebars end points are more closer to left of drawing
                if abs(svg_min_x - min(start_p1.x, start_p2.x)) < abs(
                    svg_max_x - max(start_p1.x, start_p2.x)
                ):
                    dimension_align = "Left"
                    p1 = start_p1 if start_p1.x < start_p2.x else start_p2
                    p4 = end_p1 if end_p1.x < end_p2.x else end_p2
                    if round(p4.x - p1.x) == 0 and round(p4.y - p1.y) == 0:
                        if single_rebar_outer_dimension:
                            p1 = FreeCAD.Vector(
                                dimension_left_point_x + 5 / scale, p1.y
                            )
                            p4 = FreeCAD.Vector(
                                dimension_left_point_x + 5 / scale, p4.y
                            )
                    elif multi_rebar_outer_dimension:
                        p1 = FreeCAD.Vector(
                            dimension_left_point_x + 5 / scale, p1.y
                        )
                        p4 = FreeCAD.Vector(
                            dimension_left_point_x + 5 / scale, p4.y
                        )
                    p2 = FreeCAD.Vector(dimension_left_point_x, p1.y)
                    p3 = FreeCAD.Vector(dimension_left_point_x, p4.y)
                    for mid_points in rebar_mid_points[i]:
                        dimension_mid_points.append(
                            FreeCAD.Vector(
                                dimension_left_point_x,
                                min(mid_points, key=lambda p: p.x).y,
                            )
                        )
                # Rebars end points are more closer to right of drawing
                else:
                    dimension_align = "Right"
                    p1 = start_p1 if start_p1.x > start_p2.x else start_p2
                    p4 = end_p1 if end_p1.x > end_p2.x else end_p2
                    if round(p4.x - p1.x) == 0 and round(p4.y - p1.y) == 0:
                        if single_rebar_outer_dimension:
                            p1 = FreeCAD.Vector(
                                dimension_right_point_x - 5 / scale, p1.y
                            )
                            p4 = FreeCAD.Vector(
                                dimension_right_point_x - 5 / scale, p4.y
                            )
                    elif multi_rebar_outer_dimension:
                        p1 = FreeCAD.Vector(
                            dimension_right_point_x - 5 / scale, p1.y
                        )
                        p4 = FreeCAD.Vector(
                            dimension_right_point_x - 5 / scale, p4.y
                        )
                    p2 = FreeCAD.Vector(dimension_right_point_x, p1.y)
                    p3 = FreeCAD.Vector(dimension_right_point_x, p4.y)
                    for mid_points in rebar_mid_points[i]:
                        dimension_mid_points.append(
                            FreeCAD.Vector(
                                dimension_right_point_x,
                                max(mid_points, key=lambda p: p.x).y,
                            )
                        )
            if round(p4.x - p1.x) == 0 and round(p4.y - p1.y) == 0:
                dimension_data_list.append(
                    {
                        "WayPoints": [p2, p1],
                        "DimensionLabel": dimension_labels[i],
                        "VisibleRebars": "Single",
                    }
                )
            else:
                way_points = [p1, p2]
                way_points.extend(dimension_mid_points)
                way_points.extend([p3, p4])
                dimension_data_list.append(
                    {
                        "WayPoints": way_points,
                        "DimensionLabel": dimension_labels[i],
                        "VisibleRebars": "Multiple",
                    }
                )
        return dimension_data_list, dimension_align


def getLShapeRebarDimensionData(
    rebar,
    dimension_format,
    view_plane,
    dimension_left_point_x,
    dimension_right_point_x,
    dimension_top_point_y,
    dimension_bottom_point_y,
    svg_min_x,
    svg_min_y,
    svg_max_x,
    svg_max_y,
    scale,
    single_rebar_outer_dimension,
    multi_rebar_outer_dimension,
):
    drawing_plane_normal = view_plane.axis
    rebar_span_axis = getRebarsSpanAxis(rebar)
    # LShape rebars span axis is parallel to drawing plane normal
    # Thus, only one rebar will be visible
    if (
        round(drawing_plane_normal.cross(rebar_span_axis).Length) == 0
        or rebar.Amount == 1
    ):
        basewire = rebar.Base.Shape.Wires[0].copy()
        basewire.Placement = rebar.PlacementList[0].multiply(basewire.Placement)
        p1 = getProjectionToSVGPlane(basewire.Vertexes[-1].Point, view_plane)
        p2 = getProjectionToSVGPlane(basewire.Vertexes[-2].Point, view_plane)
        if round(p1.x - p2.x) == 0 and round(p1.y - p2.y) == 0:
            p1 = getProjectionToSVGPlane(basewire.Vertexes[0].Point, view_plane)
            p2 = getProjectionToSVGPlane(basewire.Vertexes[1].Point, view_plane)
        # Rebar is more horizontal, so dimension line will be vertical
        if abs(p2.y - p1.y) <= abs(p2.x - p1.x):
            start_x = end_x = random.randint(
                int(min(p1.x, p2.x)), int(max(p1.x, p2.x))
            )
            # Rebar is more closer to top of drawing
            if abs(svg_min_y - min(p1.y, p2.y)) < abs(
                svg_max_y - max(p1.y, p2.y)
            ):
                dimension_align = "Top"
                start_y = dimension_top_point_y
            # Rebar is more closer to bottom of drawing
            else:
                dimension_align = "Bottom"
                start_y = dimension_bottom_point_y

            if single_rebar_outer_dimension:
                if dimension_align == "Top":
                    end_y = dimension_top_point_y + 5 / scale
                else:
                    end_y = dimension_bottom_point_y - 5 / scale
            else:
                end_y = (
                    (end_x - p1.x) * (p2.y - p1.y) / (p2.x - p1.x) + p1.y
                    if (p2.x - p1.x) != 0
                    else p1.y
                )

        # Rebar is more vertical, so dimension line will be horizontal
        else:
            start_y = end_y = random.randint(
                int(min(p1.y, p2.y)), int(max(p1.y, p2.y))
            )
            # Rebar is more closer to left of drawing
            if abs(svg_min_x - min(p1.x, p2.x)) < abs(
                svg_max_x - max(p1.x, p2.x)
            ):
                dimension_align = "Left"
                start_x = dimension_left_point_x
            # Rebar is more closer to right of drawing
            else:
                dimension_align = "Right"
                start_x = dimension_right_point_x

            if single_rebar_outer_dimension:
                if dimension_align == "Left":
                    end_x = dimension_left_point_x + 5 / scale
                else:
                    end_x = dimension_right_point_x - 5 / scale
            else:
                end_x = (end_y - p1.y) * (p2.x - p1.x) / (p2.y - p1.y) + p1.x

        return (
            [
                {
                    "WayPoints": [
                        FreeCAD.Vector(start_x, start_y),
                        FreeCAD.Vector(end_x, end_y),
                    ],
                    "DimensionLabel": getRebarDimensionLabel(
                        rebar, dimension_format
                    ),
                    "VisibleRebars": "Single",
                }
            ],
            dimension_align,
        )
    else:
        basewire = rebar.Base.Shape.Wires[0]
        rebar_start_end_points = []
        rebar_mid_points = []
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
                if (
                    round(start_p1.x - start_p2.x) == 0
                    and round(start_p1.y - start_p2.y) == 0
                ):
                    start_p1 = getProjectionToSVGPlane(
                        startwire.Vertexes[-1].Point, view_plane
                    )
                    start_p2 = getProjectionToSVGPlane(
                        startwire.Vertexes[-2].Point, view_plane
                    )

                if "@" in rebar_spacing_str:
                    rebars_count = int(rebar_spacing_str.split("@")[0])
                    rebars_span_length = str(
                        round(
                            rebars_count
                            * float(rebar_spacing_str.split("@")[1])
                        )
                    )
                    if "." in rebars_span_length:
                        rebars_span_length = rebars_span_length.rstrip(
                            "0"
                        ).rstrip(".")
                else:
                    rebars_count = 1
                    rebars_span_length = ""

                rebar_mid_points.append([])
                for placement in rebar.PlacementList[
                    start_rebar_index + 1 : start_rebar_index + rebars_count - 1
                ]:
                    mid_wire = basewire.copy()
                    mid_wire.Placement = placement.multiply(basewire.Placement)
                    mid_p1 = getProjectionToSVGPlane(
                        mid_wire.Vertexes[0].Point, view_plane
                    )
                    mid_p2 = getProjectionToSVGPlane(
                        mid_wire.Vertexes[1].Point, view_plane
                    )
                    rebar_mid_points[-1].append((mid_p1, mid_p2))

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
                if (
                    round(end_p1.x - end_p2.x) == 0
                    and round(end_p1.y - end_p2.y) == 0
                ):
                    end_p1 = getProjectionToSVGPlane(
                        endwire.Vertexes[-1].Point, view_plane
                    )
                    end_p2 = getProjectionToSVGPlane(
                        endwire.Vertexes[-2].Point, view_plane
                    )

                start_rebar_index += rebars_count
                rebar_start_end_points.append(
                    (start_p1, start_p2, end_p1, end_p2)
                )

                dimension_label = dimension_format.replace(
                    "%M", str(rebar.Mark)
                )
                dimension_label = dimension_label.replace(
                    "%C", str(rebars_count)
                )
                dimension_label = dimension_label.replace("%D", rebar_diameter)
                dimension_label = dimension_label.replace(
                    "%S", rebars_span_length
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
            if (
                round(start_p1.x - start_p2.x) == 0
                and round(start_p1.y - start_p2.y) == 0
            ):
                start_p1 = getProjectionToSVGPlane(
                    startwire.Vertexes[-1].Point, view_plane
                )
                start_p2 = getProjectionToSVGPlane(
                    startwire.Vertexes[-2].Point, view_plane
                )

            rebar_mid_points.append([])
            for placement in rebar.PlacementList[1:-1]:
                mid_wire = basewire.copy()
                mid_wire.Placement = placement.multiply(basewire.Placement)
                mid_p1 = getProjectionToSVGPlane(
                    mid_wire.Vertexes[0].Point, view_plane
                )
                mid_p2 = getProjectionToSVGPlane(
                    mid_wire.Vertexes[1].Point, view_plane
                )
                rebar_mid_points[-1].append((mid_p1, mid_p2))

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
            if (
                round(end_p1.x - end_p2.x) == 0
                and round(end_p1.y - end_p2.y) == 0
            ):
                end_p1 = getProjectionToSVGPlane(
                    endwire.Vertexes[-1].Point, view_plane
                )
                end_p2 = getProjectionToSVGPlane(
                    endwire.Vertexes[-2].Point, view_plane
                )

            rebar_start_end_points.append((start_p1, start_p2, end_p1, end_p2))
            dimension_labels.append(
                getRebarDimensionLabel(rebar, dimension_format)
            )

        dimension_data_list = []
        for i, (start_p1, start_p2, end_p1, end_p2) in enumerate(
            rebar_start_end_points
        ):
            dimension_mid_points = []
            # Rebars span along x-axis, so dimension lines will be either on top
            # or bottom side
            if round(rebar_span_axis.cross(view_plane.u).Length) == 0:
                # Rebars end points are more closer to top of drawing
                if abs(svg_min_y - min(start_p1.y, start_p2.y)) < abs(
                    svg_max_y - max(start_p1.y, start_p2.y)
                ):
                    dimension_align = "Top"
                    p1 = start_p1 if start_p1.y < start_p2.y else start_p2
                    p4 = end_p1 if end_p1.y < end_p2.y else end_p2
                    if round(p4.x - p1.x) == 0 and round(p4.y - p1.y) == 0:
                        if single_rebar_outer_dimension:
                            p1 = FreeCAD.Vector(
                                p1.x, dimension_top_point_y + 5 / scale
                            )
                            p4 = FreeCAD.Vector(
                                p4.x, dimension_top_point_y + 5 / scale
                            )
                    elif multi_rebar_outer_dimension:
                        p1 = FreeCAD.Vector(
                            p1.x, dimension_top_point_y + 5 / scale
                        )
                        p4 = FreeCAD.Vector(
                            p4.x, dimension_top_point_y + 5 / scale
                        )
                    p2 = FreeCAD.Vector(p1.x, dimension_top_point_y)
                    p3 = FreeCAD.Vector(p4.x, dimension_top_point_y)
                    for mid_points in rebar_mid_points[i]:
                        dimension_mid_points.append(
                            FreeCAD.Vector(
                                min(mid_points, key=lambda p: p.y).x,
                                dimension_top_point_y,
                            )
                        )
                # Rebars end points are more closer to bottom of drawing
                else:
                    dimension_align = "Bottom"
                    p1 = start_p1 if start_p1.y > start_p2.y else start_p2
                    p4 = end_p1 if end_p1.y > end_p2.y else end_p2
                    if round(p4.x - p1.x) == 0 and round(p4.y - p1.y) == 0:
                        if single_rebar_outer_dimension:
                            p1 = FreeCAD.Vector(
                                p1.x, dimension_bottom_point_y - 5 / scale
                            )
                            p4 = FreeCAD.Vector(
                                p4.x, dimension_bottom_point_y - 5 / scale
                            )
                    elif multi_rebar_outer_dimension:
                        p1 = FreeCAD.Vector(
                            p1.x, dimension_bottom_point_y - 5 / scale
                        )
                        p4 = FreeCAD.Vector(
                            p4.x, dimension_bottom_point_y - 5 / scale
                        )
                    p2 = FreeCAD.Vector(p1.x, dimension_bottom_point_y)
                    p3 = FreeCAD.Vector(p4.x, dimension_bottom_point_y)
                    for mid_points in rebar_mid_points[i]:
                        dimension_mid_points.append(
                            FreeCAD.Vector(
                                max(mid_points, key=lambda p: p.y).x,
                                dimension_bottom_point_y,
                            )
                        )
            # Rebars span along y-axis, so dimension lines will be either on
            # left or right side
            else:
                # Rebars end points are more closer to left of drawing
                if abs(svg_min_x - min(start_p1.x, start_p2.x)) < abs(
                    svg_max_x - max(start_p1.x, start_p2.x)
                ):
                    dimension_align = "Left"
                    p1 = start_p1 if start_p1.x < start_p2.x else start_p2
                    p4 = end_p1 if end_p1.x < end_p2.x else end_p2
                    if round(p4.x - p1.x) == 0 and round(p4.y - p1.y) == 0:
                        if single_rebar_outer_dimension:
                            p1 = FreeCAD.Vector(
                                dimension_left_point_x + 5 / scale, p1.y
                            )
                            p4 = FreeCAD.Vector(
                                dimension_left_point_x + 5 / scale, p4.y
                            )
                    elif multi_rebar_outer_dimension:
                        p1 = FreeCAD.Vector(
                            dimension_left_point_x + 5 / scale, p1.y
                        )
                        p4 = FreeCAD.Vector(
                            dimension_left_point_x + 5 / scale, p4.y
                        )
                    p2 = FreeCAD.Vector(dimension_left_point_x, p1.y)
                    p3 = FreeCAD.Vector(dimension_left_point_x, p4.y)
                    for mid_points in rebar_mid_points[i]:
                        dimension_mid_points.append(
                            FreeCAD.Vector(
                                dimension_left_point_x,
                                min(mid_points, key=lambda p: p.x).y,
                            )
                        )
                # Rebars end points are more closer to right of drawing
                else:
                    dimension_align = "Right"
                    p1 = start_p1 if start_p1.x > start_p2.x else start_p2
                    p4 = end_p1 if end_p1.x > end_p2.x else end_p2
                    if round(p4.x - p1.x) == 0 and round(p4.y - p1.y) == 0:
                        if single_rebar_outer_dimension:
                            p1 = FreeCAD.Vector(
                                dimension_right_point_x - 5 / scale, p1.y
                            )
                            p4 = FreeCAD.Vector(
                                dimension_right_point_x - 5 / scale, p4.y
                            )
                    elif multi_rebar_outer_dimension:
                        p1 = FreeCAD.Vector(
                            dimension_right_point_x - 5 / scale, p1.y
                        )
                        p4 = FreeCAD.Vector(
                            dimension_right_point_x - 5 / scale, p4.y
                        )
                    p2 = FreeCAD.Vector(dimension_right_point_x, p1.y)
                    p3 = FreeCAD.Vector(dimension_right_point_x, p4.y)
                    for mid_points in rebar_mid_points[i]:
                        dimension_mid_points.append(
                            FreeCAD.Vector(
                                dimension_right_point_x,
                                max(mid_points, key=lambda p: p.x).y,
                            )
                        )
            if round(p4.x - p1.x) == 0 and round(p4.y - p1.y) == 0:
                dimension_data_list.append(
                    {
                        "WayPoints": [p2, p1],
                        "DimensionLabel": dimension_labels[i],
                        "VisibleRebars": "Single",
                    }
                )
            else:
                way_points = [p1, p2]
                way_points.extend(dimension_mid_points)
                way_points.extend([p3, p4])
                dimension_data_list.append(
                    {
                        "WayPoints": way_points,
                        "DimensionLabel": dimension_labels[i],
                        "VisibleRebars": "Multiple",
                    }
                )
        return dimension_data_list, dimension_align


def getUShapeRebarDimensionData(
    rebar,
    dimension_format,
    view_plane,
    dimension_left_point_x,
    dimension_right_point_x,
    dimension_top_point_y,
    dimension_bottom_point_y,
    svg_min_x,
    svg_min_y,
    svg_max_x,
    svg_max_y,
    scale,
    single_rebar_outer_dimension,
    multi_rebar_outer_dimension,
):
    drawing_plane_normal = view_plane.axis
    rebar_span_axis = getRebarsSpanAxis(rebar)
    # UShape rebars span axis is parallel to drawing plane normal
    # Thus, only one rebar will be visible
    if (
        round(drawing_plane_normal.cross(rebar_span_axis).Length) == 0
        or rebar.Amount == 1
    ):
        basewire = rebar.Base.Shape.Wires[0].copy()
        basewire.Placement = rebar.PlacementList[0].multiply(basewire.Placement)
        edges = Part.__sortEdges__(basewire.Edges)
        mid_edge = edges[int(len(edges) / 2)]
        p1 = getProjectionToSVGPlane(mid_edge.Vertexes[0].Point, view_plane)
        p2 = getProjectionToSVGPlane(mid_edge.Vertexes[1].Point, view_plane)

        # Rebar is more horizontal, so dimension line will be vertical
        if abs(p2.y - p1.y) <= abs(p2.x - p1.x):
            start_x = end_x = random.randint(
                int(min(p1.x, p2.x)), int(max(p1.x, p2.x))
            )
            # Rebar is more closer to top of drawing
            if abs(svg_min_y - min(p1.y, p2.y)) < abs(
                svg_max_y - max(p1.y, p2.y)
            ):
                dimension_align = "Top"
                start_y = dimension_top_point_y
            # Rebar is more closer to bottom of drawing
            else:
                dimension_align = "Bottom"
                start_y = dimension_bottom_point_y

            if single_rebar_outer_dimension:
                if dimension_align == "Top":
                    end_y = dimension_top_point_y + 5 / scale
                else:
                    end_y = dimension_bottom_point_y - 5 / scale
            else:
                end_y = (
                    (end_x - p1.x) * (p2.y - p1.y) / (p2.x - p1.x) + p1.y
                    if (p2.x - p1.x) != 0
                    else p1.y
                )

        # Rebar is more vertical, so dimension line will be horizontal
        else:
            start_y = end_y = random.randint(
                int(min(p1.y, p2.y)), int(max(p1.y, p2.y))
            )
            # Rebar is more closer to left of drawing
            if abs(svg_min_x - min(p1.x, p2.x)) < abs(
                svg_max_x - max(p1.x, p2.x)
            ):
                dimension_align = "Left"
                start_x = dimension_left_point_x
            # Rebar is more closer to right of drawing
            else:
                dimension_align = "Right"
                start_x = dimension_right_point_x

            if single_rebar_outer_dimension:
                if dimension_align == "Left":
                    end_x = dimension_left_point_x + 5 / scale
                else:
                    end_x = dimension_right_point_x - 5 / scale
            else:
                end_x = (end_y - p1.y) * (p2.x - p1.x) / (p2.y - p1.y) + p1.x

        return (
            [
                {
                    "WayPoints": [
                        FreeCAD.Vector(start_x, start_y),
                        FreeCAD.Vector(end_x, end_y),
                    ],
                    "DimensionLabel": getRebarDimensionLabel(
                        rebar, dimension_format
                    ),
                    "VisibleRebars": "Single",
                }
            ],
            dimension_align,
        )
    else:
        basewire = rebar.Base.Shape.Wires[0]
        rebar_start_end_points = []
        rebar_mid_points = []
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
                    startwire.Edges[0].Vertexes[0].Point, view_plane
                )
                start_p2 = getProjectionToSVGPlane(
                    startwire.Edges[0].Vertexes[1].Point, view_plane
                )
                for edge in startwire.Edges[1:]:
                    if (
                        round(start_p1.x - start_p2.x) == 0
                        and round(start_p1.y - start_p2.y) == 0
                    ):
                        start_p1 = getProjectionToSVGPlane(
                            edge.Vertexes[0].Point, view_plane
                        )
                        start_p2 = getProjectionToSVGPlane(
                            edge.Vertexes[1].Point, view_plane
                        )

                if "@" in rebar_spacing_str:
                    rebars_count = int(rebar_spacing_str.split("@")[0])
                    rebars_span_length = str(
                        round(
                            rebars_count
                            * float(rebar_spacing_str.split("@")[1])
                        )
                    )
                    if "." in rebars_span_length:
                        rebars_span_length = rebars_span_length.rstrip(
                            "0"
                        ).rstrip(".")
                else:
                    rebars_count = 1
                    rebars_span_length = ""

                rebar_mid_points.append([])
                for placement in rebar.PlacementList[
                    start_rebar_index + 1 : start_rebar_index + rebars_count - 1
                ]:
                    mid_wire = basewire.copy()
                    mid_wire.Placement = placement.multiply(basewire.Placement)
                    mid_p1 = getProjectionToSVGPlane(
                        mid_wire.Vertexes[0].Point, view_plane
                    )
                    mid_p2 = getProjectionToSVGPlane(
                        mid_wire.Vertexes[1].Point, view_plane
                    )
                    rebar_mid_points[-1].append((mid_p1, mid_p2))

                endwire = basewire.copy()
                endwire.Placement = rebar.PlacementList[
                    start_rebar_index + rebars_count - 1
                ].multiply(basewire.Placement)
                end_p1 = getProjectionToSVGPlane(
                    endwire.Edges[0].Vertexes[0].Point, view_plane
                )
                end_p2 = getProjectionToSVGPlane(
                    endwire.Edges[0].Vertexes[1].Point, view_plane
                )
                for edge in endwire.Edges[1:]:
                    if (
                        round(end_p1.x - end_p2.x) == 0
                        and round(end_p1.y - end_p2.y) == 0
                    ):
                        end_p1 = getProjectionToSVGPlane(
                            edge.Vertexes[0].Point, view_plane
                        )
                        end_p2 = getProjectionToSVGPlane(
                            edge.Vertexes[1].Point, view_plane
                        )

                start_rebar_index += rebars_count
                rebar_start_end_points.append(
                    (start_p1, start_p2, end_p1, end_p2)
                )

                dimension_label = dimension_format.replace(
                    "%M", str(rebar.Mark)
                )
                dimension_label = dimension_label.replace(
                    "%C", str(rebars_count)
                )
                dimension_label = dimension_label.replace("%D", rebar_diameter)
                dimension_label = dimension_label.replace(
                    "%S", rebars_span_length
                ).strip()
                dimension_labels.append(dimension_label)
        else:
            basewire = rebar.Base.Shape.Wires[0]
            startwire = basewire.copy()
            startwire.Placement = rebar.PlacementList[0].multiply(
                basewire.Placement
            )
            start_p1 = getProjectionToSVGPlane(
                startwire.Edges[0].Vertexes[0].Point, view_plane
            )
            start_p2 = getProjectionToSVGPlane(
                startwire.Edges[0].Vertexes[1].Point, view_plane
            )
            for edge in startwire.Edges[1:]:
                if (
                    round(start_p1.x - start_p2.x) == 0
                    and round(start_p1.y - start_p2.y) == 0
                ):
                    start_p1 = getProjectionToSVGPlane(
                        edge.Vertexes[0].Point, view_plane
                    )
                    start_p2 = getProjectionToSVGPlane(
                        edge.Vertexes[1].Point, view_plane
                    )

            rebar_mid_points.append([])
            for placement in rebar.PlacementList[1:-1]:
                mid_wire = basewire.copy()
                mid_wire.Placement = placement.multiply(basewire.Placement)
                mid_p1 = getProjectionToSVGPlane(
                    mid_wire.Vertexes[0].Point, view_plane
                )
                mid_p2 = getProjectionToSVGPlane(
                    mid_wire.Vertexes[1].Point, view_plane
                )
                rebar_mid_points[-1].append((mid_p1, mid_p2))

            endwire = basewire.copy()
            endwire.Placement = rebar.PlacementList[-1].multiply(
                basewire.Placement
            )
            end_p1 = getProjectionToSVGPlane(
                endwire.Edges[0].Vertexes[0].Point, view_plane
            )
            end_p2 = getProjectionToSVGPlane(
                endwire.Edges[0].Vertexes[1].Point, view_plane
            )
            for edge in endwire.Edges[1:]:
                if (
                    round(end_p1.x - end_p2.x) == 0
                    and round(end_p1.y - end_p2.y) == 0
                ):
                    end_p1 = getProjectionToSVGPlane(
                        edge.Vertexes[0].Point, view_plane
                    )
                    end_p2 = getProjectionToSVGPlane(
                        edge.Vertexes[1].Point, view_plane
                    )

            rebar_start_end_points.append((start_p1, start_p2, end_p1, end_p2))
            dimension_labels.append(
                getRebarDimensionLabel(rebar, dimension_format)
            )

        dimension_data_list = []
        for i, (start_p1, start_p2, end_p1, end_p2) in enumerate(
            rebar_start_end_points
        ):
            dimension_mid_points = []
            # Rebars span along x-axis, so dimension lines will be either on top
            # or bottom side
            if round(rebar_span_axis.cross(view_plane.u).Length) == 0:
                # Rebars end points are more closer to top of drawing
                if abs(svg_min_y - min(start_p1.y, start_p2.y)) < abs(
                    svg_max_y - max(start_p1.y, start_p2.y)
                ):
                    dimension_align = "Top"
                    p1 = start_p1 if start_p1.y < start_p2.y else start_p2
                    p4 = end_p1 if end_p1.y < end_p2.y else end_p2
                    if round(p4.x - p1.x) == 0 and round(p4.y - p1.y) == 0:
                        if single_rebar_outer_dimension:
                            p1 = FreeCAD.Vector(
                                p1.x, dimension_top_point_y + 5 / scale
                            )
                            p4 = FreeCAD.Vector(
                                p4.x, dimension_top_point_y + 5 / scale
                            )
                    elif multi_rebar_outer_dimension:
                        p1 = FreeCAD.Vector(
                            p1.x, dimension_top_point_y + 5 / scale
                        )
                        p4 = FreeCAD.Vector(
                            p4.x, dimension_top_point_y + 5 / scale
                        )
                    p2 = FreeCAD.Vector(p1.x, dimension_top_point_y)
                    p3 = FreeCAD.Vector(p4.x, dimension_top_point_y)
                    for mid_points in rebar_mid_points[i]:
                        dimension_mid_points.append(
                            FreeCAD.Vector(
                                min(mid_points, key=lambda p: p.y).x,
                                dimension_top_point_y,
                            )
                        )
                # Rebars end points are more closer to bottom of drawing
                else:
                    dimension_align = "Bottom"
                    p1 = start_p1 if start_p1.y > start_p2.y else start_p2
                    p4 = end_p1 if end_p1.y > end_p2.y else end_p2
                    if round(p4.x - p1.x) == 0 and round(p4.y - p1.y) == 0:
                        if single_rebar_outer_dimension:
                            p1 = FreeCAD.Vector(
                                p1.x, dimension_bottom_point_y - 5 / scale
                            )
                            p4 = FreeCAD.Vector(
                                p4.x, dimension_bottom_point_y - 5 / scale
                            )
                    elif multi_rebar_outer_dimension:
                        p1 = FreeCAD.Vector(
                            p1.x, dimension_bottom_point_y - 5 / scale
                        )
                        p4 = FreeCAD.Vector(
                            p4.x, dimension_bottom_point_y - 5 / scale
                        )
                    p2 = FreeCAD.Vector(p1.x, dimension_bottom_point_y)
                    p3 = FreeCAD.Vector(p4.x, dimension_bottom_point_y)
                    for mid_points in rebar_mid_points[i]:
                        dimension_mid_points.append(
                            FreeCAD.Vector(
                                max(mid_points, key=lambda p: p.y).x,
                                dimension_bottom_point_y,
                            )
                        )
            # Rebars span along y-axis, so dimension lines will be either on
            # left or right side
            else:
                # Rebars end points are more closer to left of drawing
                if abs(svg_min_x - min(start_p1.x, start_p2.x)) < abs(
                    svg_max_x - max(start_p1.x, start_p2.x)
                ):
                    dimension_align = "Left"
                    p1 = start_p1 if start_p1.x < start_p2.x else start_p2
                    p4 = end_p1 if end_p1.x < end_p2.x else end_p2
                    if round(p4.x - p1.x) == 0 and round(p4.y - p1.y) == 0:
                        if single_rebar_outer_dimension:
                            p1 = FreeCAD.Vector(
                                dimension_left_point_x + 5 / scale, p1.y
                            )
                            p4 = FreeCAD.Vector(
                                dimension_left_point_x + 5 / scale, p4.y
                            )
                    elif multi_rebar_outer_dimension:
                        p1 = FreeCAD.Vector(
                            dimension_left_point_x + 5 / scale, p1.y
                        )
                        p4 = FreeCAD.Vector(
                            dimension_left_point_x + 5 / scale, p4.y
                        )
                    p2 = FreeCAD.Vector(dimension_left_point_x, p1.y)
                    p3 = FreeCAD.Vector(dimension_left_point_x, p4.y)
                    for mid_points in rebar_mid_points[i]:
                        dimension_mid_points.append(
                            FreeCAD.Vector(
                                dimension_left_point_x,
                                min(mid_points, key=lambda p: p.x).y,
                            )
                        )
                # Rebars end points are more closer to right of drawing
                else:
                    dimension_align = "Right"
                    p1 = start_p1 if start_p1.x > start_p2.x else start_p2
                    p4 = end_p1 if end_p1.x > end_p2.x else end_p2
                    if round(p4.x - p1.x) == 0 and round(p4.y - p1.y) == 0:
                        if single_rebar_outer_dimension:
                            p1 = FreeCAD.Vector(
                                dimension_right_point_x - 5 / scale, p1.y
                            )
                            p4 = FreeCAD.Vector(
                                dimension_right_point_x - 5 / scale, p4.y
                            )
                    elif multi_rebar_outer_dimension:
                        p1 = FreeCAD.Vector(
                            dimension_right_point_x - 5 / scale, p1.y
                        )
                        p4 = FreeCAD.Vector(
                            dimension_right_point_x - 5 / scale, p4.y
                        )
                    p2 = FreeCAD.Vector(dimension_right_point_x, p1.y)
                    p3 = FreeCAD.Vector(dimension_right_point_x, p4.y)
                    for mid_points in rebar_mid_points[i]:
                        dimension_mid_points.append(
                            FreeCAD.Vector(
                                dimension_right_point_x,
                                max(mid_points, key=lambda p: p.x).y,
                            )
                        )
            if round(p4.x - p1.x) == 0 and round(p4.y - p1.y) == 0:
                dimension_data_list.append(
                    {
                        "WayPoints": [p2, p1],
                        "DimensionLabel": dimension_labels[i],
                        "VisibleRebars": "Single",
                    }
                )
            else:
                way_points = [p1, p2]
                way_points.extend(dimension_mid_points)
                way_points.extend([p3, p4])
                dimension_data_list.append(
                    {
                        "WayPoints": way_points,
                        "DimensionLabel": dimension_labels[i],
                        "VisibleRebars": "Multiple",
                    }
                )
        return dimension_data_list, dimension_align


def getBentRebarDimensionData(
    rebar,
    dimension_format,
    view_plane,
    dimension_left_point_x,
    dimension_right_point_x,
    dimension_top_point_y,
    dimension_bottom_point_y,
    svg_min_x,
    svg_min_y,
    svg_max_x,
    svg_max_y,
    scale,
    single_rebar_outer_dimension,
    multi_rebar_outer_dimension,
):
    drawing_plane_normal = view_plane.axis
    rebar_span_axis = getRebarsSpanAxis(rebar)
    # Bent rebars span axis is parallel to drawing plane normal
    # Thus, only one rebar will be visible
    if (
        round(drawing_plane_normal.cross(rebar_span_axis).Length) == 0
        or rebar.Amount == 1
    ):
        basewire = rebar.Base.Shape.Wires[0].copy()
        basewire.Placement = rebar.PlacementList[0].multiply(basewire.Placement)
        edges = Part.__sortEdges__(basewire.Edges)
        mid_edge = edges[int(len(edges) / 2)]
        p1 = getProjectionToSVGPlane(mid_edge.Vertexes[0].Point, view_plane)
        p2 = getProjectionToSVGPlane(mid_edge.Vertexes[1].Point, view_plane)

        # Rebar is more horizontal, so dimension line will be vertical
        if abs(p2.y - p1.y) <= abs(p2.x - p1.x):
            start_x = end_x = random.randint(
                int(min(p1.x, p2.x)), int(max(p1.x, p2.x))
            )
            # Rebar is more closer to top of drawing
            if abs(svg_min_y - min(p1.y, p2.y)) < abs(
                svg_max_y - max(p1.y, p2.y)
            ):
                dimension_align = "Top"
                start_y = dimension_top_point_y
            # Rebar is more closer to bottom of drawing
            else:
                dimension_align = "Bottom"
                start_y = dimension_bottom_point_y

            if single_rebar_outer_dimension:
                if dimension_align == "Top":
                    end_y = dimension_top_point_y + 5 / scale
                else:
                    end_y = dimension_bottom_point_y - 5 / scale
            else:
                end_y = (
                    (end_x - p1.x) * (p2.y - p1.y) / (p2.x - p1.x) + p1.y
                    if (p2.x - p1.x) != 0
                    else p1.y
                )

        # Rebar is more vertical, so dimension line will be horizontal
        else:
            start_y = end_y = random.randint(
                int(min(p1.y, p2.y)), int(max(p1.y, p2.y))
            )
            # Rebar is more closer to left of drawing
            if abs(svg_min_x - min(p1.x, p2.x)) < abs(
                svg_max_x - max(p1.x, p2.x)
            ):
                dimension_align = "Left"
                start_x = dimension_left_point_x
            # Rebar is more closer to right of drawing
            else:
                dimension_align = "Right"
                start_x = dimension_right_point_x
            if single_rebar_outer_dimension:
                if dimension_align == "Left":
                    end_x = dimension_left_point_x + 5 / scale
                else:
                    end_x = dimension_right_point_x - 5 / scale
            else:
                end_x = (end_y - p1.y) * (p2.x - p1.x) / (p2.y - p1.y) + p1.x

        return (
            [
                {
                    "WayPoints": [
                        FreeCAD.Vector(start_x, start_y),
                        FreeCAD.Vector(end_x, end_y),
                    ],
                    "DimensionLabel": getRebarDimensionLabel(
                        rebar, dimension_format
                    ),
                    "VisibleRebars": "Single",
                }
            ],
            dimension_align,
        )
    else:
        basewire = rebar.Base.Shape.Wires[0]
        _basewire = basewire.copy()
        _basewire.Placement = rebar.PlacementList[0].multiply(
            basewire.Placement
        )
        edges = Part.__sortEdges__(_basewire.Edges)
        mid_edge = edges[int(len(edges) / 2)]
        if round(mid_edge.Curve.Direction.cross(view_plane.axis).Length) == 0:
            full_length_visible = False
        else:
            full_length_visible = True

        rebar_start_end_points = []
        rebar_mid_points = []
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
                if full_length_visible:
                    start_p1 = getProjectionToSVGPlane(
                        startwire.Vertexes[0].Point, view_plane
                    )
                    start_p2 = getProjectionToSVGPlane(
                        startwire.Vertexes[-1].Point, view_plane
                    )
                else:
                    start_p1 = getProjectionToSVGPlane(
                        startwire.Edges[1].Vertexes[0].Point, view_plane
                    )
                    start_p2 = getProjectionToSVGPlane(
                        startwire.Edges[1].Vertexes[1].Point, view_plane
                    )

                if "@" in rebar_spacing_str:
                    rebars_count = int(rebar_spacing_str.split("@")[0])
                    rebars_span_length = str(
                        round(
                            rebars_count
                            * float(rebar_spacing_str.split("@")[1])
                        )
                    )
                    if "." in rebars_span_length:
                        rebars_span_length = rebars_span_length.rstrip(
                            "0"
                        ).rstrip(".")
                else:
                    rebars_count = 1
                    rebars_span_length = ""

                rebar_mid_points.append([])
                for placement in rebar.PlacementList[
                    start_rebar_index + 1 : start_rebar_index + rebars_count - 1
                ]:
                    mid_wire = basewire.copy()
                    mid_wire.Placement = placement.multiply(basewire.Placement)
                    if full_length_visible:
                        mid_p1 = getProjectionToSVGPlane(
                            mid_wire.Vertexes[0].Point, view_plane
                        )
                        mid_p2 = getProjectionToSVGPlane(
                            mid_wire.Vertexes[-1].Point, view_plane
                        )
                    else:
                        mid_p1 = getProjectionToSVGPlane(
                            mid_wire.Edges[1].Vertexes[0].Point, view_plane
                        )
                        mid_p2 = getProjectionToSVGPlane(
                            mid_wire.Edges[1].Vertexes[1].Point, view_plane
                        )
                    rebar_mid_points[-1].append((mid_p1, mid_p2))

                endwire = basewire.copy()
                endwire.Placement = rebar.PlacementList[
                    start_rebar_index + rebars_count - 1
                ].multiply(basewire.Placement)
                if full_length_visible:
                    end_p1 = getProjectionToSVGPlane(
                        endwire.Vertexes[0].Point, view_plane
                    )
                    end_p2 = getProjectionToSVGPlane(
                        endwire.Vertexes[-1].Point, view_plane
                    )
                else:
                    end_p1 = getProjectionToSVGPlane(
                        endwire.Edges[1].Vertexes[0].Point, view_plane
                    )
                    end_p2 = getProjectionToSVGPlane(
                        endwire.Edges[1].Vertexes[1].Point, view_plane
                    )

                start_rebar_index += rebars_count
                rebar_start_end_points.append(
                    (start_p1, start_p2, end_p1, end_p2)
                )

                dimension_label = dimension_format.replace(
                    "%M", str(rebar.Mark)
                )
                dimension_label = dimension_label.replace(
                    "%C", str(rebars_count)
                )
                dimension_label = dimension_label.replace("%D", rebar_diameter)
                dimension_label = dimension_label.replace(
                    "%S", rebars_span_length
                ).strip()
                dimension_labels.append(dimension_label)
        else:
            startwire = basewire.copy()
            startwire.Placement = rebar.PlacementList[0].multiply(
                basewire.Placement
            )
            if full_length_visible:
                start_p1 = getProjectionToSVGPlane(
                    startwire.Vertexes[0].Point, view_plane
                )
                start_p2 = getProjectionToSVGPlane(
                    startwire.Vertexes[-1].Point, view_plane
                )
            else:
                start_p1 = getProjectionToSVGPlane(
                    startwire.Edges[1].Vertexes[0].Point, view_plane
                )
                start_p2 = getProjectionToSVGPlane(
                    startwire.Edges[1].Vertexes[1].Point, view_plane
                )

            rebar_mid_points.append([])
            for placement in rebar.PlacementList[1:-1]:
                mid_wire = basewire.copy()
                mid_wire.Placement = placement.multiply(basewire.Placement)
                if full_length_visible:
                    mid_p1 = getProjectionToSVGPlane(
                        mid_wire.Vertexes[0].Point, view_plane
                    )
                    mid_p2 = getProjectionToSVGPlane(
                        mid_wire.Vertexes[-1].Point, view_plane
                    )
                else:
                    mid_p1 = getProjectionToSVGPlane(
                        mid_wire.Edges[1].Vertexes[0].Point, view_plane
                    )
                    mid_p2 = getProjectionToSVGPlane(
                        mid_wire.Edges[1].Vertexes[1].Point, view_plane
                    )
                rebar_mid_points[-1].append((mid_p1, mid_p2))

            endwire = basewire.copy()
            endwire.Placement = rebar.PlacementList[-1].multiply(
                basewire.Placement
            )
            if full_length_visible:
                end_p1 = getProjectionToSVGPlane(
                    endwire.Vertexes[0].Point, view_plane
                )
                end_p2 = getProjectionToSVGPlane(
                    endwire.Vertexes[-1].Point, view_plane
                )
            else:
                end_p1 = getProjectionToSVGPlane(
                    endwire.Edges[1].Vertexes[0].Point, view_plane
                )
                end_p2 = getProjectionToSVGPlane(
                    endwire.Edges[1].Vertexes[1].Point, view_plane
                )

            rebar_start_end_points.append((start_p1, start_p2, end_p1, end_p2))
            dimension_labels.append(
                getRebarDimensionLabel(rebar, dimension_format)
            )

        dimension_data_list = []
        for i, (start_p1, start_p2, end_p1, end_p2) in enumerate(
            rebar_start_end_points
        ):
            dimension_mid_points = []
            # Rebars span along x-axis, so dimension lines will be either on top
            # or bottom side
            if round(rebar_span_axis.cross(view_plane.u).Length) == 0:
                # Rebars end points are more closer to top of drawing
                if abs(svg_min_y - min(start_p1.y, start_p2.y)) < abs(
                    svg_max_y - max(start_p1.y, start_p2.y)
                ):
                    dimension_align = "Top"
                    p1 = start_p1 if start_p1.y < start_p2.y else start_p2
                    p4 = end_p1 if end_p1.y < end_p2.y else end_p2
                    if round(p4.x - p1.x) == 0 and round(p4.y - p1.y) == 0:
                        if single_rebar_outer_dimension:
                            p1 = FreeCAD.Vector(
                                p1.x, dimension_top_point_y + 5 / scale
                            )
                            p4 = FreeCAD.Vector(
                                p4.x, dimension_top_point_y + 5 / scale
                            )
                    elif multi_rebar_outer_dimension:
                        p1 = FreeCAD.Vector(
                            p1.x, dimension_top_point_y + 5 / scale
                        )
                        p4 = FreeCAD.Vector(
                            p4.x, dimension_top_point_y + 5 / scale
                        )
                    p2 = FreeCAD.Vector(p1.x, dimension_top_point_y)
                    p3 = FreeCAD.Vector(p4.x, dimension_top_point_y)
                    for mid_points in rebar_mid_points[i]:
                        dimension_mid_points.append(
                            FreeCAD.Vector(
                                min(mid_points, key=lambda p: p.y).x,
                                dimension_top_point_y,
                            )
                        )
                # Rebars end points are more closer to bottom of drawing
                else:
                    dimension_align = "Bottom"
                    p1 = start_p1 if start_p1.y > start_p2.y else start_p2
                    p4 = end_p1 if end_p1.y > end_p2.y else end_p2
                    if round(p4.x - p1.x) == 0 and round(p4.y - p1.y) == 0:
                        if single_rebar_outer_dimension:
                            p1 = FreeCAD.Vector(
                                p1.x, dimension_bottom_point_y - 5 / scale
                            )
                            p4 = FreeCAD.Vector(
                                p4.x, dimension_bottom_point_y - 5 / scale
                            )
                    elif multi_rebar_outer_dimension:
                        p1 = FreeCAD.Vector(
                            p1.x, dimension_bottom_point_y - 5 / scale
                        )
                        p4 = FreeCAD.Vector(
                            p4.x, dimension_bottom_point_y - 5 / scale
                        )
                    p2 = FreeCAD.Vector(p1.x, dimension_bottom_point_y)
                    p3 = FreeCAD.Vector(p4.x, dimension_bottom_point_y)
                    for mid_points in rebar_mid_points[i]:
                        dimension_mid_points.append(
                            FreeCAD.Vector(
                                max(mid_points, key=lambda p: p.y).x,
                                dimension_bottom_point_y,
                            )
                        )
            # Rebars span along y-axis, so dimension lines will be either on
            # left or right side
            else:
                # Rebars end points are more closer to left of drawing
                if abs(svg_min_x - min(start_p1.x, start_p2.x)) < abs(
                    svg_max_x - max(start_p1.x, start_p2.x)
                ):
                    dimension_align = "Left"
                    p1 = start_p1 if start_p1.x < start_p2.x else start_p2
                    p4 = end_p1 if end_p1.x < end_p2.x else end_p2
                    if round(p4.x - p1.x) == 0 and round(p4.y - p1.y) == 0:
                        if single_rebar_outer_dimension:
                            p1 = FreeCAD.Vector(
                                dimension_left_point_x + 5 / scale, p1.y
                            )
                            p4 = FreeCAD.Vector(
                                dimension_left_point_x + 5 / scale, p4.y
                            )
                    elif multi_rebar_outer_dimension:
                        p1 = FreeCAD.Vector(
                            dimension_left_point_x + 5 / scale, p1.y
                        )
                        p4 = FreeCAD.Vector(
                            dimension_left_point_x + 5 / scale, p4.y
                        )
                    p2 = FreeCAD.Vector(dimension_left_point_x, p1.y)
                    p3 = FreeCAD.Vector(dimension_left_point_x, p4.y)
                    for mid_points in rebar_mid_points[i]:
                        dimension_mid_points.append(
                            FreeCAD.Vector(
                                dimension_left_point_x,
                                min(mid_points, key=lambda p: p.x).y,
                            )
                        )
                # Rebars end points are more closer to right of drawing
                else:
                    dimension_align = "Right"
                    p1 = start_p1 if start_p1.x > start_p2.x else start_p2
                    p4 = end_p1 if end_p1.x > end_p2.x else end_p2
                    if round(p4.x - p1.x) == 0 and round(p4.y - p1.y) == 0:
                        if single_rebar_outer_dimension:
                            p1 = FreeCAD.Vector(
                                dimension_right_point_x - 5 / scale, p1.y
                            )
                            p4 = FreeCAD.Vector(
                                dimension_right_point_x - 5 / scale, p4.y
                            )
                    elif multi_rebar_outer_dimension:
                        p1 = FreeCAD.Vector(
                            dimension_right_point_x - 5 / scale, p1.y
                        )
                        p4 = FreeCAD.Vector(
                            dimension_right_point_x - 5 / scale, p4.y
                        )
                    p2 = FreeCAD.Vector(dimension_right_point_x, p1.y)
                    p3 = FreeCAD.Vector(dimension_right_point_x, p4.y)
                    for mid_points in rebar_mid_points[i]:
                        dimension_mid_points.append(
                            FreeCAD.Vector(
                                dimension_right_point_x,
                                max(mid_points, key=lambda p: p.x).y,
                            )
                        )
            if round(p4.x - p1.x) == 0 and round(p4.y - p1.y) == 0:
                dimension_data_list.append(
                    {
                        "WayPoints": [p2, p1],
                        "DimensionLabel": dimension_labels[i],
                        "VisibleRebars": "Single",
                    }
                )
            else:
                way_points = [p1, p2]
                way_points.extend(dimension_mid_points)
                way_points.extend([p3, p4])
                dimension_data_list.append(
                    {
                        "WayPoints": way_points,
                        "DimensionLabel": dimension_labels[i],
                        "VisibleRebars": "Multiple",
                    }
                )
        return dimension_data_list, dimension_align


def getHelicalRebarDimensionData(
    rebar,
    dimension_format,
    view_plane,
    dimension_left_point_x,
    dimension_right_point_x,
    dimension_top_point_y,
    dimension_bottom_point_y,
    svg_min_x,
    svg_min_y,
    svg_max_x,
    svg_max_y,
    scale,
    single_rebar_outer_dimension,
    multi_rebar_outer_dimension,
):
    drawing_plane_normal = view_plane.axis
    rebar_span_axis = getRebarsSpanAxis(rebar)
    # Helical rebars span axis is parallel to drawing plane normal
    # Thus, helical rebar will be visible as circle
    if round(drawing_plane_normal.cross(rebar_span_axis).Length) == 0:
        basewire = rebar.Base.Shape.Wires[0].copy()
        basewire.Placement = rebar.PlacementList[0].multiply(basewire.Placement)
        point = getProjectionToSVGPlane(
            basewire.Vertexes[
                random.randint(
                    int(min(0, len(basewire.Vertexes) - 1)),
                    int(max(0, len(basewire.Vertexes) - 1)),
                )
            ].Point,
            view_plane,
        )
        left_dist = DraftVecUtils.dist(
            point, FreeCAD.Vector(svg_min_x, point.y)
        )
        right_dist = DraftVecUtils.dist(
            point, FreeCAD.Vector(svg_max_x, point.y)
        )
        top_dist = DraftVecUtils.dist(point, FreeCAD.Vector(point.x, svg_min_y))
        bottom_dist = DraftVecUtils.dist(
            point, FreeCAD.Vector(point.x, svg_max_y)
        )
        min_dist = min(left_dist, right_dist, top_dist, bottom_dist)

        # Dimension point is more closer to top of drawing
        if top_dist == min_dist:
            dimension_align = "Top"
            start_x = point.x
            start_y = dimension_top_point_y
            if single_rebar_outer_dimension:
                point.y = start_y + 5 / scale
        # Dimension point is more closer to bottom of drawing
        elif bottom_dist == min_dist:
            dimension_align = "Bottom"
            start_x = point.x
            start_y = dimension_bottom_point_y
            if single_rebar_outer_dimension:
                point.y = start_y - 5 / scale
        # Dimension point is more closer to left of drawing
        elif left_dist == min_dist:
            dimension_align = "Left"
            start_x = dimension_left_point_x
            start_y = point.y
            if single_rebar_outer_dimension:
                point.x = start_x + 5 / scale
        # Dimension point is more closer to right of drawing
        else:
            dimension_align = "Right"
            start_x = dimension_right_point_x
            start_y = point.y
            if single_rebar_outer_dimension:
                point.x = start_x - 5 / scale

        return (
            [
                {
                    "WayPoints": [
                        FreeCAD.Vector(start_x, start_y),
                        FreeCAD.Vector(point.x, point.y),
                    ],
                    "DimensionLabel": getRebarDimensionLabel(
                        rebar, dimension_format
                    ),
                    "VisibleRebars": "Single",
                }
            ],
            dimension_align,
        )
    else:
        basewire = rebar.Base.Shape.Wires[0].copy()
        basewire.Placement = rebar.PlacementList[0].multiply(basewire.Placement)
        p1 = getProjectionToSVGPlane(basewire.Vertexes[0].Point, view_plane)
        p4 = getProjectionToSVGPlane(basewire.Vertexes[-1].Point, view_plane)

        dimension_mid_points = []
        # Rebars span along x-axis, so dimension lines will be either on top
        # or bottom side
        if round(rebar_span_axis.cross(view_plane.u).Length) == 0:
            # Rebars end points are more closer to top of drawing
            if abs(svg_min_y - min(p1.y, p4.y)) < abs(
                svg_max_y - max(p1.y, p4.y)
            ):
                dimension_align = "Top"
                p2 = FreeCAD.Vector(p1.x, dimension_top_point_y)
                p3 = FreeCAD.Vector(p4.x, dimension_top_point_y)
                if multi_rebar_outer_dimension:
                    p1.y = dimension_top_point_y + 5 / scale
                    p4.y = dimension_top_point_y + 5 / scale
            # Rebars end points are more closer to bottom of drawing
            else:
                dimension_align = "Bottom"
                p2 = FreeCAD.Vector(p1.x, dimension_bottom_point_y)
                p3 = FreeCAD.Vector(p4.x, dimension_bottom_point_y)
                if multi_rebar_outer_dimension:
                    p1.y = dimension_bottom_point_y - 5 / scale
                    p4.y = dimension_bottom_point_y - 5 / scale
            for point_x in range(
                int(min(p1.x, p4.x)),
                int(max(p1.x, p4.x)),
                int(rebar.Base.Pitch.Value),
            ):
                dimension_mid_points.append(FreeCAD.Vector(point_x, p2.y))
        # Rebars span along y-axis, so dimension lines will be either on
        # left or right side
        else:
            # Rebars end points are more closer to left of drawing
            if abs(svg_min_x - min(p1.x, p4.x)) < abs(
                svg_max_x - max(p1.x, p4.x)
            ):
                dimension_align = "Left"
                p2 = FreeCAD.Vector(dimension_left_point_x, p1.y)
                p3 = FreeCAD.Vector(dimension_left_point_x, p4.y)
                if multi_rebar_outer_dimension:
                    p1.x = dimension_left_point_x + 5 / scale
                    p4.x = dimension_left_point_x + 5 / scale
            # Rebars end points are more closer to right of drawing
            else:
                dimension_align = "Right"
                p2 = FreeCAD.Vector(dimension_right_point_x, p1.y)
                p3 = FreeCAD.Vector(dimension_right_point_x, p4.y)
                if multi_rebar_outer_dimension:
                    p1.x = dimension_right_point_x - 5 / scale
                    p4.x = dimension_right_point_x - 5 / scale
            for point_y in range(
                int(min(p1.y, p4.y)),
                int(max(p1.y, p4.y)),
                int(rebar.Base.Pitch.Value),
            ):
                dimension_mid_points.append(FreeCAD.Vector(p2.x, point_y))

        way_points = [p1, p2]
        way_points.extend(dimension_mid_points)
        way_points.extend([p3, p4])
        return (
            [
                {
                    "WayPoints": way_points,
                    "DimensionLabel": getRebarDimensionLabel(
                        rebar, dimension_format
                    ),
                    "VisibleRebars": "Multiple",
                }
            ],
            dimension_align,
        )


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
    scale,
    single_rebar_outer_dimension,
    multi_rebar_outer_dimension,
):
    if rebar.RebarShape == "Stirrup":
        dimension_data = getStirrupDimensionData(
            rebar,
            dimension_format,
            view_plane,
            svg_min_x - dimension_left_offset,
            svg_max_x + dimension_right_offset,
            svg_min_y - dimension_top_offset,
            svg_max_y + dimension_bottom_offset,
            svg_min_x,
            svg_min_y,
            svg_max_x,
            svg_max_y,
            scale,
            single_rebar_outer_dimension,
            multi_rebar_outer_dimension,
        )
    elif rebar.RebarShape == "StraightRebar":
        dimension_data = getStraightRebarDimensionData(
            rebar,
            dimension_format,
            view_plane,
            svg_min_x - dimension_left_offset,
            svg_max_x + dimension_right_offset,
            svg_min_y - dimension_top_offset,
            svg_max_y + dimension_bottom_offset,
            svg_min_x,
            svg_min_y,
            svg_max_x,
            svg_max_y,
            scale,
            single_rebar_outer_dimension,
            multi_rebar_outer_dimension,
        )
    elif rebar.RebarShape == "LShapeRebar":
        dimension_data = getLShapeRebarDimensionData(
            rebar,
            dimension_format,
            view_plane,
            svg_min_x - dimension_left_offset,
            svg_max_x + dimension_right_offset,
            svg_min_y - dimension_top_offset,
            svg_max_y + dimension_bottom_offset,
            svg_min_x,
            svg_min_y,
            svg_max_x,
            svg_max_y,
            scale,
            single_rebar_outer_dimension,
            multi_rebar_outer_dimension,
        )
    elif rebar.RebarShape == "UShapeRebar":
        dimension_data = getUShapeRebarDimensionData(
            rebar,
            dimension_format,
            view_plane,
            svg_min_x - dimension_left_offset,
            svg_max_x + dimension_right_offset,
            svg_min_y - dimension_top_offset,
            svg_max_y + dimension_bottom_offset,
            svg_min_x,
            svg_min_y,
            svg_max_x,
            svg_max_y,
            scale,
            single_rebar_outer_dimension,
            multi_rebar_outer_dimension,
        )
    elif rebar.RebarShape == "BentShapeRebar":
        dimension_data = getBentRebarDimensionData(
            rebar,
            dimension_format,
            view_plane,
            svg_min_x - dimension_left_offset,
            svg_max_x + dimension_right_offset,
            svg_min_y - dimension_top_offset,
            svg_max_y + dimension_bottom_offset,
            svg_min_x,
            svg_min_y,
            svg_max_x,
            svg_max_y,
            scale,
            single_rebar_outer_dimension,
            multi_rebar_outer_dimension,
        )
    elif rebar.RebarShape == "HelicalRebar":
        dimension_data = getHelicalRebarDimensionData(
            rebar,
            dimension_format,
            view_plane,
            svg_min_x - dimension_left_offset,
            svg_max_x + dimension_right_offset,
            svg_min_y - dimension_top_offset,
            svg_max_y + dimension_bottom_offset,
            svg_min_x,
            svg_min_y,
            svg_max_x,
            svg_max_y,
            scale,
            single_rebar_outer_dimension,
            multi_rebar_outer_dimension,
        )
    return dimension_data
