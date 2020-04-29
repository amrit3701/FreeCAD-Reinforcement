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


from pathlib import Path
from datetime import date

import FreeCAD


# Units used to display data in Bill Of Material
COLUMN_UNITS = {
    "Diameter": "mm",
    "RebarLength": "m",
    "RebarsTotalLength": "m",
}

# Column are configurable i.e. you can change Name of column header, change
# their sequence and show/hide column.
# 1. To change column headers, change first value in tuple in below dictionary.
#    e.g. To change column header "Mark" to "Mark Number" replace ("Mark", 1)
#    with ("Mark Number", 1))
# 2. To modify sequence of column, change second value in tuple in below
# dictionary.
#    e.g. To place "Mark" column at third column in BOM, change ("Mark", 1)
#    to ("Mark", 3)
# 3. To hide column, set second value in tuple in below dictionary to 0. And to
#    show column, set it to other than 0 which will be used used as placement
#    sequence number for that column.
#    e.g. to hide column "Mark", replace ("Mark", 1) with ("Mark", 0)
#
# Note: You must take care that no two columns get same placement number. And
#       must not delete/modify values in LHS of ":" (colon).
COLUMN_HEADERS = {
    "Mark": ("Mark", 1),
    "RebarsCount": ("No. of Rebars", 2),
    "Diameter": ("Diameter in " + COLUMN_UNITS["Diameter"], 3),
    "RebarLength": ("Length in " + COLUMN_UNITS["RebarLength"] + "/piece", 4),
    "RebarsTotalLength": (
        "Total Length in " + COLUMN_UNITS["RebarsTotalLength"],
        5,
    ),
}

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


# ---------------------------------SVG Config---------------------------------

# Width of each column in svg table
COLUMN_WIDTH = 30

# Height of each row in svg table
ROW_HEIGHT = 10

# Font size of svg text
FONT_SIZE = 3

# Available sizes as widthxheight in mm
AVAILABLE_SVG_SIZES = {
    "A0": "841x1189",
    "A1": "594x841",
    "A2": "420x594",
    "A3": "297x420",
    "A4": "210x297",
}

# Size of svg sheet, if blank (SVG_SIZE = "") then it will be calculated
# automatically to fit Bill of Material
SVG_SIZE = AVAILABLE_SVG_SIZES["A4"]

# Left offset (minimum) of bill of material svg
BOM_SVG_LEFT_OFFSET = 6

# Right offset (minimum) of bill of material svg
BOM_SVG_RIGHT_OFFSET = 6

# Top offset of bill of material svg
BOM_SVG_TOP_OFFSET = 6

# Bottom offset (minimum) of bill of material svg
BOM_SVG_BOTTOM_OFFSET = 6

# Project info will be shown as "Key: value" pairs.
SVG_HEADER_PROJECT_INFO = {
    "Project": "Project Name",
    "Created By": "Author Name",
    "Date": str(date.today()),
}

# This will be shown next to company logo
SVG_HEADER_COMPANY_INFO = (
    "Company Name\nAddress Line1\nAddress Line2\nTel. 99999-88888\nEmail: "
    "foo@foo.com\nwebsite"
)

# Logo path must be absolute path of logo file.
# Supported logo file formats are: "png", "jpeg", "jpg", "ico" and "bmp"
SVG_HEADER_COMPANY_LOGO = Path(__file__).parent.absolute() / "company_logo.png"

# Maximum width of logo to be used in BOM
SVG_HEADER_COMPANY_LOGO_WIDTH = 30

# Maximum height of logo to be used in BOM
SVG_HEADER_COMPANY_LOGO_HEIGHT = 30

# Footer text to be included in BOM
SVG_FOOTER_TEXT = "Proudly generated using FreeCAD - Rebar Addon"
