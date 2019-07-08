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

__title__ = "Two Ties Six Rebars Reinforcement"
__author__ = "Suraj"
__url__ = "https://www.freecadweb.org"


import FreeCAD

from Stirrup import makeStirrup
from StraightRebar import makeStraightRebar
from LShapeRebar import makeLShapeRebar
from ColumnReinforcement.SingleTie import (
    makeSingleTieFourRebars,
    getFacenameforRebar,
    getLRebarOrientationLeftRightCover,
)
from Rebarfunc import getParametersOfFace

if FreeCAD.GuiUp:
    import FreeCADGui


def makeTwoTiesSixRebars(
    l_cover_of_ties,
    r_cover_of_ties,
    t_cover_of_ties,
    b_cover_of_ties,
    offset_of_ties,
    number_spacing_check,
    number_spacing_value,
    dia_of_ties,
    bent_angle_of_ties,
    extension_factor_of_ties,
    dia_of_main_rebars,
    t_offset_of_rebars,
    b_offset_of_rebars,
    main_rebars_type="StraightRebar",
    hook_orientation="Top Inside",
    hook_extend_along="x-axis",
    l_rebar_rounding=None,
    hook_extension=None,
    ties_sequence=("Tie1", "Tie2"),
    structure=None,
    facename=None,
):
    """makeTwoTiesSixRebars(LeftCoverOfTies, RightCoverOfTies, TopCoverOfTies,
    BottomCoverOfTies, OffsetofTies, NumberSpacingCheck, NumberSpacingValue,
    DiameterOfTies, BentAngleOfTies, ExtensionFactorOfTies,
    DiameterOfMainRebars, TopOffsetOfMainRebars, BottomOffsetOfRebars,
    MainRebarsType, LShapeHookOrientation, HookExtendAlong, LShapeRebarRounding,
    LShapeHookLength, TieSequence, Structure, Facename):"""
    if not structure and not facename:
        if FreeCAD.GuiUp:
            selected_obj = FreeCADGui.Selection.getSelectionEx()[0]
            structure = selected_obj.Object
            facename = selected_obj.SubElementNames[0]
        else:
            print("Error: Pass structure and facename arguments")
            return

    FacePRM = getParametersOfFace(structure, facename)
    face_length = FacePRM[0][0]

    dia_of_tie1 = dia_of_ties[0]
    dia_of_tie2 = dia_of_ties[1]
    bent_angle_of_tie1 = bent_angle_of_ties[0]
    bent_angle_of_tie2 = bent_angle_of_ties[1]
    extension_factor_of_tie1 = extension_factor_of_ties[0]
    extension_factor_of_tie2 = extension_factor_of_ties[1]

    if ties_sequence[0] == "Tie2" and ties_sequence[1] == "Tie1":
        start_offset_of_tie1 = offset_of_ties + 2 * dia_of_tie2
        start_offset_of_tie2 = offset_of_ties
        end_offset_of_tie1 = start_offset_of_tie2
        end_offset_of_tie2 = start_offset_of_tie1
    else:
        start_offset_of_tie1 = offset_of_ties
        start_offset_of_tie2 = offset_of_ties + 2 * dia_of_tie1
        end_offset_of_tie1 = start_offset_of_tie2 + dia_of_tie1 / 2
        end_offset_of_tie2 = start_offset_of_tie1 + dia_of_tie2 / 2

    # Calculate parameters for tie1
    l_cover_of_tie1 = l_cover_of_ties
    r_cover_of_tie1 = face_length / 2 - dia_of_main_rebars / 2 - dia_of_tie1

    # Create SingleTieFourRebars
    SingleTieFourRebarsObject = makeSingleTieFourRebars(
        l_cover_of_tie1,
        r_cover_of_tie1,
        t_cover_of_ties,
        b_cover_of_ties,
        start_offset_of_tie1,
        bent_angle_of_tie1,
        extension_factor_of_tie1,
        dia_of_tie1,
        number_spacing_check,
        number_spacing_value,
        dia_of_main_rebars,
        t_offset_of_rebars,
        b_offset_of_rebars,
        main_rebars_type,
        hook_orientation,
        hook_extend_along,
        l_rebar_rounding,
        hook_extension,
        structure,
        facename,
    )
    SingleTieFourRebarsObject.rebar_group.RebarGroups[0].Ties[
        0
    ].OffsetEnd = end_offset_of_tie1

    # Calculate parameters for tie1
    l_cover_of_tie2 = face_length / 2 - dia_of_main_rebars / 2 - dia_of_tie2
    r_cover_of_tie2 = r_cover_of_ties
    rounding = (float(dia_of_tie2) / 2 + dia_of_main_rebars / 2) / dia_of_tie2
    tie2 = makeStirrup(
        l_cover_of_tie2,
        r_cover_of_tie2,
        t_cover_of_ties,
        b_cover_of_ties,
        start_offset_of_tie2,
        bent_angle_of_tie2,
        extension_factor_of_tie2,
        dia_of_tie2,
        rounding,
        number_spacing_check,
        number_spacing_value,
        structure,
        facename,
    )
    tie2.OffsetEnd = end_offset_of_tie2


    # Calculate common parameters for Straight/LShaped rebars
    if hook_extend_along == "x-axis":
        f_cover = b_cover_of_ties + dia_of_tie2
    else:
        f_cover = r_cover_of_ties + dia_of_tie2
    t_cover = t_offset_of_rebars
    b_cover = b_offset_of_rebars
    rebar_number_spacing_check = True

    # Find facename of face normal to selected/provided face
    facename_for_rebars = getFacenameforRebar(
        hook_extend_along, facename, structure
    )

    # Create Straight Rebars
    if main_rebars_type == "StraightRebar":
        # Right and left cover changes with hook_extend_along because facename,
        # using which rebars created, changes with value of hook_extend_along
        if hook_extend_along == "x-axis":
            r_cover = r_cover_of_ties + dia_of_tie2
        else:
            r_cover = t_cover_of_ties + dia_of_tie2
            l_cover = b_cover_of_ties + dia_of_tie2
            rl_cover = [r_cover, l_cover]
        orientation = "Vertical"
        list_coverAlong = ["Right Side", "Left Side"]

        main_rebars = []
        if hook_extend_along == "x-axis":
            rebar_number_spacing_value = 2
            main_rebars.append(
                makeStraightRebar(
                    f_cover,
                    ("Right Side", r_cover),
                    t_cover,
                    b_cover,
                    dia_of_main_rebars,
                    rebar_number_spacing_check,
                    rebar_number_spacing_value,
                    orientation,
                    structure,
                    facename_for_rebars,
                )
            )
            main_rebars[-1].OffsetEnd = (
                t_cover_of_ties + dia_of_tie2 + dia_of_main_rebars / 2
            )
        elif hook_extend_along == "y-axis":
            rebar_number_spacing_value = 1
            for i, coverAlong in enumerate(list_coverAlong):
                main_rebars.append(
                    makeStraightRebar(
                        f_cover,
                        (coverAlong, rl_cover[i]),
                        t_cover,
                        b_cover,
                        dia_of_main_rebars,
                        rebar_number_spacing_check,
                        rebar_number_spacing_value,
                        orientation,
                        structure,
                        facename_for_rebars,
                    )
                )
                main_rebars[i].OffsetEnd = (
                    b_cover_of_ties + dia_of_tie2 + dia_of_main_rebars / 2
                )

    # Create L-Shaped Rebars
    elif main_rebars_type == "LShapeRebar":
        FacePRM = getParametersOfFace(structure, facename_for_rebars)
        face_length = FacePRM[0][0]
        # Implement hook extension values from here:
        # https://archive.org/details/gov.in.is.sp.16.1980/page/n207
        if not hook_extension:
            hook_extension = 4 * dia_of_main_rebars
        if not l_rebar_rounding:
            l_rebar_rounding = (
                float(dia_of_tie2) / 2 + dia_of_main_rebars / 2
            ) / dia_of_tie2
        l_rebar_orientation_cover = getLRebarOrientationLeftRightCover(
            hook_orientation,
            hook_extension,
            hook_extend_along,
            l_cover_of_ties,
            r_cover_of_ties,
            t_cover_of_ties,
            b_cover_of_ties,
            dia_of_tie2,
            dia_of_main_rebars,
            l_rebar_rounding,
            face_length,
        )
        list_orientation = l_rebar_orientation_cover["list_orientation"]
        l_cover = l_rebar_orientation_cover["l_cover"]
        r_cover = l_rebar_orientation_cover["r_cover"]
        t_cover = t_offset_of_rebars
        b_cover = b_offset_of_rebars

        main_rebars = []
        if hook_extend_along == "x-axis":
            rebar_number_spacing_value = 2
            orientation = list_orientation[1]
            main_rebars.append(
                makeLShapeRebar(
                    f_cover,
                    b_cover,
                    l_cover[1],
                    r_cover[1],
                    dia_of_main_rebars,
                    t_cover,
                    l_rebar_rounding,
                    rebar_number_spacing_check,
                    rebar_number_spacing_value,
                    orientation,
                    structure,
                    facename_for_rebars,
                )
            )
            main_rebars[-1].OffsetEnd = (
                t_cover_of_ties + dia_of_tie2 + dia_of_main_rebars / 2
            )
        elif hook_extend_along == "y-axis":
            rebar_number_spacing_value = 1
            orientation = list_orientation[1]
            for i, orientation in enumerate(list_orientation):
                main_rebars.append(
                    makeLShapeRebar(
                        f_cover,
                        b_cover,
                        l_cover[i],
                        r_cover[i],
                        dia_of_main_rebars,
                        t_cover,
                        l_rebar_rounding,
                        rebar_number_spacing_check,
                        rebar_number_spacing_value,
                        orientation,
                        structure,
                        facename_for_rebars,
                    )
                )
                main_rebars[i].OffsetEnd = (
                    l_cover_of_ties + dia_of_tie2 + dia_of_main_rebars / 2
                )

    FreeCAD.ActiveDocument.recompute()
    print("WIP")
