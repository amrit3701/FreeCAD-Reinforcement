# -*- coding: utf-8 -*-
# ***************************************************************************
# *                                                                         *
# *   Copyright (c) 2021 - Shiv Charan <shivcharanmt@gmail.com>             *
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

__title__ = "Slab Reinforcement"
__author__ = "Shiv Charan"
__url__ = "https://www.freecadweb.org"

import FreeCAD
from Rebarfunc import showWarning
from typing import Union, Tuple, Optional
from SlabReinforcement.SlabReinforcementObject import (
    SlabReinforcementGroup,
    _SlabReinforcementViewProviderGroup,
)

if FreeCAD.GuiUp:
    import FreeCADGui


def makeSlabReinforcement(
    parallel_rebar_type: str,
    parallel_front_cover: float,
    parallel_rear_cover: float,
    parallel_left_cover: float,
    parallel_right_cover: float,
    parallel_top_cover: float,
    parallel_bottom_cover: float,
    parallel_diameter: float,
    parallel_amount_spacing_check: bool,
    parallel_amount_spacing_value: Union[float, int],
    cross_rebar_type: str,
    cross_front_cover: float,
    cross_rear_cover: float,
    cross_left_cover: float,
    cross_right_cover: float,
    cross_top_cover: float,
    cross_bottom_cover: float,
    cross_diameter: float,
    cross_amount_spacing_check: bool,
    cross_amount_spacing_value: Union[float, int],
    cross_rounding: Optional[int] = 2,
    cross_bent_bar_length: Optional[int] = 50,
    cross_bent_bar_angle: Optional[int] = 135,
    cross_l_shape_hook_orintation: Optional[str] = "Alternate",
    cross_distribution_rebars_check: Optional[bool] = False,
    cross_distribution_rebars_diameter: Optional[float] = 8,
    cross_distribution_rebars_amount_spacing_check: Optional[bool] = True,
    cross_distribution_rebars_amount_spacing_value: Optional[int] = 2,
    parallel_rounding: Optional[int] = 2,
    parallel_bent_bar_length: Optional[int] = 50,
    parallel_bent_bar_angle: Optional[int] = 135,
    parallel_l_shape_hook_orintation: Optional[str] = "Alternate",
    parallel_distribution_rebars_check: Optional[bool] = False,
    parallel_distribution_rebars_diameter: Optional[float] = 8,
    parallel_distribution_rebars_amount_spacing_check: Optional[bool] = True,
    parallel_distribution_rebars_amount_spacing_value: Optional[int] = 2,
    mesh_cover_along: str = "Bottom",
    structure: Optional[Tuple] = None,
    facename: Optional[str] = None,
):
    """Generate Slab Reinforcement

    Parameters
    ----------
    parallel_rebar_type: str
        Type of rebar for parallel rebars for slab reinforcement.
        It can have four values 'StraightRebar','LShapeRebar', 'UShapeRebar',
        'BentShapeRebar'.
    parallel_front_cover: float
        The distance between parallel rebar and selected face.
    parallel_rear_cover: float
        Rear cover for slab reinforcement of parallel rebars.
    parallel_left_cover: float
        The distance between the left end of the parallel rebar to the left face of
        the structure.
    parallel_right_cover: float
        The distance between the right end of the parallel rebar to right face of
        the structure.
    parallel_top_cover: float
        The distance between parallel rebars from the top face of the structure.
    parallel_bottom_cover: float
        The distance between parallel rebars from the bottom face of the structure.
    parallel_diameter: float
        Diameter of parallel rebars.
    parallel_amount_spacing_check: bool
        If is set to True, then value of parallel_amount_spacing_value is used as
        rebars count else parallel_amount_spacing_value's value is used as spacing
        in parallel rebars.
    parallel_amount_spacing_value: float or int
        It contains count of rebars or spacing between parallel rebars based on
        value of amount_spacing_check.
    cross_rebar_type: str
        Type of rebar for cross rebars for slab reinforcement.
        It can have four values 'StraightRebar','LShapeRebar', 'UShapeRebar',
        'BentShapeRebar'.
    cross_front_cover: float
        The distance between cross rebar and cross_face (face perpendicular to selected face).
    cross_rear_cover: float
        Rear cover for slab reinforcement of cross rebars.
    cross_left_cover: float
        The distance between the left end of the cross rebar to the left face of
        the structure.
    cross_right_cover: float
        The distance between the right end of the rebar to right face of
        the structure relative to cross_face.
    cross_top_cover: float
        The distance between cross rebar from the top face of the structure.
    cross_bottom_cover: float
        The distance between cross rebar from the bottom face of the structure.
    cross_diameter: float
        Diameter of cross rebars.
    cross_amount_spacing_check: bool
        If is set to True, then value of cross_amount_spacing_value is used as
        rebars count else cross_amount_spacing_value's value is used as spacing
        in rebars.
    cross_amount_spacing_value: float or int
        It contains count of rebars or spacing between rebars based on
        value of cross_amount_spacing_check.
    cross_rounding: int
        A rounding value to be applied to the corners of the bars, expressed
        in times the cross_diameter.
    cross_bent_bar_length: float
        It represents arm's length of bent shape cross rebar when cross_rebar_type is
        BentShapeRebar
    cross_bent_bar_angle: int
        It represents angle for bent shape cross rebar when cross_rebar_type is
        BentShapeRebar
    cross_l_shape_hook_orintation: str
        It represents orintation of hook of cross L-Shape rebar if cross_rebar_type
        is LShapeRebar.
        It can have tree values "Left", "Right", "Alternate"
    cross_distribution_rebars_check: bool
        If True add distribution rebars for cross bent shape rebars.
        Default is False.
    cross_distribution_rebars_diameter: float
        Diameter for distribution rebars for cross bent shape rebars.
    cross_distribution_rebars_amount_spacing_check: bool
        If is set to True, then value of cross_distribution_rebars_amount_spacing_value
        is used as rebars count else cross_distribution_rebars_amount_spacing_value's
        value is used as spacing in cross_distribution_rebars.
        Default is True.
    cross_distribution_rebars_amount_spacing_value: int or float
        It contains count or spacing between distribution rebars for one side of cross
        bent shape rebars based on value of cross_distribution_rebars_check.
        Default is 2.
    parallel_rounding: int
        A rounding value to be applied to the corners of the bars, expressed
        in times the parallel_diameter.
    parallel_bent_bar_length: float
        It represents arm's length of bent shape parallel rebar when parallel_rebar_type is
        BentShapeRebar
    parallel_bent_bar_angle: int
        It represents angle for bent shape parallel rebar when parallel_rebar_type is
        BentShapeRebar
    parallel_l_shape_hook_orintation: str
        It represents orintation of hook of parallel L-Shape rebar if parallel_rebar_type
        is LShapeRebar.
        It can have tree values "Left", "Right", "Alternate"
    parallel_distribution_rebars_check: bool
        If True add distribution rebars for parallel bent shape rebars.
        Default is False.
    parallel_distribution_rebars_diameter: float
        Diameter of distribution rebars for parallel bent shape rebars.
    parallel_distribution_rebars_amount_spacing_check: bool
        If is set to True, then value of parallel_distribution_rebars_amount_spacing_value
        is used as rebars count else parallel_distribution_rebars_amount_spacing_value's
        value is used as spacing in parallel_distribution_rebars.
        Default is True.
    parallel_distribution_rebars_amount_spacing_value: int or float
        It contains count or spacing between distribution rebars for one side of parallel
        bent shape rebars based on value of parallel_distribution_rebars_check.
        Default is 2.
    mesh_cover_along: str
        It can have two values "Top" and "Bottom". It represent alignment of
        rebar mesh along top or bottom face of structure.
    structure: Arch structure object
        Arch structure object.
        Default is None
    facename: str
        selected face of structure.
        Default is None
    """
    # create instance of SlabReinforcementGroup
    if not structure and not facename:
        if FreeCAD.GuiUp:
            selected_obj = FreeCADGui.Selection.getSelectionEx()[0]
            structure = selected_obj.Object
            facename = selected_obj.SubElementNames[0]
        else:
            showWarning("Error: Pass structure and facename arguments")
            return None

    slabReinforcementGroup = SlabReinforcementGroup().Object
    if FreeCAD.GuiUp:
        _SlabReinforcementViewProviderGroup(slabReinforcementGroup.ViewObject)

    slabReinforcementGroup.MeshCoverAlong = mesh_cover_along
    slabReinforcementGroup.Structure = structure
    slabReinforcementGroup.Facename = facename
    slabReinforcementGroup.ParallelRebarType = parallel_rebar_type
    slabReinforcementGroup.ParallelFrontCover = parallel_front_cover
    slabReinforcementGroup.ParallelRearCover = parallel_rear_cover
    slabReinforcementGroup.ParallelLeftCover = parallel_left_cover
    slabReinforcementGroup.ParallelRightCover = parallel_right_cover
    slabReinforcementGroup.ParallelTopCover = parallel_top_cover
    slabReinforcementGroup.ParallelBottomCover = parallel_bottom_cover
    slabReinforcementGroup.ParallelDiameter = parallel_diameter
    slabReinforcementGroup.ParallelAmountSpacingCheck = (
        parallel_amount_spacing_check
    )
    if parallel_amount_spacing_check:
        slabReinforcementGroup.ParallelAmountValue = (
            parallel_amount_spacing_value
        )
    else:
        slabReinforcementGroup.ParallelSpacingValue = (
            parallel_amount_spacing_value
        )

    if parallel_rounding:
        slabReinforcementGroup.ParallelRounding = parallel_rounding
    if parallel_bent_bar_length:
        slabReinforcementGroup.ParallelBentBarLength = parallel_bent_bar_length
    if parallel_bent_bar_angle:
        slabReinforcementGroup.ParallelBentBarAngle = parallel_bent_bar_angle
    if parallel_l_shape_hook_orintation:
        slabReinforcementGroup.ParallelLShapeHookOrintation = (
            parallel_l_shape_hook_orintation
        )

    if parallel_distribution_rebars_check:
        slabReinforcementGroup.ParallelDistributionRebarsCheck = (
            parallel_distribution_rebars_check
        )

    if parallel_distribution_rebars_diameter:
        slabReinforcementGroup.ParallelDistributionRebarsDiameter = (
            parallel_distribution_rebars_diameter
        )

    if parallel_distribution_rebars_amount_spacing_check:
        slabReinforcementGroup.ParallelDistributionRebarsAmountSpacingCheck = (
            parallel_distribution_rebars_amount_spacing_check
        )

    if parallel_distribution_rebars_amount_spacing_check:
        if parallel_distribution_rebars_amount_spacing_value:
            slabReinforcementGroup.ParallelDistributionRebarsAmount = (
                parallel_distribution_rebars_amount_spacing_value
            )
    else:
        if parallel_distribution_rebars_amount_spacing_value:
            slabReinforcementGroup.ParallelDistributionRebarsSpacing = (
                parallel_distribution_rebars_amount_spacing_value
            )

    slabReinforcementGroup.CrossRebarType = cross_rebar_type
    slabReinforcementGroup.CrossFrontCover = cross_front_cover
    slabReinforcementGroup.CrossLeftCover = cross_left_cover
    slabReinforcementGroup.CrossRightCover = cross_right_cover
    slabReinforcementGroup.CrossRearCover = cross_rear_cover
    slabReinforcementGroup.CrossTopCover = cross_top_cover
    slabReinforcementGroup.CrossBottomCover = cross_bottom_cover
    slabReinforcementGroup.CrossDiameter = cross_diameter
    slabReinforcementGroup.CrossAmountSpacingCheck = cross_amount_spacing_check
    if cross_amount_spacing_check:
        slabReinforcementGroup.CrossAmountValue = cross_amount_spacing_value
    else:
        slabReinforcementGroup.CrossSpacingValue = cross_amount_spacing_value

    if cross_rounding:
        slabReinforcementGroup.CrossRounding = cross_rounding
    if cross_bent_bar_length:
        slabReinforcementGroup.CrossBentBarLength = cross_bent_bar_length
    if cross_bent_bar_angle:
        slabReinforcementGroup.CrossBentBarAngle = cross_bent_bar_angle
    if cross_l_shape_hook_orintation:
        slabReinforcementGroup.CrossLShapeHookOrintation = (
            cross_l_shape_hook_orintation
        )
    if cross_distribution_rebars_check:
        slabReinforcementGroup.CrossDistributionRebarsCheck = (
            cross_distribution_rebars_check
        )
    if cross_distribution_rebars_diameter:
        slabReinforcementGroup.CrossDistributionRebarsDiameter = (
            cross_distribution_rebars_diameter
        )
    if cross_distribution_rebars_amount_spacing_check:
        slabReinforcementGroup.CrossDistributionRebarsAmountSpacingCheck = (
            cross_distribution_rebars_amount_spacing_check
        )
    slabReinforcementGroup.IsMakeOrEditRequired = True
    if cross_distribution_rebars_amount_spacing_check:
        if cross_distribution_rebars_amount_spacing_value:
            slabReinforcementGroup.CrossDistributionRebarsAmount = (
                cross_distribution_rebars_amount_spacing_value
            )
    else:
        if cross_distribution_rebars_amount_spacing_value:
            slabReinforcementGroup.CrossDistributionRebarsSpacing = (
                cross_distribution_rebars_amount_spacing_value
            )
    FreeCAD.ActiveDocument.recompute()

    return slabReinforcementGroup


def editSlabReinforcement(
    slabReinforcementGroup: SlabReinforcementGroup,
    parallel_rebar_type: str,
    parallel_front_cover: float,
    parallel_rear_cover: float,
    parallel_left_cover: float,
    parallel_right_cover: float,
    parallel_top_cover: float,
    parallel_bottom_cover: float,
    parallel_diameter: float,
    parallel_amount_spacing_check: bool,
    parallel_amount_spacing_value: Union[float, int],
    cross_rebar_type: str,
    cross_front_cover: float,
    cross_rear_cover: float,
    cross_left_cover: float,
    cross_right_cover: float,
    cross_top_cover: float,
    cross_bottom_cover: float,
    cross_diameter: float,
    cross_amount_spacing_check: bool,
    cross_amount_spacing_value: Union[float, int],
    cross_rounding: Optional[int] = 2,
    cross_bent_bar_length: Optional[int] = 50,
    cross_bent_bar_angle: Optional[int] = 135,
    cross_l_shape_hook_orintation: Optional[str] = "Alternate",
    cross_distribution_rebars_check: Optional[bool] = False,
    cross_distribution_rebars_diameter: Optional[float] = 8,
    cross_distribution_rebars_amount_spacing_check: Optional[bool] = True,
    cross_distribution_rebars_amount_spacing_value: Optional[int] = 2,
    parallel_rounding: Optional[int] = 2,
    parallel_bent_bar_length: Optional[int] = 50,
    parallel_bent_bar_angle: Optional[int] = 135,
    parallel_l_shape_hook_orintation: Optional[str] = "Alternate",
    parallel_distribution_rebars_check: Optional[bool] = False,
    parallel_distribution_rebars_diameter: Optional[float] = 8,
    parallel_distribution_rebars_amount_spacing_check: Optional[bool] = True,
    parallel_distribution_rebars_amount_spacing_value: Optional[int] = 2,
    mesh_cover_along: str = "Bottom",
    structure: Optional[Tuple] = None,
    facename: Optional[str] = None,
):
    """Update Slab Reinforcement

    Parameters
    ----------
    slabReinforcementGroup: SlabReinforcementGroup
        Slab Reinforcement rebars group
    parallel_rebar_type: str
        Type of rebar for parallel rebars for slab reinforcement.
        It can have four values 'StraightRebar','LShapeRebar', 'UShapeRebar',
        'BentShapeRebar'.
    parallel_front_cover: float
        The distance between parallel rebar and selected face.
    parallel_rear_cover: float
        Rear cover for slab reinforcement of parallel rebars.
    parallel_left_cover: float
        The distance between the left end of the parallel rebar to the left face of
        the structure.
    parallel_right_cover: float
        The distance between the right end of the parallel rebar to right face of
        the structure.
    parallel_top_cover: float
        The distance between parallel rebars from the top face of the structure.
    parallel_bottom_cover: float
        The distance between parallel rebars from the bottom face of the structure.
    parallel_diameter: float
        Diameter of parallel rebars.
    parallel_amount_spacing_check: bool
        If is set to True, then value of parallel_amount_spacing_value is used as
        rebars count else parallel_amount_spacing_value's value is used as spacing
        in parallel rebars.
    parallel_amount_spacing_value: float or int
        It contains count of rebars or spacing between parallel rebars based on
        value of amount_spacing_check.
    cross_rebar_type: str
        Type of rebar for cross rebars for slab reinforcement.
        It can have four values 'StraightRebar','LShapeRebar', 'UShapeRebar',
        'BentShapeRebar'.
    cross_front_cover: float
        The distance between cross rebar and cross_face (face perpendicular to selected face).
    cross_rear_cover: float
        Rear cover for slab reinforcement of cross rebars.
    cross_left_cover: float
        The distance between the left end of the cross rebar to the left face of
        the structure.
    cross_right_cover: float
        The distance between the right end of the rebar to right face of
        the structure relative to cross_face.
    cross_top_cover: float
        The distance between cross rebar from the top face of the structure.
    cross_bottom_cover: float
        The distance between cross rebar from the bottom face of the structure.
    cross_diameter: float
        Diameter of cross rebars.
    cross_amount_spacing_check: bool
        If is set to True, then value of cross_amount_spacing_value is used as
        rebars count else cross_amount_spacing_value's value is used as spacing
        in rebars.
    cross_amount_spacing_value: float or int
        It contains count of rebars or spacing between rebars based on
        value of cross_amount_spacing_check.
    cross_rounding: int
        A rounding value to be applied to the corners of the bars, expressed
        in times the cross_diameter.
    cross_bent_bar_length: float
        It represents arm's length of bent shape cross rebar when cross_rebar_type is
        BentShapeRebar
    cross_bent_bar_angle: int
        It represents angle for bent shape cross rebar when cross_rebar_type is
        BentShapeRebar
    cross_l_shape_hook_orintation: str
        It represents orintation of hook of cross L-Shape rebar if cross_rebar_type
        is LShapeRebar.
        It can have tree values "Left", "Right", "Alternate"
    cross_distribution_rebars_check: bool
        If True add distribution rebars for cross bent shape rebars.
        Default is False.
    cross_distribution_rebars_diameter: float
        Diameter for distribution rebars for cross bent shape rebars.
    cross_distribution_rebars_amount_spacing_check: bool
        If is set to True, then value of cross_distribution_rebars_amount_spacing_value
        is used as rebars count else cross_distribution_rebars_amount_spacing_value's
        value is used as spacing in cross_distribution_rebars.
        Default is True.
    cross_distribution_rebars_amount_spacing_value: int or float
        It contains count or spacing between distribution rebars for one side of cross
        bent shape rebars based on value of cross_distribution_rebars_check.
        Default is 2.
    parallel_rounding: int
        A rounding value to be applied to the corners of the bars, expressed
        in times the parallel_diameter.
    parallel_bent_bar_length: float
        It represents arm's length of bent shape parallel rebar when parallel_rebar_type is
        BentShapeRebar
    parallel_bent_bar_angle: int
        It represents angle for bent shape parallel rebar when parallel_rebar_type is
        BentShapeRebar
    parallel_l_shape_hook_orintation: str
        It represents orintation of hook of parallel L-Shape rebar if parallel_rebar_type
        is LShapeRebar.
        It can have tree values "Left", "Right", "Alternate"
    parallel_distribution_rebars_check: bool
        If True add distribution rebars for parallel bent shape rebars.
        Default is False.
    parallel_distribution_rebars_diameter: float
        Diameter of distribution rebars for parallel bent shape rebars.
    parallel_distribution_rebars_amount_spacing_check: bool
        If is set to True, then value of parallel_distribution_rebars_amount_spacing_value
        is used as rebars count else parallel_distribution_rebars_amount_spacing_value's
        value is used as spacing in parallel_distribution_rebars.
        Default is True.
    parallel_distribution_rebars_amount_spacing_value: int or float
        It contains count or spacing between distribution rebars for one side of parallel
        bent shape rebars based on value of parallel_distribution_rebars_check.
        Default is 2.
    mesh_cover_along: str
        It can have two values "Top" and "Bottom". It represent alignment of
        rebar mesh along top or bottom face of structure.
    structure: Arch structure object
        Arch structure object.
        Default is None
    facename: str
        selected face of structure.
        Default is None
    """
    # Update value of SlabReinforcementGroup
    slabReinforcementGroup.MeshCoverAlong = mesh_cover_along

    if structure:
        slabReinforcementGroup.Structure = structure
    if facename:
        slabReinforcementGroup.Facename = facename
    slabReinforcementGroup.ParallelRebarType = parallel_rebar_type
    slabReinforcementGroup.ParallelFrontCover = parallel_front_cover
    slabReinforcementGroup.ParallelRearCover = parallel_rear_cover
    slabReinforcementGroup.ParallelLeftCover = parallel_left_cover
    slabReinforcementGroup.ParallelRightCover = parallel_right_cover
    slabReinforcementGroup.ParallelTopCover = parallel_top_cover
    slabReinforcementGroup.ParallelBottomCover = parallel_bottom_cover
    slabReinforcementGroup.ParallelDiameter = parallel_diameter
    slabReinforcementGroup.ParallelAmountSpacingCheck = (
        parallel_amount_spacing_check
    )
    if parallel_amount_spacing_check:
        slabReinforcementGroup.ParallelAmountValue = (
            parallel_amount_spacing_value
        )
    else:
        slabReinforcementGroup.ParallelSpacingValue = (
            parallel_amount_spacing_value
        )

    if parallel_rounding:
        slabReinforcementGroup.ParallelRounding = parallel_rounding
    if parallel_bent_bar_length:
        slabReinforcementGroup.ParallelBentBarLength = parallel_bent_bar_length
    if parallel_bent_bar_angle:
        slabReinforcementGroup.ParallelBentBarAngle = parallel_bent_bar_angle
    if parallel_l_shape_hook_orintation:
        slabReinforcementGroup.ParallelLShapeHookOrintation = (
            parallel_l_shape_hook_orintation
        )
    if parallel_distribution_rebars_check:
        slabReinforcementGroup.ParallelDistributionRebarsCheck = (
            parallel_distribution_rebars_check
        )
    if parallel_distribution_rebars_diameter:
        slabReinforcementGroup.ParallelDistributionRebarsDiameter = (
            parallel_distribution_rebars_diameter
        )
    if parallel_distribution_rebars_amount_spacing_check:
        slabReinforcementGroup.ParallelDistributionRebarsAmountSpacingCheck = (
            parallel_distribution_rebars_amount_spacing_check
        )
    if parallel_distribution_rebars_amount_spacing_check:
        if parallel_distribution_rebars_amount_spacing_value:
            slabReinforcementGroup.ParallelDistributionRebarsAmount = (
                parallel_distribution_rebars_amount_spacing_value
            )
    else:
        if parallel_distribution_rebars_amount_spacing_value:
            slabReinforcementGroup.ParallelDistributionRebarsSpacing = (
                parallel_distribution_rebars_amount_spacing_value
            )

    slabReinforcementGroup.CrossRebarType = cross_rebar_type
    slabReinforcementGroup.CrossFrontCover = cross_front_cover
    slabReinforcementGroup.CrossLeftCover = cross_left_cover
    slabReinforcementGroup.CrossRightCover = cross_right_cover
    slabReinforcementGroup.CrossRearCover = cross_rear_cover
    slabReinforcementGroup.CrossTopCover = cross_top_cover
    slabReinforcementGroup.CrossBottomCover = cross_bottom_cover
    slabReinforcementGroup.CrossDiameter = cross_diameter
    slabReinforcementGroup.CrossAmountSpacingCheck = cross_amount_spacing_check
    if cross_amount_spacing_check:
        slabReinforcementGroup.CrossAmountValue = cross_amount_spacing_value
    else:
        slabReinforcementGroup.CrossSpacingValue = cross_amount_spacing_value

    if cross_rounding:
        slabReinforcementGroup.CrossRounding = cross_rounding
    if cross_bent_bar_length:
        slabReinforcementGroup.CrossBentBarLength = cross_bent_bar_length
    if cross_bent_bar_angle:
        slabReinforcementGroup.CrossBentBarAngle = cross_bent_bar_angle
    if cross_l_shape_hook_orintation:
        slabReinforcementGroup.CrossLShapeHookOrintation = (
            cross_l_shape_hook_orintation
        )
    if cross_distribution_rebars_check:
        slabReinforcementGroup.CrossDistributionRebarsCheck = (
            cross_distribution_rebars_check
        )
    if cross_distribution_rebars_diameter:
        slabReinforcementGroup.CrossDistributionRebarsDiameter = (
            cross_distribution_rebars_diameter
        )
    if cross_distribution_rebars_amount_spacing_check:
        slabReinforcementGroup.CrossDistributionRebarsAmountSpacingCheck = (
            cross_distribution_rebars_amount_spacing_check
        )
    slabReinforcementGroup.IsMakeOrEditRequired = True
    if cross_distribution_rebars_amount_spacing_check:
        if cross_distribution_rebars_amount_spacing_value:
            slabReinforcementGroup.CrossDistributionRebarsAmount = (
                cross_distribution_rebars_amount_spacing_value
            )
    else:
        if cross_distribution_rebars_amount_spacing_value:
            slabReinforcementGroup.CrossDistributionRebarsSpacing = (
                cross_distribution_rebars_amount_spacing_value
            )
    FreeCAD.ActiveDocument.recompute()
    return slabReinforcementGroup
