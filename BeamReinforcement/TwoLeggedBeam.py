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

__title__ = "Two Legged Stirrup Beam Reinforcement"
__author__ = "Suraj"
__url__ = "https://www.freecadweb.org"


import FreeCAD

from Stirrup import makeStirrup

if FreeCAD.GuiUp:
    import FreeCADGui


def makeReinforcement(
    l_cover_of_stirrup,
    r_cover_of_stirrup,
    t_cover_of_stirrup,
    b_cover_of_stirrup,
    offset_of_stirrup,
    bent_angle,
    extension_factor,
    dia_of_stirrup,
    number_spacing_check,
    number_spacing_value,
    top_reinforcement_number_diameter_offset,
    top_reinforcement_rebar_type,
    top_reinforcement_layer_spacing,
    bottom_reinforcement_number_diameter_offset,
    bottom_reinforcement_rebar_type,
    bottom_reinforcement_layer_spacing,
    left_rebars_number_diameter_offset,
    left_rebars_type,
    left_rebars_spacing,
    right_rebars_number_diameter_offset,
    right_rebars_type,
    right_rebars_spacing,
    top_reinforcement_hook_extension=None,
    top_reinforcement_hook_orientation="Front Inside",
    bottom_reinforcement_hook_extension=None,
    bottom_reinforcement_hook_orientation="Front Inside",
    left_rebars_hook_extension=None,
    left_rebars_hook_orientation="Front Inside",
    right_rebars_hook_extension=None,
    right_rebars_hook_orientation="Front Inside",
    structure=None,
    facename=None,
):
    """makeReinforcement(LeftCoverOfStirrup, RightCoverOfStirrup,
    TopCoverOfStirrup, BottomCoverOfStirrup, OffsetofStirrup, BentAngle,
    ExtensionFactor, DiameterOfStirrup, NumberSpacingCheck, NumberSpacingValue,
    TopReinforcementNumberDiameterOffset, TopReinforcementRebarType,
    TopReinforcementLayerSpacing, BottomReinforcementNumberDiameterOffset,
    BottomReinforcementRebarType, BottomReinforcementLayerSpacing,
    LeftRebarsNumberDiameterOffset, LeftRebarsType, LeftRebarsSpacing,
    RightRebarsNumberDiameterOffset, RightRebarsType, RightRebarsSpacing,
    TopReinforcementHookLength, TopReinforcementHookOrientation,
    BottomReinforcementHookLength, BottomReinforcementHookOrientation,
    LeftRebarsHookLength, LeftRebarsHookOrientation, RightRebarsHookLength,
    RightRebarsHookOrientation,nStructure, Facename):
    Adds the Two Legged Stirrup reinforcement to the selected structural beam
    object.

    top_reinforcement_number_diameter_offset and
    bottom_reinforcement_number_diameter_offset are tuple of
    number_diameter_offset string. Each element of tuple represents
    reinforcement for each new layer.
    Syntax: (
                "number1#diameter1@offset1+number2#diameter2@offset2+...",
                "number3#diameter3@offset3+number4#diameter4@offset4+...",
                ...,
            )

    rebar_type for top/bottom/left/right rebars can be 'StraightRebar',
    'LShapeRebar'.

    Possible values for top_reinforcement_rebar_type and
    bottom_reinforcement_rebar_type:
    1. 'StraightRebar' or 'LShapeRebar'
    2. ('<rebar_type>', '<rebar_type>', ...) and number of elements of tuple
    must be equal to number of layers.
    3. [
           ('<rebar_type>', '<rebar_type>', ...),
           ('<rebar_type>', '<rebar_type>', ...),
           ...,
       ]
       each element of list is a tuple, which specifies rebar type of each
       layer. And each element of tuple represents rabar_type for each set of
       rebars.
    4. [
           <rebar_type>,
           ('<rebar_type>', '<rebar_type>', ...),
           ...,
       ]

    Possible values for top_reinforcement_layer_spacing and
    bottom_reinforcement_layer_spacing:
    1. <layer_spacing>
    2. (<spacing in layer1 and layer2>, <spacing in layer2 and layer3>, ...) and
    number of elements of tuple must be equal to one less than number of layers.

    hook_orientation for top/bottom/left/right rebars can be 'Front Inside',
    'Front Outside', 'Rear Inside', 'Rear Outside'.

    Possible values for top_reinforcement_hook_orientation,
    bottom_reinforcement_hook_orientation, top_reinforcement_hook_extension and
    bottom_reinforcement_hook_extension can be similar to as discussed above for
    top_reinforcement_rebar_type.
    """
    if not structure and not facename:
        if FreeCAD.GuiUp:
            selected_obj = FreeCADGui.Selection.getSelectionEx()[0]
            structure = selected_obj.Object
            facename = selected_obj.SubElementNames[0]
        else:
            showWarning("Error: Pass structure and facename arguments")
            return None

    # Calculate parameters for Stirrup
    rounding = (
        float(dia_of_stirrup) / 2 + dia_of_main_rebars / 2
    ) / dia_of_stirrup
    f_cover = offset_of_stirrup

    # Create Stirrup
    tie = makeStirrup(
        l_cover_of_stirrup,
        r_cover_of_stirrup,
        t_cover_of_stirrup,
        b_cover_of_stirrup,
        f_cover,
        bent_angle,
        extension_factor,
        dia_of_stirrup,
        rounding,
        number_spacing_check,
        number_spacing_value,
        structure,
        facename,
    )
    print("WIP")
