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

__title__ = "GenericRebarFuctions"
__author__ = "Amritpal Singh"
__url__ = "https://www.freecadweb.org"

from PySide import QtCore, QtGui
from DraftGeomUtils import vec, isCubic
import FreeCAD
import FreeCADGui
import math

# --------------------------------------------------------------------------
# Generic functions
# --------------------------------------------------------------------------

def getEdgesAngle(edge1, edge2):
    """ getEdgesAngle(edge1, edge2): returns a angle between two edges."""
    vec1 = vec(edge1)
    vec2 = vec(edge2)
    angle = vec1.getAngle(vec2)
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

def getFaceNumber(s):
    """ getFaceNumber(facename): This will return a face number from face name.
    For eg.:
        Input: "Face12"
        Output: 12"""
    head = s.rstrip('0123456789')
    tail = s[len(head):]
    return int(tail)

# --------------------------------------------------------------------------
# Main functions which is use while creating any rebar.
# --------------------------------------------------------------------------

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

def getParametersOfFace(structure, facename, sketch = True):
    """ getParametersOfFace(structure, facename, sketch = True): This function will return
    length, width and points of center of mass of a given face according to the sketch
    value in the form of list.

    For eg.:
    Case 1: When sketch is True: We use True when we want to create rebars from sketch
        (planar rebars) and the sketch is strictly based on 2D so we neglected the normal
        axis of the face.
        Output: [(FaceLength, FaceWidth), (CenterOfMassX, CenterOfMassY)]

    Case 2: When sketch is False: When we want to create non-planar rebars(like stirrup)
        or we want to create rebar from a wire. Also for creating rebar from wire
        we will require three coordinates (x, y, z).
        Output: [(FaceLength, FaceWidth), (CenterOfMassX, CenterOfMassY, CenterOfMassZ)]"""
    face = structure.Shape.Faces[getFaceNumber(facename) - 1]
    center_of_mass = face.CenterOfMass
    #center_of_mass = center_of_mass.sub(getBaseStructuralObject(structure).Placement.Base)
    center_of_mass = center_of_mass.sub(structure.Placement.Base)
    Edges = []
    facePRM = []
    # When structure is cubic. It support all structure is derived from
    # any other object (like a sketch, wire etc).
    if isCubic(structure.Shape):
        for edge in face.Edges:
            if not Edges:
                Edges.append(edge)
            else:
                # Checks whether similar edges is already present in Edges list
                # or not.
                if (vec(edge)).Length not in [(vec(x)).Length for x in Edges]:
                    Edges.append(edge)
        # facePRM holds length of a edges.
        facePRM = [(vec(edge)).Length for edge in Edges]
        # Find the orientation of the face. Also eliminating normal axes
        # to the edge/face.
        # When edge is parallel to x-axis
        if Edges[0].tangentAt(0)[0] in {1,-1}:
            x = center_of_mass[0]
            if Edges[1].tangentAt(0)[1] in {1, -1}:
                y = center_of_mass[1]
            else:
                y = center_of_mass[2]
        # When edge is parallel to y-axis
        elif Edges[0].tangentAt(0)[1] in {1,-1}:
            x = center_of_mass[1]
            if Edges[1].tangentAt(0)[0] in {1, -1}:
                # Change order when edge along x-axis is at second place.
                facePRM.reverse()
                y = center_of_mass[1]
            else:
                y = center_of_mass[2]
        elif Edges[0].tangentAt(0)[2] in {1,-1}:
            y = center_of_mass[2]
            if Edges[1].tangentAt(0)[0] in {1, -1}:
                x = center_of_mass[0]
            else:
                x = center_of_mass[1]
            facePRM.reverse()
        facelength = facePRM[0]
        facewidth = facePRM[1]
    # When structure is not cubic. For founding parameters of given face
    # I have used bounding box.
    else:
        boundbox = face.BoundBox
        # Check that one length of bounding box is zero. Here bounding box
        # looks like a plane.
        if 0 in {boundbox.XLength, boundbox.YLength, boundbox.ZLength}:
            normal = face.normalAt(0,0)
            normal = face.Placement.Rotation.inverted().multVec(normal)
            #print "x: ", boundbox.XLength
            #print "y: ", boundbox.YLength
            #print "z: ", boundbox.ZLength
            # Set length and width of user selected face of structural element
            flag = True
            # FIXME: Improve below logic.
            for i in range(len(normal)):
                if round(normal[i]) == 0:
                    if flag and i == 0:
                        x = center_of_mass[i]
                        facelength =  boundbox.XLength
                        flag = False
                    elif flag and i == 1:
                        x = center_of_mass[i]
                        facelength = boundbox.YLength
                        flag = False
                    if i == 1:
                        y = center_of_mass[i]
                        facewidth = boundbox.YLength
                    elif i == 2:
                        y = center_of_mass[i]
                        facewidth = boundbox.ZLength
            #print [(facelength, facewidth), (x, y)]
    # Return parameter of the face when rebar is not created from the sketch.
    # For eg. non-planar rebars like stirrup etc.
    if not sketch:
        center_of_mass = face.CenterOfMass
        return [(facelength, facewidth), center_of_mass]
    #TODO: Add support when bounding box have depth. Here bounding box looks
    # like cuboid. If we given curved face.
    return [(facelength, facewidth), (x, y)]

# -------------------------------------------------------------------------
# Functions which is mainly used in creating stirrup.
# -------------------------------------------------------------------------

def extendedTangentPartLength(rounding, diameter, angle):
    """ extendedTangentPartLength(rounding, diameter, angle): Get a extended
    length of rounding on corners."""
    radius = rounding * diameter
    x1 = radius / math.tan(math.radians(angle))
    x2 = radius / math.cos(math.radians(90 - angle)) - radius
    return x1 + x2

def extendedTangentLength(rounding, diameter, angle):
    """ extendedTangentLength(rounding, diameter, angle): Get a extended
    length of rounding at the end of Stirrup for bent."""
    radius = rounding * diameter
    x1 = radius / math.sin(math.radians(angle))
    x2 = radius * math.tan(math.radians(90 - angle))
    return x1 + x2

# -------------------------------------------------------------------------
# Warning / Alert functions when user do something wrong.
#--------------------------------------------------------------------------

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

def getSelectedFace(self):
    selected_objs = FreeCADGui.Selection.getSelectionEx()
    if selected_objs:
        if len(selected_objs[0].SubObjects) == 1:
            if "Face" in selected_objs[0].SubElementNames[0]:
                self.SelectedObj = selected_objs[0].Object
                self.FaceName = selected_objs[0].SubElementNames[0]
                self.form.PickSelectedFaceLabel.setText("Selected face is " + self.FaceName)
            else:
                showWarning("Select any face of the structural element.")
        else:
            showWarning("Select only one face of the structural element.")
    else:
        showWarning("Select any face of the structural element.")

def showWarning(message):
    """ showWarning(message): This function is used to produce warning
    message for the user."""
    msg = QtGui.QMessageBox()
    msg.setIcon(QtGui.QMessageBox.Warning)
    msg.setText(message)
    msg.setStandardButtons(QtGui.QMessageBox.Ok)
    msg.exec_()
