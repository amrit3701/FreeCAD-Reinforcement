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

__title__ = "SVG Functions"
__author__ = "Suraj"
__url__ = "https://www.freecadweb.org"


import math
from typing import Union
from xml.etree import ElementTree

import FreeCAD


# --------------------------------------------------------------------------
# Generic functions
# --------------------------------------------------------------------------


def getSVGRootElement() -> ElementTree.Element:
    """Returns svg tag element with freecad xmlns namespace.

    Returns
    -------
    ElementTree.Element
        The svg tag element with freecad xmlns namespace.
    """
    svg = ElementTree.Element("svg")
    svg.set("version", "1.1")
    svg.set("xmlns", "http://www.w3.org/2000/svg")
    svg.set("xmlns:xlink", "http://www.w3.org/1999/xlink")
    svg.set(
        "xmlns:freecad",
        "http://www.freecadweb.org/wiki/index.php?title=Svg_Namespace",
    )
    return svg


def getPointSVG(
    point: FreeCAD.Vector, radius: Union[float, str] = 1, fill: str = "black"
) -> ElementTree.Element:
    """Create and return point svg element.

    Parameters
    ----------
    point: <FreeCAD.Vector>
        The point to get its svg element.
    radius: float or str
        The radius of point in svg.
    fill: str
        The fill color for point in svg.

    Returns
    -------
    ElementTree.Element
        The point svg element.
    """
    point_svg = ElementTree.Element(
        "circle",
        cx=str(round(point.x)),
        cy=str(round(point.y)),
        r=str(radius),
        fill=fill,
    )
    return point_svg


def isPointInSVG(point, svg):
    if (
        svg.find(
            './/circle[@cx="{}"][@cy="{}"]'.format(
                round(point.x), round(point.y)
            ),
        )
        is not None
    ):
        return True
    else:
        return False


def getLineSVG(p1, p2, stroke_width=0.35, color="black"):
    line_svg = ElementTree.Element(
        "line",
        x1=str(round(p1.x)),
        y1=str(round(p1.y)),
        x2=str(round(p2.x)),
        y2=str(round(p2.y)),
        style="stroke:{};".format(color),
    )
    line_svg.set("stroke-width", str(stroke_width))
    line_svg.set("stroke", color)
    return line_svg


def isLineInSVG(p1, p2, svg):
    if (
        svg.find(
            './/line[@x1="{}"][@y1="{}"][@x2="{}"][@y2="{}"]'.format(
                round(p1.x), round(p1.y), round(p2.x), round(p2.y)
            ),
        )
        is not None
    ):
        return True
    elif (
        svg.find(
            './/line[@x1="{}"][@y1="{}"][@x2="{}"][@y2="{}"]'.format(
                round(p2.x), round(p2.y), round(p1.x), round(p1.y)
            ),
        )
        is not None
    ):
        return True
    else:
        return False


def getLinePathElement(
    points_list,
    stroke_width=0.35,
    stroke_style="Continuous",
    color="black",
    start_symbol="None",
    mid_points_symbol="None",
    end_symbol="None",
):
    """getLinePathElement(PointsList, [StrokeWidth, StrokeStyle, Color,
    StartSymbol, MidPointsSymbol, EndSymbol]):
    Returns line path joining given points.

    points_list is a list of points (x, y) defining line path.

    stroke_style can be "Continuous", "Dash", "Dot", "DashDot", "DashDotDot" OR
    stroke-dasharray value for line stroke.

    start_symbol/end_symbol can be "FilledArrow", "Tick", "Dot" or "None".

    mid_points_symbol can be "Tick", "Dot" or "None".
    """
    line_svg = ElementTree.Element("g")
    line_path_data = "M{} {}".format(points_list[0][0], points_list[0][1])
    for point in points_list[1:]:
        line_path_data += " L{} {}".format(point[0], point[1])
    line_path = ElementTree.Element(
        "path",
        d=line_path_data,
        style="stroke:{};stroke-width:{};stroke-linecap:round;"
        "fill:none;".format(color, stroke_width),
    )
    line_svg.append(line_path)

    # Set stroke style
    if stroke_style == "Continuous":
        line_path.set("stroke-dasharray", "")
    elif stroke_style == "Dash":
        line_path.set("stroke-dasharray", "4,2")
    elif stroke_style == "Dot":
        line_path.set("stroke-dasharray", "1,2")
    elif stroke_style == "DashDot":
        line_path.set("stroke-dasharray", "4,2, 1,2")
    elif stroke_style == "DashDotDot":
        line_path.set("stroke-dasharray", "4,2, 1,2, 1,2")
    else:
        line_path.set("stroke-dasharray", str(stroke_style))

    # Set start symbol
    if start_symbol == "FilledArrow":
        start_symbol_svg = getFilledArrowSVG(stroke_width, color)
    elif start_symbol == "Tick":
        start_symbol_svg = getTickSymbolSVG(stroke_width, color)
    elif start_symbol == "Dot":
        start_symbol_svg = getPointSVG(
            point=FreeCAD.Vector(0, 0, 0), radius=2 * stroke_width, fill=color
        )
    else:
        start_symbol_svg = None
    if start_symbol_svg is not None:
        start_symbol_svg.set(
            "transform",
            "translate({} {}) rotate({} 0 0)".format(
                points_list[0][0],
                points_list[0][1],
                math.degrees(
                    math.atan2(
                        points_list[0][1] - points_list[1][1],
                        points_list[0][0] - points_list[1][0],
                    )
                ),
            ),
        )
        line_svg.append(start_symbol_svg)

    # Set mid points symbol
    if mid_points_symbol == "Tick":
        mid_point_symbol_svg = getTickSymbolSVG(stroke_width, color)
    elif mid_points_symbol == "Dot":
        mid_point_symbol_svg = getPointSVG(
            FreeCAD.Vector(0, 0, 0), radius=2 * stroke_width, fill=color
        )
    else:
        mid_point_symbol_svg = None
    if mid_point_symbol_svg is not None:
        import copy

        mid_points_symbol_svg = ElementTree.Element("g", id="line_mid_points")
        p_point = points_list[0]
        for mid_point in points_list[1:-1]:
            mid_point_svg = copy.deepcopy(mid_point_symbol_svg)
            mid_point_svg.set(
                "transform",
                "translate({} {}) rotate({} 0 0)".format(
                    mid_point[0],
                    mid_point[1],
                    math.degrees(
                        math.atan2(
                            mid_point[1] - p_point[1], mid_point[0] - p_point[0]
                        )
                    ),
                ),
            )
            p_point = mid_point
            mid_points_symbol_svg.append(mid_point_svg)
        line_svg.append(mid_points_symbol_svg)

    # Set end symbol
    if end_symbol == "FilledArrow":
        end_symbol_svg = getFilledArrowSVG(stroke_width, color)
    elif end_symbol == "Tick":
        end_symbol_svg = getTickSymbolSVG(stroke_width, color)
    elif end_symbol == "Dot":
        end_symbol_svg = getPointSVG(
            point=FreeCAD.Vector(0, 0, 0), radius=2 * stroke_width, fill=color
        )
    else:
        end_symbol_svg = None
    if end_symbol_svg is not None:
        end_symbol_svg.set(
            "transform",
            "translate({} {}) rotate({} 0 0)".format(
                points_list[-1][0],
                points_list[-1][1],
                math.degrees(
                    math.atan2(
                        points_list[-1][1] - points_list[-2][1],
                        points_list[-1][0] - points_list[-2][0],
                    )
                ),
            ),
        )
        line_svg.append(end_symbol_svg)

    return line_svg


def getSVGTextElement(
    data,
    x_offset: Union[float, str],
    y_offset: Union[float, str],
    font_family: str,
    font_size: Union[float, str],
    text_anchor: str = "start",
    dominant_baseline: str = "baseline",
    preserve_space: bool = True,
    font_weight: Union[str, float] = "",
):
    """getSVGTextElement(Data, XOffset, YOffset, FontFamily, FontSize,
    [TextAnchor, DominantBaseline, PreserveSpace, FontWeight]):
    Returns text element with filled data and required placement.
    """
    text = ElementTree.Element(
        "text",
        x=str(round(x_offset)),
        y=str(round(y_offset)),
        style="",
        fill="#000000",
    )
    text.set("font-family", font_family)
    text.set("font-size", str(font_size))
    text.set("text-anchor", text_anchor)
    text.set("dominant-baseline", dominant_baseline)
    if preserve_space:
        text.set("style", "white-space:pre;")
        text.set("xml:space", "preserve")
    if font_weight:
        text.set("font-weight", str(font_weight))
    text.text = str(data)
    return text


def getSVGRectangle(x_offset, y_offset, width, height, element_id=None):
    """getSVGRectangle(XOffset, YOffset, RectangleWidth, RectangleHeight,
    ElementId):
    Returns rectangle element with required placement and size of rectangle.
    """
    rectangle_svg = ElementTree.Element(
        "rect",
        x=str(x_offset),
        y=str(y_offset),
        width=str(width),
        height=str(height),
        style="fill:none;stroke-width:0.35;stroke:#000000;",
    )
    if element_id:
        rectangle_svg.set("id", str(element_id))
    return rectangle_svg


def getSVGDataCell(
    data,
    x_offset,
    y_offset,
    width,
    height,
    font_family,
    font_size,
    element_id="",
    font_weight="",
):
    """getSVGDataCell(Data, XOffset, YOffset, CellWidth, CellHeight, FontFamily,
    FontSize, ElementId, FontWeight):
    Returns element with rectangular cell with filled data and required
    placement of cell.
    """
    cell_svg = ElementTree.Element("g")
    cell_svg.set("id", str(element_id))
    cell_svg.append(getSVGRectangle(x_offset, y_offset, width, height))
    cell_svg.append(
        getSVGTextElement(
            data,
            x_offset + width / 2,
            y_offset + height / 2,
            font_family,
            font_size,
            text_anchor="middle",
            dominant_baseline="central",
            font_weight=font_weight,
        )
    )
    return cell_svg


def getFilledArrowSVG(stroke_width=0.35, fill="black"):
    """getFilledArrowSVG([StrokeWidth, FillColor]):
    Returns arrow svg element placed at origin.
    """
    arrow_svg = ElementTree.Element(
        "path",
        d="M0,0 -8,-1.5 V1.5 L0,0",
        style="stroke:{color};fill:{color};stroke-width:{stroke_width};"
        "stroke-linecap:round;stroke-linejoin:bevel;".format(
            color=fill, stroke_width=str(stroke_width)
        ),
    )
    return arrow_svg


def getTickSymbolSVG(stroke_width=0.35, color="black"):
    """getTickSymbolSVG([StrokeWidth, Color]):
    Returns Tick(/) svg element with centre at origin.
    """
    tick_svg = ElementTree.Element(
        "path",
        d="M{} {} L{} {}".format(-2, 2, 2, -2),
        style="stroke:{};stroke-width:{};stroke-linecap:round;".format(
            color, stroke_width
        ),
    )
    return tick_svg


# --------------------------------------------------------------------------
# TechDraw SVG View functions
# --------------------------------------------------------------------------


def getTechdrawViewScalingFactor(
    view_width,
    view_height,
    view_left_offset,
    view_top_offset,
    template_width,
    template_height,
    view_min_right_offset,
    view_min_bottom_offset,
    view_table_max_width,
    view_table_max_height,
):
    """getTechdrawViewScalingFactor(ViewWidth, ViewHeight, ViewLeftOffset,
    ViewTopOffset, TemplateWidth, TemplateHeight, ViewMinRightOffset,
    ViewMinBottomOffset, ViewTableMaxWidth, ViewTableMaxHeight):
    Returns scaling factor for Techdraw svg view symbol object to fit inside
    template.
    """
    scale = False
    if (
        (template_width - view_width - view_left_offset - view_min_right_offset)
        < 0
        or (
            template_height
            - view_height
            - view_top_offset
            - view_min_bottom_offset
        )
        < 0
    ):
        scale = True

    if view_table_max_width:
        if view_table_max_width < view_width:
            scale = True

    if view_table_max_height:
        if view_table_max_height < view_height:
            scale = True

    if not scale:
        return 1

    h_scaling_factor = (
        template_width - view_left_offset - view_min_right_offset
    ) / view_width
    if view_table_max_width:
        h_scaling_factor = min(
            h_scaling_factor, view_table_max_width / view_width
        )

    v_scaling_factor = (
        template_height - view_top_offset - view_min_bottom_offset
    ) / view_height
    if view_table_max_height:
        v_scaling_factor = min(
            v_scaling_factor, view_table_max_height / view_height
        )

    scaling_factor = min(h_scaling_factor, v_scaling_factor)
    return scaling_factor
