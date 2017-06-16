from PySide import QtCore, QtGui
from Rebarfunc import *
import FreeCAD, FreeCADGui, os, sys
import math

class _StraightRebarTaskPanel:
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
        diameter = self.form.diameter.text()
        diameter = FreeCAD.Units.Quantity(diameter).Value
        amount_check = self.form.amount_radio.isChecked()
        spacing_check = self.form.spacing_radio.isChecked()
        if not self.Rebar:
            if amount_check == True:
                amount = self.form.amount.value()
                makeStraightRebar(f_cover, b_cover, s_cover, diameter, True, amount)
            elif spacing_check == True:
                spacing = self.form.spacing.text()
                spacing = FreeCAD.Units.Quantity(spacing).Value
                makeStraightRebar(f_cover, b_cover, s_cover, diameter, False, spacing)
        else:
            if amount_check == True:
                amount = self.form.amount.value()
                editStraightRebar(self.Rebar, f_cover, b_cover, s_cover, diameter, True, amount)
            elif spacing_check == True:
                spacing = self.form.spacing.text()
                spacing = FreeCAD.Units.Quantity(spacing).Value
                editStraightRebar(self.Rebar, f_cover, b_cover, s_cover, diameter, False, spacing)
        FreeCAD.Console.PrintMessage("Done!\n")
        FreeCADGui.Control.closeDialog(self)

    def amount_radio_clicked(self):
        self.form.spacing.setEnabled(False)
        self.form.amount.setEnabled(True)

    def spacing_radio_clicked(self):
        self.form.amount.setEnabled(False)
        self.form.spacing.setEnabled(True)


def makeStraightRebar(f_cover, b_cover, s_cover, diameter, amount_spacing_check, amount_spacing_value):
    """makeStraightRebar(f_cover, b_cover, s_cover, diameter, amount_spacing_check, amount_spacing_value):
    Adds the straight reinforcement bar to the selected structural object"""
    selected_obj = FreeCADGui.Selection.getSelectionEx()[0]
    FacePRM = getParametersOfFace(selected_obj.Object, selected_obj.SubObjects[0])
    # Calculate the start and end points for staight line (x1, y2) and (x2, y2)
    x1 = FacePRM[1][0] - FacePRM[0][0]/2 + s_cover
    y1 = FacePRM[1][1] - FacePRM[0][1]/2 + b_cover
    x2 = FacePRM[1][0] - FacePRM[0][0]/2 + FacePRM[0][0] - s_cover
    y2 = FacePRM[1][1] - FacePRM[0][1]/2 + b_cover
    import Part, Arch
    sketch = FreeCAD.activeDocument().addObject('Sketcher::SketchObject','Sketch')
    sketch.MapMode = "FlatFace"
    sketch.Support = [(selected_obj.Object, selected_obj.SubElementNames[0])]
    sketch.addGeometry(Part.LineSegment(FreeCAD.Vector(x1, y1, 0), FreeCAD.Vector(x2, y2, 0)), False)
    if amount_spacing_check == True:
        rebar = Arch.makeRebar(selected_obj.Object, sketch, diameter, amount_spacing_value, f_cover)
        FreeCAD.ActiveDocument.recompute()
    else:
        rebar = Arch.makeRebar(selected_obj.Object, sketch, diameter, int((width-diameter)/amount_spacing_value), f_cover)
    rebar.ViewObject.Proxy.setpropertyRebarShape(rebar.ViewObject, "StraightRebar")
    rebar.ViewObject.FrontCover = f_cover
    rebar.ViewObject.SideCover = s_cover
    rebar.ViewObject.BottomCover = b_cover
    if amount_spacing_check:
        rebar.ViewObject.AmountCheck = True
    else:
        rebar.ViewObject.AmountCheck = False
    FreeCAD.ActiveDocument.recompute()

def editStraightRebar(Rebar, f_cover, b_cover, s_cover, diameter, amount_spacing_check, amount_spacing_value):
    sketch = Rebar.Base
    facename = sketch.Support[0][1][0]
    structure = sketch.Support[0][0]
    face = structure.Shape.Faces[int(facename[-1])-1]
    FacePRM = getParametersOfFace(structure, face)
    # Calculate the start and end points for staight line (x1, y2) and (x2, y2)
    x1 = FacePRM[1][0] - FacePRM[0][0]/2 + s_cover
    y1 = FacePRM[1][1] - FacePRM[0][1]/2 + b_cover
    x2 = FacePRM[1][0] - FacePRM[0][0]/2 + FacePRM[0][0] - s_cover
    y2 = FacePRM[1][1] - FacePRM[0][1]/2 + b_cover
    FreeCAD.Console.PrintMessage(str(x1)+"  "+str(y1)+"  "+str(x2)+" "+str(y2)+"Done!\n")
    sketch.movePoint(0,1,FreeCAD.Vector(x1,y1,0),0)
    sketch.movePoint(0,2,FreeCAD.Vector(x2,y2,0),0)
    if amount_spacing_check == True:
        Rebar.Amount = amount_spacing_value
    else:
        Rebar.Amount = int((width-diameter)/amount_spacing_value)
    Rebar.ViewObject.FrontCover = f_cover
    Rebar.ViewObject.SideCover = s_cover
    Rebar.ViewObject.BottomCover = b_cover
    if amount_spacing_check:
        Rebar.ViewObject.AmountCheck = True
    else:
        Rebar.ViewObject.AmountCheck = False
    FreeCAD.ActiveDocument.recompute()

def editDialog(vobj):
    FreeCADGui.Control.closeDialog()
    obj = _StraightRebarTaskPanel(vobj.Object)
    obj.form.frontCover.setText(str(vobj.FrontCover))
    obj.form.sideCover.setText(str(vobj.SideCover))
    obj.form.bottomCover.setText(str(vobj.BottomCover))
    obj.form.diameter.setText(str(vobj.Object.Diameter))
    obj.form.amount.setValue(vobj.Object.Amount)
    FreeCADGui.Control.showDialog(obj)

if FreeCAD.GuiUp:
    #selected_obj = check_selected_face()
    selected_obj = FreeCADGui.Selection.getSelectionEx()[0]
    if selected_obj:
        FreeCADGui.Control.showDialog(_StraightRebarTaskPanel())
