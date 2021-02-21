# -*- coding: utf-8 -*-
# ***************************************************************************
# *                                                                         *
# *   Copyright (c) 2017 - Amritpal Singh <amrit3701@gmail.com>             *
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

__title__ = "HelicalRebar"
__author__ = "Amritpal Singh"
__url__ = "https://www.freecadweb.org"

import math
from pathlib import Path

import ArchCommands
import FreeCAD
import FreeCADGui
from DraftTools import translate
from PySide import QtGui
from PySide.QtCore import QT_TRANSLATE_NOOP

from PopUpImage import showPopUpImageDialog
from RebarData import RebarTypes
from Rebarfunc import (
    getSelectedFace,
    getFaceNumber,
    getParametersOfFace,
    showWarning,
    check_selected_face,
    facenormalDirection,
)


def getpointsOfHelicalRebar(
    FacePRM, s_cover, b_cover, t_cover, pitch, edges, diameter, size, direction
):
    """getpointsOfHelicalRebar(FacePRM, s_cover, b_cover, t_cover):
    Return points of the LShape rebar in the form of array for sketch."""
    dz = float(pitch) / edges
    R = FacePRM[0][0] / 2 - s_cover
    points = []
    if direction[2] in {-1, 1}:
        z = 0
        if direction[2] == 1:
            zz = FacePRM[1][2] - t_cover
        elif direction[2] == -1:
            zz = FacePRM[1][2] + b_cover
        count = 0
        flag = False
        while round(z) < abs(size - b_cover - t_cover):
            for i in range(0, int(edges) + 1):
                if not i and flag:
                    continue
                if not flag:
                    z -= dz
                    flag = True
                iAngle = i * 360 / edges
                x = FacePRM[1][0] + R * math.cos(math.radians(iAngle))
                y = FacePRM[1][1] + R * math.sin(math.radians(iAngle))
                points.append(FreeCAD.Vector(x, y, zz))
                count += 1
                if direction[2] == 1:
                    zz -= dz
                elif direction[2] == -1:
                    zz += dz
                z += dz
    return points


def createHelicalWire(
    FacePRM,
    s_cover,
    b_cover,
    t_cover,
    pitch,
    size,
    direction,
    diameter,
    helix=None,
):
    """createHelicalWire(FacePRM, SideCover, BottomCover, TopCover, Pitch,
    Size, Direction, Diameter, Helix = None):
    It creates a helical wire."""
    b_cover += diameter / 2
    t_cover += diameter / 2
    s_cover += diameter / 2

    if not helix:
        helix = FreeCAD.ActiveDocument.addObject("Part::Helix", "Helix")
    helix.Pitch = pitch
    helix.Radius = FacePRM[0][0] / 2 - s_cover
    helix.Angle = 0
    helix.LocalCoord = 0
    helix.Height = size - b_cover - t_cover
    if round(direction.x) == 1:
        helix.Placement.Base = FreeCAD.Vector(
            FacePRM[1][0] - b_cover, FacePRM[1][1], FacePRM[1][2]
        )
        helix.Placement.Rotation = FreeCAD.Rotation(
            FreeCAD.Vector(0, -1, 0), 90
        )
    elif round(direction.x) == -1:
        helix.Placement.Base = FreeCAD.Vector(
            FacePRM[1][0] + t_cover, FacePRM[1][1], FacePRM[1][2]
        )
        helix.Placement.Rotation = FreeCAD.Rotation(
            FreeCAD.Vector(0, -1, 0), -90
        )
    elif round(direction.y) == 1:
        helix.Placement.Base = FreeCAD.Vector(
            FacePRM[1][0], FacePRM[1][1] - b_cover, FacePRM[1][2]
        )
        helix.Placement.Rotation = FreeCAD.Rotation(FreeCAD.Vector(1, 0, 0), 90)
    elif round(direction.y) == -1:
        helix.Placement.Base = FreeCAD.Vector(
            FacePRM[1][0], FacePRM[1][1] + t_cover, FacePRM[1][2]
        )
        helix.Placement.Rotation = FreeCAD.Rotation(
            FreeCAD.Vector(-1, 0, 0), 90
        )
    elif round(direction.z) == 1:
        helix.Placement.Base = FreeCAD.Vector(
            FacePRM[1][0], FacePRM[1][1], FacePRM[1][2] - size + b_cover
        )
        helix.Placement.Rotation = FreeCAD.Rotation(FreeCAD.Vector(0, 0, 1), 0)
    elif round(direction.z) == -1:
        helix.Placement.Base = FreeCAD.Vector(
            FacePRM[1][0], FacePRM[1][1], FacePRM[1][2] + b_cover
        )
        helix.Placement.Rotation = FreeCAD.Rotation(FreeCAD.Vector(0, 0, -1), 0)
    FreeCAD.ActiveDocument.recompute()
    return helix


class _HelicalRebarTaskPanel:
    def __init__(self, Rebar=None):
        self.form = FreeCADGui.PySideUic.loadUi(
            str(Path(__file__).with_suffix(".ui"))
        )
        self.form.setWindowTitle(
            QtGui.QApplication.translate("Arch", "Helical Rebar", None)
        )
        if not Rebar:
            normal = facenormalDirection()
        else:
            normal = facenormalDirection(
                Rebar.Base.Support[0][0], Rebar.Base.Support[0][1][0]
            )
        if not round(normal.z) in {1, -1}:
            self.form.topCoverLabel.setText(
                translate("RebarAddon", "Left Cover")
            )
            self.form.bottomCoverLabel.setText(
                translate("RebarAddon", "Right Cover")
            )
        self.form.PickSelectedFace.clicked.connect(self.getSelectedFace)
        self.form.image.setPixmap(
            QtGui.QPixmap(
                str(Path(__file__).parent / "icons" / "HelicalRebar.svg")
            )
        )
        self.form.toolButton.clicked.connect(
            lambda: showPopUpImageDialog(
                str(
                    Path(__file__).parent / "icons" / "HelicalRebarDetailed.svg"
                )
            )
        )
        # self.form.toolButton.setIcon(
        #     self.form.toolButton.style().standardIcon(
        #         QtGui.QStyle.SP_DialogHelpButton
        #     )
        # )
        self.Rebar = Rebar
        self.SelectedObj = None
        self.FaceName = None

    @staticmethod
    def getStandardButtons():
        return (
            int(QtGui.QDialogButtonBox.Ok)
            | int(QtGui.QDialogButtonBox.Apply)
            | int(QtGui.QDialogButtonBox.Cancel)
        )

    def clicked(self, button):
        if button == int(QtGui.QDialogButtonBox.Apply):
            self.accept(button)

    def getSelectedFace(self):
        getSelectedFace(self)
        normal = facenormalDirection()
        if not round(normal.z) in {1, -1}:
            self.form.topCoverLabel.setText(
                translate("RebarAddon", "Left Cover")
            )
            self.form.bottomCoverLabel.setText(
                translate("RebarAddon", "Right Cover")
            )
        else:
            self.form.topCoverLabel.setText(
                translate("RebarAddon", "Top Cover")
            )
            self.form.bottomCoverLabel.setText(
                translate("RebarAddon", "Bottom Cover")
            )

    def accept(self, signal=None):
        b_cover = self.form.bottomCover.text()
        b_cover = FreeCAD.Units.Quantity(b_cover).Value
        s_cover = self.form.sideCover.text()
        s_cover = FreeCAD.Units.Quantity(s_cover).Value
        t_cover = self.form.topCover.text()
        t_cover = FreeCAD.Units.Quantity(t_cover).Value
        pitch = self.form.pitch.text()
        pitch = FreeCAD.Units.Quantity(pitch).Value
        diameter = self.form.diameter.text()
        diameter = FreeCAD.Units.Quantity(diameter).Value
        if not self.Rebar:
            rebar = makeHelicalRebar(
                s_cover,
                b_cover,
                diameter,
                t_cover,
                pitch,
                self.SelectedObj,
                self.FaceName,
            )
        else:
            rebar = editHelicalRebar(
                self.Rebar,
                s_cover,
                b_cover,
                diameter,
                t_cover,
                pitch,
                self.SelectedObj,
                self.FaceName,
            )
        self.Rebar = rebar
        if signal == int(QtGui.QDialogButtonBox.Apply):
            pass
        else:
            FreeCADGui.Control.closeDialog()


def makeHelicalRebar(
    s_cover, b_cover, diameter, t_cover, pitch, structure=None, facename=None
):
    """makeHelicalRebar(SideCover, BottomCover, Diameter, TopCover, Pitch,
    Structure, Facename):
    Adds the Helical reinforcement bar to the selected structural object."""
    if not structure and not facename:
        selected_obj = FreeCADGui.Selection.getSelectionEx()[0]
        structure = selected_obj.Object
        facename = selected_obj.SubElementNames[0]
    face = structure.Shape.Faces[getFaceNumber(facename) - 1]
    # StructurePRM = getTrueParametersOfStructure(structure)
    FacePRM = getParametersOfFace(structure, facename, False)
    if not FacePRM:
        FreeCAD.Console.PrintError(
            "Cannot identified shape or from which base object structural "
            "element is derived\n"
        )
        return
    size = (
        ArchCommands.projectToVector(
            structure.Shape.copy(), face.normalAt(0, 0)
        )
    ).Length
    normal = face.normalAt(0, 0)
    # normal = face.Placement.Rotation.inverted().multVec(normal)
    import Arch

    helix = createHelicalWire(
        FacePRM, s_cover, b_cover, t_cover, pitch, size, normal, diameter
    )
    helix.Support = [(structure, facename)]
    rebar = Arch.makeRebar(
        structure, helix, diameter, 1, diameter / 2, name="HelicalRebar"
    )
    rebar.OffsetStart = diameter / 2
    rebar.OffsetEnd = diameter / 2
    FreeCAD.ActiveDocument.recompute()
    # Adds properties to the rebar object
    rebar.addProperty(
        "App::PropertyEnumeration",
        "RebarShape",
        "RebarDialog",
        QT_TRANSLATE_NOOP("App::Property", "Shape of rebar"),
    ).RebarShape = RebarTypes.tolist()
    rebar.RebarShape = "HelicalRebar"
    rebar.setEditorMode("RebarShape", 2)
    rebar.addProperty(
        "App::PropertyDistance",
        "SideCover",
        "RebarDialog",
        QT_TRANSLATE_NOOP("App::Property", "Front cover of rebar"),
    ).SideCover = s_cover
    rebar.setEditorMode("SideCover", 2)
    rebar.addProperty(
        "App::PropertyDistance",
        "Pitch",
        "RebarDialog",
        QT_TRANSLATE_NOOP("App::Property", "Left Side cover of rebar"),
    ).Pitch = pitch
    rebar.setEditorMode("Pitch", 2)
    rebar.addProperty(
        "App::PropertyDistance",
        "BottomCover",
        "RebarDialog",
        QT_TRANSLATE_NOOP("App::Property", "Bottom cover of rebar"),
    ).BottomCover = b_cover
    rebar.setEditorMode("BottomCover", 2)
    rebar.addProperty(
        "App::PropertyDistance",
        "TopCover",
        "RebarDialog",
        QT_TRANSLATE_NOOP("App::Property", "Top cover of rebar"),
    ).TopCover = t_cover
    rebar.setEditorMode("TopCover", 2)
    FreeCAD.ActiveDocument.recompute()
    return rebar


def editHelicalRebar(
    Rebar,
    s_cover,
    b_cover,
    diameter,
    t_cover,
    pitch,
    structure=None,
    facename=None,
):
    sketch = Rebar.Base
    if structure and facename:
        sketch.Support = [(structure, facename)]
    # Check if sketch support is empty.
    if not sketch.Support:
        showWarning(
            "You have checked: 'Remove external geometry of base sketches when "
            "needed.'\nTo uncheck: Edit->Preferences->Arch."
        )
        return
    # Assigned values
    facename = sketch.Support[0][1][0]
    structure = sketch.Support[0][0]
    face = structure.Shape.Faces[getFaceNumber(facename) - 1]
    # StructurePRM = getTrueParametersOfStructure(structure)
    # Get parameters of the face where sketch of rebar is drawn
    FacePRM = getParametersOfFace(structure, facename, False)
    size = (
        ArchCommands.projectToVector(
            structure.Shape.copy(), face.normalAt(0, 0)
        )
    ).Length
    normal = face.normalAt(0, 0)
    # normal = face.Placement.Rotation.inverted().multVec(normal)
    createHelicalWire(
        FacePRM,
        s_cover,
        b_cover,
        t_cover,
        pitch,
        size,
        normal,
        diameter,
        Rebar.Base,
    )
    FreeCAD.ActiveDocument.recompute()
    Rebar.Diameter = diameter
    Rebar.SideCover = s_cover
    Rebar.BottomCover = b_cover
    Rebar.TopCover = t_cover
    Rebar.Pitch = pitch
    FreeCAD.ActiveDocument.recompute()
    return Rebar


def editDialog(vobj):
    FreeCADGui.Control.closeDialog()
    obj = _HelicalRebarTaskPanel(vobj.Object)
    obj.form.sideCover.setText(str(vobj.Object.SideCover))
    obj.form.bottomCover.setText(str(vobj.Object.BottomCover))
    obj.form.diameter.setText(str(vobj.Object.Diameter))
    obj.form.topCover.setText(str(vobj.Object.TopCover))
    obj.form.pitch.setText(str(vobj.Object.Pitch))
    FreeCADGui.Control.showDialog(obj)


def CommandHelicalRebar():
    selected_obj = check_selected_face()
    if selected_obj:
        FreeCADGui.Control.showDialog(_HelicalRebarTaskPanel())
