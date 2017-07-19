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

__title__ = "StirrupRebar"
__author__ = "Amritpal Singh"
__url__ = "https://www.freecadweb.org"

from PySide import QtCore, QtGui
from Rebarfunc import *
from PySide.QtCore import QT_TRANSLATE_NOOP
from RebarDistribution import runRebarDistribution, removeRebarDistribution
import FreeCAD
import FreeCADGui
import ArchCommands
import os
import sys
import math

def getpointsOfStirrup(FacePRM, s_cover, bentAngle, bentFactor, diameter, rounding, facenormal):
    """ getpointsOfStirrup(FacePRM, s_cover, bentAngle, diameter, rounding, facenormal):
    Return the coordinates points of the Stirrup in the form of array."""
    angle = 180 - bentAngle
    tangent_part_length = extendedTangentPartLength(rounding, diameter, angle)
    tangent_length = extendedTangentLength(rounding, diameter, angle)
    if round(facenormal[0]) in {1,-1}:
        x1 = FacePRM[1][0]
        y1 = FacePRM[1][1] - FacePRM[0][0] / 2 + s_cover
        z1 = FacePRM[1][2] + FacePRM[0][1] / 2 - s_cover + tangent_part_length
        y2 = FacePRM[1][1] - FacePRM[0][0] / 2 + s_cover
        z2 = FacePRM[1][2] - FacePRM[0][1] / 2 + s_cover
        y3 = FacePRM[1][1] + FacePRM[0][0] / 2 - s_cover
        z3 = FacePRM[1][2] - FacePRM[0][1] / 2 + s_cover
        y4 = FacePRM[1][1] + FacePRM[0][0] / 2 - s_cover
        z4 = FacePRM[1][2] + FacePRM[0][1] / 2 - s_cover
        y5 = FacePRM[1][1] - FacePRM[0][0] / 2 + s_cover - tangent_part_length
        z5 = FacePRM[1][2] + FacePRM[0][1] / 2 - s_cover
        side_length = abs(y5 - y4) - tangent_part_length
        normal_dis = (diameter * (side_length + tangent_part_length)) / side_length
        x2 = x1 - normal_dis / 4
        x3 = x2 - normal_dis / 4
        x4 = x3 - normal_dis / 4
        x5 = x4 - normal_dis / 4
        x0 = x1 + normal_dis / 4
        y0 = y1 + (tangent_length + bentFactor * diameter) * math.sin(math.radians(angle))
        z0 = z1 - (tangent_length + bentFactor * diameter) * math.cos(math.radians(angle))
        x6 = x5 - normal_dis / 4
        y6 = y5 + (tangent_length + bentFactor * diameter) * math.sin(math.radians(90 - angle))
        z6 = z5 - (tangent_length + bentFactor * diameter) * math.cos(math.radians(90 - angle))
    elif round(facenormal[1]) in {1,-1}:
        x1 = FacePRM[1][0] - FacePRM[0][0] / 2 + s_cover
        y1 = FacePRM[1][1]
        z1 = FacePRM[1][2] + FacePRM[0][1] / 2 - s_cover + tangent_part_length
        x2 = FacePRM[1][0] - FacePRM[0][0] / 2 + s_cover
        z2 = FacePRM[1][2] - FacePRM[0][1] / 2 + s_cover
        x3 = FacePRM[1][0] + FacePRM[0][0] / 2 - s_cover
        z3 = FacePRM[1][2] - FacePRM[0][1] / 2 + s_cover
        x4 = FacePRM[1][0] + FacePRM[0][0] / 2 - s_cover
        z4 = FacePRM[1][2] + FacePRM[0][1] / 2 - s_cover
        x5 = FacePRM[1][0] - FacePRM[0][0] / 2 + s_cover - tangent_part_length
        z5 = FacePRM[1][2] + FacePRM[0][1] / 2 - s_cover
        side_length = abs(x5 - x4) - tangent_part_length
        normal_dis = (diameter * (side_length + tangent_part_length)) / side_length
        y2 = y1 - normal_dis / 4
        y3 = y2 - normal_dis / 4
        y4 = y3 - normal_dis / 4
        y5 = y4 - normal_dis / 4
        y0 = y1 + normal_dis / 4
        x0 = x1 + (tangent_length + bentFactor * diameter) * math.sin(math.radians(angle))
        z0 = z1 - (tangent_length + bentFactor * diameter) * math.cos(math.radians(angle))
        x6 = x5 + (tangent_length + bentFactor * diameter) * math.sin(math.radians(90 - angle))
        y6 = y5 - normal_dis / 4
        z6 = z5 - (tangent_length + bentFactor * diameter) * math.cos(math.radians(90 - angle))
    elif round(facenormal[2]) in {1,-1}:
        x1 = FacePRM[1][0] - FacePRM[0][0] / 2 + s_cover
        y1 = FacePRM[1][1] + FacePRM[0][1] / 2 - s_cover + tangent_part_length
        z1 = FacePRM[1][2]
        x2 = FacePRM[1][0] - FacePRM[0][0] / 2 + s_cover
        y2 = FacePRM[1][1] - FacePRM[0][1] / 2 + s_cover
        x3 = FacePRM[1][0] + FacePRM[0][0] / 2 - s_cover
        y3 = FacePRM[1][1] - FacePRM[0][1] / 2 + s_cover
        x4 = FacePRM[1][0] + FacePRM[0][0] / 2 - s_cover
        y4 = FacePRM[1][1] + FacePRM[0][1] / 2 - s_cover
        x5 = FacePRM[1][0] - FacePRM[0][0] / 2 + s_cover - tangent_part_length
        y5 = FacePRM[1][1] + FacePRM[0][1] / 2 - s_cover
        side_length = abs(x5 - x4) - tangent_part_length
        normal_dis = (diameter * (side_length + tangent_part_length)) / side_length
        z2 = z1 - normal_dis / 4
        z3 = z2 - normal_dis / 4
        z4 = z3 - normal_dis / 4
        z5 = z4 - normal_dis / 4
        z0 = z1 + normal_dis / 4
        x0 = x1 + (tangent_length + bentFactor * diameter) * math.sin(math.radians(angle))
        y0 = y1 - (tangent_length + bentFactor * diameter) * math.cos(math.radians(angle))
        x6 = x5 + (tangent_length + bentFactor * diameter) * math.sin(math.radians(90 - angle))
        y6 = y5 - (tangent_length + bentFactor * diameter) * math.cos(math.radians(90 - angle))
        z6 = z5 - normal_dis / 4
    return [FreeCAD.Vector(x0, y0, z0), FreeCAD.Vector(x1, y1, z1),\
            FreeCAD.Vector(x2, y2, z2), FreeCAD.Vector(x3, y3, z3),\
            FreeCAD.Vector(x4, y4, z4), FreeCAD.Vector(x5, y5, z5),\
            FreeCAD.Vector(x6, y6, z6)]

class _StirrupTaskPanel:
    def __init__(self, Rebar = None):
        self.form = FreeCADGui.PySideUic.loadUi(os.path.splitext(__file__)[0] + ".ui")
        self.form.setWindowTitle(QtGui.QApplication.translate("Arch", "Stirrup Rebar", None))
        self.form.bentAngle.addItems(["135", "90"])
        self.form.amount_radio.clicked.connect(self.amount_radio_clicked)
        self.form.spacing_radio.clicked.connect(self.spacing_radio_clicked)
        #self.form.image.setPixmap(QtGui.QPixmap(os.path.split(os.path.abspath(__file__))[0]+"/icons/UShapeRebar.svg"))
        self.form.customSpacing.clicked.connect(lambda: runRebarDistribution(Rebar))
        self.form.removeCustomSpacing.clicked.connect(lambda: removeRebarDistribution(Rebar))
        self.form.PickSelectedFace.clicked.connect(lambda: getSelectedFace(self))
        self.Rebar = Rebar
        self.SelectedObj = None
        self.FaceName = None

    def getStandardButtons(self):
        return int(QtGui.QDialogButtonBox.Ok) | int(QtGui.QDialogButtonBox.Cancel)

    def accept(self):
        s_cover = self.form.sideCover.text()
        s_cover = FreeCAD.Units.Quantity(s_cover).Value
        f_cover = self.form.frontCover.text()
        f_cover = FreeCAD.Units.Quantity(f_cover).Value
        diameter = self.form.diameter.text()
        diameter = FreeCAD.Units.Quantity(diameter).Value
        bentAngle = int(self.form.bentAngle.currentText())
        bentFactor = self.form.bentFactor.value()
        rounding = self.form.rounding.value()
        amount_check = self.form.amount_radio.isChecked()
        spacing_check = self.form.spacing_radio.isChecked()
        if not self.Rebar:
            if amount_check:
                amount = self.form.amount.value()
                makeStirrup(s_cover, f_cover, bentAngle, bentFactor, diameter,\
                    rounding, True, amount, self.SelectedObj, self.FaceName)
            elif spacing_check:
                spacing = self.form.spacing.text()
                spacing = FreeCAD.Units.Quantity(spacing).Value
                makeStirrup(s_cover, f_cover, bentAngle, bentFactor, diameter,\
                    rounding, False, spacing, self.SelectedObj, self.FaceName)
        else:
            if amount_check:
                amount = self.form.amount.value()
                editStirrup(self.Rebar, s_cover, f_cover, bentAngle, bentFactor,\
                    diameter, rounding, True, amount, self.SelectedObj, self.FaceName)
            elif spacing_check:
                spacing = self.form.spacing.text()
                spacing = FreeCAD.Units.Quantity(spacing).Value
                editStirrup(self.Rebar, s_cover, f_cover, bentAngle, bentFactor,\
                    diameter, rounding, False, spacing, self.SelectedObj, self.FaceName)
        FreeCADGui.Control.closeDialog(self)

    def amount_radio_clicked(self):
        self.form.spacing.setEnabled(False)
        self.form.amount.setEnabled(True)

    def spacing_radio_clicked(self):
        self.form.amount.setEnabled(False)
        self.form.spacing.setEnabled(True)


def makeStirrup(s_cover, f_cover, bentAngle, bentFactor, diameter, rounding,\
        amount_spacing_check, amount_spacing_value, structure = None, facename = None):
    """ makeStirrup(s_cover, f_cover, bentAngle, diameter, rounding,
    amount_spacing_check, amount_spacing_value): Adds the Stirrup reinforcement bar
    to the selected structural object."""
    if not structure and not facename:
        selected_obj = FreeCADGui.Selection.getSelectionEx()[0]
        structure = selected_obj.Object
        facename = selected_obj.SubElementNames[0]
    face = structure.Shape.Faces[getFaceNumber(facename) - 1]
    StructurePRM = getTrueParametersOfStructure(structure)
    FacePRM = getParametersOfFace(structure, facename, False)
    FaceNormal = face.normalAt(0,0)
    FaceNormal = face.Placement.Rotation.inverted().multVec(FaceNormal)
    if not FacePRM:
        FreeCAD.Console.PrintError("Cannot identified shape or from which base object sturctural element is derived\n")
        return
    # Calculate the coordinate values of Stirrup
    points = getpointsOfStirrup(FacePRM, s_cover, bentAngle, bentFactor, diameter, rounding, FaceNormal)
    import Draft
    line = Draft.makeWire(points, closed = False, face = True, support = None)
    import Arch
    line.Support = [(structure, facename)]
    if amount_spacing_check:
        rebar = Arch.makeRebar(structure, line, diameter, amount_spacing_value, f_cover)
    else:
        size = (ArchCommands.projectToVector(structure.Shape.copy(), face.normalAt(0, 0))).Length
        rebar = Arch.makeRebar(structure, line, diameter,\
            int((size - diameter) / amount_spacing_value), f_cover)
    rebar.Direction = FaceNormal.negative()
    rebar.Rounding = rounding
    # Adds properties to the rebar object
    rebar.ViewObject.addProperty("App::PropertyString", "RebarShape", "RebarDialog",\
        QT_TRANSLATE_NOOP("App::Property","Shape of rebar")).RebarShape = "Stirrup"
    rebar.ViewObject.setEditorMode("RebarShape", 2)
    rebar.addProperty("App::PropertyDistance", "SideCover", "RebarDialog",\
        QT_TRANSLATE_NOOP("App::Property", "Side cover of rebar")).SideCover = s_cover
    rebar.setEditorMode("SideCover", 2)
    rebar.addProperty("App::PropertyDistance", "FrontCover", "RebarDialog",\
        QT_TRANSLATE_NOOP("App::Property", "Top cover of rebar")).FrontCover = f_cover
    rebar.setEditorMode("FrontCover", 2)
    rebar.addProperty("App::PropertyInteger", "BentAngle", "RebarDialog",\
        QT_TRANSLATE_NOOP("App::Property", "Bent angle between at the end of rebar")).BentAngle = bentAngle
    rebar.setEditorMode("BentAngle", 2)
    rebar.addProperty("App::PropertyInteger", "BentFactor", "RebarDialog",\
        QT_TRANSLATE_NOOP("App::Property", "Bent Length is the equal to BentFactor * Diameter")).BentFactor = bentFactor
    rebar.setEditorMode("BentFactor", 2)
    rebar.addProperty("App::PropertyBool", "AmountCheck", "RebarDialog",\
        QT_TRANSLATE_NOOP("App::Property", "Amount radio button is checked")).AmountCheck
    rebar.setEditorMode("AmountCheck", 2)
    rebar.addProperty("App::PropertyDistance", "TrueSpacing", "RebarDialog",\
        QT_TRANSLATE_NOOP("App::Property", "Spacing between of rebars")).TrueSpacing = amount_spacing_value
    rebar.setEditorMode("TrueSpacing", 2)
    if amount_spacing_check:
        rebar.AmountCheck = True
    else:
        rebar.AmountCheck = False
        rebar.TrueSpacing = amount_spacing_value
    rebar.Label = "Stirrup"
    FreeCAD.ActiveDocument.recompute()
    return rebar

def editStirrup(Rebar, s_cover, f_cover, bentAngle, bentFactor, diameter, rounding,\
        amount_spacing_check, amount_spacing_value, structure = None, facename = None):
    sketch = Rebar.Base
    if structure and facename:
        sketch.Support = [(structure, facename)]
    # Check if sketch support is empty.
    if not sketch.Support:
        showWarning("You have checked remove external geometry of base sketchs when needed.\nTo unchecked Edit->Preferences->Arch.")
        return
    # Assigned values
    facename = sketch.Support[0][1][0]
    structure = sketch.Support[0][0]
    face = structure.Shape.Faces[getFaceNumber(facename) - 1]
    StructurePRM = getTrueParametersOfStructure(structure)
    #FreeCAD.Console.PrintMessage(str(StructurePRM)+"\n")
    # Get parameters of the face where sketch of rebar is drawn
    FacePRM = getParametersOfFace(structure, facename, False)
    FaceNormal = face.normalAt(0, 0)
    FaceNormal = face.Placement.Rotation.inverted().multVec(FaceNormal)
    # Calculate the coordinates value of U-Shape rebar
    points = getpointsOfStirrup(FacePRM, s_cover, bentAngle, bentFactor, diameter, rounding, FaceNormal)
    Rebar.Base.Points = points
    FreeCAD.ActiveDocument.recompute()
    Rebar.Direction = FaceNormal.negative()
    Rebar.OffsetStart = f_cover
    Rebar.OffsetEnd = f_cover
    Rebar.BentAngle = bentAngle
    Rebar.BentFactor = bentFactor
    Rebar.Rounding = rounding
    Rebar.Diameter = diameter
    if amount_spacing_check:
        Rebar.Amount = amount_spacing_value
        FreeCAD.ActiveDocument.recompute()
        Rebar.AmountCheck = True
    else:
        size = (ArchCommands.projectToVector(structure.Shape.copy(), face.normalAt(0, 0))).Length
        Rebar.Amount = int((size - diameter) / amount_spacing_value)
        FreeCAD.ActiveDocument.recompute()
        Rebar.AmountCheck = False
    Rebar.FrontCover = f_cover
    Rebar.SideCover = s_cover
    Rebar.TrueSpacing = amount_spacing_value
    FreeCAD.ActiveDocument.recompute()

def editDialog(vobj):
    FreeCADGui.Control.closeDialog()
    obj = _StirrupTaskPanel(vobj.Object)
    obj.form.customSpacing.setEnabled(True)
    obj.form.removeCustomSpacing.setEnabled(True)
    obj.form.frontCover.setText(str(vobj.Object.FrontCover))
    obj.form.sideCover.setText(str(vobj.Object.SideCover))
    obj.form.diameter.setText(str(vobj.Object.Diameter))
    obj.form.bentAngle.setCurrentIndex(obj.form.bentAngle.findText(str(vobj.Object.BentAngle)))
    obj.form.bentFactor.setValue(vobj.Object.BentFactor)
    obj.form.rounding.setValue(vobj.Object.Rounding)
    if vobj.Object.AmountCheck:
        obj.form.amount.setValue(vobj.Object.Amount)
    else:
        obj.form.amount_radio.setChecked(False)
        obj.form.spacing_radio.setChecked(True)
        obj.form.amount.setDisabled(True)
        obj.form.spacing.setEnabled(True)
        obj.form.spacing.setText(str(vobj.Object.TrueSpacing))
    #obj.form.PickSelectedFace.setVisible(False)
    FreeCADGui.Control.showDialog(obj)

def CommandStirrup():
    selected_obj = check_selected_face()
    if selected_obj:
        FreeCADGui.Control.showDialog(_StirrupTaskPanel())
