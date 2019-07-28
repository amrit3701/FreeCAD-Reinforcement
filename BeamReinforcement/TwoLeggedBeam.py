# -*- coding: utf-8 -*-
# ***************************************************************************
# *                                                                         *
# *   Copyright (c) 2019 - Suraj <dadralj18@gmail.com>                      *
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

__title__ = "Two Legged Stirrup Beam Reinforcement"
__author__ = "Suraj"
__url__ = "https://www.freecadweb.org"


import FreeCAD

from Stirrup import makeStirrup

if FreeCAD.GuiUp:
    import FreeCADGui


def makeReinforcement(
    l_cover_of_stirrup,
    r_cover_of_stirrup,
    t_cover_of_stirrup,
    b_cover_of_stirrup,
    offset_of_stirrup,
    bent_angle,
    extension_factor,
    dia_of_stirrup,
    number_spacing_check,
    number_spacing_value,
    dia_of_main_rebars,
    structure=None,
    facename=None,
):
    if not structure and not facename:
        if FreeCAD.GuiUp:
            selected_obj = FreeCADGui.Selection.getSelectionEx()[0]
            structure = selected_obj.Object
            facename = selected_obj.SubElementNames[0]
        else:
            showWarning("Error: Pass structure and facename arguments")
            return None

    # Calculate parameters for Stirrup
    rounding = (
        float(dia_of_stirrup) / 2 + dia_of_main_rebars / 2
    ) / dia_of_stirrup
    f_cover = offset_of_stirrup

    # Create Stirrup
    tie = makeStirrup(
        l_cover_of_stirrup,
        r_cover_of_stirrup,
        t_cover_of_stirrup,
        b_cover_of_stirrup,
        f_cover,
        bent_angle,
        extension_factor,
        dia_of_stirrup,
        rounding,
        number_spacing_check,
        number_spacing_value,
        structure,
        facename,
    )
    print("WIP")
