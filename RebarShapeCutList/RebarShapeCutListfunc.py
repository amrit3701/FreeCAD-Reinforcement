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

__title__ = "RebarShape Cut List Functions"
__author__ = "Suraj"
__url__ = "https://www.freecadweb.org"

import math
from typing import Union, List, Tuple, Optional, Literal
from xml.dom import minidom
from xml.etree import ElementTree

import Draft
import DraftGeomUtils
import DraftVecUtils
import FreeCAD
import Part
import WorkingPlane

from ReinforcementDrawing.ReinforcementDrawingfunc import (
    getRebarsSpanAxis,
    getSVGPlaneFromAxis,
    getProjectionToSVGPlane,
    getRoundEdgeSVG,
    getRebarColor,
)
from SVGfunc import (
    getSVGRootElement,
    getPointSVG,
    getLineSVG,
    getSVGTextElement,
    getSVGRectangle,
)


def getBaseRebarsList(
    objects_filter_list: Optional[List] = None, one_rebar_per_mark: bool = True,
) -> List:
    """
    Parameters
    ----------
    objects_filter_list: list, optional
        The list of FreeCAD objects containing ArchRebar and rebar2 objects.
        If it is empty or None, then ArchRebar and rebar2 objects will be
        selected from FreeCAD.ActiveDocument.Objects
        Default is None.
    one_rebar_per_mark: bool, optional
        If it is set to True, then only single rebar will be returned per mark.
        Otherwise all ArchRebar and rebar2.BaseRebar objects will be returned
        from active document.
        Default is True.

    Returns
    -------
    list of <ArchRebar> and <rebar2.BaseRebar>
        The list of ArchRebar and rebar2.BaseRebar objects from active document.
    """
    if not objects_filter_list:
        if not FreeCAD.ActiveDocument:
            return []
        objects_filter_list = FreeCAD.ActiveDocument.Objects

    rebars = []
    mark_list = []

    arch_rebars = Draft.get_objects_of_type(objects_filter_list, "Rebar")
    if one_rebar_per_mark:
        for rebar in arch_rebars:
            if rebar.Mark and rebar.Mark not in mark_list:
                rebars.append(rebar)
                mark_list.append(rebar.Mark)
    else:
        rebars.extend(arch_rebars)

    base_rebars = Draft.get_objects_of_type(objects_filter_list, "RebarShape")
    rebar_distribution_obj_types = [
        "ReinforcementGeneric",
        "ReinforcementLattice",
        "ReinforcementCustom",
        "ReinforcementIndividual",
        "ReinforcementLinear",
    ]
    for reinforcement_type in rebar_distribution_obj_types:
        base_rebars.extend(
            {
                x.BaseRebar
                for x in Draft.get_objects_of_type(
                    objects_filter_list, reinforcement_type
                )
                if x.BaseRebar not in base_rebars
            }
        )

    if one_rebar_per_mark:
        for rebar in base_rebars:
            if str(rebar.MarkNumber) and str(rebar.MarkNumber) not in mark_list:
                rebars.append(rebar)
                mark_list.append(str(rebar.MarkNumber))
    else:
        rebars.extend(base_rebars)

    rebars = sorted(
        rebars,
        key=lambda x: str(x.MarkNumber)
        if hasattr(x, "MarkNumber")
        else str(x.Mark),
    )

    return rebars


def getVertexesMinMaxXY(
    vertex_list: List[Part.Vertex], view_plane: WorkingPlane.Plane
) -> Tuple[float, float, float, float]:
    """Returns min_x, min_y, max_x, max_y for vertex_list, when each vertex
    is projected on view_plane.

    Parameters
    ----------
    vertex_list: list of Part.Vertex
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


def getBasewireOfStirrupWithExtendedEdges(
    stirrup, view_plane: WorkingPlane.Plane, extension_offset: float
) -> Part.Wire:
    """Returns stirrup base wire after adding extension_offset to stirrup
    extended edges, so that end edges of stirrup with 90 degree bent angle do
    not overlap with stirrup edges.

    Parameters
    ----------
    stirrup: <ArchRebar._Rebar>
        The stirrup with 90 degree bent angle.
    view_plane: WorkingPlane.Plane
        The view plane from which stirrup shape is visible.
    extension_offset: float
        The distance to move extended end edges of stirrup apart.

    Returns
    -------
    Part.Wire
        The generated stirrup base wire.
    """
    basewire = stirrup.Base.Shape.Wires[0].copy()

    # This function is meant for stirrup with bent angle 90 degree
    if stirrup.BentAngle != 90:
        return basewire

    min_x, min_y, max_x, max_y = getVertexesMinMaxXY(
        basewire.Vertexes, view_plane
    )

    def getModifiedEndEdgePoints(end_edge, coincident_edge):
        p1 = getProjectionToSVGPlane(end_edge.firstVertex().Point, view_plane)
        p2 = getProjectionToSVGPlane(end_edge.lastVertex().Point, view_plane)
        p3 = getProjectionToSVGPlane(
            coincident_edge.firstVertex().Point, view_plane
        )
        p4 = getProjectionToSVGPlane(
            coincident_edge.lastVertex().Point, view_plane
        )

        # The extended edge is vertical and is left side of stirrup And
        # coincident edge is horizontal
        if (round(p1.x) == round(p2.x) == round(min_x)) and (
            round(p3.y) == round(p4.y)
        ):
            mod_p1 = end_edge.firstVertex().Point.add(
                extension_offset * view_plane.u.negative().normalize()
            )
            mod_p2 = end_edge.lastVertex().Point.add(
                extension_offset * view_plane.u.negative().normalize()
            )
        # The extended edge is vertical and is right side of stirrup And
        # coincident edge is horizontal
        elif (round(p1.x) == round(p2.x) == round(max_x)) and (
            round(p3.y) == round(p4.y)
        ):
            mod_p1 = end_edge.firstVertex().Point.add(
                extension_offset * view_plane.u.normalize()
            )
            mod_p2 = end_edge.lastVertex().Point.add(
                extension_offset * view_plane.u.normalize()
            )
        # The extended edge is horizontal and is top side of stirrup And
        # coincident edge is vertical
        elif (round(p1.y) == round(p2.y) == round(min_y)) and (
            round(p3.x) == round(p4.x)
        ):
            mod_p1 = end_edge.firstVertex().Point.add(
                extension_offset * view_plane.v.negative().normalize()
            )
            mod_p2 = end_edge.lastVertex().Point.add(
                extension_offset * view_plane.v.negative().normalize()
            )
        # The extended edge is horizontal and is bottom side of stirrup And
        # coincident edge is vertical
        elif (round(p1.y) == round(p2.y) == round(max_y)) and (
            round(p3.x) == round(p4.x)
        ):
            mod_p1 = end_edge.firstVertex().Point.add(
                extension_offset * view_plane.v.normalize()
            )
            mod_p2 = end_edge.lastVertex().Point.add(
                extension_offset * view_plane.v.normalize()
            )
        else:
            # Don't modify any point
            mod_p1 = end_edge.firstVertex().Point
            mod_p2 = end_edge.lastVertex().Point
        return mod_p1, mod_p2

    edges = Part.__sortEdges__(basewire.Edges)
    # Modify one end edge
    point_1, point_2 = getModifiedEndEdgePoints(edges[0], edges[1])
    edges[0] = DraftGeomUtils.edg(point_1, point_2)
    edges[1] = DraftGeomUtils.edg(point_2, edges[1].lastVertex().Point)
    # Modify second end edge
    extension_offset = -1 * extension_offset
    point_1, point_2 = getModifiedEndEdgePoints(edges[-1], edges[-2])
    edges[-1] = DraftGeomUtils.edg(point_1, point_2)
    edges[-2] = DraftGeomUtils.edg(edges[-2].firstVertex().Point, point_1)

    return DraftGeomUtils.connect(edges)


def getEdgesAngleSVG(
    edge1: Part.Edge,
    edge2: Part.Edge,
    arc_radius: float,
    view_plane: WorkingPlane.Plane,
    font_family: str,
    font_size: Union[float, str],
    bent_angle_exclude_list: Tuple[float, ...] = (90, 180),
    stroke_width: Union[float, str] = 0.2,
    stroke_color: str = "black",
) -> ElementTree.Element:
    """Returns svg representation for angle between two edges by drawing an arc
    of given radius and adding angle text svg.
    It returns empty svg if edges doesn't intersect when extended infinitely.

    Parameters
    ----------
    edge1: Part.Edge
        The first edge to get its angle dimension svg with edge2.
    edge2:
        The second edge to get its angle dimension svg with edge1.
    arc_radius: float
        The radius of dimension arc.
    view_plane: WorkingPlane.Plane
        The view plane acting as svg plane.
    font_family: str
        The font-family of angle dimension.
    font_size: float or str
        The font-size of angle dimension.
    bent_angle_exclude_list: tuple of float, optional
        If angle between two edges is present in bent_angle_exclude_list,
        then empty svg element will be returned.
        Default is (90, 180)
    stroke_width: float or str, optional
        The stroke-width of arc svg.
        Default is 0.2
    stroke_color: str, optional
        The stroke color of arc svg.
        Default is "black".

    Returns
    -------
    ElementTree.Element
        The generated edges angle dimension svg.
    """
    intersection = DraftGeomUtils.findIntersection(edge1, edge2, True, True)
    if not intersection:
        return ElementTree.Element("g")
    else:
        intersection = intersection[0]

    p1 = max(
        DraftGeomUtils.getVerts(edge1),
        key=lambda x: x.distanceToPoint(intersection),
    )
    p2 = max(
        DraftGeomUtils.getVerts(edge2),
        key=lambda x: x.distanceToPoint(intersection),
    )
    angle = round(
        math.degrees(
            abs(DraftVecUtils.angle(p2.sub(intersection), p1.sub(intersection)))
        )
    )
    if angle in bent_angle_exclude_list:
        return ElementTree.Element("g")

    arc_p1 = intersection.add(arc_radius * p2.sub(intersection).normalize())
    arc_p2 = intersection.add(arc_radius * p1.sub(intersection).normalize())
    arc_edge = DraftGeomUtils.arcFrom2Pts(arc_p1, arc_p2, intersection)
    arc_svg = getRoundEdgeSVG(arc_edge, view_plane, stroke_width, stroke_color)

    arc_mid_point = DraftGeomUtils.findMidpoint(arc_edge)

    proj_intersection = getProjectionToSVGPlane(intersection, view_plane)
    proj_mid_point = getProjectionToSVGPlane(arc_mid_point, view_plane)

    if round(proj_intersection.x) < round(proj_mid_point.x):
        text_anchor = "start"
    elif round(proj_intersection.x) > round(proj_mid_point.x):
        text_anchor = "end"
    else:
        text_anchor = "middle"

    if round(proj_intersection.y) < round(proj_mid_point.y):
        text_y = proj_mid_point.y + font_size
    elif round(proj_intersection.y) > round(proj_mid_point.y):
        text_y = proj_mid_point.y
    else:
        text_y = proj_mid_point.y + font_size / 2

    angle_text_svg = getSVGTextElement(
        "{}°".format(angle),
        proj_mid_point.x,
        text_y,
        font_family,
        font_size,
        text_anchor,
    )

    bent_angle_svg = ElementTree.Element("g")
    bent_angle_svg.extend([arc_svg, angle_text_svg])
    return bent_angle_svg


def getRebarShapeSVG(
    rebar,
    view_direction: Union[FreeCAD.Vector, WorkingPlane.Plane] = FreeCAD.Vector(
        0, 0, 0
    ),
    include_mark: bool = True,
    stirrup_extended_edge_offset: float = 2,
    rebar_stroke_width: float = 0.35,
    rebar_color_style: str = "shape color",
    include_dimensions: bool = True,
    rebar_dimension_units: str = "mm",
    rebar_length_dimension_precision: int = 0,
    include_units_in_dimension_label: bool = False,
    bent_angle_dimension_exclude_list: Tuple[float, ...] = (45, 90, 180),
    dimension_font_family: str = "DejaVu Sans",
    dimension_font_size: float = 2,
    helical_rebar_dimension_label_format: str = "%L,r=%R,pitch=%P",
    scale: float = 1,
    max_height: float = 0,
    max_width: float = 0,
    side_padding: float = 1,
    horizontal_shape: bool = False,
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
    include_mark: bool, optional
        If True, then rebar.Mark will be included in rebar shape svg.
        Default is True.
    stirrup_extended_edge_offset: float, optional
        The offset of extended end edges of stirrup, so that end edges of
        stirrup with 90 degree bent angle do not overlap with stirrup edges.
        Default is 2.
    rebar_stroke_width: float, optional
        The stroke-width of rebar in svg.
        Default is 0.35
    rebar_color_style: {"shape color", "color_name", "hex_value_of_color"}
        The color style of rebar.
        "shape color" means select color of rebar shape.
    include_dimensions: bool, optional
        If True, then each rebar edge dimensions and bent angle dimensions will
        be included in rebar shape svg.
    rebar_dimension_units: str, optional
        The units to be used for rebar length dimensions.
        Default is "mm".
    rebar_length_dimension_precision: int, optional
        The number of decimals that should be shown for rebar length as
        dimension label. Set it to None to use user preferred unit precision
        from FreeCAD unit preferences.
        Default is 0
    include_units_in_dimension_label: bool, optional
        If it is True, then rebar length units will be shown in dimension label.
        Default is False.
    bent_angle_dimension_exclude_list: tuple of float, optional
        The tuple of bent angles to not include their dimensions.
        Default is (45, 90, 180).
    dimension_font_family: str, optional
        The font-family of dimension text.
        Default is "DejaVu Sans".
    dimension_font_size: float, optional
        The font-size of dimension text.
        Default is 2
    helical_rebar_dimension_label_format: str, optional
        The format of helical rebar dimension label.
            %L -> Length of helical rebar
            %R -> Helix radius of helical rebar
            %P -> Helix pitch of helical rebar
        Default is "%L,r=%R,pitch=%P".
    scale: float, optional
        The scale value to scale rebar svg. The scale parameter helps to
        scale down rebar_stroke_width and dimension_font_size to make them
        resolution independent.
        if max_height or max_width is set to non-zero value, then scale
        parameter will be ignored.
        Default is 1
    max_height: float, optional
        The maximum height of rebar shape svg.
        Default is 0 to set rebar shape svg height based on scale parameter.
    max_width: float, optional
        The maximum width of rebar shape svg.
        Default is 0 to set rebar shape svg width based on scale parameter.
    side_padding: float, optional
        The padding on each side of rebar shape.
        Default is 1.
    horizontal_shape: bool, optional
        If True, then rebar shape will be made horizontal by rotating -90
        degree if shape height is more than its width.
        If False, then rebar shape svg will be returned as viewed from
        view_direction.
        Default is False.

    Returns
    -------
    ElementTree.Element
        The generated rebar shape svg.
    """
    if isinstance(view_direction, FreeCAD.Vector):
        if DraftVecUtils.isNull(view_direction):
            if (
                hasattr(rebar, "RebarShape")
                and rebar.RebarShape == "HelicalRebar"
            ):
                view_direction = rebar.Base.Placement.Rotation.multVec(
                    FreeCAD.Vector(0, -1, 0)
                )
                if hasattr(rebar, "Direction") and not DraftVecUtils.isNull(
                    rebar.Direction
                ):
                    view_direction = FreeCAD.Vector(rebar.Direction)
                    view_direction.normalize()
            else:
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

    if rebar_length_dimension_precision is None:
        # Get user preferred unit precision
        precision: int = FreeCAD.ParamGet(
            "User parameter:BaseApp/Preferences/Units"
        ).GetInt("Decimals")
    else:
        precision = abs(int(rebar_length_dimension_precision))

    rebar_color = getRebarColor(rebar, rebar_color_style)

    # Create required svg elements
    svg = getSVGRootElement()
    rebar_shape_svg = ElementTree.Element("g", attrib={"id": str(rebar.Name)})
    svg.append(rebar_shape_svg)
    rebar_edges_svg = ElementTree.Element("g")
    edge_dimension_svg = ElementTree.Element("g")
    rebar_shape_svg.extend([rebar_edges_svg, edge_dimension_svg])

    # Get basewire and fillet_basewire (basewire with round edges)
    basewire = rebar.Base.Shape.Wires[0].copy()
    fillet_radius = rebar.Rounding * rebar.Diameter.Value
    if fillet_radius:
        fillet_basewire = DraftGeomUtils.filletWire(basewire, fillet_radius)
    else:
        fillet_basewire = basewire

    (
        rebar_shape_min_x,
        rebar_shape_min_y,
        rebar_shape_max_x,
        rebar_shape_max_y,
    ) = getVertexesMinMaxXY(fillet_basewire.Vertexes, view_plane)

    # If rebar shape should be horizontal and its width is less than its
    # height, then we should rotate basewire to make rebar shape horizontal
    rebar_shape_rotation_angle = 0
    if horizontal_shape:
        line_type_edges = [
            edge
            for edge in basewire.Edges
            if DraftGeomUtils.geomType(edge) == "Line"
        ]
        if line_type_edges:
            max_length_edge = max(line_type_edges, key=lambda x: x.Length)
            rebar_shape_rotation_angle = math.degrees(
                DraftVecUtils.angle(
                    max_length_edge.lastVertex().Point.sub(
                        max_length_edge.firstVertex().Point
                    ),
                    view_plane.u,
                    view_plane.axis,
                )
            )
        elif (rebar_shape_max_x - rebar_shape_min_x) < (
            rebar_shape_max_y - rebar_shape_min_y
        ):
            rebar_shape_rotation_angle = -90
        basewire.rotate(
            basewire.CenterOfMass, view_plane.axis, rebar_shape_rotation_angle
        )

        fillet_radius = rebar.Rounding * rebar.Diameter.Value
        if fillet_radius:
            fillet_basewire = DraftGeomUtils.filletWire(basewire, fillet_radius)
        else:
            fillet_basewire = basewire

        (
            rebar_shape_min_x,
            rebar_shape_min_y,
            rebar_shape_max_x,
            rebar_shape_max_y,
        ) = getVertexesMinMaxXY(fillet_basewire.Vertexes, view_plane)

    # Check if stirrup will be having extended edges separated apart
    if (
        hasattr(rebar, "RebarShape")
        and rebar.RebarShape == "Stirrup"
        and hasattr(rebar, "BentAngle")
        and rebar.BentAngle == 90
    ):
        apply_stirrup_extended_edge_offset = True
    else:
        apply_stirrup_extended_edge_offset = False

    # Apply max_height and max_width of rebar shape svg And calculate scaling
    # factor
    rebar_shape_height = (rebar_shape_max_y - rebar_shape_min_y) or 1
    rebar_shape_width = (rebar_shape_max_x - rebar_shape_min_x) or 1
    h_scaling_factor = v_scaling_factor = scale
    if max_height:
        v_scaling_factor = (
            max_height
            - dimension_font_size
            * ((2 if include_mark else 0) + (2 if include_dimensions else 0))
            - 2 * side_padding
            - (
                stirrup_extended_edge_offset
                if apply_stirrup_extended_edge_offset
                and (
                    round(
                        getProjectionToSVGPlane(
                            Part.__sortEdges__(basewire.Edges)[0]
                            .firstVertex()
                            .Point,
                            view_plane,
                        ).y
                    )
                    in (round(rebar_shape_min_y), round(rebar_shape_max_y))
                )
                else 0
            )
        ) / rebar_shape_height
    if max_width:
        h_scaling_factor = (
            max_width
            - dimension_font_size * (2 if include_dimensions else 0)
            - 2 * side_padding
            - (
                stirrup_extended_edge_offset
                if apply_stirrup_extended_edge_offset
                and (
                    round(
                        getProjectionToSVGPlane(
                            Part.__sortEdges__(basewire.Edges)[0]
                            .firstVertex()
                            .Point,
                            view_plane,
                        ).x
                    )
                    in (round(rebar_shape_min_x), round(rebar_shape_max_x))
                )
                else 0
            )
        ) / rebar_shape_width
    scale = min(h_scaling_factor, v_scaling_factor)
    svg_height = (
        rebar_shape_height * scale
        + dimension_font_size
        * ((2 if include_mark else 0) + (2 if include_dimensions else 0))
        + 2 * side_padding
        + (
            stirrup_extended_edge_offset
            if apply_stirrup_extended_edge_offset
            and (
                round(
                    getProjectionToSVGPlane(
                        Part.__sortEdges__(basewire.Edges)[0]
                        .firstVertex()
                        .Point,
                        view_plane,
                    ).y
                )
                in (round(rebar_shape_min_y), round(rebar_shape_max_y))
            )
            else 0
        )
    )
    svg_width = (
        rebar_shape_width * scale
        + dimension_font_size * (2 if include_dimensions else 0)
        + 2 * side_padding
        + (
            stirrup_extended_edge_offset
            if apply_stirrup_extended_edge_offset
            and (
                round(
                    getProjectionToSVGPlane(
                        Part.__sortEdges__(basewire.Edges)[0]
                        .firstVertex()
                        .Point,
                        view_plane,
                    ).x
                )
                in (round(rebar_shape_min_x), round(rebar_shape_max_x))
            )
            else 0
        )
    )

    # Move (min_x, min_y) point in svg plane to (0, 0) so that entire basewire
    # should be visible in svg view box and apply required scaling
    translate_x = round(
        -(
            rebar_shape_min_x
            - (dimension_font_size if include_dimensions else 0) / scale
            - side_padding / scale
            - (
                stirrup_extended_edge_offset / scale
                if apply_stirrup_extended_edge_offset
                and (
                    round(
                        getProjectionToSVGPlane(
                            Part.__sortEdges__(basewire.Edges)[0]
                            .firstVertex()
                            .Point,
                            view_plane,
                        ).x
                    )
                    == round(rebar_shape_min_x)
                )
                else 0
            )
        )
    )
    translate_y = round(
        -(
            rebar_shape_min_y
            - ((2 if include_mark else 0) + (1 if include_dimensions else 0))
            * dimension_font_size
            / scale
            - side_padding / scale
            - (
                stirrup_extended_edge_offset / scale
                if apply_stirrup_extended_edge_offset
                and (
                    round(
                        getProjectionToSVGPlane(
                            Part.__sortEdges__(basewire.Edges)[0]
                            .firstVertex()
                            .Point,
                            view_plane,
                        ).y
                    )
                    == round(rebar_shape_min_y)
                )
                else 0
            )
        )
    )
    rebar_shape_svg.set(
        "transform",
        "scale({}) translate({} {})".format(scale, translate_x, translate_y),
    )

    svg.set("width", "{}mm".format(round(svg_width)))
    svg.set("height", "{}mm".format(round(svg_height)))
    svg.set("viewBox", "0 0 {} {}".format(round(svg_width), round(svg_height)))

    # Scale down rebar_stroke_width and dimension_font_size to make them
    # resolution independent
    rebar_stroke_width /= scale
    dimension_font_size /= scale

    # Include rebar.Mark in rebar shape svg
    if include_mark:
        if hasattr(rebar, "Mark"):
            mark = rebar.Mark
        elif hasattr(rebar, "MarkNumber"):
            mark = rebar.MarkNumber
        else:
            mark = ""
        rebar_shape_svg.append(
            getSVGTextElement(
                mark,
                rebar_shape_min_x,
                rebar_shape_min_y
                - (0.5 + bool(include_dimensions)) * dimension_font_size,
                dimension_font_family,
                1.5 * dimension_font_size,
            )
        )

    if hasattr(rebar, "RebarShape") and rebar.RebarShape == "HelicalRebar":
        helical_rebar_shape_svg = Draft.getSVG(
            rebar,
            direction=view_plane,
            linewidth=rebar_stroke_width,
            fillstyle="none",
            color=rebar_color,
        )
        if helical_rebar_shape_svg:
            helical_rebar_shape_svg_element = ElementTree.fromstring(
                "<g>{}</g>".format(helical_rebar_shape_svg)
            )
            rebar_edges_svg.append(helical_rebar_shape_svg_element)
            helical_rebar_center = getProjectionToSVGPlane(
                rebar.Base.Shape.CenterOfMass, view_plane
            )
            helical_rebar_shape_svg_element.set(
                "transform",
                "rotate({} {} {})".format(
                    rebar_shape_rotation_angle,
                    helical_rebar_center.x,
                    helical_rebar_center.y,
                ),
            )

        if include_dimensions:
            # Create rebar dimension svg
            top_mid_point = FreeCAD.Vector(
                (rebar_shape_min_x + rebar_shape_max_x) / 2, rebar_shape_min_y
            )
            helical_rebar_length = str(
                round(
                    FreeCAD.Units.Quantity(
                        "{}mm".format(rebar.Base.Shape.Wires[0].Length)
                    )
                    .getValueAs(rebar_dimension_units)
                    .Value,
                    precision,
                )
            )
            helix_radius = str(
                round(
                    rebar.Base.Radius.getValueAs(rebar_dimension_units).Value,
                    precision,
                )
            )
            helix_pitch = str(
                round(
                    rebar.Base.Pitch.getValueAs(rebar_dimension_units).Value,
                    precision,
                )
            )
            if "." in helical_rebar_length:
                helical_rebar_length = helical_rebar_length.rstrip("0").rstrip(
                    "."
                )
            if "." in helix_radius:
                helix_radius = helix_radius.rstrip("0").rstrip(".")
            if "." in helix_pitch:
                helix_pitch = helix_pitch.rstrip("0").rstrip(".")
            if include_units_in_dimension_label:
                helical_rebar_length += rebar_dimension_units
                helix_radius += rebar_dimension_units
                helix_pitch += rebar_dimension_units
            edge_dimension_svg.append(
                getSVGTextElement(
                    helical_rebar_dimension_label_format.replace(
                        "%L", helical_rebar_length
                    )
                    .replace("%R", helix_radius)
                    .replace("%P", helix_pitch),
                    top_mid_point.x,
                    top_mid_point.y - rebar_stroke_width * 2,
                    dimension_font_family,
                    dimension_font_size,
                    "middle",
                )
            )
    else:
        if stirrup_extended_edge_offset and apply_stirrup_extended_edge_offset:
            basewire = getBasewireOfStirrupWithExtendedEdges(
                rebar, view_plane, stirrup_extended_edge_offset / scale
            )
            basewire.rotate(
                basewire.CenterOfMass,
                view_plane.axis,
                rebar_shape_rotation_angle,
            )

            fillet_radius = rebar.Rounding * rebar.Diameter.Value
            if fillet_radius:
                fillet_basewire = DraftGeomUtils.filletWire(
                    basewire, fillet_radius
                )
            else:
                fillet_basewire = basewire

        edges = Part.__sortEdges__(fillet_basewire.Edges)
        straight_edges = Part.__sortEdges__(rebar.Base.Shape.Wires[0].Edges)
        for edge in list(straight_edges):
            if DraftGeomUtils.geomType(edge) != "Line":
                straight_edges.remove(edge)

        current_straight_edge_index = 0
        for edge_index, edge in enumerate(edges):
            if DraftGeomUtils.geomType(edge) == "Line":
                p1 = getProjectionToSVGPlane(edge.Vertexes[0].Point, view_plane)
                p2 = getProjectionToSVGPlane(edge.Vertexes[1].Point, view_plane)
                # Create Edge svg
                if round(p1.x) == round(p2.x) and round(p1.y) == round(p2.y):
                    edge_svg = getPointSVG(
                        p1, radius=2 * rebar_stroke_width, fill=rebar_color
                    )
                else:
                    edge_svg = getLineSVG(
                        p1, p2, rebar_stroke_width, rebar_color
                    )

                if include_dimensions:
                    # Create edge dimension svg
                    mid_point = FreeCAD.Vector(
                        (p1.x + p2.x) / 2, (p1.y + p2.y) / 2
                    )
                    dimension_rotation = (
                        math.degrees(math.atan((p2.y - p1.y) / (p2.x - p1.x)))
                        if round(p2.x) != round(p1.x)
                        else -90
                    )
                    edge_length = str(
                        round(
                            FreeCAD.Units.Quantity(
                                "{}mm".format(
                                    straight_edges[
                                        current_straight_edge_index
                                    ].Length
                                )
                            )
                            .getValueAs(rebar_dimension_units)
                            .Value,
                            precision,
                        )
                    )
                    if "." in edge_length:
                        edge_length = edge_length.rstrip("0").rstrip(".")
                    if include_units_in_dimension_label:
                        edge_length += rebar_dimension_units
                    edge_dimension_svg.append(
                        getSVGTextElement(
                            edge_length,
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
                            dimension_rotation,
                            round(mid_point.x),
                            round(mid_point.y),
                        ),
                    )
                    current_straight_edge_index += 1
                    if (
                        0 <= edge_index - 1
                        and DraftGeomUtils.geomType(edges[edge_index - 1])
                        == "Line"
                    ):
                        radius = max(fillet_radius, dimension_font_size * 0.8)
                        bent_angle_svg = getEdgesAngleSVG(
                            edges[edge_index - 1],
                            edge,
                            radius,
                            view_plane,
                            dimension_font_family,
                            dimension_font_size * 0.8,
                            bent_angle_dimension_exclude_list,
                            0.2 / scale,
                        )
                        edge_dimension_svg.append(bent_angle_svg)
            elif DraftGeomUtils.geomType(edge) == "Circle":
                p1 = getProjectionToSVGPlane(edge.Vertexes[0].Point, view_plane)
                p2 = getProjectionToSVGPlane(edge.Vertexes[1].Point, view_plane)
                if round(p1.x) == round(p2.x) or round(p1.y) == round(p2.y):
                    edge_svg = getLineSVG(
                        p1, p2, rebar_stroke_width, rebar_color
                    )
                else:
                    edge_svg = getRoundEdgeSVG(
                        edge, view_plane, rebar_stroke_width, rebar_color
                    )
                    if include_dimensions:
                        # Create bent angle svg
                        if 0 <= edge_index - 1 and edge_index + 1 < len(edges):
                            prev_edge = edges[edge_index - 1]
                            next_edge = edges[edge_index + 1]
                            if (
                                DraftGeomUtils.geomType(prev_edge)
                                == DraftGeomUtils.geomType(next_edge)
                                == "Line"
                            ):
                                radius = max(
                                    fillet_radius, dimension_font_size * 0.8
                                )
                                bent_angle_svg = getEdgesAngleSVG(
                                    prev_edge,
                                    next_edge,
                                    radius,
                                    view_plane,
                                    dimension_font_family,
                                    dimension_font_size * 0.8,
                                    bent_angle_dimension_exclude_list,
                                    0.2 / scale,
                                )
                                edge_dimension_svg.append(bent_angle_svg)
            else:
                edge_svg = ElementTree.Element("g")
            rebar_edges_svg.append(edge_svg)

    return svg


def getRebarShapeCutList(
    base_rebars_list: Optional[List] = None,
    view_directions: Union[
        Union[FreeCAD.Vector, WorkingPlane.Plane],
        List[Union[FreeCAD.Vector, WorkingPlane.Plane]],
    ] = FreeCAD.Vector(0, 0, 0),
    include_mark: bool = True,
    stirrup_extended_edge_offset: float = 2,
    rebars_stroke_width: float = 0.35,
    rebars_color_style: str = "shape color",
    include_dimensions: bool = True,
    rebar_edge_dimension_units: str = "mm",
    rebar_edge_dimension_precision: int = 0,
    include_units_in_dimension_label: bool = False,
    bent_angle_dimension_exclude_list: Union[Tuple[float, ...], List[float]] = (
        45,
        90,
        180,
    ),
    dimension_font_family: str = "DejaVu Sans",
    dimension_font_size: float = 2,
    helical_rebar_dimension_label_format: str = "%L,r=%R,pitch=%P",
    row_height: float = 40,
    column_width: float = 60,
    column_count: Union[int, Literal["row_count"]] = "row_count",
    side_padding: float = 1,
    horizontal_rebar_shape: bool = True,
    output_file: Optional[str] = None,
) -> ElementTree.Element:
    """Generate and return rebar shape cut list svg.

    Parameters
    ----------
    base_rebars_list: list of <ArchRebar._Rebar> or <rebar2.BaseRebar>, optional
        Rebars list to generate RebarShape cut list.
        If None, then all ArchRebars and rebar2.BaseRebar objects with unique
        Mark from ActiveDocument will be selected and rebars with no Mark
        assigned will be ignored.
        Default is None.
    view_directions: FreeCAD.Vector or WorkingPlane.Plane OR their list
        The view point directions for each rebar shape.
        Default is FreeCAD.Vector(0, 0, 0) to automatically choose
        view_directions.
    include_mark: bool
        If it is set to True, then rebar.Mark will be included for each rebar
        shape in rebar shape cut list svg.
        Default is True.
    stirrup_extended_edge_offset: float
        The offset of extended end edges of stirrup, so that end edges of
        stirrup with 90 degree bent angle do not overlap with stirrup edges.
        Default is 2.
    rebars_stroke_width: float
        The stroke-width of rebars in rebar shape cut list svg.
        Default is 0.35
    rebars_color_style: {"shape color", "color_name", "hex_value_of_color"}
        The color style of rebars.
        "shape color" means select color of rebar shape.
    include_dimensions: bool
        If True, then each rebar edge dimensions and bent angle dimensions will
        be included in rebar shape cut list.
    rebar_edge_dimension_units: str
        The units to be used for rebar edge length dimensions.
        Default is "mm".
    rebar_edge_dimension_precision: int
        The number of decimals that should be shown for rebar edge length as
        dimension label. Set it to None to use user preferred unit precision
        from FreeCAD unit preferences.
        Default is 0
    include_units_in_dimension_label: bool
        If it is True, then rebar edge length units will be shown in dimension
        label.
        Default is False.
    bent_angle_dimension_exclude_list: tuple of float
        The tuple of bent angles to not include their dimensions.
        Default is (45, 90, 180).
    dimension_font_family: str
        The font-family of dimension text.
        Default is "DejaVu Sans".
    dimension_font_size: float
        The font-size of dimension text.
        Default is 2
    helical_rebar_dimension_label_format: str
        The format of helical rebar dimension label.
            %L -> Length of helical rebar
            %R -> Helix radius of helical rebar
            %P -> Helix pitch of helical rebar
        Default is "%L,r=%R,pitch=%P".
    row_height: float
        The height of each row of rebar shape in rebar shape cut list.
        Default is 40
    column_width: float
        The width of each column of rebar shape in rebar shape cut list.
        Default is 60
    column_count: int, {"row_count"}
        The number of columns in rebar shape cut list.
        "row_count" means column_count <= row_count
        Default is "row_count".
    side_padding: float
        The padding on each side of rebar shape.
        Default is 1.
    horizontal_rebar_shape: bool
        If True, then rebar shape will be made horizontal by rotating max
        length edge of rebar shape.
        Default is True.
    output_file: str, optional
        The output file to write generated svg.

    Returns
    -------
    ElementTree.Element
        The rebar shape cut list svg.
    """
    if base_rebars_list is None:
        base_rebars_list = getBaseRebarsList()

    if not base_rebars_list:
        return ElementTree.Element(
            "svg",
            height="{}mm".format(row_height),
            width="{}mm".format(column_width),
            viewBox="0 0 {} {}".format(column_width, row_height),
        )

    if isinstance(view_directions, FreeCAD.Vector) or isinstance(
        view_directions, WorkingPlane.Plane
    ):
        view_directions = len(base_rebars_list) * [view_directions]
    elif isinstance(view_directions, list):
        if len(view_directions) < len(base_rebars_list):
            view_directions.extend(
                (len(base_rebars_list) - len(view_directions))
                * FreeCAD.Vector(0, 0, 0)
            )
        else:
            view_directions = view_directions[len(base_rebars_list) :]

    rebar_shape_max_height = row_height
    if include_mark:
        rebar_shape_max_height -= 2 * dimension_font_size

    svg = getSVGRootElement()
    rebar_shape_cut_list = ElementTree.Element(
        "g", attrib={"id": "RebarShapeCutList"}
    )
    svg.append(rebar_shape_cut_list)

    if column_count == "row_count":
        column_count = max(
            x
            for x in list(range(1, len(base_rebars_list) + 1))
            if x ** 2 <= len(base_rebars_list)
        )
    else:
        column_count = min(column_count, len(base_rebars_list))

    row = 1
    for i, rebar in enumerate(base_rebars_list):
        column = (i % column_count) + 1
        row = int(i / column_count) + 1
        rebar_svg = getRebarShapeSVG(
            rebar,
            view_directions[i],
            False,
            stirrup_extended_edge_offset,
            rebars_stroke_width,
            rebars_color_style,
            include_dimensions,
            rebar_edge_dimension_units,
            rebar_edge_dimension_precision,
            include_units_in_dimension_label,
            bent_angle_dimension_exclude_list,
            dimension_font_family,
            dimension_font_size,
            helical_rebar_dimension_label_format,
            max_height=rebar_shape_max_height,
            max_width=column_width,
            side_padding=side_padding,
            horizontal_shape=horizontal_rebar_shape,
        )
        # Center align rebar shape svg horizontally and vertically in row cell
        rebar_shape_svg_width = float(rebar_svg.get("width").rstrip("mm"))
        rebar_shape_svg_height = float(rebar_svg.get("height").rstrip("mm"))
        rebar_shape_svg = ElementTree.Element(
            "g",
            transform="translate({} {})".format(
                (column_width - rebar_shape_svg_width) / 2,
                (rebar_shape_max_height - rebar_shape_svg_height) / 2
                + (2 * dimension_font_size if include_mark else 0),
            ),
        )
        rebar_shape_svg.append(
            rebar_svg.find("./g[@id='{}']".format(rebar.Name))
        )
        # Create cell border svg
        cell_border_svg = getSVGRectangle(
            0,
            0,
            column_width,
            row_height,
            element_id="row_{}_column_{}".format(row, column),
        )
        # Create row svg and translate it horizontally and vertically to its
        # position
        cell_svg = ElementTree.Element(
            "g",
            transform="translate({} {})".format(
                (column - 1) * column_width, (row - 1) * row_height
            ),
        )
        cell_svg.extend([cell_border_svg, rebar_shape_svg])
        # Include mark label in each row
        if include_mark:
            if hasattr(rebar, "Mark"):
                mark = rebar.Mark
            elif hasattr(rebar, "MarkNumber"):
                mark = rebar.MarkNumber
            else:
                mark = ""
            cell_svg.append(
                getSVGTextElement(
                    mark,
                    2,
                    2 * dimension_font_size,
                    dimension_font_family,
                    1.5 * dimension_font_size,
                )
            )
        rebar_shape_cut_list.append(cell_svg)
        # Add rectangular cells to last row for unfilled columns
        if i == len(base_rebars_list) - 1:
            for rem_col_index in range(column + 1, column_count + 1):
                cell_border_svg = getSVGRectangle(
                    0,
                    0,
                    column_width,
                    row_height,
                    element_id="row_{}_column_{}".format(row, rem_col_index),
                )
                cell_svg = ElementTree.Element(
                    "g",
                    transform="translate({} {})".format(
                        (rem_col_index - 1) * column_width,
                        (row - 1) * row_height,
                    ),
                )
                cell_svg.append(cell_border_svg)
                rebar_shape_cut_list.append(cell_svg)

    svg_width = column_count * column_width
    svg_height = row * row_height
    svg.set("width", "{}mm".format(svg_width))
    svg.set("height", "{}mm".format(svg_height))
    svg.set(
        "viewBox", "0 0 {} {}".format(svg_width, svg_height),
    )

    if output_file:
        svg_sheet = minidom.parseString(
            ElementTree.tostring(svg, encoding="unicode")
        ).toprettyxml(indent="  ")
        try:
            with open(output_file, "w", encoding="utf-8") as svg_output_file:
                svg_output_file.write(svg_sheet)
        except OSError:
            FreeCAD.Console.PrintError(
                "Error writing svg to file " + str(svg_output_file) + "\n"
            )

    return svg
