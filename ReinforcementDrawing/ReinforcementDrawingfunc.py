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

__title__ = "Reinforcement Drawing Functions"
__author__ = "Suraj"
__url__ = "https://www.freecadweb.org"


import math
from xml.etree import ElementTree

import FreeCAD
import Part
import Draft
import DraftGeomUtils
import DraftVecUtils
import WorkingPlane
from importSVG import getcolor

from SVGfunc import (
    getSVGRootElement,
    getPointSVG,
    isPointInSVG,
    getLineSVG,
    isLineInSVG,
)


def getRebarsSpanAxis(rebar):
    """getRebarsSpanAxis(Rebar):
    Returns span axis of rebars.
    """
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


def getViewPlane(view):
    """getViewPlane(View):
    Returns view_plane corresponding to view, where view can be "Front", "Rear",
    "Left", "Right", "Top" or "Bottom".
    """
    if view == "Front":
        view_plane = WorkingPlane.plane()
        view_plane.axis = FreeCAD.Vector(0, -1, 0)
        view_plane.v = FreeCAD.Vector(0, 0, -1)
        view_plane.u = FreeCAD.Vector(1, 0, 0)
    elif view == "Rear":
        view_plane = WorkingPlane.plane()
        view_plane.axis = FreeCAD.Vector(0, 1, 0)
        view_plane.v = FreeCAD.Vector(0, 0, -1)
        view_plane.u = FreeCAD.Vector(-1, 0, 0)
    elif view == "Left":
        view_plane = WorkingPlane.plane()
        view_plane.axis = FreeCAD.Vector(-1, 0, 0)
        view_plane.v = FreeCAD.Vector(0, 0, -1)
        view_plane.u = FreeCAD.Vector(0, -1, 0)
    elif view == "Right":
        view_plane = WorkingPlane.plane()
        view_plane.axis = FreeCAD.Vector(1, 0, 0)
        view_plane.v = FreeCAD.Vector(0, 0, -1)
        view_plane.u = FreeCAD.Vector(0, 1, 0)
    elif view == "Top":
        view_plane = WorkingPlane.plane()
        view_plane.axis = FreeCAD.Vector(0, 0, 1)
        view_plane.v = FreeCAD.Vector(0, -1, 0)
        view_plane.u = FreeCAD.Vector(1, 0, 0)
    elif view == "Bottom":
        view_plane = WorkingPlane.plane()
        view_plane.axis = FreeCAD.Vector(0, 0, -1)
        view_plane.v = FreeCAD.Vector(0, 1, 0)
        view_plane.u = FreeCAD.Vector(1, 0, 0)
    else:
        FreeCAD.Console.PrintError(
            'Invalid/Unsupported view. Valid views are: "Front", "Rear", '
            '"Left", "Right" "Top" and "Bottom".\n'
        )
        return None
    return view_plane


def getSVGPlaneFromAxis(axis=FreeCAD.Vector(0, -1, 0)):
    view_plane = WorkingPlane.Plane()
    # axis is closed to +X axis
    if axis.getAngle(FreeCAD.Vector(1, 0, 0)) < 0.00001:
        view_plane.axis = FreeCAD.Vector(1, 0, 0)
        view_plane.u = FreeCAD.Vector(0, 1, 0)
        view_plane.v = FreeCAD.Vector(0, 0, -1)
    # axis is closed to -X axis
    elif axis.getAngle(FreeCAD.Vector(-1, 0, 0)) < 0.00001:
        view_plane.axis = FreeCAD.Vector(-1, 0, 0)
        view_plane.u = FreeCAD.Vector(0, -1, 0)
        view_plane.v = FreeCAD.Vector(0, 0, -1)
    else:
        view_plane.axis = axis
        y_axis = axis.cross(FreeCAD.Vector(1, 0, 0))
        y_axis.normalize()
        if y_axis.z > 0:
            y_axis = y_axis.negative()
        elif y_axis.y > 0:
            y_axis = y_axis.negative()
        view_plane.v = y_axis
        view_plane.u = DraftVecUtils.rotate(
            view_plane.v, math.pi / 2, view_plane.axis
        )
    return view_plane


def getProjectionToSVGPlane(vec, plane):
    """getProjectionToSVGPlane(Vector, Plane):
    Returns projection of vector on plane.
    """
    nx = DraftVecUtils.project(vec, plane.u)
    lx = nx.Length
    if abs(nx.getAngle(plane.u)) > 0.1:
        lx = -lx
    ny = DraftVecUtils.project(vec, plane.v)
    ly = ny.Length
    if abs(ny.getAngle(plane.v)) > 0.1:
        ly = -ly
    return FreeCAD.Vector(lx, ly, 0)


def getDrawingMinMaxXY(structure, rebars_list, view_plane):
    """getDrawingMinMaxXY(Structure, RebarsList, ViewPlane):
    Returns (min_x, min_y, max_x, max_y) of drawing.
    """
    if view_plane.axis == FreeCAD.Vector(0, -1, 0):
        pts = [0, 1, 4, 5]
    elif view_plane.axis == FreeCAD.Vector(0, 1, 0):
        pts = [2, 3, 6, 7]
    elif view_plane.axis == FreeCAD.Vector(0, 0, 1):
        pts = [0, 1, 2, 3]
    elif view_plane.axis == FreeCAD.Vector(0, 0, -1):
        pts = [4, 5, 6, 7]
    elif view_plane.axis == FreeCAD.Vector(1, 0, 0):
        pts = [1, 2, 5, 6]
    else:
        pts = [0, 3, 4, 7]

    bounding_box = Part.Compound(
        [rebar.Shape for rebar in rebars_list] + [structure.Shape]
    ).BoundBox
    point = getProjectionToSVGPlane(bounding_box.getPoint(pts[0]), view_plane)
    min_x = point.x
    min_y = point.y
    max_x = point.x
    max_y = point.y
    for pt in pts[1:]:
        point = getProjectionToSVGPlane(bounding_box.getPoint(pt), view_plane)
        min_x = min(min_x, point.x)
        min_y = min(min_y, point.y)
        max_x = max(max_x, point.x)
        max_y = max(max_y, point.y)
    return min_x, min_y, max_x, max_y


def getSVGWidthHeight(structure, rebars_list, view_plane):
    """getSVGWidthHeight(Structure, RebarsList, ViewPlane):
    Returns a tuple of width and height of svg.
    """
    min_x, min_y, max_x, max_y = getDrawingMinMaxXY(
        structure, rebars_list, view_plane
    )
    svg_width = round(max_x - min_x)
    svg_height = round(max_y - min_y)
    return svg_width, svg_height


def getRoundCornerSVG(edge, radius, view_plane, stroke_width, stroke_color):
    """getRoundCornerSVG(Edge, Radius, ViewPlane, StrokeWidth, StrokeColor):
    Returns round corner edge svg with given radius.
    """
    p1 = getProjectionToSVGPlane(edge.Vertexes[0].Point, view_plane)
    p2 = getProjectionToSVGPlane(edge.Vertexes[1].Point, view_plane)
    t1 = edge.tangentAt(edge.FirstParameter)
    t2 = edge.tangentAt(
        edge.FirstParameter + (edge.LastParameter - edge.FirstParameter) / 10
    )
    flag_sweep = int(DraftVecUtils.angle(t1, t2, view_plane.axis) < 0)
    svg = ElementTree.Element("path")
    svg.set("style", "stroke:#000000;fill:none")
    svg.set(
        "d",
        "M{x1} {y1} A{radius} {radius} 0 0 {flag_sweep} {x2} {y2}".format(
            x1=round(p1.x),
            y1=round(p1.y),
            x2=round(p2.x),
            y2=round(p2.y),
            radius=round(radius),
            flag_sweep=flag_sweep,
        ),
    )
    svg.set("stroke-width", str(stroke_width))
    svg.set("stroke", stroke_color)
    return svg


def isRoundCornerInSVG(edge, radius, view_plane, svg):
    """isRoundCornerInSVG(Edge, Radius, ViewPlane. SVG):
    Returns True if svg corresponding to round corner edge is present in SVG
    element, False otherwise.
    """
    p1 = getProjectionToSVGPlane(edge.Vertexes[0].Point, view_plane)
    p2 = getProjectionToSVGPlane(edge.Vertexes[1].Point, view_plane)
    t1 = edge.tangentAt(edge.FirstParameter)
    t2 = edge.tangentAt(
        edge.FirstParameter + (edge.LastParameter - edge.FirstParameter) / 10
    )
    flag_sweep = int(DraftVecUtils.angle(t1, t2, view_plane.axis) < 0)
    if (
        svg.find(
            './/path[@d="M{x1} {y1} A{radius} {radius} 0 0 {flag_sweep} {x2} '
            '{y2}"]'.format(
                x1=round(p1.x),
                y1=round(p1.y),
                x2=round(p2.x),
                y2=round(p2.y),
                radius=round(radius),
                flag_sweep=flag_sweep,
            )
        )
        is not None
    ):
        return True
    elif (
        svg.find(
            './/path[@d="M{x1} {y1} A{radius} {radius} 0 0 {flag_sweep} {x2} '
            '{y2}"]'.format(
                x1=round(p2.x),
                y1=round(p2.y),
                x2=round(p1.x),
                y2=round(p1.y),
                radius=round(radius),
                flag_sweep=not flag_sweep,
            )
        )
        is not None
    ):
        return True
    else:
        return False


def getRebarColor(rebar, rebar_color_style="shape color"):
    """getRebarColor(Rebar, [RebarColorStyle]):
    Returns rebar color.

    rebar_color_style can be:
        - "shape color" to select color of rebar shape [Default]
        - color name or hex value of color

    """
    if rebar_color_style == "shape color":
        if FreeCAD.GuiUp:
            rebar_color = Draft.getrgb(rebar.ViewObject.ShapeColor)
        else:
            # TODO: Add logic to get this from FreeCAD preferences
            rebar_color = "black"
    else:
        rebar_color = rebar_color_style
    return rebar_color


def getStirrupSVGPoints(stirrup_wire, stirrup_alignment, view_plane):
    """getStirrupSVGPoints(StirrupWire, StirrupAlignment, ViewPlane):
    stirrup_alignment can be "V" for vertical, horizontal otherwise.
    Returns points corresponding to line representation of stirrup in
    view_plane.
    """
    first_point = getProjectionToSVGPlane(
        stirrup_wire.Vertexes[0].Point, view_plane
    )
    min_x = first_point.x
    min_y = first_point.y
    max_x = first_point.x
    max_y = first_point.y
    for vertex in stirrup_wire.Vertexes[1:]:
        point = getProjectionToSVGPlane(vertex.Point, view_plane)
        min_x = min(min_x, point.x)
        min_y = min(min_y, point.y)
        max_x = max(max_x, point.x)
        max_y = max(max_y, point.y)
    if stirrup_alignment == "V":
        x_cord = (min_x + max_x) / 2
        return (
            FreeCAD.Vector(x_cord, min_y, 0),
            FreeCAD.Vector(x_cord, max_y, 0),
        )
    else:
        y_cord = (min_y + max_y) / 2
        return (
            FreeCAD.Vector(min_x, y_cord, 0),
            FreeCAD.Vector(max_x, y_cord, 0),
        )


def getStirrupSVGData(
    rebar, view_plane, rebars_svg, rebars_stroke_width, rebars_color_style
):
    """getStirrupSVGData(StirrupRebar, ViewPlane, RebarsSVG, RebarsStrokeWidth,
    RebarsColorStyle):
    Returns dictionary containing stirrup svg data.

    rebars_color_style can be:
        - "shape color" to select color of rebar shape
        - color name or hex value of color

    Returns dictionary format:
    {
        "svg": stirrup_svg,
        "visibility": is_rebar_visible,
    }
    """
    rebars_color = getRebarColor(rebar, rebars_color_style)

    stirrup_svg = ElementTree.Element("g", attrib={"id": str(rebar.Name)})
    is_rebar_visible = False
    drawing_plane_normal = view_plane.axis
    stirrup_span_axis = getRebarsSpanAxis(rebar)
    if round(drawing_plane_normal.cross(stirrup_span_axis).Length) == 0:
        basewire = rebar.Base.Shape.Wires[0].copy()
        basewire.Placement = rebar.PlacementList[0].multiply(basewire.Placement)
        edges = Part.__sortEdges__(
            DraftGeomUtils.filletWire(
                basewire, rebar.Rounding * rebar.Diameter.Value,
            ).Edges
        )
        for edge in edges:
            if DraftGeomUtils.geomType(edge) == "Line":
                p1 = getProjectionToSVGPlane(edge.Vertexes[0].Point, view_plane)
                p2 = getProjectionToSVGPlane(edge.Vertexes[1].Point, view_plane)
                edge_svg = getLineSVG(p1, p2, rebars_stroke_width, rebars_color)
                if is_rebar_visible or not isLineInSVG(p1, p2, rebars_svg):
                    stirrup_svg.append(edge_svg)
                    is_rebar_visible = True
            elif DraftGeomUtils.geomType(edge) == "Circle":
                edge_svg = getRoundCornerSVG(
                    edge,
                    rebar.Rounding * rebar.Diameter.Value,
                    view_plane,
                    rebars_stroke_width,
                    rebars_color,
                )
                if is_rebar_visible or not isRoundCornerInSVG(
                    edge,
                    rebar.Rounding * rebar.Diameter.Value,
                    view_plane,
                    rebars_svg,
                ):
                    stirrup_svg.append(edge_svg)
                    is_rebar_visible = True

    else:
        if round(stirrup_span_axis.cross(view_plane.u).Length) == 0:
            stirrup_alignment = "V"
        else:
            stirrup_alignment = "H"
        basewire = DraftGeomUtils.filletWire(
            rebar.Base.Shape.Wires[0], rebar.Rounding * rebar.Diameter.Value
        )
        for placement in rebar.PlacementList:
            wire = basewire.copy()
            wire.Placement = placement.multiply(basewire.Placement)
            p1, p2 = getStirrupSVGPoints(wire, stirrup_alignment, view_plane)
            rebar_svg = getLineSVG(p1, p2, rebars_stroke_width, rebars_color)
            if not isLineInSVG(p1, p2, rebars_svg):
                is_rebar_visible = True
            if is_rebar_visible:
                stirrup_svg.append(rebar_svg)
    return {
        "svg": stirrup_svg,
        "visibility": is_rebar_visible,
    }


def getUShapeRebarSVGData(
    rebar, view_plane, rebars_svg, rebars_stroke_width, rebars_color_style
):
    """getUShapeRebarSVGData(UShapeRebar, ViewPlane, RebarsSVG,
    RebarsStrokeWidth, RebarsColorStyle):
    Returns dictionary containing UShape rebar svg data.

    rebars_color_style can be:
        - "shape color" to select color of rebar shape
        - color name or hex value of color

    Returns dictionary format:
    {
        "svg": u_rebar_svg,
        "visibility": is_rebar_visible,
    }
    """
    rebars_color = getRebarColor(rebar, rebars_color_style)

    u_rebar_svg = ElementTree.Element("g", attrib={"id": str(rebar.Name)})
    is_rebar_visible = False
    drawing_plane_normal = view_plane.axis
    if round(drawing_plane_normal.cross(getRebarsSpanAxis(rebar)).Length) == 0:
        basewire = rebar.Base.Shape.Wires[0].copy()
        basewire.Placement = rebar.PlacementList[0].multiply(basewire.Placement)
        edges = Part.__sortEdges__(
            DraftGeomUtils.filletWire(
                basewire, rebar.Rounding * rebar.Diameter.Value,
            ).Edges
        )
        for edge in edges:
            if DraftGeomUtils.geomType(edge) == "Line":
                p1 = getProjectionToSVGPlane(edge.Vertexes[0].Point, view_plane)
                p2 = getProjectionToSVGPlane(edge.Vertexes[1].Point, view_plane)
                if round(p1.x) == round(p2.x) and round(p1.y) == round(p2.y):
                    edge_svg = getPointSVG(
                        p1, radius=2 * rebars_stroke_width, fill=rebars_color
                    )
                else:
                    edge_svg = getLineSVG(
                        p1, p2, rebars_stroke_width, rebars_color
                    )
                    if not isLineInSVG(p1, p2, rebars_svg):
                        is_rebar_visible = True
                if is_rebar_visible:
                    u_rebar_svg.append(edge_svg)
                    is_rebar_visible = True
            elif DraftGeomUtils.geomType(edge) == "Circle":
                p1 = getProjectionToSVGPlane(edge.Vertexes[0].Point, view_plane)
                p2 = getProjectionToSVGPlane(edge.Vertexes[1].Point, view_plane)
                if round(p1.x) == round(p2.x) or round(p1.y) == round(p2.y):
                    edge_svg = getLineSVG(
                        p1, p2, rebars_stroke_width, rebars_color
                    )
                    if not isLineInSVG(p1, p2, rebars_svg):
                        is_rebar_visible = True
                else:
                    edge_svg = getRoundCornerSVG(
                        edge,
                        rebar.Rounding * rebar.Diameter.Value,
                        view_plane,
                        rebars_stroke_width,
                        rebars_color,
                    )
                    if not isRoundCornerInSVG(
                        edge,
                        rebar.Rounding * rebar.Diameter.Value,
                        view_plane,
                        rebars_svg,
                    ):
                        is_rebar_visible = True
                if is_rebar_visible:
                    u_rebar_svg.append(edge_svg)
    else:
        basewire = rebar.Base.Shape.Wires[0]
        for placement in rebar.PlacementList:
            wire = basewire.copy()
            wire.Placement = placement.multiply(basewire.Placement)

            edges = Part.__sortEdges__(
                DraftGeomUtils.filletWire(
                    wire, rebar.Rounding * rebar.Diameter.Value,
                ).Edges
            )
            for edge in edges:
                if DraftGeomUtils.geomType(edge) == "Line":
                    p1 = getProjectionToSVGPlane(
                        edge.Vertexes[0].Point, view_plane
                    )
                    p2 = getProjectionToSVGPlane(
                        edge.Vertexes[1].Point, view_plane
                    )
                    if round(p1.x) == round(p2.x) and round(p1.y) == round(
                        p2.y
                    ):
                        edge_svg = getPointSVG(
                            p1,
                            radius=2 * rebars_stroke_width,
                            fill=rebars_color,
                        )
                    else:
                        edge_svg = getLineSVG(
                            p1, p2, rebars_stroke_width, rebars_color
                        )
                        if not isLineInSVG(p1, p2, rebars_svg):
                            is_rebar_visible = True
                    if is_rebar_visible or not isLineInSVG(p1, p2, rebars_svg):
                        u_rebar_svg.append(edge_svg)
                        is_rebar_visible = True
                elif DraftGeomUtils.geomType(edge) == "Circle":
                    p1 = getProjectionToSVGPlane(
                        edge.Vertexes[0].Point, view_plane
                    )
                    p2 = getProjectionToSVGPlane(
                        edge.Vertexes[1].Point, view_plane
                    )
                    if round(p1.x) == round(p2.x) or round(p1.y) == round(p2.y):
                        edge_svg = getLineSVG(
                            p1, p2, rebars_stroke_width, rebars_color
                        )
                        if not isLineInSVG(p1, p2, rebars_svg):
                            is_rebar_visible = True
                    else:
                        edge_svg = getRoundCornerSVG(
                            edge,
                            rebar.Rounding * rebar.Diameter.Value,
                            view_plane,
                            rebars_stroke_width,
                            rebars_color,
                        )
                        if not isRoundCornerInSVG(
                            edge,
                            rebar.Rounding * rebar.Diameter.Value,
                            view_plane,
                            rebars_svg,
                        ):
                            is_rebar_visible = True
                    if is_rebar_visible:
                        u_rebar_svg.append(edge_svg)
    return {
        "svg": u_rebar_svg,
        "visibility": is_rebar_visible,
    }


def getStraightRebarSVGData(
    rebar, view_plane, rebars_svg, rebars_stroke_width, rebars_color_style,
):
    """getStraightRebarSVGData(StraightRebar, ViewPlane, RebarsSVG,
    RebarsStrokeWidth, RebarsColorStyle):
    Returns dictionary containing straight rebar svg data.

    rebars_color_style can be:
        - "shape color" to select color of rebar shape
        - color name or hex value of color

    Returns dictionary format:
    {
        "svg": straight_rebar_svg,
        "visibility": is_rebar_visible,
    }
    """
    rebars_color = getRebarColor(rebar, rebars_color_style)

    straight_rebar_svg = ElementTree.Element(
        "g", attrib={"id": str(rebar.Name)}
    )
    is_rebar_visible = False
    drawing_plane_normal = view_plane.axis
    if round(drawing_plane_normal.cross(getRebarsSpanAxis(rebar)).Length) == 0:
        basewire = rebar.Base.Shape.Wires[0].copy()
        basewire.Placement = rebar.PlacementList[0].multiply(basewire.Placement)
        p1 = getProjectionToSVGPlane(basewire.Vertexes[0].Point, view_plane)
        p2 = getProjectionToSVGPlane(basewire.Vertexes[1].Point, view_plane)
        if round(p1.x) == round(p2.x) and round(p1.y) == round(p2.y):
            rebar_svg = getPointSVG(
                p1, radius=2 * rebars_stroke_width, fill=rebars_color
            )
            if not isPointInSVG(p1, rebars_svg):
                is_rebar_visible = True
        else:
            rebar_svg = getLineSVG(p1, p2, rebars_stroke_width, rebars_color)
            if not isLineInSVG(p1, p2, rebars_svg):
                is_rebar_visible = True
        if is_rebar_visible:
            straight_rebar_svg.append(rebar_svg)
    else:
        basewire = rebar.Base.Shape.Wires[0]
        for placement in rebar.PlacementList:
            wire = basewire.copy()
            wire.Placement = placement.multiply(basewire.Placement)
            p1 = getProjectionToSVGPlane(wire.Vertexes[0].Point, view_plane)
            p2 = getProjectionToSVGPlane(wire.Vertexes[1].Point, view_plane)
            if round(p1.x) == round(p2.x) and round(p1.y) == round(p2.y):
                rebar_svg = getPointSVG(
                    p1, radius=2 * rebars_stroke_width, fill=rebars_color
                )
                if not (
                    isPointInSVG(p1, rebars_svg)
                    or isPointInSVG(p1, straight_rebar_svg)
                ):
                    is_rebar_visible = True
            else:
                rebar_svg = getLineSVG(
                    p1, p2, rebars_stroke_width, rebars_color
                )
                if not (
                    isLineInSVG(p1, p2, rebars_svg)
                    or isLineInSVG(p1, p2, straight_rebar_svg)
                ):
                    is_rebar_visible = True
            if is_rebar_visible:
                straight_rebar_svg.append(rebar_svg)
    return {
        "svg": straight_rebar_svg,
        "visibility": is_rebar_visible,
    }


def getReinforcementDrawingSVGData(
    structure,
    rebars_list,
    view_direction,
    rebars_stroke_width,
    rebars_color_style,
    structure_stroke_width,
    structure_fill_style,
):
    """getReinforcementDrawingSVGData(Structure, RebarsList, ViewDirection,
    RebarsStrokeWidth, RebarsFillStyle, StructureStrokeWidth,
    StructureFillStyle):
    Generates Reinforcement Drawing View.

    view_direction is FreeCAD.Vector() or WorkingPlane.plane() corresponding to
    direction of view point.

    rebars_color_style can be:
        - "shape color" to select color of rebar shape
        - color name or hex value of color
    structure_fill_style can be:
        - "shape color" to select color of rebar shape
        - color name or hex value of color
        - "none" to not fill structure shape

    Returns dictionary format:
    {
        "svg": reinforcement_drawing_svg,
        "rebars": visible_rebars,
    }
    """
    if isinstance(view_direction, FreeCAD.Vector):
        if not DraftVecUtils.isNull(view_direction):
            view_plane = getSVGPlaneFromAxis(view_direction)
    elif isinstance(view_direction, WorkingPlane.Plane):
        view_plane = view_direction

    min_x, min_y, max_x, max_y = getDrawingMinMaxXY(
        structure, rebars_list, view_plane
    )

    svg = getSVGRootElement()

    reinforcement_drawing = ElementTree.Element(
        "g", attrib={"id": "reinforcement_drawing"}
    )
    svg.append(reinforcement_drawing)

    # Filter rebars created using Reinforcement Workbench
    stirrups = []
    bent_rebars = []
    u_rebars = []
    l_rebars = []
    straight_rebars = []
    helical_rebars = []
    custom_rebars = []
    for rebar in rebars_list:
        if not hasattr(rebar, "RebarShape"):
            custom_rebars.append(rebar)
        elif rebar.RebarShape == "Stirrup":
            stirrups.append(rebar)
        elif rebar.RebarShape == "BentShapeRebar":
            bent_rebars.append(rebar)
        elif rebar.RebarShape == "UShapeRebar":
            u_rebars.append(rebar)
        elif rebar.RebarShape == "LShapeRebar":
            l_rebars.append(rebar)
        elif rebar.RebarShape == "StraightRebar":
            straight_rebars.append(rebar)
        elif rebar.RebarShape == "HelicalRebar":
            helical_rebars.append(rebar)
        else:
            custom_rebars.append(rebar)

    rebars_svg = ElementTree.Element("g", attrib={"id": "Rebars"})
    reinforcement_drawing.append(rebars_svg)

    visible_rebars = []
    stirrups_svg = ElementTree.Element("g", attrib={"id": "Stirrup"})
    rebars_svg.append(stirrups_svg)
    for rebar in stirrups:
        rebar_data = getStirrupSVGData(
            rebar,
            view_plane,
            rebars_svg,
            rebars_stroke_width,
            rebars_color_style,
        )
        if rebar_data["visibility"]:
            stirrups_svg.append(rebar_data["svg"])
            visible_rebars.append(rebar)

    bent_rebars_svg = ElementTree.Element("g", attrib={"id": "BentShapeRebar"})
    rebars_svg.append(bent_rebars_svg)
    for rebar in bent_rebars:
        rebar_data = getUShapeRebarSVGData(
            rebar,
            view_plane,
            rebars_svg,
            rebars_stroke_width,
            rebars_color_style,
        )
        if rebar_data["visibility"]:
            bent_rebars_svg.append(rebar_data["svg"])
            visible_rebars.append(rebar)

    u_rebars_svg = ElementTree.Element("g", attrib={"id": "UShapeRebar"})
    rebars_svg.append(u_rebars_svg)
    for rebar in u_rebars:
        rebar_data = getUShapeRebarSVGData(
            rebar,
            view_plane,
            rebars_svg,
            rebars_stroke_width,
            rebars_color_style,
        )
        if rebar_data["visibility"]:
            u_rebars_svg.append(rebar_data["svg"])
            visible_rebars.append(rebar)

    l_rebars_svg = ElementTree.Element("g", attrib={"id": "LShapeRebar"})
    rebars_svg.append(l_rebars_svg)
    for rebar in l_rebars:
        rebar_data = getUShapeRebarSVGData(
            rebar,
            view_plane,
            rebars_svg,
            rebars_stroke_width,
            rebars_color_style,
        )
        if rebar_data["visibility"]:
            l_rebars_svg.append(rebar_data["svg"])
            visible_rebars.append(rebar)

    straight_rebars_svg = ElementTree.Element(
        "g", attrib={"id": "StraightRebar"}
    )
    rebars_svg.append(straight_rebars_svg)

    for rebar in straight_rebars:
        rebar_data = getStraightRebarSVGData(
            rebar,
            view_plane,
            rebars_svg,
            rebars_stroke_width,
            rebars_color_style,
        )
        if rebar_data["visibility"]:
            straight_rebars_svg.append(rebar_data["svg"])
            visible_rebars.append(rebar)

    helical_rebars_svg = ElementTree.Element("g", attrib={"id": "HelicalRebar"})
    rebars_svg.append(helical_rebars_svg)

    # SVG is generated for all helical rebars, because all helical rebars in
    # circular column are assumed to be visible, not overlapped by any other
    # rebar type (it makes sense for me). Please create an issue on github
    # repository if you think its wrong assumption
    for rebar in helical_rebars:
        rebars_color = getRebarColor(rebar, rebars_color_style)
        rebars_color = getcolor(rebars_color)
        rebar_svg_draft = Draft.getSVG(
            rebar,
            direction=view_plane,
            linewidth=rebars_stroke_width,
            fillstyle="none",
            color=rebars_color,
        )
        if rebar_svg_draft:
            helical_rebars_svg.append(ElementTree.fromstring(rebar_svg_draft))
            visible_rebars.append(rebar)

    custom_rebars_svg = ElementTree.Element("g", attrib={"id": "CustomRebar"})
    rebars_svg.append(custom_rebars_svg)
    for rebar in custom_rebars:
        rebars_color = getRebarColor(rebar, rebars_color_style)
        rebars_color = getcolor(rebars_color)
        rebar_svg_draft = Draft.getSVG(
            rebar,
            direction=view_plane,
            linewidth=rebars_stroke_width,
            fillstyle="none",
            color=rebars_color,
        )
        if rebar_svg_draft:
            custom_rebars_svg.append(ElementTree.fromstring(rebar_svg_draft))

    # Create Structure SVG
    _structure_svg = '<g id="structure">{}</g>'.format(
        Draft.getSVG(
            structure,
            direction=view_plane,
            linewidth=structure_stroke_width,
            fillstyle=structure_fill_style,
        )
    )

    # Fix structure transparency (useful in console mode where
    # obj.ViewObject.Transparency is not available OR in gui mode if
    # structure transparency is ~0)
    if structure_fill_style != "none":
        if _structure_svg.find("fill-opacity") == -1:
            _structure_svg = _structure_svg.replace(
                ";fill:", ";fill-opacity:0.2;fill:"
            )
        else:
            import re

            _structure_svg = re.sub(
                '(fill-opacity:)([^:]+)(;|")', r"\1 0.2\3", _structure_svg
            )

    structure_svg = ElementTree.fromstring(_structure_svg)
    reinforcement_drawing.append(structure_svg)
    reinforcement_drawing.set(
        "transform", "translate({}, {})".format(round(-min_x), round(-min_y)),
    )

    svg_width = round(max_x - min_x)
    svg_height = round(max_y - min_y)

    svg.set("width", "{}mm".format(svg_width))
    svg.set("height", "{}mm".format(svg_height))
    svg.set("viewBox", "0 0 {} {}".format(svg_width, svg_height))

    return {"svg": svg, "rebars": visible_rebars}
