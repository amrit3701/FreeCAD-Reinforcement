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


import FreeCAD

from .BOMfunc import *
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


def getSVGHead():
    """Returns svg start tag with freecad namespace."""
    head = """<svg
    xmlns="http://www.w3.org/2000/svg" version="1.1"
    xmlns:freecad="http://www.freecadweb.org/wiki/index.php?title=Svg_Namespace">
    """.rstrip(
        "    "
    )
    return head


def getSVGDataCell(column_offset, row_offset, width, height, data, font_size):
    """getSVGDataCell(ColumnOffset, RowOffset, CellWidth, CellHeight, Data,
    FontSize):
    Returns svg code for rectangular cell with filled data and required
    pleacement of cell.
    """
    data_cell_svg = ""
    data_cell_svg += (
        '<rect x="{}" y="{}" width="{}" height="{}" '
        'style="fill:none;stroke-width:0.35;stroke:#000000;"/>\n'
    ).format(column_offset, row_offset, width, height)
    data_cell_svg += (
        '<text text-anchor="middle" style="" x="{}" y="{}" '
        'dominant-baseline="central" font-family="DejaVu Sans"'
        ' font-size="{}" fill="#000000">{}</text>\n'
    ).format(
        column_offset + width / 2, row_offset + height / 2, font_size, data,
    )
    return data_cell_svg


def getColumnHeadersSVG(
    column_headers, diameter_list, column_width, row_height, font_size
):
    """getColumnHeadersSVG(ColumnHeaders, DiameterList, ColumnWidth, RowHeight,
    FontSize):
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

    header_svg = '<g id="BOM_Headers">\n'
    column_offset = 0
    if "RebarsTotalLength" in column_headers:
        height = 2 * row_height
    else:
        height = row_height

    for column_header in sorted(
        column_headers, key=lambda x: column_headers[x][1]
    ):
        if column_header != "RebarsTotalLength":
            header_svg += "  " + getSVGDataCell(
                column_offset,
                0,
                column_width,
                height,
                column_headers[column_header][0],
                font_size,
            ).replace("\n", "\n  ").rstrip("  ")
            column_offset += column_width
        elif column_header == "RebarsTotalLength":
            header_svg += "  " + getSVGDataCell(
                column_offset,
                0,
                column_width * len(diameter_list),
                row_height,
                column_headers[column_header][0],
                font_size,
            ).replace("\n", "\n  ").rstrip("  ")
            header_svg += '  <g id="BOM_Headers_Diameter">\n'
            for dia in diameter_list:
                header_svg += "    " + getSVGDataCell(
                    column_offset,
                    row_height,
                    column_width,
                    row_height,
                    "#" + str(dia.Value).rstrip("0").rstrip("."),
                    font_size,
                ).replace("\n", "\n    ").rstrip("    ")
                column_offset += column_width
            header_svg += "  </g>\n"

    header_svg += "</g>\n"
    return header_svg


def getBOMonSheet(bom_svg, svg_size, bom_width, bom_height):
    """getBOMonSheet(BillOfMaterialSVG, SVGSize, BOMWidth, BOMHeight):
    svg_size is the size of svg sheet as widthxheight in mm.

    Returns svg setting BOM to fit svg size.
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

        bom_svg = bom_svg.replace(
            '<svg width="{width}mm" height="{height}mm" '
            'viewBox="0 0 {width} {height}"'.format(
                width=bom_width, height=bom_height
            ),
            '<svg width="{width}mm" height="{height}mm" '
            'viewBox="0 0 {width} {height}"'.format(
                width=svg_width, height=svg_height
            ),
        )

        bom_svg = bom_svg.replace(
            '<g id="BOM"',
            '<g id="BOM" transform="scale({})"'.format(svg_width / bom_width),
        )

        return bom_svg


def makeBillOfMaterialSVG(
    column_headers=COLUMN_HEADERS,
    column_units=COLUMN_UNITS,
    rebar_length_type=REBAR_LENGTH_TYPE,
    column_width=COLUMN_WIDTH,
    row_height=ROW_HEIGHT,
    svg_size=SVG_SIZE,
    font_size=FONT_SIZE,
    output_file=None,
):
    """makeBillOfMaterialSVG(ColumnHeaders, ColumnUnits, RebarLengthType,
    ColumnWidth, RowHeight, SVGSize, FontSize, OutputFile):
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
    head = getSVGHead()
    svg_output = head

    svg_output += '<g id="BOM">\n'
    indent_level = "  "

    mark_reinforcements_dict = getMarkReinforcementsDict()
    diameter_list = getUniqueDiameterList(mark_reinforcements_dict)
    header_svg = getColumnHeadersSVG(
        column_headers, diameter_list, column_width, row_height, font_size
    )
    svg_output += indent_level + header_svg.replace(
        "\n", "\n" + indent_level
    ).rstrip(indent_level)

    # Dictionary to store total length of rebars corresponding to its dia
    dia_total_length_dict = {
        dia.Value: FreeCAD.Units.Quantity("0 mm") for dia in diameter_list
    }

    # Add data to svg
    if "RebarsTotalLength" in column_headers:
        first_row = 3
        current_row = 3
    else:
        first_row = 2
        current_row = 2
    svg_output += indent_level + '<g id="BOM_Data">\n'
    indent_level += "  "
    for mark_number in sorted(mark_reinforcements_dict):
        base_rebar = mark_reinforcements_dict[mark_number][0].BaseRebar
        svg_output += (
            indent_level
            + '<g id="BOM_Data_row'
            + str(current_row - first_row + 1)
            + '">\n'
        )
        indent_level += "  "

        if "Mark" in column_headers:
            column_offset = getColumnOffset(
                column_headers, diameter_list, "Mark", column_width
            )
            svg_output += indent_level + getSVGDataCell(
                column_offset,
                row_height * (current_row - 1),
                column_width,
                row_height,
                mark_number,
                font_size,
            ).replace("\n", "\n" + indent_level).rstrip(indent_level)

        rebars_count = 0
        for reinforcement in mark_reinforcements_dict[mark_number]:
            rebars_count += reinforcement.Amount

        if "RebarsCount" in column_headers:
            column_offset = getColumnOffset(
                column_headers, diameter_list, "RebarsCount", column_width
            )
            svg_output += indent_level + getSVGDataCell(
                column_offset,
                row_height * (current_row - 1),
                column_width,
                row_height,
                rebars_count,
                font_size,
            ).replace("\n", "\n" + indent_level).rstrip(indent_level)

        if "Diameter" in column_headers:
            disp_diameter = base_rebar.Diameter
            if "Diameter" in column_units:
                disp_diameter = (
                    str(
                        disp_diameter.getValueAs(column_units["Diameter"]).Value
                    )
                    .rstrip("0")
                    .rstrip(".")
                    + " "
                    + column_units["Diameter"]
                )
            else:
                disp_diameter = disp_diameter.toStr()
            column_offset = getColumnOffset(
                column_headers, diameter_list, "Diameter", column_width
            )
            svg_output += indent_level + getSVGDataCell(
                column_offset,
                row_height * (current_row - 1),
                column_width,
                row_height,
                disp_diameter,
                font_size,
            ).replace("\n", "\n" + indent_level).rstrip(indent_level)

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
                        base_rebar_length.getValueAs(
                            column_units["RebarLength"]
                        ).Value
                    )
                    .rstrip("0")
                    .rstrip(".")
                    + " "
                    + column_units["RebarLength"]
                )
            else:
                disp_base_rebar_length = disp_base_rebar_length.toStr()

            column_offset = getColumnOffset(
                column_headers, diameter_list, "RebarLength", column_width
            )
            svg_output += indent_level + getSVGDataCell(
                column_offset,
                row_height * (current_row - 1),
                column_width,
                row_height,
                disp_base_rebar_length,
                font_size,
            ).replace("\n", "\n" + indent_level).rstrip(indent_level)

        rebar_total_length = FreeCAD.Units.Quantity("0 mm")
        for reinforcement in mark_reinforcements_dict[mark_number]:
            rebar_total_length += reinforcement.Amount * base_rebar_length
        dia_total_length_dict[base_rebar.Diameter.Value] += rebar_total_length

        if "RebarsTotalLength" in column_headers:
            disp_rebar_total_length = rebar_total_length
            if "RebarsTotalLength" in column_units:
                disp_rebar_total_length = (
                    str(
                        rebar_total_length.getValueAs(
                            column_units["RebarsTotalLength"]
                        ).Value
                    )
                    .rstrip("0")
                    .rstrip(".")
                    + " "
                    + column_units["RebarsTotalLength"]
                )
            else:
                disp_rebar_total_length = disp_rebar_total_length.toStr()

            column_offset = getColumnOffset(
                column_headers, diameter_list, "RebarsTotalLength", column_width
            )
            for dia in diameter_list:
                if dia == base_rebar.Diameter:
                    svg_output += indent_level + getSVGDataCell(
                        column_offset
                        + (diameter_list.index(dia)) * column_width,
                        row_height * (current_row - 1),
                        column_width,
                        row_height,
                        disp_rebar_total_length,
                        font_size,
                    ).replace("\n", "\n" + indent_level).rstrip(indent_level)
                else:
                    svg_output += (
                        indent_level
                        + '<rect x="{}" y="{}" width="{}" height="{}" '
                        'style="fill:none;stroke-width:0.35;stroke:#000000;"/>\n'
                    ).format(
                        column_offset + diameter_list.index(dia) * column_width,
                        row_height * (current_row - 1),
                        column_width,
                        row_height,
                    )

        indent_level = " " * (len(indent_level) - 2)
        svg_output += indent_level + "</g>\n"
        current_row += 1
    indent_level = " " * (len(indent_level) - 2)
    svg_output += indent_level + "</g>\n"

    svg_output += (
        indent_level + '<rect x="{}" y="{}" width="{}" height="{}" '
        'style="fill:none;stroke-width:0.35;stroke:#000000;"/>\n'
    ).format(
        0,
        row_height * (current_row - 1),
        column_width * (len(column_headers) + len(diameter_list) - 1),
        1 * row_height,
    )
    current_row += 1

    svg_output += indent_level + '<g id="BOM_Data_Total">\n'
    indent_level += "  "
    # Display total length, weight/m and total weight of all rebars
    if "RebarsTotalLength" in column_headers:
        if column_headers["RebarsTotalLength"][1] != 1:
            rebar_total_length_offset = getColumnOffset(
                column_headers, diameter_list, "RebarsTotalLength", column_width
            )

            svg_output += indent_level + getSVGDataCell(
                0,
                row_height * (current_row - 1),
                rebar_total_length_offset,
                row_height,
                "Total length in "
                + column_units["RebarsTotalLength"]
                + "/Diameter",
                font_size,
            ).replace("\n", "\n" + indent_level).rstrip(indent_level)
            svg_output += indent_level + getSVGDataCell(
                0,
                row_height * (current_row),
                rebar_total_length_offset,
                row_height,
                "Weight in Kg/" + column_units["RebarsTotalLength"],
                font_size,
            ).replace("\n", "\n" + indent_level).rstrip(indent_level)
            svg_output += indent_level + getSVGDataCell(
                0,
                row_height * (current_row + 1),
                rebar_total_length_offset,
                row_height,
                "Total Weight in Kg/Diameter",
                font_size,
            ).replace("\n", "\n" + indent_level).rstrip(indent_level)

            for i, dia in enumerate(diameter_list):
                disp_dia_total_length = dia_total_length_dict[dia.Value]
                if "RebarsTotalLength" in column_units:
                    disp_dia_total_length = (
                        str(
                            disp_dia_total_length.getValueAs(
                                column_units["RebarsTotalLength"]
                            ).Value
                        )
                        .rstrip("0")
                        .rstrip(".")
                        + " "
                        + column_units["RebarsTotalLength"]
                    )
                else:
                    disp_dia_total_length = disp_dia_total_length.toStr()

                svg_output += indent_level + getSVGDataCell(
                    rebar_total_length_offset + i * column_width,
                    row_height * (current_row - 1),
                    column_width,
                    row_height,
                    disp_dia_total_length,
                    font_size,
                ).replace("\n", "\n" + indent_level).rstrip(indent_level)

                if dia.Value in DIA_WEIGHT_MAP:
                    disp_dia_weight = DIA_WEIGHT_MAP[dia.Value]
                    if "RebarsTotalLength" in column_units:
                        disp_dia_weight = (
                            str(
                                disp_dia_weight.getValueAs(
                                    "kg/" + column_units["RebarsTotalLength"]
                                ).Value
                            )
                            .rstrip("0")
                            .rstrip(".")
                            + " "
                            + column_units["RebarsTotalLength"]
                        )
                    else:
                        disp_dia_weight = disp_dia_weight.toStr()

                    svg_output += indent_level + getSVGDataCell(
                        rebar_total_length_offset + i * column_width,
                        row_height * (current_row),
                        column_width,
                        row_height,
                        disp_dia_weight,
                        font_size,
                    ).replace("\n", "\n" + indent_level).rstrip(indent_level)
                    svg_output += indent_level + getSVGDataCell(
                        rebar_total_length_offset + i * column_width,
                        row_height * (current_row + 1),
                        column_width,
                        row_height,
                        (
                            DIA_WEIGHT_MAP[dia.Value]
                            * dia_total_length_dict[dia.Value]
                        ).toStr(),
                        font_size,
                    ).replace("\n", "\n" + indent_level).rstrip(indent_level)

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
                    svg_output += (
                        indent_level
                        + '<rect x="{}" y="{}" width="{}" height="{}" '
                        'style="fill:none;stroke-width:0.35;stroke:#000000;"/>\n'
                    ).format(
                        column_offset,
                        row_height * (current_row - 1 + row),
                        column_width,
                        row_height,
                    )
        else:
            for i, dia in enumerate(diameter_list):
                disp_dia_total_length = dia_total_length_dict[dia.Value]
                if "RebarsTotalLength" in column_units:
                    disp_dia_total_length = (
                        str(
                            disp_dia_total_length.getValueAs(
                                column_units["RebarsTotalLength"]
                            ).Value
                        )
                        .rstrip("0")
                        .rstrip(".")
                        + " "
                        + column_units["RebarsTotalLength"]
                    )
                else:
                    disp_dia_total_length = disp_dia_total_length.toStr()

                svg_output += indent_level + getSVGDataCell(
                    i * column_width,
                    row_height * (current_row - 1),
                    column_width,
                    row_height,
                    disp_dia_total_length,
                    font_size,
                ).replace("\n", "\n" + indent_level).rstrip(indent_level)

                if dia.Value in DIA_WEIGHT_MAP:
                    disp_dia_weight = DIA_WEIGHT_MAP[dia.Value]
                    if "RebarsTotalLength" in column_units:
                        disp_dia_weight = (
                            str(
                                disp_dia_weight.getValueAs(
                                    "kg/" + column_units["RebarsTotalLength"]
                                ).Value
                            )
                            .rstrip("0")
                            .rstrip(".")
                            + " "
                            + column_units["RebarsTotalLength"]
                        )
                    else:
                        disp_dia_weight = disp_dia_weight.toStr()

                    svg_output += indent_level + getSVGDataCell(
                        i * column_width,
                        row_height * (current_row),
                        column_width,
                        row_height,
                        disp_dia_weight,
                        font_size,
                    ).replace("\n", "\n" + indent_level).rstrip(indent_level)
                    svg_output += indent_level + getSVGDataCell(
                        i * column_width,
                        row_height * (current_row + 1),
                        column_width,
                        row_height,
                        (
                            DIA_WEIGHT_MAP[dia.Value]
                            * dia_total_length_dict[dia.Value]
                        ).toStr(),
                        font_size,
                    ).replace("\n", "\n" + indent_level).rstrip(indent_level)

            first_txt_column_offset = len(diameter_list) * column_width
            svg_output += indent_level + getSVGDataCell(
                first_txt_column_offset,
                row_height * (current_row - 1),
                column_width * (len(column_headers) - 1),
                row_height,
                "Total length in "
                + column_units["RebarsTotalLength"]
                + "/Diameter",
                font_size,
            ).replace("\n", "\n" + indent_level).rstrip(indent_level)
            svg_output += indent_level + getSVGDataCell(
                first_txt_column_offset,
                row_height * (current_row),
                column_width * (len(column_headers) - 1),
                row_height,
                "Weight in Kg/" + column_units["RebarsTotalLength"],
                font_size,
            ).replace("\n", "\n" + indent_level).rstrip(indent_level)
            svg_output += indent_level + getSVGDataCell(
                first_txt_column_offset,
                row_height * (current_row + 1),
                column_width * (len(column_headers) - 1),
                row_height,
                "Total Weight in Kg/Diameter",
                font_size,
            ).replace("\n", "\n" + indent_level).rstrip(indent_level)
    indent_level = " " * (len(indent_level) - 2)
    svg_output += indent_level + "</g>\n"

    svg_output += "</g>\n"
    svg_output += "\n</svg>"

    bom_height = row_height * (current_row + 2)
    bom_width = column_width * (len(column_headers) + len(diameter_list) - 1)

    svg_output = svg_output.replace(
        "<svg",
        '<svg width="{width}mm" height="{height}mm" '
        'viewBox="0 0 {width} {height}"'.format(
            width=bom_width, height=bom_height
        ),
    )

    svg_output = getBOMonSheet(svg_output, svg_size, bom_width, bom_height)

    if output_file:
        try:
            with open(output_file, "w") as svg_output_file:
                svg_output_file.write(svg_output)
        except:
            FreeCAD.Console.PrintError(
                "Error writing svg to file " + svg_output_file + "\n"
            )
    return svg_output
