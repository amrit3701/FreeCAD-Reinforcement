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
from PySide.QtCore import QT_TRANSLATE_NOOP
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

def facenormalDirection(structure = None, facename = None):
    if not structure and not facename:
        selected_obj = FreeCADGui.Selection.getSelectionEx()[0]
        structure = selected_obj.Object
        facename = selected_obj.SubElementNames[0]
    face = structure.Shape.Faces[getFaceNumber(facename) - 1]
    normal = face.normalAt(0,0)
    normal = face.Placement.Rotation.inverted().multVec(normal)
    return normal


def gettupleOfNumberDiameter(diameter_string):
    """gettupleOfNumberDiameter(diameter_string): This function take input in
    specific syntax and return output in the form of list. For eg.
    Input: "3#100+2#200+3#100"
    Output: [(3, 100), (2, 200), (3, 100)]"""
    diameter_st = diameter_string.strip()
    diameter_sp = diameter_st.split("+")
    index = 0
    number_diameter_list = []
    while index < len(diameter_sp):
        # Find "#" recursively in diameter_sp array.
        in_sp = diameter_sp[index].split("#")
        number_diameter_list.append(
            (int(in_sp[0]), float(in_sp[1].replace("mm", "")))
        )
        index += 1
    return number_diameter_list


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

def getParametersOfFace(structure, facename, sketch=True):
    """ getParametersOfFace(structure, facename, sketch = True): This function will return
    length, width and points of center of mass of a given face w.r.t sketch value.

    For eg.:
    Case 1: When sketch is True: We use True when we want to create rebars from sketch
        (planar rebars) and the sketch is strictly based on 2D, so we neglected the normal
        axis of the face.
        Output: [(FaceLength, FaceWidth), (CenterOfMassX, CenterOfMassY)]

    Case 2: When sketch is False: When we want to create non-planar rebars(like stirrup)
        or rebar from a wire. Also for creating rebar from wire we will require
        three coordinates (x, y, z).
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
                if round((vec(edge)).Length) not in [round((vec(x)).Length) for x in Edges]:
                    Edges.append(edge)
        if len(Edges) == 1:
            Edges.append(edge)
        # facePRM holds length of a edges.
        facePRM = [(vec(edge)).Length for edge in Edges]
        face_normal = face.normalAt(0, 0)
        if round(face_normal[0]) in (-1, 1):
            x = center_of_mass[1]
            y = center_of_mass[2]
        elif round(face_normal[1]) in (-1, 1):
            x = center_of_mass[0]
            y = center_of_mass[2]
        elif round(face_normal[2]) in (-1, 1):
            x = center_of_mass[0]
            y = center_of_mass[1]
        # When edge is parallel to y-axis
        if round(Edges[0].tangentAt(0)[1]) in {1, -1}:
            if round(Edges[1].tangentAt(0)[0]) in {1, -1}:
                # Change order when edge along x-axis is at second place.
                facePRM.reverse()
        elif round(Edges[0].tangentAt(0)[2]) in {1, -1}:
            facePRM.reverse()
        facelength = facePRM[0]
        facewidth = facePRM[1]

    # When structure is not cubic. For founding parameters of given face
    # I have used bounding box.
    else:
        boundbox = face.BoundBox
        # Check that one length of bounding box is zero. Here bounding box
        # looks like a plane.
        if 0 in {round(boundbox.XLength), round(boundbox.YLength), round(boundbox.ZLength)}:
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
# Functions which is mainly used while creating stirrup.
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
# Classes and functions which are mainly used while creating Column
# Reinforcement.
# -------------------------------------------------------------------------


class _RebarGroup:
    "A Rebar Group object."

    def __init__(self, obj_name):
        self.Type = "RebarGroup"
        self.rebar_group = FreeCAD.ActiveDocument.addObject(
            "App::DocumentObjectGroupPython", obj_name
        )
        self.ties_group = self.rebar_group.newObject(
            "App::DocumentObjectGroupPython", "Ties"
        )
        self.main_rebars_group = self.rebar_group.newObject(
            "App::DocumentObjectGroupPython", "MainRebars"
        )
        # Add properties to rebar_group object
        properties = []
        properties.append(
            ("App::PropertyLinkList", "RebarGroups", "List of rebar groups", 1)
        )
        self.setProperties(properties, self.rebar_group)
        self.rebar_group.RebarGroups = [self.ties_group, self.main_rebars_group]
        self.Object = self.rebar_group

    def execute(self, obj):
        pass

    def addTies(self, ties_list):
        """Add Ties to ties_group object."""
        if isinstance(ties_list, list):
            self.ties_group.addObjects(ties_list)
        else:
            self.ties_group.addObject(ties_list)
            ties_list = [ties_list]
        prev_ties_list = self.ties_group.Ties
        prev_ties_list.extend(ties_list)
        self.ties_group.Ties = prev_ties_list

    def addMainRebars(self, main_rebars_list):
        """Add Main Rebars to main_rebars group object."""
        self.main_rebars_group.addObjects(main_rebars_list)
        prev_main_rebars_list = self.main_rebars_group.MainRebars
        main_rebars_list.extend(prev_main_rebars_list)
        self.main_rebars_group.MainRebars = main_rebars_list

    def setProperties(self, properties, group_obj):
        for prop in properties:
            group_obj.addProperty(
                prop[0],
                prop[1],
                "RebarDialog",
                QT_TRANSLATE_NOOP("App::Property", prop[2]),
            )
            group_obj.setEditorMode(prop[1], prop[3])

    def setPropertiesValues(self, properties_values, group_obj):
        for prop in properties_values:
            setattr(group_obj, prop[0], prop[1])


class _ViewProviderRebarGroup:
    "A View Provider for the Rebar Group object."

    def __init__(self, vobj):
        vobj.Proxy = self
        self.Object = vobj.Object

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None

    def doubleClicked(self, vobj):
        from ColumnReinforcement import MainColumnReinforcement

        MainColumnReinforcement.editDialog(vobj)


def getLRebarOrientationLeftRightCover(
    hook_orientation,
    hook_extension,
    hook_extend_along,
    l_cover_of_tie,
    r_cover_of_tie,
    t_cover_of_tie,
    b_cover_of_tie,
    dia_of_tie,
    dia_of_rebars,
    rounding_of_rebars,
    face_length,
):
    """getLRebarOrientationLeftRightCover(HookOrientation, HookExtension,
    HookExtendAlong, LeftCoverOfTie, RightCoverOfTie, TopCoverOfTie,
    BottomCoverOfTie, DiameterOfTie, DiameterOfRebars, RoundingOfRebars,
    FaceLength):
    Return orientation and left and right cover of LShapeRebar in the form of
    dictionary of list.
    It takes eight different orientations input for LShapeHook i.e. 'Top
    Inside', 'Top Outside', 'Bottom Inside', 'Bottom Outside', 'Top Right',
    'Top Left', 'Bottom Right', 'Bottom Left'.
    It takes two different inputs for hook_extend_along i.e. 'x-axis', 'y-axis'.
    """
    if hook_extend_along == "y-axis":
        # Swap values of covers
        l_cover_of_tie, b_cover_of_tie = b_cover_of_tie, l_cover_of_tie
        r_cover_of_tie, t_cover_of_tie = t_cover_of_tie, r_cover_of_tie
    l_cover = []
    r_cover = []
    l_cover.append(l_cover_of_tie + dia_of_tie)
    if hook_orientation in ("Top Inside", "Bottom Inside"):
        # Assign orientation value
        if hook_orientation == "Top Inside":
            list_orientation = ["Top Left", "Top Right"]
        else:
            list_orientation = ["Bottom Left", "Bottom Right"]
        r_cover.append(
            face_length
            - l_cover_of_tie
            - dia_of_tie
            - dia_of_rebars / 2
            - rounding_of_rebars * dia_of_rebars
            - hook_extension
        )
        l_cover.append(
            face_length
            - r_cover_of_tie
            - dia_of_tie
            - dia_of_rebars / 2
            - rounding_of_rebars * dia_of_rebars
            - hook_extension
        )

    elif hook_orientation in ("Top Outside", "Bottom Outside"):
        if hook_orientation == "Top Outside":
            list_orientation = ["Top Left", "Top Right"]
        else:
            list_orientation = ["Bottom Left", "Bottom Right"]
        r_cover.append(
            face_length
            - l_cover_of_tie
            - dia_of_tie
            - dia_of_rebars / 2
            + rounding_of_rebars * dia_of_rebars
            + hook_extension
        )
        l_cover.append(
            face_length
            - r_cover_of_tie
            - dia_of_tie
            - dia_of_rebars / 2
            + rounding_of_rebars * dia_of_rebars
            + hook_extension
        )

    elif hook_orientation in ("Top Left", "Bottom Left"):
        if hook_orientation == "Top Left":
            list_orientation = ["Top Left", "Top Right"]
        else:
            list_orientation = ["Bottom Left", "Bottom Right"]
        r_cover.append(
            face_length
            - l_cover_of_tie
            - dia_of_tie
            - dia_of_rebars / 2
            + rounding_of_rebars * dia_of_rebars
            + hook_extension
        )
        l_cover.append(
            face_length
            - r_cover_of_tie
            - dia_of_tie
            - dia_of_rebars / 2
            - rounding_of_rebars * dia_of_rebars
            - hook_extension
        )

    elif hook_orientation in ("Top Right", "Bottom Right"):
        if hook_orientation == "Top Right":
            list_orientation = ["Top Left", "Top Right"]
        else:
            list_orientation = ["Bottom Left", "Bottom Right"]
        r_cover.append(
            face_length
            - l_cover_of_tie
            - dia_of_tie
            - dia_of_rebars / 2
            - rounding_of_rebars * dia_of_rebars
            - hook_extension
        )
        l_cover.append(
            face_length
            - r_cover_of_tie
            - dia_of_tie
            - dia_of_rebars / 2
            + rounding_of_rebars * dia_of_rebars
            + hook_extension
        )

    r_cover.append(r_cover_of_tie + dia_of_tie)
    l_rebar_orientation_cover = {}
    l_rebar_orientation_cover["list_orientation"] = list_orientation
    l_rebar_orientation_cover["l_cover"] = l_cover
    l_rebar_orientation_cover["r_cover"] = r_cover
    return l_rebar_orientation_cover


def getFacenameforRebar(hook_extend_along, facename, structure):
    """getFacenameforRebar(HookExtendAlong, Facename, Structure):
    Return facename of face normal to selected/provided face
    It takes two different inputs for hook_extend_along i.e. 'x-axis', 'y-axis'.
    """
    face = structure.Shape.Faces[getFaceNumber(facename) - 1]
    normal1 = face.normalAt(0, 0)
    faces = structure.Shape.Faces
    index = 1
    for face in faces:
        normal2 = face.normalAt(0, 0)
        if hook_extend_along == "x-axis":
            if (
                int(normal1.dot(normal2)) == 0
                and int(normal1.cross(normal2).x) == 1
            ):
                facename_for_rebars = "Face" + str(index)
                break
        else:
            if (
                int(normal1.dot(normal2)) == 0
                and int(normal1.cross(normal2).y) == 1
            ):
                facename_for_rebars = "Face" + str(index)
                break
        index += 1
    return facename_for_rebars


# -------------------------------------------------------------------------
# Classes and functions which are mainly used while creating Beam Reinforcement.
# -------------------------------------------------------------------------


class _BeamReinforcementGroup:
    "A Beam Reinforcement Group object."

    def __init__(self):
        self.Type = "BeamReinforcementGroup"
        self.rebar_group = FreeCAD.ActiveDocument.addObject(
            "App::DocumentObjectGroupPython", "BeamReinforcement"
        )
        self.stirrups_group = self.rebar_group.newObject(
            "App::DocumentObjectGroupPython", "Stirrups"
        )
        self.top_reinforcement_group = self.rebar_group.newObject(
            "App::DocumentObjectGroupPython", "TopReinforcement"
        )
        self.bottom_reinforcement_group = self.rebar_group.newObject(
            "App::DocumentObjectGroupPython", "BottomReinforcement"
        )
        self.shear_reinforcement_group = self.rebar_group.newObject(
            "App::DocumentObjectGroupPython", "ShearReinforcement"
        )
        self.left_rebars_group = self.shear_reinforcement_group.newObject(
            "App::DocumentObjectGroupPython", "LeftRebars"
        )
        self.right_rebars_group = self.shear_reinforcement_group.newObject(
            "App::DocumentObjectGroupPython", "RightRebars"
        )
        # Add properties to rebar_group object
        properties = []
        properties.append(
            (
                "App::PropertyLinkList",
                "ReinforcementGroups",
                "List of reinforcement groups",
                1,
            )
        )
        self.setProperties(properties, self.rebar_group)
        self.rebar_group.ReinforcementGroups = [
            self.stirrups_group,
            self.top_reinforcement_group,
            self.bottom_reinforcement_group,
            self.shear_reinforcement_group,
        ]
        # Add properties to stirrups_group object
        properties = []
        properties.append(
            ("App::PropertyLinkList", "Stirrups", "List of Stirrups", 1)
        )
        self.setProperties(properties, self.stirrups_group)
        # Add properties to top_reinforcement_group object
        properties = []
        properties.append(
            (
                "App::PropertyLinkList",
                "TopRebars",
                "List of top reinforcement rebars",
                1,
            )
        )
        self.setProperties(properties, self.top_reinforcement_group)
        # Add properties to bottom_reinforcement_group object
        properties = []
        properties.append(
            (
                "App::PropertyLinkList",
                "BottomRebars",
                "List of bottom reinforcement rebars",
                1,
            )
        )
        self.setProperties(properties, self.bottom_reinforcement_group)
        # Add properties to shear_reinforcement_group object
        properties = []
        properties.append(
            (
                "App::PropertyLinkList",
                "ShearReinforcementGroups",
                "List of shear reinforcement groups",
                1,
            )
        )
        self.setProperties(properties, self.shear_reinforcement_group)
        self.shear_reinforcement_group.ShearReinforcementGroups = [
            self.left_rebars_group,
            self.right_rebars_group,
        ]
        # Add properties to left_rebars_group object
        properties = []
        properties.append(
            (
                "App::PropertyLinkList",
                "LeftRebars",
                "List of shear reinforcement left rebars",
                1,
            )
        )
        self.setProperties(properties, self.left_rebars_group)
        # Add properties to right_rebars_group object
        properties = []
        properties.append(
            (
                "App::PropertyLinkList",
                "RightRebars",
                "List of shear reinforcement right rebars",
                1,
            )
        )
        self.setProperties(properties, self.right_rebars_group)
        self.Object = self.rebar_group

    def execute(self, obj):
        pass

    def addStirrups(self, stirrups_list):
        """Add Stirrups to stirrups_group object."""
        if isinstance(stirrups_list, list):
            self.stirrups_group.addObjects(stirrups_list)
        else:
            self.stirrups_group.addObject(stirrups_list)
            stirrups_list = [stirrups_list]
        prev_stirrups_list = self.stirrups_group.Stirrups
        prev_stirrups_list.extend(stirrups_list)
        self.stirrups_group.Stirrups = prev_stirrups_list

    def addTopRebars(self, top_rebars_list):
        """Add top reinforcement rebars to top_reinforcement_group object."""
        self.top_reinforcement_group.addObjects(top_rebars_list)
        prev_top_rebars_list = self.top_reinforcement_group.TopRebars
        prev_top_rebars_list.extend(top_rebars_list)
        self.top_reinforcement_group.TopRebars = prev_top_rebars_list

    def addBottomRebars(self, bottom_rebars_list):
        """Add bottom reinforcement rebars to bottom_reinforcement_group
        object."""
        self.bottom_reinforcement_group.addObjects(bottom_rebars_list)
        prev_bottom_rebars_list = self.bottom_reinforcement_group.BottomRebars
        prev_bottom_rebars_list.extend(bottom_rebars_list)
        self.bottom_reinforcement_group.BottomRebars = prev_bottom_rebars_list

    def addLeftRebars(self, left_rebars_list):
        """Add left reinforcement rebars to left_reinforcement_group object."""
        self.left_reinforcement_group.addObjects(left_rebars_list)
        prev_left_rebars_list = self.left_reinforcement_group.LeftRebars
        prev_left_rebars_list.extend(left_rebars_list)
        self.left_reinforcement_group.LeftRebars = prev_left_rebars_list

    def addRightRebars(self, right_rebars_list):
        """Add right reinforcement rebars to right_reinforcement_group
        object."""
        self.right_reinforcement_group.addObjects(right_rebars_list)
        prev_right_rebars_list = self.right_reinforcement_group.RightRebars
        prev_right_rebars_list.extend(right_rebars_list)
        self.right_reinforcement_group.RightRebars = prev_right_rebars_list

    def setProperties(self, properties, group_obj):
        for prop in properties:
            group_obj.addProperty(
                prop[0],
                prop[1],
                "RebarDialog",
                QT_TRANSLATE_NOOP("App::Property", prop[2]),
            )
            group_obj.setEditorMode(prop[1], prop[3])

    def setPropertiesValues(self, properties_values, group_obj):
        for prop in properties_values:
            setattr(group_obj, prop[0], prop[1])


def getFacenamesforBeamReinforcement(facename, structure):
    """getFacenamesforBeamReinforcement(Facename, Structure):
    Return tuple of facenames of faces normal to selected/provided face to
    create straight/lshaped rebars.
    """
    face = structure.Shape.Faces[getFaceNumber(facename) - 1]
    normal1 = face.normalAt(0, 0)
    faces = structure.Shape.Faces
    index = 1
    for face in faces:
        normal2 = face.normalAt(0, 0)
        if (
            int(normal1.dot(normal2)) == 0
            and int(normal1.cross(normal2).z) == -1
        ):
            facename_for_tb_rebars = "Face" + str(index)
        if (
            int(normal1.dot(normal2)) == 0
            and int(normal1.cross(normal2).y) == 1
        ):
            facename_for_s_rebars = "Face" + str(index)
        index += 1
    return (facename_for_tb_rebars, facename_for_s_rebars)


def getdictofNumberDiameterOffset(number_diameter_offset_tuple):
    """getdictofNumberDiameterOffset(NumberDiameterOffsetTuple):
    This function take input in specific syntax and return output in the form of
    dictionary. For eg.
    Input: ("2#20@50+3#16@100+2#20@50", "1#18@30+2#14@30+1#18@30")
    Output: {
                'layer1': [(2, 20, 50), (3, 16, 100), (2, 20, 50)],
                'layer2': [(1, 18, 30), (2, 14, 30), (1, 18, 30)],
            }
    """
    number_diameter_offset_dict = {}
    for i, number_diameter_offset_string in enumerate(
        number_diameter_offset_tuple
    ):
        number_diameter_offset_dict[
            "layer" + str(i + 1)
        ] = gettupleOfNumberDiameterOffset(number_diameter_offset_string)
    return number_diameter_offset_dict


def gettupleOfNumberDiameterOffset(number_diameter_offset_string):
    """gettupleOfNumberDiameterOffset(NumberDiameterOffsetString):
    This function take input in specific syntax and return output in the form of
    tuple. For eg.
    Input: "2#20@50+3#16@100+2#20@50"
    Output: [(2, 20, 50), (3, 16, 100), (2, 20, 50)]
    """
    import re

    number_diameter_offset_st = number_diameter_offset_string.strip()
    number_diameter_offset_sp = number_diameter_offset_st.split("+")
    index = 0
    number_diameter_offset_list = []
    while index < len(number_diameter_offset_sp):
        # Find "#" and "@" recursively in number_diameter_offset_sp array.
        in_sp = re.split("#|@", number_diameter_offset_sp[index])
        number_diameter_offset_list.append(
            (
                int(in_sp[0]),
                float(in_sp[1].replace("mm", "")),
                float(in_sp[2].replace("mm", "")),
            )
        )
        index += 1
    return number_diameter_offset_list


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
    msg.setText(translate("RebarAddon", message))
    msg.setStandardButtons(QtGui.QMessageBox.Ok)
    msg.exec_()

# Qt tanslation handling
def translate(context, text, disambig=None):
    return QtCore.QCoreApplication.translate(context, text, disambig)


def print_in_freecad_console(*msg):
    """ Print given arguments on FreeCAD console."""
    s = ''
    for m in msg:
        s += str(m) + ', '
    FreeCAD.Console.PrintMessage(str(s) + '\n')
