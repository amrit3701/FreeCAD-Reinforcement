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

from pathlib import Path
from typing import Tuple, List

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
    facenormalDirection,
    get_rebar_amount_from_spacing,
)


# TODO: Use(Uncomment) typing.Literal for minimum python3.8


def getpointsOfStraightRebar(
    FacePRM: Tuple[Tuple[float, float], Tuple[float, float]],
    rt_cover: float,
    lb_cover: float,
    # coverAlong: Tuple[
    #     Literal["Bottom Side", "Top Side", "Left Side", "Right Side"], float
    # ],
    coverAlong: Tuple[str, float],
    # orientation: Literal["Horizontal", "Vertical"],
    orientation: str,
    diameter: float,
    face_normal: FreeCAD.Vector,
) -> List[FreeCAD.Vector]:
    """getpointsOfStraightRebar(FacePRM, RightTopcover, LeftBottomcover,
    CoverAlong, Orientation, Diameter, FaceNormal):
    Return points of the Straight rebar in the form of array for sketch.

    Case I: When Orientation is 'Horizontal':
        We have two option in CoverAlong i.e. 'Bottom Side' or 'Top Side'
    Case II: When Orientation is 'Vertical':
        We have two option in CoverAlong i.e. 'Left Side' or 'Right Side'
    """
    center_x = FacePRM[1][0]
    center_y = FacePRM[1][1]
    # When Left/Rear Face of structure is selected
    if round(face_normal[0]) == -1 or round(face_normal[1]) == 1:
        center_x = -center_x
    # When Bottom Face of structure is selected
    elif round(face_normal[2]) == -1:
        center_y = -center_y
    if orientation == "Horizontal":
        if coverAlong[0] == "Bottom Side":
            cover = coverAlong[1] + diameter / 2
            x1 = center_x - FacePRM[0][0] / 2 + lb_cover
            y1 = center_y - FacePRM[0][1] / 2 + cover
            x2 = center_x + FacePRM[0][0] / 2 - rt_cover
            y2 = center_y - FacePRM[0][1] / 2 + cover
        elif coverAlong[0] == "Top Side":
            cover = FacePRM[0][1] - coverAlong[1] - diameter / 2
            x1 = center_x - FacePRM[0][0] / 2 + lb_cover
            y1 = center_y - FacePRM[0][1] / 2 + cover
            x2 = center_x + FacePRM[0][0] / 2 - rt_cover
            y2 = center_y - FacePRM[0][1] / 2 + cover
    elif orientation == "Vertical":
        if coverAlong[0] == "Left Side":
            cover = coverAlong[1] + diameter / 2
            x1 = center_x - FacePRM[0][0] / 2 + cover
            y1 = center_y - FacePRM[0][1] / 2 + lb_cover
            x2 = center_x - FacePRM[0][0] / 2 + cover
            y2 = center_y + FacePRM[0][1] / 2 - rt_cover
        elif coverAlong[0] == "Right Side":
            cover = FacePRM[0][0] - coverAlong[1] - diameter / 2
            x1 = center_x - FacePRM[0][0] / 2 + cover
            y1 = center_y - FacePRM[0][1] / 2 + lb_cover
            x2 = center_x - FacePRM[0][0] / 2 + cover
            y2 = center_y + FacePRM[0][1] / 2 - rt_cover
    return [FreeCAD.Vector(x1, y1, 0), FreeCAD.Vector(x2, y2, 0)]


class _StraightRebarTaskPanel:
    def __init__(self, Rebar=None):
        if not Rebar:
            self.CustomSpacing = None
            selected_obj = FreeCADGui.Selection.getSelectionEx()[0]
            self.SelectedObj = selected_obj.Object
            self.FaceName = selected_obj.SubElementNames[0]
        else:
            self.CustomSpacing = Rebar.CustomSpacing
            self.FaceName = Rebar.Base.Support[0][1][0]
            self.SelectedObj = Rebar.Base.Support[0][0]
        self.form = FreeCADGui.PySideUic.loadUi(
            str(Path(__file__).with_suffix(".ui"))
        )
        self.form.setWindowTitle(
            QtGui.QApplication.translate("RebarAddon", "Straight Rebar", None)
        )
        self.form.orientationValue.addItems(["Horizontal", "Vertical"])
        self.form.coverAlong.addItems(["Bottom Side", "Top Side"])
        self.form.amount_radio.clicked.connect(self.amount_radio_clicked)
        self.form.spacing_radio.clicked.connect(self.spacing_radio_clicked)
        self.form.customSpacing.clicked.connect(
            lambda: runRebarDistribution(self)
        )
        self.form.removeCustomSpacing.clicked.connect(
            lambda: removeRebarDistribution(self)
        )
        self.form.PickSelectedFace.setCheckable(True)
        self.form.PickSelectedFace.toggle()
        self.form.PickSelectedFace.clicked.connect(
            lambda: getSelectedFace(self)
        )
        self.form.image.setPixmap(
            QtGui.QPixmap(
                str(Path(__file__).parent / "icons" / "StraightRebarH.svg")
            )
        )
        self.form.orientationValue.currentIndexChanged.connect(
            self.changeOrientation
        )
        self.form.coverAlong.currentIndexChanged.connect(self.changeCoverAlong)
        # help_button = QtWidgets.QStyle()
        # self.form.toolButton.setIcon(
        #     self.form.toolButton.style().standardIcon(
        #         help_button.SP_DialogHelpButton
        #     )
        # )
        # self.form.toolButton2 = QtWidgets.QToolButton()
        # self.form.toolButton2.setIcon(
        #     self.form.toolButton2.style().standardIcon(
        #         QtGui.QStyle.SP_DialogHelpButton
        #     )
        # )
        self.form.toolButton.clicked.connect(
            lambda: showPopUpImageDialog(
                str(
                    Path(__file__).parent
                    / "icons"
                    / "StraightRebarDetailed.svg"
                )
            )
        )
        self.Rebar = Rebar

    def changeOrientation(self):
        orientation = self.form.orientationValue.currentText()
        if orientation == "Horizontal":
            self.form.image.setPixmap(
                QtGui.QPixmap(
                    str(Path(__file__).parent / "icons" / "StraightRebarH.svg")
                )
            )
            self.form.r_sideCoverLabel.setText("Right Side Cover")
            self.form.l_sideCoverLabel.setText("Left Side Cover")
            self.form.coverAlong.clear()
            self.form.coverAlong.addItems(["Bottom Side", "Top Side"])
        else:
            self.form.image.setPixmap(
                QtGui.QPixmap(
                    str(Path(__file__).parent / "icons" / "StraightRebarV.svg")
                )
            )
            self.form.r_sideCoverLabel.setText("Top Side Cover")
            self.form.l_sideCoverLabel.setText("Bottom Side Cover")
            self.form.coverAlong.clear()
            self.form.coverAlong.addItems(["Right Side", "Left Side"])

    def changeCoverAlong(self):
        coverAlong = self.form.coverAlong.currentText()
        if coverAlong == "Bottom Side":
            self.form.bottomCoverLabel.setText("Bottom Cover")
        elif coverAlong == "Top Side":
            self.form.bottomCoverLabel.setText("Top Cover")
        elif coverAlong == "Right Side":
            self.form.bottomCoverLabel.setText("Right Cover")
        else:
            self.form.bottomCoverLabel.setText("Left Cover")

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
        f_cover = self.form.frontCover.text()
        f_cover = FreeCAD.Units.Quantity(f_cover).Value
        cover = self.form.bottomCover.text()
        cover = FreeCAD.Units.Quantity(cover).Value
        lb_cover = self.form.l_sideCover.text()
        lb_cover = FreeCAD.Units.Quantity(lb_cover).Value
        rt_cover = self.form.r_sideCover.text()
        rt_cover = FreeCAD.Units.Quantity(rt_cover).Value
        orientation = self.form.orientationValue.currentText()
        coverAlong = self.form.coverAlong.currentText()
        diameter = self.form.diameter.text()
        diameter = FreeCAD.Units.Quantity(diameter).Value
        amount_check = self.form.amount_radio.isChecked()
        spacing_check = self.form.spacing_radio.isChecked()
        if not self.Rebar:
            if amount_check:
                amount = self.form.amount.value()
                rebar = makeStraightRebar(
                    f_cover,
                    (coverAlong, cover),
                    rt_cover,
                    lb_cover,
                    diameter,
                    True,
                    amount,
                    orientation,
                    self.SelectedObj,
                    self.FaceName,
                )
            elif spacing_check:
                spacing = self.form.spacing.text()
                spacing = FreeCAD.Units.Quantity(spacing).Value
                rebar = makeStraightRebar(
                    f_cover,
                    (coverAlong, cover),
                    rt_cover,
                    lb_cover,
                    diameter,
                    False,
                    spacing,
                    orientation,
                    self.SelectedObj,
                    self.FaceName,
                )
        else:
            if amount_check:
                amount = self.form.amount.value()
                rebar = editStraightRebar(
                    self.Rebar,
                    f_cover,
                    (coverAlong, cover),
                    rt_cover,
                    lb_cover,
                    diameter,
                    True,
                    amount,
                    orientation,
                    self.SelectedObj,
                    self.FaceName,
                )
            elif spacing_check:
                spacing = self.form.spacing.text()
                spacing = FreeCAD.Units.Quantity(spacing).Value
                rebar = editStraightRebar(
                    self.Rebar,
                    f_cover,
                    (coverAlong, cover),
                    rt_cover,
                    lb_cover,
                    diameter,
                    False,
                    spacing,
                    orientation,
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


def makeStraightRebar(
    f_cover,
    coverAlong,
    rt_cover,
    lb_cover,
    diameter,
    amount_spacing_check,
    amount_spacing_value,
    orientation="Horizontal",
    structure=None,
    facename=None,
):
    """Adds the straight reinforcement bar to the selected structural object.

    Case I: When orientation of straight rebar is 'Horizontal':
        makeStraightRebar(FrontCover, CoverAlong, RightCover, LeftCover,
        Diameter, AmountSpacingCheck, AmountSpacingValue, Orientation =
        "Horizontal", Structure, Facename)
        Note: Type of CoverAlong argument is a tuple. Syntax: (<Along>,
        <Value>). Here we have horizontal orientation so we can pass Top Side
        and Bottom Side to <Along> arguments.
        For eg. ("Top Side", 20) and ("Bottom Side", 20)

    Case II: When orientation of straight rebar is 'Vertical':
        makeStraightRebar(FrontCover, CoverAlong, TopCover, BottomCover,
        Diameter, AmountSpacingCheck, AmountSpacingValue, Orientation =
        "Horizontal", Structure, Facename)
        Note: Type of CoverAlong argument is a tuple. Syntax: (<Along>,
        <Value>). Here we have vertical orientation so we can pass Left Side
        and Right Side to <Along> arguments.
        For eg. ("Left Side", 20) and ("Right Side", 20)
    """
    if not structure and not facename:
        selected_obj = FreeCADGui.Selection.getSelectionEx()[0]
        structure = selected_obj.Object
        facename = selected_obj.SubElementNames[0]
    face = structure.Shape.Faces[getFaceNumber(facename) - 1]
    # StructurePRM = getTrueParametersOfStructure(structure)
    FacePRM = getParametersOfFace(structure, facename)
    if not FacePRM:
        FreeCAD.Console.PrintError(
            "Cannot identified shape or from which base object sturctural "
            "element is derived\n"
        )
        return
    # Get points of Striaght rebar
    points = getpointsOfStraightRebar(
        FacePRM,
        rt_cover,
        lb_cover,
        coverAlong,
        orientation,
        diameter,
        facenormalDirection(structure, facename),
    )
    import Part
    import Arch

    sketch = FreeCAD.activeDocument().addObject(
        "Sketcher::SketchObject", "Sketch"
    )
    sketch.MapMode = "FlatFace"
    sketch.Support = [(structure, facename)]
    FreeCAD.ActiveDocument.recompute()
    sketch.addGeometry(Part.LineSegment(points[0], points[1]), False)
    if amount_spacing_check:
        rebar = Arch.makeRebar(
            structure,
            sketch,
            diameter,
            amount_spacing_value,
            f_cover + diameter / 2,
            name="StraightRebar",
        )
        FreeCAD.ActiveDocument.recompute()
    else:
        size = (
            ArchCommands.projectToVector(
                structure.Shape.copy(), face.normalAt(0, 0)
            )
        ).Length
        rebar = Arch.makeRebar(
            structure,
            sketch,
            diameter,
            get_rebar_amount_from_spacing(size, diameter, amount_spacing_value),
            f_cover + diameter / 2,
            name="StraightRebar",
        )
    # Adds properties to the rebar object
    rebar.addProperty(
        "App::PropertyEnumeration",
        "RebarShape",
        "RebarDialog",
        QT_TRANSLATE_NOOP("App::Property", "Shape of rebar"),
    ).RebarShape = RebarTypes.tolist()
    rebar.RebarShape = "StraightRebar"
    rebar.setEditorMode("RebarShape", 2)
    rebar.addProperty(
        "App::PropertyDistance",
        "FrontCover",
        "RebarDialog",
        QT_TRANSLATE_NOOP("App::Property", "Front cover of rebar"),
    ).FrontCover = f_cover
    rebar.setEditorMode("FrontCover", 2)
    rebar.addProperty(
        "App::PropertyDistance",
        "RightTopCover",
        "RebarDialog",
        QT_TRANSLATE_NOOP("App::Property", "Right/Top Side cover of rebar"),
    ).RightTopCover = rt_cover
    rebar.setEditorMode("RightTopCover", 2)
    rebar.addProperty(
        "App::PropertyDistance",
        "LeftBottomCover",
        "RebarDialog",
        QT_TRANSLATE_NOOP("App::Property", "Left/Bottom Side cover of rebar"),
    ).LeftBottomCover = lb_cover
    rebar.setEditorMode("LeftBottomCover", 2)
    rebar.addProperty(
        "App::PropertyString",
        "CoverAlong",
        "RebarDialog",
        QT_TRANSLATE_NOOP("App::Property", "Cover along"),
    ).CoverAlong = coverAlong[0]
    rebar.setEditorMode("CoverAlong", 2)
    rebar.addProperty(
        "App::PropertyDistance",
        "Cover",
        "RebarDialog",
        QT_TRANSLATE_NOOP(
            "App::Property", "Cover of rebar along user selected side"
        ),
    ).Cover = coverAlong[1]
    rebar.setEditorMode("Cover", 2)
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
    rebar.addProperty(
        "App::PropertyString",
        "Orientation",
        "RebarDialog",
        QT_TRANSLATE_NOOP("App::Property", "Shape of rebar"),
    ).Orientation = orientation
    rebar.setEditorMode("Orientation", 2)
    if amount_spacing_check:
        rebar.AmountCheck = True
    else:
        rebar.AmountCheck = False
        rebar.TrueSpacing = amount_spacing_value
    FreeCAD.ActiveDocument.recompute()
    return rebar


def editStraightRebar(
    Rebar,
    f_cover,
    coverAlong,
    rt_cover,
    lb_cover,
    diameter,
    amount_spacing_check,
    amount_spacing_value,
    orientation,
    structure=None,
    facename=None,
):
    sketch = Rebar.Base
    if structure and facename:
        sketch.Support = [(structure, facename)]
        FreeCAD.ActiveDocument.recompute()
    # Check if sketch support is empty.
    if not sketch.Support:
        showWarning(
            "You have checked: 'Remove external geometry of base sketches when "
            "needed.'\nTo uncheck: Edit->Preferences->Arch."
        )
        return
    # Assigned values
    facename = sketch.Support[0][1][0]
    structure = sketch.Support[0][0]
    face = structure.Shape.Faces[getFaceNumber(facename) - 1]
    # StructurePRM = getTrueParametersOfStructure(structure)
    # Get parameters of the face where sketch of rebar is drawn
    FacePRM = getParametersOfFace(structure, facename)
    # Get points of Striaght rebar
    points = getpointsOfStraightRebar(
        FacePRM,
        rt_cover,
        lb_cover,
        coverAlong,
        orientation,
        diameter,
        facenormalDirection(structure, facename),
    )
    sketch.movePoint(0, 1, points[0], 0)
    FreeCAD.ActiveDocument.recompute()
    sketch.movePoint(0, 2, points[1], 0)
    FreeCAD.ActiveDocument.recompute()
    Rebar.OffsetStart = f_cover + diameter / 2
    Rebar.OffsetEnd = f_cover + diameter / 2
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
    Rebar.RightTopCover = rt_cover
    Rebar.LeftBottomCover = lb_cover
    Rebar.CoverAlong = coverAlong[0]
    Rebar.Cover = coverAlong[1]
    Rebar.TrueSpacing = amount_spacing_value
    Rebar.Diameter = diameter
    Rebar.Orientation = orientation
    FreeCAD.ActiveDocument.recompute()
    return Rebar


def editDialog(vobj):
    FreeCADGui.Control.closeDialog()
    obj = _StraightRebarTaskPanel(vobj.Object)
    obj.form.frontCover.setText(str(vobj.Object.FrontCover))
    obj.form.r_sideCover.setText(str(vobj.Object.RightTopCover))
    obj.form.l_sideCover.setText(str(vobj.Object.LeftBottomCover))
    obj.form.bottomCover.setText(str(vobj.Object.Cover))
    obj.form.diameter.setText(str(vobj.Object.Diameter))
    obj.form.orientationValue.setCurrentIndex(
        obj.form.orientationValue.findText(str(vobj.Object.Orientation))
    )
    obj.form.coverAlong.setCurrentIndex(
        obj.form.coverAlong.findText(str(vobj.Object.CoverAlong))
    )
    if vobj.Object.AmountCheck:
        obj.form.amount.setValue(vobj.Object.Amount)
    else:
        obj.form.amount_radio.setChecked(False)
        obj.form.spacing_radio.setChecked(True)
        obj.form.amount.setDisabled(True)
        obj.form.spacing.setEnabled(True)
        obj.form.spacing.setText(str(vobj.Object.TrueSpacing))
    # obj.form.PickSelectedFace.setVisible(False)
    FreeCADGui.Control.showDialog(obj)


def CommandStraightRebar():
    selected_obj = check_selected_face()
    if selected_obj:
        FreeCADGui.Control.showDialog(_StraightRebarTaskPanel())
