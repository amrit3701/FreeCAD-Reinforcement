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


def getMembersRebarsDict(structures_list=None):
    # Get Part::FeaturePython objects list
    objects_list = FreeCAD.ActiveDocument.findObjects("Part::FeaturePython")

    # Create dictionary with members as key with corresponding rebars list as
    # value
    members_rebars_dict = {}
    if not structures_list:
        for item in objects_list:
            if hasattr(item, "IfcType"):
                if item.IfcType == "Reinforcing Bar":
                    base_obj = item.Base
                    if not base_obj:
                        member = "Unknown"
                    else:
                        member = base_obj.Support[0][0].Label
                    if member not in members_rebars_dict:
                        members_rebars_dict[member] = []
                    members_rebars_dict[member].append(item)
    else:
        for item in objects_list:
            if hasattr(item, "IfcType"):
                if item.IfcType == "Reinforcing Bar":
                    base_obj = item.Base
                    if base_obj:
                        if base_obj.Support[0][0] in structures_list:
                            member = base_obj.Support[0][0].Label
                            if member not in members_rebars_dict:
                                members_rebars_dict[member] = []
                            members_rebars_dict[member].append(item)

    return members_rebars_dict


def addSheetHeaders(column_headers, spreadsheet):
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


def getRebarRealLength(rebar):
    base = rebar.Base
    # When rebar is drived from DWire or from Sketch
    if hasattr(base, "Length") or base.isDerivedFrom("Sketcher::SketchObject"):
        wire = base.Shape.Wires[0]
        radius = rebar.Rounding * rebar.Diameter.Value
        import DraftGeomUtils

        fillet_wire = DraftGeomUtils.filletWire(wire, radius)
        real_rebar_length = fillet_wire.Length
        return FreeCAD.Units.Quantity(str(real_rebar_length) + "mm")
    else:
        print("Cannot calculate rebar real length from its base object")
        return FreeCAD.Units.Quantity("0 mm")


def makeBillOfMaterial(
    column_headers=COLUMN_HEADERS,
    dia_weight_map=DIA_WEIGHT_MAP,
    rebar_length_type=REBAR_LENGTH_TYPE,
    structures_list=None,
    obj_name="RebarBillOfMaterial",
):
    # Create new spreadsheet object
    bill_of_material = FreeCAD.ActiveDocument.addObject(
        "Spreadsheet::Sheet", obj_name
    )

    # Add column headers
    column_headers = addSheetHeaders(column_headers, bill_of_material)

    # Get members rebars dictionary
    members_rebars_dict = getMembersRebarsDict(structures_list)

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
    for member in members_rebars_dict:
        if "Member" in column_headers:
            bill_of_material.set(
                chr(ord("A") + column_headers["Member"][1] - 1)
                + str(current_row),
                member,
            )
        for rebars in members_rebars_dict[member]:
            if rebars.Diameter not in diameter_list:
                diameter_list.append(rebars.Diameter)
                diameter_list.sort()
                if "RebarsTotalLength" in column_headers:
                    addDiameterHeader(
                        rebars.Diameter,
                        diameter_list,
                        column_headers,
                        bill_of_material,
                    )
                    dia_total_length_dict[
                        rebars.Diameter.Value
                    ] = FreeCAD.Units.Quantity("0 mm")

            for column_header, column_header_tuple in column_headers.items():
                column = chr(
                    ord("A") + column_header_tuple[1] - 2 + len(diameter_list)
                )
                if column_header == "Mark":
                    pass
                elif column_header == "RebarsCount":
                    bill_of_material.set(
                        column + str(current_row), str(rebars.Amount),
                    )
                elif column_header == "Diameter":
                    bill_of_material.set(
                        column + str(current_row), str(rebars.Diameter),
                    )
                elif column_header == "RebarLength":
                    if rebar_length_type == "RealLength":
                        bill_of_material.set(
                            column + str(current_row),
                            str(getRebarRealLength(rebars)),
                        )
                    else:
                        bill_of_material.set(
                            column + str(current_row), str(rebars.Length)
                        )
                elif column_header == "RebarsTotalLength":
                    if rebar_length_type == "RealLength":
                        bill_of_material.set(
                            chr(
                                ord("A")
                                + column_headers["RebarsTotalLength"][1]
                                - 1
                                + diameter_list.index(rebars.Diameter)
                            )
                            + str(current_row),
                            str(rebars.Amount * getRebarRealLength(rebars)),
                        )
                        dia_total_length_dict[
                            rebars.Diameter.Value
                        ] += rebars.Amount * getRebarRealLength(rebars)
                    else:
                        bill_of_material.set(
                            chr(
                                ord("A")
                                + column_headers["RebarsTotalLength"][1]
                                - 1
                                + diameter_list.index(rebars.Diameter)
                            )
                            + str(current_row),
                            str(rebars.TotalLength),
                        )
                        dia_total_length_dict[
                            rebars.Diameter.Value
                        ] += rebars.TotalLength
            current_row += 1
        current_row += 1

    # Set display units
    if "RebarLength" in column_headers:
        column = chr(ord("A") + column_headers["RebarLength"][1] - 1)
        bill_of_material.setDisplayUnit(
            column + str(first_row) + ":" + column + str(current_row), "m"
        )
    if "RebarsTotalLength" in column_headers:
        start_column = chr(
            ord("A") + column_headers["RebarsTotalLength"][1] - 1
        )
        end_column = chr(ord(start_column) + len(diameter_list) - 1)
        bill_of_material.setDisplayUnit(
            start_column + str(first_row) + ":" + end_column + str(current_row),
            "m",
        )

    current_row += 4
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
                "A" + str(current_row), "Total length in m/Diameter"
            )
            bill_of_material.set("A" + str(current_row + 1), "Weight in Kg/m")
            bill_of_material.set(
                "A" + str(current_row + 2), "Total Weight in Kg/Diameter"
            )
            for i, dia in enumerate(diameter_list):
                bill_of_material.set(
                    chr(ord(first_dia_column) + i) + str(current_row),
                    str(dia_total_length_dict[dia.Value]),
                )
                bill_of_material.setDisplayUnit(
                    chr(ord(first_dia_column) + i) + str(current_row), "m"
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
                        "kg/m",
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
                    chr(ord("A") + i) + str(current_row), "m"
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
                        chr(ord("A") + i) + str(current_row + 1), "kg/m"
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
                "Total length in m/Diameter",
            )
            bill_of_material.set(
                first_txt_column + str(current_row + 1), "Weight in Kg/m",
            )
            bill_of_material.set(
                first_txt_column + str(current_row + 2),
                "Total Weight in Kg/Diameter",
            )

    FreeCAD.ActiveDocument.recompute()
    print("WIP")
