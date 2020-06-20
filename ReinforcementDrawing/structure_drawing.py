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

import FreeCAD
import Draft
import DraftGeomUtils
import DraftVecUtils
import WorkingPlane


def get_rebars_span_axis(rebar):
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


def get_projection_to_svg_plane(vec, plane):
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


def get_structure_min_max_points(structure, view_plane):
    min_x = 9999999
    min_y = 9999999
    max_x = -9999999
    max_y = -9999999
    vertex_list = structure.Shape.Vertexes
    for vertex in vertex_list:
        point = get_projection_to_svg_plane(vertex.Point, view_plane)
        min_x = min(min_x, point.x)
        min_y = min(min_y, point.y)
        max_x = max(max_x, point.x)
        max_y = max(max_y, point.y)
    return (min_x, min_y, max_x, max_y)


def get_line_svg(p1, p2, plane):
    if round(p1.x, 2) == round(p2.x, 2) and round(p1.y, 2) == round(p2.y, 2):
        line_svg = '<circle cx="{}" cy="{}" r="1" ' 'fill="black"/>'.format(
            round(p1.x, 2), round(p1.y, 2),
        )
    else:
        line_svg = (
            '<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
            'style="stroke:#000000"/>'.format(
                x1=round(p1.x, 2),
                y1=round(p1.y, 2),
                x2=round(p2.x, 2),
                y2=round(p2.y, 2),
            )
        )
    return line_svg


def get_line_dimensions_data(
    p1, p2, dimension_text, h_dim_x, h_dim_y, v_dim_x, v_dim_y
):
    if abs(p2.y - p1.y) < abs(p2.x - p1.x):
        dimension_line_horizontal = False
        x_cord = v_dim_x
        y_cord = (x_cord - p1.x) * (p2.y - p1.y) / (p2.x - p1.x) + p1.y
        dimension_line = (
            '<path d="M{} {} V{}" marker-start="url(#startarrow)" '
            'style="stroke:#000000"/>'.format(x_cord, y_cord, v_dim_y)
        )
        dimension_line += (
            '<text x="{}" y="{}" style="stroke-width:0.35px" fill="#000000" '
            'font-family="DejaVu Sans" font-size="10px" text-anchor="middle" '
            'dominant-baseline="baseline">{}</text>'
        ).format(v_dim_x, v_dim_y, dimension_text)
    else:
        dimension_line_horizontal = True
        y_cord = h_dim_y
        x_cord = (y_cord - p1.y) * (p2.x - p1.x) / (p2.y - p1.y) + p1.x
        dimension_line = (
            '<path d="M{} {} H{}" marker-start="url(#startarrow)" '
            'style="stroke:#000000"/>'.format(x_cord, y_cord, h_dim_x)
        )
        dimension_line += (
            '<text x="{}" y="{}" style="stroke-width:0.35px" fill="#000000" '
            'font-family="DejaVu Sans" font-size="10px" text-anchor="start" '
            'dominant-baseline="central">{}</text>'
        ).format(h_dim_x, h_dim_y, dimension_text)
    return {
        "svg": dimension_line,
        "dimension_line_horizontal": dimension_line_horizontal,
    }


def get_straight_rebar_svg_data(
    rebar,
    view_plane,
    h_dim_x_offset,
    h_dim_y_offset,
    v_dim_x_offset,
    v_dim_y_offset,
    svg,
):
    rebars_svg = ""
    min_x = 9999999
    min_y = 9999999
    max_x = -9999999
    max_y = -9999999
    is_rebar_visible = False
    drawing_plane_normal = view_plane.axis
    rebars_dimension_svg = ""
    if (
        round(drawing_plane_normal.cross(get_rebars_span_axis(rebar)).Length)
        == 0
    ):
        p1 = get_projection_to_svg_plane(
            rebar.Base.Shape.Wires[0].Vertexes[0].Point, view_plane
        )
        p2 = get_projection_to_svg_plane(
            rebar.Base.Shape.Wires[0].Vertexes[1].Point, view_plane
        )
        rebar_svg = get_line_svg(p1, p2, view_plane)
        if rebar_svg not in svg:
            rebars_svg += rebar_svg
            dimension_data = get_line_dimensions_data(
                p1,
                p2,
                "{}⌀{}".format(rebar.Amount, rebar.Diameter),
                h_dim_x_offset,
                h_dim_y_offset,
                v_dim_x_offset,
                v_dim_y_offset,
            )
            rebars_dimension_svg += dimension_data["svg"]
            if dimension_data["dimension_line_horizontal"]:
                # Add logic calculate increment
                h_dim_y_offset += 100
            else:
                v_dim_x_offset += 100
            min_x = min(p1.x, p2.x)
            min_y = min(p1.y, p2.y)
            max_x = max(p1.x, p2.x)
            max_y = max(p1.y, p2.y)
            is_rebar_visible = True
    else:
        basewire = rebar.Base.Shape.Wires[0]
        rebar_points = []
        for placement in rebar.PlacementList:
            wire = basewire.copy()
            wire.Placement = placement.multiply(basewire.Placement)
            p1 = get_projection_to_svg_plane(wire.Vertexes[0].Point, view_plane)
            p2 = get_projection_to_svg_plane(wire.Vertexes[1].Point, view_plane)
            rebar_svg = get_line_svg(p1, p2, view_plane)
            if rebar_svg not in svg and rebar_svg not in rebars_svg:
                rebars_svg += rebar_svg
                min_x = min(min_x, p1.x, p2.x)
                min_y = min(min_y, p1.y, p2.y)
                max_x = max(max_x, p1.x, p2.x)
                max_y = max(max_y, p1.y, p2.y)
                is_rebar_visible = True
            rebar_points.append((p1, p2))
    return {
        "svg": rebars_svg + rebars_dimension_svg,
        "visibility": is_rebar_visible,
        "min_x": min_x,
        "min_y": min_y,
        "max_x": max_x,
        "max_y": max_y,
        "h_dim_y_offset": h_dim_y_offset,
        "v_dim_x_offset": v_dim_x_offset,
    }


def get_reinforcement_drawing_svg(structure, rebars_list, view_direction):
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
    ) = get_structure_min_max_points(structure, view_plane)
    max_x = struct_max_x
    max_y = struct_max_y
    min_x = struct_min_x
    min_y = struct_min_y

    rebars_svg = '<g id="StraightRebar">'
    h_dim_x_offset = max_x + 50
    h_dim_y_offset = min_y + 50
    v_dim_x_offset = min_x + 50
    v_dim_y_offset = min_y - 50
    visible_rebars = []
    for rebar in straight_rebars:
        rebar_data = get_straight_rebar_svg_data(
            rebar,
            view_plane,
            h_dim_x_offset,
            h_dim_y_offset,
            v_dim_x_offset,
            v_dim_y_offset,
            rebars_svg,
        )
        if rebar_data["visibility"] is True:
            rebars_svg += rebar_data["svg"]
            min_x = min(min_x, rebar_data["min_x"])
            min_y = min(min_y, rebar_data["min_y"])
            max_x = max(max_x, rebar_data["max_x"])
            max_y = max(max_y, rebar_data["max_y"])
            h_dim_y_offset = rebar_data["h_dim_y_offset"]
            v_dim_x_offset = rebar_data["v_dim_x_offset"]
            visible_rebars.append(rebar)
    rebars_svg += "</g>"

    # Create Structure SVG
    structure_svg = Draft.getSVG(
        structure, direction=view_plane, fillstyle="none"
    )

    symbol_svg = (
        '<defs><marker id="startarrow" markerWidth="10" markerHeight="7" '
        'refX="0" refY="3.5" orient="auto"><polygon points="10 0, 10 7, 0 3.5"'
        "/></marker>"
        '<marker id="endarrow" markerWidth="10" markerHeight="7" refX="0" '
        'refY="3.5" orient="auto" markerUnits="strokeWidth"> <polygon '
        'points="0 0, 10 3.5, 0 7"/></marker>'
        "</defs>"
    )
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" height="{svg_height}mm" '
        'width="{svg_width}mm" viewBox="0 0 {svg_width} {svg_height}">'
        "<defs>{symbol_def}</defs>"
        '<g id="rebar_drawing" transform="translate({trans_x}, {trans_y})">'
        "{structure_svg}{rebars_svg}</g></svg>".format(
            svg_width=round(max_x - min_x + 200, 2),
            svg_height=round(max_y - min_y + 200, 2),
            symbol_def=symbol_svg,
            trans_x=round(-min_x + 60, 2),
            trans_y=round(-min_y + 100, 2),
            structure_svg=structure_svg,
            rebars_svg=rebars_svg,
        )
    )
    return svg


def get_reinforcement_drawing(structure, rebars_list, structure_view="Front"):
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
    svg = get_reinforcement_drawing_svg(structure, rebars_list, view_direction)
    return svg
