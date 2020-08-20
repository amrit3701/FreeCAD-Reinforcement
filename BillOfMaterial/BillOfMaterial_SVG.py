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


from xml.etree import ElementTree
from xml.dom import minidom

import FreeCAD

from SVGfunc import (
    getSVGRootElement,
    getSVGRectangle,
    getSVGDataCell,
    getTechdrawViewScalingFactor,
)
from .BOMfunc import (
    getMarkReinforcementsDict,
    getUniqueDiameterList,
    getRebarSharpEdgedLength,
    fixColumnUnits,
)
from .BillOfMaterialContent import makeBOMObject
from .BOMPreferences import BOMPreferences


def getColumnNumber(column_headers, diameter_list, column_header):
    """getColumnNumber(ColumnHeadersConfig, DiameterList, ColumnHeader):
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

    Returns position number of column in svg.
    """
    seq = column_headers[column_header][1]
    if "RebarsTotalLength" in column_headers:
        if column_headers["RebarsTotalLength"][1] < seq:
            if len(diameter_list) != 0:
                seq += len(diameter_list) - 1
    return seq


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
    column_headers_svg = ElementTree.Element("g")
    column_headers_svg.set("id", "BOM_column_headers")
    column_offset = 0
    if "RebarsTotalLength" in column_headers:
        height = 2 * row_height
    else:
        height = row_height

    column_seq = 1
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
                    "bom_table_cell_column_{}".format(column_seq),
                    "bold",
                )
            )
            column_offset += column_width
            column_seq += 1
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
                    "bom_table_cell_column_multi_column",
                    "bold",
                )
            )
            dia_headers_svg = ElementTree.Element("g")
            dia_headers_svg.set("id", "BOM_headers_diameter")
            for dia in diameter_list:
                dia_label = "#" + str(round(dia.Value, dia_precision))
                if "." in dia_label:
                    dia_label = dia_label.rstrip("0").rstrip(".")
                dia_headers_svg.append(
                    getSVGDataCell(
                        dia_label,
                        column_offset,
                        y_offset + row_height,
                        column_width,
                        row_height,
                        font_family,
                        font_size,
                        "bom_table_cell_column_{}".format(column_seq),
                        "bold",
                    )
                )
                column_offset += column_width
                column_seq += 1
            column_headers_svg.append(dia_headers_svg)

    return column_headers_svg


def makeBillOfMaterialSVG(
    column_headers=None,
    column_units=None,
    dia_weight_map=None,
    rebar_length_type=None,
    font_family=None,
    font_filename=None,
    font_size=None,
    column_width=None,
    row_height=None,
    bom_left_offset=None,
    bom_top_offset=None,
    bom_min_right_offset=None,
    bom_min_bottom_offset=None,
    bom_table_svg_max_width=None,
    bom_table_svg_max_height=None,
    template_file=None,
    output_file=None,
    rebar_objects=None,
    return_svg_only=False,
):
    """makeBillOfMaterialSVG([ColumnHeaders, ColumnUnits, DiaWeightMap,
    RebarLengthType, FontFamily, FontSize, FontFilename, ColumnWidth, RowHeight,
    BOMLeftOffset, BOMTopOffset, BOMMinRightOffset, BOMMinBottomOffset,
    BOMTableSVGMaxWidth, BOMTableSVGMaxHeight, TemplateFile, OutputFile,
    RebarObjects, ReturnSVGOnly]):
    Generates the Rebars Material Bill SVG.

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

    font_filename is required if you are working in pure console mode, without
    any gui.

    rebar_objects is the list of ArchRebar and/or rebar2 objects.

    If return_svg_only is True, then neither BOMContent object is created nor
    svg is written to output_file. And it returns svg element.
    Default is False.

    Returns Bill Of Material svg code.
    """
    # Get mark reinforcement dictionary
    mark_reinforcements_dict = getMarkReinforcementsDict(rebar_objects)
    if not mark_reinforcements_dict:
        FreeCAD.Console.PrintWarning(
            "No rebar object in current selection/document. "
            "Returning without BillOfMaterial SVG.\n"
        )
        return

    bom_preferences = BOMPreferences()
    if not column_headers:
        column_headers = bom_preferences.getColumnHeaders()
    if not column_units:
        column_units = bom_preferences.getColumnUnits()
    if not dia_weight_map:
        dia_weight_map = bom_preferences.getDiaWeightMap()
    if not rebar_length_type:
        rebar_length_type = bom_preferences.getRebarLengthType()

    svg_pref = bom_preferences.getSVGPrefGroup()
    if not font_family:
        font_family = svg_pref.GetString("FontFamily")
    if not font_filename:
        font_filename = svg_pref.GetString("FontFilename")
    if not font_size:
        font_size = svg_pref.GetFloat("FontSize")
    if not column_width:
        column_width = svg_pref.GetFloat("ColumnWidth")
    if not row_height:
        row_height = svg_pref.GetFloat("RowHeight")
    if not bom_left_offset:
        bom_left_offset = svg_pref.GetFloat("LeftOffset")
    if not bom_top_offset:
        bom_top_offset = svg_pref.GetFloat("TopOffset")
    if not bom_min_right_offset:
        bom_min_right_offset = svg_pref.GetFloat("MinRightOffset")
    if not bom_min_bottom_offset:
        bom_min_bottom_offset = svg_pref.GetFloat("MinBottomOffset")
    if not bom_table_svg_max_width:
        bom_table_svg_max_width = svg_pref.GetFloat("MaxWidth")
    if not bom_table_svg_max_height:
        bom_table_svg_max_height = svg_pref.GetFloat("MaxHeight")
    if not template_file:
        template_file = svg_pref.GetString("TemplateFile")

    # Delete hidden headers
    column_headers = {
        column_header: column_header_tuple
        for column_header, column_header_tuple in column_headers.items()
        if column_header_tuple[1] != 0
    }

    # Fix column units
    column_units = fixColumnUnits(column_units)

    # Get unique diameter list
    diameter_list = getUniqueDiameterList(mark_reinforcements_dict)

    svg = getSVGRootElement()

    # Get user preferred unit precision
    precision = FreeCAD.ParamGet(
        "User parameter:BaseApp/Preferences/Units"
    ).GetInt("Decimals")

    bom_table_svg = ElementTree.Element("g")
    bom_table_svg.set("id", "BOM_table")

    y_offset = 0
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

    for mark_number in mark_reinforcements_dict:
        if hasattr(mark_reinforcements_dict[mark_number][0], "BaseRebar"):
            base_rebar = mark_reinforcements_dict[mark_number][0].BaseRebar
        else:
            base_rebar = mark_reinforcements_dict[mark_number][0]

        bom_row_svg = ElementTree.Element("g")
        # TODO: Modify logic of str(current_row - first_row + 1)
        # first_row variable maybe eliminated
        bom_row_svg.set(
            "id", "BOM_table_row" + str(current_row - first_row + 1)
        )

        if "Mark" in column_headers:
            column_number = getColumnNumber(
                column_headers, diameter_list, "Mark"
            )
            column_offset = column_width * (column_number - 1)
            bom_row_svg.append(
                getSVGDataCell(
                    mark_number,
                    column_offset,
                    y_offset,
                    column_width,
                    row_height,
                    font_family,
                    font_size,
                    "bom_table_cell_column_{}".format(column_number),
                )
            )

        rebars_count = 0
        for reinforcement in mark_reinforcements_dict[mark_number]:
            rebars_count += reinforcement.Amount

        if "RebarsCount" in column_headers:
            column_number = getColumnNumber(
                column_headers, diameter_list, "RebarsCount"
            )
            column_offset = column_width * (column_number - 1)
            bom_row_svg.append(
                getSVGDataCell(
                    rebars_count,
                    column_offset,
                    y_offset,
                    column_width,
                    row_height,
                    font_family,
                    font_size,
                    "bom_table_cell_column_{}".format(column_number),
                )
            )

        if "Diameter" in column_headers:
            disp_diameter = str(
                round(
                    base_rebar.Diameter.getValueAs(
                        column_units["Diameter"]
                    ).Value,
                    precision,
                )
            )
            if "." in disp_diameter:
                disp_diameter = disp_diameter.rstrip("0").rstrip(".")
            disp_diameter += " " + column_units["Diameter"]
            column_number = getColumnNumber(
                column_headers, diameter_list, "Diameter"
            )
            column_offset = column_width * (column_number - 1)
            bom_row_svg.append(
                getSVGDataCell(
                    disp_diameter,
                    column_offset,
                    y_offset,
                    column_width,
                    row_height,
                    font_family,
                    font_size,
                    "bom_table_cell_column_{}".format(column_number),
                )
            )

        base_rebar_length = FreeCAD.Units.Quantity("0 mm")
        if "RebarLength" in column_headers:
            if rebar_length_type == "RealLength":
                base_rebar_length = base_rebar.Length
            else:
                base_rebar_length = getRebarSharpEdgedLength(base_rebar)
            disp_base_rebar_length = str(
                round(
                    base_rebar_length.getValueAs(
                        column_units["RebarLength"]
                    ).Value,
                    precision,
                )
            )
            if "." in disp_base_rebar_length:
                disp_base_rebar_length = disp_base_rebar_length.rstrip(
                    "0"
                ).rstrip(".")
            disp_base_rebar_length += " " + column_units["RebarLength"]

            column_number = getColumnNumber(
                column_headers, diameter_list, "RebarLength"
            )
            column_offset = column_width * (column_number - 1)
            bom_row_svg.append(
                getSVGDataCell(
                    disp_base_rebar_length,
                    column_offset,
                    y_offset,
                    column_width,
                    row_height,
                    font_family,
                    font_size,
                    "bom_table_cell_column_{}".format(column_number),
                )
            )

        rebar_total_length = FreeCAD.Units.Quantity("0 mm")
        for reinforcement in mark_reinforcements_dict[mark_number]:
            rebar_total_length += reinforcement.Amount * base_rebar_length
        dia_total_length_dict[base_rebar.Diameter.Value] += rebar_total_length

        if "RebarsTotalLength" in column_headers:
            disp_rebar_total_length = str(
                round(
                    rebar_total_length.getValueAs(
                        column_units["RebarsTotalLength"]
                    ).Value,
                    precision,
                )
            )
            if "." in disp_rebar_total_length:
                disp_rebar_total_length = disp_rebar_total_length.rstrip(
                    "0"
                ).rstrip(".")
            disp_rebar_total_length += " " + column_units["RebarsTotalLength"]

            column_number = getColumnNumber(
                column_headers, diameter_list, "RebarsTotalLength"
            )
            column_offset = column_width * (column_number - 1)
            for i, dia in enumerate(diameter_list):
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
                            "bom_table_cell_column_{}".format(
                                column_number + i
                            ),
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
                            "bom_table_cell_column_{}".format(
                                column_number + i
                            ),
                        )
                    )

        bom_table_svg.append(bom_row_svg)
        y_offset += row_height
        current_row += 1

    if "RebarsTotalLength" in column_headers:
        bom_table_svg.append(
            getSVGRectangle(
                0,
                y_offset,
                column_width * (len(column_headers) + len(diameter_list) - 1),
                row_height,
                "bom_table_cell_column_separator",
            )
        )
        y_offset += row_height

    # Display total length, weight/m and total weight of all rebars
    if "RebarsTotalLength" in column_headers:
        bom_data_total_svg = ElementTree.Element("g")
        bom_data_total_svg.set("id", "BOM_data_total")
        if column_headers["RebarsTotalLength"][1] != 1:
            column_number = getColumnNumber(
                column_headers, diameter_list, "RebarsTotalLength"
            )
            rebar_total_length_offset = column_width * (column_number - 1)

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
                    "bom_table_cell_column_multi_column",
                    "bold",
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
                    "bom_table_cell_column_multi_column",
                    "bold",
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
                    "bom_table_cell_column_multi_column",
                    "bold",
                )
            )

            for i, dia in enumerate(diameter_list):
                disp_dia_total_length = str(
                    round(
                        dia_total_length_dict[dia.Value]
                        .getValueAs(column_units["RebarsTotalLength"])
                        .Value,
                        precision,
                    )
                )
                if "." in disp_dia_total_length:
                    disp_dia_total_length = disp_dia_total_length.rstrip(
                        "0"
                    ).rstrip(".")
                disp_dia_total_length += " " + column_units["RebarsTotalLength"]

                bom_data_total_svg.append(
                    getSVGDataCell(
                        disp_dia_total_length,
                        rebar_total_length_offset + i * column_width,
                        y_offset,
                        column_width,
                        row_height,
                        font_family,
                        font_size,
                        "bom_table_cell_column_{}".format(column_number + i),
                    )
                )

                if dia.Value in dia_weight_map:
                    disp_dia_weight = str(
                        round(
                            dia_weight_map[dia.Value]
                            .getValueAs(
                                "kg/" + column_units["RebarsTotalLength"]
                            )
                            .Value,
                            precision,
                        )
                    )
                    if "." in disp_dia_weight:
                        disp_dia_weight = disp_dia_weight.rstrip("0").rstrip(
                            "."
                        )
                    disp_dia_weight += (
                        " kg/" + column_units["RebarsTotalLength"]
                    )

                    bom_data_total_svg.append(
                        getSVGDataCell(
                            disp_dia_weight,
                            rebar_total_length_offset + i * column_width,
                            y_offset + row_height,
                            column_width,
                            row_height,
                            font_family,
                            font_size,
                            "bom_table_cell_column_{}".format(
                                column_number + i
                            ),
                        )
                    )
                    disp_total_weight = str(
                        round(
                            (
                                dia_weight_map[dia.Value]
                                * dia_total_length_dict[dia.Value]
                            ).Value,
                            precision,
                        )
                    )
                    if "." in disp_total_weight:
                        disp_total_weight = disp_total_weight.rstrip(
                            "0"
                        ).rstrip(".")
                    bom_data_total_svg.append(
                        getSVGDataCell(
                            disp_total_weight + " kg",
                            rebar_total_length_offset + i * column_width,
                            y_offset + 2 * row_height,
                            column_width,
                            row_height,
                            font_family,
                            font_size,
                            "bom_table_cell_column_{}".format(
                                column_number + i
                            ),
                        )
                    )
                else:
                    bom_data_total_svg.append(
                        getSVGRectangle(
                            rebar_total_length_offset + i * column_width,
                            y_offset + row_height,
                            column_width,
                            row_height,
                            "bom_table_cell_column_{}".format(
                                column_number + i
                            ),
                        )
                    )
                    bom_data_total_svg.append(
                        getSVGRectangle(
                            rebar_total_length_offset + i * column_width,
                            y_offset + 2 * row_height,
                            column_width,
                            row_height,
                            "bom_table_cell_column_{}".format(
                                column_number + i
                            ),
                        )
                    )

            for remColumn in range(
                len(column_headers) - column_headers["RebarsTotalLength"][1]
            ):
                rem_column_number = (
                    column_headers["RebarsTotalLength"][1]
                    + len(diameter_list)
                    + remColumn
                )
                rem_column_offset = (column_number - 1) * column_width
                for row in range(3):
                    bom_data_total_svg.append(
                        getSVGRectangle(
                            rem_column_offset,
                            y_offset + row * row_height,
                            column_width,
                            row_height,
                            "bom_table_cell_column_{}".format(
                                rem_column_number
                            ),
                        )
                    )
        else:
            for i, dia in enumerate(diameter_list):
                disp_dia_total_length = str(
                    round(
                        dia_total_length_dict[dia.Value]
                        .getValueAs(column_units["RebarsTotalLength"])
                        .Value,
                        precision,
                    )
                )
                if "." in disp_dia_total_length:
                    disp_dia_total_length = disp_dia_total_length.rstrip(
                        "0"
                    ).rstrip(".")
                disp_dia_total_length += " " + column_units["RebarsTotalLength"]

                bom_data_total_svg.append(
                    getSVGDataCell(
                        disp_dia_total_length,
                        i * column_width,
                        y_offset,
                        column_width,
                        row_height,
                        font_family,
                        font_size,
                        "bom_table_cell_column_{}".format(i + 1),
                    )
                )

                if dia.Value in dia_weight_map:
                    disp_dia_weight = str(
                        round(
                            dia_weight_map[dia.Value]
                            .getValueAs(
                                "kg/" + column_units["RebarsTotalLength"]
                            )
                            .Value,
                            precision,
                        )
                    )
                    if "." in disp_dia_weight:
                        disp_dia_weight = disp_dia_weight.rstrip("0").rstrip(
                            "."
                        )
                    disp_dia_weight += (
                        " kg/" + column_units["RebarsTotalLength"]
                    )

                    bom_data_total_svg.append(
                        getSVGDataCell(
                            disp_dia_weight,
                            i * column_width,
                            y_offset + row_height,
                            column_width,
                            row_height,
                            font_family,
                            font_size,
                            "bom_table_cell_column_{}".format(i + 1),
                        )
                    )
                    disp_total_weight = str(
                        round(
                            (
                                dia_weight_map[dia.Value]
                                * dia_total_length_dict[dia.Value]
                            ).Value,
                            precision,
                        )
                    )
                    if "." in disp_total_weight:
                        disp_total_weight = disp_total_weight.rstrip(
                            "0"
                        ).rstrip(".")
                    bom_data_total_svg.append(
                        getSVGDataCell(
                            disp_total_weight + " kg",
                            i * column_width,
                            y_offset + 2 * row_height,
                            column_width,
                            row_height,
                            font_family,
                            font_size,
                            "bom_table_cell_column_{}".format(i + 1),
                        )
                    )

            first_txt_column_offset = len(diameter_list) * column_width
            bom_data_total_svg.append(
                getSVGDataCell(
                    "Total length in "
                    + column_units["RebarsTotalLength"]
                    + "/Diameter",
                    "multi_column",
                    y_offset,
                    column_width * (len(column_headers) - 1),
                    row_height,
                    font_family,
                    font_size,
                    "bom_table_cell_column_{}".format(first_txt_column_offset),
                    "bold",
                )
            )
            bom_data_total_svg.append(
                getSVGDataCell(
                    "Weight in Kg/" + column_units["RebarsTotalLength"],
                    "multi_column",
                    y_offset + row_height,
                    column_width * (len(column_headers) - 1),
                    row_height,
                    font_family,
                    font_size,
                    "bom_table_cell_column_{}".format(first_txt_column_offset),
                    "bold",
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
                    "bom_table_cell_column_multi_column",
                    "bold",
                )
            )
        y_offset += 3 * row_height
        bom_table_svg.append(bom_data_total_svg)
    svg.append(bom_table_svg)

    bom_height = y_offset
    if "RebarsTotalLength" in column_headers:
        bom_width = column_width * (
            len(column_headers) + len(diameter_list) - 1
        )
    else:
        bom_width = column_width * len(column_headers)
    svg.set("width", str(bom_width) + "mm")
    svg.set("height", str(bom_height) + "mm")
    svg.set("viewBox", "0 0 {} {}".format(bom_width, bom_height))
    if return_svg_only:
        return svg

    svg_output = minidom.parseString(
        ElementTree.tostring(svg, encoding="unicode")
    ).toprettyxml(indent="  ")

    bom_obj = makeBOMObject(template_file)
    template_height = bom_obj.Template.Height.Value
    template_width = bom_obj.Template.Width.Value

    scaling_factor = getTechdrawViewScalingFactor(
        bom_width,
        bom_height,
        bom_left_offset,
        bom_top_offset,
        template_width,
        template_height,
        bom_min_right_offset,
        bom_min_bottom_offset,
        bom_table_svg_max_width,
        bom_table_svg_max_height,
    )

    bom_content_obj = bom_obj.Views[0]
    bom_content_obj.Symbol = svg_output
    bom_content_obj.Font = font_family
    bom_content_obj.FontFilename = font_filename
    bom_content_obj.FontSize = font_size
    bom_content_obj.Template = bom_obj.Template
    bom_content_obj.PrefColumnWidth = column_width
    bom_content_obj.RowHeight = row_height
    bom_content_obj.Width = bom_width
    bom_content_obj.Height = bom_height
    bom_content_obj.LeftOffset = bom_left_offset
    bom_content_obj.TopOffset = bom_top_offset
    bom_content_obj.MinRightOffset = bom_min_right_offset
    bom_content_obj.MinBottomOffset = bom_min_bottom_offset
    bom_content_obj.MaxWidth = bom_table_svg_max_width
    bom_content_obj.MaxHeight = bom_table_svg_max_height
    bom_content_obj.X = bom_width * scaling_factor / 2 + bom_left_offset
    bom_content_obj.Y = (
        template_height - bom_height * scaling_factor / 2 - bom_top_offset
    )
    bom_content_obj.Scale = scaling_factor
    bom_content_obj.recompute()

    template_svg = ""
    try:
        with open(template_file, "r") as template:
            template_svg = template.read()
    except OSError:
        FreeCAD.Console.PrintError(
            "Error reading template file " + str(template_file) + "\n"
        )

    if output_file:
        svg_sheet = minidom.parseString(
            ElementTree.tostring(bom_table_svg, encoding="unicode")
        ).toprettyxml(indent="  ")

        if template_svg:
            bom_table_svg.set(
                "transform",
                "translate({} {}) scale({})".format(
                    bom_left_offset, bom_top_offset, scaling_factor
                ),
            )
            bom_svg = minidom.parseString(
                ElementTree.tostring(bom_table_svg, encoding="unicode")
            ).toprettyxml(indent="  ")
            # Remove xml declaration as XML declaration allowed only at the
            # start of the document
            if "<?xml" in bom_svg.splitlines()[0]:
                bom_svg = bom_svg.lstrip(bom_svg.splitlines()[0])
            svg_sheet = template_svg.replace("<!-- DrawingContent -->", bom_svg)

        try:
            with open(output_file, "w") as svg_output_file:
                svg_output_file.write(svg_sheet)
        except OSError:
            FreeCAD.Console.PrintError(
                "Error writing svg to file " + str(svg_output_file) + "\n"
            )

    FreeCAD.ActiveDocument.recompute()
    return bom_obj
