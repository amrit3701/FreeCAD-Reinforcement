# -*- coding: utf-8 -*-
# ***************************************************************************
# *                                                                         *
# *   Copyright (c) 2019 - Suraj <dadralj18@gmail.com>             *
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

__title__ = "Single Tie Reinforcement"
__author__ = "Suraj"
__url__ = "https://www.freecadweb.org"

import FreeCADGui
import sys

sys.path.append("../")
from Stirrup import makeStirrup
from StraightRebar import makeStraightRebar


def singleTieColumn1Reinforcement(
    xdir_cover,
    ydir_cover,
    offset_of_tie,
    bentAngle,
    bentFactor,
    dia_of_tie,
    amount_spacing_check,
    amount_spacing_value,
    dia_of_rebars,
    t_offset_of_rebars,
    b_offset_of_rebars,
    rebar_type="StraightRebar",
    structure=None,
):
    """ singleTieColumn1Reinforcement(XDirectionCover, YDirectionCover,
    OffsetOfTie, BentAngle, BentFactor, DiameterOfTie, AmountSpacingCheck,
    AmountSpacingValue, DiameterOfRebars, RebarType, Structure)
    Adds the Single Tie reinforcement to the selected structural column
    object."""
    if not structure:
        selected_obj = FreeCADGui.Selection.getSelectionEx()[0]
        structure = selected_obj.Object

    # Calculate parameters for Straight rebars
    f_cover = xdir_cover + dia_of_rebars / 2 + dia_of_tie / 2
    rl_cover = ydir_cover + dia_of_rebars / 2 + dia_of_tie / 2
    t_cover = t_offset_of_rebars
    b_cover = b_offset_of_rebars
    orientation = "Vertical"
    # facename = "Face2"
    # find facename of face perpendicular to x-axis
    index = 1
    faces = structure.Shape.Faces
    for face in faces:
        normal = face.normalAt(0, 0)
        if normal.x == 1 and normal.y == 0 and normal.z == 0:
            facename = "Face" + str(index)
        index = index + 1

    rebar_amount_spacing_check = True
    rebar_amount_spacing_value = 2
    list_coverAlong = ["Right Side", "Left Side"]

    # Create Straight Rebars
    for coverAlong in list_coverAlong:
        makeStraightRebar(
            f_cover,
            (coverAlong, rl_cover),
            t_cover,
            b_cover,
            dia_of_rebars,
            rebar_amount_spacing_check,
            rebar_amount_spacing_value,
            orientation,
            structure,
            facename,
        )

    # Calculate parameters for Stirrup
    rounding = (float(dia_of_tie) / 2 + dia_of_rebars / 2) / dia_of_tie

    # facename = "Face6"
    # find facename of face perpendicular to z-axis
    index = 1
    faces = structure.Shape.Faces
    for face in faces:
        normal = face.normalAt(0, 0)
        if normal.x == 0 and normal.y == 0 and normal.z == 1:
            facename = "Face" + str(index)
        index = index + 1

    l_cover = r_cover = xdir_cover
    t_cover = b_cover = ydir_cover
    f_cover = offset_of_tie

    # Create Stirrups
    makeStirrup(
        l_cover,
        r_cover,
        t_cover,
        b_cover,
        f_cover,
        bentAngle,
        bentFactor,
        dia_of_tie,
        rounding,
        amount_spacing_check,
        amount_spacing_value,
        structure,
        facename,
    )
