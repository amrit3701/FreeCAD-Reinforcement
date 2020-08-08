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


import math
from typing import Union, List, Tuple
from xml.etree import ElementTree

import DraftGeomUtils
import DraftVecUtils
import FreeCAD
import Part
import WorkingPlane

from ReinforcementDrawing.ReinforcementDrawingfunc import (
    getRebarsSpanAxis,
    getSVGPlaneFromAxis,
    getProjectionToSVGPlane,
    getRoundCornerSVG,
    getRebarColor,
)
from SVGfunc import (
    getSVGRootElement,
    getPointSVG,
    getLineSVG,
    getSVGTextElement,
)


def getVertexesMinMaxXY(
    vertex_list: List[Part.Vertex], view_plane: WorkingPlane.Plane
) -> Tuple[float, float, float, float]:
    """Returns min_x, min_y, max_x, max_y for vertex_list, when each vertex
    is projected on view_plane.

    Parameters
    ----------
    vertex_list: list of <Part.Vertex>
        Input vertex list.
    view_plane: WorkingPlane.Plane
        view plane to project vertexes on it.

    Returns
    -------
    min_x: float
        The minimum x_coordinate value when each vertex is projected on
        view_plane.
    min_y: float
        The minimum y_coordinate value when each vertex is projected on
        view_plane.
    max_x: float
        The maximum x_coordinate value when each vertex is projected on
        view_plane.
    max_y: float
        The maximum y_coordinate value when each vertex is projected on
        view_plane.
    """
    point = getProjectionToSVGPlane(vertex_list[0].Point, view_plane)
    min_x = point.x
    min_y = point.y
    max_x = point.x
    max_y = point.y
    for vertex in vertex_list[1:]:
        point = getProjectionToSVGPlane(vertex.Point, view_plane)
        min_x = min(point.x, min_x)
        min_y = min(point.y, min_y)
        max_x = max(point.x, max_x)
        max_y = max(point.y, max_y)
    return min_x, min_y, max_x, max_y


def getRebarShapeSVG(
    rebar,
    view_direction: Union[FreeCAD.Vector, WorkingPlane.Plane] = FreeCAD.Vector(
        0, 0, 0
    ),
    rebar_stroke_width: float = 0.35,
    rebar_color_style: str = "shape color",
    dimension_font_family: str = "DejaVu Sans",
    dimension_font_size: float = 3,
    scale: float = 1,
) -> ElementTree.Element:
    """Generate and return rebar shape svg.

    Parameters
    ----------
    rebar: <ArchRebar._Rebar> or <rebar2.BaseRebar>
        Rebar to generate its shape svg.
    view_direction: FreeCAD.Vector or WorkingPlane.Plane, optional
        The view point direction for rebar shape.
        Default is FreeCAD.Vector(0, 0, 0) to automatically choose
        view_direction.
    rebar_stroke_width: float, optional
        The stroke-width of rebar in svg.
        Default is 0.35
    rebar_color_style: {"shape color", "color_name", "hex_value_of_color"}
        The color style of rebar.
        "shape color" means select color of rebar shape.
    dimension_font_family: str, optional
        The font-family of dimension text.
        Default is "DejaVu Sans".
    dimension_font_size: float, optional
        The font-size of dimension text.
        Default is 3
    scale: float, optional
        The scale value to scale rebar svg. The scale parameter helps to
        scale down rebar_stroke_width and dimension_font_size to make them
        resolution independent.
        Default is 1

    Returns
    -------
    ElementTree.Element
        Returns the generated rebar shape svg.
    """
    if isinstance(view_direction, FreeCAD.Vector):
        if DraftVecUtils.isNull(view_direction):
            view_direction = getRebarsSpanAxis(rebar)
        view_plane = getSVGPlaneFromAxis(view_direction)
    elif isinstance(view_direction, WorkingPlane.Plane):
        view_plane = view_direction
    else:
        FreeCAD.Console.PrintError(
            "Invalid view_direction type. Supported view_direction types: "
            "FreeCAD.Vector, WorkingPlane.Plane\n"
        )
        return ElementTree.Element("g")

    # Get user preferred unit precision
    precision: int = FreeCAD.ParamGet(
        "User parameter:BaseApp/Preferences/Units"
    ).GetInt("Decimals")

    # Scale down rebar_stroke_width and dimension_font_size to make them
    # resolution independent
    rebar_stroke_width /= scale
    dimension_font_size /= scale

    rebar_color = getRebarColor(rebar, rebar_color_style)
    rebar_shape_svg = ElementTree.Element("g", attrib={"id": str(rebar.Name)})
    rebar_edges_svg = ElementTree.Element("g")
    edge_dimension_svg = ElementTree.Element("g")
    rebar_shape_svg.extend([rebar_edges_svg, edge_dimension_svg])

    basewire = rebar.Base.Shape.Wires[0].copy()
    fillet_radius = rebar.Rounding * rebar.Diameter.Value
    if fillet_radius:
        fillet_basewire = DraftGeomUtils.filletWire(basewire, fillet_radius)
    else:
        fillet_basewire = basewire

    edges = Part.__sortEdges__(fillet_basewire.Edges)
    straight_edges = Part.__sortEdges__(basewire.Edges)
    current_straight_edge_index = 0
    for edge in edges:
        if DraftGeomUtils.geomType(edge) == "Line":
            p1 = getProjectionToSVGPlane(edge.Vertexes[0].Point, view_plane)
            p2 = getProjectionToSVGPlane(edge.Vertexes[1].Point, view_plane)
            # Create Edge svg
            if round(p1.x) == round(p2.x) and round(p1.y) == round(p2.y):
                edge_svg = getPointSVG(
                    p1, radius=2 * rebar_stroke_width, fill=rebar_color
                )
            else:
                edge_svg = getLineSVG(p1, p2, rebar_stroke_width, rebar_color)
            # Create edge dimension svg
            mid_point = FreeCAD.Vector((p1.x + p2.x) / 2, (p1.y + p2.y) / 2)
            dimension_rotation = (
                math.degrees(math.atan((p2.y - p1.y) / (p2.x - p1.x)))
                if round(p2.x) != round(p1.x)
                else -90
            )
            edge_dimension_svg.append(
                getSVGTextElement(
                    round(
                        straight_edges[current_straight_edge_index].Length,
                        precision,
                    ),
                    mid_point.x,
                    mid_point.y - rebar_stroke_width * 2,
                    dimension_font_family,
                    dimension_font_size,
                    "middle",
                )
            )
            edge_dimension_svg[-1].set(
                "transform",
                "rotate({} {} {})".format(
                    dimension_rotation, round(mid_point.x), round(mid_point.y)
                ),
            )
            current_straight_edge_index += 1
        elif DraftGeomUtils.geomType(edge) == "Circle":
            p1 = getProjectionToSVGPlane(edge.Vertexes[0].Point, view_plane)
            p2 = getProjectionToSVGPlane(edge.Vertexes[1].Point, view_plane)
            if round(p1.x) == round(p2.x) or round(p1.y) == round(p2.y):
                edge_svg = getLineSVG(p1, p2, rebar_stroke_width, rebar_color)
            else:
                edge_svg = getRoundCornerSVG(
                    edge,
                    rebar.Rounding * rebar.Diameter.Value,
                    view_plane,
                    rebar_stroke_width,
                    rebar_color,
                )
        else:
            edge_svg = ElementTree.Element("g")
        rebar_edges_svg.append(edge_svg)

    # Move (min_x, min_y) of basewire to (0, 0) so that entire basewire
    # should be visible in svg view box
    min_x, min_y, max_x, max_y = getVertexesMinMaxXY(
        fillet_basewire.Vertexes, view_plane
    )
    min_x -= dimension_font_size + rebar_stroke_width * 2
    min_y -= dimension_font_size + rebar_stroke_width * 2
    max_x += dimension_font_size + rebar_stroke_width * 2
    max_y += dimension_font_size + rebar_stroke_width * 2
    rebar_shape_svg.set(
        "transform",
        "scale({}) translate({} {})".format(
            scale, round(-min_x), round(-min_y)
        ),
    )

    svg = getSVGRootElement()
    svg.append(rebar_shape_svg)
    svg_width = round((max_x - min_x) * scale)
    svg_height = round((max_y - min_y) * scale)
    svg.set("width", "{}mm".format(svg_width))
    svg.set("height", "{}mm".format(svg_height))
    svg.set("viewBox", "0 0 {} {}".format(svg_width, svg_height))

    return svg
