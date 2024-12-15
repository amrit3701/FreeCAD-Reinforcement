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

__title__ = "Bill Of Material Preferences"
__author__ = "Suraj"
__url__ = "https://www.freecadweb.org"


from collections import OrderedDict
from pathlib import Path
from typing import Dict, OrderedDict as OrderedDictType, Union

import FreeCAD

from .config import (
    COLUMN_UNITS,
    COLUMN_HEADERS,
    DIA_WEIGHT_MAP,
    REBAR_LENGTH_TYPE,
    REINFORCEMENT_GROUP_BY,
    COLUMN_WIDTH,
    ROW_HEIGHT,
    FONT_FAMILY,
    FONT_FILENAME,
    FONT_SIZE,
    BOM_SVG_LEFT_OFFSET,
    BOM_SVG_TOP_OFFSET,
    BOM_SVG_MIN_RIGHT_OFFSET,
    BOM_SVG_MIN_BOTTOM_OFFSET,
    BOM_TABLE_SVG_MAX_WIDTH,
    BOM_TABLE_SVG_MAX_HEIGHT,
    TEMPLATE_FILE,
)


# TODO: Use(Uncomment) typing.Literal for minimum python3.8


class BOMPreferences:
    def __init__(
        self,
        # conf_column_units: Dict[
        #     Literal["Diameter", "RebarLength", "RebarsTotalLength"], str
        # ] = COLUMN_UNITS,
        conf_column_units: Dict[str, str] = COLUMN_UNITS,
        # conf_column_headers: OrderedDictType[
        #     Literal[
        #         "Host",
        #         "Mark",
        #         "RebarsCount",
        #         "Diameter",
        #         "RebarLength",
        #         "RebarsTotalLength",
        #     ],
        #     str,
        # ] = COLUMN_HEADERS,
        conf_column_headers: OrderedDictType[str, str] = COLUMN_HEADERS,
        conf_dia_weight_map: Dict[
            float, FreeCAD.Units.Quantity
        ] = DIA_WEIGHT_MAP,
        # conf_rebar_length_type: Literal[
        #     "RealLength", "LengthWithSharpEdges"
        # ] = REBAR_LENGTH_TYPE,
        conf_rebar_length_type: str = REBAR_LENGTH_TYPE,
        # conf_reinforcement_group_by: Literal[
        #     "Mark", "Host"
        # ] = REINFORCEMENT_GROUP_BY,
        conf_reinforcement_group_by: str = REINFORCEMENT_GROUP_BY,
        conf_column_width: float = COLUMN_WIDTH,
        conf_row_height: float = ROW_HEIGHT,
        conf_font_family: str = FONT_FAMILY,
        conf_font_filename: str = FONT_FILENAME,
        conf_font_size: float = FONT_SIZE,
        conf_bom_svg_left_offset: float = BOM_SVG_LEFT_OFFSET,
        conf_bom_svg_top_offset: float = BOM_SVG_TOP_OFFSET,
        conf_bom_svg_min_right_offset: float = BOM_SVG_MIN_RIGHT_OFFSET,
        conf_bom_svg_min_bottom_offset: float = BOM_SVG_MIN_BOTTOM_OFFSET,
        conf_bom_table_svg_max_width: float = BOM_TABLE_SVG_MAX_WIDTH,
        conf_bom_table_svg_max_height: float = BOM_TABLE_SVG_MAX_HEIGHT,
        conf_template_file: Union[str, Path] = TEMPLATE_FILE,
        overwrite: bool = False,
    ):
        self.bom_pref = FreeCAD.ParamGet(
            "User parameter:BaseApp/Preferences/Mod/RebarTools/BOM"
        )
        self.conf_column_units = conf_column_units
        self.conf_column_headers = conf_column_headers
        self.conf_dia_weight_map = conf_dia_weight_map
        self.conf_rebar_length_type = conf_rebar_length_type
        self.available_rebar_length_types = [
            "RealLength",
            "LengthWithSharpEdges",
        ]
        self.conf_reinforcement_group_by = conf_reinforcement_group_by
        self.available_reinforcement_group_by = ["Mark", "Host"]
        self.conf_column_width = conf_column_width
        self.conf_row_height = conf_row_height
        self.conf_font_family = conf_font_family
        self.conf_font_filename = conf_font_filename
        self.conf_font_size = conf_font_size
        self.conf_bom_svg_left_offset = conf_bom_svg_left_offset
        self.conf_bom_svg_top_offset = conf_bom_svg_top_offset
        self.conf_template_file = conf_template_file
        self.conf_bom_svg_min_right_offset = conf_bom_svg_min_right_offset
        self.conf_bom_svg_min_bottom_offset = conf_bom_svg_min_bottom_offset
        self.conf_bom_table_svg_max_width = conf_bom_table_svg_max_width
        self.conf_bom_table_svg_max_height = conf_bom_table_svg_max_height
        self.overwrite = overwrite
        self.column_units = self.bom_pref.GetGroup("ColumnUnits")
        self.column_headers = self.bom_pref.GetGroup("ColumnHeaders")
        self.dia_weight_map = self.bom_pref.GetGroup("DiaWeightMap")
        self.rebar_length_type = self.available_rebar_length_types[
            self.bom_pref.GetInt(
                "RebarLengthType",
                self.available_rebar_length_types.index(
                    self.conf_rebar_length_type
                ),
            )
        ]
        self.reinforcement_group_by = self.available_reinforcement_group_by[
            self.bom_pref.GetInt(
                "ReinforcementGroupBy",
                self.available_reinforcement_group_by.index(
                    self.conf_reinforcement_group_by
                ),
            )
        ]
        self.svg_pref = self.bom_pref.GetGroup("SVG")
        self.setColumnUnits()
        self.setColumnHeaders()
        self.setDiaWeightMap()
        self.setRebarLengthType()
        self.setReinforcementGroupBy()
        self.setSVGPref()

    def setColumnUnits(self):
        for column in self.conf_column_units:
            units = self.column_units.GetString(
                column, self.conf_column_units[column]
            )
            self.column_units.SetString(
                column,
                units if not self.overwrite else self.conf_column_units[column],
            )

    def setColumnHeaders(self):
        for i, column in enumerate(self.conf_column_headers.items(), start=1):
            header = self.column_headers.GetGroup(column[0])
            header_disp = header.GetString("display", column[1])
            header_seq = header.GetInt("sequence", i)
            header.SetString(
                "display",
                header_disp if not self.overwrite else column[1],
            )
            header.SetInt(
                "sequence",
                header_seq if not self.overwrite else i,
            )
        # Hide headers which are not present in self.conf_column_headers
        for column in self.column_headers.GetGroups():
            if column not in self.conf_column_headers:
                self.column_headers.GetGroup(column).SetInt("sequence", 0)

    def setDiaWeightMap(self):
        for dia in self.conf_dia_weight_map:
            weight = self.dia_weight_map.GetFloat(
                str(dia), self.conf_dia_weight_map[dia].Value
            )
            self.dia_weight_map.SetFloat(
                str(dia),
                weight
                if not self.overwrite
                else self.conf_dia_weight_map[dia].Value,
            )

    def setRebarLengthType(self):
        self.bom_pref.SetInt(
            "RebarLengthType",
            self.available_rebar_length_types.index(self.rebar_length_type)
            if not self.overwrite
            else self.available_rebar_length_types.index(
                self.conf_rebar_length_type
            ),
        )

    def setReinforcementGroupBy(self):
        self.bom_pref.SetInt(
            "ReinforcementGroupBy",
            self.available_reinforcement_group_by.index(
                self.reinforcement_group_by
            )
            if not self.overwrite
            else self.available_reinforcement_group_by.index(
                self.conf_reinforcement_group_by
            ),
        )

    def setSVGPref(self):
        column_width = self.svg_pref.GetFloat(
            "ColumnWidth", self.conf_column_width
        )
        self.svg_pref.SetFloat(
            "ColumnWidth",
            column_width if not self.overwrite else self.conf_column_width,
        )
        row_height = self.svg_pref.GetFloat("RowHeight", self.conf_row_height)
        self.svg_pref.SetFloat(
            "RowHeight",
            row_height if not self.overwrite else self.conf_row_height,
        )
        font_family = self.svg_pref.GetString(
            "FontFamily", self.conf_font_family
        )
        self.svg_pref.SetString(
            "FontFamily",
            font_family if not self.overwrite else self.conf_font_family,
        )
        font_filename = self.svg_pref.GetString(
            "FontFilename", str(self.conf_font_filename)
        )
        self.svg_pref.SetString(
            "FontFilename",
            str(font_filename)
            if not self.overwrite
            else str(self.conf_font_filename),
        )
        font_size = self.svg_pref.GetFloat("FontSize", self.conf_font_size)
        self.svg_pref.SetFloat(
            "FontSize", font_size if not self.overwrite else self.conf_font_size
        )
        bom_svg_left_offset = self.svg_pref.GetFloat(
            "LeftOffset", self.conf_bom_svg_left_offset
        )
        self.svg_pref.SetFloat(
            "LeftOffset",
            bom_svg_left_offset
            if not self.overwrite
            else self.conf_bom_svg_left_offset,
        )
        bom_svg_top_offset = self.svg_pref.GetFloat(
            "TopOffset", self.conf_bom_svg_top_offset
        )
        self.svg_pref.SetFloat(
            "TopOffset",
            bom_svg_top_offset
            if not self.overwrite
            else self.conf_bom_svg_top_offset,
        )
        min_right_offset = self.svg_pref.GetFloat(
            "MinRightOffset", self.conf_bom_svg_min_right_offset
        )
        self.svg_pref.SetFloat(
            "MinRightOffset",
            min_right_offset
            if not self.overwrite
            else self.conf_bom_svg_min_right_offset,
        )
        min_bottom_offset = self.svg_pref.GetFloat(
            "MinBottomOffset", self.conf_bom_svg_min_bottom_offset
        )
        self.svg_pref.SetFloat(
            "MinBottomOffset",
            min_bottom_offset
            if not self.overwrite
            else self.conf_bom_svg_min_bottom_offset,
        )
        max_width = self.svg_pref.GetFloat(
            "MaxWidth", self.conf_bom_table_svg_max_width
        )
        self.svg_pref.SetFloat(
            "MaxWidth",
            max_width
            if not self.overwrite
            else self.conf_bom_table_svg_max_width,
        )
        max_height = self.svg_pref.GetFloat(
            "MaxHeight", self.conf_bom_table_svg_max_height
        )
        self.svg_pref.SetFloat(
            "MaxHeight",
            max_height
            if not self.overwrite
            else self.conf_bom_table_svg_max_height,
        )
        template_file = self.svg_pref.GetString(
            "TemplateFile", str(self.conf_template_file)
        )
        self.svg_pref.SetString(
            "TemplateFile",
            str(template_file)
            if not self.overwrite
            else str(self.conf_template_file),
        )

    def getColumnUnits(
        self,
        # ) -> Dict[Literal["Diameter", "RebarLength", "RebarsTotalLength"], str]:
    ) -> Dict[str, str]:
        column_units = {}
        for column in self.column_units.GetStrings():
            units = self.column_units.GetString(column)
            column_units[column] = units
        return column_units

    def getColumnHeaders(
        self,
        # ) -> OrderedDictType[
        #     Literal[
        #         "Host",
        #         "Mark",
        #         "RebarsCount",
        #         "Diameter",
        #         "RebarLength",
        #         "RebarsTotalLength",
        #     ],
        #     str,
        # ]:
    ) -> OrderedDictType[str, str]:
        columns = []
        for column in self.column_headers.GetGroups():
            header = self.column_headers.GetGroup(column)
            header_disp = header.GetString("display")
            header_seq = header.GetInt("sequence")
            if header_seq != 0:
                columns.append((column, header_disp, header_seq))
        column_headers = OrderedDict()
        for column in sorted(columns, key=lambda x: x[2]):
            column_headers[column[0]] = column[1]
        return column_headers

    def getDiaWeightMap(self) -> Dict[float, FreeCAD.Units.Quantity]:
        dia_weight_map = {}
        for dia in self.dia_weight_map.GetFloats():
            weight = self.dia_weight_map.GetFloat(dia)
            weight = FreeCAD.Units.Quantity(str(weight * 10**3) + "kg/m")
            dia_weight_map[int(dia)] = weight
        return dia_weight_map

    def getRebarLengthType(
        self,
        # ) -> Literal["RealLength", "LengthWithSharpEdges"]:
    ) -> str:
        rebar_length_type = self.available_rebar_length_types[
            self.bom_pref.GetInt(
                "RebarLengthType",
                self.available_rebar_length_types.index(
                    self.conf_rebar_length_type
                ),
            )
        ]
        return rebar_length_type

    # def getReinforcementGroupBy(self) -> Literal["Mark", "Host"]:
    def getReinforcementGroupBy(self) -> str:
        reinforcement_group_by = self.available_reinforcement_group_by[
            self.bom_pref.GetInt(
                "ReinforcementGroupBy",
                self.available_reinforcement_group_by.index(
                    self.conf_reinforcement_group_by
                ),
            )
        ]
        return reinforcement_group_by

    def getSVGPrefGroup(self):
        return self.svg_pref
