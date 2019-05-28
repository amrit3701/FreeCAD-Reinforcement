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

from Stirrup import makeStirrup
from StraightRebar import makeStraightRebar
from LShapeRebar import makeLShapeRebar
from Rebarfunc import (
    getParametersOfFace,
    getFaceNumber,
    _RebarGroup,
    _ViewProviderRebarGroup,
)

if FreeCAD.GuiUp:
    import FreeCADGui


def getLRebarOrientationLeftRightCover(
    hook_orientation,
    hook_extension,
    hook_extend_along,
    l_cover_of_tie,
    r_cover_of_tie,
    t_cover_of_tie,
    b_cover_of_tie,
    dia_of_tie,
    dia_of_rebars,
    rounding_of_rebars,
    face_length,
):
    """getLRebarOrientationLeftRightCover(HookOrientation, HookExtension,
    HookExtendAlong, LeftCoverOfTie, RightCoverOfTie, TopCoverOfTie,
    BottomCoverOfTie, DiameterOfTie, DiameterOfRebars, RoundingOfRebars,
    FaceLength):
    Return orientation and left and right cover of LShapeRebar in the form of
    dictionary of list.
    It takes eight different orientations input for LShapeHook i.e. 'Top
    Inside', 'Top Outside', 'Bottom Inside', 'Bottom Outside', 'Top Right',
    'Top Left', 'Bottom Right', 'Bottom Left'.
    It takes two different inputs for hook_extend_along i.e. 'x-axis', 'y-axis'.
    """
    if hook_extend_along == "y-axis":
        # Swap values of covers
        l_cover_of_tie, b_cover_of_tie = b_cover_of_tie, l_cover_of_tie
        r_cover_of_tie, t_cover_of_tie = t_cover_of_tie, r_cover_of_tie
    l_cover = []
    r_cover = []
    l_cover.append(l_cover_of_tie + dia_of_tie)
    if hook_orientation == "Top Inside" or hook_orientation == "Bottom Inside":
        # Assign orientation value
        if hook_orientation == "Top Inside":
            list_orientation = ["Top Left", "Top Right"]
        else:
            list_orientation = ["Bottom Left", "Bottom Right"]
        r_cover.append(
            face_length
            - l_cover_of_tie
            - dia_of_tie
            - dia_of_rebars / 2
            - rounding_of_rebars * dia_of_rebars
            - hook_extension
        )
        l_cover.append(
            face_length
            - r_cover_of_tie
            - dia_of_tie
            - dia_of_rebars / 2
            - rounding_of_rebars * dia_of_rebars
            - hook_extension
        )

    elif hook_orientation == "Top Outside" or hook_orientation == "Bottom Outside":
        if hook_orientation == "Top Outside":
            list_orientation = ["Top Left", "Top Right"]
        else:
            list_orientation = ["Bottom Left", "Bottom Right"]
        r_cover.append(
            face_length
            - l_cover_of_tie
            - dia_of_tie
            - dia_of_rebars / 2
            + rounding_of_rebars * dia_of_rebars
            + hook_extension
        )
        l_cover.append(
            face_length
            - r_cover_of_tie
            - dia_of_tie
            - dia_of_rebars / 2
            + rounding_of_rebars * dia_of_rebars
            + hook_extension
        )

    elif hook_orientation == "Top Left" or hook_orientation == "Bottom Left":
        if hook_orientation == "Top Left":
            list_orientation = ["Top Left", "Top Right"]
        else:
            list_orientation = ["Bottom Left", "Bottom Right"]
        r_cover.append(
            face_length
            - l_cover_of_tie
            - dia_of_tie
            - dia_of_rebars / 2
            + rounding_of_rebars * dia_of_rebars
            + hook_extension
        )
        l_cover.append(
            face_length
            - r_cover_of_tie
            - dia_of_tie
            - dia_of_rebars / 2
            - rounding_of_rebars * dia_of_rebars
            - hook_extension
        )

    elif hook_orientation == "Top Right" or hook_orientation == "Bottom Right":
        if hook_orientation == "Top Right":
            list_orientation = ["Top Left", "Top Right"]
        else:
            list_orientation = ["Bottom Left", "Bottom Right"]
        r_cover.append(
            face_length
            - l_cover_of_tie
            - dia_of_tie
            - dia_of_rebars / 2
            - rounding_of_rebars * dia_of_rebars
            - hook_extension
        )
        l_cover.append(
            face_length
            - r_cover_of_tie
            - dia_of_tie
            - dia_of_rebars / 2
            + rounding_of_rebars * dia_of_rebars
            + hook_extension
        )

    r_cover.append(r_cover_of_tie + dia_of_tie)
    l_rebar_orientation_cover = {}
    l_rebar_orientation_cover["list_orientation"] = list_orientation
    l_rebar_orientation_cover["l_cover"] = l_cover
    l_rebar_orientation_cover["r_cover"] = r_cover
    return l_rebar_orientation_cover


def getFacenameforRebar(hook_extend_along, facename, structure):
    """getFacenameforRebar(HookExtendAlong, Facename, Structure):
    Return facename of face normal to selected/provided face
    It takes two different inputs for hook_extend_along i.e. 'x-axis', 'y-axis'.
    """
    face = structure.Shape.Faces[getFaceNumber(facename) - 1]
    normal1 = face.normalAt(0, 0)
    faces = structure.Shape.Faces
    index = 1
    for face in faces:
        normal2 = face.normalAt(0, 0)
        if hook_extend_along == "x-axis":
            if int(normal1.dot(normal2)) == 0 and int(normal1.cross(normal2).x) == 1:
                facename_for_rebars = "Face" + str(index)
                break
        else:
            if int(normal1.dot(normal2)) == 0 and int(normal1.cross(normal2).y) == 1:
                facename_for_rebars = "Face" + str(index)
                break
        index += 1
    return facename_for_rebars


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
    NumberSpacingCheck, NumberSpacingValue, DiameterOfRebars, TopOffsetofRebars,
    BottomOffsetofRebars, RebarType, LShapeHookOrientation, HookExtendAlong,
    LShapeRebarRounding, LShapeHookLength, Structure, Facename):
    Adds the Single Tie reinforcement to the selected structural column
    object.
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
            print("Error: Pass structure and facename arguments")
            return None

    # Calculate common parameters for Straight/LShaped rebars
    if hook_extend_along == "x-axis":
        f_cover = b_cover_of_tie + dia_of_tie
    else:
        f_cover = r_cover_of_tie + dia_of_tie
    t_cover = t_offset_of_rebars
    b_cover = b_offset_of_rebars
    rebar_number_spacing_check = True
    rebar_number_spacing_value = 2

    # Find facename of face normal to selected/provided face
    facename_for_rebars = getFacenameforRebar(hook_extend_along, facename, structure)

    # Create Straight Rebars
    if rebar_type == "StraightRebar":
        # Right and left cover changes with hook_extend_along because facename,
        # using which rebars created, changes with value of hook_extend_along
        if hook_extend_along == "x-axis":
            r_cover = r_cover_of_tie + dia_of_tie
            l_cover = l_cover_of_tie + dia_of_tie
        else:
            r_cover = t_cover_of_tie + dia_of_tie
            l_cover = l_cover_of_tie + dia_of_tie
        orientation = "Vertical"
        list_coverAlong = ["Right Side", "Left Side"]
        rl_cover = [r_cover, l_cover]

        i = 0
        main_rebars = []
        for coverAlong in list_coverAlong:
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
            if hook_extend_along == "x-axis":
                main_rebars[i].OffsetEnd = (
                    t_cover_of_tie + dia_of_tie + dia_of_rebars / 2
                )
            else:
                main_rebars[i].OffsetEnd = (
                    l_cover_of_tie + dia_of_tie + dia_of_rebars / 2
                )
            i += 1

    # Create L-Shaped Rebars
    elif rebar_type == "LShapeRebar":
        FacePRM = getParametersOfFace(structure, facename_for_rebars)
        face_length = FacePRM[0][0]
        # TODO: Implement hook extension values from here:
        # https://archive.org/details/gov.in.is.sp.16.1980/page/n207
        if not hook_extension:
            if hook_extend_along == "x-axis":
                hook_extension = (
                    face_length - l_cover_of_tie - r_cover_of_tie - 2 * dia_of_tie
                ) / 3
            else:
                hook_extension = (
                    face_length - t_cover_of_tie - b_cover_of_tie - 2 * dia_of_tie
                ) / 3
        if not l_rebar_rounding:
            l_rebar_rounding = (float(dia_of_tie) / 2 + dia_of_rebars / 2) / dia_of_tie
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

        i = 0
        main_rebars = []
        for orientation in list_orientation:
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
            i += 1

    # Calculate parameters for Stirrup
    rounding = (float(dia_of_tie) / 2 + dia_of_rebars / 2) / dia_of_tie
    f_cover = offset_of_tie

    # Create Stirrups
    stirrup = makeStirrup(
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

    # Add created tie and rebars to SingleTieFourRebars group
    SingleTieFourRebars.addObject(stirrup)
    SingleTieFourRebars.addObjects(main_rebars)

    # Set properties values for tie and rebars in SingleTieFourRebars group
    properties_values = []
    properties_values.append(("ColumnConfiguration", "SingleTieFourRebars"))
    properties_values.append(("MainRebarType", rebar_type))
    properties_values.append(("RebarTopOffset", t_offset_of_rebars))
    properties_values.append(("RebarBottomOffset", b_offset_of_rebars))
    properties_values.append(("HookOrientation", hook_orientation))
    properties_values.append(("HookExtendAlong", hook_extend_along))
    properties_values.append(("HookExtension", hook_extension))
    SingleTieFourRebars.setPropertiesValues(properties_values)
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
    print("Implementation in progress")


class _SingleTieFourRebars(_RebarGroup, _ViewProviderRebarGroup):
    "A SingleTieFourRebars group object."

    def __init__(self):
        """Create Group object and add properties to it."""
        rebar_group = FreeCAD.ActiveDocument.addObject(
            "App::DocumentObjectGroupPython", "SingleTieFourRebars"
        )
        _RebarGroup.__init__(self, rebar_group)
        if FreeCAD.GuiUp:
            _ViewProviderRebarGroup.__init__(self, rebar_group.ViewObject)
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
                "ColumnConfiguration",
                "Configuration of Column Reinforcement",
                1,
            )
        )
        properties.append(
            ("App::PropertyString", "MainRebarType", "Type of main rebars", 1)
        )
        properties.append(
            ("App::PropertyDistance", "RebarTopOffset", "Top offset of main rebars", 1)
        )
        properties.append(
            (
                "App::PropertyDistance",
                "RebarBottomOffset",
                "Bottom offset of main rebars",
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
            ("App::PropertyString", "HookExtendAlong", "Direction of hook extension", 1)
        )
        properties.append(
            ("App::PropertyDistance", "HookExtension", "Length of hook", 1)
        )
        self.setProperties(properties)
