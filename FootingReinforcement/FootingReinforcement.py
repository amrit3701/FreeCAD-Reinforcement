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

from FootingReinforcement.FootingReinforcementObject import (
    FootingReinforcementGroup,
    _FootingReinforcementViewProviderGroup,
)

if FreeCAD.GuiUp:
    import FreeCADGui


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
    if not structure and not facename:
        if FreeCAD.GuiUp:
            selected_obj = FreeCADGui.Selection.getSelectionEx()[0]
            structure = selected_obj.Object
            facename = selected_obj.SubElementNames[0]
        else:
            showWarning("Error: Pass structure and facename arguments")
            return None

    footingReinforcementGroup = FootingReinforcementGroup().Object
    if FreeCAD.GuiUp:
        _FootingReinforcementViewProviderGroup(
            footingReinforcementGroup.ViewObject
        )

    footingReinforcementGroup.IsMakeOrEditRequired = False
    footingReinforcementGroup.MeshCoverAlong = mesh_cover_along
    footingReinforcementGroup.Facename = facename
    footingReinforcementGroup.Structure = structure
    footingReinforcementGroup.ParallelRebarType = parallel_rebar_type
    footingReinforcementGroup.ParallelFrontCover = parallel_front_cover
    footingReinforcementGroup.ParallelRearCover = parallel_rear_cover
    footingReinforcementGroup.ParallelLeftCover = parallel_left_cover
    footingReinforcementGroup.ParallelRightCover = parallel_right_cover
    footingReinforcementGroup.ParallelTopCover = parallel_top_cover
    footingReinforcementGroup.ParallelBottomCover = parallel_bottom_cover
    footingReinforcementGroup.ParallelDiameter = parallel_diameter
    footingReinforcementGroup.ParallelAmountSpacingCheck = (
        parallel_amount_spacing_check
    )
    if parallel_amount_spacing_check:
        footingReinforcementGroup.ParallelAmountValue = (
            parallel_amount_spacing_value
        )
    else:
        footingReinforcementGroup.ParallelSpacingValue = (
            parallel_amount_spacing_value
        )

    if parallel_rounding:
        footingReinforcementGroup.ParallelRounding = parallel_rounding
    if parallel_l_shape_hook_orintation:
        footingReinforcementGroup.ParallelLShapeHookOrintation = (
            parallel_l_shape_hook_orintation
        )

    footingReinforcementGroup.CrossRebarType = cross_rebar_type
    footingReinforcementGroup.CrossFrontCover = cross_front_cover
    footingReinforcementGroup.CrossRearCover = cross_rear_cover
    footingReinforcementGroup.CrossLeftCover = cross_left_cover
    footingReinforcementGroup.CrossRightCover = cross_right_cover
    footingReinforcementGroup.CrossTopCover = cross_top_cover
    footingReinforcementGroup.CrossBottomCover = cross_bottom_cover
    footingReinforcementGroup.CrossDiameter = cross_diameter
    footingReinforcementGroup.CrossAmountSpacingCheck = (
        cross_amount_spacing_check
    )
    if cross_amount_spacing_check:
        footingReinforcementGroup.CrossAmountValue = cross_amount_spacing_value
    else:
        footingReinforcementGroup.CrossSpacingValue = cross_amount_spacing_value
    if cross_rounding:
        footingReinforcementGroup.CrossRounding = cross_rounding
    if cross_l_shape_hook_orintation:
        footingReinforcementGroup.CrossLShapeHookOrintation = (
            cross_l_shape_hook_orintation
        )

    footingReinforcementGroup.ColumnFrontCover = column_front_cover
    footingReinforcementGroup.ColumnLeftCover = column_left_cover
    footingReinforcementGroup.ColumnRightCover = column_right_cover
    footingReinforcementGroup.ColumnRearCover = column_rear_cover
    footingReinforcementGroup.TieTopCover = tie_top_cover
    footingReinforcementGroup.TieBottomCover = tie_bottom_cover
    footingReinforcementGroup.TieBentAngle = tie_bent_angle
    footingReinforcementGroup.TieExtensionFactor = tie_extension_factor
    footingReinforcementGroup.TieDiameter = tie_diameter
    footingReinforcementGroup.TieNumberSpacingCheck = tie_number_spacing_check
    if tie_number_spacing_check:
        footingReinforcementGroup.TieAmountValue = tie_number_spacing_value
    else:
        footingReinforcementGroup.TieSpacingValue = tie_number_spacing_value
    footingReinforcementGroup.ColumnMainRebarsDiameter = (
        column_main_rebar_diameter
    )
    footingReinforcementGroup.ColumnMainRebarsTopOffset = (
        column_main_rebars_t_offset
    )
    footingReinforcementGroup.ColumnWidth = column_width
    footingReinforcementGroup.ColumnLength = column_length
    footingReinforcementGroup.XDirColumnNumberSpacingCheck = (
        xdir_column_amount_spacing_check
    )
    if xdir_column_amount_spacing_check:
        footingReinforcementGroup.XDirColumnAmountValue = (
            xdir_column_amount_spacing_value
        )
    else:
        footingReinforcementGroup.XDirColumnSpacingValue = (
            xdir_column_amount_spacing_value
        )
    footingReinforcementGroup.YDirColumnNumberSpacingCheck = (
        ydir_column_amount_spacing_check
    )
    if ydir_column_amount_spacing_check:
        footingReinforcementGroup.YDirColumnAmountValue = (
            ydir_column_amount_spacing_value
        )
    else:
        footingReinforcementGroup.YDirColumnSpacingValue = (
            ydir_column_amount_spacing_value
        )
    if column_main_rebars_type:
        footingReinforcementGroup.ColumnMainRebarType = column_main_rebars_type
    if column_main_hook_orientation:
        footingReinforcementGroup.ColumnMainHookOrientation = (
            column_main_hook_orientation
        )
    if column_main_hook_extend_along:
        footingReinforcementGroup.ColumnMainHookExtendAlong = (
            column_main_hook_extend_along
        )
    if column_l_main_rebar_rounding:
        footingReinforcementGroup.ColumnMainLRebarRounding = (
            column_l_main_rebar_rounding
        )
    if column_main_hook_extension:
        footingReinforcementGroup.ColumnMainHookExtension = (
            column_main_hook_extension
        )
    if column_sec_rebar_check:
        footingReinforcementGroup.ColumnSecRebarsCheck = column_sec_rebar_check
    if column_sec_rebars_t_offset:
        footingReinforcementGroup.ColumnSecRebarsTopOffset = (
            column_sec_rebars_t_offset
        )
    if column_sec_rebars_number_diameter:
        footingReinforcementGroup.ColumnSecRebarsNumberDiameter = (
            column_sec_rebars_number_diameter
        )
    if column_sec_rebars_type:
        footingReinforcementGroup.ColumnSecRebarsType = column_sec_rebars_type
    if column_sec_hook_orientation:
        footingReinforcementGroup.ColumnSecHookOrientation = (
            column_sec_hook_orientation
        )
    if column_l_sec_rebar_rounding:
        footingReinforcementGroup.ColumnSecLRebarRounding = (
            column_l_sec_rebar_rounding
        )
    footingReinforcementGroup.IsMakeOrEditRequired = True
    if column_sec_hook_extension:
        footingReinforcementGroup.ColumnSecHookExtension = (
            column_sec_hook_extension
        )
    FreeCAD.ActiveDocument.recompute()
    return footingReinforcementGroup


def editFootingReinforcement(
    footingReinforcementGroup: FootingReinforcementGroup,
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
    """Update Footing Reinforcement

    Parameters
    ----------
    footingReinforcementGroup: FootingReinforcementGroup
        Footing Reinforcement rebars group
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
    footingReinforcementGroup.IsMakeOrEditRequired = False
    footingReinforcementGroup.MeshCoverAlong = mesh_cover_along
    if facename:
        footingReinforcementGroup.Facename = facename
    if structure:
        footingReinforcementGroup.Structure = structure
    footingReinforcementGroup.ParallelRebarType = parallel_rebar_type
    footingReinforcementGroup.ParallelFrontCover = parallel_front_cover
    footingReinforcementGroup.ParallelRearCover = parallel_rear_cover
    footingReinforcementGroup.ParallelLeftCover = parallel_left_cover
    footingReinforcementGroup.ParallelRightCover = parallel_right_cover
    footingReinforcementGroup.ParallelTopCover = parallel_top_cover
    footingReinforcementGroup.ParallelBottomCover = parallel_bottom_cover
    footingReinforcementGroup.ParallelDiameter = parallel_diameter
    footingReinforcementGroup.ParallelAmountSpacingCheck = (
        parallel_amount_spacing_check
    )
    if parallel_amount_spacing_check:
        footingReinforcementGroup.ParallelAmountValue = (
            parallel_amount_spacing_value
        )
    else:
        footingReinforcementGroup.ParallelSpacingValue = (
            parallel_amount_spacing_value
        )

    if parallel_rounding:
        footingReinforcementGroup.ParallelRounding = parallel_rounding
    if parallel_l_shape_hook_orintation:
        footingReinforcementGroup.ParallelLShapeHookOrintation = (
            parallel_l_shape_hook_orintation
        )

    footingReinforcementGroup.CrossRebarType = cross_rebar_type
    footingReinforcementGroup.CrossFrontCover = cross_front_cover
    footingReinforcementGroup.CrossRearCover = cross_rear_cover
    footingReinforcementGroup.CrossLeftCover = cross_left_cover
    footingReinforcementGroup.CrossRightCover = cross_right_cover
    footingReinforcementGroup.CrossTopCover = cross_top_cover
    footingReinforcementGroup.CrossBottomCover = cross_bottom_cover
    footingReinforcementGroup.CrossDiameter = cross_diameter
    footingReinforcementGroup.CrossAmountSpacingCheck = (
        cross_amount_spacing_check
    )
    if cross_amount_spacing_check:
        footingReinforcementGroup.CrossAmountValue = cross_amount_spacing_value
    else:
        footingReinforcementGroup.CrossSpacingValue = cross_amount_spacing_value
    if cross_rounding:
        footingReinforcementGroup.CrossRounding = cross_rounding
    if cross_l_shape_hook_orintation:
        footingReinforcementGroup.CrossLShapeHookOrintation = (
            cross_l_shape_hook_orintation
        )

    footingReinforcementGroup.ColumnFrontCover = column_front_cover
    footingReinforcementGroup.ColumnLeftCover = column_left_cover
    footingReinforcementGroup.ColumnRightCover = column_right_cover
    footingReinforcementGroup.ColumnRearCover = column_rear_cover
    footingReinforcementGroup.TieTopCover = tie_top_cover
    footingReinforcementGroup.TieBottomCover = tie_bottom_cover
    footingReinforcementGroup.TieBentAngle = tie_bent_angle
    footingReinforcementGroup.TieExtensionFactor = tie_extension_factor
    footingReinforcementGroup.TieDiameter = tie_diameter
    footingReinforcementGroup.TieNumberSpacingCheck = tie_number_spacing_check
    if tie_number_spacing_check:
        footingReinforcementGroup.TieAmountValue = tie_number_spacing_value
    else:
        footingReinforcementGroup.TieSpacingValue = tie_number_spacing_value
    footingReinforcementGroup.ColumnMainRebarsDiameter = (
        column_main_rebar_diameter
    )
    footingReinforcementGroup.ColumnMainRebarsTopOffset = (
        column_main_rebars_t_offset
    )
    footingReinforcementGroup.ColumnWidth = column_width
    footingReinforcementGroup.ColumnLength = column_length
    footingReinforcementGroup.XDirColumnNumberSpacingCheck = (
        xdir_column_amount_spacing_check
    )
    if xdir_column_amount_spacing_check:
        footingReinforcementGroup.XDirColumnAmountValue = (
            xdir_column_amount_spacing_value
        )
    else:
        footingReinforcementGroup.XDirColumnSpacingValue = (
            xdir_column_amount_spacing_value
        )
    footingReinforcementGroup.YDirColumnNumberSpacingCheck = (
        ydir_column_amount_spacing_check
    )
    if ydir_column_amount_spacing_check:
        footingReinforcementGroup.YDirColumnAmountValue = (
            ydir_column_amount_spacing_value
        )
    else:
        footingReinforcementGroup.YDirColumnSpacingValue = (
            ydir_column_amount_spacing_value
        )
    if column_main_rebars_type:
        footingReinforcementGroup.ColumnMainRebarType = column_main_rebars_type
    if column_main_hook_orientation:
        footingReinforcementGroup.ColumnMainHookOrientation = (
            column_main_hook_orientation
        )
    if column_main_hook_extend_along:
        footingReinforcementGroup.ColumnMainHookExtendAlong = (
            column_main_hook_extend_along
        )
    if column_l_main_rebar_rounding:
        footingReinforcementGroup.ColumnMainLRebarRounding = (
            column_l_main_rebar_rounding
        )
    if column_main_hook_extension:
        footingReinforcementGroup.ColumnMainHookExtension = (
            column_main_hook_extension
        )
    if column_sec_rebar_check:
        footingReinforcementGroup.ColumnSecRebarsCheck = column_sec_rebar_check
    if column_sec_rebars_t_offset:
        footingReinforcementGroup.ColumnSecRebarsTopOffset = (
            column_sec_rebars_t_offset
        )
    if column_sec_rebars_number_diameter:
        footingReinforcementGroup.ColumnSecRebarsNumberDiameter = (
            column_sec_rebars_number_diameter
        )
    if column_sec_rebars_type:
        footingReinforcementGroup.ColumnSecRebarsType = column_sec_rebars_type
    if column_sec_hook_orientation:
        footingReinforcementGroup.ColumnSecHookOrientation = (
            column_sec_hook_orientation
        )
    if column_l_sec_rebar_rounding:
        footingReinforcementGroup.ColumnSecLRebarRounding = (
            column_l_sec_rebar_rounding
        )
    footingReinforcementGroup.IsMakeOrEditRequired = True
    if column_sec_hook_extension:
        footingReinforcementGroup.ColumnSecHookExtension = (
            column_sec_hook_extension
        )
    FreeCAD.ActiveDocument.recompute()
    return footingReinforcementGroup
