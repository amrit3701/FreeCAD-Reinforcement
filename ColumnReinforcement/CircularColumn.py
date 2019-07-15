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
    dia_of_straight_rebars,
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
        - dia_of_straight_rebars / 2
    )
    points_of_centre = FacePRM[1]
    u_points = [
        (
            points_of_centre[0] + radius,
            points_of_centre[1],
            points_of_centre[2] - t_offset,
        )
    ]
    b_points = [
        (
            points_of_centre[0] + radius,
            points_of_centre[1],
            points_of_centre[2] - column_size + b_offset,
        )
    ]
    tmp_angle = angle
    while tmp_angle < 360:
        u_points.append(
            (
                points_of_centre[0]
                + radius * math.cos(math.radians(tmp_angle)),
                points_of_centre[1]
                + radius * math.sin(math.radians(tmp_angle)),
                points_of_centre[2] - t_offset,
            )
        )
        b_points.append(
            (
                points_of_centre[0]
                + radius * math.cos(math.radians(tmp_angle)),
                points_of_centre[1]
                + radius * math.sin(math.radians(tmp_angle)),
                points_of_centre[2] - column_size + b_offset,
            )
        )
        tmp_angle += angle
    return [u_points, b_points]


def makeReinforcement(
    s_cover,
    t_offset,
    b_offset,
    pitch,
    dia_of_helical_rebar,
    dia_of_straight_rebars,
    number_angle_check,
    number_angle_value,
    structure=None,
    facename=None,
):
    """makeReinforcement(SideCover, TopOffset, BottomOffset, Pitch,
    DiameterOfHelicalRebar, DiameterOfStraightRebars, NumberAngleCheck,
    NumberAngleValue, Structure, Facename):
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
                "Cannot identified shape or from which base object sturcturalelement is derived\n"
            )
            return
        makeHelicalRebar(
            s_cover,
            b_offset,
            dia_of_helical_rebar,
            t_offset,
            pitch,
            structure,
            facename,
        )
        column_size = ArchCommands.projectToVector(
            structure.Shape.copy(), face.normalAt(0, 0)
        ).Length
        u_points, b_points = getPointsOfStraightRebars(
            FacePRM,
            s_cover,
            t_offset,
            b_offset,
            column_size,
            dia_of_helical_rebar,
            dia_of_straight_rebars,
            number_angle_check,
            number_angle_value,
        )
        import Arch, Part

        for i, u_point in enumerate(u_points):
            sketch = FreeCAD.ActiveDocument.addObject(
                "Sketcher::SketchObject", "Sketch"
            )
            sketch.Support = [(structure, facename)]
            sketch.Placement = FreeCAD.Placement(
                FreeCAD.Vector(0, u_point[1], 0),
                FreeCAD.Rotation(FreeCAD.Vector(1, 0, 0), 90),
            )
            sketch.addGeometry(
                Part.LineSegment(
                    FreeCAD.Vector(u_point[0], u_point[2], 0),
                    FreeCAD.Vector(b_points[i][0], b_points[i][2], 0),
                ),
                False,
            )
            rebar = Arch.makeRebar(
                structure, sketch, dia_of_straight_rebars, 1
            )

        FreeCAD.ActiveDocument.recompute()
