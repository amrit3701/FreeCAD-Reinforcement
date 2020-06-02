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


import FreeCAD

from .config import (
    COLUMN_UNITS,
    COLUMN_HEADERS,
    DIA_WEIGHT_MAP,
    REBAR_LENGTH_TYPE,
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


class BOMPreferences:
    def __init__(
        self,
        conf_column_units=COLUMN_UNITS,
        conf_column_headers=COLUMN_HEADERS,
        conf_dia_weight_map=DIA_WEIGHT_MAP,
        conf_rebar_length_type=REBAR_LENGTH_TYPE,
        conf_column_width=COLUMN_WIDTH,
        conf_row_height=ROW_HEIGHT,
        conf_font_family=FONT_FAMILY,
        conf_font_filename=FONT_FILENAME,
        conf_font_size=FONT_SIZE,
        conf_bom_svg_left_offset=BOM_SVG_LEFT_OFFSET,
        conf_bom_svg_top_offset=BOM_SVG_TOP_OFFSET,
        conf_bom_svg_min_right_offset=BOM_SVG_MIN_RIGHT_OFFSET,
        conf_bom_svg_min_bottom_offset=BOM_SVG_MIN_BOTTOM_OFFSET,
        conf_bom_table_svg_max_width=BOM_TABLE_SVG_MAX_WIDTH,
        conf_bom_table_svg_max_height=BOM_TABLE_SVG_MAX_HEIGHT,
        conf_template_file=TEMPLATE_FILE,
        overwrite=False,
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
        self.setColumnUnits()
        self.setColumnHeaders()
        self.setDiaWeightMap()
        self.setRebarLengthType()
        self.setSVGPref()

    def setColumnUnits(self):
        self.column_units = self.bom_pref.GetGroup("ColumnUnits")
        for column in self.conf_column_units:
            units = self.column_units.GetString(
                column, self.conf_column_units[column]
            )
            self.column_units.SetString(
                column,
                units if not self.overwrite else self.conf_column_units[column],
            )

    def setColumnHeaders(self):
        self.column_headers = self.bom_pref.GetGroup("ColumnHeaders")
        for column in self.conf_column_headers:
            header = self.column_headers.GetGroup(column)
            header_disp = header.GetString(
                "display", self.conf_column_headers[column][0]
            )
            header_seq = header.GetInt(
                "sequence", self.conf_column_headers[column][1]
            )
            header.SetString(
                "display",
                header_disp
                if not self.overwrite
                else self.conf_column_headers[column][0],
            )
            header.SetInt(
                "sequence",
                header_seq
                if not self.overwrite
                else self.conf_column_headers[column][1],
            )

    def setDiaWeightMap(self):
        self.dia_weight_map = self.bom_pref.GetGroup("DiaWeightMap")
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
        self.rebar_length_type = self.available_rebar_length_types[
            self.bom_pref.GetInt(
                "RebarLengthType",
                self.available_rebar_length_types.index(
                    self.conf_rebar_length_type
                ),
            )
        ]
        self.bom_pref.SetInt(
            "RebarLengthType",
            self.available_rebar_length_types.index(self.rebar_length_type)
            if not self.overwrite
            else self.available_rebar_length_types.index(
                self.conf_rebar_length_type
            ),
        )

    def setSVGPref(self):
        self.svg_pref = self.bom_pref.GetGroup("SVG")
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

    def getColumnUnits(self):
        column_units = {}
        for column in self.column_units.GetStrings():
            units = self.column_units.GetString(column)
            column_units[column] = units
        return column_units

    def getColumnHeaders(self):
        column_headers = {}
        for column in self.column_headers.GetGroups():
            header = self.column_headers.GetGroup(column)
            header_disp = header.GetString("display")
            header_seq = header.GetInt("sequence")
            column_headers[column] = (header_disp, header_seq)
        return column_headers

    def getDiaWeightMap(self):
        dia_weight_map = {}
        for dia in self.dia_weight_map.GetFloats():
            weight = self.dia_weight_map.GetFloat(dia)
            weight = FreeCAD.Units.Quantity(str(weight * 10 ** 3) + "kg/m")
            dia_weight_map[int(dia)] = weight
        return dia_weight_map

    def getRebarLengthType(self):
        return self.rebar_length_type

    def getSVGPrefGroup(self):
        return self.svg_pref
