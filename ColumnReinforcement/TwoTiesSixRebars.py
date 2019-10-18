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

from Stirrup import makeStirrup, editStirrup
from StraightRebar import makeStraightRebar, editStraightRebar
from LShapeRebar import makeLShapeRebar, editLShapeRebar
from ColumnReinforcement.SingleTie import (
    makeSingleTieFourRebars,
    editSingleTieFourRebars,
)
from Rebarfunc import (
    showWarning,
    getParametersOfFace,
    getFacenameforRebar,
    getLRebarOrientationLeftRightCover,
    setGroupProperties,
)

if FreeCAD.GuiUp:
    import FreeCADGui


def makeTwoTiesSixRebars(
    l_cover_of_ties,
    r_cover_of_ties,
    t_cover_of_ties,
    b_cover_of_ties,
    offset_of_ties,
    bent_angle_of_ties,
    extension_factor_of_ties,
    dia_of_ties,
    number_spacing_check,
    number_spacing_value,
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
    BottomCoverOfTies, OffsetofTies, BentAngleOfTies, ExtensionFactorOfTies,
    DiameterOfTies, NumberSpacingCheck, NumberSpacingValue,
    DiameterOfMainRebars, TopOffsetOfMainRebars, BottomOffsetOfRebars,
    MainRebarsType, LShapeHookOrientation, HookExtendAlong, LShapeRebarRounding,
    LShapeHookLength, TiesSequence, Structure, Facename):
    """
    if not structure and not facename:
        if FreeCAD.GuiUp:
            selected_obj = FreeCADGui.Selection.getSelectionEx()[0]
            structure = selected_obj.Object
            facename = selected_obj.SubElementNames[0]
        else:
            showWarning("Error: Pass structure and facename arguments")
            return

    FacePRM = getParametersOfFace(structure, facename)
    face_length = FacePRM[0][0]

    # Calculate parameters for tie1 and tie2
    if ties_sequence[0] == "Tie2" and ties_sequence[1] == "Tie1":
        start_offset_of_tie1 = offset_of_ties + dia_of_ties + dia_of_ties / 2
        start_offset_of_tie2 = offset_of_ties
        end_offset_of_tie1 = start_offset_of_tie2
        end_offset_of_tie2 = start_offset_of_tie1
    else:
        start_offset_of_tie1 = offset_of_ties
        start_offset_of_tie2 = offset_of_ties + 2 * dia_of_ties
        end_offset_of_tie1 = start_offset_of_tie2
        end_offset_of_tie2 = start_offset_of_tie1
    l_cover_of_tie1 = l_cover_of_ties
    r_cover_of_tie1 = face_length / 2 - dia_of_main_rebars / 2 - dia_of_ties
    l_cover_of_tie2 = r_cover_of_tie1
    r_cover_of_tie2 = r_cover_of_ties

    # Create SingleTieFourRebars
    SingleTieFourRebarsObject = makeSingleTieFourRebars(
        l_cover_of_tie1,
        r_cover_of_tie1,
        t_cover_of_ties,
        b_cover_of_ties,
        start_offset_of_tie1,
        bent_angle_of_ties,
        extension_factor_of_ties,
        dia_of_ties,
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
    SingleTieFourRebarsObject.rebar_group.RebarGroups[0].Ties[0].OffsetEnd = (
        end_offset_of_tie1 + dia_of_ties / 2
    )

    # Create tie2
    rounding = (float(dia_of_ties) / 2 + dia_of_main_rebars / 2) / dia_of_ties
    tie2 = makeStirrup(
        l_cover_of_tie2,
        r_cover_of_tie2,
        t_cover_of_ties,
        b_cover_of_ties,
        start_offset_of_tie2,
        bent_angle_of_ties,
        extension_factor_of_ties,
        dia_of_ties,
        rounding,
        number_spacing_check,
        number_spacing_value,
        structure,
        facename,
    )
    tie2.OffsetEnd = end_offset_of_tie2 + dia_of_ties / 2

    main_rebars = makeMainRebars(
        l_cover_of_ties,
        r_cover_of_ties,
        t_cover_of_ties,
        b_cover_of_ties,
        dia_of_ties,
        dia_of_main_rebars,
        t_offset_of_rebars,
        b_offset_of_rebars,
        main_rebars_type,
        hook_orientation,
        hook_extend_along,
        hook_extension,
        l_rebar_rounding,
        structure,
        facename,
    )

    SingleTieFourRebarsObject.ties_group.TiesConfiguration = "TwoTiesSixRebars"
    SingleTieFourRebarsObject.addTies(tie2)
    SingleTieFourRebarsObject.addMainRebars(main_rebars)
    SingleTieFourRebarsObject.ties_group.LeftCover = l_cover_of_ties
    SingleTieFourRebarsObject.ties_group.RightCover = r_cover_of_ties
    SingleTieFourRebarsObject.ties_group.TopCover = t_cover_of_ties
    SingleTieFourRebarsObject.ties_group.BottomCover = b_cover_of_ties

    TwoTiesSixRebars = _TwoTiesSixRebars(SingleTieFourRebarsObject)
    TwoTiesSixRebars.ties_group.TiesSequence = ties_sequence

    FreeCAD.ActiveDocument.recompute()
    return TwoTiesSixRebars.Object


def makeMainRebars(
    l_cover_of_ties,
    r_cover_of_ties,
    t_cover_of_ties,
    b_cover_of_ties,
    dia_of_ties,
    dia_of_main_rebars,
    t_offset_of_rebars,
    b_offset_of_rebars,
    main_rebars_type,
    hook_orientation,
    hook_extend_along,
    hook_extension,
    l_rebar_rounding,
    structure,
    facename,
):
    # Calculate common parameters for Straight/LShaped rebars
    t_cover = t_offset_of_rebars
    b_cover = b_offset_of_rebars
    rebar_number_spacing_check = True
    main_rebars = []

    # Create Straight Rebars
    if main_rebars_type == "StraightRebar":
        hook_extend_along = "x-axis"
        facename_for_rebars = getFacenameforRebar(
            hook_extend_along, facename, structure
        )
        f_cover = b_cover_of_ties + dia_of_ties
        r_cover = r_cover_of_ties + dia_of_ties
        orientation = "Vertical"
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
            t_cover_of_ties + dia_of_ties + dia_of_main_rebars / 2
        )

    # Create L-Shaped Rebars
    elif main_rebars_type == "LShapeRebar":
        facename_for_rebars = getFacenameforRebar(
            hook_extend_along, facename, structure
        )
        FacePRM = getParametersOfFace(structure, facename_for_rebars)
        face_length = FacePRM[0][0]
        if hook_extend_along == "x-axis":
            f_cover = b_cover_of_ties + dia_of_ties
        else:
            f_cover = r_cover_of_ties + dia_of_ties
        # Implement hook extension values from here:
        # https://archive.org/details/gov.in.is.sp.16.1980/page/n207
        if not hook_extension:
            hook_extension = 4 * dia_of_main_rebars
        if not l_rebar_rounding:
            l_rebar_rounding = (
                float(dia_of_ties) / 2 + dia_of_main_rebars / 2
            ) / dia_of_ties
        l_rebar_orientation_cover = getLRebarOrientationLeftRightCover(
            hook_orientation,
            hook_extension,
            hook_extend_along,
            l_cover_of_ties,
            r_cover_of_ties,
            t_cover_of_ties,
            b_cover_of_ties,
            dia_of_ties,
            dia_of_main_rebars,
            l_rebar_rounding,
            face_length,
        )
        list_orientation = l_rebar_orientation_cover["list_orientation"]
        l_cover = l_rebar_orientation_cover["l_cover"]
        r_cover = l_rebar_orientation_cover["r_cover"]
        t_cover = t_offset_of_rebars
        b_cover = b_offset_of_rebars

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
                t_cover_of_ties + dia_of_ties + dia_of_main_rebars / 2
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
                    l_cover_of_ties + dia_of_ties + dia_of_main_rebars / 2
                )
    FreeCAD.ActiveDocument.recompute()
    return main_rebars


def editTwoTiesSixRebars(
    rebar_group,
    l_cover_of_ties,
    r_cover_of_ties,
    t_cover_of_ties,
    b_cover_of_ties,
    offset_of_ties,
    bent_angle_of_ties,
    extension_factor_of_ties,
    dia_of_ties,
    number_spacing_check,
    number_spacing_value,
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
    """editTwoTiesSixRebars(RebarGroup, LeftCoverOfTies, RightCoverOfTies,
    TopCoverOfTies, BottomCoverOfTies, OffsetofTies, BentAngleOfTies,
    ExtensionFactorOfTies, DiameterOfTies, NumberSpacingCheck,
    NumberSpacingValue, DiameterOfMainRebars, TopOffsetOfMainRebars,
    BottomOffsetOfRebars, MainRebarsType, LShapeHookOrientation,
    HookExtendAlong, LShapeRebarRounding, LShapeHookLength, TiesSequence,
    Structure, Facename):
    """
    if len(rebar_group.RebarGroups) == 0:
        return rebar_group
    for i, tmp_rebar_group in enumerate(rebar_group.RebarGroups):
        if hasattr(tmp_rebar_group, "Ties"):
            if len(tmp_rebar_group.Ties) > 0:
                Tie = tmp_rebar_group.Ties[0]
                break
            else:
                showWarning(
                    "You have deleted ties. Please recreate the"
                    "ColumnReinforcement."
                )
                return rebar_group
        elif i == len(rebar_group.RebarGroups) - 1:
            showWarning(
                "You have deleted ties group. Please recreate the"
                "ColumnReinforcement."
            )
            return rebar_group

    if not structure and not facename:
        structure = Tie.Base.Support[0][0]
        facename = Tie.Base.Support[0][1][0]

    FacePRM = getParametersOfFace(structure, facename)
    face_length = FacePRM[0][0]

    # Calculate parameters for tie1 and tie2
    if ties_sequence[0] == "Tie2" and ties_sequence[1] == "Tie1":
        start_offset_of_tie1 = offset_of_ties + dia_of_ties + dia_of_ties / 2
        start_offset_of_tie2 = offset_of_ties
        end_offset_of_tie1 = start_offset_of_tie2
        end_offset_of_tie2 = start_offset_of_tie1
    else:
        start_offset_of_tie1 = offset_of_ties
        start_offset_of_tie2 = offset_of_ties + 2 * dia_of_ties
        end_offset_of_tie1 = start_offset_of_tie2
        end_offset_of_tie2 = start_offset_of_tie1
    l_cover_of_tie1 = l_cover_of_ties
    r_cover_of_tie1 = face_length / 2 - dia_of_main_rebars / 2 - dia_of_ties
    l_cover_of_tie2 = r_cover_of_tie1
    r_cover_of_tie2 = r_cover_of_ties

    # Edit tie2
    tie2 = rebar_group.RebarGroups[0].Ties[1]
    rounding = (float(dia_of_ties) / 2 + dia_of_main_rebars / 2) / dia_of_ties
    tie2 = editStirrup(
        tie2,
        l_cover_of_tie2,
        r_cover_of_tie2,
        t_cover_of_ties,
        b_cover_of_ties,
        start_offset_of_tie2,
        bent_angle_of_ties,
        extension_factor_of_ties,
        dia_of_ties,
        rounding,
        number_spacing_check,
        number_spacing_value,
        structure,
        facename,
    )
    tie2.OffsetEnd = end_offset_of_tie2 + dia_of_ties / 2

    main_rebar_group = rebar_group.RebarGroups[1]
    main_rebars = editMainRebars(
        main_rebar_group,
        l_cover_of_ties,
        r_cover_of_ties,
        t_cover_of_ties,
        b_cover_of_ties,
        dia_of_ties,
        dia_of_main_rebars,
        t_offset_of_rebars,
        b_offset_of_rebars,
        main_rebars_type,
        hook_orientation,
        hook_extend_along,
        hook_extension,
        l_rebar_rounding,
        structure,
        facename,
    )

    # Edit SingleTieFourRebars
    rebar_group = editSingleTieFourRebars(
        rebar_group,
        l_cover_of_tie1,
        r_cover_of_tie1,
        t_cover_of_ties,
        b_cover_of_ties,
        start_offset_of_tie1,
        bent_angle_of_ties,
        extension_factor_of_ties,
        dia_of_ties,
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
    rebar_group.RebarGroups[0].Ties[0].OffsetEnd = (
        end_offset_of_tie1 + dia_of_ties / 2
    )

    if main_rebars:
        main_rebar_group.addObjects(main_rebars)
        prev_main_rebars = main_rebar_group.MainRebars
        prev_main_rebars.extend(main_rebars)
        main_rebar_group.MainRebars = prev_main_rebars

    rebar_group.RebarGroups[0].LeftCover = l_cover_of_ties
    rebar_group.RebarGroups[0].RightCover = r_cover_of_ties
    rebar_group.RebarGroups[0].TopCover = t_cover_of_ties
    rebar_group.RebarGroups[0].BottomCover = b_cover_of_ties
    rebar_group.RebarGroups[0].TiesSequence = ties_sequence

    FreeCAD.ActiveDocument.recompute()
    return rebar_group


def editMainRebars(
    main_rebar_group,
    l_cover_of_ties,
    r_cover_of_ties,
    t_cover_of_ties,
    b_cover_of_ties,
    dia_of_ties,
    dia_of_main_rebars,
    t_offset_of_rebars,
    b_offset_of_rebars,
    main_rebars_type,
    hook_orientation,
    hook_extend_along,
    hook_extension,
    l_rebar_rounding,
    structure,
    facename,
):
    prev_main_rebars_type = main_rebar_group.RebarType
    prev_hook_extend_along = main_rebar_group.HookExtendAlong
    if prev_main_rebars_type == main_rebars_type:
        recreate_main_rebars = False
    else:
        recreate_main_rebars = True
    main_rebars = []

    if recreate_main_rebars:
        for rebar in main_rebar_group.MainRebars[2:]:
            base_name = rebar.Base.Name
            FreeCAD.ActiveDocument.removeObject(rebar.Name)
            FreeCAD.ActiveDocument.removeObject(base_name)
        main_rebars = makeMainRebars(
            l_cover_of_ties,
            r_cover_of_ties,
            t_cover_of_ties,
            b_cover_of_ties,
            dia_of_ties,
            dia_of_main_rebars,
            t_offset_of_rebars,
            b_offset_of_rebars,
            main_rebars_type,
            hook_orientation,
            hook_extend_along,
            hook_extension,
            l_rebar_rounding,
            structure,
            facename,
        )
    else:
        for rebar in main_rebar_group.MainRebars[2:]:
            main_rebars.append(rebar)
        # Calculate common parameters for Straight/LShaped rebars
        t_cover = t_offset_of_rebars
        b_cover = b_offset_of_rebars
        rebar_number_spacing_check = True

        # Edit Straight Rebars
        if main_rebars_type == "StraightRebar":
            hook_extend_along = "x-axis"
            facename_for_rebars = getFacenameforRebar(
                hook_extend_along, facename, structure
            )
            f_cover = b_cover_of_ties + dia_of_ties
            r_cover = r_cover_of_ties + dia_of_ties
            orientation = "Vertical"
            rebar_number_spacing_value = 2

            editStraightRebar(
                main_rebars[-1],
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
            main_rebars[-1].OffsetEnd = (
                t_cover_of_ties + dia_of_ties + dia_of_main_rebars / 2
            )

        # Edit L-Shaped Rebars
        elif main_rebars_type == "LShapeRebar":
            facename_for_rebars = getFacenameforRebar(
                hook_extend_along, facename, structure
            )
            FacePRM = getParametersOfFace(structure, facename_for_rebars)
            face_length = FacePRM[0][0]
            if hook_extend_along == "x-axis":
                f_cover = b_cover_of_ties + dia_of_ties
            else:
                f_cover = r_cover_of_ties + dia_of_ties
            # Implement hook extension values from here:
            # https://archive.org/details/gov.in.is.sp.16.1980/page/n207
            if not hook_extension:
                hook_extension = 4 * dia_of_main_rebars
            if not l_rebar_rounding:
                l_rebar_rounding = (
                    float(dia_of_ties) / 2 + dia_of_main_rebars / 2
                ) / dia_of_ties
            l_rebar_orientation_cover = getLRebarOrientationLeftRightCover(
                hook_orientation,
                hook_extension,
                hook_extend_along,
                l_cover_of_ties,
                r_cover_of_ties,
                t_cover_of_ties,
                b_cover_of_ties,
                dia_of_ties,
                dia_of_main_rebars,
                l_rebar_rounding,
                face_length,
            )
            list_orientation = l_rebar_orientation_cover["list_orientation"]
            l_cover = l_rebar_orientation_cover["l_cover"]
            r_cover = l_rebar_orientation_cover["r_cover"]
            t_cover = t_offset_of_rebars
            b_cover = b_offset_of_rebars

            if hook_extend_along == "x-axis":
                if prev_hook_extend_along == "y-axis":
                    rebar = main_rebars.pop()
                    base_name = rebar.Base.Name
                    FreeCAD.ActiveDocument.removeObject(rebar.Name)
                    FreeCAD.ActiveDocument.removeObject(base_name)
                rebar_number_spacing_value = 2
                orientation = list_orientation[1]
                editLShapeRebar(
                    main_rebars[-1],
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
                main_rebars[-1].OffsetEnd = (
                    t_cover_of_ties + dia_of_ties + dia_of_main_rebars / 2
                )
            elif hook_extend_along == "y-axis":
                rebar_number_spacing_value = 1
                orientation = list_orientation[1]
                for i, orientation in enumerate(list_orientation):
                    if len(main_rebars) > i:
                        editLShapeRebar(
                            main_rebars[i],
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
                    else:
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
                        l_cover_of_ties + dia_of_ties + dia_of_main_rebars / 2
                    )
    FreeCAD.ActiveDocument.recompute()
    return main_rebars


class _TwoTiesSixRebars:
    def __init__(self, obj):
        """Add properties to object obj."""
        self.Object = obj.rebar_group
        self.ties_group = obj.ties_group
        properties = []
        properties.append(
            ("App::PropertyStringList", "TiesSequence", "Sequence of ties", 1)
        )
        setGroupProperties(properties, obj.ties_group)
