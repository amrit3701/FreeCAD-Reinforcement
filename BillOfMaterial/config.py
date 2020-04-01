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

# Column headers can be changed without affecting their data
# e.g. changing column header "No. of Rebars" to something else will still be
# used to represent amount of rebars
COLUMN_HEADERS = (
    "Member",
    "Mark",
    "No. Of Rebars",
    "Diameter in mm",
    "Length in m/piece",
    "Total Length in m",
)

# These diameters will be displayed by adding "#" before that diameter
# i.e. 8 will be displayed as #8
COLUMN_DIA_HEADERS = (8, 10, 12, 16, 20)
