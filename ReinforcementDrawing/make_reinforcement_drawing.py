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

from .config import (
    FONT_FAMILY,
    FONT_SIZE,
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
)


def getStructureRebarsDict(structure_list=None):
    """getStructureRebarsDict([StructureList]):
    structure_list is the list of structural objects. If not provided,
    structures will be selected from active document acting as Host for rebar
    objects.

    Returns dictionary with structure as key and corresponding rebar objects
    list as value.
    """
    if not structure_list:
        structure_list = FreeCAD.ActiveDocument.Objects
    rebar_objects = Draft.get_objects_of_type(
        FreeCAD.ActiveDocument.Objects, "Rebar"
    )

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
    font_family,
    font_size,
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
):
    """makeReinforcementDrawing(Structure, RebarsList, View, FontFamily,
    FontSize, RebarsStrokeWidth, RebarsColorStyle, RebarsColor,
    StructureStrokeWidth, StructureColorStyle, StructureColor,
    DrawingLeftOffset, DrawingTopOffset, DrawingMinRightOffset,
    DrawingMinBottomOffset, DrawingMaxWidth, DrawingMaxHeight, TemplateFile):
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
    drawing_content_obj.recompute()
    reinforcement_drawing_page.recompute(True)

    return reinforcement_drawing_page


def makeStructuresReinforcementDrawing(
    structure_list=None,
    view="Front",
    font_family=FONT_FAMILY,
    font_size=FONT_SIZE,
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
):
    """makeStructuresReinforcementDrawing([StructureList, View, FontFamily,
    FontSize, RebarsStrokeWidth, RebarsColorStyle, RebarsColor,
    StructureStrokeWidth, StructureColorStyle, StructureColor,
    DrawingLeftOffset, DrawingTopOffset, DrawingMinRightOffset,
    DrawingMinBottomOffset, DrawingMaxWidth, DrawingMaxHeight, TemplateFile]):
    Generates Reinforcement Drawing SVG view for structures.

    structure_list is the list of structural objects. If not provided,
    structures will be selected from active document acting as Host for rebar
    objects.

    view can be "Front", "Rear", "Left", "Right", "Top" or "Bottom".

    rebars_color_style/structure_color_style can be "Automatic" to select color
    from rebar/structure shape or "Custom" to use color as defined by parameter
    rebars_color/structure_color.

    rebars_color/structure_color is tuple of r, g, b values of color.
    r, g, b must be between 0 to 1 and must be float. Divide r, g, b value of
    color to get values between 0 and 1.

    Returns dictionary with structure as key and corresponding reinforcement
    drawing page as value.
    """
    struct_rebars_dict = getStructureRebarsDict(structure_list)
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
            font_family,
            font_size,
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
        )
    return struct_drawing_page_dict
