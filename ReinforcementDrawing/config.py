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


import FreeCAD


# The diameter of circular point (for rebars perpendicular to view plane) is
# calculated as: SVG_POINT_DIA_FACTOR * <dia_of_rebar>
SVG_POINT_DIA_FACTOR = 0.1

# Font family of dimension text
FONT_FAMILY = "DejaVu Sans"

# Font size of dimension text
FONT_SIZE = 30

# Default Template File for Drawing
TEMPLATE_FILE = FreeCAD.ParamGet(
    "User parameter:BaseApp/Preferences/Mod/TechDraw/Files"
).GetString("TemplateFile")

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
