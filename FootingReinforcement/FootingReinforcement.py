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

__title__ = "Footing Reinforcement"
__author__ = "Shiv Charan"
__url__ = "https://www.freecadweb.org"

import FreeCAD
from Rebarfunc import showWarning
from typing import Union, Tuple, Optional

from SlabReinforcement.SlabReinforcement import makeSlabReinforcement
from ColumnReinforcement.SingleTieMultipleRebars import (
    makeSingleTieMultipleRebars,
    makeSingleTieFourRebars,
)
from Rebarfunc import getFacenamesforFootingReinforcement, getParametersOfFace


def makeFootingReinforcement(
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
    column_front_cover: float,
    column_left_cover: float,
    column_right_cover: float,
    column_rear_cover: float,
    tie_top_cover: float,
    tie_bottom_cover: float,
    tie_bent_angle: int,
    tie_extension_factor: int,
    tie_diameter: float,
    tie_number_spacing_check: bool,
    tie_number_spacing_value: Union[float, int],
    column_main_rebar_diameter: float,
    column_main_rebars_t_offset: float,
    cross_amount_spacing_value: Union[float, int],
    column_width: float,
    column_length: float,
    xdir_column_amount_spacing_check: bool = True,
    xdir_column_amount_spacing_value: Union[float, int] = 1,
    ydir_column_amount_spacing_check: bool = True,
    ydir_column_amount_spacing_value: Union[float, int] = 1,
    parallel_rounding: Optional[int] = 2,
    parallel_l_shape_hook_orintation: Optional[str] = "Alternate",
    cross_rounding: Optional[int] = 2,
    cross_l_shape_hook_orintation: Optional[str] = "Alternate",
    column_main_rebars_type: Optional[str] = "StraightRebar",
    column_main_hook_orientation: Optional[str] = "Bottom Outside",
    column_main_hook_extend_along: Optional[str] = "x-axis",
    column_l_main_rebar_rounding: Optional[int] = 2,
    column_main_hook_extension: Optional[float] = 40,
    column_sec_rebar_check: Optional[bool] = False,
    column_sec_rebars_t_offset: Optional[Tuple[float, float]] = (400, 400),
    column_sec_rebars_number_diameter: Optional[Tuple[float, float]] = (
        "1#8mm+1#8mm+1#8mm",
        "1#8mm+1#8mm+1#8mm",
    ),
    column_sec_rebars_type: Optional[Tuple[str, str]] = (
        "StraightRebar",
        "StraightRebar",
    ),
    column_sec_hook_orientation: Optional[Tuple[str, str]] = (
        "Top Inside",
        "Top Inside",
    ),
    column_l_sec_rebar_rounding: Optional[Tuple[int, int]] = (2, 2),
    column_sec_hook_extension: Optional[Tuple[float, float]] = (40, 40),
    mesh_cover_along: str = "Bottom",
    structure: Optional[Tuple] = None,
    facename: Optional[str] = None,
):
    """Generate Footing Reinforcement

    Parameters
    ----------
    parallel_rebar_type: str
        Type of rebar for parallel rebars for Footing reinforcement.
        It can have four values 'StraightRebar','LShapeRebar', 'UShapeRebar'.
    parallel_front_cover: float
        The distance between parallel rebar and selected face.
    parallel_rear_cover: float
        Rear cover for footing reinforcement of parallel rebars.
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
        It can have four values 'StraightRebar','LShapeRebar', 'UShapeRebar'.
    cross_front_cover: float
        The distance between cross rebar and cross_face (face perpendicular to selected face).
    cross_rear_cover: float
        Rear cover for footing reinforcement of cross rebars.
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
    cross_l_shape_hook_orintation: str
        It represents orintation of hook of cross L-Shape rebar if cross_rebar_type
        is LShapeRebar.
        It can have tree values "Left", "Right", "Alternate"
    parallel_rounding: int
        A rounding value to be applied to the corners of the bars, expressed
        in times the parallel_diameter.
    parallel_l_shape_hook_orintation: str
        It represents orintation of hook of parallel L-Shape rebar if parallel_rebar_type
        is LShapeRebar.
        It can have tree values "Left", "Right", "Alternate".
    column_front_cover: float
        Distance between selected face and front columns.
    column_left_cover: float,
        Distance between left face and left columns.
    column_right_cover: float
        Distance between right face and right columns.
    column_rear_cover: float
        Distance between rear face and rear columns.
    tie_top_cover: float
        Top cover for ties outside footing.
    tie_bottom_cover: float
        Bottom cover of ties from Bottom footing rebars mesh.
    tie_bent_angle: int
        Bent angle for ties.
    tie_extension_factor: int
        Extension factor for ties extended edge.
    tie_diameter: float
        Diameter of ties.
    tie_number_spacing_check: bool
        If is set to True, then value of tie_number_spacing_value is used as
        rebars count else tie_number_spacing_value's value is used as spacing
        in ties.
    tie_number_spacing_value: float
        It contains count of rebars or spacing between ties based on
        value of tie_number_spacing_check.
    column_main_rebar_diameter: float
        Diameter of main rebars in columns.
    column_main_rebars_t_offset: float
        Top offset of main rebars in column outside footing.
    column_width: float
        Width of columns.
    column_length: float
        Length of columns.
    xdir_column_amount_spacing_check: bool
        If is set to True, then value of xdir_column_amount_spacing_value is used as
        rebars count else xdir_column_amount_spacing_value's value is used as spacing
        between columns in x direction.
    xdir_column_amount_spacing_value: int
        It contains count of rebars or spacing between  between columns in x direction based on
        value of xdir_column_amount_spacing_check.
    ydir_column_amount_spacing_check: bool
        If is set to True, then value of ydir_column_amount_spacing_value is used as
        rebars count else ydir_column_amount_spacing_value's value is used as spacing
        between columns in y direction.
    ydir_column_amount_spacing_value: int
        It contains count of rebars or spacing between  between columns in x direction based on
        value of ydir_column_amount_spacing_check.
    column_main_rebars_type: Optional[str] ,
        Rebar type for main rebars of column. It takes two different inputs for 'StraightRebar',
        'LShapeRebar'. Default  is StraightRebar.
    column_main_hook_orientation: Optional[str],
        Hook orientation of main rebars in columns if column_main_rebars_type is LShapeRebar.
        It takes eight different orientations input for L-shaped hooks i.e.
        'Top Inside', 'Top Outside', 'Bottom Inside', 'Bottom Outside', 'Top Left',
        'Top Right', 'Bottom Left', 'Bottom Right'.
    column_main_hook_extend_along: Optional[str],
        Direction of main rebar (LShapeRebar) hook. it has two option "x-axis" and "y-axis".
    column_l_main_rebar_rounding: Optional[int],
        A rounding value to be applied to the corners of the bars, expressed
        in times the column_main_rebar_diameter.
    column_main_hook_extension: Optional[float],
        It specifies length of hook of main rebar (LShapeRebar).
    column_sec_rebar_check: Optional[bool]
        If True add secoundary x and y direction rebars in columns.
    column_sec_rebars_t_offset: Optional[Tuple[ float,float]],
        Top offset for secounday rebars of column.
        Syntax: (<value_for_sec_xdir_rebars>, <value_for_sec_ydir_rebars>)
    column_sec_rebars_number_diameter: Optional[Tuple[ float,float]],
        Diameter of secoundary rebars of columns.
        Syntax: (<value_for_sec_xdir_rebars>, <value_for_sec_ydir_rebars>)
    column_sec_rebars_type: Optional[Tuple[ str,str]],
        Rebar type of secoundary rebars of columns.
        Syntax: (<value_for_sec_xdir_rebars>, <value_for_sec_ydir_rebars>)
    column_sec_hook_orientation: Optional[Tuple[ str,str]],
        Hook Orientation of secoundary rebars of columns.
        In column_sec_hook_orientation(<xdir_rebars_orientation>, <ydir_rebars_orientation>).
        Value of xdir_rebars_orientation can be: 'Top Inside', 'Top Outside',
        'Bottom Inside', 'Bottom Outside', 'Top Upward', 'Top Downward', 'Bottom
        Upward', 'Bottom Downward'.
        Value of ydir_rebars_orientation can be: 'Top Inside', 'Top Outside',
        'Bottom Inside', 'Bottom Outside', 'Top Left', 'Top Right', 'Bottom
        Left', 'Bottom Right'.
        Syntax: (<value_for_sec_xdir_rebars>, <value_for_sec_ydir_rebars>)
    column_l_sec_rebar_rounding: Optional[Tuple[ int,int]],
        A rounding value to be applied to the corners of the bars, expressed
        in times the column_sec_rebars_number_diameter.
        Syntax: (<value_for_sec_xdir_rebars>, <value_for_sec_ydir_rebars>)
    column_sec_hook_extension: Optional[Tuple[ float,float]],
        Hook length of secoundary rebars (LShapeRebar) of columns.
        Syntax: (<value_for_sec_xdir_rebars>, <value_for_sec_ydir_rebars>)
    mesh_cover_along: str
        It can have two values "Top", "Bottom" and "Both". It represent alignment of
        rebar mesh along top or bottom face of structure.
        If "Both" is used as input then footing mesh will be added to top and bottom of footing.
    structure: Arch structure object
        Arch structure object.
        Default is None
    facename: str
        selected face of structure.
        Default is None

    Note: Type of
        column_sec_rebars_t_offset
        column_sec_rebars_number_diameter
        column_sec_rebars_type
        column_sec_hook_orientation
        column_l_sec_rebar_rounding
        column_sec_hook_extension arguments is a tuple.
    Syntax: (<value_for_sec_xdir_rebars>, <value_for_sec_ydir_rebars>).
    """

    selected_face_hight = getParametersOfFace(structure, facename)[0][1]

    top_facename = getFacenamesforFootingReinforcement(facename, structure)[1]
    column_b_offset = parallel_bottom_cover + parallel_diameter + cross_diameter
    top_face_width, top_face_length = getParametersOfFace(
        structure, top_facename
    )[0]

    # remove cover length from face lengths
    top_face_width = top_face_width - column_left_cover
    top_face_length = top_face_length - column_front_cover

    # Calculate spacing value from column amount in x-axis direction
    if xdir_column_amount_spacing_check:
        xdir_column_amount_value = xdir_column_amount_spacing_value
        empty_space_length = (
            top_face_length
            - column_rear_cover
            - (xdir_column_amount_spacing_value) * column_length
        )
        if empty_space_length < 0:
            # given X direction column amount is too large to add in given structure
            showWarning(
                "Error: Given X direction column amount is too large for given structure"
            )
            return None
        empty_space_length = empty_space_length if empty_space_length > 0 else 0
        if xdir_column_amount_spacing_value > 1:
            xdir_column_spacing_value = empty_space_length / (
                xdir_column_amount_spacing_value - 1
            )
        else:
            xdir_column_spacing_value = empty_space_length

    else:
        xdir_column_spacing_value = xdir_column_amount_spacing_value
        xdir_column_amount_value = 1
        empty_space_length = top_face_length - column_rear_cover - column_length
        while empty_space_length > 0:
            empty_space_length = (
                empty_space_length - column_length - xdir_column_spacing_value
            )
            xdir_column_amount_value = xdir_column_amount_value + 1

    # Calculate spacing value from column amount in y-axis direction
    if ydir_column_amount_spacing_check:
        ydir_column_amount_value = ydir_column_amount_spacing_value
        empty_space_length = (
            top_face_width
            - column_right_cover
            - (ydir_column_amount_spacing_value) * column_width
        )
        if empty_space_length < 0:
            # given Y direction column amount is too large to add in given structure
            showWarning(
                "Error: Given Y direction column amount is too large for given structure"
            )
            return None
        print(xdir_column_amount_spacing_value)
        if xdir_column_amount_spacing_value > 1:
            ydir_column_spacing_value = empty_space_length / (
                ydir_column_amount_spacing_value - 1
            )
        else:
            ydir_column_spacing_value = empty_space_length
    else:
        ydir_column_spacing_value = ydir_column_amount_spacing_value
        ydir_column_amount_value = 1
        empty_space_length = top_face_width - column_right_cover - column_width
        while empty_space_length > 0:
            empty_space_length = (
                empty_space_length - column_width - ydir_column_spacing_value
            )
            ydir_column_amount_value = ydir_column_amount_value + 1

    makeSlabReinforcement(
        parallel_rebar_type=parallel_rebar_type,
        parallel_front_cover=parallel_front_cover,
        parallel_rear_cover=parallel_rear_cover,
        parallel_left_cover=parallel_left_cover,
        parallel_right_cover=parallel_right_cover,
        parallel_top_cover=parallel_top_cover
        if mesh_cover_along != "Both"
        else parallel_top_cover + selected_face_hight / 2,
        parallel_bottom_cover=parallel_bottom_cover,
        parallel_diameter=parallel_diameter,
        parallel_amount_spacing_check=parallel_amount_spacing_check,
        parallel_amount_spacing_value=parallel_amount_spacing_value,
        cross_rebar_type=cross_rebar_type,
        cross_front_cover=cross_front_cover,
        cross_rear_cover=cross_rear_cover,
        cross_left_cover=cross_left_cover,
        cross_right_cover=cross_right_cover,
        cross_top_cover=cross_top_cover
        if mesh_cover_along != "Both"
        else cross_top_cover + selected_face_hight / 2,
        cross_bottom_cover=cross_bottom_cover,
        cross_diameter=cross_diameter,
        cross_amount_spacing_check=cross_amount_spacing_check,
        cross_amount_spacing_value=cross_amount_spacing_value,
        cross_rounding=cross_rounding,
        cross_l_shape_hook_orintation=cross_l_shape_hook_orintation,
        cross_distribution_rebars_check=False,
        parallel_rounding=parallel_rounding,
        parallel_l_shape_hook_orintation=parallel_l_shape_hook_orintation,
        parallel_distribution_rebars_check=False,
        mesh_cover_along=mesh_cover_along
        if mesh_cover_along != "Both"
        else "Bottom",
        structure=structure,
        facename=facename,
    )

    if mesh_cover_along == "Both":
        makeSlabReinforcement(
            parallel_rebar_type=parallel_rebar_type,
            parallel_front_cover=parallel_front_cover,
            parallel_rear_cover=parallel_rear_cover,
            parallel_left_cover=parallel_left_cover,
            parallel_right_cover=parallel_right_cover,
            parallel_top_cover=parallel_top_cover,
            parallel_bottom_cover=parallel_bottom_cover
            + selected_face_hight / 2,
            parallel_diameter=parallel_diameter,
            parallel_amount_spacing_check=parallel_amount_spacing_check,
            parallel_amount_spacing_value=parallel_amount_spacing_value,
            cross_rebar_type=cross_rebar_type,
            cross_front_cover=cross_front_cover,
            cross_rear_cover=cross_rear_cover,
            cross_left_cover=cross_left_cover,
            cross_right_cover=cross_right_cover,
            cross_top_cover=cross_top_cover,
            cross_bottom_cover=cross_bottom_cover + selected_face_hight / 2,
            cross_diameter=cross_diameter,
            cross_amount_spacing_check=cross_amount_spacing_check,
            cross_amount_spacing_value=cross_amount_spacing_value,
            cross_rounding=cross_rounding,
            cross_l_shape_hook_orintation=cross_l_shape_hook_orintation,
            cross_distribution_rebars_check=False,
            parallel_rounding=parallel_rounding,
            parallel_l_shape_hook_orintation=parallel_l_shape_hook_orintation,
            parallel_distribution_rebars_check=False,
            mesh_cover_along="Top",
            structure=structure,
            facename=facename,
        )

    if column_sec_rebar_check:
        for column in range(ydir_column_amount_value):
            for row in range(xdir_column_amount_value):
                modified_l_cover_of_tie = column_left_cover + (column) * (
                    column_width + ydir_column_spacing_value
                )
                modified_r_cover_of_tie = (
                    top_face_width
                    - (column + 1) * (column_width)
                    - (column) * (ydir_column_spacing_value)
                )
                modified_t_cover_of_tie = (
                    top_face_length
                    - (row + 1) * (column_length)
                    - (row) * (xdir_column_spacing_value)
                )
                modified_b_cover_of_tie = column_front_cover + (row) * (
                    column_length + xdir_column_spacing_value
                )
                columnReinforcementGroup = makeSingleTieMultipleRebars(
                    l_cover_of_tie=modified_l_cover_of_tie,
                    r_cover_of_tie=modified_r_cover_of_tie,
                    t_cover_of_tie=modified_t_cover_of_tie,
                    b_cover_of_tie=modified_b_cover_of_tie,
                    offset_of_tie=tie_top_cover,
                    bent_angle=tie_bent_angle,
                    extension_factor=tie_extension_factor,
                    dia_of_tie=tie_diameter,
                    number_spacing_check=tie_number_spacing_check,
                    number_spacing_value=tie_number_spacing_value,
                    dia_of_main_rebars=column_main_rebar_diameter,
                    main_rebars_t_offset=-column_main_rebars_t_offset,
                    main_rebars_b_offset=column_b_offset,
                    main_rebars_type=column_main_rebars_type,
                    main_hook_orientation=column_main_hook_orientation,
                    main_hook_extend_along=column_main_hook_extend_along,
                    l_main_rebar_rounding=column_l_main_rebar_rounding,
                    main_hook_extension=column_main_hook_extension,
                    sec_rebars_t_offset=tuple(
                        -x for x in column_sec_rebars_t_offset
                    ),
                    sec_rebars_b_offset=(column_b_offset, column_b_offset),
                    sec_rebars_number_diameter=column_sec_rebars_number_diameter,
                    sec_rebars_type=column_sec_rebars_type,
                    sec_hook_orientation=column_sec_hook_orientation,
                    l_sec_rebar_rounding=column_l_sec_rebar_rounding,
                    sec_hook_extension=column_sec_hook_extension,
                    structure=structure,
                    facename=top_facename,
                )
                columnReinforcementGroup.RebarGroups[0].Ties[0].OffsetStart = (
                    selected_face_hight
                    - 2 * column_b_offset
                    - tie_diameter
                    - tie_bottom_cover
                )
    else:
        for column in range(ydir_column_amount_value):
            for row in range(xdir_column_amount_value):
                modified_l_cover_of_tie = column_left_cover + (column) * (
                    column_width + ydir_column_spacing_value
                )
                modified_r_cover_of_tie = (
                    top_face_width
                    - (column + 1) * (column_width)
                    - (column) * (ydir_column_spacing_value)
                )
                modified_t_cover_of_tie = (
                    top_face_length
                    - (row + 1) * (column_length)
                    - (row) * (xdir_column_spacing_value)
                )
                modified_b_cover_of_tie = column_front_cover + (row) * (
                    column_length + xdir_column_spacing_value
                )
                columnReinforcementGroup = makeSingleTieFourRebars(
                    l_cover_of_tie=modified_l_cover_of_tie,
                    r_cover_of_tie=modified_r_cover_of_tie,
                    t_cover_of_tie=modified_t_cover_of_tie,
                    b_cover_of_tie=modified_b_cover_of_tie,
                    offset_of_tie=tie_top_cover,
                    bent_angle=tie_bent_angle,
                    extension_factor=tie_extension_factor,
                    dia_of_tie=tie_diameter,
                    number_spacing_check=tie_number_spacing_check,
                    number_spacing_value=tie_number_spacing_value,
                    dia_of_rebars=column_main_rebar_diameter,
                    t_offset_of_rebars=-column_main_rebars_t_offset,
                    b_offset_of_rebars=column_b_offset,
                    rebar_type=column_main_rebars_type,
                    hook_orientation=column_main_hook_orientation,
                    hook_extend_along=column_main_hook_extend_along,
                    l_rebar_rounding=column_l_main_rebar_rounding,
                    hook_extension=column_main_hook_extension,
                    structure=structure,
                    facename=top_facename,
                )
                columnReinforcementGroup.ties_group.Ties[0].OffsetStart = (
                    selected_face_hight
                    - 2 * column_b_offset
                    - tie_diameter
                    - tie_bottom_cover
                )

    FreeCAD.ActiveDocument.recompute()
