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


from PySide2 import QtGui, QtWidgets

import FreeCAD


def getMarkReinforcementsDict():
    """Returns dictionary with mark as key and corresponding reinforcement
    objects list as value from active document."""
    # Get Part::FeaturePython objects list
    objects_list = FreeCAD.ActiveDocument.findObjects("Part::FeaturePython")

    # Create dictionary with mark number as key with corresponding reinforcement
    # objects list as value
    default_mark_number = 0
    mark_reinforcements_dict = {}
    for item in objects_list:
        if hasattr(item, "BaseRebar"):
            if hasattr(item.BaseRebar, "IfcType"):
                if item.BaseRebar.IfcType == "Reinforcing Bar":
                    if not hasattr(item.BaseRebar, "MarkNumber"):
                        mark_number = default_mark_number
                    else:
                        mark_number = item.BaseRebar.MarkNumber
                    if mark_number not in mark_reinforcements_dict:
                        mark_reinforcements_dict[mark_number] = []
                    mark_reinforcements_dict[mark_number].append(item)
    return mark_reinforcements_dict


def getUniqueDiameterList(mark_reinforcements_dict):
    """getUniqueDiameterList(MarkReinforcementDict):
    mark_reinforcements_dict is a dictionary with mark as key and corresponding
    reinforcement objects list as value.

    Returns list of unique diameters of reinforcement objects.
    """
    diameter_list = []
    for _, reinforcement_list in mark_reinforcements_dict.items():
        diameter = reinforcement_list[0].BaseRebar.Diameter
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


def getStringWidth(input_string, font_size, font_family):
    """getStringWidth(InputString, FontSize, FontFamily):
    font_size is size of font in mm.

    Known Issue
    -----------
    This function uses QtGui which makes the function can't be used in non-gui
    environment e.g. on server with no X11 display.

    Returns width of string in mm.
    """
    app = QtWidgets.QApplication.instance()
    if app is None:
        app = QtWidgets.QApplication()
    # Convert font size from mm to points
    font_size = 2.8346456693 * font_size
    font = QtGui.QFont(font_family, font_size)
    font_metrics = QtGui.QFontMetrics(font)
    width = font_metrics.boundingRect(input_string).width()
    # Convert width from pixels to mm
    width = 0.2645833333 * width
    return width
