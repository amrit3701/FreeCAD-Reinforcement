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

from Stirrup import makeStirrup, editStirrup
from StraightRebar import makeStraightRebar
from LShapeRebar import makeLShapeRebar
from Rebarfunc import (
    getParametersOfFace,
    getFaceNumber,
    getFacenamesforBeamReinforcement,
    gettupleOfNumberDiameterOffset,
    getdictofNumberDiameterOffset,
    _BeamReinforcementGroup,
    _ViewProviderBeamReinforcementGroup,
    print_in_freecad_console,
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
    top_reinforcement_l_rebar_rounding=2,
    top_reinforcement_hook_extension=40,
    top_reinforcement_hook_orientation="Front Inside",
    bottom_reinforcement_l_rebar_rounding=2,
    bottom_reinforcement_hook_extension=40,
    bottom_reinforcement_hook_orientation="Front Inside",
    left_l_rebar_rounding=2,
    left_rebars_hook_extension=40,
    left_rebars_hook_orientation="Front Inside",
    right_l_rebar_rounding=2,
    right_rebars_hook_extension=40,
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
    TopReinforcementLRebarRounding, TopReinforcementHookLength,
    TopReinforcementHookOrientation, BottomReinforcementLRebarRounding,
    BottomReinforcementHookLength, BottomReinforcementHookOrientation,
    LeftLRebarRounding, LeftRebarsHookLength, LeftRebarsHookOrientation,
    RightLRebarRounding, RightRebarsHookLength, RightRebarsHookOrientation,
    Structure, Facename):

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
    bottom_reinforcement_hook_orientation, top_reinforcement_hook_extension,
    bottom_reinforcement_hook_extension, top_reinforcement_l_rebar_rounding and
    bottom_reinforcement_l_rebar_rounding can be similar to as discussed above
    for top_reinforcement_rebar_type.

    left_rebars_number_diameter_offset and right_rebars_number_diameter_offset
    are string of number_diameter_offset.
    Syntax: "number1#diameter1@offset1+number2#diameter2@offset2+..."

    Possible values for left_rebars_type and right_rebars_type:
    1. 'StraightRebar' or 'LShapeRebar'
    2. ('<rebar_type>', '<rebar_type>', ...) and each element of tuple
    represents rabar_type for each set of rebars.

    Possible values for left_l_rebar_rounding, right_l_rebar_rounding
    left_rebars_hook_extension, right_rebars_hook_extension,
    left_rebars_hook_orientation and right_rebars_hook_orientation can be
    similar to as discussed above for left_rebars_type.

    left_rebars_spacing/right_rebars_spacing is clear spacing between left/right
    rebars.
    """
    if not structure and not facename:
        if FreeCAD.GuiUp:
            selected_obj = FreeCADGui.Selection.getSelectionEx()[0]
            structure = selected_obj.Object
            facename = selected_obj.SubElementNames[0]
        else:
            showWarning("Error: Pass structure and facename arguments")
            return None

    # Create TwoLeggedBeam group object
    TwoLeggedBeam = _TwoLeggedBeam()
    if FreeCAD.GuiUp:
        _ViewProviderBeamReinforcementGroup(TwoLeggedBeam.Object.ViewObject)

    if isinstance(top_reinforcement_number_diameter_offset, str):
        top_reinforcement_number_diameter_offset = (
            top_reinforcement_number_diameter_offset,
        )
    if isinstance(bottom_reinforcement_number_diameter_offset, str):
        bottom_reinforcement_number_diameter_offset = (
            bottom_reinforcement_number_diameter_offset,
        )

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
    stirrup = makeStirrup(
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
    TwoLeggedBeam.addStirrups(stirrup)

    # Create top reinforcement
    makeTopReinforcement(
        TwoLeggedBeam,
        l_cover_of_stirrup,
        r_cover_of_stirrup,
        t_cover_of_stirrup,
        b_cover_of_stirrup,
        offset_of_stirrup,
        dia_of_stirrup,
        top_reinforcement_number_diameter_offset,
        top_reinforcement_rebar_type,
        top_reinforcement_layer_spacing,
        top_reinforcement_l_rebar_rounding,
        top_reinforcement_hook_extension,
        top_reinforcement_hook_orientation,
        facename,
        structure,
    )

    # Create bottom reinforcement
    makeBottomReinforcement(
        TwoLeggedBeam,
        l_cover_of_stirrup,
        r_cover_of_stirrup,
        t_cover_of_stirrup,
        b_cover_of_stirrup,
        offset_of_stirrup,
        dia_of_stirrup,
        bottom_reinforcement_number_diameter_offset,
        bottom_reinforcement_rebar_type,
        bottom_reinforcement_layer_spacing,
        bottom_reinforcement_l_rebar_rounding,
        bottom_reinforcement_hook_extension,
        bottom_reinforcement_hook_orientation,
        facename,
        structure,
    )

    # Create left reinforcement
    left_reinforcement_rebars = makeLeftReinforcement(
        TwoLeggedBeam,
        l_cover_of_stirrup,
        dia_of_stirrup,
        left_rebars_number_diameter_offset,
        left_rebars_type,
        left_rebars_spacing,
        left_l_rebar_rounding,
        left_rebars_hook_extension,
        left_rebars_hook_orientation,
        structure,
        facename,
    )

    # Create right reinforcement
    right_reinforcement_rebars = makeRightReinforcement(
        TwoLeggedBeam,
        r_cover_of_stirrup,
        dia_of_stirrup,
        right_rebars_number_diameter_offset,
        right_rebars_type,
        right_rebars_spacing,
        right_l_rebar_rounding,
        right_rebars_hook_extension,
        right_rebars_hook_orientation,
        structure,
        facename,
    )

    if not left_reinforcement_rebars and not right_reinforcement_rebars:
        FreeCAD.ActiveDocument.removeObject(
            TwoLeggedBeam.shear_reinforcement_group.Name
        )

    FreeCAD.ActiveDocument.recompute()
    return TwoLeggedBeam.Object


def makeTopReinforcement(
    obj,
    l_cover_of_stirrup,
    r_cover_of_stirrup,
    t_cover_of_stirrup,
    b_cover_of_stirrup,
    offset_of_stirrup,
    dia_of_stirrup,
    top_reinforcement_number_diameter_offset,
    top_reinforcement_rebar_type,
    top_reinforcement_layer_spacing,
    top_reinforcement_l_rebar_rounding,
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

    top_reinforcement_rebar_type_list = []
    if isinstance(top_reinforcement_rebar_type, list) or isinstance(
        top_reinforcement_rebar_type, tuple
    ):
        layer = 1
        while layer <= top_reinforcement_layers:
            if isinstance(
                top_reinforcement_rebar_type[layer - 1], list
            ) or isinstance(top_reinforcement_rebar_type[layer - 1], tuple):
                top_reinforcement_rebar_type_list.append(
                    top_reinforcement_rebar_type[layer - 1]
                )
            elif isinstance(top_reinforcement_rebar_type[layer - 1], str):
                top_reinforcement_rebar_type_list.append([])
                i = 0
                while i < len(
                    top_reinforcement_number_diameter_offset_dict[
                        "layer" + str(layer)
                    ]
                ):
                    top_reinforcement_rebar_type_list[-1].append(
                        top_reinforcement_rebar_type[layer - 1]
                    )
                    i += 1
            layer += 1
    elif isinstance(top_reinforcement_rebar_type, str):
        layer = 1
        while layer <= top_reinforcement_layers:
            top_reinforcement_rebar_type_list.append([])
            i = 0
            while i < len(
                top_reinforcement_number_diameter_offset_dict[
                    "layer" + str(layer)
                ]
            ):
                top_reinforcement_rebar_type_list[-1].append(
                    top_reinforcement_rebar_type
                )
                i += 1
            layer += 1

    if isinstance(top_reinforcement_layer_spacing, float) or isinstance(
        top_reinforcement_layer_spacing, int
    ):
        top_reinforcement_layer_spacing = [top_reinforcement_layer_spacing]
        i = 0
        while i < top_reinforcement_layers - 1:
            top_reinforcement_layer_spacing.append(
                top_reinforcement_layer_spacing[0]
            )
            i += 1

    top_reinforcement_l_rebar_rounding_list = []
    if isinstance(top_reinforcement_l_rebar_rounding, list) or isinstance(
        top_reinforcement_l_rebar_rounding, tuple
    ):
        layer = 1
        while layer <= top_reinforcement_layers:
            if isinstance(
                top_reinforcement_l_rebar_rounding[layer - 1], list
            ) or isinstance(
                top_reinforcement_l_rebar_rounding[layer - 1], tuple
            ):
                top_reinforcement_l_rebar_rounding_list.append(
                    top_reinforcement_l_rebar_rounding[layer - 1]
                )
            elif isinstance(
                top_reinforcement_l_rebar_rounding[layer - 1], float
            ) or isinstance(top_reinforcement_l_rebar_rounding[layer - 1], int):
                top_reinforcement_l_rebar_rounding_list.append([])
                i = 0
                while i < len(
                    top_reinforcement_number_diameter_offset_dict[
                        "layer" + str(layer)
                    ]
                ):
                    if (
                        top_reinforcement_rebar_type_list[layer - 1][i]
                        == "StraightRebar"
                    ):
                        top_reinforcement_l_rebar_rounding_list(-1).append(None)
                    else:
                        top_reinforcement_l_rebar_rounding_list(-1).append(
                            top_reinforcement_l_rebar_rounding[layer - 1]
                        )
                    i += 1
            layer += 1
    elif isinstance(top_reinforcement_l_rebar_rounding, float) or isinstance(
        top_reinforcement_l_rebar_rounding, int
    ):
        layer = 1
        while layer <= top_reinforcement_layers:
            top_reinforcement_l_rebar_rounding_list.append([])
            i = 0
            while i < len(
                top_reinforcement_number_diameter_offset_dict[
                    "layer" + str(layer)
                ]
            ):
                if (
                    top_reinforcement_rebar_type_list[layer - 1][i]
                    == "StraightRebar"
                ):
                    top_reinforcement_l_rebar_rounding_list[layer - 1].append(
                        None
                    )
                else:
                    top_reinforcement_l_rebar_rounding_list[layer - 1].append(
                        top_reinforcement_l_rebar_rounding
                    )
                i += 1
            layer += 1

    top_reinforcement_hook_extension_list = []
    if isinstance(top_reinforcement_hook_extension, list) or isinstance(
        top_reinforcement_hook_extension, tuple
    ):
        layer = 1
        while layer <= top_reinforcement_layers:
            if isinstance(
                top_reinforcement_hook_extension[layer - 1], list
            ) or isinstance(top_reinforcement_hook_extension[layer - 1], tuple):
                top_reinforcement_hook_extension_list.append(
                    top_reinforcement_hook_extension[layer - 1]
                )
            elif isinstance(
                top_reinforcement_hook_extension[layer - 1], float
            ) or isinstance(top_reinforcement_hook_extension[layer - 1], int):
                top_reinforcement_hook_extension_list.append([])
                i = 0
                while i < len(
                    top_reinforcement_number_diameter_offset_dict[
                        "layer" + str(layer)
                    ]
                ):
                    if (
                        top_reinforcement_rebar_type_list[layer - 1][i]
                        == "StraightRebar"
                    ):
                        top_reinforcement_hook_extension_list[-1].append(None)
                    else:
                        top_reinforcement_hook_extension_list[-1].append(
                            top_reinforcement_hook_extension[layer - 1]
                        )
                    i += 1
            layer += 1
    elif isinstance(top_reinforcement_hook_extension, float) or isinstance(
        top_reinforcement_hook_extension, int
    ):
        layer = 1
        while layer <= top_reinforcement_layers:
            top_reinforcement_hook_extension_list.append([])
            i = 0
            while i < len(
                top_reinforcement_number_diameter_offset_dict[
                    "layer" + str(layer)
                ]
            ):
                if (
                    top_reinforcement_rebar_type_list[layer - 1][i]
                    == "StraightRebar"
                ):
                    top_reinforcement_hook_extension_list[-1].append(None)
                else:
                    top_reinforcement_hook_extension_list[-1].append(
                        top_reinforcement_hook_extension
                    )
                i += 1
            layer += 1

    top_reinforcement_hook_orientation_list = []
    if isinstance(top_reinforcement_hook_orientation, list) or isinstance(
        top_reinforcement_hook_orientation, tuple
    ):
        layer = 1
        while layer <= top_reinforcement_layers:
            if isinstance(
                top_reinforcement_hook_orientation[layer - 1], list
            ) or isinstance(
                top_reinforcement_hook_orientation[layer - 1], tuple
            ):
                top_reinforcement_hook_orientation_list.append(
                    top_reinforcement_hook_orientation[layer - 1]
                )
            elif isinstance(top_reinforcement_hook_orientation[layer - 1], str):
                top_reinforcement_hook_orientation_list.append([])
                i = 0
                while i < len(
                    top_reinforcement_number_diameter_offset_dict[
                        "layer" + str(layer)
                    ]
                ):
                    if (
                        top_reinforcement_rebar_type_list[layer - 1][i]
                        == "StraightRebar"
                    ):
                        top_reinforcement_hook_orientation_list[-1].append(None)
                    else:
                        top_reinforcement_hook_orientation_list[-1].append(
                            top_reinforcement_hook_orientation[layer - 1]
                        )
                    i += 1
            layer += 1
    elif isinstance(top_reinforcement_hook_orientation, str):
        layer = 1
        while layer <= top_reinforcement_layers:
            top_reinforcement_hook_orientation_list.append([])
            i = 0
            while i < len(
                top_reinforcement_number_diameter_offset_dict[
                    "layer" + str(layer)
                ]
            ):
                if (
                    top_reinforcement_rebar_type_list[layer - 1][i]
                    == "StraightRebar"
                ):
                    top_reinforcement_hook_orientation_list[-1].append(None)
                else:
                    top_reinforcement_hook_orientation_list[-1].append(
                        top_reinforcement_hook_orientation
                    )
                i += 1
            layer += 1

    FacePRM = getParametersOfFace(structure, facename)
    face_length = FacePRM[0][0]
    face_width = FacePRM[0][1]
    top_reinforcement_span_length = (
        face_length
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
        if top_reinforcement_rebars_number[-1] == 1:
            spacing_in_top_reinforcement.append(
                (
                    top_reinforcement_span_length
                    - req_space_for_top_reinforcement[-1]
                )
                / 2
            )
        else:
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
        if top_reinforcement_rebars_number[layer - 1] == 1:
            f_cover += spacing_in_top_reinforcement[layer - 1]

        for i, (number, diameter, offset) in enumerate(
            top_reinforcement_number_diameter_offset_list
        ):
            r_cover = l_cover = offset
            rear_cover = (
                face_length
                - f_cover
                - number * diameter
                - (number - 1) * spacing_in_top_reinforcement[layer - 1]
            )
            if (
                top_reinforcement_rebar_type_list[layer - 1][i]
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
            else:
                if layer == 1:
                    b_cover = face_width - t_cover - diameter / 2
                else:
                    b_cover = (
                        face_width
                        - t_cover
                        - sum(
                            x
                            for x in top_reinforcement_layer_spacing[
                                : layer - 1
                            ]
                        )
                        - diameter / 2
                    )
                if top_reinforcement_hook_orientation_list[layer - 1][i] in (
                    "Front Inside",
                    "Rear Inside",
                ):
                    b_cover -= (
                        top_reinforcement_l_rebar_rounding_list[layer - 1][i]
                        * diameter
                        + top_reinforcement_hook_extension_list[layer - 1][i]
                    )
                    if (
                        top_reinforcement_hook_orientation_list[layer - 1][i]
                        == "Front Inside"
                    ):
                        orientation = "Top Right"
                    else:
                        orientation = "Top Left"
                else:
                    b_cover += (
                        top_reinforcement_l_rebar_rounding_list[layer - 1][i]
                        * diameter
                        + top_reinforcement_hook_extension_list[layer - 1][i]
                    )
                    if (
                        top_reinforcement_hook_orientation_list[layer - 1][i]
                        == "Front Outside"
                    ):
                        orientation = "Top Right"
                    else:
                        orientation = "Top Left"

                top_reinforcement_rebars.append(
                    makeLShapeRebar(
                        f_cover,
                        b_cover,
                        l_cover,
                        r_cover,
                        diameter,
                        t_cover,
                        top_reinforcement_l_rebar_rounding_list[layer - 1][i],
                        True,
                        number,
                        orientation,
                        structure,
                        facename_for_t_rebars,
                    )
                )
            top_reinforcement_rebars[-1].OffsetEnd = rear_cover + diameter / 2
            f_cover += (
                number * diameter
                + number * spacing_in_top_reinforcement[layer - 1]
            )
        layer += 1
    FreeCAD.ActiveDocument.recompute()

    obj.addTopRebars(top_reinforcement_rebars)
    properties_values = []
    properties_values.append(
        ("NumberDiameterOffset", top_reinforcement_number_diameter_offset)
    )
    properties_values.append(
        ("RebarType", str(top_reinforcement_rebar_type_list))
    )
    properties_values.append(
        ("LayerSpacing", list(top_reinforcement_layer_spacing))
    )
    properties_values.append(
        ("HookExtension", str(top_reinforcement_hook_extension_list))
    )
    properties_values.append(
        ("HookOrientation", str(top_reinforcement_hook_orientation_list))
    )
    obj.setPropertiesValues(properties_values, obj.top_reinforcement_group)
    return top_reinforcement_rebars


def makeBottomReinforcement(
    obj,
    l_cover_of_stirrup,
    r_cover_of_stirrup,
    t_cover_of_stirrup,
    b_cover_of_stirrup,
    offset_of_stirrup,
    dia_of_stirrup,
    bottom_reinforcement_number_diameter_offset,
    bottom_reinforcement_rebar_type,
    bottom_reinforcement_layer_spacing,
    bottom_reinforcement_l_rebar_rounding,
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

    bottom_reinforcement_rebar_type_list = []
    if isinstance(bottom_reinforcement_rebar_type, list) or isinstance(
        bottom_reinforcement_rebar_type, tuple
    ):
        layer = 1
        while layer <= bottom_reinforcement_layers:
            if isinstance(
                bottom_reinforcement_rebar_type[layer - 1], list
            ) or isinstance(bottom_reinforcement_rebar_type[layer - 1], tuple):
                bottom_reinforcement_rebar_type_list.append(
                    bottom_reinforcement_rebar_type[layer - 1]
                )
            elif isinstance(bottom_reinforcement_rebar_type[layer - 1], str):
                bottom_reinforcement_rebar_type_list.append([])
                i = 0
                while i < len(
                    bottom_reinforcement_number_diameter_offset_dict[
                        "layer" + str(layer)
                    ]
                ):
                    bottom_reinforcement_rebar_type_list[-1].append(
                        bottom_reinforcement_rebar_type[layer - 1]
                    )
                    i += 1
            layer += 1
    elif isinstance(bottom_reinforcement_rebar_type, str):
        layer = 1
        while layer <= bottom_reinforcement_layers:
            bottom_reinforcement_rebar_type_list.append([])
            i = 0
            while i < len(
                bottom_reinforcement_number_diameter_offset_dict[
                    "layer" + str(layer)
                ]
            ):
                bottom_reinforcement_rebar_type_list[-1].append(
                    bottom_reinforcement_rebar_type
                )
                i += 1
            layer += 1

    if isinstance(bottom_reinforcement_layer_spacing, float) or isinstance(
        bottom_reinforcement_layer_spacing, int
    ):
        bottom_reinforcement_layer_spacing = [
            bottom_reinforcement_layer_spacing
        ]
        i = 0
        while i < bottom_reinforcement_layers - 1:
            bottom_reinforcement_layer_spacing.append(
                bottom_reinforcement_layer_spacing[0]
            )
            i += 1

    bottom_reinforcement_l_rebar_rounding_list = []
    if isinstance(bottom_reinforcement_l_rebar_rounding, list) or isinstance(
        bottom_reinforcement_l_rebar_rounding, tuple
    ):
        layer = 1
        while layer <= bottom_reinforcement_layers:
            if isinstance(
                bottom_reinforcement_l_rebar_rounding[layer - 1], list
            ) or isinstance(
                bottom_reinforcement_l_rebar_rounding[layer - 1], tuple
            ):
                bottom_reinforcement_l_rebar_rounding_list.append(
                    bottom_reinforcement_l_rebar_rounding[layer - 1]
                )
            elif isinstance(
                bottom_reinforcement_l_rebar_rounding[layer - 1], float
            ) or isinstance(
                bottom_reinforcement_l_rebar_rounding[layer - 1], int
            ):
                bottom_reinforcement_l_rebar_rounding_list.append([])
                i = 0
                while i < len(
                    bottom_reinforcement_number_diameter_offset_dict[
                        "layer" + str(layer)
                    ]
                ):
                    if (
                        bottom_reinforcement_rebar_type_list[layer - 1][i]
                        == "StraightRebar"
                    ):
                        bottom_reinforcement_l_rebar_rounding_list(-1).append(
                            None
                        )
                    else:
                        bottom_reinforcement_l_rebar_rounding_list(-1).append(
                            bottom_reinforcement_l_rebar_rounding[layer - 1]
                        )
                    i += 1
            layer += 1
    elif isinstance(bottom_reinforcement_l_rebar_rounding, float) or isinstance(
        bottom_reinforcement_l_rebar_rounding, int
    ):
        layer = 1
        while layer <= bottom_reinforcement_layers:
            bottom_reinforcement_l_rebar_rounding_list.append([])
            i = 0
            while i < len(
                bottom_reinforcement_number_diameter_offset_dict[
                    "layer" + str(layer)
                ]
            ):
                if (
                    bottom_reinforcement_rebar_type_list[layer - 1][i]
                    == "StraightRebar"
                ):
                    bottom_reinforcement_l_rebar_rounding_list[
                        layer - 1
                    ].append(None)
                else:
                    bottom_reinforcement_l_rebar_rounding_list[
                        layer - 1
                    ].append(bottom_reinforcement_l_rebar_rounding)
                i += 1
            layer += 1

    bottom_reinforcement_hook_extension_list = []
    if isinstance(bottom_reinforcement_hook_extension, list) or isinstance(
        bottom_reinforcement_hook_extension, tuple
    ):
        layer = 1
        while layer <= bottom_reinforcement_layers:
            if isinstance(
                bottom_reinforcement_hook_extension[layer - 1], list
            ) or isinstance(
                bottom_reinforcement_hook_extension[layer - 1], tuple
            ):
                bottom_reinforcement_hook_extension_list.append(
                    bottom_reinforcement_hook_extension[layer - 1]
                )
            elif isinstance(
                bottom_reinforcement_hook_extension[layer - 1], float
            ) or isinstance(
                bottom_reinforcement_hook_extension[layer - 1], int
            ):
                bottom_reinforcement_hook_extension_list.append([])
                i = 0
                while i < len(
                    bottom_reinforcement_number_diameter_offset_dict[
                        "layer" + str(layer)
                    ]
                ):
                    if (
                        bottom_reinforcement_rebar_type_list[layer - 1][i]
                        == "StraightRebar"
                    ):
                        bottom_reinforcement_hook_extension_list[-1].append(
                            None
                        )
                    else:
                        bottom_reinforcement_hook_extension_list[-1].append(
                            bottom_reinforcement_hook_extension[layer - 1]
                        )
                    i += 1
            layer += 1
    elif isinstance(bottom_reinforcement_hook_extension, float) or isinstance(
        bottom_reinforcement_hook_extension, int
    ):
        layer = 1
        while layer <= bottom_reinforcement_layers:
            bottom_reinforcement_hook_extension_list.append([])
            i = 0
            while i < len(
                bottom_reinforcement_number_diameter_offset_dict[
                    "layer" + str(layer)
                ]
            ):
                if (
                    bottom_reinforcement_rebar_type_list[layer - 1][i]
                    == "StraightRebar"
                ):
                    bottom_reinforcement_hook_extension_list[-1].append(None)
                else:
                    bottom_reinforcement_hook_extension_list[-1].append(
                        bottom_reinforcement_hook_extension
                    )
                i += 1
            layer += 1

    bottom_reinforcement_hook_orientation_list = []
    if isinstance(bottom_reinforcement_hook_orientation, list) or isinstance(
        bottom_reinforcement_hook_orientation, tuple
    ):
        layer = 1
        while layer <= bottom_reinforcement_layers:
            if isinstance(
                bottom_reinforcement_hook_orientation[layer - 1], list
            ) or isinstance(
                bottom_reinforcement_hook_orientation[layer - 1], tuple
            ):
                bottom_reinforcement_hook_orientation_list.append(
                    bottom_reinforcement_hook_orientation[layer - 1]
                )
            elif isinstance(
                bottom_reinforcement_hook_orientation[layer - 1], str
            ):
                bottom_reinforcement_hook_orientation_list.append([])
                i = 0
                while i < len(
                    bottom_reinforcement_number_diameter_offset_dict[
                        "layer" + str(layer)
                    ]
                ):
                    if (
                        bottom_reinforcement_rebar_type_list[layer - 1][i]
                        == "StraightRebar"
                    ):
                        bottom_reinforcement_hook_orientation_list[-1].append(
                            None
                        )
                    else:
                        bottom_reinforcement_hook_orientation_list[-1].append(
                            bottom_reinforcement_hook_orientation[layer - 1]
                        )
                    i += 1
            layer += 1
    elif isinstance(bottom_reinforcement_hook_orientation, str):
        layer = 1
        while layer <= bottom_reinforcement_layers:
            bottom_reinforcement_hook_orientation_list.append([])
            i = 0
            while i < len(
                bottom_reinforcement_number_diameter_offset_dict[
                    "layer" + str(layer)
                ]
            ):
                if (
                    bottom_reinforcement_rebar_type_list[layer - 1][i]
                    == "StraightRebar"
                ):
                    bottom_reinforcement_hook_orientation_list[-1].append(None)
                else:
                    bottom_reinforcement_hook_orientation_list[-1].append(
                        bottom_reinforcement_hook_orientation
                    )
                i += 1
            layer += 1

    FacePRM = getParametersOfFace(structure, facename)
    face_length = FacePRM[0][0]
    face_width = FacePRM[0][1]
    bottom_reinforcement_span_length = (
        face_length
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
        if bottom_reinforcement_rebars_number[-1] == 1:
            spacing_in_bottom_reinforcement.append(
                (
                    bottom_reinforcement_span_length
                    - req_space_for_bottom_reinforcement[-1]
                )
                / 2
            )
        else:
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
        if bottom_reinforcement_rebars_number[layer - 1] == 1:
            f_cover += spacing_in_bottom_reinforcement[layer - 1]

        for i, (number, diameter, offset) in enumerate(
            bottom_reinforcement_number_diameter_offset_list
        ):
            r_cover = l_cover = offset
            rear_cover = (
                face_length
                - f_cover
                - number * diameter
                - (number - 1) * spacing_in_bottom_reinforcement[layer - 1]
            )
            if (
                bottom_reinforcement_rebar_type_list[layer - 1][i]
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
            else:
                if layer == 1:
                    t_cover = face_width - b_cover - diameter / 2
                else:
                    t_cover = (
                        face_width
                        - b_cover
                        - sum(
                            x
                            for x in bottom_reinforcement_layer_spacing[
                                : layer - 1
                            ]
                        )
                        - diameter / 2
                    )
                if bottom_reinforcement_hook_orientation_list[layer - 1][i] in (
                    "Front Inside",
                    "Rear Inside",
                ):
                    t_cover -= (
                        bottom_reinforcement_l_rebar_rounding_list[layer - 1][i]
                        * diameter
                        + bottom_reinforcement_hook_extension_list[layer - 1][i]
                    )
                    if (
                        bottom_reinforcement_hook_orientation_list[layer - 1][i]
                        == "Front Inside"
                    ):
                        orientation = "Bottom Right"
                    else:
                        orientation = "Bottom Left"
                else:
                    t_cover += (
                        bottom_reinforcement_l_rebar_rounding_list[layer - 1][i]
                        * diameter
                        + bottom_reinforcement_hook_extension_list[layer - 1][i]
                    )
                    if (
                        bottom_reinforcement_hook_orientation_list[layer - 1][i]
                        == "Front Outside"
                    ):
                        orientation = "Bottom Right"
                    else:
                        orientation = "Bottom Left"

                bottom_reinforcement_rebars.append(
                    makeLShapeRebar(
                        f_cover,
                        b_cover,
                        l_cover,
                        r_cover,
                        diameter,
                        t_cover,
                        bottom_reinforcement_l_rebar_rounding_list[layer - 1][
                            i
                        ],
                        True,
                        number,
                        orientation,
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
    FreeCAD.ActiveDocument.recompute()

    obj.addBottomRebars(bottom_reinforcement_rebars)
    properties_values = []
    properties_values.append(
        ("NumberDiameterOffset", bottom_reinforcement_number_diameter_offset)
    )
    properties_values.append(
        ("RebarType", str(bottom_reinforcement_rebar_type_list))
    )
    properties_values.append(
        ("LayerSpacing", list(bottom_reinforcement_layer_spacing))
    )
    properties_values.append(
        ("HookExtension", str(bottom_reinforcement_hook_extension_list))
    )
    properties_values.append(
        ("HookOrientation", str(bottom_reinforcement_hook_orientation_list))
    )
    obj.setPropertiesValues(properties_values, obj.bottom_reinforcement_group)

    return bottom_reinforcement_rebars


def makeLeftReinforcement(
    obj,
    l_cover_of_stirrup,
    dia_of_stirrup,
    left_rebars_number_diameter_offset,
    left_rebars_type,
    left_rebars_spacing,
    left_l_rebar_rounding,
    left_rebars_hook_extension,
    left_rebars_hook_orientation,
    structure,
    facename,
):
    if not left_rebars_number_diameter_offset:
        FreeCAD.ActiveDocument.removeObject(obj.left_rebars_group.Name)
        return None

    facename_for_s_rebars = getFacenamesforBeamReinforcement(
        facename, structure
    )[1]
    face = structure.Shape.Faces[getFaceNumber(facename) - 1]
    FacePRM = getParametersOfFace(structure, facename)
    face_length = FacePRM[0][0]
    face_width = FacePRM[0][1]

    left_rebars_number_diameter_offset_tuple = gettupleOfNumberDiameterOffset(
        left_rebars_number_diameter_offset
    )

    left_rebars_type_list = []
    if isinstance(left_rebars_type, str):
        i = 0
        while i < len(left_rebars_number_diameter_offset_tuple):
            left_rebars_type_list.append(left_rebars_type)
            i += 1
    elif isinstance(left_rebars_type, list) or isinstance(
        left_rebars_type, tuple
    ):
        left_rebars_type_list = list(left_rebars_type)

    left_l_rebar_rounding_list = []
    if isinstance(left_l_rebar_rounding, float) or isinstance(
        left_l_rebar_rounding, int
    ):
        i = 0
        while i < len(left_rebars_number_diameter_offset_tuple):
            if left_rebars_type_list[i] == "StraightRebar":
                left_l_rebar_rounding_list.append(0)
            else:
                left_l_rebar_rounding_list.append(left_l_rebar_rounding)
            i += 1
    elif isinstance(left_l_rebar_rounding, list) or isinstance(
        left_l_rebar_rounding, tuple
    ):
        left_l_rebar_rounding_list = list(left_l_rebar_rounding)

    left_rebars_hook_extension_list = []
    if isinstance(left_rebars_hook_extension, float) or isinstance(
        left_rebars_hook_extension, int
    ):
        i = 0
        while i < len(left_rebars_number_diameter_offset_tuple):
            if left_rebars_type_list[i] == "StraightRebar":
                left_rebars_hook_extension_list.append(0)
            else:
                left_rebars_hook_extension_list.append(
                    left_rebars_hook_extension
                )
            i += 1
    elif isinstance(left_rebars_hook_extension, list) or isinstance(
        left_rebars_hook_extension, tuple
    ):
        for i, _ in enumerate(left_rebars_number_diameter_offset_tuple):
            if left_rebars_type_list[i] == "StraightRebar":
                left_rebars_hook_extension_list.append(0)
            elif left_rebars_hook_extension[i] == None:
                left_rebars_hook_extension_list.append(10)
            else:
                left_rebars_hook_extension_list.append(
                    left_rebars_hook_extension[i]
                )
    elif left_rebars_hook_extension == None:
        for i, _ in enumerate(left_rebars_number_diameter_offset_tuple):
            if left_rebars_type_list[i] == "StraightRebar":
                left_rebars_hook_extension_list.append(0)
            else:
                left_rebars_hook_extension_list.append(10)

    left_rebars_hook_orientation_list = []
    if isinstance(left_rebars_hook_orientation, str):
        i = 0
        while i < len(left_rebars_number_diameter_offset_tuple):
            if left_rebars_type_list[i] == "StraightRebar":
                left_rebars_hook_orientation_list.append("")
            else:
                left_rebars_hook_orientation_list.append(
                    left_rebars_hook_orientation
                )
            i += 1
    elif isinstance(left_rebars_hook_orientation, list) or isinstance(
        left_rebars_hook_orientation, tuple
    ):
        for i, _ in enumerate(left_rebars_number_diameter_offset_tuple):
            if left_rebars_type_list[i] == "StraightRebar":
                left_rebars_hook_orientation_list.append("")
            elif left_rebars_hook_orientation[i] == None:
                left_rebars_hook_orientation_list.append("Front Inside")
            else:
                left_rebars_hook_orientation_list.append(
                    left_rebars_hook_orientation[i]
                )
    elif left_rebars_hook_orientation == None:
        for i, _ in enumerate(left_rebars_number_diameter_offset_tuple):
            if left_rebars_type_list[i] == "StraightRebar":
                left_rebars_hook_orientation_list.append("")
            else:
                left_rebars_hook_orientation_list.append("Front Inside")

    left_rebars_number = sum(
        x[0] for x in left_rebars_number_diameter_offset_tuple
    )
    left_reinforcement_span_length = (
        left_rebars_number - 1
    ) * left_rebars_spacing + sum(
        x[0] * x[1] for x in left_rebars_number_diameter_offset_tuple
    )
    left_rebars_f_cover = (face_width - left_reinforcement_span_length) / 2

    left_reinforcement_rebars = []
    for i, (number, diameter, offset) in enumerate(
        left_rebars_number_diameter_offset_tuple
    ):
        t_cover = l_cover_of_stirrup + dia_of_stirrup
        r_cover = l_cover = offset
        rear_cover = (
            face_width
            - left_rebars_f_cover
            - number * diameter
            - (number - 1) * left_rebars_spacing
        )
        if left_rebars_type_list[i] == "StraightRebar":
            if face.normalAt(0, 0).x in (1, -1):
                orientation = "Horizontal"
                coverAlong = "Top Side"
            else:
                orientation = "Vertical"
                coverAlong = "Left Side"
            left_reinforcement_rebars.append(
                makeStraightRebar(
                    left_rebars_f_cover,
                    (coverAlong, t_cover),
                    r_cover,
                    l_cover,
                    diameter,
                    True,
                    number,
                    orientation,
                    structure,
                    facename_for_s_rebars,
                )
            )
        else:
            b_cover = face_length - t_cover - diameter / 2
            if left_rebars_hook_orientation_list[i] in (
                "Front Inside",
                "Rear Inside",
            ):
                b_cover -= (
                    left_l_rebar_rounding_list[i] * diameter
                    + left_rebars_hook_extension_list[i]
                )
                if left_rebars_hook_orientation_list[i] == "Front Inside":
                    if face.normalAt(0, 0).x in (1, -1):
                        orientation = "Top Right"
                    else:
                        orientation = "Top Left"
                else:
                    if face.normalAt(0, 0).x in (1, -1):
                        orientation = "Top Left"
                    else:
                        orientation = "Bottom Left"
            else:
                b_cover += (
                    left_l_rebar_rounding_list[i] * diameter
                    + left_rebars_hook_extension_list[i]
                )
                if left_rebars_hook_orientation_list[i] == "Front Outside":
                    if face.normalAt(0, 0).x in (1, -1):
                        orientation = "Top Right"
                    else:
                        orientation = "Top Left"
                else:
                    if face.normalAt(0, 0).x in (1, -1):
                        orientation = "Top Left"
                    else:
                        orientation = "Bottom Left"

            if face.normalAt(0, 0).y in (1, -1):
                l_cover = t_cover
                r_cover = b_cover
                t_cover = b_cover = offset

            left_reinforcement_rebars.append(
                makeLShapeRebar(
                    left_rebars_f_cover,
                    b_cover,
                    l_cover,
                    r_cover,
                    diameter,
                    t_cover,
                    left_l_rebar_rounding_list[i],
                    True,
                    number,
                    orientation,
                    structure,
                    facename_for_s_rebars,
                )
            )
        left_reinforcement_rebars[-1].OffsetEnd = rear_cover + diameter / 2
        left_rebars_f_cover += number * diameter + number * left_rebars_spacing

    obj.addLeftRebars(left_reinforcement_rebars)
    properties_values = []
    properties_values.append(
        ("NumberDiameterOffset", left_rebars_number_diameter_offset)
    )
    properties_values.append(("RebarType", left_rebars_type_list))
    properties_values.append(("RebarSpacing", left_rebars_spacing))
    properties_values.append(("HookExtension", left_rebars_hook_extension_list))
    properties_values.append(
        ("HookOrientation", left_rebars_hook_orientation_list)
    )
    obj.setPropertiesValues(properties_values, obj.left_rebars_group)

    return left_reinforcement_rebars


def makeRightReinforcement(
    obj,
    r_cover_of_stirrup,
    dia_of_stirrup,
    right_rebars_number_diameter_offset,
    right_rebars_type,
    right_rebars_spacing,
    right_l_rebar_rounding,
    right_rebars_hook_extension,
    right_rebars_hook_orientation,
    structure,
    facename,
):
    if not right_rebars_number_diameter_offset:
        FreeCAD.ActiveDocument.removeObject(obj.right_rebars_group.Name)
        return None

    facename_for_s_rebars = getFacenamesforBeamReinforcement(
        facename, structure
    )[1]
    face = structure.Shape.Faces[getFaceNumber(facename) - 1]
    FacePRM = getParametersOfFace(structure, facename)
    face_length = FacePRM[0][0]
    face_width = FacePRM[0][1]

    right_rebars_number_diameter_offset_tuple = gettupleOfNumberDiameterOffset(
        right_rebars_number_diameter_offset
    )

    right_rebars_type_list = []
    if isinstance(right_rebars_type, str):
        i = 0
        while i < len(right_rebars_number_diameter_offset_tuple):
            right_rebars_type_list.append(right_rebars_type)
            i += 1
    elif isinstance(right_rebars_type, list) or isinstance(
        right_rebars_type, tuple
    ):
        right_rebars_type_list = list(right_rebars_type)

    right_l_rebar_rounding_list = []
    if isinstance(right_l_rebar_rounding, float) or isinstance(
        right_l_rebar_rounding, int
    ):
        i = 0
        while i < len(right_rebars_number_diameter_offset_tuple):
            if right_rebars_type_list[i] == "StraightRebar":
                right_l_rebar_rounding_list.append(0)
            else:
                right_l_rebar_rounding_list.append(right_l_rebar_rounding)
            i += 1
    elif isinstance(right_l_rebar_rounding, list) or isinstance(
        right_l_rebar_rounding, tuple
    ):
        right_l_rebar_rounding_list = list(right_l_rebar_rounding)

    right_rebars_hook_extension_list = []
    if isinstance(right_rebars_hook_extension, float) or isinstance(
        right_rebars_hook_extension, int
    ):
        i = 0
        while i < len(right_rebars_number_diameter_offset_tuple):
            if right_rebars_type_list[i] == "StraightRebar":
                right_rebars_hook_extension_list.append(0)
            else:
                right_rebars_hook_extension_list.append(
                    right_rebars_hook_extension
                )
            i += 1
    elif isinstance(right_rebars_hook_extension, list) or isinstance(
        right_rebars_hook_extension, tuple
    ):
        for i, _ in enumerate(right_rebars_number_diameter_offset_tuple):
            if right_rebars_type_list[i] == "StraightRebar":
                right_rebars_hook_extension_list.append(0)
            elif right_rebars_hook_extension[i] == None:
                right_rebars_hook_extension_list.append(10)
            else:
                right_rebars_hook_extension_list.append(
                    right_rebars_hook_extension[i]
                )
    elif right_rebars_hook_extension == None:
        for i, _ in enumerate(right_rebars_number_diameter_offset_tuple):
            if right_rebars_type_list[i] == "StraightRebar":
                right_rebars_hook_extension_list.append(0)
            else:
                right_rebars_hook_extension_list.append(10)

    right_rebars_hook_orientation_list = []
    if isinstance(right_rebars_hook_orientation, str):
        i = 0
        while i < len(right_rebars_number_diameter_offset_tuple):
            if right_rebars_type_list[i] == "StraightRebar":
                right_rebars_hook_orientation_list.append("")
            else:
                right_rebars_hook_orientation_list.append(
                    right_rebars_hook_orientation
                )
            i += 1
    elif isinstance(right_rebars_hook_orientation, list) or isinstance(
        right_rebars_hook_orientation, tuple
    ):
        for i, _ in enumerate(right_rebars_number_diameter_offset_tuple):
            if right_rebars_type_list[i] == "StraightRebar":
                right_rebars_hook_orientation_list.append("")
            elif right_rebars_hook_orientation[i] == None:
                right_rebars_hook_orientation_list.append("Front Inside")
            else:
                right_rebars_hook_orientation_list.append(
                    right_rebars_hook_orientation[i]
                )
    elif right_rebars_hook_orientation == None:
        for i, _ in enumerate(right_rebars_number_diameter_offset_tuple):
            if right_rebars_type_list[i] == "StraightRebar":
                right_rebars_hook_orientation_list.append("")
            else:
                right_rebars_hook_orientation_list.append("Front Inside")

    right_rebars_number = sum(
        x[0] for x in right_rebars_number_diameter_offset_tuple
    )
    right_reinforcement_span_length = (
        right_rebars_number - 1
    ) * right_rebars_spacing + sum(
        x[0] * x[1] for x in right_rebars_number_diameter_offset_tuple
    )
    right_rebars_f_cover = (face_width - right_reinforcement_span_length) / 2

    right_reinforcement_rebars = []
    for i, (number, diameter, offset) in enumerate(
        right_rebars_number_diameter_offset_tuple
    ):
        b_cover = r_cover_of_stirrup + dia_of_stirrup
        r_cover = l_cover = offset
        rear_cover = (
            face_width
            - right_rebars_f_cover
            - number * diameter
            - (number - 1) * right_rebars_spacing
        )
        if right_rebars_type_list[i] == "StraightRebar":
            if face.normalAt(0, 0).x in (1, -1):
                orientation = "Horizontal"
                coverAlong = "Bottom Side"
            else:
                orientation = "Vertical"
                coverAlong = "Right Side"
            right_reinforcement_rebars.append(
                makeStraightRebar(
                    right_rebars_f_cover,
                    (coverAlong, b_cover),
                    r_cover,
                    l_cover,
                    diameter,
                    True,
                    number,
                    orientation,
                    structure,
                    facename_for_s_rebars,
                )
            )
        else:
            t_cover = face_length - b_cover - diameter / 2
            if right_rebars_hook_orientation_list[i] in (
                "Front Inside",
                "Rear Inside",
            ):
                t_cover -= (
                    right_l_rebar_rounding_list[i] * diameter
                    + right_rebars_hook_extension_list[i]
                )
                if right_rebars_hook_orientation_list[i] == "Front Inside":
                    if face.normalAt(0, 0).x in (1, -1):
                        orientation = "Bottom Right"
                    else:
                        orientation = "Top Right"
                else:
                    if face.normalAt(0, 0).x in (1, -1):
                        orientation = "Bottom Left"
                    else:
                        orientation = "Bottom Right"
            else:
                t_cover += (
                    right_l_rebar_rounding_list[i] * diameter
                    + right_rebars_hook_extension_list[i]
                )
                if right_rebars_hook_orientation_list[i] == "Front Outside":
                    if face.normalAt(0, 0).x in (1, -1):
                        orientation = "Bottom Right"
                    else:
                        orientation = "Top Right"
                else:
                    if face.normalAt(0, 0).x in (1, -1):
                        orientation = "Bottom Left"
                    else:
                        orientation = "Bottom Right"

            if face.normalAt(0, 0).y in (1, -1):
                l_cover = t_cover
                r_cover = b_cover
                t_cover = b_cover = offset

            right_reinforcement_rebars.append(
                makeLShapeRebar(
                    right_rebars_f_cover,
                    b_cover,
                    l_cover,
                    r_cover,
                    diameter,
                    t_cover,
                    right_l_rebar_rounding_list[i],
                    True,
                    number,
                    orientation,
                    structure,
                    facename_for_s_rebars,
                )
            )
        right_reinforcement_rebars[-1].OffsetEnd = rear_cover + diameter / 2
        right_rebars_f_cover += (
            number * diameter + number * right_rebars_spacing
        )
    FreeCAD.ActiveDocument.recompute()

    obj.addRightRebars(right_reinforcement_rebars)
    properties_values = []
    properties_values.append(
        ("NumberDiameterOffset", right_rebars_number_diameter_offset)
    )
    properties_values.append(("RebarType", right_rebars_type_list))
    properties_values.append(("RebarSpacing", right_rebars_spacing))
    properties_values.append(
        ("HookExtension", right_rebars_hook_extension_list)
    )
    properties_values.append(
        ("HookOrientation", right_rebars_hook_orientation_list)
    )
    obj.setPropertiesValues(properties_values, obj.right_rebars_group)

    return right_reinforcement_rebars


def editReinforcement(
    rebar_group,
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
    top_reinforcement_l_rebar_rounding=2,
    top_reinforcement_hook_extension=40,
    top_reinforcement_hook_orientation="Front Inside",
    bottom_reinforcement_l_rebar_rounding=2,
    bottom_reinforcement_hook_extension=40,
    bottom_reinforcement_hook_orientation="Front Inside",
    left_l_rebar_rounding=2,
    left_rebars_hook_extension=40,
    left_rebars_hook_orientation="Front Inside",
    right_l_rebar_rounding=2,
    right_rebars_hook_extension=40,
    right_rebars_hook_orientation="Front Inside",
    structure=None,
    facename=None,
):
    """editReinforcement(RebarGroup, LeftCoverOfStirrup, RightCoverOfStirrup,
    TopCoverOfStirrup, BottomCoverOfStirrup, OffsetofStirrup, BentAngle,
    ExtensionFactor, DiameterOfStirrup, NumberSpacingCheck, NumberSpacingValue,
    TopReinforcementNumberDiameterOffset, TopReinforcementRebarType,
    TopReinforcementLayerSpacing, BottomReinforcementNumberDiameterOffset,
    BottomReinforcementRebarType, BottomReinforcementLayerSpacing,
    LeftRebarsNumberDiameterOffset, LeftRebarsType, LeftRebarsSpacing,
    RightRebarsNumberDiameterOffset, RightRebarsType, RightRebarsSpacing,
    TopReinforcementLRebarRounding, TopReinforcementHookLength,
    TopReinforcementHookOrientation, BottomReinforcementLRebarRounding,
    BottomReinforcementHookLength, BottomReinforcementHookOrientation,
    LeftLRebarRounding, LeftRebarsHookLength, LeftRebarsHookOrientation,
    RightLRebarRounding, RightRebarsHookLength, RightRebarsHookOrientation,
    Structure, Facename):

    Edit the Two Legged Stirrup reinforcement for the selected structural beam
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
    bottom_reinforcement_hook_orientation, top_reinforcement_hook_extension,
    bottom_reinforcement_hook_extension, top_reinforcement_l_rebar_rounding and
    bottom_reinforcement_l_rebar_rounding can be similar to as discussed above
    for top_reinforcement_rebar_type.

    left_rebars_number_diameter_offset and right_rebars_number_diameter_offset
    are string of number_diameter_offset.
    Syntax: "number1#diameter1@offset1+number2#diameter2@offset2+..."

    Possible values for left_rebars_type and right_rebars_type:
    1. 'StraightRebar' or 'LShapeRebar'
    2. ('<rebar_type>', '<rebar_type>', ...) and each element of tuple
    represents rabar_type for each set of rebars.

    Possible values for left_l_rebar_rounding, right_l_rebar_rounding
    left_rebars_hook_extension, right_rebars_hook_extension,
    left_rebars_hook_orientation and right_rebars_hook_orientation can be
    similar to as discussed above for left_rebars_type.

    left_rebars_spacing/right_rebars_spacing is clear spacing between left/right
    rebars.
    """
    if len(rebar_group.ReinforcementGroups) == 0:
        return rebar_group
    for i, tmp_rebar_group in enumerate(rebar_group.ReinforcementGroups):
        if hasattr(tmp_rebar_group, "Stirrups"):
            if len(tmp_rebar_group.Stirrups) > 0:
                Stirrup = tmp_rebar_group.Stirrups[0]
                break
            else:
                showWarning(
                    "You have deleted stirrups. Please recreate the "
                    "BeamReinforcement."
                )
                return rebar_group
        elif i == len(rebar_group.ReinforcementGroups) - 1:
            showWarning(
                "You have deleted stirrups group. Please recreate the "
                "BeamReinforcement."
            )
            return rebar_group

    if not structure and not facename:
        structure = Stirrup.Base.Support[0][0]
        facename = Stirrup.Base.Support[0][1][0]

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
    stirrup = editStirrup(
        Stirrup,
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
    return rebar_group


class _TwoLeggedBeam(_BeamReinforcementGroup):
    "A TwoLeggedBeam group object."

    def __init__(self):
        """Create Group object and add properties to it."""
        _BeamReinforcementGroup.__init__(self)
        # Add properties to top/bottom reinforcement rebar groups
        properties = []
        properties.append(
            (
                "App::PropertyStringList",
                "NumberDiameterOffset",
                "List of Number Diameter Offset string",
                1,
            )
        )
        properties.append(
            (
                "App::PropertyString",
                "RebarType",
                "String representation of list of tuples of type of rebars",
                1,
            )
        )
        properties.append(
            (
                "App::PropertyFloatList",
                "LayerSpacing",
                "List of spacing between adjacent reinforcement layers",
                1,
            )
        )
        properties.append(
            (
                "App::PropertyString",
                "HookExtension",
                "String representation of list of tuples of hook extension",
                1,
            )
        )
        properties.append(
            (
                "App::PropertyString",
                "HookOrientation",
                "String representation of list of tuples of hook orientation",
                1,
            )
        )
        self.setProperties(properties, self.top_reinforcement_group)
        self.setProperties(properties, self.bottom_reinforcement_group)
        # Add properties to left/right rebar groups
        properties = []
        properties.append(
            (
                "App::PropertyString",
                "NumberDiameterOffset",
                "Number Diameter Offset string",
                1,
            )
        )
        properties.append(
            (
                "App::PropertyStringList",
                "RebarType",
                "List of type of rebars",
                1,
            )
        )
        properties.append(
            (
                "App::PropertyDistance",
                "RebarSpacing",
                "Clear spacing between rebars",
                1,
            )
        )
        properties.append(
            (
                "App::PropertyFloatList",
                "HookExtension",
                "List of hook extension of lshape rebars",
                1,
            )
        )
        properties.append(
            (
                "App::PropertyStringList",
                "HookOrientation",
                "List of hook orientation of lshape rebars",
                1,
            )
        )
        self.setProperties(properties, self.left_rebars_group)
        self.setProperties(properties, self.right_rebars_group)
