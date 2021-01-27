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

__title__ = "Bill Of Material Configuration"
__author__ = "Suraj"
__url__ = "https://www.freecadweb.org"


from collections import OrderedDict
from pathlib import Path

import FreeCAD


# Units used to display data in Bill Of Material
COLUMN_UNITS = {
    "Diameter": "mm",
    "RebarLength": "m",
    "RebarsTotalLength": "m",
}

# Column headers config in format -> ColumnData: ColumnDisplayName
COLUMN_HEADERS = OrderedDict(
    [
        ("Host", "Member"),
        ("Mark", "Mark"),
        ("RebarsCount", "No. of Rebars"),
        ("Diameter", "Diameter in " + COLUMN_UNITS["Diameter"]),
        ("RebarLength", "Length in " + COLUMN_UNITS["RebarLength"] + "/piece"),
        (
            "RebarsTotalLength",
            "Total Length in " + COLUMN_UNITS["RebarsTotalLength"],
        ),
    ]
)

# Map diameter (in mm) with weight (kg/m)
# Default list is taken as per book SP34 from here:
# https://archive.org/details/gov.in.is.sp.34.1987/page/n236/mode/2up
DIA_WEIGHT_MAP = {
    6: FreeCAD.Units.Quantity("0.222 kg/m"),
    8: FreeCAD.Units.Quantity("0.395 kg/m"),
    10: FreeCAD.Units.Quantity("0.617 kg/m"),
    12: FreeCAD.Units.Quantity("0.888 kg/m"),
    14: FreeCAD.Units.Quantity("1.206 kg/m"),
    16: FreeCAD.Units.Quantity("1.578 kg/m"),
    18: FreeCAD.Units.Quantity("2.000 kg/m"),
    20: FreeCAD.Units.Quantity("2.466 kg/m"),
    22: FreeCAD.Units.Quantity("2.980 kg/m"),
    25: FreeCAD.Units.Quantity("3.854 kg/m"),
    28: FreeCAD.Units.Quantity("4.830 kg/m"),
    32: FreeCAD.Units.Quantity("6.313 kg/m"),
    36: FreeCAD.Units.Quantity("7.990 kg/m"),
    40: FreeCAD.Units.Quantity("9.864 kg/m"),
    45: FreeCAD.Units.Quantity("12.490 kg/m"),
    50: FreeCAD.Units.Quantity("15.410 kg/m"),
}

# Type of length to be used in BOM
# It can be "RealLength" or "LengthWithSharpEdges"
REBAR_LENGTH_TYPE = "RealLength"

# Specifies how reinforcement objects should be grouped
# It can be "Mark" or "Host"
REINFORCEMENT_GROUP_BY = "Mark"


# ---------------------------------SVG Config---------------------------------

# Width of each column in svg table
COLUMN_WIDTH = 30

# Height of each row in svg table
ROW_HEIGHT = 10

# Font family of text in bom svg
FONT_FAMILY = "DejaVu Sans"

# Font filename of font for text in bom svg
FONT_FILENAME = "DejaVuSans.ttf"

# Font size of svg text
FONT_SIZE = 3

# Left offset of bill of material svg
BOM_SVG_LEFT_OFFSET = 6

# Top offset of bill of material svg
BOM_SVG_TOP_OFFSET = 40

# BillOfMaterial Template File. It must be valid TechDraw template file as here:
# https://wiki.freecadweb.org/Svg_Namespace
TEMPLATE_FILE = Path(__file__).parent.absolute() / "BOMTemplate.svg"

# ------------------------Constraints on bom table svg------------------------
# Minimum right offset of bill of material svg
BOM_SVG_MIN_RIGHT_OFFSET = 6

# Minimum bottom offset of bill of material svg
BOM_SVG_MIN_BOTTOM_OFFSET = 6

# Maximum width of bill of material table in svg
# Set BOM_TABLE_SVG_MAX_WIDTH = None, if you don't want this constraint to be
# applied
BOM_TABLE_SVG_MAX_WIDTH = 198

# Maximum height of bill of material table in svg
# Set BOM_TABLE_SVG_MAX_HEIGHT = None, if you don't want this constraint to be
# applied
BOM_TABLE_SVG_MAX_HEIGHT = 250
