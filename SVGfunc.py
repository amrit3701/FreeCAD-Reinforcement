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


from xml.etree import ElementTree


# --------------------------------------------------------------------------
# Generic functions
# --------------------------------------------------------------------------


def getSVGRootElement():
    """Returns svg tag element with freecad namespace."""
    svg = ElementTree.Element("svg")
    svg.set("version", "1.1")
    svg.set("xmlns", "http://www.w3.org/2000/svg")
    svg.set("xmlns:xlink", "http://www.w3.org/1999/xlink")
    svg.set(
        "xmlns:freecad",
        "http://www.freecadweb.org/wiki/index.php?title=Svg_Namespace",
    )
    return svg


def getPointSVG(point, radius=1):
    point_svg = ElementTree.Element(
        "circle",
        cx=str(round(point.x)),
        cy=str(round(point.y)),
        r=str(radius),
        fill="black",
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


def getLineSVG(p1, p2):
    line_svg = ElementTree.Element(
        "line",
        x1=str(round(p1.x)),
        y1=str(round(p1.y)),
        x2=str(round(p2.x)),
        y2=str(round(p2.y)),
        style="stroke:#000000",
    )
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


def getSVGTextElement(
    data,
    x_offset,
    y_offset,
    font_family,
    font_size,
    text_anchor="start",
    dominant_baseline="baseline",
):
    """getSVGTextElement(Data, XOffset, YOffset, FontFamily, FontSize,
    TextAnchor, DominantBaseline):
    Returns text element with filled data and required placement.
    """
    text = ElementTree.Element(
        "text", x=str(x_offset), y=str(y_offset), style="", fill="#000000"
    )
    text.set("font-family", font_family)
    text.set("font-size", str(font_size))
    text.set("text-anchor", text_anchor)
    text.set("dominant-baseline", dominant_baseline)
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
):
    """getSVGDataCell(Data, XOffset, YOffset, CellWidth, CellHeight, FontFamily,
    FontSize, ElementId):
    Returns element with rectangular cell with filled data and required
    pleacement of cell.
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
        )
    )
    return cell_svg


def getSVGPathElement(path_data, marker_start="", style=""):
    """getSVGPathElement(PathData, MarkerStart, Style):
    Return svg path element.
    """
    path = ElementTree.Element("path")
    path.set("d", str(path_data))
    path.set("style", str(style))
    path.set("marker-start", str(marker_start))
    return path


def getArrowMarkerElement(arrow_id, marker="start"):
    """getStartArrowSVGElement(ArrowId, [Marker]):
    arrow_id is id assigned to arrow marker element.
    marker can be "start" or "end".
    Returns arrow marker element.
    """
    if marker == "start":
        arrow_svg = ElementTree.Element("marker")
        arrow_svg.set("id", str(arrow_id))
        arrow_svg.set("refX", str(0))
        arrow_svg.set("refY", "3.5")
        arrow_svg.set("orient", "auto")
        arrow_svg.set("markerUnits", "strokeWidth")
        arrow_svg.append(
            ElementTree.Element("polygon", points="0 3.5, 10 0, 10 7")
        )
        return arrow_svg
    else:
        arrow_svg = ElementTree.Element("marker")
        arrow_svg.set("id", str(arrow_id))
        arrow_svg.set("refX", str(0))
        arrow_svg.set("refY", "3.5")
        arrow_svg.set("orient", "auto")
        arrow_svg.set("markerUnits", "strokeWidth")
        arrow_svg.append(
            ElementTree.Element("polygon", points="0 0, 0 7, 10 3.5")
        )
        return arrow_svg


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
