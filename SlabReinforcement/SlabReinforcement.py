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
    rebar_type,
    front_cover,
    rear_cover,
    left_cover,
    right_cover,
    top_cover,
    bottom_cover,
    diameter,
    amount_spacing_check,
    amount_spacing_value,
    rounding=2,
    mesh_cover_along="Bottom",
    structure=None,
    facename=None,
    bent_bar_length=50,
    bent_bar_angle=135,
):
    """Generate Slab Reinforcement

    Parameters
    ----------
    rebar_type: str
        Type of rebar for parallel and cross rebars for slab reinforcement.
        It can have four values 'StraightRebar','LShapeRebar', 'UShapeRebar',
        'BentShapeRebar'.
    front_cover: float
        The distance between rebar and selected face.
    rear_cover: float
        Front cover for slab reinforcement
    left_cover: float
        The distance between the left end of the rebar to the left face of
        the structure.
    right_cover: float
        The distance between the right end of the rebar to right face of
        the structure.
    top_cover: float
        The distance between rebar from the top face of the structure.
    bottom_cover: float
        The distance between rebar from the bottom face of the structure.
    diameter: float
        Diameter of rebars.
    amount_spacing_check: bool
        If is set to True, then value of amount_spacing_value is used as
        rebars count else amount_spacing_value's value is used as spacing
        in rebars.
    amount_spacing_value: float or int
        It contains count of rebars or spacing between rebars based on
        value of amount_spacing_check.
    rounding: int
        A rounding value to be applied to the corners of the bars, expressed
        in times the diameter.
    mesh_cover_along: str
        It can have two values "Top" and "Bottom". It represent alignment of
        rebar mesh along top or bottom face of structure.
    structure: Arch structure object
        Arch structure object.
        Default is None
    facename: str
        selected face of structure.
        Default is None
    bent_bar_length: float
        It represents arm's length of bent shape rebar when rebar_type is
        BentShapeRebar
    bent_bar_angle: int
        It represents angle for bent shape rebar when rebar_type is
        BentShapeRebar
    """
    cross_facename = getFacenamesforBeamReinforcement(facename, structure)[0]
    if rebar_type == RebarTypes.straight:
        parallel_rebars = makeStraightRebar(
            front_cover,
            (
                f"{mesh_cover_along} Side",
                top_cover if mesh_cover_along == "Top" else bottom_cover,
            ),
            right_cover,
            left_cover,
            diameter,
            amount_spacing_check,
            amount_spacing_value,
            "Horizontal",
            structure,
            facename,
        )
        parallel_rebars.OffsetEnd = rear_cover + diameter / 2
        cross_rebars = makeStraightRebar(
            front_cover,
            (
                f"{mesh_cover_along} Side",
                top_cover - diameter
                if mesh_cover_along == "Top"
                else bottom_cover + diameter,
            ),
            right_cover,
            left_cover,
            diameter,
            amount_spacing_check,
            amount_spacing_value,
            "Horizontal",
            structure,
            cross_facename,
        )
        cross_rebars.OffsetEnd = rear_cover + diameter / 2
    elif rebar_type == RebarTypes.ushape:
        parallel_rebars = makeUShapeRebar(
            front_cover,
            bottom_cover,
            right_cover,
            left_cover,
            diameter,
            top_cover,
            rounding,
            amount_spacing_check,
            amount_spacing_value,
            mesh_cover_along,
            structure,
            facename,
        )
        parallel_rebars.OffsetEnd = rear_cover + diameter / 2
        cross_rebars = makeUShapeRebar(
            front_cover,
            bottom_cover + (diameter if mesh_cover_along == "Bottom" else 0),
            right_cover,
            left_cover,
            diameter,
            top_cover - (diameter if mesh_cover_along == "Top" else 0),
            rounding,
            amount_spacing_check,
            amount_spacing_value,
            mesh_cover_along,
            structure,
            cross_facename,
        )
        cross_rebars.OffsetEnd = rear_cover + diameter / 2

    elif rebar_type == RebarTypes.bentshape:
        parallel_rebars = makeBentShapeRebar(
            front_cover,
            bottom_cover,
            left_cover,
            right_cover,
            diameter,
            top_cover,
            bent_bar_length,
            bent_bar_angle,
            rounding,
            amount_spacing_check,
            amount_spacing_value,
            mesh_cover_along,
            structure,
            facename,
        )
        parallel_rebars.OffsetEnd = rear_cover + diameter / 2
        cross_rebars = makeBentShapeRebar(
            front_cover,
            bottom_cover + (diameter if mesh_cover_along == "Bottom" else 0),
            left_cover,
            right_cover,
            diameter,
            top_cover - (diameter if mesh_cover_along == "Top" else 0),
            bent_bar_length,
            bent_bar_angle,
            rounding,
            amount_spacing_check,
            amount_spacing_value,
            mesh_cover_along,
            structure,
            cross_facename,
        )
        cross_rebars.OffsetEnd = rear_cover + diameter / 2

    elif rebar_type == RebarTypes.lshape:
        cross_face_length = getParametersOfFace(structure, cross_facename)[0][0]
        parallel_face_length = getParametersOfFace(structure, facename)[0][0]
        if not amount_spacing_check:
            parallel_rebars_amount = get_rebar_amount_from_spacing(
                cross_face_length, diameter, amount_spacing_value
            )
            cross_rebars_amount = get_rebar_amount_from_spacing(
                parallel_face_length, diameter, amount_spacing_value
            )
        else:
            parallel_rebars_amount = amount_spacing_value
            cross_rebars_amount = amount_spacing_value

        parallel_modified_amount_spacing_value_2 = parallel_rebars_amount // 2
        parallel_modified_amount_spacing_value_1 = (
            parallel_rebars_amount - parallel_modified_amount_spacing_value_2
        )
        if parallel_rebars_amount == 1:
            parallel_interval = front_cover
        else:
            parallel_interval = (
                cross_face_length - front_cover - rear_cover
            ) / (parallel_rebars_amount - 1)
        parallel_modified_front_cover = front_cover + parallel_interval

        cross_modified_amount_spacing_value_2 = cross_rebars_amount // 2
        cross_modified_amount_spacing_value_1 = (
            cross_rebars_amount - cross_modified_amount_spacing_value_2
        )
        if cross_rebars_amount == 1:
            cross_interval = front_cover
        else:
            cross_interval = (
                parallel_face_length - front_cover - rear_cover
            ) / (cross_rebars_amount - 1)
        cross_modified_front_cover = front_cover + cross_interval

        if parallel_modified_amount_spacing_value_1:
            parallel_left_rebars = makeLShapeRebar(
                front_cover,
                bottom_cover,
                left_cover,
                right_cover,
                diameter,
                top_cover,
                rounding,
                True,
                parallel_modified_amount_spacing_value_1,
                f"{mesh_cover_along} Left",
                structure,
                facename,
            )
            parallel_left_rebars.OffsetEnd = (
                rear_cover
                + diameter / 2
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
                bottom_cover,
                left_cover,
                right_cover,
                diameter,
                top_cover,
                rounding,
                True,
                parallel_modified_amount_spacing_value_2,
                f"{mesh_cover_along} Right",
                structure,
                facename,
            )
            parallel_right_rebars.OffsetEnd = (
                rear_cover
                + diameter / 2
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

        if cross_modified_amount_spacing_value_1:
            cross_left_rebars = makeLShapeRebar(
                front_cover,
                bottom_cover
                + (diameter if mesh_cover_along == "Bottom" else 0),
                left_cover,
                right_cover,
                diameter,
                top_cover - (diameter if mesh_cover_along == "Top" else 0),
                rounding,
                True,
                cross_modified_amount_spacing_value_1,
                f"{mesh_cover_along} Left",
                structure,
                cross_facename,
            )
            cross_left_rebars.OffsetEnd = (
                rear_cover
                + diameter / 2
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
                bottom_cover
                + (diameter if mesh_cover_along == "Bottom" else 0),
                left_cover,
                right_cover,
                diameter,
                top_cover - (diameter if mesh_cover_along == "Top" else 0),
                rounding,
                True,
                cross_modified_amount_spacing_value_2,
                f"{mesh_cover_along} Right",
                structure,
                cross_facename,
            )
            cross_right_rebars.OffsetEnd = (
                rear_cover
                + diameter / 2
                + +(
                    cross_interval
                    if (
                        cross_modified_amount_spacing_value_1
                        - cross_modified_amount_spacing_value_2
                    )
                    == 1
                    else 0
                )
            )

    FreeCAD.ActiveDocument.recompute()
