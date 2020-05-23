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
    TEMPLATE_FILE,
    BOM_SVG_MIN_RIGHT_OFFSET,
    BOM_SVG_MIN_BOTTOM_OFFSET,
    BOM_TABLE_SVG_MAX_WIDTH,
    BOM_TABLE_SVG_MAX_HEIGHT,
)


class BOMPreferences:
    def __init__(self):
        self.bom_pref = FreeCAD.ParamGet(
            "User parameter:BaseApp/Preferences/Mod/RebarTools/BOM"
        )
        self.setColumnUnits()
        self.setColumnHeaders()
        self.setDiaWeightMap()
        self.setRebarLengthType()
        self.setSVGPref()

    def setColumnUnits(self):
        self.column_units = self.bom_pref.GetGroup("ColumnUnits")
        for column in COLUMN_UNITS:
            units = self.column_units.GetString(column, COLUMN_UNITS[column])
            self.column_units.SetString(column, units)

    def setColumnHeaders(self):
        self.column_headers = self.bom_pref.GetGroup("ColumnHeaders")
        for column in COLUMN_HEADERS:
            header = self.column_headers.GetGroup(column)
            header_disp = header.GetString("display", COLUMN_HEADERS[column][0])
            header_seq = header.GetInt("sequence", COLUMN_HEADERS[column][1])
            header.SetString("display", header_disp)
            header.SetInt("sequence", header_seq)

    def setDiaWeightMap(self):
        self.dia_weight_map = self.bom_pref.GetGroup("DiaWeightMap")
        for dia in DIA_WEIGHT_MAP:
            weight = self.dia_weight_map.GetFloat(
                str(dia), DIA_WEIGHT_MAP[dia].Value
            )
            self.dia_weight_map.SetFloat(str(dia), weight)

    def setRebarLengthType(self):
        self.rebar_length_type = self.bom_pref.GetString(
            "RebarLengthType", REBAR_LENGTH_TYPE
        )
        self.bom_pref.SetString("RebarLengthType", self.rebar_length_type)

    def setSVGPref(self):
        self.svg_pref = self.bom_pref.GetGroup("SVG")
        column_width = self.svg_pref.GetFloat("ColumnWidth", COLUMN_WIDTH)
        self.svg_pref.SetFloat("ColumnWidth", column_width)
        row_height = self.svg_pref.GetFloat("RowHeight", ROW_HEIGHT)
        self.svg_pref.SetFloat("RowHeight", row_height)
        font_family = self.svg_pref.GetString("FontFamily", FONT_FAMILY)
        self.svg_pref.SetString("FontFamily", font_family)
        font_filename = self.svg_pref.GetString(
            "FontFilename", str(FONT_FILENAME)
        )
        self.svg_pref.SetString("FontFilename", str(font_filename))
        font_size = self.svg_pref.GetFloat("FontSize", FONT_SIZE)
        self.svg_pref.SetFloat("FontSize", font_size)
        bom_svg_left_offset = self.svg_pref.GetFloat(
            "LeftOffset", BOM_SVG_LEFT_OFFSET
        )
        self.svg_pref.SetFloat("LeftOffset", bom_svg_left_offset)
        bom_svg_top_offset = self.svg_pref.GetFloat(
            "TopOffset", BOM_SVG_TOP_OFFSET
        )
        self.svg_pref.SetFloat("TopOffset", bom_svg_top_offset)
        template_file = self.svg_pref.GetString(
            "TemplateFile", str(TEMPLATE_FILE)
        )
        self.svg_pref.SetString("TemplateFile", str(template_file))
        min_right_offset = self.svg_pref.GetFloat(
            "MinRightOffset", BOM_SVG_MIN_RIGHT_OFFSET
        )
        self.svg_pref.SetFloat("MinRightOffset", min_right_offset)
        min_bottom_offset = self.svg_pref.GetFloat(
            "MinBottomOffset", BOM_SVG_MIN_BOTTOM_OFFSET
        )
        self.svg_pref.SetFloat("MinBottomOffset", min_bottom_offset)
        max_width = self.svg_pref.GetFloat("MaxWidth", BOM_TABLE_SVG_MAX_WIDTH)
        self.svg_pref.SetFloat("MaxWidth", max_width)
        max_height = self.svg_pref.GetFloat(
            "MaxHeight", BOM_TABLE_SVG_MAX_HEIGHT
        )
        self.svg_pref.SetFloat("MaxHeight", max_height)

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
        for dia in self.dia_weight_map.GetStrings():
            weight = self.dia_weight_map.GetFloat(dia)
            weight = FreeCAD.Units.Quantity(str(weight * 10 ** 3) + "kg/m")
            dia_weight_map[int(dia)] = weight
        return dia_weight_map

    def getRebarLengthType(self):
        return self.rebar_length_type

    def getSVGPrefGroup(self):
        return self.svg_pref
