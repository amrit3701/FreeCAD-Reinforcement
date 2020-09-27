# -*- coding: utf-8 -*-
# ***************************************************************************
# *                                                                         *
# *   Copyright (c) 2020 - Suraj <dadralj18@gmail.com>                      *
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

__title__ = "Reinforcement Drawing"
__author__ = "Suraj"
__url__ = "https://www.freecadweb.org"


import FreeCAD
import Draft

from .ReinforcementDrawingView import makeReinforcementDrawingObject
from .ReinforcementDimensioning import makeReinforcementDimensioningObject

from .config import (
    REBARS_STROKE_WIDTH,
    REBARS_COLOR_STYLE,
    REBARS_COLOR,
    STRUCTURE_STROKE_WIDTH,
    STRUCTURE_COLOR_STYLE,
    STRUCTURE_COLOR,
    DRAWING_LEFT_OFFSET,
    DRAWING_TOP_OFFSET,
    DRAWING_MIN_RIGHT_OFFSET,
    DRAWING_MIN_BOTTOM_OFFSET,
    DRAWING_MAX_WIDTH,
    DRAWING_MAX_HEIGHT,
    TEMPLATE_FILE,
    DIMENSION_LABEL_FORMAT,
    DIMENSION_FONT_FAMILY,
    DIMENSION_FONT_SIZE,
    DIMENSION_STROKE_WIDTH,
    DIMENSION_LINE_STYLE,
    DIMENSION_LINE_COLOR,
    DIMENSION_TEXT_COLOR,
    DIMENSION_SINGLE_REBAR_LINE_START_SYMBOL,
    DIMENSION_SINGLE_REBAR_LINE_END_SYMBOL,
    DIMENSION_MULTI_REBAR_LINE_START_SYMBOL,
    DIMENSION_MULTI_REBAR_LINE_END_SYMBOL,
    DIMENSION_LINE_MID_POINT_SYMBOL,
    DIMENSION_LEFT_OFFSET,
    DIMENSION_RIGHT_OFFSET,
    DIMENSION_TOP_OFFSET,
    DIMENSION_BOTTOM_OFFSET,
    DIMENSION_LEFT_OFFSET_INCREMENT,
    DIMENSION_RIGHT_OFFSET_INCREMENT,
    DIMENSION_TOP_OFFSET_INCREMENT,
    DIMENSION_BOTTOM_OFFSET_INCREMENT,
    DIMENSION_SINGLE_REBAR_OUTER_DIM,
    DIMENSION_MULTI_REBAR_OUTER_DIM,
    DIMENSION_SINGLE_REBAR_TEXT_POSITION_TYPE,
    DIMENSION_MULTI_REBAR_TEXT_POSITION_TYPE,
)


def getStructureRebarsDict(structure_list=None, rebars_list=None):
    """getStructureRebarsDict([StructureList, RebarsList]):
    structure_list is the list of structural objects. If not provided,
    structures will be selected from active document acting as Host for rebar
    objects.

    rebars_list is the list of rebar objects. If not provided, rebars objects
    having Host in structure_list will be selected from active document.

    Returns dictionary with structure as key and corresponding rebar objects
    list as value.
    """
    if not structure_list:
        structure_list = FreeCAD.ActiveDocument.Objects

    if not rebars_list:
        rebar_objects = Draft.get_objects_of_type(
            FreeCAD.ActiveDocument.Objects, "Rebar"
        )
    else:
        rebar_objects = Draft.get_objects_of_type(rebars_list, "Rebar")

    struct_rebars_dict = {}
    for rebar in rebar_objects:
        if rebar.Host in structure_list:
            if rebar.Host not in struct_rebars_dict:
                struct_rebars_dict[rebar.Host] = []
            struct_rebars_dict[rebar.Host].append(rebar)

    return struct_rebars_dict


def makeReinforcementDrawing(
    structure,
    rebars_list,
    view,
    rebars_stroke_width,
    rebars_color_style,
    rebars_color,
    structure_stroke_width,
    structure_color_style,
    structure_color,
    drawing_left_offset,
    drawing_top_offset,
    drawing_min_right_offset,
    drawing_min_bottom_offset,
    drawing_max_width,
    drawing_max_height,
    template_file,
    dimension_left_offset,
    dimension_right_offset,
    dimension_top_offset,
    dimension_bottom_offset,
):
    """makeReinforcementDrawing(Structure, RebarsList, View, RebarsStrokeWidth,
    RebarsColorStyle, RebarsColor, StructureStrokeWidth, StructureColorStyle,
    StructureColor, DrawingLeftOffset, DrawingTopOffset, DrawingMinRightOffset,
    DrawingMinBottomOffset, DrawingMaxWidth, DrawingMaxHeight, TemplateFile,
    DimensionLeftOffset, DimensionRightOffset, DimensionTopOffset,
    DimensionBottomOffset):
    Generates Reinforcement Drawing SVG view for structure.

    view can be "Front", "Rear", "Left", "Right", "Top" or "Bottom".

    rebars_color_style/structure_color_style can be "Automatic" to select color
    from rebar/structure shape or "Custom" to use color as defined by parameter
    rebars_color/structure_color.

    rebars_color/structure_color is tuple of r, g, b values of color.
    r, g, b must be between 0 to 1 and must be float. Divide r, g, b value of
    color to get values between 0 and 1.

    Returns reinforcement drawing page of type TechDraw::DrawPage.
    """

    reinforcement_drawing_page = makeReinforcementDrawingObject(template_file)
    reinforcement_drawing_page.Label = structure.Label + " Drawing"
    drawing_content_obj = reinforcement_drawing_page.Views[0]
    drawing_content_obj.Label = view + " View"
    drawing_content_obj.Structure = structure
    drawing_content_obj.Rebars = rebars_list
    drawing_content_obj.View = view
    drawing_content_obj.ScaleType = "Automatic"
    drawing_content_obj.PositionType = "Automatic"
    drawing_content_obj.RebarsStrokeWidth = rebars_stroke_width
    drawing_content_obj.RebarsColorStyle = rebars_color_style
    drawing_content_obj.RebarsColor = rebars_color
    drawing_content_obj.StructureStrokeWidth = structure_stroke_width
    drawing_content_obj.StructureColorStyle = structure_color_style
    drawing_content_obj.StructureColor = structure_color
    drawing_content_obj.Template = reinforcement_drawing_page.Template
    drawing_content_obj.LeftOffset = drawing_left_offset
    drawing_content_obj.TopOffset = drawing_top_offset
    drawing_content_obj.MinRightOffset = drawing_min_right_offset
    drawing_content_obj.MinBottomOffset = drawing_min_bottom_offset
    drawing_content_obj.MaxWidth = drawing_max_width
    drawing_content_obj.MaxHeight = drawing_max_height
    drawing_content_obj.DimensionLeftOffset = dimension_left_offset
    drawing_content_obj.DimensionRightOffset = dimension_right_offset
    drawing_content_obj.DimensionTopOffset = dimension_top_offset
    drawing_content_obj.DimensionBottomOffset = dimension_bottom_offset
    drawing_content_obj.recompute()
    reinforcement_drawing_page.recompute(True)

    return reinforcement_drawing_page


def makeStructuresReinforcementDrawing(
    structure_list=None,
    rebars_list=None,
    view="Front",
    rebars_stroke_width=REBARS_STROKE_WIDTH,
    rebars_color_style=REBARS_COLOR_STYLE,
    rebars_color=REBARS_COLOR,
    structure_stroke_width=STRUCTURE_STROKE_WIDTH,
    structure_color_style=STRUCTURE_COLOR_STYLE,
    structure_color=STRUCTURE_COLOR,
    drawing_left_offset=DRAWING_LEFT_OFFSET,
    drawing_top_offset=DRAWING_TOP_OFFSET,
    drawing_min_right_offset=DRAWING_MIN_RIGHT_OFFSET,
    drawing_min_bottom_offset=DRAWING_MIN_BOTTOM_OFFSET,
    drawing_max_width=DRAWING_MAX_WIDTH,
    drawing_max_height=DRAWING_MAX_HEIGHT,
    template_file=TEMPLATE_FILE,
    perform_dimensioning=False,
    dimension_rebars_filter_list=None,
    dimension_label_format=DIMENSION_LABEL_FORMAT,
    dimension_font_family=DIMENSION_FONT_FAMILY,
    dimension_font_size=DIMENSION_FONT_SIZE,
    dimension_stroke_width=DIMENSION_STROKE_WIDTH,
    dimension_line_style=DIMENSION_LINE_STYLE,
    dimension_line_color=DIMENSION_LINE_COLOR,
    dimension_text_color=DIMENSION_TEXT_COLOR,
    dimension_single_rebar_line_start_symbol=(
        DIMENSION_SINGLE_REBAR_LINE_START_SYMBOL
    ),
    dimension_single_rebar_line_end_symbol=(
        DIMENSION_SINGLE_REBAR_LINE_END_SYMBOL
    ),
    dimension_multi_rebar_line_start_symbol=(
        DIMENSION_MULTI_REBAR_LINE_START_SYMBOL
    ),
    dimension_multi_rebar_line_end_symbol=(
        DIMENSION_MULTI_REBAR_LINE_END_SYMBOL
    ),
    dimension_line_mid_point_symbol=DIMENSION_LINE_MID_POINT_SYMBOL,
    dimension_left_offset=DIMENSION_LEFT_OFFSET,
    dimension_right_offset=DIMENSION_RIGHT_OFFSET,
    dimension_top_offset=DIMENSION_TOP_OFFSET,
    dimension_bottom_offset=DIMENSION_BOTTOM_OFFSET,
    dimension_left_offset_increment=DIMENSION_LEFT_OFFSET_INCREMENT,
    dimension_right_offset_increment=DIMENSION_RIGHT_OFFSET_INCREMENT,
    dimension_top_offset_increment=DIMENSION_TOP_OFFSET_INCREMENT,
    dimension_bottom_offset_increment=DIMENSION_BOTTOM_OFFSET_INCREMENT,
    dimension_single_rebar_outer_dim=DIMENSION_SINGLE_REBAR_OUTER_DIM,
    dimension_multi_rebar_outer_dim=DIMENSION_MULTI_REBAR_OUTER_DIM,
    dimension_single_rebar_text_position_type=(
        DIMENSION_SINGLE_REBAR_TEXT_POSITION_TYPE
    ),
    dimension_multi_rebar_text_position_type=(
        DIMENSION_MULTI_REBAR_TEXT_POSITION_TYPE
    ),
):
    """makeStructuresReinforcementDrawing([StructureList, RebarsList, View,
    RebarsStrokeWidth, RebarsColorStyle, RebarsColor, StructureStrokeWidth,
    StructureColorStyle, StructureColor, DrawingLeftOffset, DrawingTopOffset,
    DrawingMinRightOffset, DrawingMinBottomOffset, DrawingMaxWidth,
    DrawingMaxHeight, TemplateFile, PerformDimensioning,
    DimensionRebarsFilterList, DimensionLabelFormat, DimensionFontFamily,
    DimensionFontSize, DimensionStrokeWidth, DimensionLineStyle,
    DimensionLineColor, DimensionTextColor,
    SingleRebar_DimensionLineStartSymbol, SingleRebar_DimensionLineEndSymbol,
    MultiRebar_DimensionLineStartSymbol, MultiRebar_DimensionLineEndSymbol,
    DimensionLineMidPointSymbol, DimensionLeftOffset, DimensionRightOffset,
    DimensionTopOffset, DimensionBottomOffset, DimensionLeftOffsetIncrement,
    DimensionRightOffsetIncrement, DimensionTopOffsetIncrement,
    DimensionBottomOffsetIncrement, SingleRebar_OuterDimension,
    MultiRebar_OuterDimension, SingleRebar_TextPositionType,
    MultiRebar_TextPositionType]):
    Generates Reinforcement Drawing SVG view for structures.

    structure_list is the list of structural objects. If not provided,
    structures will be selected from active document acting as Host for rebar
    objects.

    rebars_list is the list of rebar objects. If not provided, rebars objects
    having Host in structure_list will be selected from active document.

    view can be "Front", "Rear", "Left", "Right", "Top" or "Bottom".

    rebars_color_style/structure_color_style can be "Automatic" to select color
    from rebar/structure shape or "Custom" to use color as defined by parameter
    rebars_color/structure_color.

    rebars_color/structure_color is tuple of r, g, b values of color.
    r, g, b must be between 0 to 1 and must be float. Divide r, g, b value of
    color to get values between 0 and 1.

    Dimensioning:
    set perform_dimensioning True to dimension reinforcement drawing,
    False otherwise.

    dimension_rebars_filter_list is the list of rebars to perform dimensioning.
    Set it to None to dimension all visible rebars in drawing.

    Returns dictionary with structure as key and corresponding reinforcement
    drawing page as value.
    """
    struct_rebars_dict = getStructureRebarsDict(structure_list, rebars_list)
    if not struct_rebars_dict:
        FreeCAD.Console.PrintWarning(
            "No structure/rebar object in current selection/document. "
            "Returning without drawing svg.\n"
        )
        return None
    struct_drawing_page_dict = {}
    for structure in struct_rebars_dict:
        struct_drawing_page_dict[structure] = makeReinforcementDrawing(
            structure,
            struct_rebars_dict[structure],
            view,
            rebars_stroke_width,
            rebars_color_style,
            rebars_color,
            structure_stroke_width,
            structure_color_style,
            structure_color,
            drawing_left_offset,
            drawing_top_offset,
            drawing_min_right_offset,
            drawing_min_bottom_offset,
            drawing_max_width,
            drawing_max_height,
            template_file,
            dimension_left_offset,
            dimension_right_offset,
            dimension_top_offset,
            dimension_bottom_offset,
        )
        if perform_dimensioning:
            drawing_page = struct_drawing_page_dict[structure]
            drawing_view = drawing_page.Views[0]
            rebars = drawing_view.VisibleRebars
            if dimension_rebars_filter_list:
                rebars = list(set(rebars) & set(dimension_rebars_filter_list))
            for rebar in rebars:
                makeReinforcementDimensioningObject(
                    rebar,
                    drawing_view,
                    drawing_page,
                    dimension_label_format,
                    dimension_font_family,
                    dimension_font_size,
                    dimension_stroke_width,
                    dimension_line_style,
                    dimension_line_color,
                    dimension_text_color,
                    dimension_single_rebar_line_start_symbol,
                    dimension_single_rebar_line_end_symbol,
                    dimension_multi_rebar_line_start_symbol,
                    dimension_multi_rebar_line_end_symbol,
                    dimension_line_mid_point_symbol,
                    dimension_left_offset_increment,
                    dimension_right_offset_increment,
                    dimension_top_offset_increment,
                    dimension_bottom_offset_increment,
                    dimension_single_rebar_outer_dim,
                    dimension_multi_rebar_outer_dim,
                    dimension_single_rebar_text_position_type,
                    dimension_multi_rebar_text_position_type,
                )
    return struct_drawing_page_dict
