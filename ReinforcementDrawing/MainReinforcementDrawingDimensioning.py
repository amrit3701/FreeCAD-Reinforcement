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

__title__ = "Reinforcement Drawing Dimensioning Command"
__author__ = "Suraj"
__url__ = "https://www.freecadweb.org"

from typing import Union, Literal, List

import FreeCADGui

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


def CommandReinforcementDrawingDimensioning(
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
    perform_dimensioning=True,
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
    FreeCADGui.addModule("ReinforcementDrawing.make_reinforcement_drawing")

    def getFreeCADObjectsList(
        objects: list,
    ) -> Union[Literal["None"], List[str]]:
        return (
            "None"
            if not objects
            else ["FreeCAD.ActiveDocument." + obj.Name for obj in objects]
        )

    structure_list = getFreeCADObjectsList(structure_list)
    rebars_list = getFreeCADObjectsList(rebars_list)
    FreeCADGui.doCommand(
        "ReinforcementDrawing.make_reinforcement_drawing."
        f"makeStructuresReinforcementDrawing(structure_list={structure_list}, "
        f"rebars_list={rebars_list}, "
        f'view="{view}", '
        f"rebars_stroke_width={rebars_stroke_width}, "
        f'rebars_color_style="{rebars_color_style}", '
        f"rebars_color={rebars_color}, "
        f"structure_stroke_width={structure_stroke_width}, "
        f'structure_color_style="{structure_color_style}", '
        f"structure_color={structure_color}, "
        f"drawing_left_offset={drawing_left_offset}, "
        f"drawing_top_offset={drawing_top_offset}, "
        f"drawing_min_right_offset={drawing_min_right_offset}, "
        f"drawing_min_bottom_offset={drawing_min_bottom_offset}, "
        f"drawing_max_width={drawing_max_width}, "
        f"drawing_max_height={drawing_max_height}, "
        f'template_file=r"{template_file}", '
        f"perform_dimensioning={perform_dimensioning}, "
        f"dimension_rebars_filter_list={dimension_rebars_filter_list}, "
        f'dimension_label_format="{dimension_label_format}",  '
        f'dimension_font_family="{dimension_font_family}", '
        f"dimension_font_size={dimension_font_size}, "
        f"dimension_stroke_width={dimension_stroke_width}, "
        f'dimension_line_style="{dimension_line_style}",'
        f" dimension_line_color={dimension_line_color}, "
        f"dimension_text_color={dimension_text_color}, "
        'dimension_single_rebar_line_start_symbol="'
        f'{dimension_single_rebar_line_start_symbol}", '
        'dimension_single_rebar_line_end_symbol="'
        f'{dimension_single_rebar_line_end_symbol}", '
        'dimension_multi_rebar_line_start_symbol="'
        f'{dimension_multi_rebar_line_start_symbol}", '
        'dimension_multi_rebar_line_end_symbol="'
        f'{dimension_multi_rebar_line_end_symbol}", '
        f'dimension_line_mid_point_symbol="{dimension_line_mid_point_symbol}",'
        f" dimension_left_offset={dimension_left_offset}, "
        f"dimension_right_offset={dimension_right_offset}, "
        f"dimension_top_offset={dimension_top_offset}, "
        f"dimension_bottom_offset={dimension_bottom_offset}, "
        f"dimension_left_offset_increment={dimension_left_offset_increment}, "
        f"dimension_right_offset_increment={dimension_right_offset_increment}, "
        f"dimension_top_offset_increment={dimension_top_offset_increment}, "
        "dimension_bottom_offset_increment="
        f"{dimension_bottom_offset_increment}, "
        f"dimension_single_rebar_outer_dim={dimension_single_rebar_outer_dim}, "
        f"dimension_multi_rebar_outer_dim={dimension_multi_rebar_outer_dim}, "
        "dimension_single_rebar_text_position_type="
        f'"{dimension_single_rebar_text_position_type}", '
        "dimension_multi_rebar_text_position_type="
        f'"{dimension_multi_rebar_text_position_type}")'
    )
