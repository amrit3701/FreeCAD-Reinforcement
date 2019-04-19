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
from LShapeRebar import makeLShapeRebar
from Rebarfunc import getParametersOfFace


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
    l_rebar_orientation="Top Inside",
    l_rebar_rounding=None,
    l_part_length=None,
    structure=None,
):
    """ singleTieColumn1Reinforcement(XDirectionCover, YDirectionCover,
    OffsetOfTie, BentAngle, BentFactor, DiameterOfTie, AmountSpacingCheck,
    AmountSpacingValue, DiameterOfRebars, RebarType, LShapeRebarOrientation,
    LShapeRebarRounding, LShapePartLength, Structure)
    Adds the Single Tie reinforcement to the selected structural column
    object.
    It takes four different orientations input for L-shaped rebars i.e. 'Top
    Inside', 'Top Outside', 'Bottom Inside', 'Bottom Outside'.
    """
    if not structure:
        selected_obj = FreeCADGui.Selection.getSelectionEx()[0]
        structure = selected_obj.Object

    # Calculate common parameters for Straight/LShaped rebars
    f_cover = xdir_cover + dia_of_rebars / 2 + dia_of_tie / 2
    t_cover = t_offset_of_rebars
    b_cover = b_offset_of_rebars
    rebar_amount_spacing_check = True
    rebar_amount_spacing_value = 2

    # facename = "Face2"
    # find facename of face perpendicular to x-axis
    index = 1
    faces = structure.Shape.Faces
    for face in faces:
        normal = face.normalAt(0, 0)
        if normal.x == 1 and normal.y == 0 and normal.z == 0:
            facename = "Face" + str(index)
        index += 1

    # Create Straight Rebars
    if rebar_type == "StraightRebar":
        rl_cover = ydir_cover + dia_of_rebars / 2 + dia_of_tie / 2
        orientation = "Vertical"
        list_coverAlong = ["Right Side", "Left Side"]
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
    # Create L-Shaped Rebars
    elif rebar_type == "LShapeRebar":
        FacePRM = getParametersOfFace(structure, facename)
        face_length = FacePRM[0][0]
        if not l_part_length:
            l_part_length = (face_length - 2 * ydir_cover) / 3
        if not l_rebar_rounding:
            l_rebar_rounding = (float(dia_of_tie) / 2 + dia_of_rebars / 2) / dia_of_tie

        if (
            l_rebar_orientation == "Top Inside"
            or l_rebar_orientation == "Bottom Inside"
        ):
            l_cover = []
            r_cover = []
            l_cover.append(ydir_cover + dia_of_rebars / 2 + dia_of_tie / 2)
            r_cover.append(
                face_length
                - l_part_length
                - ydir_cover
                - dia_of_tie / 2
                - dia_of_rebars / 2
            )
            l_cover.append(r_cover[0])
            r_cover.append(l_cover[0])
            # Assign orientation value
            if l_rebar_orientation == "Top Inside":
                list_orientation = ["Top Left", "Top Right"]
            else:
                list_orientation = ["Bottom Left", "Bottom Right"]

        elif (
            l_rebar_orientation == "Top Outside"
            or l_rebar_orientation == "Bottom Outside"
        ):
            if l_rebar_orientation == "Top Outside":
                list_orientation = ["Top Left", "Top Right"]
            else:
                list_orientation = ["Bottom Left", "Bottom Right"]
            l_cover = []
            r_cover = []
            l_cover.append(ydir_cover + dia_of_rebars / 2 + dia_of_tie / 2)
            r_cover.append(
                face_length
                - ydir_cover
                - dia_of_tie / 2
                - dia_of_rebars / 2
                + l_part_length
            )
            l_cover.append(r_cover[0])
            r_cover.append(l_cover[0])

        i = 0
        for orientation in list_orientation:
            makeLShapeRebar(
                f_cover,
                b_cover,
                l_cover[i],
                r_cover[i],
                dia_of_rebars,
                t_cover,
                l_rebar_rounding,
                rebar_amount_spacing_check,
                rebar_amount_spacing_value,
                orientation,
                structure,
                facename,
            )
            i += 1

    # Calculate parameters for Stirrup
    rounding = (float(dia_of_tie) / 2 + dia_of_rebars / 2) / dia_of_tie
    l_cover = r_cover = xdir_cover
    t_cover = b_cover = ydir_cover
    f_cover = offset_of_tie

    # facename = "Face6"
    # find facename of face perpendicular to z-axis
    index = 1
    faces = structure.Shape.Faces
    for face in faces:
        normal = face.normalAt(0, 0)
        if normal.x == 0 and normal.y == 0 and normal.z == 1:
            facename = "Face" + str(index)
        index += 1

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
