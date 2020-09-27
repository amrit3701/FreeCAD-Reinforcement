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


__title__ = "Reinforcement Drawing Configuration"
__author__ = "Suraj"
__url__ = "https://www.freecadweb.org"


from pathlib import Path


# stroke-width of structure in drawing svg
STRUCTURE_STROKE_WIDTH = 0.5

# Fill style of structure
# - set it to "Automatic" to automatically select structure color
# - set it to "Custom" to choose structure color value from variable
#   STRUCTURE_COLOR
# - set it to none to not fill nothing in structure
STRUCTURE_COLOR_STYLE = "Automatic"

# Fill color for structure in drawing svg
# Format: (r, g, b)
# r, g, b value should be between 0 to 1, so you may need to divide value of r,
# g, b by 255 to get its value between 0 to 1
# Make sure r, g, b must be float
STRUCTURE_COLOR = (0.3, 0.9, 0.91)

# stroke-width of rebars in drawing svg
REBARS_STROKE_WIDTH = 0.35

# Color style of rebars
# - set it to "Automatic" to automatically select rebars color
# - set it to "Custom" to choose shape color value from variable REBARS_COLOR
REBARS_COLOR_STYLE = "Automatic"

# Fill color for rebars in drawing svg
# Format: (r, g, b)
# r, g, b value should be between 0 to 1, so you may need to divide value of r,
# g, b by 255 to get its value between 0 to 1
# Make sure r, g, b must be float
REBARS_COLOR = (0.67, 0.0, 0.0)

# Default Template File for Drawing
TEMPLATE_FILE = str(
    Path(__file__).parent.absolute() / "Templates" / "A4_Landscape_blank.svg"
)

# Left offset of drawing on Template File
DRAWING_LEFT_OFFSET = 20

# Top offset of drawing on Template File
DRAWING_TOP_OFFSET = 20

# ------------------------Constraints on size of drawing svg------------------
# Minimum right offset of drawing on Template File
DRAWING_MIN_RIGHT_OFFSET = 20

# Minimum bottom offset of drawing on Template File
DRAWING_MIN_BOTTOM_OFFSET = 20

# Maximum width of drawing on Template File
DRAWING_MAX_WIDTH = 297

# Maximum height of drawing on Template File
DRAWING_MAX_HEIGHT = 210

# -------------------------Reinforcement Dimensioning-------------------------
# The format of dimension label
# %M -> Rebar.Mark
# %C -> Rebar.Amount
# %D -> Rebar.Diameter
# %S -> Rebar span length
DIMENSION_LABEL_FORMAT = "%M %C⌀%D,span=%S"

# Font family of dimension label
DIMENSION_FONT_FAMILY = "DejaVu Sans"

# Font size of dimension label
DIMENSION_FONT_SIZE = 3

# The stroke-width of dimension line
DIMENSION_STROKE_WIDTH = 0.25

# The stroke style of dimension line
# Supported line styles: "Continuous", "Dash", "Dot", "DashDot" or "DashDotDot"
DIMENSION_LINE_STYLE = "Continuous"

# The color of dimension line
# Format: (r, g, b)
# r, g, b value should be between 0 to 1, so you may need to divide value of r,
# g, b by 255 to get its value between 0 to 1
# Make sure r, g, b must be float
DIMENSION_LINE_COLOR = (0.0, 0.0, 0.50)

# The color of dimension text
DIMENSION_TEXT_COLOR = (0.0, 0.33, 0.0)

# The dimension line start symbol, in case of single rebar is visible
# Supported values: "FilledArrow", "Tick", "Dot" or "None"
DIMENSION_SINGLE_REBAR_LINE_START_SYMBOL = "None"

# The dimension line end symbol, in case of single rebar is visible
# Supported values: "FilledArrow", "Tick", "Dot" or "None"
DIMENSION_SINGLE_REBAR_LINE_END_SYMBOL = "FilledArrow"

# The dimension line start symbol, in case of multiple rebars are visible
# Supported values: "FilledArrow", "Tick", "Dot" or "None"
DIMENSION_MULTI_REBAR_LINE_START_SYMBOL = "FilledArrow"

# The dimension line end symbol, in case of multiple rebars are visible
# Supported values: "FilledArrow", "Tick", "Dot" or "None"
DIMENSION_MULTI_REBAR_LINE_END_SYMBOL = "FilledArrow"

# The dimension line mid points symbol
# Supported values: "Tick", "Dot" or "None"
DIMENSION_LINE_MID_POINT_SYMBOL = "Dot"

# The left/right/top/bottom offset of dimension from drawing
DIMENSION_LEFT_OFFSET = 10
DIMENSION_RIGHT_OFFSET = 10
DIMENSION_TOP_OFFSET = 10
DIMENSION_BOTTOM_OFFSET = 10

# The increment in left/right/top/bottom offset to move each new dimension label
# away from drawing
DIMENSION_LEFT_OFFSET_INCREMENT = 6
DIMENSION_RIGHT_OFFSET_INCREMENT = 6
DIMENSION_TOP_OFFSET_INCREMENT = 6
DIMENSION_BOTTOM_OFFSET_INCREMENT = 6

# Set it to True if dimension lines to be outside of reinforcement drawing
# for automated reinforcement dimensioning, in case of single rebar is
# visible, set False otherwise
DIMENSION_SINGLE_REBAR_OUTER_DIM = False

# Set it to True if dimension lines to be outside of reinforcement drawing
# for automated reinforcement dimensioning, in case of multiple rebars are
# visible, set False otherwise
DIMENSION_MULTI_REBAR_OUTER_DIM = True

# The dimension label position type, in case of single rebar is visible
# Supported values: "StartOfLine", "MidOfLine" or "EndOfLine"
DIMENSION_SINGLE_REBAR_TEXT_POSITION_TYPE = "StartOfLine"

# The dimension label position type, in case of multiple rebars are visible
# Supported values: "StartOfLine", "MidOfLine" or "EndOfLine"
DIMENSION_MULTI_REBAR_TEXT_POSITION_TYPE = "MidOfLine"
