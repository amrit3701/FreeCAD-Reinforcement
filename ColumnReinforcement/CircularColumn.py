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

__title__ = "Circular Column Reinforcement"
__author__ = "Suraj"
__url__ = "https://www.freecadweb.org"


import math
from PySide.QtCore import QT_TRANSLATE_NOOP

import FreeCAD
import ArchCommands

from HelicalRebar import makeHelicalRebar
from Rebarfunc import getFaceNumber, getParametersOfFace

if FreeCAD.GuiUp:
    import FreeCADGui


def getPointsOfStraightRebars(
    FacePRM,
    s_cover,
    t_offset,
    b_offset,
    column_size,
    dia_of_helical_rebar,
    dia_of_main_rebars,
    number_angle_check,
    number_angle_value,
):
    if number_angle_check:
        angle = 360.0 / number_angle_value
    else:
        angle = number_angle_value
    radius = (
        FacePRM[0][0] / 2
        - s_cover
        - dia_of_helical_rebar
        - dia_of_main_rebars / 2
    )
    points_of_centre = FacePRM[1]
    u_point = (
        points_of_centre[0] + radius,
        points_of_centre[1],
        points_of_centre[2] - t_offset,
    )
    b_point = (
        points_of_centre[0] + radius,
        points_of_centre[1],
        points_of_centre[2] - column_size + b_offset,
    )
    points_list = [[FreeCAD.Vector(u_point), FreeCAD.Vector(b_point)]]
    tmp_angle = angle
    while tmp_angle < 360:
        u_point = (
            points_of_centre[0] + radius * math.cos(math.radians(tmp_angle)),
            points_of_centre[1] + radius * math.sin(math.radians(tmp_angle)),
            points_of_centre[2] - t_offset,
        )
        b_point = (
            points_of_centre[0] + radius * math.cos(math.radians(tmp_angle)),
            points_of_centre[1] + radius * math.sin(math.radians(tmp_angle)),
            points_of_centre[2] - column_size + b_offset,
        )
        points_list.append([FreeCAD.Vector(u_point), FreeCAD.Vector(b_point)])
        tmp_angle += angle
    return points_list


def makeReinforcement(
    s_cover,
    helical_rebar_t_offset,
    helical_rebar_b_offset,
    pitch,
    dia_of_helical_rebar,
    main_rebars_t_offset,
    main_rebars_b_offset,
    dia_of_main_rebars,
    number_angle_check,
    number_angle_value,
    structure=None,
    facename=None,
):
    """makeReinforcement(SideCover, TopOffsetOfHelicalRebars,
    BottomOffsetOfHelicalRebars, Pitch, DiameterOfHelicalRebar,
    TopOffsetOfMainRebars, BottomOffsetOfMainRebars, DiameterOfMainRebars,
    NumberAngleCheck, NumberAngleValue, Structure, Facename):
    Adds the helical and straight rebars to the selected structural column
    object.
    """
    if not structure and not facename:
        if FreeCAD.GuiUp:
            selected_obj = FreeCADGui.Selection.getSelectionEx()[0]
            structure = selected_obj.Object
            facename = selected_obj.SubElementNames[0]
        else:
            print("Error: Pass structure and facename arguments")
            return
    face = structure.Shape.Faces[(getFaceNumber(facename) - 1)]
    FacePRM = getParametersOfFace(structure, facename, False)
    if not FacePRM:
        FreeCAD.Console.PrintError(
            "Cannot identified shape or from which base object"
            "sturcturalelement is derived\n"
        )
        return
    helical_rebar = makeHelicalRebar(
        s_cover,
        helical_rebar_b_offset,
        dia_of_helical_rebar,
        helical_rebar_t_offset,
        pitch,
        structure,
        facename,
    )
    column_size = ArchCommands.projectToVector(
        structure.Shape.copy(), face.normalAt(0, 0)
    ).Length
    points_list = getPointsOfStraightRebars(
        FacePRM,
        s_cover,
        main_rebars_t_offset,
        main_rebars_b_offset,
        column_size,
        dia_of_helical_rebar,
        dia_of_main_rebars,
        number_angle_check,
        number_angle_value,
    )
    import Arch, Draft

    pl = FreeCAD.Placement()
    pl.Rotation.Q = (0.5, 0.5, 0.5, 0.5)
    main_rebars_list = []
    for points in points_list:
        line = Draft.makeWire(
            points, placement=pl, closed=False, face=True, support=None
        )
        main_rebars_list.append(
            Arch.makeRebar(structure, line, dia_of_main_rebars, 1)
        )
        main_rebars_list[-1].Label = "StraightRebar"

    CircularColumnReinforcementRebarGroup = (
        _CircularColumnReinforcementRebarGroup()
    )
    if FreeCAD.GuiUp:
        _ViewProviderCircularColumnReinforcementRebarGroup(
            CircularColumnReinforcementRebarGroup.Object.ViewObject
        )
    CircularColumnReinforcementRebarGroup.addHelicalRebars(helical_rebar)
    CircularColumnReinforcementRebarGroup.addMainRebars(main_rebars_list)

    properties_values = []
    properties_values.append(("TopOffset", main_rebars_t_offset))
    properties_values.append(("BottomOffset", main_rebars_b_offset))
    properties_values.append(("Diameter", dia_of_main_rebars))
    properties_values.append(("NumberAngleCheck", number_angle_check))
    if number_angle_check:
        properties_values.append(("Number", number_angle_value))
        properties_values.append(("Angle", 360.00 / number_angle_value))
    else:
        properties_values.append(
            ("Number", math.ceil(360 / number_angle_value))
        )
        properties_values.append(("Angle", number_angle_value))
    CircularColumnReinforcementRebarGroup.setPropertiesValues(
        properties_values,
        CircularColumnReinforcementRebarGroup.main_rebars_group,
    )
    FreeCAD.ActiveDocument.recompute()
    return CircularColumnReinforcementRebarGroup


class _CircularColumnReinforcementRebarGroup:
    def __init__(self):
        self.Type = "RebarGroup"
        self.rebar_group = FreeCAD.ActiveDocument.addObject(
            "App::DocumentObjectGroupPython", "ColumnReinforcement"
        )
        self.helical_rebar_group = self.rebar_group.newObject(
            "App::DocumentObjectGroupPython", "HelicalRebars"
        )
        self.main_rebars_group = self.rebar_group.newObject(
            "App::DocumentObjectGroupPython", "MainRebars"
        )

        # Add properties to rebar_group object
        properties = []
        properties.append(
            ("App::PropertyLinkList", "RebarGroups", "List of rebar groups", 1)
        )
        self.setProperties(properties, self.rebar_group)
        self.rebar_group.RebarGroups = [
            self.helical_rebar_group,
            self.main_rebars_group,
        ]

        # Add properties to helical_rebar_group object
        properties = []
        properties.append(
            (
                "App::PropertyLinkList",
                "HelicalRebars",
                "List of helical rebars",
                1,
            )
        )
        self.setProperties(properties, self.helical_rebar_group)

        # Add properties to main_rebars_group object
        properties = []
        properties.append(
            ("App::PropertyLinkList", "MainRebars", "List of main rebars", 1)
        )
        properties.append(
            (
                "App::PropertyDistance",
                "TopOffset",
                "Top offset of main rebars",
                1,
            )
        )
        properties.append(
            (
                "App::PropertyDistance",
                "BottomOffset",
                "Bottom offset of main rebars",
                1,
            )
        )
        properties.append(
            ("App::PropertyDistance", "Diameter", "Diameter of main rebars", 1)
        )
        properties.append(
            (
                "App::PropertyBool",
                "NumberAngleCheck",
                "Number radio button is checked",
                1,
            )
        )
        properties.append(
            ("App::PropertyQuantity", "Number", "Number of main rebars", 1)
        )
        properties.append(
            (
                "App::PropertyAngle",
                "Angle",
                "Angle between consecutive main rebars",
                1,
            )
        )
        self.setProperties(properties, self.main_rebars_group)

        self.Object = self.rebar_group

    def setProperties(self, properties, group_obj):
        for prop in properties:
            group_obj.addProperty(
                prop[0],
                prop[1],
                "RebarDialog",
                QT_TRANSLATE_NOOP("App::Property", prop[2]),
            )
            group_obj.setEditorMode(prop[1], prop[3])

    def setPropertiesValues(self, properties_values, group_obj):
        for prop in properties_values:
            setattr(group_obj, prop[0], prop[1])

    def addHelicalRebars(self, helical_rebars_list):
        """Add helical rebars to helical_rebar_group object."""
        if type(helical_rebars_list) == list:
            self.helical_rebar_group.addObjects(helical_rebars_list)
        else:
            self.helical_rebar_group.addObject(helical_rebars_list)
            helical_rebars_list = [helical_rebars_list]
        prev_helical_rebars_list = self.helical_rebar_group.HelicalRebars
        helical_rebars_list.extend(prev_helical_rebars_list)
        self.helical_rebar_group.HelicalRebars = helical_rebars_list

    def addMainRebars(self, main_rebars_list):
        """Add Main Rebars to main_rebars group object."""
        self.main_rebars_group.addObjects(main_rebars_list)
        prev_main_rebars_list = self.main_rebars_group.MainRebars
        main_rebars_list.extend(prev_main_rebars_list)
        self.main_rebars_group.MainRebars = main_rebars_list


class _ViewProviderCircularColumnReinforcementRebarGroup:
    def __init__(self, vobj):
        vobj.Proxy = self
        self.Object = vobj.Object

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None

    def doubleClicked(self, vobj):
        from ColumnReinforcement import MainColumnReinforcement

        MainColumnReinforcement.editDialog(vobj)
