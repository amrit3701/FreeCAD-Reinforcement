# ***************************************************************************
# *                                                                         *
# *   Copyright (c) 2017 - Amritpal Singh <amrit3701@gmail.com              *
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

__title__ = "UShapeRebar"
__author__ = "Amritpal Singh"
__url__ = "https://www.freecadweb.org"

from PySide import QtCore, QtGui
from Rebarfunc import *
from PySide.QtCore import QT_TRANSLATE_NOOP
import FreeCAD, FreeCADGui, os, sys
import math

class _UShapeRebarTaskPanel:
    def __init__(self, Rebar = None):
        self.form = FreeCADGui.PySideUic.loadUi(os.path.splitext(__file__)[0]+".ui")
        self.form.setWindowTitle(QtGui.QApplication.translate("Arch", "U-Shape Rebar", None))
        self.form.amount_radio.clicked.connect(self.amount_radio_clicked)
        self.form.spacing_radio.clicked.connect(self.spacing_radio_clicked)
        self.form.image.setPixmap(QtGui.QPixmap(os.path.split(os.path.abspath(__file__))[0]+"/icons/UShapeRebar.svg"))
        self.Rebar = Rebar

    def getStandardButtons(self):
        return int(QtGui.QDialogButtonBox.Ok) | int(QtGui.QDialogButtonBox.Cancel)

    def accept(self):
        f_cover = self.form.frontCover.text()
        f_cover = FreeCAD.Units.Quantity(f_cover).Value
        b_cover = self.form.bottomCover.text()
        b_cover = FreeCAD.Units.Quantity(b_cover).Value
        s_cover = self.form.sideCover.text()
        s_cover = FreeCAD.Units.Quantity(s_cover).Value
        t_cover = self.form.topCover.text()
        t_cover = FreeCAD.Units.Quantity(t_cover).Value
        diameter = self.form.diameter.text()
        diameter = FreeCAD.Units.Quantity(diameter).Value
        rounding = self.form.rounding.value()
        amount_check = self.form.amount_radio.isChecked()
        spacing_check = self.form.spacing_radio.isChecked()
        if not self.Rebar:
            if amount_check == True:
                amount = self.form.amount.value()
                makeUShapeRebar(f_cover, b_cover, s_cover, diameter, t_cover, rounding, True, amount)
            elif spacing_check == True:
                spacing = self.form.spacing.text()
                spacing = FreeCAD.Units.Quantity(spacing).Value
                makeUShapeRebar(f_cover, b_cover, s_cover, diameter, t_cover, rounding, False, spacing)
        else:
            if amount_check == True:
                amount = self.form.amount.value()
                editUShapeRebar(self.Rebar, f_cover, b_cover, s_cover, diameter, t_cover, rounding, True, amount)
            elif spacing_check == True:
                spacing = self.form.spacing.text()
                spacing = FreeCAD.Units.Quantity(spacing).Value
                editUShapeRebar(self.Rebar, f_cover, b_cover, s_cover, diameter, t_cover, rounding, False, spacing)
        FreeCAD.Console.PrintMessage("Done!\n")
        FreeCADGui.Control.closeDialog(self)

    def amount_radio_clicked(self):
        self.form.spacing.setEnabled(False)
        self.form.amount.setEnabled(True)

    def spacing_radio_clicked(self):
        self.form.amount.setEnabled(False)
        self.form.spacing.setEnabled(True)


def makeUShapeRebar(f_cover, b_cover, s_cover, diameter, t_cover, rounding, amount_spacing_check, amount_spacing_value):
    """ makeUShapeRebar(f_cover, b_cover, s_cover, diameter, t_cover, rounding, rebarAlong, amount_spacing_check, amount_spacing_value):
    Adds the U-Shape reinforcement bar to the selected structural object"""
    selected_obj = FreeCADGui.Selection.getSelectionEx()[0]
    StructurePRM = getTrueParametersOfStructure(selected_obj.Object)
    FacePRM = getParametersOfFace(selected_obj.Object, selected_obj.SubObjects[0])
    if not FacePRM:
        FreeCAD.Console.PrintError("Cannot identified shape or from which base object sturctural element is derived\n")
        return
    # Calculate the coordinate values of U-Shape rebar
    x1 = FacePRM[1][0] - FacePRM[0][0]/2 + s_cover
    y1 = FacePRM[1][1] + FacePRM[0][1]/2 - t_cover
    x2 = FacePRM[1][0] - FacePRM[0][0]/2 + s_cover
    y2 = FacePRM[1][1] - FacePRM[0][1]/2 + b_cover
    x3 = FacePRM[1][0] - FacePRM[0][0]/2 + FacePRM[0][0] - s_cover
    y3 = FacePRM[1][1] - FacePRM[0][1]/2 + b_cover
    x4 = FacePRM[1][0] - FacePRM[0][0]/2 + FacePRM[0][0] - s_cover
    y4 = FacePRM[1][1] + FacePRM[0][1]/2 - t_cover
    import Part, Arch
    sketch = FreeCAD.activeDocument().addObject('Sketcher::SketchObject','Sketch')
    sketch.MapMode = "FlatFace"
    sketch.Support = [(selected_obj.Object, selected_obj.SubElementNames[0])]
    FreeCAD.ActiveDocument.recompute()
    sketch.addGeometry(Part.LineSegment(FreeCAD.Vector(x1, y1, 0), FreeCAD.Vector(x2, y2, 0)), False)
    sketch.addGeometry(Part.LineSegment(FreeCAD.Vector(x2, y2, 0), FreeCAD.Vector(x3, y3, 0)), False)
    import Sketcher
    sketch.addConstraint(Sketcher.Constraint('Coincident',0,2,1,1))
    sketch.addGeometry(Part.LineSegment(FreeCAD.Vector(x3, y3, 0), FreeCAD.Vector(x4, y4, 0)), False)
    sketch.addConstraint(Sketcher.Constraint('Coincident',1,2,2,1))
    if amount_spacing_check == True:
        rebar = Arch.makeRebar(selected_obj.Object, sketch, diameter, amount_spacing_value, f_cover)
        FreeCAD.ActiveDocument.recompute()
    else:
        rebar = Arch.makeRebar(selected_obj.Object, sketch, diameter, int((StructurePRM[1]-diameter)/amount_spacing_value), f_cover)
    rebar.Rounding = rounding
    # Adds properties to the rebar object
    rebar.ViewObject.addProperty("App::PropertyString","RebarShape","RebarDialog",QT_TRANSLATE_NOOP("App::Property","Shape of rebar")).RebarShape = "UShapeRebar"
    rebar.ViewObject.setEditorMode("RebarShape",2)
    rebar.addProperty("App::PropertyDistance","FrontCover","RebarDialog",QT_TRANSLATE_NOOP("App::Property","Front cover of rebar")).FrontCover = f_cover
    rebar.setEditorMode("FrontCover",2)
    rebar.addProperty("App::PropertyDistance","SideCover","RebarDialog",QT_TRANSLATE_NOOP("App::Property","Side cover of rebar")).SideCover = s_cover
    rebar.setEditorMode("SideCover",2)
    rebar.addProperty("App::PropertyDistance","BottomCover","RebarDialog",QT_TRANSLATE_NOOP("App::Property","Bottom cover of rebar")).BottomCover = b_cover
    rebar.setEditorMode("BottomCover",2)
    rebar.addProperty("App::PropertyBool","AmountCheck","RebarDialog",QT_TRANSLATE_NOOP("App::Property","Amount radio button is checked")).AmountCheck
    rebar.setEditorMode("AmountCheck",2)
    rebar.addProperty("App::PropertyDistance","TopCover","RebarDialog",QT_TRANSLATE_NOOP("App::Property","Top cover of rebar")).TopCover = t_cover
    rebar.setEditorMode("TopCover",2)
    rebar.addProperty("App::PropertyDistance","TrueSpacing","RebarDialog",QT_TRANSLATE_NOOP("App::Property","Spacing between of rebars")).TrueSpacing = amount_spacing_value
    rebar.setEditorMode("TrueSpacing",2)
#    rebar.FrontCover = f_cover
#    rebar.SideCover = s_cover
#    rebar.BottomCover = b_cover
#    rebar.TopCover = t_cover
    if amount_spacing_check:
        rebar.AmountCheck = True
    else:
        rebar.AmountCheck = False
        rebar.TrueSpacing = amount_spacing_value
    FreeCAD.ActiveDocument.recompute()

def editUShapeRebar(Rebar, f_cover, b_cover, s_cover, diameter, t_cover, rounding, amount_spacing_check, amount_spacing_value):
    sketch = Rebar.Base
    # Check if sketch support is empty.
    if not sketch.Support:
        showWarning("You have checked remove external geometry of base sketchs when needed.\nTo unchecked Edit->Preferences->Arch.")
        return
    # Assigned values
    facename = sketch.Support[0][1][0]
    structure = sketch.Support[0][0]
    face = structure.Shape.Faces[int(facename[-1])-1]
    StructurePRM = getTrueParametersOfStructure(structure)
    # Get parameters of the face where sketch of rebar is drawn
    FacePRM = getParametersOfFace(structure, face)
    # Calculate the coordinates value of U-Shape rebar
    x1 = FacePRM[1][0] - FacePRM[0][0]/2 + s_cover
    y1 = FacePRM[1][1] + FacePRM[0][1]/2 - t_cover
    x2 = FacePRM[1][0] - FacePRM[0][0]/2 + s_cover
    y2 = FacePRM[1][1] - FacePRM[0][1]/2 + b_cover
    x3 = FacePRM[1][0] - FacePRM[0][0]/2 + FacePRM[0][0] - s_cover
    y3 = FacePRM[1][1] - FacePRM[0][1]/2 + b_cover
    x4 = FacePRM[1][0] - FacePRM[0][0]/2 + FacePRM[0][0] - s_cover
    y4 = FacePRM[1][1] + FacePRM[0][1]/2 - t_cover
    sketch.movePoint(0,1,FreeCAD.Vector(x1,y1,0),0)
    FreeCAD.ActiveDocument.recompute()
    sketch.movePoint(0,2,FreeCAD.Vector(x2,y2,0),0)
    FreeCAD.ActiveDocument.recompute()
    sketch.movePoint(1,2,FreeCAD.Vector(x3,y3,0),0)
    FreeCAD.ActiveDocument.recompute()
    sketch.movePoint(2,2,FreeCAD.Vector(x4,y4,0),0)
    FreeCAD.ActiveDocument.recompute()
    Rebar.OffsetStart = f_cover
    Rebar.OffsetEnd = f_cover
    if amount_spacing_check == True:
        Rebar.Amount = amount_spacing_value
        FreeCAD.ActiveDocument.recompute()
        Rebar.AmountCheck = True
    else:
        Rebar.Amount = int((StructurePRM[1]-diameter)/amount_spacing_value)
        FreeCAD.ActiveDocument.recompute()
        Rebar.AmountCheck = False
    Rebar.FrontCover = f_cover
    Rebar.SideCover = s_cover
    Rebar.BottomCover = b_cover
    Rebar.TopCover = t_cover
    Rebar.Rounding = rounding
    Rebar.TrueSpacing = amount_spacing_value
    FreeCAD.ActiveDocument.recompute()

def editDialog(vobj):
    FreeCADGui.Control.closeDialog()
    obj = _UShapeRebarTaskPanel(vobj.Object)
    obj.form.frontCover.setText(str(vobj.Object.FrontCover))
    obj.form.sideCover.setText(str(vobj.Object.SideCover))
    obj.form.bottomCover.setText(str(vobj.Object.BottomCover))
    obj.form.diameter.setText(str(vobj.Object.Diameter))
    obj.form.topCover.setText(str(vobj.Object.TopCover))
    obj.form.rounding.setValue(vobj.Object.Rounding)
    if vobj.Object.AmountCheck == True:
        obj.form.amount.setValue(vobj.Object.Amount)
    else:
        obj.form.amount_radio.setChecked(False)
        obj.form.spacing_radio.setChecked(True)
        obj.form.amount.setDisabled(True)
        obj.form.spacing.setEnabled(True)
        obj.form.spacing.setText(str(vobj.Object.TrueSpacing))
    FreeCADGui.Control.showDialog(obj)

def CommandUShapeRebar():
    selected_obj = check_selected_face()
    if selected_obj:
        FreeCADGui.Control.showDialog(_UShapeRebarTaskPanel())
