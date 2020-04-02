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


def addSheetHeaders(column_headers, spreadsheet):
    # Format cells
    spreadsheet.mergeCells("A1:A2")
    spreadsheet.mergeCells("B1:B2")
    spreadsheet.mergeCells("C1:C2")
    spreadsheet.mergeCells("D1:D2")
    spreadsheet.mergeCells("E1:E2")

    # Add column headers
    spreadsheet.set("A1", column_headers[0])
    spreadsheet.set("B1", column_headers[1])
    spreadsheet.set("C1", column_headers[2])
    spreadsheet.set("D1", column_headers[3])
    spreadsheet.set("E1", column_headers[4])


def addDiameterHeader(dia, diameter_list, main_column_header, spreadsheet):
    # Append new dia to diameter list
    diameter_list.append(dia)
    diameter_list.sort()

    # Create new column to insert dia
    loc = diameter_list.index(dia)
    new_column = chr(ord("F") + loc)
    spreadsheet.insertColumns(new_column, 1)

    # Format cells
    spreadsheet.splitCell("F1")
    last_dia_column = chr(ord("F") + len(diameter_list) - 1)
    spreadsheet.mergeCells("F1:" + last_dia_column + "1")
    spreadsheet.setAlignment("F1", "center|vcenter")
    spreadsheet.setAlignment("F2:" + last_dia_column + "2", "center|vcenter")

    # Insert dia column header
    spreadsheet.set("F1", main_column_header)
    spreadsheet.set(new_column + "2", "#" + str(dia.Value))

    # Return new sorted diameter list
    return diameter_list


def makeBillOfMaterial(
    column_headers=COLUMN_HEADERS, obj_name="RebarBillOfMaterial",
):
    # Create new spreadsheet object
    bill_of_material = FreeCAD.ActiveDocument.addObject(
        "Spreadsheet::Sheet", obj_name
    )

    # Add column headers
    addSheetHeaders(column_headers, bill_of_material)

    # Get Part::FeaturePython objects list
    objects_list = FreeCAD.ActiveDocument.findObjects("Part::FeaturePython")

    # Create rebars list and dictionary with members as key with corresponding
    # rebars list as value
    rebars_list = []
    members_rebars_dict = {}
    for item in objects_list:
        if hasattr(item, "IfcType"):
            if item.IfcType == "Reinforcing Bar":
                rebars_list.append(item)
                base_obj = item.Base
                if not base_obj:
                    member = "Unknown"
                else:
                    member = base_obj.Support[0][0].Label
                if member not in members_rebars_dict:
                    members_rebars_dict[member] = []
                else:
                    members_rebars_dict[member].append(item)

    # Dictionary to store total length of rebars corresponding to its dia
    dia_total_length_dict = {}

    # Add data to spreadsheet
    row = 3
    diameter_list = []
    for member in members_rebars_dict:
        # Add member label to spreadsheet
        bill_of_material.set("A" + str(row), member)
        # Add rebars data
        for rebars in members_rebars_dict[member]:
            bill_of_material.set("C" + str(row), str(rebars.Amount))
            bill_of_material.set("D" + str(row), str(rebars.Diameter))
            bill_of_material.set("E" + str(row), str(rebars.Length))

            if rebars.Diameter not in diameter_list:
                # Add new column corresponding to rebar diameter in bill of
                # material spreadsheet, if not already exists in spreadsheet
                diameter_list = addDiameterHeader(
                    rebars.Diameter,
                    diameter_list,
                    column_headers[5],
                    bill_of_material,
                )
                dia_total_length_dict[
                    rebars.Diameter.Value
                ] = FreeCAD.Units.Quantity("0 mm")

            bill_of_material.set(
                chr(ord("F") + diameter_list.index(rebars.Diameter)) + str(row),
                str(rebars.TotalLength),
            )
            dia_total_length_dict[rebars.Diameter.Value] += rebars.TotalLength
            row += 1
        row += 1

    # Set display units
    bill_of_material.setDisplayUnit("E3:E" + str(row), "m")
    bill_of_material.setDisplayUnit(
        "F3:" + chr(ord("F") + len(diameter_list) - 1) + str(row), "m"
    )

    # Display total length of rebars
    row += 4
    bill_of_material.mergeCells("A" + str(row) + ":E" + str(row))
    bill_of_material.set("A" + str(row), "Total length in m/Diameter")
    for i, dia in enumerate(diameter_list):
        bill_of_material.set(
            chr(ord("F") + i) + str(row), str(dia_total_length_dict[dia.Value])
        )

    # Set display units for total length of rebars
    bill_of_material.setDisplayUnit(
        "F"
        + str(row)
        + ":"
        + chr(ord("F") + len(diameter_list) - 1)
        + str(row),
        "m",
    )
    row += 1

    # Display weight (kg/m) and total weight of rebars
    bill_of_material.mergeCells("A" + str(row) + ":E" + str(row))
    bill_of_material.mergeCells("A" + str(row + 1) + ":E" + str(row + 1))
    bill_of_material.set("A" + str(row), "Weight in Kg/m")
    bill_of_material.set("A" + str(row + 1), "Total Weight in Kg/Diameter")
    for i, dia in enumerate(diameter_list):
        if dia.Value in dia_weight_map:
            bill_of_material.set(
                chr(ord("F") + i) + str(row), str(dia_weight_map[dia.Value])
            )
            bill_of_material.set(
                chr(ord("F") + i) + str(row + 1),
                str(
                    dia_weight_map[dia.Value] * dia_total_length_dict[dia.Value]
                ),
            )

    # Set display units for weight and total weight of rebars
    bill_of_material.setDisplayUnit(
        "F"
        + str(row)
        + ":"
        + chr(ord("F") + len(diameter_list) - 1)
        + str(row),
        "kg/m",
    )

    FreeCAD.ActiveDocument.recompute()
    print("WIP")
