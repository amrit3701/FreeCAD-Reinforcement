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

__title__ = "Reinforcement Drawing"
__author__ = "Suraj"
__url__ = "https://www.freecadweb.org"


from xml.etree import ElementTree

import FreeCAD
import Draft
import DraftGeomUtils
import DraftVecUtils
import WorkingPlane

from SVGfunc import (
    getSVGRootElement,
    getPointSVG,
    isPointInSVG,
    getLineSVG,
    isLineInSVG,
    getSVGTextElement,
    getSVGPathElement,
    getArrowMarkerElement,
)


def getRebarsSpanAxis(rebar):
    if (
        Draft.getType(rebar.Base) == "Wire"
    ):  # Draft Wires can have "wrong" placement
        axis = DraftGeomUtils.getNormal(rebar.Base.Shape)
    else:
        axis = rebar.Base.Placement.Rotation.multVec(FreeCAD.Vector(0, 0, -1))
    if hasattr(rebar, "Direction"):
        if not DraftVecUtils.isNull(rebar.Direction):
            axis = FreeCAD.Vector(rebar.Direction)
            axis.normalize()
    return axis


def getProjectionToSVGPlane(vec, plane):
    nx = DraftVecUtils.project(vec, plane.u)
    lx = nx.Length
    if abs(nx.getAngle(plane.u)) > 0.1:
        lx = -lx
    ny = DraftVecUtils.project(vec, plane.v)
    ly = ny.Length
    if abs(ny.getAngle(plane.v)) > 0.1:
        ly = -ly
    # if techdraw: buggy - we now simply do it at the end
    #    ly = -ly
    return FreeCAD.Vector(lx, ly, 0)


def getStructureMinMaxPoints(structure, view_plane):
    min_x = 9999999
    min_y = 9999999
    max_x = -9999999
    max_y = -9999999
    vertex_list = structure.Shape.Vertexes
    for vertex in vertex_list:
        point = getProjectionToSVGPlane(vertex.Point, view_plane)
        min_x = min(min_x, point.x)
        min_y = min(min_y, point.y)
        max_x = max(max_x, point.x)
        max_y = max(max_y, point.y)
    return (min_x, min_y, max_x, max_y)


def getLineDimensionsData(
    p1, p2, dimension_text, h_dim_x, h_dim_y, v_dim_x, v_dim_y
):
    dimension = ElementTree.Element("g")
    if abs(p2.y - p1.y) < abs(p2.x - p1.x):
        dimension_line_horizontal = False
        x_cord = v_dim_x
        y_cord = (x_cord - p1.x) * (p2.y - p1.y) / (p2.x - p1.x) + p1.y
        dimension_line = getSVGPathElement(
            "M{} {} V{}".format(x_cord, y_cord, v_dim_y),
            "url(#start_arrow)",
            "stroke:#000000",
        )
        dimension_label = getSVGTextElement(
            dimension_text, v_dim_x, v_dim_y, "DejaVu Sans", "10px", "middle"
        )
        dimension.append(dimension_line)
        dimension.append(dimension_label)
    else:
        dimension_line_horizontal = True
        y_cord = h_dim_y
        x_cord = (y_cord - p1.y) * (p2.x - p1.x) / (p2.y - p1.y) + p1.x
        dimension_line = getSVGPathElement(
            "M{} {} H{}".format(x_cord, y_cord, h_dim_x),
            "url(#start_arrow)",
            "stroke:#000000",
        )
        dimension_label = getSVGTextElement(
            dimension_text,
            h_dim_x,
            h_dim_y,
            "DejaVu Sans",
            "10px",
            dominant_baseline="central",
        )
        dimension.append(dimension_line)
        dimension.append(dimension_label)
    return {
        "svg": dimension,
        "dimension_line_horizontal": dimension_line_horizontal,
    }


def getStraightRebarSVGData(
    rebar,
    view_plane,
    h_dim_x_offset,
    h_dim_y_offset,
    v_dim_x_offset,
    v_dim_y_offset,
    rebars_svg,
):
    straight_rebar_svg = ElementTree.Element(
        "g", attrib={"id": str(rebar.Name)}
    )
    min_x = 9999999
    min_y = 9999999
    max_x = -9999999
    max_y = -9999999
    is_rebar_visible = False
    drawing_plane_normal = view_plane.axis
    # rebars_dimension_svg = ""
    if round(drawing_plane_normal.cross(getRebarsSpanAxis(rebar)).Length) == 0:
        p1 = getProjectionToSVGPlane(
            rebar.Base.Shape.Wires[0].Vertexes[0].Point, view_plane
        )
        p2 = getProjectionToSVGPlane(
            rebar.Base.Shape.Wires[0].Vertexes[1].Point, view_plane
        )
        if round(p1.x) == round(p2.x) and round(p1.y) == round(p2.y):
            rebar_svg = getPointSVG(p1)
            if not isPointInSVG(p1, rebars_svg):
                is_rebar_visible = True
        else:
            rebar_svg = getLineSVG(p1, p2)
            if not isLineInSVG(p1, p2, rebars_svg):
                is_rebar_visible = True
        if is_rebar_visible:
            straight_rebar_svg.append(rebar_svg)
            dimension_data = getLineDimensionsData(
                p1,
                p2,
                "{}⌀{}".format(rebar.Amount, rebar.Diameter),
                h_dim_x_offset,
                h_dim_y_offset,
                v_dim_x_offset,
                v_dim_y_offset,
            )
            straight_rebar_svg.append(dimension_data["svg"])
            if dimension_data["dimension_line_horizontal"]:
                # Add logic calculate increment
                h_dim_y_offset += 100
            else:
                v_dim_x_offset += 100
            min_x = min(p1.x, p2.x)
            min_y = min(p1.y, p2.y)
            max_x = max(p1.x, p2.x)
            max_y = max(p1.y, p2.y)
    else:
        basewire = rebar.Base.Shape.Wires[0]
        for placement in rebar.PlacementList:
            wire = basewire.copy()
            wire.Placement = placement.multiply(basewire.Placement)
            p1 = getProjectionToSVGPlane(wire.Vertexes[0].Point, view_plane)
            p2 = getProjectionToSVGPlane(wire.Vertexes[1].Point, view_plane)
            if round(p1.x) == round(p2.x) and round(p1.y) == round(p2.y):
                rebar_svg = getPointSVG(p1)
                if not (
                    isPointInSVG(p1, rebars_svg)
                    or isPointInSVG(p1, straight_rebar_svg)
                ):
                    is_rebar_visible = True
            else:
                rebar_svg = getLineSVG(p1, p2)
                if not (
                    isLineInSVG(p1, p2, rebars_svg)
                    or isLineInSVG(p1, p2, straight_rebar_svg)
                ):
                    is_rebar_visible = True
            if is_rebar_visible:
                straight_rebar_svg.append(rebar_svg)
                min_x = min(min_x, p1.x, p2.x)
                min_y = min(min_y, p1.y, p2.y)
                max_x = max(max_x, p1.x, p2.x)
                max_y = max(max_y, p1.y, p2.y)
    return {
        # "svg": rebars_svg + rebars_dimension_svg,
        "svg": straight_rebar_svg,
        "visibility": is_rebar_visible,
        "min_x": min_x,
        "min_y": min_y,
        "max_x": max_x,
        "max_y": max_y,
        "h_dim_y_offset": h_dim_y_offset,
        "v_dim_x_offset": v_dim_x_offset,
    }


def getReinforcementDrawingSVG(structure, rebars_list, view_direction):
    if isinstance(view_direction, FreeCAD.Vector):
        if view_direction != FreeCAD.Vector(0, 0, 0):
            view_plane = WorkingPlane.plane()
            view_plane.alignToPointAndAxis(
                FreeCAD.Vector(0, 0, 0),
                view_direction.negative().negative(),
                0,
            )
    elif isinstance(view_direction, WorkingPlane.plane):
        view_plane = view_direction

    svg = getSVGRootElement()
    defs_element = ElementTree.Element("defs")
    defs_element.append(getArrowMarkerElement("start_arrow", "start"))
    defs_element.append(getArrowMarkerElement("end_arrow", "end"))
    svg.append(defs_element)

    reinforcement_drawing = ElementTree.Element(
        "g", attrib={"id": "reinforcement_drawing"}
    )
    svg.append(reinforcement_drawing)

    # Filter rebars created using Reinforcement Workbench
    straight_rebars = []
    stirrups = []
    for rebar in rebars_list:
        if rebar.ViewObject.RebarShape == "StraightRebar":
            straight_rebars.append(rebar)
        elif rebar.ViewObject.RebarShape == "Stirrup":
            stirrups.append(rebar)
        # There will be more

    (
        struct_min_x,
        struct_min_y,
        struct_max_x,
        struct_max_y,
    ) = getStructureMinMaxPoints(structure, view_plane)
    max_x = struct_max_x
    max_y = struct_max_y
    min_x = struct_min_x
    min_y = struct_min_y

    rebars_svg = ElementTree.Element("g", attrib={"id": "Rebars"})
    reinforcement_drawing.append(rebars_svg)

    straight_rebars_svg = ElementTree.Element("g")
    straight_rebars_svg.set("id", "StraightRebar")
    rebars_svg.append(straight_rebars_svg)

    h_dim_x_offset = max_x + 50
    h_dim_y_offset = min_y + 50
    v_dim_x_offset = min_x + 50
    v_dim_y_offset = min_y - 50
    visible_rebars = []
    for rebar in straight_rebars:
        rebar_data = getStraightRebarSVGData(
            rebar,
            view_plane,
            h_dim_x_offset,
            h_dim_y_offset,
            v_dim_x_offset,
            v_dim_y_offset,
            rebars_svg,
        )
        if rebar_data["visibility"]:
            straight_rebars_svg.append(rebar_data["svg"])
            min_x = min(min_x, rebar_data["min_x"])
            min_y = min(min_y, rebar_data["min_y"])
            max_x = max(max_x, rebar_data["max_x"])
            max_y = max(max_y, rebar_data["max_y"])
            h_dim_y_offset = rebar_data["h_dim_y_offset"]
            v_dim_x_offset = rebar_data["v_dim_x_offset"]
            visible_rebars.append(rebar)

    # Create Structure SVG
    structure_svg = ElementTree.fromstring(
        '<g id="structure">'
        + Draft.getSVG(structure, direction=view_plane, fillstyle="none")
        + "</g>"
    )
    reinforcement_drawing.append(structure_svg)
    reinforcement_drawing.set(
        "transform",
        "translate({}, {})".format(round(-min_x + 60), round(-min_y + 100)),
    )

    svg_width = round(max_x - min_x + 200)
    svg_height = round(max_y - min_y + 200)

    svg.set("width", str(svg_width) + "mm")
    svg.set("height", str(svg_height) + "mm")
    svg.set("viewBox", "0 0 {} {}".format(svg_width, svg_height))

    return ElementTree.tostring(svg, encoding="unicode")


def getReinforcementDrawing(structure, rebars_list, structure_view="Front"):
    if structure_view == "Front":
        view_direction = FreeCAD.Vector(0, -1, 0)
    if structure_view == "Rear":
        view_direction = FreeCAD.Vector(0, 1, 0)
    elif structure_view == "Left":
        view_direction = FreeCAD.Vector(-1, 0, 0)
    elif structure_view == "Right":
        view_direction = FreeCAD.Vector(1, 0, 0)
    elif structure_view == "Top":
        view_direction = FreeCAD.Vector(0, 0, 1)
    elif structure_view == "Bottom":
        view_direction = FreeCAD.Vector(0, 0, -1)
    else:
        # Fallback
        view_direction = FreeCAD.Vector(0, 1, 0)
    svg = getReinforcementDrawingSVG(structure, rebars_list, view_direction)
    return svg
