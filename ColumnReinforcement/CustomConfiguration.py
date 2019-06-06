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

__title__ = "Custom Column Reinforcement"
__author__ = "Suraj"
__url__ = "https://www.freecadweb.org"


import FreeCAD

from .SingleTie import makeSingleTieFourRebars, getFacenameforRebar
from StraightRebar import makeStraightRebar
from Rebarfunc import getParametersOfFace, gettupleOfNumberDiameter

if FreeCAD.GuiUp:
    import FreeCADGui


def makeCustomColumnReinforcement(
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
    t_offset_of_main_rebars,
    b_offset_of_main_rebars,
    main_rebar_type="StraightRebar",
    main_hook_orientation="Top Inside",
    main_hook_extend_along="x-axis",
    l_main_rebar_rounding=None,
    main_hook_extension=None,
    t_offset_of_sec_rebars=None,
    b_offset_of_sec_rebars=None,
    sec_rebars_number_diameter=None,
    sec_rebar_type=("StraightRebar", "StraightRebar"),
    sec_hook_orientation=("Top Inside", "Top Inside"),
    l_sec_rebar_rounding=None,
    sec_hook_extension=None,
    structure=None,
    facename=None,
):
    """makeCustomColumnReinforcement(LeftCoverOfTie, RightCoverOfTie,
    TopCoverOfTie, BottomCoverOfTie, OffsetofTie, BentAngle, ExtensionFactor,
    DiameterOfTie, NumberSpacingCheck, NumberSpacingValue, DiameterOfMainRebars,
    TopOffsetofMainRebars, BottomOffsetofMainRebars, MainRebarType,
    MainLShapeHookOrientation, MainLShapeHookExtendAlong,
    LShapeMainRebarRounding, LShapeMainHookLength, TopOffsetofSecondaryRebars,
    BottomOffsetofSecondaryRebars, SecondaryRebarNumberDiameterString,
    SecondaryRebarType, SecondaryLShapeHookOrientation, LShapeSecondaryRebarRounding,
    LShapeSecondaryHookLength, Structure, Facename):
    Adds the Custom Reinforcement to the selected structural column object.
    It takes two different inputs for main_rebar_type i.e. 'StraightRebar',
    'LShapeRebar'.
    It takes eight different orientations input for Main L-shaped hooks i.e.
    'Top Inside', 'Top Outside', 'Bottom Inside', 'Bottom Outside', 'Top Left',
    'Top Right', 'Bottom Left', 'Bottom Right'.
    It takes two different inputs for main_hook_extend_along i.e. 'x-axis', 'y-axis'.
    Note: Type of t_offset_of_sec_rebars, b_offset_of_sec_rebars,
    sec_rebars_number_diameter, sec_rebar_type, sec_hook_orientation,
    l_sec_rebar_rounding and sec_hook_extension argumants is a tuple.
    Syntax: (<value_for_xdir_rebars>, <value_for_ydir_rebars>).
    """
    # Get structure and facename
    if not structure and not facename:
        if FreeCAD.GuiUp:
            selected_obj = FreeCADGui.Selection.getSelectionEx()[0]
            structure = selected_obj.Object
            facename = selected_obj.SubElementNames[0]
        else:
            print("Error: Pass structure and facename arguments")
            return None

    # Set parameters for xdir and ydir rebars
    if not t_offset_of_sec_rebars:
        t_offset_of_xdir_rebars = (
            t_offset_of_ydir_rebars
        ) = t_offset_of_main_rebars
    else:
        t_offset_of_xdir_rebars = t_offset_of_sec_rebars[0]
        t_offset_of_ydir_rebars = t_offset_of_sec_rebars[1]
    if not b_offset_of_sec_rebars:
        b_offset_of_xdir_rebars = (
            b_offset_of_ydir_rebars
        ) = b_offset_of_main_rebars
    else:
        b_offset_of_xdir_rebars = b_offset_of_sec_rebars[0]
        b_offset_of_ydir_rebars = b_offset_of_sec_rebars[1]
    if not sec_rebars_number_diameter:
        xdir_rebars_number_diameter = None
        ydir_rebars_number_diameter = None
    else:
        xdir_rebars_number_diameter = sec_rebars_number_diameter[0]
        ydir_rebars_number_diameter = sec_rebars_number_diameter[1]
    xdir_rebar_type = sec_rebar_type[0]
    ydir_rebar_type = sec_rebar_type[1]
    xdir_hook_orientation = sec_hook_orientation[0]
    ydir_hook_orientation = sec_hook_orientation[1]
    if l_sec_rebar_rounding:
        l_xdir_rebar_rounding = l_sec_rebar_rounding[0]
        l_ydir_rebar_rounding = l_sec_rebar_rounding[1]
    if sec_hook_extension:
        xdir_hook_extension = sec_hook_extension[0]
        ydir_hook_extension = sec_hook_extension[1]

    # Find facename for xdir and ydir rebars
    facename_for_xdir_rebars = getFacenameforRebar(
        "y-axis", facename, structure
    )
    facename_for_ydir_rebars = getFacenameforRebar(
        "x-axis", facename, structure
    )

    # Create SingleTieFourRebars
    SingleTieFourRebarsGroup = makeSingleTieFourRebars(
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
        t_offset_of_main_rebars,
        b_offset_of_main_rebars,
        main_rebar_type,
        main_hook_orientation,
        main_hook_extend_along,
        l_main_rebar_rounding,
        main_hook_extension,
        structure,
        facename,
        ColumnConfiguration="CustomColumnReinforcement",
    )

    if xdir_rebars_number_diameter:
        # find list of tuples of number and diameter of xdir rebars
        xdir_rebars_number_diameter_list = gettupleOfNumberDiameter(
            xdir_rebars_number_diameter
        )
        xdir_rebars_number_diameter_list.reverse()

        FacePRM = getParametersOfFace(structure, facename)
        # Calculate spacing between xdir-rebars
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
        spacing_in_xdir_rebars = (
            xdir_span_length - req_space_for_xdir_rebars
        ) / (xdir_rebars_number + 1)

        # Set parameter values for xdir_rebars
        list_coverAlong = ["Right Side", "Left Side"]
        r_cover = t_cover_of_tie + dia_of_tie
        l_cover = b_cover_of_tie + dia_of_tie
        rl_cover = [r_cover, l_cover]
        orientation = "Vertical"

        xdir_rebars = []

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
                        t_offset_of_xdir_rebars,
                        b_offset_of_xdir_rebars,
                        dia,
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

    if ydir_rebars_number_diameter:
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
        spacing_in_ydir_rebars = (
            ydir_span_length - req_space_for_ydir_rebars
        ) / (ydir_rebars_number + 1)

        # Set parameter values for ydir_rebars
        list_coverAlong = ["Right Side", "Left Side"]
        r_cover = r_cover_of_tie + dia_of_tie
        l_cover = l_cover_of_tie + dia_of_tie
        rl_cover = [r_cover, l_cover]
        orientation = "Vertical"

        ydir_rebars = []

        # Create Straight rebars along x-direction
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
                        t_offset_of_ydir_rebars,
                        b_offset_of_ydir_rebars,
                        dia,
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
    FreeCAD.ActiveDocument.recompute()
