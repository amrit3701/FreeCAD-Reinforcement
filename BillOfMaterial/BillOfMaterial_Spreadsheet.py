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

__title__ = "Bill Of Material Spreadsheet"
__author__ = "Suraj"
__url__ = "https://www.freecadweb.org"

from typing import Optional, Dict, Tuple, Literal, List, Union

import FreeCAD

from .BOMfunc import (
    getMarkReinforcementsDict,
    getRebarSharpEdgedLength,
    getReinforcementRebarObjects,
    getUniqueDiameterList,
    fixColumnUnits,
    getBaseRebar,
    getHostReinforcementsDict,
)
from .BOMPreferences import BOMPreferences


def addSheetHeaders(
    column_headers: Dict[str, Tuple[str, int]],
    diameter_list: List[FreeCAD.Units.Quantity],
    spreadsheet,
) -> None:
    """addSheetHeaders(ColumnHeaders, Spreadsheet):
    Add headers to columns in spreadsheet object.
    """
    # Format cells and insert headers if column "RebarsTotalLength" is to be
    # shown in BOM, only insert headers otherwise
    if "RebarsTotalLength" in column_headers:
        for column_header in column_headers:
            column = chr(ord("A") + column_headers[column_header][1] - 1)
            if column_header != "RebarsTotalLength":
                spreadsheet.mergeCells(column + "1:" + column + "2")
                spreadsheet.set(column + "1", column_headers[column_header][0])
            elif column_header == "RebarsTotalLength":
                last_dia_column = chr(ord(column) + len(diameter_list) - 1)
                spreadsheet.mergeCells(column + "1:" + last_dia_column + "1")
                spreadsheet.setAlignment(
                    column + "1:" + last_dia_column + "1", "center|vcenter"
                )
                spreadsheet.setAlignment(
                    column + "2:" + last_dia_column + "2", "center|vcenter"
                )
                spreadsheet.set(column + "1", column_headers[column_header][0])
                for dia_index, dia in enumerate(diameter_list):
                    spreadsheet.set(
                        chr(ord(column) + dia_index) + "2",
                        "#" + str(dia.Value).rstrip("0").rstrip("."),
                    )
    else:
        for column_header in column_headers:
            column = chr(ord("A") + column_headers[column_header][1] - 1)
            spreadsheet.set(column + "1", column_headers[column_header][0])


def getHeaderColumn(column_headers, diameter_list, column_header):
    """getHeaderColumn(ColumnHeadersConfig, DiameterList, ColumnHeader):
    column_headers is a dictionary with keys: "Mark", "RebarsCount", "Diameter",
    "RebarLength", "RebarsTotalLength" and values are tuple of column_header and
    its sequence number.
    e.g. {
            "Host": ("Member", 1),
            "Mark": ("Mark", 2),
            "RebarsCount": ("No. of Rebars", 3),
            "Diameter": ("Diameter in mm", 4),
            "RebarLength": ("Length in m/piece", 5),
            "RebarsTotalLength": ("Total Length in m", 6),
        }

    column_header is the key from dictionary column_headers for which we need to
    find its column in spreadsheet.

    Returns column corresponding to column_header.
    """
    seq = column_headers[column_header][1]
    if "RebarsTotalLength" in column_headers:
        if column_headers["RebarsTotalLength"][1] < seq:
            if len(diameter_list) == 0:
                seq += len(diameter_list)
            else:
                seq += len(diameter_list) - 1
    column = chr(ord("A") + seq - 1)
    return column


def makeBillOfMaterial(
    column_headers: Optional[Dict[str, Tuple[str, int]]] = None,
    column_units: Optional[Dict[str, str]] = None,
    dia_weight_map: Optional[Dict[float, FreeCAD.Units.Quantity]] = None,
    rebar_length_type: Optional[
        Literal["RealLength", "LengthWithSharpEdges"]
    ] = None,
    rebar_objects: Optional[List] = None,
    reinforcement_group_by: Optional[Literal["Mark", "Host"]] = None,
    obj_name: str = "RebarBillOfMaterial",
):
    """makeBillOfMaterial(ColumnHeadersConfig, ColumnUnitsDict, DiaWeightMap,
    RebarLengthType, RebarObjects, ReinforcementGroupBy, ObjectName):
    Generates the Rebars Material Bill.

    column_headers is a dictionary with keys: "Host", "Mark", "RebarsCount",
    "Diameter", "RebarLength", "RebarsTotalLength" and values are tuple of
    column_header and its sequence number.
    e.g. {
            "Host": ("Member", 1),
            "Mark": ("Mark", 2),
            "RebarsCount": ("No. of Rebars", 3),
            "Diameter": ("Diameter in mm", 4),
            "RebarLength": ("Length in m/piece", 5),
            "RebarsTotalLength": ("Total Length in m", 6),
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
    rebar_objects is the list of ArchRebar and/or rebar2 objects.

    reinforcement_group_by can be "Mark" or "Host".

    Returns Bill Of Material spreadsheet object.
    """
    reinforcement_objects = getReinforcementRebarObjects(rebar_objects)
    if not reinforcement_objects:
        FreeCAD.Console.PrintWarning(
            "No rebar object in current selection/document. "
            "Returning without BillOfMaterial Spreadsheet.\n"
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
    if not reinforcement_group_by:
        reinforcement_group_by = bom_preferences.getReinforcementGroupBy()

    # Delete hidden headers
    column_headers = {
        column_header: column_header_tuple
        for column_header, column_header_tuple in column_headers.items()
        if column_header_tuple[1] != 0
    }
    # Fix column units
    column_units = fixColumnUnits(column_units)

    # Create new spreadsheet object
    bill_of_material = FreeCAD.ActiveDocument.addObject(
        "Spreadsheet::Sheet", obj_name
    )

    # Get unique diameter list
    diameter_list = getUniqueDiameterList(reinforcement_objects)

    # Add column headers
    addSheetHeaders(column_headers, diameter_list, bill_of_material)

    # Dictionary to store total length of rebars corresponding to its dia
    dia_total_length_dict = {
        dia.Value: FreeCAD.Units.Quantity("0 mm") for dia in diameter_list
    }

    # Add data to spreadsheet
    if "RebarsTotalLength" in column_headers:
        first_row = 3
        current_row = 3
    else:
        first_row = 2
        current_row = 2

    def addHostCellData(_host_label: str) -> None:
        bill_of_material.set(
            getHeaderColumn(column_headers, diameter_list, "Host")
            + str(current_row),
            "'" + _host_label,
        )

    def addMarkCellData(rebar_mark: Union[str, float]) -> None:
        bill_of_material.set(
            getHeaderColumn(column_headers, diameter_list, "Mark")
            + str(current_row),
            "'" + str(rebar_mark),
        )

    def addRebarsCountCellData(reinforcement_objs: List) -> None:
        bill_of_material.set(
            getHeaderColumn(column_headers, diameter_list, "RebarsCount")
            + str(current_row),
            "'" + str(sum(map(lambda x: x.Amount, reinforcement_objs))),
        )

    def addDiameterCellData(rebar_diameter: FreeCAD.Units.Quantity) -> None:
        bill_of_material.set(
            getHeaderColumn(column_headers, diameter_list, "Diameter")
            + str(current_row),
            str(rebar_diameter),
        )

    def addRebarLengthCellData(rebar_length: FreeCAD.Units.Quantity) -> None:
        bill_of_material.set(
            getHeaderColumn(column_headers, diameter_list, "RebarLength")
            + str(current_row),
            str(rebar_length),
        )

    def addRebarTotalLengthCellData(
        _rebar_total_length: FreeCAD.Units.Quantity,
    ) -> None:
        bill_of_material.set(
            chr(
                ord(
                    getHeaderColumn(
                        column_headers, diameter_list, "RebarsTotalLength"
                    )
                )
                + diameter_list.index(base_rebar.Diameter)
            )
            + str(current_row),
            str(_rebar_total_length),
        )

    if reinforcement_group_by == "Mark":
        mark_reinforcements_dict = getMarkReinforcementsDict(rebar_objects)
        for mark_number in mark_reinforcements_dict:
            base_rebar = getBaseRebar(mark_reinforcements_dict[mark_number][0])

            if "Host" in column_headers:
                host_label = []
                for reinforcement in mark_reinforcements_dict[mark_number]:
                    if (
                        reinforcement.Host
                        and reinforcement.Host.Label not in host_label
                    ):
                        host_label.append(reinforcement.Host.Label)
                addHostCellData(",".join(sorted(host_label)))

            if "Mark" in column_headers:
                addMarkCellData(mark_number)

            if "RebarsCount" in column_headers:
                addRebarsCountCellData(mark_reinforcements_dict[mark_number])

            if "Diameter" in column_headers:
                addDiameterCellData(base_rebar.Diameter)

            base_rebar_length = FreeCAD.Units.Quantity("0 mm")
            if "RebarLength" in column_headers:
                if rebar_length_type == "RealLength":
                    base_rebar_length = base_rebar.Length
                else:
                    base_rebar_length = getRebarSharpEdgedLength(base_rebar)
                addRebarLengthCellData(base_rebar_length)

            if "RebarsTotalLength" in column_headers:
                rebar_total_length = FreeCAD.Units.Quantity("0 mm")
                for reinforcement in mark_reinforcements_dict[mark_number]:
                    rebar_total_length += (
                        reinforcement.Amount * base_rebar_length
                    )
                dia_total_length_dict[
                    base_rebar.Diameter.Value
                ] += rebar_total_length

                addRebarTotalLengthCellData(rebar_total_length)

            current_row += 1
    else:
        host_reinforcements_dict = getHostReinforcementsDict(rebar_objects)
        for rebar_host, reinforcement_list in host_reinforcements_dict.items():
            mark_reinforcements_dict = getMarkReinforcementsDict(
                reinforcement_list
            )
            add_host_in_column = True
            for mark_number in mark_reinforcements_dict:
                base_rebar = getBaseRebar(
                    mark_reinforcements_dict[mark_number][0]
                )

                if "Host" in column_headers:
                    if add_host_in_column:
                        add_host_in_column = False
                        host_label = (
                            rebar_host.Label
                            if hasattr(rebar_host, "Label")
                            else str(rebar_host)
                        )
                    else:
                        host_label = ""
                    addHostCellData(host_label)

                if "Mark" in column_headers:
                    addMarkCellData(mark_number)

                if "RebarsCount" in column_headers:
                    addRebarsCountCellData(
                        mark_reinforcements_dict[mark_number]
                    )

                if "Diameter" in column_headers:
                    addDiameterCellData(base_rebar.Diameter)

                base_rebar_length = FreeCAD.Units.Quantity("0 mm")
                if "RebarLength" in column_headers:
                    if rebar_length_type == "RealLength":
                        base_rebar_length = base_rebar.Length
                    else:
                        base_rebar_length = getRebarSharpEdgedLength(base_rebar)
                    addRebarLengthCellData(base_rebar_length)

                if "RebarsTotalLength" in column_headers:
                    rebar_total_length = FreeCAD.Units.Quantity("0 mm")
                    for reinforcement in mark_reinforcements_dict[mark_number]:
                        rebar_total_length += (
                            reinforcement.Amount * base_rebar_length
                        )
                    dia_total_length_dict[
                        base_rebar.Diameter.Value
                    ] += rebar_total_length

                    addRebarTotalLengthCellData(rebar_total_length)

                current_row += 1

    # Set display units
    if "Diameter" in column_headers:
        column = getHeaderColumn(column_headers, diameter_list, "Diameter")
        bill_of_material.setDisplayUnit(
            column + str(first_row) + ":" + column + str(current_row),
            column_units["Diameter"],
        )
    if "RebarLength" in column_headers:
        column = getHeaderColumn(column_headers, diameter_list, "RebarLength")
        bill_of_material.setDisplayUnit(
            column + str(first_row) + ":" + column + str(current_row),
            column_units["RebarLength"],
        )
    if "RebarsTotalLength" in column_headers:
        start_column = getHeaderColumn(
            column_headers, diameter_list, "RebarsTotalLength"
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
            first_dia_column = getHeaderColumn(
                column_headers, diameter_list, "RebarsTotalLength"
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
    return bill_of_material
