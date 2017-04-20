from PySide import QtCore, QtGui
import Arch

class _UShapeRebarTaskPanel:
    def __init__(self):
        self.form = FreeCADGui.PySideUic.loadUi("<path of UShapeRebar.ui file>")
        self.form.rebarAlong.addItems(["Length", "Width"])
        self.form.amount_radio.clicked.connect(self.amount_radio_clicked)
        self.form.spacing_radio.clicked.connect(self.spacing_radio_clicked)
        QtCore.QObject.connect(self.form.submit, QtCore.SIGNAL("clicked()"), self.accept)

    def getStandardButtons(self):
        return int(QtGui.QDialogButtonBox.Close)

    def accept(self):
        try:
            f_cover = int(self.form.frontCover.text())
            b_cover = int(self.form.bottomCover.text())
            s_cover = int(self.form.sideCover.text())
            bent_length = int(self.form.bentLength.text())
            rounding = self.form.rounding.value()
            rebarAlong = str(self.form.rebarAlong.currentText())
            diameter = self.form.diameter.value()
            amount_check = self.form.amount_radio.isChecked()
            spacing_check = self.form.spacing_radio.isChecked()
            if amount_check == True:
                amount = int(self.form.amount.text())
                makeUShapeRebar(f_cover, b_cover, s_cover, diameter, bent_length, rounding, rebarAlong, True, amount)
            elif spacing_check == True:
                spacing = int(self.form.spacing.text())
                makeUShapeRebar(f_cover, b_cover, s_cover, diameter, bent_length, rounding, rebarAlong, False, spacing)
            FreeCAD.Console.PrintMessage("Done!\n")
            self.form.hide()
        except Exception as e: FreeCAD.Console.PrintMessage(str(e)+"\n")

    def amount_radio_clicked(self):
        self.form.spacing.setEnabled(False)
        self.form.amount.setEnabled(True)

    def spacing_radio_clicked(self):
        self.form.amount.setEnabled(False)
        self.form.spacing.setEnabled(True)


def makeUShapeRebar(f_cover, b_cover, s_cover, diameter, bent_length, rounding, rebarAlong, amount_spacing_check, amount_spacing_value):
    """makeUShapeRebar(f_cover, b_cover, s_cover, diameter, bent_length, rounding, rebarAlong, amount_spacing_check, amount_spacing_value):
    Adds the U-Shape reinforcement bar to the selected structural object"""
    try:
        selected_obj = FreeCADGui.Selection.getSelectionEx()[0]
	length = int(selected_obj.Object.Length)
	width = int(selected_obj.Object.Width)
	height = int(selected_obj.Object.Height)
	sketch = App.activeDocument().addObject('Sketcher::SketchObject','Sketch')
	sketch.MapMode = "FlatFace"
	if rebarAlong == "Length":
            sketch.Support = [(selected_obj.Object, "Face1")]
            sketch.addGeometry(Part.LineSegment(App.Vector(s_cover, -(height/2)+b_cover+bent_length, 0), App.Vector(s_cover, -(height/2)+b_cover, 0)), False)
            sketch.addGeometry(Part.LineSegment(App.Vector(s_cover, -(height/2)+b_cover, 0), App.Vector(length-s_cover, -(height/2)+b_cover, 0)), False)
            sketch.addConstraint(Sketcher.Constraint('Coincident',0,2,1,1))
            sketch.addGeometry(Part.LineSegment(App.Vector(length-s_cover, -(height/2)+b_cover, 0), App.Vector(length-s_cover, -(height/2)+b_cover+bent_length, 0)), False)
            sketch.addConstraint(Sketcher.Constraint('Coincident',1,2,2,1))
            if amount_spacing_check == True:
                structure = Arch.makeRebar(selected_obj.Object, sketch, diameter, amount_spacing_value, f_cover)
            else:
                structure = Arch.makeRebar(selected_obj.Object, sketch, diameter, (length-diameter)/amount_spacing_value, f_cover)
        elif rebarAlong == "Width":
            sketch.Support = [(selected_obj.Object, "Face6")]
            sketch.addGeometry(Part.LineSegment(App.Vector(-(width/2)+s_cover, -(height/2)+b_cover+bent_length, 0), App.Vector(-(width/2)+s_cover, -(height/2)+b_cover, 0)), False)
            sketch.addGeometry(Part.LineSegment(App.Vector(-(width/2)+s_cover, -(height/2)+b_cover, 0), App.Vector((width/2)-s_cover, -(height/2)+b_cover, 0)), False)
            sketch.addConstraint(Sketcher.Constraint('Coincident',0,2,1,1))
            sketch.addGeometry(Part.LineSegment(App.Vector((width/2)-s_cover, -(height/2)+b_cover, 0), App.Vector((width/2)-s_cover, -(height/2)+b_cover+bent_length, 0)), False)
            sketch.addConstraint(Sketcher.Constraint('Coincident',1,2,2,1))
            if amount_spacing_check == True:
                structure = Arch.makeRebar(selected_obj.Object, sketch, diameter, amount_spacing_value, f_cover)
            else:
                structure = Arch.makeRebar(selected_obj.Object, sketch, diameter, (width-diameter)/amount_spacing_value, f_cover)
        structure.Rounding = rounding
        FreeCAD.ActiveDocument.recompute()
    except Exception as e: FreeCAD.Console.PrintMessage(str(e)+"\n")

if FreeCAD.GuiUp:
    FreeCADGui.Control.showDialog(_UShapeRebarTaskPanel())
