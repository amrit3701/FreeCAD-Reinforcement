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
from typing import Union, Tuple, Optional
from Rebarfunc import (
    getFacenamesforBeamReinforcement,
    getParametersOfFace,
    get_rebar_amount_from_spacing,
)
from StraightRebar import makeStraightRebar
from UShapeRebar import makeUShapeRebar
from BentShapeRebar import makeBentShapeRebar
from LShapeRebar import makeLShapeRebar
from RebarData import RebarTypes


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
    cross_facename = getFacenamesforBeamReinforcement(facename, structure)[0]
    if parallel_rebar_type == RebarTypes.straight:
        parallel_rebars = makeStraightRebar(
            parallel_front_cover,
            (
                f"{mesh_cover_along} Side",
                parallel_top_cover
                if mesh_cover_along == "Top"
                else parallel_bottom_cover,
            ),
            parallel_right_cover,
            parallel_left_cover,
            parallel_diameter,
            parallel_amount_spacing_check,
            parallel_amount_spacing_value,
            "Horizontal",
            structure,
            facename,
        )
        parallel_rebars.OffsetEnd = parallel_rear_cover + parallel_diameter / 2

    elif parallel_rebar_type == RebarTypes.ushape:
        parallel_rebars = makeUShapeRebar(
            parallel_front_cover,
            parallel_bottom_cover,
            parallel_right_cover,
            parallel_left_cover,
            parallel_diameter,
            parallel_top_cover,
            parallel_rounding,
            parallel_amount_spacing_check,
            parallel_amount_spacing_value,
            mesh_cover_along,
            structure,
            facename,
        )
        parallel_rebars.OffsetEnd = parallel_rear_cover + parallel_diameter / 2

    elif parallel_rebar_type == RebarTypes.bentshape:
        parallel_rebars = makeBentShapeRebar(
            parallel_front_cover,
            parallel_bottom_cover,
            parallel_left_cover,
            parallel_right_cover,
            parallel_diameter,
            parallel_top_cover,
            parallel_bent_bar_length,
            parallel_bent_bar_angle,
            parallel_rounding,
            parallel_amount_spacing_check,
            parallel_amount_spacing_value,
            mesh_cover_along,
            structure,
            facename,
        )
        parallel_rebars.OffsetEnd = parallel_rear_cover + parallel_diameter / 2

        if parallel_distribution_rebars_check:
            parallel_face_length = getParametersOfFace(structure, facename)[0][
                0
            ]
            cover_along_length = parallel_diameter + (
                parallel_bottom_cover
                if mesh_cover_along == "Top"
                else parallel_top_cover
            )
            cover_along = (
                "Top Side" if mesh_cover_along == "Bottom" else "Bottom Side"
            )
            parallel_distribution_rebars_amount = (
                parallel_distribution_rebars_amount_spacing_value
            )
            if not parallel_distribution_rebars_amount_spacing_check:
                # calculate distribution rebars amount based on length of
                # arm of bent shape rebar and covers for distribution rebars
                parallel_distribution_rebars_amount = (
                    get_rebar_amount_from_spacing(
                        parallel_bent_bar_length
                        + parallel_left_cover
                        - cross_front_cover
                        - cross_diameter,
                        parallel_distribution_rebars_diameter,
                        parallel_distribution_rebars_amount_spacing_value,
                    )
                )
            parallel_left_distribution_rebars = makeStraightRebar(
                cross_front_cover + cross_diameter,
                (
                    cover_along,
                    cover_along_length,
                ),
                cross_right_cover,
                cross_left_cover,
                parallel_distribution_rebars_diameter,
                True,
                parallel_distribution_rebars_amount,
                "Horizontal",
                structure,
                cross_facename,
            )
            parallel_left_distribution_rebars.OffsetEnd = (
                parallel_face_length
                - parallel_bent_bar_length
                - parallel_left_cover
                + parallel_distribution_rebars_diameter / 2
            )

            parallel_right_front_cover = (
                parallel_face_length
                - parallel_right_cover
                - parallel_bent_bar_length
                + parallel_distribution_rebars_diameter / 2
            )
            parallel_right_distribution_rebars = makeStraightRebar(
                parallel_right_front_cover,
                (
                    cover_along,
                    cover_along_length,
                ),
                cross_right_cover,
                cross_left_cover,
                parallel_distribution_rebars_diameter,
                True,
                parallel_distribution_rebars_amount,
                "Horizontal",
                structure,
                cross_facename,
            )
            parallel_right_distribution_rebars.OffsetEnd = (
                cross_rear_cover
                + cross_diameter
                + cross_distribution_rebars_diameter / 2
            )

    elif parallel_rebar_type == RebarTypes.lshape:

        if parallel_l_shape_hook_orintation == "Alternate":
            cross_face_length = getParametersOfFace(structure, cross_facename)[
                0
            ][0]
            if not parallel_amount_spacing_check:
                parallel_rebars_amount = get_rebar_amount_from_spacing(
                    cross_face_length,
                    parallel_diameter,
                    parallel_amount_spacing_value,
                )
            else:
                parallel_rebars_amount = parallel_amount_spacing_value

            parallel_modified_amount_spacing_value_2 = (
                parallel_rebars_amount // 2
            )
            parallel_modified_amount_spacing_value_1 = (
                parallel_rebars_amount
                - parallel_modified_amount_spacing_value_2
            )
            if parallel_rebars_amount == 1:
                parallel_interval = parallel_front_cover
            else:
                parallel_interval = (
                    cross_face_length
                    - parallel_front_cover
                    - parallel_rear_cover
                ) / (parallel_rebars_amount - 1)
            parallel_modified_front_cover = (
                parallel_front_cover + parallel_interval
            )
            if parallel_modified_amount_spacing_value_1:
                parallel_left_rebars = makeLShapeRebar(
                    parallel_front_cover,
                    parallel_bottom_cover,
                    parallel_left_cover,
                    parallel_right_cover,
                    parallel_diameter,
                    parallel_top_cover,
                    parallel_rounding,
                    True,
                    parallel_modified_amount_spacing_value_1,
                    f"{mesh_cover_along} Left",
                    structure,
                    facename,
                )
                parallel_left_rebars.OffsetEnd = (
                    parallel_rear_cover
                    + parallel_diameter / 2
                    + (
                        parallel_interval
                        if parallel_modified_amount_spacing_value_1
                        == parallel_modified_amount_spacing_value_2
                        else 0
                    )
                )

            if parallel_modified_amount_spacing_value_2:
                parallel_right_rebars = makeLShapeRebar(
                    parallel_modified_front_cover,
                    parallel_bottom_cover,
                    parallel_left_cover,
                    parallel_right_cover,
                    parallel_diameter,
                    parallel_top_cover,
                    parallel_rounding,
                    True,
                    parallel_modified_amount_spacing_value_2,
                    f"{mesh_cover_along} Right",
                    structure,
                    facename,
                )
                parallel_right_rebars.OffsetEnd = (
                    parallel_rear_cover
                    + parallel_diameter / 2
                    + (
                        parallel_interval
                        if (
                            parallel_modified_amount_spacing_value_1
                            - parallel_modified_amount_spacing_value_2
                        )
                        == 1
                        else 0
                    )
                )
        else:
            parallel_rebars = makeLShapeRebar(
                parallel_front_cover,
                parallel_bottom_cover,
                parallel_left_cover,
                parallel_right_cover,
                parallel_diameter,
                parallel_top_cover,
                parallel_rounding,
                True,
                parallel_amount_spacing_value,
                f"{mesh_cover_along} {parallel_l_shape_hook_orintation}",
                structure,
                facename,
            )
            parallel_rebars.OffsetEnd = (
                parallel_rear_cover + parallel_diameter / 2
            )

    if cross_rebar_type == RebarTypes.straight:
        cross_rebars = makeStraightRebar(
            cross_front_cover,
            (
                f"{mesh_cover_along} Side",
                cross_top_cover - parallel_diameter
                if mesh_cover_along == "Top"
                else cross_bottom_cover + parallel_diameter,
            ),
            cross_right_cover,
            cross_left_cover,
            cross_diameter,
            cross_amount_spacing_check,
            cross_amount_spacing_value,
            "Horizontal",
            structure,
            cross_facename,
        )
        cross_rebars.OffsetEnd = cross_rear_cover + cross_diameter / 2

    elif cross_rebar_type == RebarTypes.ushape:
        cross_rebars = makeUShapeRebar(
            cross_front_cover,
            cross_bottom_cover
            + (parallel_diameter if mesh_cover_along == "Bottom" else 0),
            cross_right_cover,
            cross_left_cover,
            cross_diameter,
            cross_top_cover
            - (parallel_diameter if mesh_cover_along == "Top" else 0),
            cross_rounding,
            cross_amount_spacing_check,
            cross_amount_spacing_value,
            mesh_cover_along,
            structure,
            cross_facename,
        )
        cross_rebars.OffsetEnd = cross_rear_cover + cross_diameter / 2

    elif cross_rebar_type == RebarTypes.bentshape:
        cross_bottom_cover = cross_bottom_cover + (
            parallel_diameter if mesh_cover_along == "Bottom" else 0
        )
        cross_top_cover = cross_top_cover - (
            parallel_diameter if mesh_cover_along == "Top" else 0
        )
        # prevent overlaping of arms in BentShapeRebars
        if parallel_rebar_type == RebarTypes.bentshape:
            if mesh_cover_along == "Bottom":
                required_rebar_axises_sepration = cross_diameter
                if (
                    cross_distribution_rebars_check
                    and cross_top_cover < parallel_top_cover
                ):
                    required_rebar_axises_sepration = (
                        required_rebar_axises_sepration
                        + cross_distribution_rebars_diameter
                    )
                elif parallel_distribution_rebars_check:
                    required_rebar_axises_sepration = (
                        required_rebar_axises_sepration
                        + parallel_distribution_rebars_diameter
                    )
                cross_top_cover = set_minimum_seperation_distance(
                    cross_top_cover,
                    parallel_top_cover,
                    required_rebar_axises_sepration,
                )
            else:
                required_rebar_axises_sepration = cross_diameter
                if (
                    cross_distribution_rebars_check
                    and cross_bottom_cover < parallel_bottom_cover
                ):
                    required_rebar_axises_sepration = (
                        required_rebar_axises_sepration
                        + cross_distribution_rebars_diameter
                    )
                elif parallel_distribution_rebars_check:
                    required_rebar_axises_sepration = (
                        required_rebar_axises_sepration
                        + parallel_distribution_rebars_diameter
                    )
                cross_bottom_cover = set_minimum_seperation_distance(
                    cross_bottom_cover,
                    parallel_bottom_cover,
                    required_rebar_axises_sepration,
                )

        cross_rebars = makeBentShapeRebar(
            cross_front_cover,
            cross_bottom_cover,
            cross_left_cover,
            cross_right_cover,
            cross_diameter,
            cross_top_cover,
            cross_bent_bar_length,
            cross_bent_bar_angle,
            cross_rounding,
            cross_amount_spacing_check,
            cross_amount_spacing_value,
            mesh_cover_along,
            structure,
            cross_facename,
        )
        cross_rebars.OffsetEnd = cross_rear_cover + cross_diameter / 2

        if cross_distribution_rebars_check:
            cross_face_length = getParametersOfFace(structure, cross_facename)[
                0
            ][0]
            cover_along_length = cross_diameter + (
                cross_bottom_cover
                if mesh_cover_along == "Top"
                else cross_top_cover
            )
            cover_along = (
                "Top Side" if mesh_cover_along == "Bottom" else "Bottom Side"
            )
            cross_distribution_rebars_amount = (
                cross_distribution_rebars_amount_spacing_value
            )
            if not cross_distribution_rebars_amount_spacing_check:
                # calculate distribution rebars amount based on length of
                # arm of bent shape rebar and covers for distribution rebars
                cross_distribution_rebars_amount = (
                    get_rebar_amount_from_spacing(
                        cross_bent_bar_length
                        + cross_left_cover
                        - parallel_front_cover
                        - parallel_diameter,
                        cross_distribution_rebars_diameter,
                        cross_distribution_rebars_amount_spacing_value,
                    )
                )
            cross_left_distribution_rebars = makeStraightRebar(
                parallel_front_cover + parallel_diameter,
                (
                    cover_along,
                    cover_along_length,
                ),
                parallel_right_cover,
                parallel_left_cover,
                cross_distribution_rebars_diameter,
                True,
                cross_distribution_rebars_amount,
                "Horizontal",
                structure,
                facename,
            )
            cross_left_distribution_rebars.OffsetEnd = (
                cross_face_length
                - cross_bent_bar_length
                - cross_left_cover
                + cross_distribution_rebars_diameter / 2
            )

            cross_right_front_cover = (
                cross_face_length
                - cross_right_cover
                - cross_bent_bar_length
                + cross_distribution_rebars_diameter / 2
            )
            cross_right_distribution_rebars = makeStraightRebar(
                cross_right_front_cover,
                (
                    cover_along,
                    cover_along_length,
                ),
                parallel_right_cover,
                parallel_left_cover,
                cross_distribution_rebars_diameter,
                True,
                cross_distribution_rebars_amount,
                "Horizontal",
                structure,
                facename,
            )
            cross_right_distribution_rebars.OffsetEnd = (
                parallel_rear_cover
                + parallel_diameter
                + cross_distribution_rebars_diameter / 2
            )

    elif cross_rebar_type == RebarTypes.lshape:
        if cross_l_shape_hook_orintation == "Alternate":
            parallel_face_length = getParametersOfFace(structure, facename)[0][
                0
            ]
            if not cross_amount_spacing_check:
                cross_rebars_amount = get_rebar_amount_from_spacing(
                    parallel_face_length,
                    cross_diameter,
                    cross_amount_spacing_value,
                )
            else:
                cross_rebars_amount = cross_amount_spacing_value
            cross_modified_amount_spacing_value_2 = cross_rebars_amount // 2
            cross_modified_amount_spacing_value_1 = (
                cross_rebars_amount - cross_modified_amount_spacing_value_2
            )
            if cross_rebars_amount == 1:
                cross_interval = cross_front_cover
            else:
                cross_interval = (
                    parallel_face_length - cross_front_cover - cross_rear_cover
                ) / (cross_rebars_amount - 1)
            cross_modified_front_cover = cross_front_cover + cross_interval

            if cross_modified_amount_spacing_value_1:
                cross_left_rebars = makeLShapeRebar(
                    cross_front_cover,
                    cross_bottom_cover
                    + (
                        parallel_diameter if mesh_cover_along == "Bottom" else 0
                    ),
                    cross_left_cover,
                    cross_right_cover,
                    cross_diameter,
                    cross_top_cover
                    - (parallel_diameter if mesh_cover_along == "Top" else 0),
                    cross_rounding,
                    True,
                    cross_modified_amount_spacing_value_1,
                    f"{mesh_cover_along} Left",
                    structure,
                    cross_facename,
                )
                cross_left_rebars.OffsetEnd = (
                    cross_rear_cover
                    + cross_diameter / 2
                    + (
                        cross_interval
                        if cross_modified_amount_spacing_value_1
                        == cross_modified_amount_spacing_value_2
                        else 0
                    )
                )

            if cross_modified_amount_spacing_value_2:
                cross_right_rebars = makeLShapeRebar(
                    cross_modified_front_cover,
                    cross_bottom_cover
                    + (
                        parallel_diameter if mesh_cover_along == "Bottom" else 0
                    ),
                    cross_left_cover,
                    cross_right_cover,
                    cross_diameter,
                    cross_top_cover
                    - (parallel_diameter if mesh_cover_along == "Top" else 0),
                    cross_rounding,
                    True,
                    cross_modified_amount_spacing_value_2,
                    f"{mesh_cover_along} Right",
                    structure,
                    cross_facename,
                )
                cross_right_rebars.OffsetEnd = (
                    cross_rear_cover
                    + cross_diameter / 2
                    + (
                        cross_interval
                        if (
                            cross_modified_amount_spacing_value_1
                            - cross_modified_amount_spacing_value_2
                        )
                        == 1
                        else 0
                    )
                )
        else:
            cross_rebars = makeLShapeRebar(
                cross_front_cover,
                cross_bottom_cover
                + (parallel_diameter if mesh_cover_along == "Bottom" else 0),
                cross_left_cover,
                cross_right_cover,
                cross_diameter,
                cross_top_cover
                - (parallel_diameter if mesh_cover_along == "Top" else 0),
                cross_rounding,
                True,
                cross_amount_spacing_value,
                f"{mesh_cover_along} {cross_l_shape_hook_orintation}",
                structure,
                cross_facename,
            )
            cross_rebars.OffsetEnd = cross_rear_cover + cross_diameter / 2

    FreeCAD.ActiveDocument.recompute()


def set_minimum_seperation_distance(
    relative_distance, absolute_distance, min_seperation_distance
):
    """
    Get new relative distance having min_seperation_distance from
    absolute_distance
    """
    sepration_distance = relative_distance - absolute_distance
    if abs(sepration_distance) < min_seperation_distance:
        if sepration_distance < 0:
            relative_distance = absolute_distance - min_seperation_distance
        else:
            relative_distance = absolute_distance + min_seperation_distance
    return relative_distance
