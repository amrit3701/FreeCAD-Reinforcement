from PySide import QtCore, QtGui
import FreeCAD, FreeCADGui, os
import math

class _StraightRebarTaskPanel:
    def __init__(self):
        self.form = FreeCADGui.PySideUic.loadUi(os.path.splitext(__file__)[0]+".ui")
        self.form.amount_radio.clicked.connect(self.amount_radio_clicked)
        self.form.spacing_radio.clicked.connect(self.spacing_radio_clicked)
        QtCore.QObject.connect(self.form.submit, QtCore.SIGNAL("clicked()"), self.accept)
        self.form.image.setPixmap(QtGui.QPixmap(os.path.split(os.path.abspath(__file__))[0]+"/icons/FrontFaceStraightRebar.svg"))

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
        if amount_check == True:
            amount = self.form.amount.value()
            makeStraightRebar(f_cover, b_cover, s_cover, diameter, True, amount)
        elif spacing_check == True:
            spacing = self.form.spacing.text()
            spacing = FreeCAD.Units.Quantity(spacing).Value
            makeStraightRebar(f_cover, b_cover, s_cover, diameter, False, spacing)
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
    selected_face = selected_obj.SubObjects[0]
    normal = selected_face.normalAt(0,0)
    normal = selected_face.Placement.Rotation.inverted().multVec(normal)
    center_of_mass = selected_face.CenterOfMass
    # If selected_obj is not derived from any base object
    if selected_obj.Object.Base == None:
        length = selected_obj.Object.Length.Value
        width = selected_obj.Object.Width.Value
    # If selected_obj is derived from SketchObject
    elif selected_obj.Object.Base.isDerivedFrom("Sketcher::SketchObject"):
        edges = selected_obj.Object.Shape.Edges
        if checkRectangle(edges):
            for edge in edges:
                # Representation vector of edge
                rep_vector = edge.Vertexes[1].Point.sub(edge.Vertexes[0].Point)
                rep_vector_angle = round(math.degrees(rep_vector.getAngle(FreeCAD.Vector(1,0,0))))
                if rep_vector_angle in {0, 180}:
                    length = edge.Length
                else:
                    width = edge.Length
    else:
        FreeCAD.Console.PrintError("Cannot identified from which base object sturctural element is derived\n")
        return
    height = selected_obj.Object.Height.Value
    # Set length and width of user selected face of structural element
    flag = True
    for i in range(len(normal)):
        if round(normal[i]) == 0:
            if flag and i == 0:
                x = center_of_mass[i]
                facelength = length
                flag = False
            elif flag and i == 1:
                x = center_of_mass[i]
                facelength = width
                flag = False
            if i == 1:
                y = center_of_mass[i]
                facewidth = width
            elif i == 2:
                y = center_of_mass[i]
                facewidth = height
    sketch = FreeCAD.activeDocument().addObject('Sketcher::SketchObject','Sketch')
    sketch.MapMode = "FlatFace"
    # Calculate the start and end points for staight line (x1, y2) and (x2, y2)
    x1 = x - facelength/2 + s_cover
    y1 = y - facewidth/2 + b_cover
    x2 = x - facelength/2 + facelength - s_cover
    y2 = y - facewidth/2 + b_cover
    sketch.Support = [(selected_obj.Object, selected_obj.SubElementNames[0])]
    import Part, Arch
    sketch.addGeometry(Part.LineSegment(FreeCAD.Vector(x1, y1, 0), FreeCAD.Vector(x2, y2, 0)), False)
    if amount_spacing_check == True:
        structure = Arch.makeRebar(selected_obj.Object, sketch, diameter, amount_spacing_value, f_cover)
    else:
        structure = Arch.makeRebar(selected_obj.Object, sketch, diameter, int((width-diameter)/amount_spacing_value), f_cover)
    FreeCADGui.ActiveDocument.getObject(structure.Label).RebarShape = "StraightRebar"
    FreeCAD.ActiveDocument.recompute()

def check_selected_face():
    selected_objs = FreeCADGui.Selection.getSelectionEx()
    if not selected_objs:
        showWarning("Select any face of the structural element.")
        selected_obj = None
    else:
        selected_face_names = selected_objs[0].SubElementNames
        if not selected_face_names:
            selected_obj = None
            showWarning("Select any face of the structural element.")
        elif "Face" in selected_face_names[0]:
            if len(selected_face_names) > 1:
                showWarning("You have selected more than one face of the structural element.")
                selected_obj = None
            elif len(selected_face_names) == 1:
                selected_obj = selected_objs[0]
        else:
            showWarning("Select any face of the selected the face.")
            selected_obj = None
    return selected_obj

def vec(edge):
    """ vec(edge) or vec(line): returns a vector from an edge or a Part.line."""
    # if edge is not straight, you'll get strange results!
    import Part
    if isinstance(edge,Part.Shape):
        return edge.Vertexes[-1].Point.sub(edge.Vertexes[0].Point)
    elif isinstance(edge,Part.Line):
        return edge.EndPoint.sub(edge.StartPoint)
    else:
        return None

def EdgesAngle(edge1, edge2):
    """ EdgesAngle(edge1, edge2): returns a angle between two edges."""
    vec1 = vec(edge1)
    vec2 = vec(edge2)
    angle = vec1.getAngle(vec2)
    import math
    angle = math.degrees(angle)
    return angle

def checkRectangle(edges):
    """ checkRectangle(edges=[]): This function checks whether the given form rectangle
        or not. It will return True when edges form rectangular shape or return False
        when edges not form a rectangular."""
    angles = [round(EdgesAngle(edges[0], edges[1])), round(EdgesAngle(edges[0], edges[2])),
            round(EdgesAngle(edges[0], edges[3]))]
    if angles.count(90) == 2 and (angles.count(180) == 1 or angles.count(0) == 1):
        return True
    else:
        return False

def showWarning(message):
    msg = QtGui.QMessageBox()
    msg.setIcon(QtGui.QMessageBox.Warning)
    msg.setText(message)
    msg.setStandardButtons(QtGui.QMessageBox.Ok)
    msg.exec_()

if FreeCAD.GuiUp:
    selected_obj = check_selected_face()
    if selected_obj:
        FreeCADGui.Control.showDialog(_StraightRebarTaskPanel())
