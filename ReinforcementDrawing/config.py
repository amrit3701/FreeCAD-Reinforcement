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

# Fill color for structure in drawing svg
# Format: (r, g, b)
# r, g, b value should be between 0 to 1, so you may need to divide value of r,
# g, b by 255 to get its value between 0 to 1
# Make sure r, g, b must be float
REBARS_COLOR = (0.67, 0.0, 0.0)

# Font family of dimension text
FONT_FAMILY = "DejaVu Sans"

# Font size of dimension text
FONT_SIZE = 3

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
