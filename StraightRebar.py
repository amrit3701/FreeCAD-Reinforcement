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

__title__ = "StraightRebar"
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

def getpointsOfStraightRebar(FacePRM, s_cover, b_cover):
    """ getpointsOfStraightRebar(FacePRM, s_cover, b_cover):
    Return points of the Straight rebar in the form of array for sketch."""
    x1 = FacePRM[1][0] - FacePRM[0][0] / 2 + s_cover
    y1 = FacePRM[1][1] - FacePRM[0][1] / 2 + b_cover
    x2 = FacePRM[1][0] - FacePRM[0][0] / 2 + FacePRM[0][0] - s_cover
    y2 = FacePRM[1][1] - FacePRM[0][1] / 2 + b_cover
    return [FreeCAD.Vector(x1, y1, 0), FreeCAD.Vector(x2, y2, 0)]

class _StraightRebarTaskPanel:
    def __init__(self, Rebar = None):
        self.form = FreeCADGui.PySideUic.loadUi(os.path.splitext(__file__)[0] + ".ui")
        self.form.setWindowTitle(QtGui.QApplication.translate("Arch", "Straight Rebar", None))
        self.form.amount_radio.clicked.connect(self.amount_radio_clicked)
        self.form.spacing_radio.clicked.connect(self.spacing_radio_clicked)
        self.form.customSpacing.clicked.connect(lambda: runRebarDistribution(Rebar))
        self.form.removeCustomSpacing.clicked.connect(lambda: removeRebarDistribution(Rebar))
        self.form.PickSelectedFace.setCheckable(True)
        self.form.PickSelectedFace.toggle()
        self.form.PickSelectedFace.clicked.connect(lambda: getSelectedFace(self))
        self.form.image.setPixmap(QtGui.QPixmap(os.path.split(os.path.abspath(__file__))[0] + "/icons/StraightRebar.svg"))
        self.Rebar = Rebar
        self.SelectedObj = None
        self.FaceName = None

    def getStandardButtons(self):
        return int(QtGui.QDialogButtonBox.Ok) | int(QtGui.QDialogButtonBox.Cancel)

    def accept(self):
        f_cover = self.form.frontCover.text()
        f_cover = FreeCAD.Units.Quantity(f_cover).Value
        b_cover = self.form.bottomCover.text()
        b_cover = FreeCAD.Units.Quantity(b_cover).Value
        s_cover = self.form.sideCover.text()
        s_cover = FreeCAD.Units.Quantity(s_cover).Value
        diameter = self.form.diameter.text()
        diameter = FreeCAD.Units.Quantity(diameter).Value
        amount_check = self.form.amount_radio.isChecked()
        spacing_check = self.form.spacing_radio.isChecked()
        if not self.Rebar:
            if amount_check:
                amount = self.form.amount.value()
                makeStraightRebar(f_cover, b_cover, s_cover, diameter, True, amount, self.SelectedObj, self.FaceName)
            elif spacing_check:
                spacing = self.form.spacing.text()
                spacing = FreeCAD.Units.Quantity(spacing).Value
                makeStraightRebar(f_cover, b_cover, s_cover, diameter, False, spacing, self.SelectedObj, self.FaceName)
        else:
            if amount_check:
                amount = self.form.amount.value()
                editStraightRebar(self.Rebar, f_cover, b_cover, s_cover, diameter, True, amount, self.SelectedObj, self.FaceName)
            elif spacing_check:
                spacing = self.form.spacing.text()
                spacing = FreeCAD.Units.Quantity(spacing).Value
                editStraightRebar(self.Rebar, f_cover, b_cover, s_cover, diameter, False, spacing, self.SelectedObj, self.FaceName)
        FreeCADGui.Control.closeDialog(self)

    def amount_radio_clicked(self):
        self.form.spacing.setEnabled(False)
        self.form.amount.setEnabled(True)

    def spacing_radio_clicked(self):
        self.form.amount.setEnabled(False)
        self.form.spacing.setEnabled(True)


def makeStraightRebar(f_cover, b_cover, s_cover, diameter, amount_spacing_check, amount_spacing_value, structure = None, facename = None):
    """ makeStraightRebar(f_cover, b_cover, s_cover, diameter, amount_spacing_check, amount_spacing_value):
    Adds the straight reinforcement bar to the selected structural object."""
    if not structure and not facename:
        selected_obj = FreeCADGui.Selection.getSelectionEx()[0]
        structure = selected_obj.Object
        facename = selected_obj.SubElementNames[0]
    face = structure.Shape.Faces[int(facename[-1]) - 1]
    StructurePRM = getTrueParametersOfStructure(structure)
    FacePRM = getParametersOfFace(structure, face)
    if not FacePRM:
        FreeCAD.Console.PrintError("Cannot identified shape or from which base object sturctural element is derived\n")
        return
    # Get points of Striaght rebar
    points = getpointsOfStraightRebar(FacePRM, s_cover, b_cover)
    import Part
    import Arch
    sketch = FreeCAD.activeDocument().addObject('Sketcher::SketchObject', 'Sketch')
    sketch.MapMode = "FlatFace"
    sketch.Support = [(structure, facename)]
    FreeCAD.ActiveDocument.recompute()
    sketch.addGeometry(Part.LineSegment(points[0], points[1]), False)
    if amount_spacing_check:
        rebar = Arch.makeRebar(structure, sketch, diameter, amount_spacing_value, f_cover)
        FreeCAD.ActiveDocument.recompute()
    else:
        size = (ArchCommands.projectToVector(structure.Shape.copy(), face.normalAt(0, 0))).Length
        rebar = Arch.makeRebar(structure, sketch, diameter, int((size - diameter) / amount_spacing_value), f_cover)
    # Adds properties to the rebar object
    rebar.ViewObject.addProperty("App::PropertyString", "RebarShape", "RebarDialog", QT_TRANSLATE_NOOP("App::Property", "Shape of rebar")).RebarShape = "StraightRebar"
    rebar.ViewObject.setEditorMode("RebarShape", 2)
    rebar.addProperty("App::PropertyDistance", "FrontCover", "RebarDialog", QT_TRANSLATE_NOOP("App::Property", "Front cover of rebar")).FrontCover = f_cover
    rebar.setEditorMode("FrontCover", 2)
    rebar.addProperty("App::PropertyDistance", "SideCover", "RebarDialog", QT_TRANSLATE_NOOP("App::Property", "Side cover of rebar")).SideCover = s_cover
    rebar.setEditorMode("SideCover", 2)
    rebar.addProperty("App::PropertyDistance", "BottomCover", "RebarDialog", QT_TRANSLATE_NOOP("App::Property", "Bottom cover of rebar")).BottomCover = b_cover
    rebar.setEditorMode("BottomCover", 2)
    rebar.addProperty("App::PropertyBool", "AmountCheck", "RebarDialog", QT_TRANSLATE_NOOP("App::Property", "Amount radio button is checked")).AmountCheck
    rebar.setEditorMode("AmountCheck", 2)
    rebar.addProperty("App::PropertyDistance", "TrueSpacing", "RebarDialog", QT_TRANSLATE_NOOP("App::Property", "Spacing between of rebars")).TrueSpacing = amount_spacing_value
    rebar.setEditorMode("TrueSpacing", 2)
    if amount_spacing_check:
        rebar.AmountCheck = True
    else:
        rebar.AmountCheck = False
        rebar.TrueSpacing = amount_spacing_value
    FreeCAD.ActiveDocument.recompute()

def editStraightRebar(Rebar, f_cover, b_cover, s_cover, diameter, amount_spacing_check, amount_spacing_value, structure = None, facename = None):
    sketch = Rebar.Base
    if structure and facename:
        sketch.Support = [(structure, facename)]
        FreeCAD.ActiveDocument.recompute()
    # Check if sketch support is empty.
    if not sketch.Support:
        showWarning("You have checked remove external geometry of base sketchs when needed.\nTo unchecked Edit->Preferences->Arch.")
        return
    # Assigned values
    facename = sketch.Support[0][1][0]
    structure = sketch.Support[0][0]
    face = structure.Shape.Faces[int(facename[-1]) - 1]
    StructurePRM = getTrueParametersOfStructure(structure)
    # Get parameters of the face where sketch of rebar is drawn
    FacePRM = getParametersOfFace(structure, face)
    # Get points of Striaght rebar
    points = getpointsOfStraightRebar(FacePRM, s_cover, b_cover)
    sketch.movePoint(0, 1, points[0], 0)
    FreeCAD.ActiveDocument.recompute()
    sketch.movePoint(0, 2, points[1], 0)
    FreeCAD.ActiveDocument.recompute()
    Rebar.OffsetStart = f_cover
    Rebar.OffsetEnd = f_cover
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
    Rebar.BottomCover = b_cover
    Rebar.TrueSpacing = amount_spacing_value
    Rebar.Diameter = diameter
    FreeCAD.ActiveDocument.recompute()

def editDialog(vobj):
    FreeCADGui.Control.closeDialog()
    obj = _StraightRebarTaskPanel(vobj.Object)
    obj.form.customSpacing.setEnabled(True)
    obj.form.removeCustomSpacing.setEnabled(True)
    obj.form.frontCover.setText(str(vobj.Object.FrontCover))
    obj.form.sideCover.setText(str(vobj.Object.SideCover))
    obj.form.bottomCover.setText(str(vobj.Object.BottomCover))
    obj.form.diameter.setText(str(vobj.Object.Diameter))
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

def CommandStraightRebar():
    selected_obj = check_selected_face()
    if selected_obj:
        FreeCADGui.Control.showDialog(_StraightRebarTaskPanel())
