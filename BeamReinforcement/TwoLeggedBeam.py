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

from StraightRebar import makeStraightRebar
from Stirrup import makeStirrup
from Rebarfunc import (
    getParametersOfFace,
    getFacenamesforBeamReinforcement,
    getdictofNumberDiameterOffset,
)

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
    top_reinforcement_number_diameter_offset_dict = getdictofNumberDiameterOffset(
        top_reinforcement_number_diameter_offset
    )
    bottom_reinforcement_number_diameter_offset_dict = getdictofNumberDiameterOffset(
        bottom_reinforcement_number_diameter_offset
    )

    max_dia_of_main_rebars = max(
        top_reinforcement_number_diameter_offset_dict["layer1"][0][1],
        top_reinforcement_number_diameter_offset_dict["layer1"][-1][1],
        bottom_reinforcement_number_diameter_offset_dict["layer1"][0][1],
        bottom_reinforcement_number_diameter_offset_dict["layer1"][-1][1],
    )
    rounding = (
        float(dia_of_stirrup) / 2 + max_dia_of_main_rebars / 2
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

    # Create top reinforcement
    top_reinforcement_rebars = makeTopReinforcement(
        l_cover_of_stirrup,
        r_cover_of_stirrup,
        t_cover_of_stirrup,
        b_cover_of_stirrup,
        offset_of_stirrup,
        dia_of_stirrup,
        top_reinforcement_number_diameter_offset,
        top_reinforcement_rebar_type,
        top_reinforcement_layer_spacing,
        top_reinforcement_hook_extension,
        top_reinforcement_hook_orientation,
        facename,
        structure,
    )

    # Create bottom reinforcement
    bottom_reinforcement_rebars = makeBottomReinforcement(
        l_cover_of_stirrup,
        r_cover_of_stirrup,
        t_cover_of_stirrup,
        b_cover_of_stirrup,
        offset_of_stirrup,
        dia_of_stirrup,
        bottom_reinforcement_number_diameter_offset,
        bottom_reinforcement_rebar_type,
        bottom_reinforcement_layer_spacing,
        bottom_reinforcement_hook_extension,
        bottom_reinforcement_hook_orientation,
        facename,
        structure,
    )

    FreeCAD.ActiveDocument.recompute()
    print("WIP")


def makeTopReinforcement(
    l_cover_of_stirrup,
    r_cover_of_stirrup,
    t_cover_of_stirrup,
    b_cover_of_stirrup,
    offset_of_stirrup,
    dia_of_stirrup,
    top_reinforcement_number_diameter_offset,
    top_reinforcement_rebar_type,
    top_reinforcement_layer_spacing,
    top_reinforcement_hook_extension,
    top_reinforcement_hook_orientation,
    facename,
    structure,
):
    facename_for_t_rebars = getFacenamesforBeamReinforcement(
        facename, structure
    )[0]

    top_reinforcement_layers = len(top_reinforcement_number_diameter_offset)

    top_reinforcement_number_diameter_offset_dict = getdictofNumberDiameterOffset(
        top_reinforcement_number_diameter_offset
    )

    top_reinforcement_rebar_type_dict = {}
    if type(top_reinforcement_rebar_type) in (list, tuple):
        layer = 1
        while layer <= top_reinforcement_layers:
            top_reinforcement_rebar_type_dict["layer" + str(layer)] = []
            if type(top_reinforcement_rebar_type[layer - 1]) in (list, tuple):
                top_reinforcement_rebar_type_dict[
                    "layer" + str(layer)
                ] = top_reinforcement_rebar_type[layer - 1]
            elif type(top_reinforcement_rebar_type[layer - 1]) == str:
                i = 0
                while i < len(
                    top_reinforcement_number_diameter_offset_dict[
                        "layer" + str(layer)
                    ]
                ):
                    top_reinforcement_rebar_type_dict[
                        "layer" + str(layer)
                    ].append(top_reinforcement_rebar_type[layer - 1])
                    i += 1
            layer += 1
    elif type(top_reinforcement_rebar_type) == str:
        layer = 1
        while layer <= top_reinforcement_layers:
            top_reinforcement_rebar_type_dict["layer" + str(layer)] = []
            i = 0
            while i < len(
                top_reinforcement_number_diameter_offset_dict[
                    "layer" + str(layer)
                ]
            ):
                top_reinforcement_rebar_type_dict["layer" + str(layer)].append(
                    top_reinforcement_rebar_type
                )
                i += 1
            layer += 1

    if type(top_reinforcement_layer_spacing) in (float, int):
        top_reinforcement_layer_spacing = [top_reinforcement_layer_spacing]
        while i < top_reinforcement_layers - 1:
            top_reinforcement_layer_spacing.append(
                top_reinforcement_layer_spacing[0]
            )

    top_reinforcement_hook_extension_dict = {}
    if type(top_reinforcement_hook_extension) in (list, tuple):
        layer = 1
        while layer <= top_reinforcement_layers:
            top_reinforcement_hook_extension_dict["layer" + str(layer)] = []
            if type(top_reinforcement_hook_extension[layer - 1]) in (
                list,
                tuple,
            ):
                top_reinforcement_hook_extension_dict[
                    "layer" + str(layer)
                ] = top_reinforcement_hook_extension[layer - 1]
            elif type(top_reinforcement_hook_extension[layer - 1]) in (
                float,
                int,
            ):
                i = 0
                while i < len(
                    top_reinforcement_number_diameter_offset_dict[
                        "layer" + str(layer)
                    ]
                ):
                    if (
                        top_reinforcement_rebar_type_dict["layer" + str(layer)][
                            i
                        ]
                        == "StraightRebar"
                    ):
                        top_reinforcement_hook_extension_dict[
                            "layer" + str(layer)
                        ].append(None)
                    else:
                        top_reinforcement_hook_extension_dict[
                            "layer" + str(layer)
                        ].append(top_reinforcement_hook_extension[layer - 1])
                    i += 1
            layer += 1
    elif (type(top_reinforcement_hook_extension) == (float, int)) or (
        top_reinforcement_hook_extension == None
    ):
        layer = 1
        while layer <= top_reinforcement_layers:
            top_reinforcement_hook_extension_dict["layer" + str(layer)] = []
            i = 0
            while i < len(
                top_reinforcement_number_diameter_offset_dict[
                    "layer" + str(layer)
                ]
            ):
                if (
                    top_reinforcement_rebar_type_dict["layer" + str(layer)][i]
                    == "StraightRebar"
                ):
                    top_reinforcement_hook_extension_dict[
                        "layer" + str(layer)
                    ].append(None)
                else:
                    if top_reinforcement_hook_extension == None:
                        top_reinforcement_hook_extension = (
                            10
                            * top_reinforcement_number_diameter_offset_dict[
                                "layer" + str(layer)
                            ][i][1]
                        )
                    top_reinforcement_hook_extension_dict[
                        "layer" + str(layer)
                    ].append(top_reinforcement_hook_extension)
                i += 1
            layer += 1

    top_reinforcement_hook_orientation_dict = {}
    if type(top_reinforcement_hook_orientation) in (list, tuple):
        layer = 1
        while layer <= top_reinforcement_layers:
            top_reinforcement_hook_orientation_dict["layer" + str(layer)] = []
            if type(top_reinforcement_hook_orientation[layer - 1]) in (
                list,
                tuple,
            ):
                top_reinforcement_hook_orientation_dict[
                    "layer" + str(layer)
                ] = top_reinforcement_hook_orientation[layer - 1]
            elif type(top_reinforcement_hook_orientation[layer - 1]) == str:
                i = 0
                while i < len(
                    top_reinforcement_number_diameter_offset_dict[
                        "layer" + str(layer)
                    ]
                ):
                    if (
                        top_reinforcement_rebar_type_dict["layer" + str(layer)][
                            i
                        ]
                        == "StraightRebar"
                    ):
                        top_reinforcement_hook_orientation_dict[
                            "layer" + str(layer)
                        ].append(None)
                    else:
                        top_reinforcement_hook_orientation_dict[
                            "layer" + str(layer)
                        ].append(top_reinforcement_hook_orientation[layer - 1])
                    i += 1
            layer += 1
    elif type(top_reinforcement_hook_orientation) == str:
        layer = 1
        while layer <= top_reinforcement_layers:
            top_reinforcement_hook_orientation_dict["layer" + str(layer)] = []
            i = 0
            while i < len(
                top_reinforcement_number_diameter_offset_dict[
                    "layer" + str(layer)
                ]
            ):
                if (
                    top_reinforcement_rebar_type_dict["layer" + str(layer)][i]
                    == "StraightRebar"
                ):
                    top_reinforcement_hook_orientation_dict[
                        "layer" + str(layer)
                    ].append(None)
                else:
                    top_reinforcement_hook_orientation_dict[
                        "layer" + str(layer)
                    ].append(top_reinforcement_hook_orientation)
                i += 1
            layer += 1

    FacePRM = getParametersOfFace(structure, facename)
    face_width = FacePRM[0][0]
    top_reinforcement_span_length = (
        face_width
        - l_cover_of_stirrup
        - r_cover_of_stirrup
        - 2 * dia_of_stirrup
    )

    req_space_for_top_reinforcement = []
    top_reinforcement_rebars_number = []
    spacing_in_top_reinforcement = []
    layer = 1
    while layer <= top_reinforcement_layers:
        req_space_for_top_reinforcement.append(
            sum(
                x[0] * x[1]
                for x in top_reinforcement_number_diameter_offset_dict[
                    "layer" + str(layer)
                ]
            )
        )
        top_reinforcement_rebars_number.append(
            sum(
                x[0]
                for x in top_reinforcement_number_diameter_offset_dict[
                    "layer" + str(layer)
                ]
            )
        )
        spacing_in_top_reinforcement.append(
            (
                top_reinforcement_span_length
                - req_space_for_top_reinforcement[-1]
            )
            / (top_reinforcement_rebars_number[-1] - 1)
        )
        layer += 1

    coverAlong = "Top Side"
    top_reinforcement_rebars = []
    layer = 1
    while layer <= top_reinforcement_layers:
        top_reinforcement_number_diameter_offset_list = top_reinforcement_number_diameter_offset_dict[
            "layer" + str(layer)
        ]
        if layer == 1:
            t_cover = t_cover_of_stirrup + dia_of_stirrup
        else:
            t_cover += (
                max(x[1] for x in top_reinforcement_number_diameter_offset_list)
                + top_reinforcement_layer_spacing[layer - 2]
            )

        f_cover = l_cover_of_stirrup + dia_of_stirrup
        for i, (number, diameter, offset) in enumerate(
            top_reinforcement_number_diameter_offset_list
        ):
            if i == 0:
                r_cover = l_cover = offset
            rear_cover = (
                face_width
                - f_cover
                - number * diameter
                - (number - 1) * spacing_in_top_reinforcement[layer - 1]
            )
            if (
                top_reinforcement_rebar_type_dict["layer" + str(layer)][i]
                == "StraightRebar"
            ):
                top_reinforcement_rebars.append(
                    makeStraightRebar(
                        f_cover,
                        (coverAlong, t_cover),
                        r_cover,
                        l_cover,
                        diameter,
                        True,
                        number,
                        "Horizontal",
                        structure,
                        facename_for_t_rebars,
                    )
                )
                top_reinforcement_rebars[-1].OffsetEnd = (
                    rear_cover + diameter / 2
                )
            f_cover += (
                number * diameter
                + number * spacing_in_top_reinforcement[layer - 1]
            )
        layer += 1
    print("WIP")
    FreeCAD.ActiveDocument.recompute()
    return top_reinforcement_rebars


def makeBottomReinforcement(
    l_cover_of_stirrup,
    r_cover_of_stirrup,
    t_cover_of_stirrup,
    b_cover_of_stirrup,
    offset_of_stirrup,
    dia_of_stirrup,
    bottom_reinforcement_number_diameter_offset,
    bottom_reinforcement_rebar_type,
    bottom_reinforcement_layer_spacing,
    bottom_reinforcement_hook_extension,
    bottom_reinforcement_hook_orientation,
    facename,
    structure,
):
    facename_for_b_rebars = getFacenamesforBeamReinforcement(
        facename, structure
    )[0]

    bottom_reinforcement_layers = len(
        bottom_reinforcement_number_diameter_offset
    )

    bottom_reinforcement_number_diameter_offset_dict = getdictofNumberDiameterOffset(
        bottom_reinforcement_number_diameter_offset
    )

    bottom_reinforcement_rebar_type_dict = {}
    if type(bottom_reinforcement_rebar_type) in (list, tuple):
        layer = 1
        while layer <= bottom_reinforcement_layers:
            bottom_reinforcement_rebar_type_dict["layer" + str(layer)] = []
            if type(bottom_reinforcement_rebar_type[layer - 1]) in (
                list,
                tuple,
            ):
                bottom_reinforcement_rebar_type_dict[
                    "layer" + str(layer)
                ] = bottom_reinforcement_rebar_type[layer - 1]
            elif type(bottom_reinforcement_rebar_type[layer - 1]) == str:
                i = 0
                while i < len(
                    bottom_reinforcement_number_diameter_offset_dict[
                        "layer" + str(layer)
                    ]
                ):
                    bottom_reinforcement_rebar_type_dict[
                        "layer" + str(layer)
                    ].append(bottom_reinforcement_rebar_type[layer - 1])
                    i += 1
            layer += 1
    elif type(bottom_reinforcement_rebar_type) == str:
        layer = 1
        while layer <= bottom_reinforcement_layers:
            bottom_reinforcement_rebar_type_dict["layer" + str(layer)] = []
            i = 0
            while i < len(
                bottom_reinforcement_number_diameter_offset_dict[
                    "layer" + str(layer)
                ]
            ):
                bottom_reinforcement_rebar_type_dict[
                    "layer" + str(layer)
                ].append(bottom_reinforcement_rebar_type)
                i += 1
            layer += 1

    if type(bottom_reinforcement_layer_spacing) in (float, int):
        bottom_reinforcement_layer_spacing = [
            bottom_reinforcement_layer_spacing
        ]
        while i < bottom_reinforcement_layers - 1:
            bottom_reinforcement_layer_spacing.append(
                bottom_reinforcement_layer_spacing[0]
            )

    bottom_reinforcement_hook_extension_dict = {}
    if type(bottom_reinforcement_hook_extension) in (list, tuple):
        layer = 1
        while layer <= bottom_reinforcement_layers:
            bottom_reinforcement_hook_extension_dict["layer" + str(layer)] = []
            if type(bottom_reinforcement_hook_extension[layer - 1]) in (
                list,
                tuple,
            ):
                bottom_reinforcement_hook_extension_dict[
                    "layer" + str(layer)
                ] = bottom_reinforcement_hook_extension[layer - 1]
            elif type(bottom_reinforcement_hook_extension[layer - 1]) in (
                float,
                int,
            ):
                i = 0
                while i < len(
                    bottom_reinforcement_number_diameter_offset_dict[
                        "layer" + str(layer)
                    ]
                ):
                    if (
                        bottom_reinforcement_rebar_type_dict[
                            "layer" + str(layer)
                        ][i]
                        == "StraightRebar"
                    ):
                        bottom_reinforcement_hook_extension_dict[
                            "layer" + str(layer)
                        ].append(None)
                    else:
                        bottom_reinforcement_hook_extension_dict[
                            "layer" + str(layer)
                        ].append(bottom_reinforcement_hook_extension[layer - 1])
                    i += 1
            layer += 1
    elif (type(bottom_reinforcement_hook_extension) == (float, int)) or (
        bottom_reinforcement_hook_extension == None
    ):
        layer = 1
        while layer <= bottom_reinforcement_layers:
            bottom_reinforcement_hook_extension_dict["layer" + str(layer)] = []
            i = 0
            while i < len(
                bottom_reinforcement_number_diameter_offset_dict[
                    "layer" + str(layer)
                ]
            ):
                if (
                    bottom_reinforcement_rebar_type_dict["layer" + str(layer)][
                        i
                    ]
                    == "StraightRebar"
                ):
                    bottom_reinforcement_hook_extension_dict[
                        "layer" + str(layer)
                    ].append(None)
                else:
                    if bottom_reinforcement_hook_extension == None:
                        bottom_reinforcement_hook_extension = (
                            10
                            * bottom_reinforcement_number_diameter_offset_dict[
                                "layer" + str(layer)
                            ][i][1]
                        )
                    bottom_reinforcement_hook_extension_dict[
                        "layer" + str(layer)
                    ].append(bottom_reinforcement_hook_extension)
                i += 1
            layer += 1

    bottom_reinforcement_hook_orientation_dict = {}
    if type(bottom_reinforcement_hook_orientation) in (list, tuple):
        layer = 1
        while layer <= bottom_reinforcement_layers:
            bottom_reinforcement_hook_orientation_dict[
                "layer" + str(layer)
            ] = []
            if type(bottom_reinforcement_hook_orientation[layer - 1]) in (
                list,
                tuple,
            ):
                bottom_reinforcement_hook_orientation_dict[
                    "layer" + str(layer)
                ] = bottom_reinforcement_hook_orientation[layer - 1]
            elif type(bottom_reinforcement_hook_orientation[layer - 1]) == str:
                i = 0
                while i < len(
                    bottom_reinforcement_number_diameter_offset_dict[
                        "layer" + str(layer)
                    ]
                ):
                    if (
                        bottom_reinforcement_rebar_type_dict[
                            "layer" + str(layer)
                        ][i]
                        == "StraightRebar"
                    ):
                        bottom_reinforcement_hook_orientation_dict[
                            "layer" + str(layer)
                        ].append(None)
                    else:
                        bottom_reinforcement_hook_orientation_dict[
                            "layer" + str(layer)
                        ].append(
                            bottom_reinforcement_hook_orientation[layer - 1]
                        )
                    i += 1
            layer += 1
    elif type(bottom_reinforcement_hook_orientation) == str:
        layer = 1
        while layer <= bottom_reinforcement_layers:
            bottom_reinforcement_hook_orientation_dict[
                "layer" + str(layer)
            ] = []
            i = 0
            while i < len(
                bottom_reinforcement_number_diameter_offset_dict[
                    "layer" + str(layer)
                ]
            ):
                if (
                    bottom_reinforcement_rebar_type_dict["layer" + str(layer)][
                        i
                    ]
                    == "StraightRebar"
                ):
                    bottom_reinforcement_hook_orientation_dict[
                        "layer" + str(layer)
                    ].append(None)
                else:
                    bottom_reinforcement_hook_orientation_dict[
                        "layer" + str(layer)
                    ].append(bottom_reinforcement_hook_orientation)
                i += 1
            layer += 1

    FacePRM = getParametersOfFace(structure, facename)
    face_width = FacePRM[0][0]
    bottom_reinforcement_span_length = (
        face_width
        - l_cover_of_stirrup
        - r_cover_of_stirrup
        - 2 * dia_of_stirrup
    )

    req_space_for_bottom_reinforcement = []
    bottom_reinforcement_rebars_number = []
    spacing_in_bottom_reinforcement = []
    layer = 1
    while layer <= bottom_reinforcement_layers:
        req_space_for_bottom_reinforcement.append(
            sum(
                x[0] * x[1]
                for x in bottom_reinforcement_number_diameter_offset_dict[
                    "layer" + str(layer)
                ]
            )
        )
        bottom_reinforcement_rebars_number.append(
            sum(
                x[0]
                for x in bottom_reinforcement_number_diameter_offset_dict[
                    "layer" + str(layer)
                ]
            )
        )
        spacing_in_bottom_reinforcement.append(
            (
                bottom_reinforcement_span_length
                - req_space_for_bottom_reinforcement[-1]
            )
            / (bottom_reinforcement_rebars_number[-1] - 1)
        )
        layer += 1

    coverAlong = "Bottom Side"
    bottom_reinforcement_rebars = []
    layer = 1
    while layer <= bottom_reinforcement_layers:
        bottom_reinforcement_number_diameter_offset_list = bottom_reinforcement_number_diameter_offset_dict[
            "layer" + str(layer)
        ]
        if layer == 1:
            b_cover = b_cover_of_stirrup + dia_of_stirrup
        else:
            b_cover += (
                max(
                    x[1]
                    for x in bottom_reinforcement_number_diameter_offset_list
                )
                + bottom_reinforcement_layer_spacing[layer - 2]
            )

        f_cover = l_cover_of_stirrup + dia_of_stirrup
        for i, (number, diameter, offset) in enumerate(
            bottom_reinforcement_number_diameter_offset_list
        ):
            if i == 0:
                r_cover = l_cover = offset
            rear_cover = (
                face_width
                - f_cover
                - number * diameter
                - (number - 1) * spacing_in_bottom_reinforcement[layer - 1]
            )
            if (
                bottom_reinforcement_rebar_type_dict["layer" + str(layer)][i]
                == "StraightRebar"
            ):
                bottom_reinforcement_rebars.append(
                    makeStraightRebar(
                        f_cover,
                        (coverAlong, b_cover),
                        r_cover,
                        l_cover,
                        diameter,
                        True,
                        number,
                        "Horizontal",
                        structure,
                        facename_for_b_rebars,
                    )
                )
                bottom_reinforcement_rebars[-1].OffsetEnd = (
                    rear_cover + diameter / 2
                )
            f_cover += (
                number * diameter
                + number * spacing_in_bottom_reinforcement[layer - 1]
            )
        layer += 1
    print("WIP")
    FreeCAD.ActiveDocument.recompute()
    return bottom_reinforcement_rebars
