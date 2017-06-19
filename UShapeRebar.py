from PySide import QtCore, QtGui
from Rebarfunc import *
from PySide.QtCore import QT_TRANSLATE_NOOP
import FreeCAD, FreeCADGui, os, sys
import Sketcher
import math

class _UShapeRebarTaskPanel:
    def __init__(self, Rebar = None):
        self.form = FreeCADGui.PySideUic.loadUi(os.path.splitext(__file__)[0]+".ui")
        self.form.amount_radio.clicked.connect(self.amount_radio_clicked)
        self.form.spacing_radio.clicked.connect(self.spacing_radio_clicked)
        QtCore.QObject.connect(self.form.submit, QtCore.SIGNAL("clicked()"), self.accept)
        self.form.image.setPixmap(QtGui.QPixmap(os.path.split(os.path.abspath(__file__))[0]+"/icons/FrontFaceStraightRebar.svg"))
        self.Rebar = Rebar

    def getStandardButtons(self):
        return int(QtGui.QDialogButtonBox.Close)

    def accept(self):
        f_cover = self.form.frontCover.text()
        f_cover = FreeCAD.Units.Quantity(f_cover).Value
        b_cover = self.form.bottomCover.text()
        b_cover = FreeCAD.Units.Quantity(b_cover).Value
        s_cover = self.form.sideCover.text()
        s_cover = FreeCAD.Units.Quantity(s_cover).Value
        bent_length = self.form.bentLength.text()
        bent_length = FreeCAD.Units.Quantity(bent_length).Value
        diameter = self.form.diameter.text()
        diameter = FreeCAD.Units.Quantity(diameter).Value
        rounding = self.form.rounding.value()
        amount_check = self.form.amount_radio.isChecked()
        spacing_check = self.form.spacing_radio.isChecked()
        if not self.Rebar:
            if amount_check == True:
                amount = self.form.amount.value()
                makeUShapeRebar(f_cover, b_cover, s_cover, diameter, bent_length, rounding, True, amount)
            elif spacing_check == True:
                spacing = self.form.spacing.text()
                spacing = FreeCAD.Units.Quantity(spacing).Value
                makeUShapeRebar(f_cover, b_cover, s_cover, diameter, bent_length, rounding, False, spacing)
        else:
            if amount_check == True:
                amount = self.form.amount.value()
                editUShapeRebar(self.Rebar, f_cover, b_cover, s_cover, diameter, bent_length, rounding, True, amount)
            elif spacing_check == True:
                spacing = self.form.spacing.text()
                spacing = FreeCAD.Units.Quantity(spacing).Value
                editUShapeRebar(self.Rebar, f_cover, b_cover, s_cover, diameter, bent_length, rounding, False, spacing)
        FreeCAD.Console.PrintMessage("Done!\n")
        FreeCADGui.Control.closeDialog(self)

    def amount_radio_clicked(self):
        self.form.spacing.setEnabled(False)
        self.form.amount.setEnabled(True)

    def spacing_radio_clicked(self):
        self.form.amount.setEnabled(False)
        self.form.spacing.setEnabled(True)


def makeUShapeRebar(f_cover, b_cover, s_cover, diameter, bent_length, rounding, amount_spacing_check, amount_spacing_value):
    """makeUShapeRebar(f_cover, b_cover, s_cover, diameter, bent_length, rounding, rebarAlong, amount_spacing_check, amount_spacing_value):
    Adds the U-Shape reinforcement bar to the selected structural object"""
    selected_obj = FreeCADGui.Selection.getSelectionEx()[0]
    StructurePRM = getTrueParametersOfStructure(selected_obj.Object)
    FacePRM = getParametersOfFace(selected_obj.Object, selected_obj.SubObjects[0])
    if not FacePRM:
        FreeCAD.Console.PrintError("Cannot identified shape or from which base object sturctural element is derived\n")
        return
    # Calculate the start and end points for staight line (x1, y2) and (x2, y2)
    x1 = FacePRM[1][0] - FacePRM[0][0]/2 + s_cover
    y1 = FacePRM[1][1] - FacePRM[0][1]/2 + b_cover + bent_length
    x2 = FacePRM[1][0] - FacePRM[0][0]/2 + s_cover
    y2 = FacePRM[1][1] - FacePRM[0][1]/2 + b_cover
    x3 = FacePRM[1][0] - FacePRM[0][0]/2 + FacePRM[0][0] - s_cover
    y3 = FacePRM[1][1] - FacePRM[0][1]/2 + b_cover
    x4 = FacePRM[1][0] - FacePRM[0][0]/2 + FacePRM[0][0] - s_cover
    y4 = FacePRM[1][1] - FacePRM[0][1]/2 + b_cover + bent_length
    import Part, Arch
    sketch = FreeCAD.activeDocument().addObject('Sketcher::SketchObject','Sketch')
    sketch.MapMode = "FlatFace"
    sketch.Support = [(selected_obj.Object, selected_obj.SubElementNames[0])]
    FreeCAD.ActiveDocument.recompute()
    sketch.addGeometry(Part.LineSegment(FreeCAD.Vector(x1, y1, 0), FreeCAD.Vector(x2, y2, 0)), False)
    sketch.addGeometry(Part.LineSegment(FreeCAD.Vector(x2, y2, 0), FreeCAD.Vector(x3, y3, 0)), False)
    sketch.addConstraint(Sketcher.Constraint('Coincident',0,2,1,1))
    sketch.addGeometry(Part.LineSegment(FreeCAD.Vector(x3, y3, 0), FreeCAD.Vector(x4, y4, 0)), False)
    sketch.addConstraint(Sketcher.Constraint('Coincident',1,2,2,1))
    if amount_spacing_check == True:
        rebar = Arch.makeRebar(selected_obj.Object, sketch, diameter, amount_spacing_value, f_cover)
        FreeCAD.ActiveDocument.recompute()
    else:
        rebar = Arch.makeRebar(selected_obj.Object, sketch, diameter, int((StructurePRM[1]-diameter)/amount_spacing_value), f_cover)
    rebar.Rounding = rounding
    rebar.ViewObject.addProperty("App::PropertyString","RebarShape","RebarDialog",QT_TRANSLATE_NOOP("App::Property","Shape of rebar")).RebarShape = "UShapeRebar"
    rebar.ViewObject.setEditorMode("RebarShape",2)
    rebar.addProperty("App::PropertyLength","FrontCover","RebarDialog",QT_TRANSLATE_NOOP("App::Property","Front cover of rebar")).FrontCover = f_cover
    rebar.setEditorMode("FrontCover",2)
    rebar.addProperty("App::PropertyLength","SideCover","RebarDialog",QT_TRANSLATE_NOOP("App::Property","Side cover of rebar")).SideCover = s_cover
    rebar.setEditorMode("SideCover",2)
    rebar.addProperty("App::PropertyLength","BottomCover","RebarDialog",QT_TRANSLATE_NOOP("App::Property","Bottom cover of rebar")).BottomCover = b_cover
    rebar.setEditorMode("BottomCover",2)
    rebar.addProperty("App::PropertyBool","AmountCheck","RebarDialog",QT_TRANSLATE_NOOP("App::Property","Amount radio button is checked")).AmountCheck
    rebar.setEditorMode("AmountCheck",2)
    rebar.addProperty("App::PropertyLength","BentLength","RebarDialog",QT_TRANSLATE_NOOP("App::Property","Bent Length of rebar")).BentLength = bent_length
    rebar.FrontCover = f_cover
    rebar.SideCover = s_cover
    rebar.BottomCover = b_cover
    rebar.BentLength = bent_length
    if amount_spacing_check:
        rebar.AmountCheck = True
    else:
        rebar.AmountCheck = False
    FreeCAD.ActiveDocument.recompute()

def editUShapeRebar(Rebar, f_cover, b_cover, s_cover, diameter, bent_length, rounding, amount_spacing_check, amount_spacing_value):
    sketch = Rebar.Base
    # Assigned values
    facename = sketch.Support[0][1][0]
    structure = sketch.Support[0][0]
    face = structure.Shape.Faces[int(facename[-1])-1]
    StructurePRM = getTrueParametersOfStructure(structure)
    # Get parameters of the face where sketch of rebar is drawn
    FacePRM = getParametersOfFace(structure, face)
    # Calculate the start and end points for staight line (x1, y2) and (x2, y2)
    x1 = FacePRM[1][0] - FacePRM[0][0]/2 + s_cover
    y1 = FacePRM[1][1] - FacePRM[0][1]/2 + b_cover + bent_length
    x2 = FacePRM[1][0] - FacePRM[0][0]/2 + s_cover
    y2 = FacePRM[1][1] - FacePRM[0][1]/2 + b_cover
    x3 = FacePRM[1][0] - FacePRM[0][0]/2 + FacePRM[0][0] - s_cover
    y3 = FacePRM[1][1] - FacePRM[0][1]/2 + b_cover
    x4 = FacePRM[1][0] - FacePRM[0][0]/2 + FacePRM[0][0] - s_cover
    y4 = FacePRM[1][1] - FacePRM[0][1]/2 + b_cover + bent_length
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
    Rebar.BentLength = bent_length
    Rebar.Rounding = rounding
    FreeCAD.ActiveDocument.recompute()

def editDialog(vobj):
    FreeCADGui.Control.closeDialog()
    obj = _UShapeRebarTaskPanel(vobj.Object)
    obj.form.frontCover.setText(str(vobj.Object.FrontCover))
    obj.form.sideCover.setText(str(vobj.Object.SideCover))
    obj.form.bottomCover.setText(str(vobj.Object.BottomCover))
    obj.form.diameter.setText(str(vobj.Object.Diameter))
    obj.form.bentLength.setText(str(vobj.Object.BentLength))
    obj.form.rounding.setValue(vobj.Object.Rounding)
    obj.form.amount.setValue(vobj.Object.Amount)
    FreeCADGui.Control.showDialog(obj)

if FreeCAD.GuiUp:
    selected_obj = check_selected_face()
    if selected_obj:
        FreeCADGui.Control.showDialog(_UShapeRebarTaskPanel())
