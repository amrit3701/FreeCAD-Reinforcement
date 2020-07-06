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

__title__ = "Bill Of Material Helper Functions"
__author__ = "Suraj"
__url__ = "https://www.freecadweb.org"


from PySide2 import QtGui

import FreeCAD
import Draft


def getReinforcementRebarObjects(objects_list=None):
    """getReinforcementRebarObjects(ObjectsList):
    objects_list is the list of ArchRebar, rebar2 and/or structural objects.

    Returns list of ArchRebar objects that belongs to passed structural elements
    and reinforcement objects that are derived from passed base rebar2 objects,
    if objects_list is provided. Otherwise returns list of ArchRebar and
    reinforcement objects from active document.
    """
    if not objects_list:
        # Get all objects in active document
        objects_list = FreeCAD.ActiveDocument.Objects

    # Get ArchRebar objects
    rebars_list = Draft.get_objects_of_type(objects_list, "Rebar")

    # Add all ArchRebar objects present in active document having host present
    # in objects_list
    if objects_list != FreeCAD.ActiveDocument.Objects:
        all_arch_rebar_objects = Draft.get_objects_of_type(
            FreeCAD.ActiveDocument.Objects, "Rebar"
        )
        for arch_rebar_object in all_arch_rebar_objects:
            if (
                arch_rebar_object.Host in objects_list
                and arch_rebar_object not in rebars_list
            ):
                rebars_list.append(arch_rebar_object)

    # Get Rebar2 objects
    reinforcement_list = Draft.get_objects_of_type(
        objects_list, "ReinforcementGeneric"
    )
    reinforcement_list.extend(
        Draft.get_objects_of_type(objects_list, "ReinforcementLattice")
    )
    reinforcement_list.extend(
        Draft.get_objects_of_type(objects_list, "ReinforcementCustom")
    )
    reinforcement_list.extend(
        Draft.get_objects_of_type(objects_list, "ReinforcementIndividual")
    )
    reinforcement_list.extend(
        Draft.get_objects_of_type(objects_list, "ReinforcementLinear")
    )

    # Add all reinforcement elements present in active document derived from
    # base rebar objects in objects_list
    base_rebar_objects = Draft.get_objects_of_type(objects_list, "RebarShape")
    if objects_list != FreeCAD.ActiveDocument.Objects and base_rebar_objects:
        all_objects = FreeCAD.ActiveDocument.Objects
        all_reinforcement_obj = Draft.get_objects_of_type(
            all_objects, "ReinforcementGeneric"
        )
        all_reinforcement_obj.extend(
            Draft.get_objects_of_type(all_objects, "ReinforcementLattice")
        )
        all_reinforcement_obj.extend(
            Draft.get_objects_of_type(all_objects, "ReinforcementCustom")
        )
        all_reinforcement_obj.extend(
            Draft.get_objects_of_type(all_objects, "ReinforcementIndividual")
        )
        all_reinforcement_obj.extend(
            Draft.get_objects_of_type(all_objects, "ReinforcementLinear")
        )
        for reinforcement in all_reinforcement_obj:
            if (
                reinforcement.BaseRebar in base_rebar_objects
                and reinforcement not in reinforcement_list
            ):
                reinforcement_list.append(reinforcement)

    rebars_list.extend(reinforcement_list)
    return rebars_list


def getMarkReinforcementsDict(objects_list=None):
    """getMarkReinforcementsDict(ObjectsList):
    objects_list is the list of ArchRebar, rebar2 and/or structural objects.

    Returns dictionary with mark as key and corresponding reinforcement objects
    list as value from active document."""
    rebar_objects = getReinforcementRebarObjects(objects_list)

    # Create dictionary with mark number as key with corresponding reinforcement
    # objects list as value
    mark_reinforcements_dict = {}

    for rebar in rebar_objects:
        # If object is ArchRebar object
        if Draft.get_type(rebar) == "Rebar":
            if hasattr(rebar, "MarkNumber"):
                if rebar.MarkNumber:
                    mark = rebar.MarkNumber
                else:
                    mark = "D{}L{}".format(
                        round(rebar.Diameter.Value), round(rebar.Length.Value)
                    )
            else:
                mark = "D{}L{}".format(
                    round(rebar.Diameter.Value), round(rebar.Length.Value)
                )

            if mark not in mark_reinforcements_dict:
                mark_reinforcements_dict[mark] = []
            mark_reinforcements_dict[mark].append(rebar)
        # Otherwise object is Rebar2 reinforcement object
        else:
            if rebar.BaseRebar.MarkNumber not in mark_reinforcements_dict:
                mark_reinforcements_dict[rebar.BaseRebar.MarkNumber] = []
            mark_reinforcements_dict[rebar.BaseRebar.MarkNumber].append(rebar)

    return mark_reinforcements_dict


def getUniqueDiameterList(mark_reinforcements_dict):
    """getUniqueDiameterList(MarkReinforcementDict):
    mark_reinforcements_dict is a dictionary with mark as key and corresponding
    reinforcement objects list as value.

    Returns list of unique diameters of reinforcement objects.
    """
    diameter_list = []
    for _, reinforcement_list in mark_reinforcements_dict.items():
        if hasattr(reinforcement_list[0], "BaseRebar"):
            diameter = reinforcement_list[0].BaseRebar.Diameter
            if diameter not in diameter_list:
                diameter_list.append(diameter)
        elif hasattr(reinforcement_list[0], "Diameter"):
            for rebar in reinforcement_list:
                diameter = rebar.Diameter
                if diameter not in diameter_list:
                    diameter_list.append(diameter)
    diameter_list.sort()
    return diameter_list


def getRebarSharpEdgedLength(rebar):
    """getRebarSharpEdgedLength(Rebar):
    Returns sharp edged length of rebar object.
    """
    base = rebar.Base
    # When rebar is drived from DWire
    if hasattr(base, "Length"):
        # When wire shape is created using DraftGeomUtils.filletWire()
        if not hasattr(base, "FilletRadius"):
            return base.Length
        # If FilletRadius of DWire is zero
        elif not base.FilletRadius:
            return base.Length
        else:
            edges = base.Shape.Edges
            if base.Closed:
                corners = len(edges) / 2
            else:
                corners = (len(edges) - 1) / 2
            extension_length = 2 * corners * base.FilletRadius
            rebar_straight_length = 0
            for edge in edges[::2]:
                rebar_straight_length += edge.Length
            rebar_sharp_edged_length = (
                FreeCAD.Units.Quantity(str(rebar_straight_length) + "mm")
                + extension_length
            )
            return rebar_sharp_edged_length
    # When rebar is drived from Sketch
    elif base.isDerivedFrom("Sketcher::SketchObject"):
        rebar_length = 0
        for geo in base.Geometry:
            rebar_length += geo.length()
        return FreeCAD.Units.Quantity(str(rebar_length) + "mm")
    else:
        FreeCAD.Console.PrintError(
            "Cannot calculate rebar length from its base object\n"
        )
        return FreeCAD.Units.Quantity("0 mm")


def getStringWidth(
    input_string,
    font_size,
    font_family="DejaVu Sans",
    font_file="DejaVuSans.ttf",
):
    """getStringWidth(InputString, FontSize, FontFamily):
    font_size is size of font in mm.
    font_file is required where no X11 display is available, in pure console
    mode.

    Returns width of string in mm.
    """
    # Convert font size from mm to points
    font_size = 2.8346456693 * font_size

    if FreeCAD.GuiUp:
        font = QtGui.QFont(font_family, font_size)
        font_metrics = QtGui.QFontMetrics(font)
        width = font_metrics.boundingRect(input_string).width()
        # Convert width from pixels to mm
        width = 0.2645833333 * width
    else:
        try:
            from PIL import ImageFont
        except ModuleNotFoundError as error:
            FreeCAD.Console.PrintError(
                "Module {} not found. It is required to calculate string width "
                "in console mode.\n".format(error.name)
            )
            return len(input_string) * font_size / 2.8346456693

        try:
            font = ImageFont.truetype(font_file, round(font_size))
        except OSError:
            FreeCAD.Console.PrintError(
                "Unable to find/open Font file `{}`. Default font `better than "
                "nothing` will be used from PIL library.\n".format(font_file)
            )
            font = ImageFont.load_default()

        width = font.getsize(input_string, stroke_width=0.35)[0]
        # Convert width from points to mm
        width = width / 2.8346456693
    return width
