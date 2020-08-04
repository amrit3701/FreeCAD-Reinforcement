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

__title__ = "Single Tie Reinforcement"
__author__ = "Suraj"
__url__ = "https://www.freecadweb.org"


import FreeCAD

from Stirrup import makeStirrup, editStirrup
from StraightRebar import makeStraightRebar, editStraightRebar
from LShapeRebar import makeLShapeRebar, editLShapeRebar
from Rebarfunc import (
    showWarning,
    getParametersOfFace,
    getFacenameforRebar,
    getLRebarOrientationLeftRightCover,
    setGroupProperties,
    setGroupPropertiesValues,
    _RebarGroup,
    _ViewProviderRebarGroup,
)

if FreeCAD.GuiUp:
    import FreeCADGui


def makeSingleTieFourRebars(
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
    dia_of_rebars,
    t_offset_of_rebars,
    b_offset_of_rebars,
    rebar_type="StraightRebar",
    hook_orientation="Top Inside",
    hook_extend_along="x-axis",
    l_rebar_rounding=None,
    hook_extension=None,
    structure=None,
    facename=None,
):
    """makeSingleTieFourRebars(LeftCoverOfTie, RightCoverOfTie, TopCoverOfTie,
    BottomCoverOfTie, OffsetofTie, BentAngle, ExtensionFactor, DiameterOfTie,
    NumberSpacingCheck, NumberSpacingValue, DiameterOfRebars, TopOffsetOfRebars,
    BottomOffsetOfRebars, RebarType, LShapeHookOrientation, HookExtendAlong,
    LShapeRebarRounding, LShapeHookLength, Structure, Facename):
    Adds the Single Tie Four Rebars reinforcement to the selected structural
    column object.
    It takes two different inputs for rebar_type i.e. 'StraightRebar',
    'LShapeRebar'.
    It takes eight different orientations input for L-shaped hooks i.e. 'Top
    Inside', 'Top Outside', 'Bottom Inside', 'Bottom Outside', 'Top Left',
    'Top Right', 'Bottom Left', 'Bottom Right'.
    It takes two different inputs for hook_extend_along i.e. 'x-axis', 'y-axis'.
    """
    if not structure and not facename:
        if FreeCAD.GuiUp:
            selected_obj = FreeCADGui.Selection.getSelectionEx()[0]
            structure = selected_obj.Object
            facename = selected_obj.SubElementNames[0]
        else:
            showWarning("Error: Pass structure and facename arguments")
            return None

    # Calculate common parameters for Straight/LShaped rebars
    t_cover = t_offset_of_rebars
    b_cover = b_offset_of_rebars
    rebar_number_spacing_check = True
    rebar_number_spacing_value = 2

    # Create Straight Rebars
    if rebar_type == "StraightRebar":
        facename_for_rebars = getFacenameforRebar(
            hook_extend_along, facename, structure
        )
        f_cover = b_cover_of_tie + dia_of_tie
        r_cover = r_cover_of_tie + dia_of_tie
        l_cover = l_cover_of_tie + dia_of_tie
        orientation = "Vertical"
        list_coverAlong = ["Right Side", "Left Side"]
        rl_cover = [r_cover, l_cover]

        main_rebars = []
        for i, coverAlong in enumerate(list_coverAlong):
            main_rebars.append(
                makeStraightRebar(
                    f_cover,
                    (coverAlong, rl_cover[i]),
                    t_cover,
                    b_cover,
                    dia_of_rebars,
                    rebar_number_spacing_check,
                    rebar_number_spacing_value,
                    orientation,
                    structure,
                    facename_for_rebars,
                )
            )
            main_rebars[i].OffsetEnd = (
                t_cover_of_tie + dia_of_tie + dia_of_rebars / 2
            )

    # Create L-Shaped Rebars
    elif rebar_type == "LShapeRebar":
        facename_for_rebars = getFacenameforRebar(
            hook_extend_along, facename, structure
        )
        FacePRM = getParametersOfFace(structure, facename_for_rebars)
        face_length = FacePRM[0][0]
        if hook_extend_along == "x-axis":
            f_cover = b_cover_of_tie + dia_of_tie
        else:
            f_cover = r_cover_of_tie + dia_of_tie
        # Implement hook extension values from here:
        # https://archive.org/details/gov.in.is.sp.16.1980/page/n207
        if not hook_extension:
            hook_extension = 4 * dia_of_rebars
        if not l_rebar_rounding:
            l_rebar_rounding = (
                float(dia_of_tie) / 2 + dia_of_rebars / 2
            ) / dia_of_tie
        l_rebar_orientation_cover = getLRebarOrientationLeftRightCover(
            hook_orientation,
            hook_extension,
            hook_extend_along,
            l_cover_of_tie,
            r_cover_of_tie,
            t_cover_of_tie,
            b_cover_of_tie,
            dia_of_tie,
            dia_of_rebars,
            l_rebar_rounding,
            face_length,
        )
        list_orientation = l_rebar_orientation_cover["list_orientation"]
        l_cover = l_rebar_orientation_cover["l_cover"]
        r_cover = l_rebar_orientation_cover["r_cover"]
        t_cover = t_offset_of_rebars
        b_cover = b_offset_of_rebars

        main_rebars = []
        for i, orientation in enumerate(list_orientation):
            main_rebars.append(
                makeLShapeRebar(
                    f_cover,
                    b_cover,
                    l_cover[i],
                    r_cover[i],
                    dia_of_rebars,
                    t_cover,
                    l_rebar_rounding,
                    rebar_number_spacing_check,
                    rebar_number_spacing_value,
                    orientation,
                    structure,
                    facename_for_rebars,
                )
            )
            if hook_extend_along == "x-axis":
                main_rebars[i].OffsetEnd = (
                    t_cover_of_tie + dia_of_tie + dia_of_rebars / 2
                )
            else:
                main_rebars[i].OffsetEnd = (
                    l_cover_of_tie + dia_of_tie + dia_of_rebars / 2
                )

    # Calculate parameters for Tie
    rounding = (float(dia_of_tie) / 2 + dia_of_rebars / 2) / dia_of_tie
    f_cover = offset_of_tie

    # Create Tie
    ties = makeStirrup(
        l_cover_of_tie,
        r_cover_of_tie,
        t_cover_of_tie,
        b_cover_of_tie,
        f_cover,
        bent_angle,
        extension_factor,
        dia_of_tie,
        rounding,
        number_spacing_check,
        number_spacing_value,
        structure,
        facename,
    )

    # Create SingleTieFourRebars group object
    SingleTieFourRebars = _SingleTieFourRebars()
    if FreeCAD.GuiUp:
        _ViewProviderRebarGroup(SingleTieFourRebars.Object.ViewObject)

    # Add created tie and rebars to SingleTieFourRebars group
    SingleTieFourRebars.addTies(ties)
    SingleTieFourRebars.addMainRebars(main_rebars)

    # Set properties values for ties in Ties group object
    properties_values = []
    properties_values.append(("TiesConfiguration", "SingleTie"))
    properties_values.append(("LeftCover", l_cover_of_tie))
    properties_values.append(("RightCover", r_cover_of_tie))
    properties_values.append(("TopCover", t_cover_of_tie))
    properties_values.append(("BottomCover", b_cover_of_tie))
    setGroupPropertiesValues(properties_values, SingleTieFourRebars.ties_group)

    # Set properties values for rebars in MainRebars group object
    properties_values = []
    properties_values.append(("RebarType", rebar_type))
    properties_values.append(("TopOffset", t_offset_of_rebars))
    properties_values.append(("BottomOffset", b_offset_of_rebars))
    properties_values.append(("HookOrientation", hook_orientation))
    properties_values.append(("HookExtendAlong", hook_extend_along))
    if not hook_extension:
        hook_extension = "0.00 mm"
    properties_values.append(("HookExtension", hook_extension))
    setGroupPropertiesValues(
        properties_values, SingleTieFourRebars.main_rebars_group
    )
    FreeCAD.ActiveDocument.recompute()
    return SingleTieFourRebars


def editSingleTieFourRebars(
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
    dia_of_rebars,
    t_offset_of_rebars,
    b_offset_of_rebars,
    rebar_type="StraightRebar",
    hook_orientation="Top Inside",
    hook_extend_along="x-axis",
    l_rebar_rounding=None,
    hook_extension=None,
    structure=None,
    facename=None,
):
    """editSingleTieFourRebars(RebarGroup, LeftCoverOfTie, RightCoverOfTie,
    TopCoverOfTie, BottomCoverOfTie, OffsetofTie, BentAngle, ExtensionFactor,
    DiameterOfTie, NumberSpacingCheck, NumberSpacingValue, DiameterOfRebars,
    TopOffsetofRebars, BottomOffsetofRebars, RebarType, LShapeHookOrientation,
    HookExtendAlong, LShapeRebarRounding, LShapeHookLength, Structure,
    Facename):
    Edit the Single Tie reinforcement for the selected structural column
    object.
    It takes two different inputs for rebar_type i.e. 'StraightRebar',
    'LShapeRebar'.
    It takes eight different orientations input for L-shaped hooks i.e. 'Top
    Inside', 'Top Outside', 'Bottom Inside', 'Bottom Outside', 'Top Left',
    'Top Right', 'Bottom Left', 'Bottom Right'.
    It takes two different inputs for hook_extend_along i.e. 'x-axis', 'y-axis'.
    """
    Tie = rebar_group.RebarGroups[0].Ties[0]
    prev_rebar_type = rebar_group.RebarGroups[1].MainRebars[0].RebarShape
    if not structure and not facename:
        structure = Tie.Base.Support[0][0]
        facename = Tie.Base.Support[0][1][0]

    # Check if main rebar_type changed or not
    if prev_rebar_type == rebar_type:
        change_rebar_type = False
    else:
        change_rebar_type = True

    # Edit Tie
    rounding = (float(dia_of_tie) / 2 + dia_of_rebars / 2) / dia_of_tie
    f_cover = offset_of_tie
    editStirrup(
        Tie,
        l_cover_of_tie,
        r_cover_of_tie,
        t_cover_of_tie,
        b_cover_of_tie,
        f_cover,
        bent_angle,
        extension_factor,
        dia_of_tie,
        rounding,
        number_spacing_check,
        number_spacing_value,
        structure,
        facename,
    )

    # Calculate common parameters for Straight/LShaped rebars
    t_cover = t_offset_of_rebars
    b_cover = b_offset_of_rebars
    rebar_number_spacing_check = True
    rebar_number_spacing_value = 2

    # Create/Edit Straight Rebars
    if rebar_type == "StraightRebar":
        hook_extend_along == "x-axis"
        facename_for_rebars = getFacenameforRebar(
            hook_extend_along, facename, structure
        )
        f_cover = b_cover_of_tie + dia_of_tie
        r_cover = r_cover_of_tie + dia_of_tie
        l_cover = l_cover_of_tie + dia_of_tie
        orientation = "Vertical"
        list_coverAlong = ["Right Side", "Left Side"]
        rl_cover = [r_cover, l_cover]

        if change_rebar_type:
            # Delete previously created LShaped rebars
            for Rebar in rebar_group.RebarGroups[1].MainRebars[:2]:
                base_name = Rebar.Base.Name
                FreeCAD.ActiveDocument.removeObject(Rebar.Name)
                FreeCAD.ActiveDocument.removeObject(base_name)
            main_rebars = []
            for i, coverAlong in enumerate(list_coverAlong):
                main_rebars.append(
                    makeStraightRebar(
                        f_cover,
                        (coverAlong, rl_cover[i]),
                        t_cover,
                        b_cover,
                        dia_of_rebars,
                        rebar_number_spacing_check,
                        rebar_number_spacing_value,
                        orientation,
                        structure,
                        facename_for_rebars,
                    )
                )
                main_rebars[i].OffsetEnd = (
                    t_cover_of_tie + dia_of_tie + dia_of_rebars / 2
                )
            rebar_group.RebarGroups[1].addObjects(main_rebars)
        else:
            main_rebars = []
            for Rebar in rebar_group.RebarGroups[1].MainRebars[:2]:
                main_rebars.append(Rebar)
            for i, coverAlong in enumerate(list_coverAlong):
                editStraightRebar(
                    main_rebars[i],
                    f_cover,
                    (coverAlong, rl_cover[i]),
                    t_cover,
                    b_cover,
                    dia_of_rebars,
                    rebar_number_spacing_check,
                    rebar_number_spacing_value,
                    orientation,
                    structure,
                    facename_for_rebars,
                )
                main_rebars[i].OffsetEnd = (
                    t_cover_of_tie + dia_of_tie + dia_of_rebars / 2
                )

    # Create L-Shaped Rebars
    elif rebar_type == "LShapeRebar":
        facename_for_rebars = getFacenameforRebar(
            hook_extend_along, facename, structure
        )
        FacePRM = getParametersOfFace(structure, facename_for_rebars)
        face_length = FacePRM[0][0]
        if hook_extend_along == "x-axis":
            f_cover = b_cover_of_tie + dia_of_tie
        else:
            f_cover = r_cover_of_tie + dia_of_tie
        # Implement hook extension values from here:
        # https://archive.org/details/gov.in.is.sp.16.1980/page/n207
        if not hook_extension:
            hook_extension = 4 * dia_of_rebars
        if not l_rebar_rounding:
            l_rebar_rounding = (
                float(dia_of_tie) / 2 + dia_of_rebars / 2
            ) / dia_of_tie
        l_rebar_orientation_cover = getLRebarOrientationLeftRightCover(
            hook_orientation,
            hook_extension,
            hook_extend_along,
            l_cover_of_tie,
            r_cover_of_tie,
            t_cover_of_tie,
            b_cover_of_tie,
            dia_of_tie,
            dia_of_rebars,
            l_rebar_rounding,
            face_length,
        )
        list_orientation = l_rebar_orientation_cover["list_orientation"]
        l_cover = l_rebar_orientation_cover["l_cover"]
        r_cover = l_rebar_orientation_cover["r_cover"]
        t_cover = t_offset_of_rebars
        b_cover = b_offset_of_rebars

        if change_rebar_type:
            # Delete previously created Straight rebars
            for Rebar in rebar_group.RebarGroups[1].MainRebars[:2]:
                base_name = Rebar.Base.Name
                FreeCAD.ActiveDocument.removeObject(Rebar.Name)
                FreeCAD.ActiveDocument.removeObject(base_name)
            main_rebars = []
            for i, orientation in enumerate(list_orientation):
                main_rebars.append(
                    makeLShapeRebar(
                        f_cover,
                        b_cover,
                        l_cover[i],
                        r_cover[i],
                        dia_of_rebars,
                        t_cover,
                        l_rebar_rounding,
                        rebar_number_spacing_check,
                        rebar_number_spacing_value,
                        orientation,
                        structure,
                        facename_for_rebars,
                    )
                )
                if hook_extend_along == "x-axis":
                    main_rebars[i].OffsetEnd = (
                        t_cover_of_tie + dia_of_tie + dia_of_rebars / 2
                    )
                else:
                    main_rebars[i].OffsetEnd = (
                        l_cover_of_tie + dia_of_tie + dia_of_rebars / 2
                    )
            rebar_group.RebarGroups[1].addObjects(main_rebars)
        else:
            main_rebars = []
            for Rebar in rebar_group.RebarGroups[1].MainRebars[:2]:
                main_rebars.append(Rebar)
            for i, orientation in enumerate(list_orientation):
                editLShapeRebar(
                    main_rebars[i],
                    f_cover,
                    b_cover,
                    l_cover[i],
                    r_cover[i],
                    dia_of_rebars,
                    t_cover,
                    l_rebar_rounding,
                    rebar_number_spacing_check,
                    rebar_number_spacing_value,
                    orientation,
                    structure,
                    facename_for_rebars,
                )
                if hook_extend_along == "x-axis":
                    main_rebars[i].OffsetEnd = (
                        t_cover_of_tie + dia_of_tie + dia_of_rebars / 2
                    )
                else:
                    main_rebars[i].OffsetEnd = (
                        l_cover_of_tie + dia_of_tie + dia_of_rebars / 2
                    )

    # Set properties values for ties in ties_group object
    ties_group = rebar_group.RebarGroups[0]
    ties_group.LeftCover = l_cover_of_tie
    ties_group.RightCover = r_cover_of_tie
    ties_group.TopCover = t_cover_of_tie
    ties_group.BottomCover = b_cover_of_tie

    # Set properties values for main_rebars in main_rebars_group object
    main_rebars_group = rebar_group.RebarGroups[1]
    main_rebars_group.MainRebars = main_rebars
    main_rebars_group.RebarType = rebar_type
    main_rebars_group.TopOffset = t_offset_of_rebars
    main_rebars_group.BottomOffset = b_offset_of_rebars
    main_rebars_group.HookOrientation = hook_orientation
    main_rebars_group.HookExtendAlong = hook_extend_along
    if not hook_extension:
        hook_extension = "0.00 mm"
    main_rebars_group.HookExtension = hook_extension

    FreeCAD.ActiveDocument.recompute()
    return rebar_group


class _SingleTieFourRebars(_RebarGroup):
    "A SingleTieFourRebars group object."

    def __init__(self):
        """Create Group object and add properties to it."""
        _RebarGroup.__init__(self, "ColumnReinforcement")
        # Add properties to group of rebars
        # Syntax to add new property:
        # properties.append(
        #     (
        #         "<property_type>",
        #         "<property_name>",
        #         "<property_description>",
        #         "<property_value>",
        #         "<property_editor_mode>",
        #     )
        #
        # property_editor_mode:
        # 0 -- read and write mode
        # 1 -- read-only mode
        # 2 -- hidden mode

        properties = []
        properties.append(
            (
                "App::PropertyString",
                "ColumnType",
                "Type of column reinforcement",
                1,
            )
        )
        setGroupProperties(properties, self.rebar_group)
        self.rebar_group.ColumnType = "RectangularColumn"

        # Add properties to ties group object
        properties = []
        properties.append(
            (
                "App::PropertyString",
                "TiesConfiguration",
                "Configuration of Ties in Column Reinforcement",
                1,
            )
        )
        properties.append(("App::PropertyLinkList", "Ties", "List of ties", 1))
        properties.append(
            ("App::PropertyDistance", "LeftCover", "Left cover of ties", 1)
        )
        properties.append(
            ("App::PropertyDistance", "RightCover", "Right cover of ties", 1)
        )
        properties.append(
            ("App::PropertyDistance", "TopCover", "Top cover of ties", 1)
        )
        properties.append(
            ("App::PropertyDistance", "BottomCover", "Bottom cover of ties", 1)
        )
        setGroupProperties(properties, self.ties_group)

        # Add properties to main rebars group object
        properties = []
        properties.append(
            ("App::PropertyString", "RebarType", "Type of main rebars", 1)
        )
        properties.append(
            ("App::PropertyLinkList", "MainRebars", "List of main rebars", 1)
        )
        properties.append(
            ("App::PropertyDistance", "TopOffset", "Top offset of rebars", 1)
        )
        properties.append(
            (
                "App::PropertyDistance",
                "BottomOffset",
                "Bottom offset of rebars",
                1,
            )
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
            (
                "App::PropertyString",
                "HookExtendAlong",
                "Direction of hook extension",
                1,
            )
        )
        properties.append(
            ("App::PropertyDistance", "HookExtension", "Length of hook", 1)
        )
        setGroupProperties(properties, self.main_rebars_group)
