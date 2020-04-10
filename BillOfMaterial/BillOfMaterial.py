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

__title__ = "Bill Of Material"
__author__ = "Suraj"
__url__ = "https://www.freecadweb.org"


import FreeCAD
from .config import *


def getMarkReinforcementsDict():
    # Get Part::FeaturePython objects list
    objects_list = FreeCAD.ActiveDocument.findObjects("Part::FeaturePython")

    # Create dictionary with mark number as key with corresponding reinforcement
    # objects list as value
    default_mark_number = 0
    mark_reinforcements_dict = {}
    for item in objects_list:
        if hasattr(item, "BaseRebar"):
            if hasattr(item.BaseRebar, "IfcType"):
                if item.BaseRebar.IfcType == "Reinforcing Bar":
                    if not hasattr(item.BaseRebar, "MarkNumber"):
                        mark_number = default_mark_number
                    else:
                        mark_number = item.BaseRebar.MarkNumber
                    if mark_number not in mark_reinforcements_dict:
                        mark_reinforcements_dict[mark_number] = []
                    mark_reinforcements_dict[mark_number].append(item)
    return mark_reinforcements_dict


def addSheetHeaders(column_headers, spreadsheet):
    """addSheetHeaders(ColumnHeaders, Spreadsheet):
    Add headers to columns in spreadsheet object.
    """
    # Delete hidden headers
    column_headers = {
        column_header: column_header_tuple
        for column_header, column_header_tuple in column_headers.items()
        if column_header_tuple[1] != 0
    }

    # Format cells and insert headers if column "RebarsTotalLength" is to be
    # shown in BOM, only insert headers otherwise
    if "RebarsTotalLength" in column_headers:
        for column_header in column_headers:
            column = chr(ord("A") + column_headers[column_header][1] - 1)
            if column_header != "RebarsTotalLength":
                spreadsheet.mergeCells(column + "1:" + column + "2")
                spreadsheet.set(column + "1", column_headers[column_header][0])
            elif column_header == "RebarsTotalLength":
                spreadsheet.set(column + "1", column_headers[column_header][0])
    else:
        for column_header in column_headers:
            column = chr(ord("A") + column_headers[column_header][1] - 1)
            spreadsheet.set(column + "1", column_headers[column_header][0])

    return column_headers


def addDiameterHeader(dia, diameter_list, column_headers, spreadsheet):
    """addDiameterHeader(Diameter, DiameterList, ColumnHeaders, Spreadsheet):
    Add diameter header under total rebar length column header.
    """
    # Split previously merged main header cells
    first_dia_column = chr(
        ord("A") + column_headers["RebarsTotalLength"][1] - 1
    )
    spreadsheet.splitCell(first_dia_column + "1")

    # Create new column to insert dia
    loc = column_headers["RebarsTotalLength"][1] - 1 + diameter_list.index(dia)
    new_column = chr(ord("A") + loc)
    if len(diameter_list) != 1:
        spreadsheet.insertColumns(new_column, 1)

    # Merge main header cells and set alignment
    last_dia_column = chr(
        ord("A")
        + column_headers["RebarsTotalLength"][1]
        - 1
        + len(diameter_list)
        - 1
    )
    spreadsheet.mergeCells(first_dia_column + "1:" + last_dia_column + "1")
    spreadsheet.setAlignment(
        first_dia_column + "1:" + last_dia_column + "1", "center|vcenter"
    )
    spreadsheet.setAlignment(
        first_dia_column + "2:" + last_dia_column + "2", "center|vcenter"
    )

    # Insert dia column header
    spreadsheet.set(
        first_dia_column + "1", column_headers["RebarsTotalLength"][0]
    )
    spreadsheet.set(new_column + "2", "#" + str(dia.Value))


def getRebarSharpEdgedLength(rebar):
    """getRebarSharpEdgedLength(Rebar):
    Returns sharp edged length of rebar object.
    """
    base = rebar.Base
    # When rebar is drived from DWire
    if hasattr(base, "Length"):
        # When wire shape is created using DraftGeomUtils.filletWire()
        if not hasattr(base, "FilletRadius"):
            return base.Length
        # If FilletRadius of DWire is zero
        elif not base.FilletRadius:
            return base.Length
        else:
            edges = base.Shape.Edges
            if base.Closed:
                corners = len(edges) / 2
            else:
                corners = (len(edges) - 1) / 2
            extension_length = 2 * corners * base.FilletRadius
            rebar_straight_length = 0
            for edge in edges[::2]:
                rebar_straight_length += edge.Length
            rebar_sharp_edged_length = (
                FreeCAD.Units.Quantity(str(rebar_straight_length) + "mm")
                + extension_length
            )
            return rebar_sharp_edged_length
    # When rebar is drived from Sketch
    elif base.isDerivedFrom("Sketcher::SketchObject"):
        rebar_length = 0
        for geo in base.Geometry:
            rebar_length += geo.length()
        return FreeCAD.Units.Quantity(str(rebar_length) + "mm")
    else:
        print("Cannot calculate rebar length from its base object")
        return FreeCAD.Units.Quantity("0 mm")


def makeBillOfMaterial(
    column_headers=COLUMN_HEADERS,
    column_units=COLUMN_UNITS,
    dia_weight_map=DIA_WEIGHT_MAP,
    rebar_length_type=REBAR_LENGTH_TYPE,
    structures_list=None,
    obj_name="RebarBillOfMaterial",
):
    """makeBillOfMaterial(ColumnHeadersConfig, ColumnUnitsDict, DiaWeightMap,
    RebarLengthType, StructuresList, ObjectName):
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
    """
    # Create new spreadsheet object
    bill_of_material = FreeCAD.ActiveDocument.addObject(
        "Spreadsheet::Sheet", obj_name
    )

    # Add column headers
    column_headers = addSheetHeaders(column_headers, bill_of_material)

    # Get mark reinforcement dictionary
    mark_reinforcements_dict = getMarkReinforcementsDict()

    # Dictionary to store total length of rebars corresponding to its dia
    dia_total_length_dict = {}

    # Add data to spreadsheet
    if "RebarsTotalLength" in column_headers:
        first_row = 3
        current_row = 3
    else:
        first_row = 2
        current_row = 2
    diameter_list = []
    for mark_number in sorted(mark_reinforcements_dict):
        base_rebar = mark_reinforcements_dict[mark_number][0].BaseRebar

        if "Mark" in column_headers:
            bill_of_material.set(
                chr(ord("A") + column_headers["Mark"][1] - 1)
                + str(current_row),
                "'" + str(mark_number),
            )

        rebars_count = 0
        for reinforcement in mark_reinforcements_dict[mark_number]:
            rebars_count += reinforcement.Amount

        if "RebarsCount" in column_headers:
            bill_of_material.set(
                chr(ord("A") + column_headers["RebarsCount"][1] - 1)
                + str(current_row),
                "'" + str(rebars_count),
            )

        if "Diameter" in column_headers:
            bill_of_material.set(
                chr(ord("A") + column_headers["Diameter"][1] - 1)
                + str(current_row),
                str(base_rebar.Diameter),
            )

        if base_rebar.Diameter not in diameter_list:
            diameter_list.append(base_rebar.Diameter)
            diameter_list.sort()
            if "RebarsTotalLength" in column_headers:
                addDiameterHeader(
                    base_rebar.Diameter,
                    diameter_list,
                    column_headers,
                    bill_of_material,
                )
                dia_total_length_dict[
                    base_rebar.Diameter.Value
                ] = FreeCAD.Units.Quantity("0 mm")

        base_rebar_length = FreeCAD.Units.Quantity("0 mm")
        if "RebarLength" in column_headers:
            if rebar_length_type == "RealLength":
                base_rebar_length = base_rebar.Length
                bill_of_material.set(
                    chr(ord("A") + column_headers["RebarLength"][1] - 1)
                    + str(current_row),
                    str(base_rebar_length),
                )
            else:
                base_rebar_length = getRebarSharpEdgedLength(base_rebar)
                bill_of_material.set(
                    chr(ord("A") + column_headers["RebarLength"][1] - 1)
                    + str(current_row),
                    str(base_rebar_length),
                )

        rebar_total_length = FreeCAD.Units.Quantity("0 mm")
        for reinforcement in mark_reinforcements_dict[mark_number]:
            rebar_total_length += reinforcement.Amount * base_rebar_length
        dia_total_length_dict[base_rebar.Diameter.Value] += rebar_total_length

        if "RebarsTotalLength" in column_headers:
            bill_of_material.set(
                chr(
                    ord("A")
                    + column_headers["RebarsTotalLength"][1]
                    - 1
                    + diameter_list.index(base_rebar.Diameter)
                )
                + str(current_row),
                str(rebar_total_length),
            )

        current_row += 1

    # Set display units
    if "Diameter" in column_headers:
        column = chr(ord("A") + column_headers["Diameter"][1] - 1)
        bill_of_material.setDisplayUnit(
            column + str(first_row) + ":" + column + str(current_row),
            column_units["Diameter"],
        )
    if "RebarLength" in column_headers:
        column = chr(ord("A") + column_headers["RebarLength"][1] - 1)
        bill_of_material.setDisplayUnit(
            column + str(first_row) + ":" + column + str(current_row),
            column_units["RebarLength"],
        )
    if "RebarsTotalLength" in column_headers:
        start_column = chr(
            ord("A") + column_headers["RebarsTotalLength"][1] - 1
        )
        end_column = chr(ord(start_column) + len(diameter_list) - 1)
        bill_of_material.setDisplayUnit(
            start_column + str(first_row) + ":" + end_column + str(current_row),
            column_units["RebarsTotalLength"],
        )

    current_row += 3
    # Display total length, weight/m and total weight of all rebars
    if "RebarsTotalLength" in column_headers:
        if column_headers["RebarsTotalLength"][1] != 1:
            first_dia_column = chr(
                ord("A") + column_headers["RebarsTotalLength"][1] - 1
            )
            bill_of_material.mergeCells(
                "A"
                + str(current_row)
                + ":"
                + chr(ord(first_dia_column) - 1)
                + str(current_row)
            )
            bill_of_material.mergeCells(
                "A"
                + str(current_row + 1)
                + ":"
                + chr(ord(first_dia_column) - 1)
                + str(current_row + 1)
            )
            bill_of_material.mergeCells(
                "A"
                + str(current_row + 2)
                + ":"
                + chr(ord(first_dia_column) - 1)
                + str(current_row + 2)
            )
            bill_of_material.set(
                "A" + str(current_row),
                "Total length in "
                + column_units["RebarsTotalLength"]
                + "/Diameter",
            )
            bill_of_material.set(
                "A" + str(current_row + 1),
                "Weight in Kg/" + column_units["RebarsTotalLength"],
            )
            bill_of_material.set(
                "A" + str(current_row + 2), "Total Weight in Kg/Diameter"
            )
            for i, dia in enumerate(diameter_list):
                bill_of_material.set(
                    chr(ord(first_dia_column) + i) + str(current_row),
                    str(dia_total_length_dict[dia.Value]),
                )
                bill_of_material.setDisplayUnit(
                    chr(ord(first_dia_column) + i) + str(current_row),
                    column_units["RebarsTotalLength"],
                )
                if dia.Value in dia_weight_map:
                    bill_of_material.set(
                        chr(ord(first_dia_column) + i) + str(current_row + 1),
                        str(dia_weight_map[dia.Value]),
                    )
                    bill_of_material.set(
                        chr(ord(first_dia_column) + i) + str(current_row + 2),
                        str(
                            dia_weight_map[dia.Value]
                            * dia_total_length_dict[dia.Value]
                        ),
                    )
                    bill_of_material.setDisplayUnit(
                        chr(ord(first_dia_column) + i) + str(current_row + 1),
                        "kg/" + column_units["RebarsTotalLength"],
                    )
                    bill_of_material.setDisplayUnit(
                        chr(ord(first_dia_column) + i) + str(current_row + 2),
                        "kg",
                    )
        else:
            for i, dia in enumerate(diameter_list):
                bill_of_material.set(
                    chr(ord("A") + i) + str(current_row),
                    str(dia_total_length_dict[dia.Value]),
                )
                bill_of_material.setDisplayUnit(
                    chr(ord("A") + i) + str(current_row),
                    column_units["RebarsTotalLength"],
                )
                if dia.Value in dia_weight_map:
                    bill_of_material.set(
                        chr(ord("A") + i) + str(current_row + 1),
                        str(dia_weight_map[dia.Value]),
                    )
                    bill_of_material.set(
                        chr(ord("A") + i) + str(current_row + 2),
                        str(
                            dia_weight_map[dia.Value]
                            * dia_total_length_dict[dia.Value]
                        ),
                    )
                    bill_of_material.setDisplayUnit(
                        chr(ord("A") + i) + str(current_row + 1),
                        "kg/" + column_units["RebarsTotalLength"],
                    )
                    bill_of_material.setDisplayUnit(
                        chr(ord("A") + i) + str(current_row + 2), "kg"
                    )

            first_txt_column = chr(ord("A") + len(diameter_list))
            bill_of_material.mergeCells(
                first_txt_column
                + str(current_row)
                + ":"
                + chr(ord(first_txt_column) + len(column_headers) - 2)
                + str(current_row)
            )
            bill_of_material.mergeCells(
                first_txt_column
                + str(current_row + 1)
                + ":"
                + chr(ord(first_txt_column) + len(column_headers) - 2)
                + str(current_row + 1)
            )
            bill_of_material.mergeCells(
                first_txt_column
                + str(current_row + 2)
                + ":"
                + chr(ord(first_txt_column) + len(column_headers) - 2)
                + str(current_row + 2)
            )
            bill_of_material.set(
                first_txt_column + str(current_row),
                "Total length in "
                + column_units["RebarsTotalLength"]
                + "/Diameter",
            )
            bill_of_material.set(
                first_txt_column + str(current_row + 1),
                "Weight in Kg/" + column_units["RebarsTotalLength"],
            )
            bill_of_material.set(
                first_txt_column + str(current_row + 2),
                "Total Weight in Kg/Diameter",
            )

    FreeCAD.ActiveDocument.recompute()
    print("WIP")
