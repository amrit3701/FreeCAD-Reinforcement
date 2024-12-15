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

import math
from pathlib import Path

import ArchCommands
import FreeCAD
import FreeCADGui
from PySide import QtGui
from PySide.QtCore import QT_TRANSLATE_NOOP

from PopUpImage import showPopUpImageDialog
from RebarData import RebarTypes
from RebarDistribution import runRebarDistribution, removeRebarDistribution
from Rebarfunc import (
    getSelectedFace,
    getFaceNumber,
    getParametersOfFace,
    showWarning,
    check_selected_face,
    extendedTangentLength,
    extendedTangentPartLength,
    get_rebar_amount_from_spacing,
)


def getpointsOfStirrup(
    FacePRM,
    l_cover,
    r_cover,
    t_cover,
    b_cover,
    bentAngle,
    bentFactor,
    diameter,
    rounding,
    facenormal,
):
    """getpointsOfStirrup(FacePRM, LeftCover, RightCover, TopCover,
    BottomCover, BentAngle, BentFactor, Diameter, Rounding, FaceNormal):
    Return the coordinates points of the Stirrup in the form of array."""
    l_cover += diameter / 2
    r_cover += diameter / 2
    t_cover += diameter / 2
    b_cover += diameter / 2
    angle = 180 - bentAngle
    tangent_part_length = extendedTangentPartLength(rounding, diameter, angle)
    tangent_length = extendedTangentLength(rounding, diameter, angle)
    if round(facenormal[0]) in {1, -1}:
        x1 = FacePRM[1][0]
        y1 = FacePRM[1][1] - FacePRM[0][0] / 2 + l_cover
        z1 = FacePRM[1][2] + FacePRM[0][1] / 2 - t_cover + tangent_part_length
        y2 = FacePRM[1][1] - FacePRM[0][0] / 2 + l_cover
        z2 = FacePRM[1][2] - FacePRM[0][1] / 2 + b_cover
        y3 = FacePRM[1][1] + FacePRM[0][0] / 2 - r_cover
        z3 = FacePRM[1][2] - FacePRM[0][1] / 2 + b_cover
        y4 = FacePRM[1][1] + FacePRM[0][0] / 2 - r_cover
        z4 = FacePRM[1][2] + FacePRM[0][1] / 2 - t_cover
        y5 = FacePRM[1][1] - FacePRM[0][0] / 2 + l_cover - tangent_part_length
        z5 = FacePRM[1][2] + FacePRM[0][1] / 2 - t_cover
        side_length = abs(y5 - y4) - tangent_part_length
        normal_dis = (
            diameter * (side_length + tangent_part_length)
        ) / side_length
        x2 = x1 - normal_dis / 4
        x3 = x2 - normal_dis / 4
        x4 = x3 - normal_dis / 4
        x5 = x4 - normal_dis / 4
        x0 = x1 + normal_dis / 4
        y0 = y1 + (tangent_length + bentFactor * diameter) * math.sin(
            math.radians(angle)
        )
        z0 = z1 - (tangent_length + bentFactor * diameter) * math.cos(
            math.radians(angle)
        )
        x6 = x5 - normal_dis / 4
        y6 = y5 + (tangent_length + bentFactor * diameter) * math.sin(
            math.radians(90 - angle)
        )
        z6 = z5 - (tangent_length + bentFactor * diameter) * math.cos(
            math.radians(90 - angle)
        )
    elif round(facenormal[1]) in {1, -1}:
        x1 = FacePRM[1][0] - FacePRM[0][0] / 2 + l_cover
        y1 = FacePRM[1][1]
        z1 = FacePRM[1][2] + FacePRM[0][1] / 2 - t_cover + tangent_part_length
        x2 = FacePRM[1][0] - FacePRM[0][0] / 2 + l_cover
        z2 = FacePRM[1][2] - FacePRM[0][1] / 2 + b_cover
        x3 = FacePRM[1][0] + FacePRM[0][0] / 2 - r_cover
        z3 = FacePRM[1][2] - FacePRM[0][1] / 2 + b_cover
        x4 = FacePRM[1][0] + FacePRM[0][0] / 2 - r_cover
        z4 = FacePRM[1][2] + FacePRM[0][1] / 2 - t_cover
        x5 = FacePRM[1][0] - FacePRM[0][0] / 2 + l_cover - tangent_part_length
        z5 = FacePRM[1][2] + FacePRM[0][1] / 2 - t_cover
        side_length = abs(x5 - x4) - tangent_part_length
        normal_dis = (
            diameter * (side_length + tangent_part_length)
        ) / side_length
        y2 = y1 - normal_dis / 4
        y3 = y2 - normal_dis / 4
        y4 = y3 - normal_dis / 4
        y5 = y4 - normal_dis / 4
        y0 = y1 + normal_dis / 4
        x0 = x1 + (tangent_length + bentFactor * diameter) * math.sin(
            math.radians(angle)
        )
        z0 = z1 - (tangent_length + bentFactor * diameter) * math.cos(
            math.radians(angle)
        )
        x6 = x5 + (tangent_length + bentFactor * diameter) * math.sin(
            math.radians(90 - angle)
        )
        y6 = y5 - normal_dis / 4
        z6 = z5 - (tangent_length + bentFactor * diameter) * math.cos(
            math.radians(90 - angle)
        )
    elif round(facenormal[2]) in {1, -1}:
        x1 = FacePRM[1][0] - FacePRM[0][0] / 2 + l_cover
        y1 = FacePRM[1][1] + FacePRM[0][1] / 2 - t_cover + tangent_part_length
        z1 = FacePRM[1][2]
        x2 = FacePRM[1][0] - FacePRM[0][0] / 2 + l_cover
        y2 = FacePRM[1][1] - FacePRM[0][1] / 2 + b_cover
        x3 = FacePRM[1][0] + FacePRM[0][0] / 2 - r_cover
        y3 = FacePRM[1][1] - FacePRM[0][1] / 2 + b_cover
        x4 = FacePRM[1][0] + FacePRM[0][0] / 2 - r_cover
        y4 = FacePRM[1][1] + FacePRM[0][1] / 2 - t_cover
        x5 = FacePRM[1][0] - FacePRM[0][0] / 2 + l_cover - tangent_part_length
        y5 = FacePRM[1][1] + FacePRM[0][1] / 2 - t_cover
        side_length = abs(x5 - x4) - tangent_part_length
        normal_dis = (
            diameter * (side_length + tangent_part_length)
        ) / side_length
        z2 = z1 - normal_dis / 4
        z3 = z2 - normal_dis / 4
        z4 = z3 - normal_dis / 4
        z5 = z4 - normal_dis / 4
        z0 = z1 + normal_dis / 4
        x0 = x1 + (tangent_length + bentFactor * diameter) * math.sin(
            math.radians(angle)
        )
        y0 = y1 - (tangent_length + bentFactor * diameter) * math.cos(
            math.radians(angle)
        )
        x6 = x5 + (tangent_length + bentFactor * diameter) * math.sin(
            math.radians(90 - angle)
        )
        y6 = y5 - (tangent_length + bentFactor * diameter) * math.cos(
            math.radians(90 - angle)
        )
        z6 = z5 - normal_dis / 4
    return [
        FreeCAD.Vector(x0, y0, z0),
        FreeCAD.Vector(x1, y1, z1),
        FreeCAD.Vector(x2, y2, z2),
        FreeCAD.Vector(x3, y3, z3),
        FreeCAD.Vector(x4, y4, z4),
        FreeCAD.Vector(x5, y5, z5),
        FreeCAD.Vector(x6, y6, z6),
    ]


class _StirrupTaskPanel:
    def __init__(self, Rebar=None):
        if not Rebar:
            self.CustomSpacing = None
            selected_obj = FreeCADGui.Selection.getSelectionEx()[0]
            self.SelectedObj = selected_obj.Object
            self.FaceName = selected_obj.SubElementNames[0]
        else:
            self.CustomSpacing = Rebar.CustomSpacing
            if hasattr(Rebar.Base, "Support"):
                self.FaceName = Rebar.Base.Support[0][1][0]
                self.SelectedObj = Rebar.Base.Support[0][0]
            else:
                self.FaceName = Rebar.Base.AttachmentSupport[0][1][0]
                self.SelectedObj = Rebar.Base.AttachmentSupport[0][0]
        self.form = FreeCADGui.PySideUic.loadUi(
            str(Path(__file__).with_suffix(".ui"))
        )
        self.form.setWindowTitle(
            QtGui.QApplication.translate("RebarAddon", "Stirrup Rebar", None)
        )
        self.form.bentAngle.addItems(["135", "90"])
        self.form.amount_radio.clicked.connect(self.amount_radio_clicked)
        self.form.spacing_radio.clicked.connect(self.spacing_radio_clicked)
        self.form.image.setPixmap(
            QtGui.QPixmap(str(Path(__file__).parent / "icons" / "Stirrup.svg"))
        )
        self.form.customSpacing.clicked.connect(
            lambda: runRebarDistribution(self)
        )
        self.form.removeCustomSpacing.clicked.connect(
            lambda: removeRebarDistribution(self)
        )
        self.form.PickSelectedFace.clicked.connect(
            lambda: getSelectedFace(self)
        )
        # self.form.toolButton.setIcon(
        #     self.form.toolButton.style().standardIcon(
        #         QtGui.QStyle.SP_DialogHelpButton
        #     )
        # )
        self.form.toolButton.clicked.connect(
            lambda: showPopUpImageDialog(
                str(Path(__file__).parent / "icons" / "StirrupDetailed.svg")
            )
        )
        self.Rebar = Rebar

    @staticmethod
    def getStandardButtons():
        return (
            int(QtGui.QDialogButtonBox.Ok)
            | int(QtGui.QDialogButtonBox.Apply)
            | int(QtGui.QDialogButtonBox.Cancel)
        )

    def clicked(self, button):
        if button == int(QtGui.QDialogButtonBox.Apply):
            self.accept(button)

    def accept(self, signal=None):
        l_cover = self.form.l_sideCover.text()
        l_cover = FreeCAD.Units.Quantity(l_cover).Value
        r_cover = self.form.r_sideCover.text()
        r_cover = FreeCAD.Units.Quantity(r_cover).Value
        t_cover = self.form.t_sideCover.text()
        t_cover = FreeCAD.Units.Quantity(t_cover).Value
        b_cover = self.form.b_sideCover.text()
        b_cover = FreeCAD.Units.Quantity(b_cover).Value
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
                rebar = makeStirrup(
                    l_cover,
                    r_cover,
                    t_cover,
                    b_cover,
                    f_cover,
                    bentAngle,
                    bentFactor,
                    diameter,
                    rounding,
                    True,
                    amount,
                    self.SelectedObj,
                    self.FaceName,
                )
            elif spacing_check:
                spacing = self.form.spacing.text()
                spacing = FreeCAD.Units.Quantity(spacing).Value
                rebar = makeStirrup(
                    l_cover,
                    r_cover,
                    t_cover,
                    b_cover,
                    f_cover,
                    bentAngle,
                    bentFactor,
                    diameter,
                    rounding,
                    False,
                    spacing,
                    self.SelectedObj,
                    self.FaceName,
                )
        else:
            if amount_check:
                amount = self.form.amount.value()
                rebar = editStirrup(
                    self.Rebar,
                    l_cover,
                    r_cover,
                    t_cover,
                    b_cover,
                    f_cover,
                    bentAngle,
                    bentFactor,
                    diameter,
                    rounding,
                    True,
                    amount,
                    self.SelectedObj,
                    self.FaceName,
                )
            elif spacing_check:
                spacing = self.form.spacing.text()
                spacing = FreeCAD.Units.Quantity(spacing).Value
                rebar = editStirrup(
                    self.Rebar,
                    l_cover,
                    r_cover,
                    t_cover,
                    b_cover,
                    f_cover,
                    bentAngle,
                    bentFactor,
                    diameter,
                    rounding,
                    False,
                    spacing,
                    self.SelectedObj,
                    self.FaceName,
                )
        if self.CustomSpacing:
            rebar.CustomSpacing = self.CustomSpacing
            FreeCAD.ActiveDocument.recompute()
        self.Rebar = rebar
        if signal == int(QtGui.QDialogButtonBox.Apply):
            pass
        else:
            FreeCADGui.Control.closeDialog()

    def amount_radio_clicked(self):
        self.form.spacing.setEnabled(False)
        self.form.amount.setEnabled(True)

    def spacing_radio_clicked(self):
        self.form.amount.setEnabled(False)
        self.form.spacing.setEnabled(True)


def makeStirrup(
    l_cover,
    r_cover,
    t_cover,
    b_cover,
    f_cover,
    bentAngle,
    bentFactor,
    diameter,
    rounding,
    amount_spacing_check,
    amount_spacing_value,
    structure=None,
    facename=None,
):
    """makeStirrup(LeftCover, RightCover, TopCover, BottomCover, FrontCover,
    BentAngle, BentFactor, Diameter, Rounding, AmountSpacingCheck,
    AmountSpacingValue, Structure, Facename):
    Adds the Stirrup reinforcement bar to the selected structural object."""
    if not structure and not facename:
        selected_obj = FreeCADGui.Selection.getSelectionEx()[0]
        structure = selected_obj.Object
        facename = selected_obj.SubElementNames[0]
    face = structure.Shape.Faces[getFaceNumber(facename) - 1]
    # StructurePRM = getTrueParametersOfStructure(structure)
    FacePRM = getParametersOfFace(structure, facename, False)
    FaceNormal = face.normalAt(0, 0)
    # FaceNormal = face.Placement.Rotation.inverted().multVec(FaceNormal)
    if not FacePRM:
        FreeCAD.Console.PrintError(
            "Cannot identify shape or from which base object structural "
            "element is derived\n"
        )
        return
    # Calculate the coordinate values of Stirrup
    points = getpointsOfStirrup(
        FacePRM,
        l_cover,
        r_cover,
        t_cover,
        b_cover,
        bentAngle,
        bentFactor,
        diameter,
        rounding,
        FaceNormal,
    )
    import Draft

    line = Draft.makeWire(points, closed=False, face=True, support=None)
    import Arch

    if hasattr(line, "Support"):
        line.Support = [(structure, facename)]
    else:
        line.AttachmentSupport = [(structure, facename)]
    if amount_spacing_check:
        rebar = Arch.makeRebar(
            structure,
            line,
            diameter,
            amount_spacing_value,
            f_cover + diameter / 2,
            name="Stirrup",
        )
    else:
        size = (
            ArchCommands.projectToVector(
                structure.Shape.copy(), face.normalAt(0, 0)
            )
        ).Length
        rebar = Arch.makeRebar(
            structure,
            line,
            diameter,
            get_rebar_amount_from_spacing(size, diameter, amount_spacing_value),
            f_cover + diameter / 2,
            name="Stirrup",
        )
    rebar.Direction = FaceNormal.negative()
    rebar.Rounding = rounding
    # Adds properties to the rebar object
    rebar.addProperty(
        "App::PropertyEnumeration",
        "RebarShape",
        "RebarDialog",
        QT_TRANSLATE_NOOP("App::Property", "Shape of rebar"),
    ).RebarShape = RebarTypes.tolist()
    rebar.RebarShape = "Stirrup"
    rebar.setEditorMode("RebarShape", 2)
    rebar.addProperty(
        "App::PropertyDistance",
        "LeftCover",
        "RebarDialog",
        QT_TRANSLATE_NOOP("App::Property", "Left Side cover of rebar"),
    ).LeftCover = l_cover
    rebar.setEditorMode("LeftCover", 2)
    rebar.addProperty(
        "App::PropertyDistance",
        "RightCover",
        "RebarDialog",
        QT_TRANSLATE_NOOP("App::Property", "Right Side cover of rebar"),
    ).RightCover = r_cover
    rebar.setEditorMode("RightCover", 2)
    rebar.addProperty(
        "App::PropertyDistance",
        "TopCover",
        "RebarDialog",
        QT_TRANSLATE_NOOP("App::Property", "Top Side cover of rebar"),
    ).TopCover = t_cover
    rebar.setEditorMode("TopCover", 2)
    rebar.addProperty(
        "App::PropertyDistance",
        "BottomCover",
        "RebarDialog",
        QT_TRANSLATE_NOOP("App::Property", "Bottom Side cover of rebar"),
    ).BottomCover = b_cover
    rebar.setEditorMode("BottomCover", 2)
    rebar.addProperty(
        "App::PropertyDistance",
        "FrontCover",
        "RebarDialog",
        QT_TRANSLATE_NOOP("App::Property", "Top cover of rebar"),
    ).FrontCover = f_cover
    rebar.setEditorMode("FrontCover", 2)
    rebar.addProperty(
        "App::PropertyInteger",
        "BentAngle",
        "RebarDialog",
        QT_TRANSLATE_NOOP(
            "App::Property", "Bent angle between at the end of rebar"
        ),
    ).BentAngle = bentAngle
    rebar.setEditorMode("BentAngle", 2)
    rebar.addProperty(
        "App::PropertyInteger",
        "BentFactor",
        "RebarDialog",
        QT_TRANSLATE_NOOP(
            "App::Property", "Bent Length is the equal to BentFactor * Diameter"
        ),
    ).BentFactor = bentFactor
    rebar.setEditorMode("BentFactor", 2)
    rebar.addProperty(
        "App::PropertyBool",
        "AmountCheck",
        "RebarDialog",
        QT_TRANSLATE_NOOP("App::Property", "Amount radio button is checked"),
    )
    rebar.setEditorMode("AmountCheck", 2)
    rebar.addProperty(
        "App::PropertyDistance",
        "TrueSpacing",
        "RebarDialog",
        QT_TRANSLATE_NOOP("App::Property", "Spacing between of rebars"),
    ).TrueSpacing = amount_spacing_value
    rebar.setEditorMode("TrueSpacing", 2)
    if amount_spacing_check:
        rebar.AmountCheck = True
    else:
        rebar.AmountCheck = False
        rebar.TrueSpacing = amount_spacing_value
    FreeCAD.ActiveDocument.recompute()
    return rebar


def editStirrup(
    Rebar,
    l_cover,
    r_cover,
    t_cover,
    b_cover,
    f_cover,
    bentAngle,
    bentFactor,
    diameter,
    rounding,
    amount_spacing_check,
    amount_spacing_value,
    structure=None,
    facename=None,
):
    sketch = Rebar.Base
    if structure and facename:
        if hasattr(sketch, "Support"):
            sketch.Support = [(structure, facename)]
        else:
            sketch.AttachmentSupport = [(structure, facename)]
    # Check if sketch support is empty.
    if hasattr(sketch, "Support"):
        if not sketch.Support:
            showWarning(
                "You have checked: 'Remove external geometry of base sketches when "
                "needed.'\nTo uncheck: Edit->Preferences->Arch."
            )
            return
    else:
        if not sketch.AttachmentSupport:
            showWarning(
                "You have checked: 'Remove external geometry of base sketches when "
                "needed.'\nTo uncheck: Edit->Preferences->BIM."
            )
            return
    # Assigned values
    if hasattr(sketch, "Support"):
        facename = sketch.Support[0][1][0]
        structure = sketch.Support[0][0]
    else:
        facename = sketch.AttachmentSupport[0][1][0]
        structure = sketch.AttachmentSupport[0][0]
    face = structure.Shape.Faces[getFaceNumber(facename) - 1]
    # StructurePRM = getTrueParametersOfStructure(structure)
    # Get parameters of the face where sketch of rebar is drawn
    FacePRM = getParametersOfFace(structure, facename, False)
    FaceNormal = face.normalAt(0, 0)
    # FaceNormal = face.Placement.Rotation.inverted().multVec(FaceNormal)
    # Calculate the coordinates value of Stirrup rebar
    points = getpointsOfStirrup(
        FacePRM,
        l_cover,
        r_cover,
        t_cover,
        b_cover,
        bentAngle,
        bentFactor,
        diameter,
        rounding,
        FaceNormal,
    )
    Rebar.Base.Points = points
    FreeCAD.ActiveDocument.recompute()
    Rebar.Direction = FaceNormal.negative()
    Rebar.OffsetStart = f_cover + diameter / 2
    Rebar.OffsetEnd = f_cover + diameter / 2
    Rebar.BentAngle = bentAngle
    Rebar.BentFactor = bentFactor
    Rebar.Rounding = rounding
    Rebar.Diameter = diameter
    if amount_spacing_check:
        Rebar.Amount = amount_spacing_value
        FreeCAD.ActiveDocument.recompute()
        Rebar.AmountCheck = True
    else:
        size = (
            ArchCommands.projectToVector(
                structure.Shape.copy(), face.normalAt(0, 0)
            )
        ).Length
        Rebar.Amount = get_rebar_amount_from_spacing(
            size, diameter, amount_spacing_value
        )
        FreeCAD.ActiveDocument.recompute()
        Rebar.AmountCheck = False
    Rebar.FrontCover = f_cover
    Rebar.LeftCover = l_cover
    Rebar.RightCover = r_cover
    Rebar.TopCover = t_cover
    Rebar.BottomCover = b_cover
    Rebar.TrueSpacing = amount_spacing_value
    FreeCAD.ActiveDocument.recompute()
    return Rebar


def editDialog(vobj):
    FreeCADGui.Control.closeDialog()
    obj = _StirrupTaskPanel(vobj.Object)
    obj.form.frontCover.setText(
        FreeCAD.Units.Quantity(
            vobj.Object.FrontCover, FreeCAD.Units.Length
        ).UserString
    )
    obj.form.l_sideCover.setText(
        FreeCAD.Units.Quantity(
            vobj.Object.LeftCover, FreeCAD.Units.Length
        ).UserString
    )
    obj.form.r_sideCover.setText(
        FreeCAD.Units.Quantity(
            vobj.Object.RightCover, FreeCAD.Units.Length
        ).UserString
    )
    obj.form.t_sideCover.setText(
        FreeCAD.Units.Quantity(
            vobj.Object.TopCover, FreeCAD.Units.Length
        ).UserString
    )
    obj.form.b_sideCover.setText(
        FreeCAD.Units.Quantity(
            vobj.Object.BottomCover, FreeCAD.Units.Length
        ).UserString
    )
    obj.form.diameter.setText(
        FreeCAD.Units.Quantity(
            vobj.Object.Diameter, FreeCAD.Units.Length
        ).UserString
    )
    obj.form.bentAngle.setCurrentIndex(
        obj.form.bentAngle.findText(str(vobj.Object.BentAngle))
    )
    obj.form.bentFactor.setValue(vobj.Object.BentFactor)
    obj.form.rounding.setValue(vobj.Object.Rounding)
    if vobj.Object.AmountCheck:
        obj.form.amount.setValue(vobj.Object.Amount)
    else:
        obj.form.amount_radio.setChecked(False)
        obj.form.spacing_radio.setChecked(True)
        obj.form.amount.setDisabled(True)
        obj.form.spacing.setEnabled(True)
        obj.form.spacing.setText(
            FreeCAD.Units.Quantity(
                vobj.Object.TrueSpacing, FreeCAD.Units.Length
            ).UserString
        )
    # obj.form.PickSelectedFace.setVisible(False)
    FreeCADGui.Control.showDialog(obj)


def CommandStirrup():
    selected_obj = check_selected_face()
    if selected_obj:
        FreeCADGui.Control.showDialog(_StirrupTaskPanel())
