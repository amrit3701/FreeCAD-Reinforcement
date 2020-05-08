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

__title__ = "Bill Of Material SVG"
__author__ = "Suraj"
__url__ = "https://www.freecadweb.org"


import os
import base64
from xml.etree import ElementTree

import FreeCAD

from .BOMfunc import (
    getMarkReinforcementsDict,
    getUniqueDiameterList,
    getRebarSharpEdgedLength,
    getStringWidth,
)
from .config import *


def getColumnOffset(column_headers, diameter_list, column_header, column_width):
    """getColumnOffset(ColumnHeadersConfig, DiameterList, ColumnHeader,
    ColumnWidth):
    column_headers is a dictionary with keys: "Mark", "RebarsCount", "Diameter",
    "RebarLength", "RebarsTotalLength" and values are tuple of column_header and
    its sequence number.
    e.g. {
            "Mark": ("Mark", 1),
            "RebarsCount": ("No. of Rebars", 2),
            "Diameter": ("Diameter in mm", 3),
            "RebarLength": ("Length in m/piece", 4),
            "RebarsTotalLength": ("Total Length in m", 5),
        }

    column_header is the key from dictionary column_headers for which we need to
    find its left offset in SVG.
    column_width is the width of each column in svg.

    Returns left offset of column in svg.
    """
    seq = column_headers[column_header][1]
    if "RebarsTotalLength" in column_headers:
        if column_headers["RebarsTotalLength"][1] < seq:
            if len(diameter_list) != 0:
                seq += len(diameter_list) - 1
    offset = column_width * (seq - 1)
    return offset


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


def getEditableSVGTextElement(
    data,
    element_id,
    x_offset,
    y_offset,
    font_family,
    font_size,
    text_anchor="start",
    dominant_baseline="baseline",
):
    """getEditableSVGTextElement(Data, ElementId, XOffset, YOffset, FontFamily,
    FontSize, TextAnchor, DominantBaseline):
    Returns freecad:editable text element with filled data and required
    placement.
    """
    text = getSVGTextElement(
        "",
        x_offset,
        y_offset,
        font_family,
        font_size,
        text_anchor,
        dominant_baseline,
    )
    text.set("freecad:editable", element_id)
    tspan = ElementTree.Element("tspan")
    tspan.text = str(data)
    text.append(tspan)
    return text


def getSVGRectangle(x_offset, y_offset, width, height):
    """getSVGRectangle(XOffset, YOffset, RectangleWidth, RectangleHeight):
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
    return rectangle_svg


def getSVGDataCell(
    data, x_offset, y_offset, width, height, font_family, font_size
):
    """getSVGDataCell(Data, XOffset, YOffset, CellWidth, CellHeight, FontFamily,
    FontSize):
    Returns element with rectangular cell with filled data and required
    pleacement of cell.
    """
    cell_svg = ElementTree.Element("g")
    cell_svg.set("id", "bom_table_cell")
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


def getSVGImage(image_file, x_offset, y_offset, image_width, image_height):
    """getSVGImage(ImageFile, XOffset, YOffset, ImageWidth, ImageHeight):
    Returns svg image element with required placement and size of image.
    """
    file_type = os.path.splitext(image_file)[1].lstrip(".").lower()
    valid_image_filetypes = ["png", "jpeg", "jpg", "ico", "bmp"]
    if file_type in valid_image_filetypes:
        # TODO: Add support for inserting svg image into BOM
        try:
            with open(image_file, "rb") as image:
                base64_encoded_image = base64.b64encode(image.read())
                base64_image = base64_encoded_image.decode("utf-8")
                svg_image = ElementTree.Element(
                    "image",
                    x=str(x_offset),
                    y=str(0),
                    width=str(image_width),
                    height=str(image_height),
                )
                svg_image.set(
                    "xlink:href",
                    "data:image/{};base64,{}".format(file_type, base64_image),
                )
                return svg_image
        except:
            FreeCAD.Console.PrintError(
                "Error opening file "
                + str(image_file)
                + "\nCannot insert image into BOM svg.\n"
            )
            return None
    else:
        FreeCAD.Console.PrintError(
            "Error: Unsupported image file type.\nValid file types for "
            "image are: " + ", ".join(valid_image_filetypes) + "\n"
        )
        return None


def getBOMSVGHeader(
    svg_bom_header_text,
    svg_header_project_info,
    svg_header_company_info,
    svg_header_company_logo,
    svg_header_company_logo_width,
    svg_header_company_logo_height,
    font_family,
    font_size,
    row_height,
    bom_width,
):
    """getBOMSVGHeader(BOMHeaderText, ProjectInfoHeader, CompanyInfoHeader,
    ComapyLogoFile, CompanyLogoWidth, CompanyLogoHeight, FontFamily, FontSize,
    RowHeight, BOMWidth):
    Returns (SVGHeaderElement, HeaderHeight) where SVGHeaderElement consists of
    svg elements for svg_bom_header_text, svg_header_project_info,
    svg_header_company_info, and svg_header_company_logo.
    """
    column_headers_svg = ElementTree.Element("g")
    column_headers_svg.set("id", "BOM_header")

    y_offset = 0
    if svg_bom_header_text:
        column_headers_svg.append(
            getEditableSVGTextElement(
                svg_bom_header_text.strip(),
                "BOM_header_text",
                0,
                4 * font_size,
                font_family,
                4 * font_size,
            )
        )
        y_offset += 4 * font_size

    project_info_y_offset = y_offset
    if svg_header_project_info:
        project_info_svg = ElementTree.Element("g")
        project_info_svg.set("id", "BOM_project_info")

        for i, line in enumerate(svg_header_project_info.strip().split("\n")):
            project_info_svg.append(
                getEditableSVGTextElement(
                    line,
                    "BOM_project_info_" + str(i),
                    0,
                    project_info_y_offset + 2 * font_size,
                    font_family,
                    2 * font_size,
                )
            )
            project_info_y_offset += 2 * font_size
        column_headers_svg.append(project_info_svg)

    company_info_y_offset = 0
    x_offset = bom_width
    if svg_header_company_info:
        x_offset = bom_width - max(
            getStringWidth(input_string, 2 * font_size, font_family)
            for input_string in svg_header_company_info.strip().split("\n")
        )
        company_info_svg = ElementTree.Element("g")
        company_info_svg.set("id", "BOM_company_info")

        for i, line in enumerate(svg_header_company_info.strip().split("\n")):
            line = line.strip()
            company_info_svg.append(
                getEditableSVGTextElement(
                    line,
                    "BOM_company_info_" + str(i),
                    x_offset,
                    company_info_y_offset + 2 * font_size,
                    font_family,
                    2 * font_size,
                )
            )
            company_info_y_offset += 2 * font_size
        column_headers_svg.append(company_info_svg)

    logo_height = 0
    if svg_header_company_logo:
        logo_svg = getSVGImage(
            svg_header_company_logo,
            x_offset - svg_header_company_logo_width - 2,
            0,
            svg_header_company_logo_width,
            svg_header_company_logo_height,
        )
        if logo_svg is not None:
            column_headers_svg.append(logo_svg)
            logo_height = svg_header_company_logo_height

    y_offset = (
        max(project_info_y_offset, company_info_y_offset, logo_height)
        + row_height
    )

    return (column_headers_svg, y_offset)


def getColumnHeadersSVG(
    column_headers,
    diameter_list,
    dia_precision,
    y_offset,
    column_width,
    row_height,
    font_family,
    font_size,
):
    """getColumnHeadersSVG(ColumnHeaders, DiameterList, DiameterPrecision,
    YOffset, ColumnWidth, RowHeight, FontFamily, FontSize):
    column_headers is a dictionary with keys: "Mark", "RebarsCount", "Diameter",
    "RebarLength", "RebarsTotalLength" and values are tuple of column_header and
    its sequence number.
    e.g. {
            "Mark": ("Mark", 1),
            "RebarsCount": ("No. of Rebars", 2),
            "Diameter": ("Diameter in mm", 3),
            "RebarLength": ("Length in m/piece", 4),
            "RebarsTotalLength": ("Total Length in m", 5),
        }

    Returns svg code for column headers.
    """
    # Delete hidden headers
    column_headers = {
        column_header: column_header_tuple
        for column_header, column_header_tuple in column_headers.items()
        if column_header_tuple[1] != 0
    }

    column_headers_svg = ElementTree.Element("g")
    column_headers_svg.set("id", "BOM_column_headers")
    column_offset = 0
    if "RebarsTotalLength" in column_headers:
        height = 2 * row_height
    else:
        height = row_height

    for column_header in sorted(
        column_headers, key=lambda x: column_headers[x][1]
    ):
        if column_header != "RebarsTotalLength":
            column_headers_svg.append(
                getSVGDataCell(
                    column_headers[column_header][0],
                    column_offset,
                    y_offset,
                    column_width,
                    height,
                    font_family,
                    font_size,
                )
            )
            column_offset += column_width
        elif column_header == "RebarsTotalLength":
            column_headers_svg.append(
                getSVGDataCell(
                    column_headers[column_header][0],
                    column_offset,
                    y_offset,
                    column_width * len(diameter_list),
                    row_height,
                    font_family,
                    font_size,
                )
            )
            dia_headers_svg = ElementTree.Element("g")
            dia_headers_svg.set("id", "BOM_headers_diameter")
            for dia in diameter_list:
                dia_headers_svg.append(
                    getSVGDataCell(
                        "#"
                        + str(round(dia.Value, dia_precision))
                        .rstrip("0")
                        .rstrip("."),
                        column_offset,
                        y_offset + row_height,
                        column_width,
                        row_height,
                        font_family,
                        font_size,
                    )
                )
                column_offset += column_width
            column_headers_svg.append(dia_headers_svg)

    return column_headers_svg


def getBOMSVGFooter(
    svg_footer_text, y_offset, bom_width, row_height, font_family, font_size
):
    """getBOMSVGFooter(FooterText, YOffset, BOMWidth, RowHeight, FontFamily,
    FontSize):
    Returns svg element for footer text.
    """
    footer_svg = ElementTree.Element("g")
    footer_svg.set("id", "BOM_footer")

    footer_width = getStringWidth(svg_footer_text, font_size, font_family)
    x_offset = bom_width - footer_width

    footer_svg.append(
        getEditableSVGTextElement(
            svg_footer_text,
            "BOM_footer",
            x_offset,
            y_offset + row_height,
            font_family,
            font_size,
        )
    )

    return footer_svg


def getBOMonSheet(
    bom_svg,
    svg_size,
    bom_width,
    bom_height,
    bom_left_offset,
    bom_right_offset,
    bom_top_offset,
    bom_bottom_offset,
):
    """getBOMonSheet(BillOfMaterialSVG, SVGSize, BOMWidth, BOMHeight,
    BOMLeftOffset, BOMRightOffset, BOMTopOffset, BOMBottomOffset):
    svg_size is the size of svg sheet as widthxheight in mm.

    Returns svg setting BOM to fit svg size applying required offsets.
    """
    if not svg_size:
        return bom_svg
    else:
        svg_width = 0
        svg_height = 0
        try:
            svg_width = float(svg_size.split("x")[0].strip())
            svg_height = float(svg_size.split("x")[1].strip())
        except:
            FreeCAD.Console.PrintError(
                "Unable to parse svg size to get weight and height.\n"
                "Expected format: widthxheight\n"
            )
            return bom_svg

        if svg_width == bom_width and svg_height == bom_height:
            return bom_svg

        h_scaling_factor = (
            svg_width - bom_left_offset - bom_right_offset
        ) / bom_width
        v_scaling_factor = (
            svg_height - bom_top_offset - bom_bottom_offset
        ) / bom_height

        bom_svg.set("width", str(svg_width) + "mm")
        bom_svg.set("height", str(svg_height) + "mm")

        if v_scaling_factor < h_scaling_factor:
            bom_svg.set(
                "viewBox",
                "-{left_offset} -{top_offset} {width} {height}".format(
                    left_offset=(svg_width - v_scaling_factor * bom_width) / 2,
                    top_offset=bom_top_offset,
                    width=svg_width,
                    height=svg_height,
                ),
            )
        else:
            bom_svg.set(
                "viewBox",
                "-{left_offset} -{top_offset} {width} {height}".format(
                    left_offset=bom_left_offset,
                    top_offset=bom_top_offset,
                    width=svg_width,
                    height=svg_height,
                ),
            )

        scaling_factor = min(h_scaling_factor, v_scaling_factor)
        bom_svg.find(".//*[@id='BOM_sheet']").set(
            "transform", "scale({})".format(scaling_factor)
        )

        return bom_svg


def makeBillOfMaterialSVG(
    column_headers=COLUMN_HEADERS,
    column_units=COLUMN_UNITS,
    rebar_length_type=REBAR_LENGTH_TYPE,
    svg_bom_header_text=SVG_BOM_HEADER_TEXT,
    svg_header_project_info=SVG_HEADER_PROJECT_INFO,
    svg_header_company_info=SVG_HEADER_COMPANY_INFO,
    svg_header_company_logo=SVG_HEADER_COMPANY_LOGO,
    svg_header_company_logo_width=SVG_HEADER_COMPANY_LOGO_WIDTH,
    svg_header_company_logo_height=SVG_HEADER_COMPANY_LOGO_HEIGHT,
    svg_footer_text=SVG_FOOTER_TEXT,
    font_family=FONT_FAMILY,
    font_size=FONT_SIZE,
    column_width=COLUMN_WIDTH,
    row_height=ROW_HEIGHT,
    bom_left_offset=BOM_SVG_LEFT_OFFSET,
    bom_right_offset=BOM_SVG_RIGHT_OFFSET,
    bom_top_offset=BOM_SVG_TOP_OFFSET,
    bom_bottom_offset=BOM_SVG_BOTTOM_OFFSET,
    svg_size=SVG_SIZE,
    output_file=None,
):
    """makeBillOfMaterialSVG(ColumnHeaders, ColumnUnits, RebarLengthType,
    SVGBOMHeaderText, SVGHeader_ProjectInfo, SVGHeader_CompanyInfo,
    SVGHeader_CompanyLogo, SVGHeader_CompanyLogoWidth,
    SVGHeader_CompanyLogoHeight, SVGFooterText, FontFamily, FontSize,
    ColumnWidth, RowHeight, BOMLeftOffset, BOMRightOffset, BOMTopOffset,
    BOMBottomOffset, SVGSize, OutputFile):
    Generates the Rebars Material Bill.

    column_headers is a dictionary with keys: "Mark", "RebarsCount", "Diameter",
    "RebarLength", "RebarsTotalLength" and values are tuple of column_header and
    its sequence number.
    e.g. {
            "Mark": ("Mark", 1),
            "RebarsCount": ("No. of Rebars", 2),
            "Diameter": ("Diameter in mm", 3),
            "RebarLength": ("Length in m/piece", 4),
            "RebarsTotalLength": ("Total Length in m", 5),
        }
    set column sequence number to 0 to hide column.

    column_units is a dictionary with keys: "Diameter", "RebarLength",
    "RebarsTotalLength" and their corresponding units as value.
    e.g. {
            "Diameter": "mm",
            "RebarLength": "m",
            "RebarsTotalLength": "m",
         }

    dia_weight_map is a dictionary with diameter as key and corresponding weight
    (kg/m) as value.
    e.g. {
            6: FreeCAD.Units.Quantity("0.222 kg/m"),
            8: FreeCAD.Units.Quantity("0.395 kg/m"),
            10: FreeCAD.Units.Quantity("0.617 kg/m"),
            12: FreeCAD.Units.Quantity("0.888 kg/m"),
            ...,
         }

    rebar_length_type can be "RealLength" or "LengthWithSharpEdges".

    Returns Bill Of Material svg code.
    """
    mark_reinforcements_dict = getMarkReinforcementsDict()
    diameter_list = getUniqueDiameterList(mark_reinforcements_dict)

    svg = getSVGRootElement()

    bom_sheet_svg = ElementTree.Element("g")
    bom_sheet_svg.set("id", "BOM_sheet")

    bom_width = column_width * (len(column_headers) + len(diameter_list) - 1)
    if (
        svg_bom_header_text
        or svg_header_project_info
        or svg_header_company_info
        or svg_header_company_logo
    ):
        svg_header, y_offset = getBOMSVGHeader(
            svg_bom_header_text,
            svg_header_project_info,
            svg_header_company_info,
            svg_header_company_logo,
            svg_header_company_logo_width,
            svg_header_company_logo_height,
            font_family,
            font_size,
            row_height,
            bom_width,
        )
        bom_sheet_svg.append(svg_header)

    # Get user preferred unit precision
    precision = FreeCAD.ParamGet(
        "User parameter:BaseApp/Preferences/Units"
    ).GetInt("Decimals")

    bom_table_svg = ElementTree.Element("g")
    bom_table_svg.set("id", "BOM_table")

    column_headers_svg = getColumnHeadersSVG(
        column_headers,
        diameter_list,
        precision,
        y_offset,
        column_width,
        row_height,
        font_family,
        font_size,
    )
    bom_table_svg.append(column_headers_svg)

    # Dictionary to store total length of rebars corresponding to its dia
    dia_total_length_dict = {
        dia.Value: FreeCAD.Units.Quantity("0 mm") for dia in diameter_list
    }

    if "RebarsTotalLength" in column_headers:
        first_row = 3
        current_row = 3
        y_offset += 2 * row_height
    else:
        first_row = 2
        current_row = 2
        y_offset += row_height

    for mark_number in sorted(mark_reinforcements_dict):
        base_rebar = mark_reinforcements_dict[mark_number][0].BaseRebar
        bom_row_svg = ElementTree.Element("g")
        # TODO: Modify logic of str(current_row - first_row + 1)
        # first_row variable maybe eliminated
        bom_row_svg.set(
            "id", "BOM_table_row" + str(current_row - first_row + 1)
        )

        if "Mark" in column_headers:
            column_offset = getColumnOffset(
                column_headers, diameter_list, "Mark", column_width
            )
            bom_row_svg.append(
                getSVGDataCell(
                    mark_number,
                    column_offset,
                    y_offset,
                    column_width,
                    row_height,
                    font_family,
                    font_size,
                )
            )

        rebars_count = 0
        for reinforcement in mark_reinforcements_dict[mark_number]:
            rebars_count += reinforcement.Amount

        if "RebarsCount" in column_headers:
            column_offset = getColumnOffset(
                column_headers, diameter_list, "RebarsCount", column_width
            )
            bom_row_svg.append(
                getSVGDataCell(
                    rebars_count,
                    column_offset,
                    y_offset,
                    column_width,
                    row_height,
                    font_family,
                    font_size,
                )
            )

        if "Diameter" in column_headers:
            disp_diameter = base_rebar.Diameter
            if "Diameter" in column_units:
                disp_diameter = (
                    str(
                        round(
                            disp_diameter.getValueAs(
                                column_units["Diameter"]
                            ).Value,
                            precision,
                        )
                    )
                    .rstrip("0")
                    .rstrip(".")
                    + " "
                    + column_units["Diameter"]
                )
            else:
                disp_diameter = str(round(disp_diameter, precision))
            column_offset = getColumnOffset(
                column_headers, diameter_list, "Diameter", column_width
            )
            bom_row_svg.append(
                getSVGDataCell(
                    disp_diameter,
                    column_offset,
                    y_offset,
                    column_width,
                    row_height,
                    font_family,
                    font_size,
                )
            )

        base_rebar_length = FreeCAD.Units.Quantity("0 mm")
        if "RebarLength" in column_headers:
            if rebar_length_type == "RealLength":
                base_rebar_length = base_rebar.Length
            else:
                base_rebar_length = getRebarSharpEdgedLength(base_rebar)
            disp_base_rebar_length = base_rebar_length
            if "RebarLength" in column_units:
                disp_base_rebar_length = (
                    str(
                        round(
                            base_rebar_length.getValueAs(
                                column_units["RebarLength"]
                            ).Value,
                            precision,
                        )
                    )
                    .rstrip("0")
                    .rstrip(".")
                    + " "
                    + column_units["RebarLength"]
                )
            else:
                disp_base_rebar_length = str(
                    round(disp_base_rebar_length, precision)
                )

            column_offset = getColumnOffset(
                column_headers, diameter_list, "RebarLength", column_width
            )
            bom_row_svg.append(
                getSVGDataCell(
                    disp_base_rebar_length,
                    column_offset,
                    y_offset,
                    column_width,
                    row_height,
                    font_family,
                    font_size,
                )
            )

        rebar_total_length = FreeCAD.Units.Quantity("0 mm")
        for reinforcement in mark_reinforcements_dict[mark_number]:
            rebar_total_length += reinforcement.Amount * base_rebar_length
        dia_total_length_dict[base_rebar.Diameter.Value] += rebar_total_length

        if "RebarsTotalLength" in column_headers:
            disp_rebar_total_length = rebar_total_length
            if "RebarsTotalLength" in column_units:
                disp_rebar_total_length = (
                    str(
                        round(
                            rebar_total_length.getValueAs(
                                column_units["RebarsTotalLength"]
                            ).Value,
                            precision,
                        )
                    )
                    .rstrip("0")
                    .rstrip(".")
                    + " "
                    + column_units["RebarsTotalLength"]
                )
            else:
                disp_rebar_total_length = str(
                    round(disp_rebar_total_length, precision)
                )

            column_offset = getColumnOffset(
                column_headers, diameter_list, "RebarsTotalLength", column_width
            )
            for dia in diameter_list:
                if dia == base_rebar.Diameter:
                    bom_row_svg.append(
                        getSVGDataCell(
                            disp_rebar_total_length,
                            column_offset
                            + (diameter_list.index(dia)) * column_width,
                            y_offset,
                            column_width,
                            row_height,
                            font_family,
                            font_size,
                        )
                    )
                else:
                    bom_row_svg.append(
                        getSVGRectangle(
                            column_offset
                            + diameter_list.index(dia) * column_width,
                            y_offset,
                            column_width,
                            row_height,
                        )
                    )

        bom_table_svg.append(bom_row_svg)
        y_offset += row_height
        current_row += 1

    bom_table_svg.append(
        getSVGRectangle(
            0,
            y_offset,
            column_width * (len(column_headers) + len(diameter_list) - 1),
            row_height,
        )
    )
    y_offset += row_height

    bom_data_total_svg = ElementTree.Element("g")
    bom_data_total_svg.set("id", "BOM_data_total")
    # Display total length, weight/m and total weight of all rebars
    if "RebarsTotalLength" in column_headers:
        if column_headers["RebarsTotalLength"][1] != 1:
            rebar_total_length_offset = getColumnOffset(
                column_headers, diameter_list, "RebarsTotalLength", column_width
            )

            bom_data_total_svg.append(
                getSVGDataCell(
                    "Total length in "
                    + column_units["RebarsTotalLength"]
                    + "/Diameter",
                    0,
                    y_offset,
                    rebar_total_length_offset,
                    row_height,
                    font_family,
                    font_size,
                )
            )
            bom_data_total_svg.append(
                getSVGDataCell(
                    "Weight in Kg/" + column_units["RebarsTotalLength"],
                    0,
                    y_offset + row_height,
                    rebar_total_length_offset,
                    row_height,
                    font_family,
                    font_size,
                )
            )
            bom_data_total_svg.append(
                getSVGDataCell(
                    "Total Weight in Kg/Diameter",
                    0,
                    y_offset + 2 * row_height,
                    rebar_total_length_offset,
                    row_height,
                    font_family,
                    font_size,
                )
            )

            for i, dia in enumerate(diameter_list):
                disp_dia_total_length = dia_total_length_dict[dia.Value]
                if "RebarsTotalLength" in column_units:
                    disp_dia_total_length = (
                        str(
                            round(
                                disp_dia_total_length.getValueAs(
                                    column_units["RebarsTotalLength"]
                                ).Value,
                                precision,
                            )
                        )
                        .rstrip("0")
                        .rstrip(".")
                        + " "
                        + column_units["RebarsTotalLength"]
                    )
                else:
                    disp_dia_total_length = str(
                        round(disp_dia_total_length, precision)
                    )

                bom_data_total_svg.append(
                    getSVGDataCell(
                        disp_dia_total_length,
                        rebar_total_length_offset + i * column_width,
                        y_offset,
                        column_width,
                        row_height,
                        font_family,
                        font_size,
                    )
                )

                if dia.Value in DIA_WEIGHT_MAP:
                    disp_dia_weight = DIA_WEIGHT_MAP[dia.Value]
                    if "RebarsTotalLength" in column_units:
                        disp_dia_weight = (
                            str(
                                round(
                                    disp_dia_weight.getValueAs(
                                        "kg/"
                                        + column_units["RebarsTotalLength"]
                                    ).Value,
                                    precision,
                                )
                            )
                            .rstrip("0")
                            .rstrip(".")
                            + " "
                            + column_units["RebarsTotalLength"]
                        )
                    else:
                        disp_dia_weight = str(round(disp_dia_weight, precision))

                    bom_data_total_svg.append(
                        getSVGDataCell(
                            disp_dia_weight,
                            rebar_total_length_offset + i * column_width,
                            y_offset + row_height,
                            column_width,
                            row_height,
                            font_family,
                            font_size,
                        )
                    )
                    bom_data_total_svg.append(
                        getSVGDataCell(
                            round(
                                DIA_WEIGHT_MAP[dia.Value]
                                * dia_total_length_dict[dia.Value],
                                precision,
                            ),
                            rebar_total_length_offset + i * column_width,
                            y_offset + 2 * row_height,
                            column_width,
                            row_height,
                            font_family,
                            font_size,
                        )
                    )
                else:
                    bom_data_total_svg.append(
                        getSVGRectangle(
                            rebar_total_length_offset + i * column_width,
                            y_offset + row_height,
                            column_width,
                            row_height,
                        )
                    )
                    bom_data_total_svg.append(
                        getSVGRectangle(
                            rebar_total_length_offset + i * column_width,
                            y_offset + 2 * row_height,
                            column_width,
                            row_height,
                        )
                    )

            for remColumn in range(
                len(column_headers) - column_headers["RebarsTotalLength"][1]
            ):
                column_offset = (
                    column_headers["RebarsTotalLength"][1]
                    + len(diameter_list)
                    - 1
                    + remColumn
                ) * column_width
                for row in range(3):
                    bom_data_total_svg.append(
                        getSVGRectangle(
                            column_offset,
                            y_offset + row * row_height,
                            column_width,
                            row_height,
                        )
                    )
        else:
            for i, dia in enumerate(diameter_list):
                disp_dia_total_length = dia_total_length_dict[dia.Value]
                if "RebarsTotalLength" in column_units:
                    disp_dia_total_length = (
                        str(
                            round(
                                disp_dia_total_length.getValueAs(
                                    column_units["RebarsTotalLength"]
                                ).Value,
                                precision,
                            )
                        )
                        .rstrip("0")
                        .rstrip(".")
                        + " "
                        + column_units["RebarsTotalLength"]
                    )
                else:
                    disp_dia_total_length = str(
                        round(disp_dia_total_length, precision)
                    )

                bom_data_total_svg.append(
                    getSVGDataCell(
                        disp_dia_total_length,
                        i * column_width,
                        y_offset,
                        column_width,
                        row_height,
                        font_family,
                        font_size,
                    )
                )

                if dia.Value in DIA_WEIGHT_MAP:
                    disp_dia_weight = DIA_WEIGHT_MAP[dia.Value]
                    if "RebarsTotalLength" in column_units:
                        disp_dia_weight = (
                            str(
                                round(
                                    disp_dia_weight.getValueAs(
                                        "kg/"
                                        + column_units["RebarsTotalLength"]
                                    ).Value,
                                    precision,
                                )
                            )
                            .rstrip("0")
                            .rstrip(".")
                            + " "
                            + column_units["RebarsTotalLength"]
                        )
                    else:
                        disp_dia_weight = str(round(disp_dia_weight, precision))

                    bom_data_total_svg.append(
                        getSVGDataCell(
                            disp_dia_weight,
                            i * column_width,
                            y_offset + row_height,
                            column_width,
                            row_height,
                            font_family,
                            font_size,
                        )
                    )
                    bom_data_total_svg.append(
                        getSVGDataCell(
                            round(
                                DIA_WEIGHT_MAP[dia.Value]
                                * dia_total_length_dict[dia.Value],
                                precision,
                            ),
                            i * column_width,
                            y_offset + 2 * row_height,
                            column_width,
                            row_height,
                            font_family,
                            font_size,
                        )
                    )

            first_txt_column_offset = len(diameter_list) * column_width
            bom_data_total_svg.append(
                getSVGDataCell(
                    "Total length in "
                    + column_units["RebarsTotalLength"]
                    + "/Diameter",
                    first_txt_column_offset,
                    y_offset,
                    column_width * (len(column_headers) - 1),
                    row_height,
                    font_family,
                    font_size,
                )
            )
            bom_data_total_svg.append(
                getSVGDataCell(
                    "Weight in Kg/" + column_units["RebarsTotalLength"],
                    first_txt_column_offset,
                    y_offset + row_height,
                    column_width * (len(column_headers) - 1),
                    row_height,
                    font_family,
                    font_size,
                )
            )
            bom_data_total_svg.append(
                getSVGDataCell(
                    "Total Weight in Kg/Diameter",
                    first_txt_column_offset,
                    y_offset + 2 * row_height,
                    column_width * (len(column_headers) - 1),
                    row_height,
                    font_family,
                    font_size,
                )
            )
    y_offset += 3 * row_height
    bom_table_svg.append(bom_data_total_svg)
    bom_sheet_svg.append(bom_table_svg)

    if svg_footer_text:
        footer_svg = getBOMSVGFooter(
            svg_footer_text,
            y_offset,
            bom_width,
            row_height,
            font_family,
            font_size,
        )
        bom_sheet_svg.append(footer_svg)
        y_offset += row_height
    svg.append(bom_sheet_svg)

    bom_height = y_offset
    bom_width = column_width * (len(column_headers) + len(diameter_list) - 1)

    svg.set("width", str(bom_width) + "mm")
    svg.set("height", str(bom_height) + "mm")
    svg.set("viewBox", "0 0 {} {}".format(bom_width, bom_height))

    svg = getBOMonSheet(
        svg,
        svg_size,
        bom_width,
        bom_height,
        bom_left_offset,
        bom_right_offset,
        bom_top_offset,
        bom_bottom_offset,
    )

    svg_output = ElementTree.tostring(svg, encoding="unicode")

    if output_file:
        try:
            with open(output_file, "w") as svg_output_file:
                svg_output_file.write(svg_output)
        except:
            FreeCAD.Console.PrintError(
                "Error writing svg to file " + svg_output_file + "\n"
            )
    return svg_output
