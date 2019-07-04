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

__title__ = "Single Tie Multiple Rebars Reinforcement"
__author__ = "Suraj"
__url__ = "https://www.freecadweb.org"


import FreeCAD

from ColumnReinforcement.SingleTie import (
    makeSingleTieFourRebars,
    editSingleTieFourRebars,
    getFacenameforRebar,
    getLRebarOrientationLeftRightCover,
)
from StraightRebar import makeStraightRebar
from LShapeRebar import makeLShapeRebar, editLShapeRebar
from Rebarfunc import getParametersOfFace, gettupleOfNumberDiameter

if FreeCAD.GuiUp:
    import FreeCADGui


def makeSingleTieMultipleRebars(
    l_cover_of_tie,
    r_cover_of_tie,
    t_cover_of_tie,
    b_cover_of_tie,
    offset_of_tie,
    bent_angle,
    extension_factor,
    dia_of_tie,
    number_spacing_check,
    number_spacing_value,
    dia_of_main_rebars,
    main_rebars_t_offset,
    main_rebars_b_offset,
    main_rebars_type="StraightRebar",
    main_hook_orientation="Top Inside",
    main_hook_extend_along="x-axis",
    l_main_rebar_rounding=None,
    main_hook_extension=None,
    sec_rebars_t_offset=None,
    sec_rebars_b_offset=None,
    sec_rebars_number_diameter=None,
    sec_rebars_type=("StraightRebar", "StraightRebar"),
    sec_hook_orientation=("Top Inside", "Top Inside"),
    l_sec_rebar_rounding=None,
    sec_hook_extension=None,
    structure=None,
    facename=None,
):
    """makeSingleTieMultipleRebars(LeftCoverOfTie, RightCoverOfTie,
    TopCoverOfTie, BottomCoverOfTie, OffsetofTie, BentAngle, ExtensionFactor,
    DiameterOfTie, NumberSpacingCheck, NumberSpacingValue, DiameterOfMainRebars,
    TopOffsetOfMainRebars, BottomOffsetofMainRebars, MainRebarType,
    MainLShapeHookOrientation, MainLShapeHookExtendAlong,
    LShapeMainRebarRounding, LShapeMainHookLength, TopOffsetOfSecondaryRebars,
    BottomOffsetOfSecondaryRebars, SecondaryRebarNumberDiameterString,
    SecondaryRebarType, SecondaryLShapeHookOrientation,
    LShapeSecondaryRebarRounding, LShapeSecondaryHookLength, Structure,
    Facename):
    Adds the Single Tie Multiple Rebars reinforcement to the selected structural
    column object.

    It takes two different inputs for main_rebars_type i.e. 'StraightRebar',
    'LShapeRebar'.

    It takes eight different orientations input for Main L-shaped hooks i.e.
    'Top Inside', 'Top Outside', 'Bottom Inside', 'Bottom Outside', 'Top Left',
    'Top Right', 'Bottom Left', 'Bottom Right'.

    It takes two different inputs for main_hook_extend_along i.e. 'x-axis',
    'y-axis'.

    Note: Type of sec_rebars_t_offset, sec_rebars_b_offset,
    sec_rebars_number_diameter, sec_rebars_type, sec_hook_orientation,
    l_sec_rebar_rounding and sec_hook_extension argumants is a tuple.
    Syntax: (<value_for_xdir_rebars>, <value_for_ydir_rebars>).

    In sec_hook_orientation(<xdir_rebars_orientation>,
    <ydir_rebars_orientation>),
    Value of xdir_rebars_orientation can be: 'Top Inside', 'Top Outside',
    'Bottom Inside', 'Bottom Outside', 'Top Upward', 'Top Downward', 'Bottom
    Upward', 'Bottom Downward'.
    Value of ydir_rebars_orientation can be: 'Top Inside', 'Top Outside',
    'Bottom Inside', 'Bottom Outside', 'Top Left', 'Top Right', 'Bottom
    Left', 'Bottom Right'.
    """
    if not structure and not facename:
        if FreeCAD.GuiUp:
            selected_obj = FreeCADGui.Selection.getSelectionEx()[0]
            structure = selected_obj.Object
            facename = selected_obj.SubElementNames[0]
        else:
            print("Error: Pass structure and facename arguments")
            return None

    SingleTieFourRebarsObject = makeSingleTieFourRebars(
        l_cover_of_tie,
        r_cover_of_tie,
        t_cover_of_tie,
        b_cover_of_tie,
        offset_of_tie,
        bent_angle,
        extension_factor,
        dia_of_tie,
        number_spacing_check,
        number_spacing_value,
        dia_of_main_rebars,
        main_rebars_t_offset,
        main_rebars_b_offset,
        main_rebars_type,
        main_hook_orientation,
        main_hook_extend_along,
        l_main_rebar_rounding,
        main_hook_extension,
        structure,
        facename,
    )

    if not sec_rebars_number_diameter:
        return SingleTieFourRebarsObject
    else:
        xdir_rebars_number_diameter = sec_rebars_number_diameter[0]
        ydir_rebars_number_diameter = sec_rebars_number_diameter[1]
        if (
            not xdir_rebars_number_diameter
            or xdir_rebars_number_diameter == "0"
        ) and (
            not ydir_rebars_number_diameter
            or ydir_rebars_number_diameter == "0"
        ):
            return SingleTieFourRebarsObject

    # Set parameters for xdir and ydir rebars
    if not sec_rebars_t_offset:
        xdir_rebars_t_offset = ydir_rebars_t_offset = main_rebars_t_offset
    else:
        xdir_rebars_t_offset = sec_rebars_t_offset[0]
        ydir_rebars_t_offset = sec_rebars_t_offset[1]
    if not sec_rebars_b_offset:
        xdir_rebars_b_offset = ydir_rebars_b_offset = main_rebars_b_offset
    else:
        xdir_rebars_b_offset = sec_rebars_b_offset[0]
        ydir_rebars_b_offset = sec_rebars_b_offset[1]
    xdir_rebars_type = sec_rebars_type[0]
    ydir_rebars_type = sec_rebars_type[1]
    if not sec_hook_orientation:
        if xdir_rebars_type == "StraightRebar":
            xdir_hook_orientation = None
        elif xdir_rebars_type == "LShapeRebar":
            xdir_hook_orientation = "Top Inside"
        if ydir_rebars_type == "StraightRebar":
            ydir_hook_orientation = None
        elif ydir_rebars_type == "LShapeRebar":
            ydir_hook_orientation = "Top Inside"
    else:
        xdir_hook_orientation = sec_hook_orientation[0]
        ydir_hook_orientation = sec_hook_orientation[1]
    if l_sec_rebar_rounding:
        l_xdir_rebar_rounding = l_sec_rebar_rounding[0]
        l_ydir_rebar_rounding = l_sec_rebar_rounding[1]
    if sec_hook_extension:
        xdir_hook_extension = sec_hook_extension[0]
        ydir_hook_extension = sec_hook_extension[1]

    if xdir_rebars_number_diameter and xdir_rebars_number_diameter != "0":
        xdir_rebars = makeXDirRebars(
            l_cover_of_tie,
            r_cover_of_tie,
            t_cover_of_tie,
            b_cover_of_tie,
            dia_of_tie,
            dia_of_main_rebars,
            xdir_rebars_t_offset,
            xdir_rebars_b_offset,
            xdir_rebars_type,
            xdir_hook_orientation,
            xdir_hook_extension,
            l_xdir_rebar_rounding,
            xdir_rebars_number_diameter,
            facename,
            structure,
        )
    if ydir_rebars_number_diameter and ydir_rebars_number_diameter != "0":
        ydir_rebars = makeYDirRebars(
            l_cover_of_tie,
            r_cover_of_tie,
            t_cover_of_tie,
            b_cover_of_tie,
            dia_of_tie,
            dia_of_main_rebars,
            ydir_rebars_t_offset,
            ydir_rebars_b_offset,
            ydir_rebars_type,
            ydir_hook_orientation,
            ydir_hook_extension,
            l_ydir_rebar_rounding,
            ydir_rebars_number_diameter,
            facename,
            structure,
        )

    # Create object of _SingleTieMultipleRebars to add new properties to it
    SingleTieMultipleRebars = _SingleTieMultipleRebars(
        SingleTieFourRebarsObject
    )

    # Add created xdir/ydir rebars to xdir_rebars_group/ydir_rebars_group
    SingleTieMultipleRebars.addXDirRebars(xdir_rebars)
    SingleTieMultipleRebars.addYDirRebars(ydir_rebars)

    # Set properties values for xdir_rebars in  xdir_rebars_group object
    if len(xdir_rebars) > 0:
        xdir_rebars_group = SingleTieMultipleRebars.xdir_rebars_group
        xdir_rebars_group.RebarType = xdir_rebars_type
        if xdir_rebars_type == "LShapeRebar":
            xdir_rebars_group.HookOrientation = xdir_hook_orientation
            xdir_rebars_group.HookExtension = xdir_hook_extension
        else:
            xdir_rebars_group.HookOrientation = "Top Inside"
        xdir_rebars_group.TopOffset = xdir_rebars_t_offset
        xdir_rebars_group.BottomOffset = xdir_rebars_b_offset
        xdir_rebars_group.NumberDiameter = xdir_rebars_number_diameter

    # Set properties values for ydir_rebars in  ydir_rebars_group object
    if len(ydir_rebars) > 0:
        ydir_rebars_group = SingleTieMultipleRebars.ydir_rebars_group
        ydir_rebars_group.RebarType = ydir_rebars_type
        if ydir_rebars_type == "LShapeRebar":
            ydir_rebars_group.HookOrientation = ydir_hook_orientation
            ydir_rebars_group.HookExtension = ydir_hook_extension
        else:
            ydir_rebars_group.HookOrientation = "Top Inside"
        ydir_rebars_group.TopOffset = ydir_rebars_t_offset
        ydir_rebars_group.BottomOffset = ydir_rebars_b_offset
        ydir_rebars_group.NumberDiameter = ydir_rebars_number_diameter

    FreeCAD.ActiveDocument.recompute()
    return SingleTieMultipleRebars.Object


def makeXDirRebars(
    l_cover_of_tie,
    r_cover_of_tie,
    t_cover_of_tie,
    b_cover_of_tie,
    dia_of_tie,
    dia_of_main_rebars,
    xdir_rebars_t_offset,
    xdir_rebars_b_offset,
    xdir_rebars_type,
    xdir_hook_orientation,
    xdir_hook_extension,
    l_xdir_rebar_rounding,
    xdir_rebars_number_diameter,
    facename,
    structure,
):
    """Adds the rebars along x-direction to the structural column object."""
    xdir_rebars = []
    facename_for_xdir_rebars = getFacenameforRebar(
        "y-axis", facename, structure
    )

    # Find parameters of selected face
    FacePRM = getParametersOfFace(structure, facename)

    # find list of tuples of number and diameter of xdir rebars
    xdir_rebars_number_diameter_list = gettupleOfNumberDiameter(
        xdir_rebars_number_diameter
    )
    xdir_rebars_number_diameter_list.reverse()

    # Calculate spacing between xdir-rebars
    face_length = FacePRM[0][0]
    xdir_span_length = (
        FacePRM[0][0]
        - l_cover_of_tie
        - r_cover_of_tie
        - 2 * dia_of_tie
        - 2 * dia_of_main_rebars
    )
    req_space_for_xdir_rebars = sum(
        x[0] * x[1] for x in xdir_rebars_number_diameter_list
    )
    xdir_rebars_number = sum(
        number for number, _ in xdir_rebars_number_diameter_list
    )
    spacing_in_xdir_rebars = (xdir_span_length - req_space_for_xdir_rebars) / (
        xdir_rebars_number + 1
    )

    # Set parameter values for Straight/LShape xdir_rebars
    list_coverAlong = ["Right Side", "Left Side"]

    if xdir_rebars_type == "StraightRebar":
        # Set parameter values for Straight xdir_rebars
        r_cover = t_cover_of_tie + dia_of_tie
        l_cover = b_cover_of_tie + dia_of_tie
        rl_cover = [r_cover, l_cover]

        # Create Straight rebars along x-direction
        for i, coverAlong in enumerate(list_coverAlong):
            for j, (number, dia) in enumerate(xdir_rebars_number_diameter_list):
                if j == 0:
                    f_cover_of_xdir_rebars = (
                        r_cover_of_tie
                        + dia_of_tie
                        + dia_of_main_rebars
                        + spacing_in_xdir_rebars
                    )
                rear_cover_of_xdir_rebars = (
                    FacePRM[0][0]
                    - f_cover_of_xdir_rebars
                    - number * dia
                    - (number - 1) * spacing_in_xdir_rebars
                )

                xdir_rebars.append(
                    makeStraightRebar(
                        f_cover_of_xdir_rebars,
                        (coverAlong, rl_cover[i]),
                        xdir_rebars_t_offset,
                        xdir_rebars_b_offset,
                        dia,
                        True,
                        number,
                        "Vertical",
                        structure,
                        facename_for_xdir_rebars,
                    )
                )
                xdir_rebars[-1].OffsetEnd = rear_cover_of_xdir_rebars + dia / 2
                f_cover_of_xdir_rebars += (
                    number * dia + number * spacing_in_xdir_rebars
                )
    elif xdir_rebars_type == "LShapeRebar":
        face_length = getParametersOfFace(structure, facename_for_xdir_rebars)[
            0
        ][0]
        l_rebar_orientation_cover_list = []
        for i, (number, dia_of_rebars) in enumerate(
            xdir_rebars_number_diameter_list
        ):
            l_rebar_orientation_cover_list.append(
                getLRebarOrientationLeftRightCover(
                    xdir_hook_orientation,
                    xdir_hook_extension,
                    "y-axis",
                    l_cover_of_tie,
                    r_cover_of_tie,
                    t_cover_of_tie,
                    b_cover_of_tie,
                    dia_of_tie,
                    dia_of_rebars,
                    l_xdir_rebar_rounding,
                    face_length,
                )
            )
        list_orientation = l_rebar_orientation_cover_list[0]["list_orientation"]
        l_cover_list = []
        for l_rebar_orientation_cover in l_rebar_orientation_cover_list:
            l_cover_list.append(l_rebar_orientation_cover["l_cover"])

        r_cover_list = []
        for l_rebar_orientation_cover in l_rebar_orientation_cover_list:
            r_cover_list.append(l_rebar_orientation_cover["r_cover"])

        # Create LShape rebars along x-direction
        for i, orientation in enumerate(list_orientation):
            for j, (number, dia) in enumerate(xdir_rebars_number_diameter_list):
                if j == 0:
                    f_cover_of_xdir_rebars = (
                        r_cover_of_tie
                        + dia_of_tie
                        + dia_of_main_rebars
                        + spacing_in_xdir_rebars
                    )
                rear_cover_of_xdir_rebars = (
                    FacePRM[0][0]
                    - f_cover_of_xdir_rebars
                    - number * dia
                    - (number - 1) * spacing_in_xdir_rebars
                )
                xdir_rebars.append(
                    makeLShapeRebar(
                        f_cover_of_xdir_rebars,
                        xdir_rebars_b_offset,
                        l_cover_list[j][i],
                        r_cover_list[j][i],
                        dia,
                        xdir_rebars_t_offset,
                        l_xdir_rebar_rounding,
                        True,
                        number,
                        orientation,
                        structure,
                        facename_for_xdir_rebars,
                    )
                )
                xdir_rebars[-1].OffsetEnd = rear_cover_of_xdir_rebars + dia / 2
                f_cover_of_xdir_rebars += (
                    number * dia + number * spacing_in_xdir_rebars
                )
    return xdir_rebars


def makeYDirRebars(
    l_cover_of_tie,
    r_cover_of_tie,
    t_cover_of_tie,
    b_cover_of_tie,
    dia_of_tie,
    dia_of_main_rebars,
    ydir_rebars_t_offset,
    ydir_rebars_b_offset,
    ydir_rebars_type,
    ydir_hook_orientation,
    ydir_hook_extension,
    l_ydir_rebar_rounding,
    ydir_rebars_number_diameter,
    facename,
    structure,
):
    """Adds the rebars along y-direction to the structural column object."""
    ydir_rebars = []
    facename_for_ydir_rebars = getFacenameforRebar(
        "x-axis", facename, structure
    )

    # Find parameters of selected face
    FacePRM = getParametersOfFace(structure, facename)

    # find list of tuples of number and diameter of ydir rebars
    ydir_rebars_number_diameter_list = gettupleOfNumberDiameter(
        ydir_rebars_number_diameter
    )

    # Calculate spacing between ydir-rebars
    ydir_span_length = (
        FacePRM[0][1]
        - t_cover_of_tie
        - b_cover_of_tie
        - 2 * dia_of_tie
        - 2 * dia_of_main_rebars
    )
    req_space_for_ydir_rebars = sum(
        x[0] * x[1] for x in ydir_rebars_number_diameter_list
    )
    ydir_rebars_number = sum(
        number for number, _ in ydir_rebars_number_diameter_list
    )
    spacing_in_ydir_rebars = (ydir_span_length - req_space_for_ydir_rebars) / (
        ydir_rebars_number + 1
    )

    # Set parameter values for Straight/LShape ydir_rebars
    list_coverAlong = ["Right Side", "Left Side"]

    if ydir_rebars_type == "StraightRebar":
        # Set parameter values for Straight ydir_rebars
        r_cover = r_cover_of_tie + dia_of_tie
        l_cover = l_cover_of_tie + dia_of_tie
        rl_cover = [r_cover, l_cover]

        # Create Straight rebars along y-direction
        for i, coverAlong in enumerate(list_coverAlong):
            for j, (number, dia) in enumerate(ydir_rebars_number_diameter_list):
                if j == 0:
                    f_cover_of_ydir_rebars = (
                        b_cover_of_tie
                        + dia_of_tie
                        + dia_of_main_rebars
                        + spacing_in_ydir_rebars
                    )
                rear_cover_of_ydir_rebars = (
                    FacePRM[0][1]
                    - f_cover_of_ydir_rebars
                    - number * dia
                    - (number - 1) * spacing_in_ydir_rebars
                )

                ydir_rebars.append(
                    makeStraightRebar(
                        f_cover_of_ydir_rebars,
                        (coverAlong, rl_cover[i]),
                        ydir_rebars_t_offset,
                        ydir_rebars_b_offset,
                        dia,
                        True,
                        number,
                        "Vertical",
                        structure,
                        facename_for_ydir_rebars,
                    )
                )
                ydir_rebars[-1].OffsetEnd = rear_cover_of_ydir_rebars + dia / 2
                f_cover_of_ydir_rebars += (
                    number * dia + number * spacing_in_ydir_rebars
                )
    elif ydir_rebars_type == "LShapeRebar":
        face_length = getParametersOfFace(structure, facename_for_ydir_rebars)[
            0
        ][0]
        l_rebar_orientation_cover_list = []
        for i, (number, dia_of_rebars) in enumerate(
            ydir_rebars_number_diameter_list
        ):
            l_rebar_orientation_cover_list.append(
                getLRebarOrientationLeftRightCover(
                    ydir_hook_orientation,
                    ydir_hook_extension,
                    "x-axis",
                    l_cover_of_tie,
                    r_cover_of_tie,
                    t_cover_of_tie,
                    b_cover_of_tie,
                    dia_of_tie,
                    dia_of_rebars,
                    l_ydir_rebar_rounding,
                    face_length,
                )
            )
        list_orientation = l_rebar_orientation_cover_list[0]["list_orientation"]
        l_cover_list = []
        for l_rebar_orientation_cover in l_rebar_orientation_cover_list:
            l_cover_list.append(l_rebar_orientation_cover["l_cover"])

        r_cover_list = []
        for l_rebar_orientation_cover in l_rebar_orientation_cover_list:
            r_cover_list.append(l_rebar_orientation_cover["r_cover"])

        # Create LShape rebars along y-direction
        for i, orientation in enumerate(list_orientation):
            for j, (number, dia) in enumerate(ydir_rebars_number_diameter_list):
                if j == 0:
                    f_cover_of_ydir_rebars = (
                        r_cover_of_tie
                        + dia_of_tie
                        + dia_of_main_rebars
                        + spacing_in_ydir_rebars
                    )
                rear_cover_of_ydir_rebars = (
                    FacePRM[0][1]
                    - f_cover_of_ydir_rebars
                    - number * dia
                    - (number - 1) * spacing_in_ydir_rebars
                )
                ydir_rebars.append(
                    makeLShapeRebar(
                        f_cover_of_ydir_rebars,
                        ydir_rebars_b_offset,
                        l_cover_list[j][i],
                        r_cover_list[j][i],
                        dia,
                        ydir_rebars_t_offset,
                        l_ydir_rebar_rounding,
                        True,
                        number,
                        orientation,
                        structure,
                        facename_for_ydir_rebars,
                    )
                )
                ydir_rebars[-1].OffsetEnd = rear_cover_of_ydir_rebars + dia / 2
                f_cover_of_ydir_rebars += (
                    number * dia + number * spacing_in_ydir_rebars
                )
    return ydir_rebars


def editSingleTieMultipleRebars(
    rebar_group,
    l_cover_of_tie,
    r_cover_of_tie,
    t_cover_of_tie,
    b_cover_of_tie,
    offset_of_tie,
    bent_angle,
    extension_factor,
    dia_of_tie,
    number_spacing_check,
    number_spacing_value,
    dia_of_main_rebars,
    main_rebars_t_offset,
    main_rebars_b_offset,
    main_rebars_type="StraightRebar",
    main_hook_orientation="Top Inside",
    main_hook_extend_along="x-axis",
    l_main_rebar_rounding=None,
    main_hook_extension=None,
    sec_rebars_t_offset=None,
    sec_rebars_b_offset=None,
    sec_rebars_number_diameter=None,
    sec_rebars_type=("StraightRebar", "StraightRebar"),
    sec_hook_orientation=("Top Inside", "Top Inside"),
    l_sec_rebar_rounding=None,
    sec_hook_extension=None,
    structure=None,
    facename=None,
):
    """editSingleTieMultipleRebars(RebarGroup, LeftCoverOfTie, RightCoverOfTie,
    TopCoverOfTie, BottomCoverOfTie, OffsetofTie, BentAngle, ExtensionFactor,
    DiameterOfTie, NumberSpacingCheck, NumberSpacingValue, DiameterOfMainRebars,
    TopOffsetofMainRebars, BottomOffsetofMainRebars, MainRebarType,
    MainLShapeHookOrientation, MainLShapeHookExtendAlong,
    LShapeMainRebarRounding, LShapeMainHookLength, TopOffsetofSecondaryRebars,
    BottomOffsetofSecondaryRebars, SecondaryRebarNumberDiameterString,
    SecondaryRebarType, SecondaryLShapeHookOrientation,
    LShapeSecondaryRebarRounding, LShapeSecondaryHookLength, Structure,
    Facename):
    Edit the Single Tie Multiple Rebars reinforcement for the selected
    structural column object.

    It takes two different inputs for main_rebars_type i.e. 'StraightRebar',
    'LShapeRebar'.

    It takes eight different orientations input for Main L-shaped hooks i.e.
    'Top Inside', 'Top Outside', 'Bottom Inside', 'Bottom Outside', 'Top Left',
    'Top Right', 'Bottom Left', 'Bottom Right'.

    It takes two different inputs for main_hook_extend_along i.e. 'x-axis',
    'y-axis'.

    Note: Type of sec_rebars_t_offset, sec_rebars_b_offset,
    sec_rebars_number_diameter, sec_rebars_type, sec_hook_orientation,
    l_sec_rebar_rounding and sec_hook_extension argumants is a tuple.
    Syntax: (<value_for_xdir_rebars>, <value_for_ydir_rebars>).

    In sec_hook_orientation(<xdir_rebars_orientation>,
    <ydir_rebars_orientation>),
    Value of xdir_rebars_orientation can be: 'Top Inside', 'Top Outside',
    'Bottom Inside', 'Bottom Outside', 'Top Upward', 'Top Downward', 'Bottom
    Upward', 'Bottom Downward'.
    Value of ydir_rebars_orientation can be: 'Top Inside', 'Top Outside',
    'Bottom Inside', 'Bottom Outside', 'Top Left', 'Top Right', 'Bottom
    Left', 'Bottom Right'.
    """
    if len(rebar_group.RebarGroups) == 0:
        return rebar_group
    for i, tmp_rebar_group in enumerate(rebar_group.RebarGroups):
        if hasattr(tmp_rebar_group, "Ties"):
            if len(tmp_rebar_group.Ties) > 0:
                Tie = tmp_rebar_group.Ties[0]
                break
            else:
                print(
                    "You have deleted ties. Please recreate the"
                    "ColumnReinforcement."
                )
                return rebar_group
        elif i == len(rebar_group.RebarGroups) - 1:
            print(
                "You have deleted ties group. Please recreate the"
                "ColumnReinforcement."
            )
            return rebar_group

    if not structure and not facename:
        structure = Tie.Base.Support[0][0]
        facename = Tie.Base.Support[0][1][0]

    # Edit ties and main rebars
    editSingleTieFourRebars(
        rebar_group,
        l_cover_of_tie,
        r_cover_of_tie,
        t_cover_of_tie,
        b_cover_of_tie,
        offset_of_tie,
        bent_angle,
        extension_factor,
        dia_of_tie,
        number_spacing_check,
        number_spacing_value,
        dia_of_main_rebars,
        main_rebars_t_offset,
        main_rebars_b_offset,
        main_rebars_type,
        main_hook_orientation,
        main_hook_extend_along,
        l_main_rebar_rounding,
        main_hook_extension,
        structure,
        facename,
    )

    if len(rebar_group.RebarGroups) == 3:
        # Set parameters for xdir and ydir rebars
        xdir_rebars_group = rebar_group.RebarGroups[2].SecondaryRebars[0]
        ydir_rebars_group = rebar_group.RebarGroups[2].SecondaryRebars[1]
        if not sec_rebars_t_offset:
            xdir_rebars_t_offset = xdir_rebars_group.TopOffset
            ydir_rebars_t_offset = ydir_rebars_group.TopOffset
        else:
            xdir_rebars_t_offset = sec_rebars_t_offset[0]
            ydir_rebars_t_offset = sec_rebars_t_offset[1]
        if not sec_rebars_b_offset:
            xdir_rebars_b_offset = xdir_rebars_group.BottomOffset
            ydir_rebars_b_offset = ydir_rebars_group.BottomOffset
        else:
            xdir_rebars_b_offset = sec_rebars_b_offset[0]
            ydir_rebars_b_offset = sec_rebars_b_offset[1]
        if not sec_rebars_number_diameter:
            xdir_rebars_number_diameter = xdir_rebars_group.NumberDiameter
            ydir_rebars_number_diameter = ydir_rebars_group.NumberDiameter
        else:
            xdir_rebars_number_diameter = sec_rebars_number_diameter[0]
            ydir_rebars_number_diameter = sec_rebars_number_diameter[1]
    else:
        # Set parameters for xdir and ydir rebars
        if not sec_rebars_t_offset:
            xdir_rebars_t_offset = "0.00 mm"
            ydir_rebars_t_offset = "0.00 mm"
        else:
            xdir_rebars_t_offset = sec_rebars_t_offset[0]
            ydir_rebars_t_offset = sec_rebars_t_offset[1]
        if not sec_rebars_b_offset:
            xdir_rebars_b_offset = "0.00 mm"
            ydir_rebars_b_offset = "0.00 mm"
        else:
            xdir_rebars_b_offset = sec_rebars_b_offset[0]
            ydir_rebars_b_offset = sec_rebars_b_offset[1]
        if not sec_rebars_number_diameter:
            xdir_rebars_number_diameter = "2#20mm+1#16mm+2#20mm"
            ydir_rebars_number_diameter = "1#20mm+1#16mm+1#20mm"
        else:
            xdir_rebars_number_diameter = sec_rebars_number_diameter[0]
            ydir_rebars_number_diameter = sec_rebars_number_diameter[1]
    xdir_rebars_type = sec_rebars_type[0]
    ydir_rebars_type = sec_rebars_type[1]
    xdir_hook_orientation = sec_hook_orientation[0]
    ydir_hook_orientation = sec_hook_orientation[1]
    if l_sec_rebar_rounding:
        l_xdir_rebar_rounding = l_sec_rebar_rounding[0]
        l_ydir_rebar_rounding = l_sec_rebar_rounding[1]
    if sec_hook_extension:
        xdir_hook_extension = sec_hook_extension[0]
        ydir_hook_extension = sec_hook_extension[1]

    # Set common parameters of xdir and ydir rebars
    xdir_rebars = xdir_rebars_group.XDirRebars
    ydir_rebars = ydir_rebars_group.YDirRebars

    # Delete previously created xdir rebars
    for Rebar in xdir_rebars:
        base_name = Rebar.Base.Name
        FreeCAD.ActiveDocument.removeObject(Rebar.Name)
        FreeCAD.ActiveDocument.removeObject(base_name)
    FreeCAD.ActiveDocument.recompute()

    if xdir_rebars_number_diameter and xdir_rebars_number_diameter != "0":
        xdir_rebars = makeXDirRebars(
            l_cover_of_tie,
            r_cover_of_tie,
            t_cover_of_tie,
            b_cover_of_tie,
            dia_of_tie,
            dia_of_main_rebars,
            xdir_rebars_t_offset,
            xdir_rebars_b_offset,
            xdir_rebars_type,
            xdir_hook_orientation,
            xdir_hook_extension,
            l_xdir_rebar_rounding,
            xdir_rebars_number_diameter,
            facename,
            structure,
        )

    # Delete previously created ydir rebars
    for Rebar in ydir_rebars:
        base_name = Rebar.Base.Name
        FreeCAD.ActiveDocument.removeObject(Rebar.Name)
        FreeCAD.ActiveDocument.removeObject(base_name)
    FreeCAD.ActiveDocument.recompute()

    if ydir_rebars_number_diameter and ydir_rebars_number_diameter != "0":
        ydir_rebars = makeYDirRebars(
            l_cover_of_tie,
            r_cover_of_tie,
            t_cover_of_tie,
            b_cover_of_tie,
            dia_of_tie,
            dia_of_main_rebars,
            ydir_rebars_t_offset,
            ydir_rebars_b_offset,
            ydir_rebars_type,
            ydir_hook_orientation,
            ydir_hook_extension,
            l_ydir_rebar_rounding,
            ydir_rebars_number_diameter,
            facename,
            structure,
        )
    FreeCAD.ActiveDocument.recompute()

    # Add created xdir/ydir rebars to xdir_rebars_group/ydir_rebars_group
    xdir_rebars_group.addObjects(xdir_rebars)
    ydir_rebars_group.addObjects(ydir_rebars)

    # Set properties values for xdir_rebars in  xdir_rebars_group object
    xdir_rebars_group.XDirRebars = xdir_rebars
    xdir_rebars_group.RebarType = xdir_rebars_type
    if xdir_rebars_type == "LShapeRebar":
        xdir_rebars_group.HookOrientation = xdir_hook_orientation
        xdir_rebars_group.HookExtension = xdir_hook_extension
    xdir_rebars_group.TopOffset = xdir_rebars_t_offset
    xdir_rebars_group.BottomOffset = xdir_rebars_b_offset
    xdir_rebars_group.NumberDiameter = xdir_rebars_number_diameter

    # Set properties values for ydir_rebars in  ydir_rebars_group object
    ydir_rebars_group.YDirRebars = ydir_rebars
    ydir_rebars_group.RebarType = ydir_rebars_type
    if ydir_rebars_type == "LShapeRebar":
        ydir_rebars_group.HookOrientation = ydir_hook_orientation
        ydir_rebars_group.HookExtension = ydir_hook_extension
    ydir_rebars_group.TopOffset = ydir_rebars_t_offset
    ydir_rebars_group.BottomOffset = ydir_rebars_b_offset
    ydir_rebars_group.NumberDiameter = ydir_rebars_number_diameter

    FreeCAD.ActiveDocument.recompute()
    return rebar_group


class _SingleTieMultipleRebars:
    def __init__(self, obj):
        """Add properties to object obj."""
        self.Object = obj.rebar_group
        self.sec_rebars_group = self.Object.newObject(
            "App::DocumentObjectGroupPython", "SecondaryRebars"
        )
        self.xdir_rebars_group = self.sec_rebars_group.newObject(
            "App::DocumentObjectGroupPython", "XDirRebars"
        )
        self.ydir_rebars_group = self.sec_rebars_group.newObject(
            "App::DocumentObjectGroupPython", "YDirRebars"
        )
        # Add secondary rebars group object to list of rebars groups of rebar
        # group object
        prev_rebar_groups = obj.rebar_group.RebarGroups
        prev_rebar_groups.append(self.sec_rebars_group)
        obj.rebar_group.RebarGroups = prev_rebar_groups
        # Add and set properties for secondary rebars group object
        properties = []
        properties.append(
            (
                "App::PropertyLinkList",
                "SecondaryRebars",
                "List of secondary rebars",
                1,
            )
        )
        obj.setProperties(properties, self.sec_rebars_group)
        self.sec_rebars_group.SecondaryRebars = [
            self.xdir_rebars_group,
            self.ydir_rebars_group,
        ]
        # Add properties to xdir rebars group object
        properties = []
        properties.append(
            ("App::PropertyLinkList", "XDirRebars", "List of xdir rebars", 1)
        )
        properties.append(
            ("App::PropertyString", "RebarType", "Type of xdir rebars", 1)
        )
        properties.append(
            (
                "App::PropertyString",
                "HookOrientation",
                "Orientation of LShaped Rebar Hook",
                1,
            )
        )
        properties.append(
            ("App::PropertyDistance", "HookExtension", "Length of hook", 1)
        )
        properties.append(
            (
                "App::PropertyDistance",
                "TopOffset",
                "Top offset of xdir rebars",
                1,
            )
        )
        properties.append(
            (
                "App::PropertyDistance",
                "BottomOffset",
                "Bottom offset of xdir rebars",
                1,
            )
        )
        properties.append(
            (
                "App::PropertyString",
                "NumberDiameter",
                "Number Diameter list of rebars",
                1,
            )
        )
        obj.setProperties(properties, self.xdir_rebars_group)
        # Add properties to ydir rebars group object
        properties = []
        properties.append(
            ("App::PropertyLinkList", "YDirRebars", "List of ydir rebars", 1)
        )
        properties.append(
            ("App::PropertyString", "RebarType", "Type of ydir rebars", 1)
        )
        properties.append(
            (
                "App::PropertyString",
                "HookOrientation",
                "Orientation of LShaped Rebar Hook",
                1,
            )
        )
        properties.append(
            ("App::PropertyDistance", "HookExtension", "Length of hook", 1)
        )
        properties.append(
            (
                "App::PropertyDistance",
                "TopOffset",
                "Top offset of ydir rebars",
                1,
            )
        )
        properties.append(
            (
                "App::PropertyDistance",
                "BottomOffset",
                "Bottom offset of ydir rebars",
                1,
            )
        )
        properties.append(
            (
                "App::PropertyString",
                "NumberDiameter",
                "Number Diameter list of rebars",
                1,
            )
        )
        obj.setProperties(properties, self.ydir_rebars_group)

    def addXDirRebars(self, xdir_rebars_list):
        """Add XDir Rebars to xdir_rebars group object."""
        self.xdir_rebars_group.addObjects(xdir_rebars_list)
        prev_xdir_rebars_list = self.xdir_rebars_group.XDirRebars
        xdir_rebars_list.extend(prev_xdir_rebars_list)
        self.xdir_rebars_group.XDirRebars = xdir_rebars_list

    def addYDirRebars(self, ydir_rebars_list):
        """Add YDir Rebars to ydir_rebars group object."""
        self.ydir_rebars_group.addObjects(ydir_rebars_list)
        prev_ydir_rebars_list = self.ydir_rebars_group.YDirRebars
        ydir_rebars_list.extend(prev_ydir_rebars_list)
        self.ydir_rebars_group.YDirRebars = ydir_rebars_list
