from PySide import QtCore, QtGui
import FreeCADGui, FreeCAD
import math

def check_selected_face():
    """ check_selected_face(): This function checks whether user have selected
        any face or not."""
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

def getEdgesAngle(edge1, edge2):
    """ getEdgesAngle(edge1, edge2): returns a angle between two edges."""
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
    angles = [round(getEdgesAngle(edges[0], edges[1])), round(getEdgesAngle(edges[0], edges[2])),
            round(getEdgesAngle(edges[0], edges[3]))]
    if angles.count(90) == 2 and (angles.count(180) == 1 or angles.count(0) == 1):
        return True
    else:
        return False

def getBaseStructuralObject(obj):
    """ getBaseStructuralObject(obj): This function will return last base
        structural object."""
    if not obj.Base:
        return obj
    else:
        return getBaseStructuralObject(obj.Base)


def getBaseObject(obj):
    """ getBaseObject(obj): This function will return last base object."""
    if hasattr(obj, "Base"):
        return getBaseObject(obj.Base)
    else:
        return obj

def getTrueParametersOfStructure(obj):
    """ getTrueParametersOfStructure(obj): This function return actual length,
    width and height of the structural element in the form of array like
    [Length, Width, Height]"""
    baseObject = getBaseObject(obj)
    # If selected_obj is not derived from any base object
    if baseObject:
        # If selected_obj is derived from SketchObject
        if baseObject.isDerivedFrom("Sketcher::SketchObject"):
            edges = baseObject.Shape.Edges
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
                return None
        else:
            return None
        height = obj.Height.Value
    else:
        structuralBaseObject = getBaseStructuralObject(obj)
        length = structuralBaseObject.Length.Value
        width = structuralBaseObject.Width.Value
        height = structuralBaseObject.Height.Value
    return [length, width, height]

def getParametersOfFace(obj, selected_face, sketch=True):
    """ getParametersOfFace(obj, selected_face): This function will return
    length, width and points of center of mass of a given face in the form of list like
    [(FaceLength, FaceWidth), (CenterOfMassX, CenterOfMassY)]"""
    StructurePRM = getTrueParametersOfStructure(obj)
    if not StructurePRM:
        return None
    normal = selected_face.normalAt(0,0)
    normal = selected_face.Placement.Rotation.inverted().multVec(normal)
    center_of_mass = selected_face.CenterOfMass
    if not obj.Armatures:
        center_of_mass = center_of_mass.sub(getBaseStructuralObject(obj).Placement.Base)
    # Set length and width of user selected face of structural element
    flag = True
    for i in range(len(normal)):
        if round(normal[i]) == 0:
            if flag and i == 0:
                x = center_of_mass[i]
                facelength = StructurePRM[0]
                flag = False
            elif flag and i == 1:
                x = center_of_mass[i]
                facelength = StructurePRM[1]
                flag = False
            if i == 1:
                y = center_of_mass[i]
                facewidth = StructurePRM[1]
            elif i == 2:
                y = center_of_mass[i]
                facewidth = StructurePRM[2]
        else:
            z = center_of_mass[i]
    if not sketch:
        center_of_mass = selected_face.CenterOfMass
        return [(facelength, facewidth), center_of_mass]
    return [(facelength, facewidth), (x, y)]

def showWarning(message):
    """ showWarning(message): This function is used to produce warning
    message for the user."""
    msg = QtGui.QMessageBox()
    msg.setIcon(QtGui.QMessageBox.Warning)
    msg.setText(message)
    msg.setStandardButtons(QtGui.QMessageBox.Ok)
    msg.exec_()
