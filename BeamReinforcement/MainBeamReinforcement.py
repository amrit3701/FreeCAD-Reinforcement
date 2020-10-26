# -*- coding: utf-8 -*-
# ***************************************************************************
# *                                                                         *
# *   Copyright (c) 2019 - Suraj <dadralj18@gmail.com>                      *
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

__title__ = "Beam Reinforcement Dialog Box"
__author__ = "Suraj"
__url__ = "https://www.freecadweb.org"

import ast
from pathlib import Path
from PySide2 import QtWidgets, QtGui

import FreeCAD
import FreeCADGui

from Rebarfunc import check_selected_face, showWarning
from BeamReinforcement.NumberDiameterOffset import (
    runNumberDiameterOffsetDialog,
)
from BeamReinforcement.RebarTypeEditDialog import runRebarTypeEditDialog
from BeamReinforcement.HookOrientationEditDialog import (
    runHookOrientationEditDialog,
)
from BeamReinforcement.HookExtensionEditDialog import (
    runHookExtensionEditDialog,
)
from BeamReinforcement.RoundingEditDialog import runRoundingEditDialog
from BeamReinforcement.LayerSpacingEditDialog import runLayerSpacingEditDialog
from BeamReinforcement import (
    ShearRebars_NumberDiameterOffset,
    ShearRebarTypeEditDialog,
    ShearRebars_HookOrientationEditDialog,
    ShearRebars_HookExtensionEditDialog,
    ShearRebars_RoundingEditDialog,
)
from BeamReinforcement import TwoLeggedBeam


class _BeamReinforcementDialog:
    def __init__(self, RebarGroup=None):
        """This function set initial data in Beam Reinforcement dialog box."""
        if not RebarGroup:
            # If beam reinforcement is not created yet, then get SelectedObj
            # from FreeCAD Gui selection
            selected_obj = FreeCADGui.Selection.getSelectionEx()[0]
            self.SelectedObj = selected_obj.Object
            self.FaceName = selected_obj.SubElementNames[0]
            self.CustomSpacing = None
        else:
            # If beam reinforcement is already created, then get selectedObj
            # from data stored in created Stirrup
            for rebar_group in RebarGroup.ReinforcementGroups:
                if hasattr(rebar_group, "Stirrups"):
                    Stirrup = rebar_group.Stirrups[0]
                    self.FaceName = Stirrup.Base.Support[0][1][0]
                    self.SelectedObj = Stirrup.Base.Support[0][0]
                    self.CustomSpacing = Stirrup.CustomSpacing
                    break

        # Load ui from file MainBeamReinforcement.ui
        self.form = FreeCADGui.PySideUic.loadUi(
            str(Path(__file__).with_suffix(".ui").absolute())
        )
        self.form.setWindowTitle(
            QtWidgets.QApplication.translate(
                "RebarAddon", "Beam Reinforcement Dialog Box", None
            )
        )
        self.RebarGroup = RebarGroup

    def setupUi(self):
        """This function is used to add components to ui."""
        # Load and add widgets into stacked widget
        self.stirrups_widget = FreeCADGui.PySideUic.loadUi(
            str(Path(__file__).parent.absolute() / "Stirrups.ui")
        )
        self.form.rebars_stackedWidget.addWidget(self.stirrups_widget)
        self.top_reinforcement_widget = FreeCADGui.PySideUic.loadUi(
            str(Path(__file__).parent.absolute() / "TopBottomReinforcement.ui")
        )
        self.form.rebars_stackedWidget.addWidget(self.top_reinforcement_widget)
        self.bottom_reinforcement_widget = FreeCADGui.PySideUic.loadUi(
            str(Path(__file__).parent.absolute() / "TopBottomReinforcement.ui")
        )
        self.form.rebars_stackedWidget.addWidget(
            self.bottom_reinforcement_widget
        )
        self.left_reinforcement_widget = FreeCADGui.PySideUic.loadUi(
            str(Path(__file__).parent.absolute() / "LeftRightReinforcement.ui")
        )
        self.form.rebars_stackedWidget.addWidget(self.left_reinforcement_widget)
        self.right_reinforcement_widget = FreeCADGui.PySideUic.loadUi(
            str(Path(__file__).parent.absolute() / "LeftRightReinforcement.ui")
        )
        self.form.rebars_stackedWidget.addWidget(
            self.right_reinforcement_widget
        )
        # Add dropdown menu items
        self.addDropdownMenuItems()
        # Add image of Two Legged Stirrup
        self.form.stirrups_configurationImage.setPixmap(
            QtGui.QPixmap(
                str(
                    Path(__file__).parent.parent.absolute()
                    / "icons"
                    / "Beam_TwoLeggedStirrups.png"
                )
            )
        )
        # Set default values in UI
        self.setDefaultValues()
        # Connect signals and slots
        self.connectSignalSlots()

    def setDefaultValues(self):
        # Set stirrups data
        self.form.stirrups_configuration.setCurrentIndex(
            self.form.stirrups_configuration.findText("Two Legged Stirrups")
        )
        self.stirrups_widget.stirrups_leftCover.setText("20 mm")
        self.stirrups_widget.stirrups_rightCover.setText("20 mm")
        self.stirrups_widget.stirrups_topCover.setText("20 mm")
        self.stirrups_widget.stirrups_bottomCover.setText("20 mm")
        self.stirrups_widget.stirrups_allCoversEqual.setChecked(True)
        self.stirrupsAllCoversEqualClicked()
        self.stirrups_widget.stirrups_offset.setText("100 mm")
        self.stirrups_widget.stirrups_diameter.setText("8 mm")
        self.stirrups_widget.stirrups_bentAngle.setCurrentIndex(
            self.stirrups_widget.stirrups_bentAngle.findText("135")
        )
        self.stirrups_widget.stirrups_extensionFactor.setValue(4)
        self.stirrups_widget.stirrups_number_radio.setChecked(False)
        self.stirrups_widget.stirrups_spacing_radio.setChecked(True)
        self.stirrups_widget.stirrups_number.setEnabled(False)
        self.stirrups_widget.stirrups_spacing.setEnabled(True)
        self.stirrups_widget.stirrups_number.setValue(10)
        self.stirrups_widget.stirrups_spacing.setText("100 mm")
        # Set top reinforcement data
        self.top_reinforcement_widget.numberDiameterOffset.setPlainText(
            "('1#20@-60+2#16@-60+1#20@-60', '3#16@-100')"
        )
        self.top_reinforcement_widget.rebarType.setPlainText(
            "(('LShapeRebar', 'LShapeRebar', 'LShapeRebar'), ('LShapeRebar',))"
        )
        self.top_reinforcement_widget.hookOrientation.setPlainText(
            "(('Rear Outside', 'Rear Outside', 'Rear Outside'), "
            "('Rear Outside',))"
        )
        self.top_reinforcement_widget.hookExtension.setPlainText(
            "((100.0, 100.0, 100.0), (100.0,))"
        )
        self.top_reinforcement_widget.LRebarRounding.setPlainText(
            "((2, 2, 2), (2,))"
        )
        self.top_reinforcement_widget.layers.setValue(2)
        self.top_reinforcement_widget.layerSpacing.setText("(30.0, 30.0)")
        # Set bottom reinforcement data
        self.bottom_reinforcement_widget.numberDiameterOffset.setPlainText(
            "('1#20@-60+2#16@-60+1#20@-60', '3#16@-100')"
        )
        self.bottom_reinforcement_widget.rebarType.setPlainText(
            "(('LShapeRebar', 'LShapeRebar', 'LShapeRebar'), ('LShapeRebar',))"
        )
        self.bottom_reinforcement_widget.hookOrientation.setPlainText(
            "(('Rear Outside', 'Rear Outside', 'Rear Outside'), "
            "('Rear Outside',))"
        )
        self.bottom_reinforcement_widget.hookExtension.setPlainText(
            "((100.0, 100.0, 100.0), (100.0,))"
        )
        self.bottom_reinforcement_widget.LRebarRounding.setPlainText(
            "((2, 2, 2), (2,))"
        )
        self.bottom_reinforcement_widget.layers.setValue(2)
        self.bottom_reinforcement_widget.layerSpacing.setText("(30.0, 30.0)")
        # Set left reinforcement data
        self.left_reinforcement_widget.numberDiameterOffset.setText(
            "1#16@-100+1#16@-100+1#16@-100"
        )
        self.left_reinforcement_widget.rebarType.setText(
            "('LShapeRebar', 'LShapeRebar', 'LShapeRebar')"
        )
        self.left_reinforcement_widget.hookOrientation.setText(
            "('Rear Inside', 'Front Inside', 'Rear Inside')"
        )
        self.left_reinforcement_widget.hookExtension.setText(
            "(80.0, 80.0, 80.0)"
        )
        self.left_reinforcement_widget.LRebarRounding.setText("(2, 2, 2)")
        self.left_reinforcement_widget.rebarSpacing.setText("30 mm")
        self.left_reinforcement_widget.rebarTypeEditButton.setEnabled(True)
        self.left_reinforcement_widget.hookOrientationEditButton.setEnabled(
            True
        )
        self.left_reinforcement_widget.hookExtensionEditButton.setEnabled(True)
        self.left_reinforcement_widget.LRebarRoundingEditButton.setEnabled(True)
        # Set right reinforcement data
        self.right_reinforcement_widget.numberDiameterOffset.setText(
            "1#16@-100+1#16@-100+1#16@-100"
        )
        self.right_reinforcement_widget.rebarType.setText(
            "('LShapeRebar', 'LShapeRebar', 'LShapeRebar')"
        )
        self.right_reinforcement_widget.hookOrientation.setText(
            "('Front Inside', 'Rear Inside', 'Front Inside')"
        )
        self.right_reinforcement_widget.hookExtension.setText(
            "(80.0, 80.0, 80.0)"
        )
        self.right_reinforcement_widget.LRebarRounding.setText("(2, 2, 2)")
        self.right_reinforcement_widget.rebarSpacing.setText("30 mm")
        self.right_reinforcement_widget.rebarTypeEditButton.setEnabled(True)
        self.right_reinforcement_widget.hookOrientationEditButton.setEnabled(
            True
        )
        self.right_reinforcement_widget.hookExtensionEditButton.setEnabled(True)
        self.right_reinforcement_widget.LRebarRoundingEditButton.setEnabled(
            True
        )

    def addDropdownMenuItems(self):
        """This function add dropdown items to each Gui::PrefComboBox."""
        self.form.stirrups_configuration.addItems(["Two Legged Stirrups"])
        self.stirrups_widget.stirrups_bentAngle.addItems(["90", "135"])

    def connectSignalSlots(self):
        """This function is used to connect different slots in UI to appropriate
        functions."""
        self.form.rebars_listWidget.currentRowChanged.connect(
            self.changeRebarsListWidget
        )
        self.stirrups_widget.stirrups_leftCover.textChanged.connect(
            self.stirrupsLeftCoverChanged
        )
        self.stirrups_widget.stirrups_allCoversEqual.clicked.connect(
            self.stirrupsAllCoversEqualClicked
        )
        self.stirrups_widget.stirrups_number_radio.clicked.connect(
            self.stirrupsNumberRadioClicked
        )
        self.stirrups_widget.stirrups_spacing_radio.clicked.connect(
            self.stirrupsSpacingRadioClicked
        )
        self.stirrups_widget.stirrups_customSpacing.clicked.connect(
            self.runRebarDistribution
        )
        self.stirrups_widget.stirrups_removeCustomSpacing.clicked.connect(
            self.removeRebarDistribution
        )
        self.top_reinforcement_widget.numberDiameterOffsetEditButton.clicked.connect(
            lambda: self.numberDiameterOffsetEditButtonClicked(
                self.top_reinforcement_widget.numberDiameterOffsetEditButton
            )
        )
        self.bottom_reinforcement_widget.numberDiameterOffsetEditButton.clicked.connect(
            lambda: self.numberDiameterOffsetEditButtonClicked(
                self.bottom_reinforcement_widget.numberDiameterOffsetEditButton
            )
        )
        self.top_reinforcement_widget.rebarTypeEditButton.clicked.connect(
            lambda: self.rebarTypeEditButtonClicked(
                self.top_reinforcement_widget.rebarTypeEditButton
            )
        )
        self.bottom_reinforcement_widget.rebarTypeEditButton.clicked.connect(
            lambda: self.rebarTypeEditButtonClicked(
                self.bottom_reinforcement_widget.rebarTypeEditButton
            )
        )
        self.top_reinforcement_widget.hookOrientationEditButton.clicked.connect(
            lambda: self.hookOrientationEditButtonClicked(
                self.top_reinforcement_widget.hookOrientationEditButton
            )
        )
        self.bottom_reinforcement_widget.hookOrientationEditButton.clicked.connect(
            lambda: self.hookOrientationEditButtonClicked(
                self.bottom_reinforcement_widget.hookOrientationEditButton
            )
        )
        self.top_reinforcement_widget.hookExtensionEditButton.clicked.connect(
            lambda: self.hookExtensionEditButtonClicked(
                self.top_reinforcement_widget.hookExtensionEditButton
            )
        )
        self.bottom_reinforcement_widget.hookExtensionEditButton.clicked.connect(
            lambda: self.hookExtensionEditButtonClicked(
                self.bottom_reinforcement_widget.hookExtensionEditButton
            )
        )
        self.top_reinforcement_widget.LRebarRoundingEditButton.clicked.connect(
            lambda: self.LRebarRoundingEditButtonClicked(
                self.top_reinforcement_widget.LRebarRoundingEditButton
            )
        )
        self.bottom_reinforcement_widget.LRebarRoundingEditButton.clicked.connect(
            lambda: self.LRebarRoundingEditButtonClicked(
                self.bottom_reinforcement_widget.LRebarRoundingEditButton
            )
        )
        self.top_reinforcement_widget.layerSpacingEditButton.clicked.connect(
            lambda: self.layerSpacingEditButtonClicked(
                self.top_reinforcement_widget.layerSpacingEditButton
            )
        )
        self.bottom_reinforcement_widget.layerSpacingEditButton.clicked.connect(
            lambda: self.layerSpacingEditButtonClicked(
                self.bottom_reinforcement_widget.layerSpacingEditButton
            )
        )
        self.left_reinforcement_widget.numberDiameterOffsetEditButton.clicked.connect(
            lambda: self.shearNumberDiameterOffsetEditButtonClicked(
                self.left_reinforcement_widget.numberDiameterOffsetEditButton
            )
        )
        self.right_reinforcement_widget.numberDiameterOffsetEditButton.clicked.connect(
            lambda: self.shearNumberDiameterOffsetEditButtonClicked(
                self.right_reinforcement_widget.numberDiameterOffsetEditButton
            )
        )
        self.left_reinforcement_widget.rebarTypeEditButton.clicked.connect(
            lambda: self.shearRebarTypeEditButtonClicked(
                self.left_reinforcement_widget.rebarTypeEditButton
            )
        )
        self.right_reinforcement_widget.rebarTypeEditButton.clicked.connect(
            lambda: self.shearRebarTypeEditButtonClicked(
                self.right_reinforcement_widget.rebarTypeEditButton
            )
        )
        self.left_reinforcement_widget.hookOrientationEditButton.clicked.connect(
            lambda: self.shearHookOrientationEditButtonClicked(
                self.left_reinforcement_widget.hookOrientationEditButton
            )
        )
        self.right_reinforcement_widget.hookOrientationEditButton.clicked.connect(
            lambda: self.shearHookOrientationEditButtonClicked(
                self.right_reinforcement_widget.hookOrientationEditButton
            )
        )
        self.left_reinforcement_widget.hookExtensionEditButton.clicked.connect(
            lambda: self.shearHookExtensionEditButtonClicked(
                self.left_reinforcement_widget.hookExtensionEditButton
            )
        )
        self.right_reinforcement_widget.hookExtensionEditButton.clicked.connect(
            lambda: self.shearHookExtensionEditButtonClicked(
                self.right_reinforcement_widget.hookExtensionEditButton
            )
        )
        self.left_reinforcement_widget.LRebarRoundingEditButton.clicked.connect(
            lambda: self.shearLRebarRoundingEditButtonClicked(
                self.left_reinforcement_widget.LRebarRoundingEditButton
            )
        )
        self.right_reinforcement_widget.LRebarRoundingEditButton.clicked.connect(
            lambda: self.shearLRebarRoundingEditButtonClicked(
                self.right_reinforcement_widget.LRebarRoundingEditButton
            )
        )
        self.form.next_button.clicked.connect(self.nextButtonClicked)
        self.form.back_button.clicked.connect(self.backButtonClicked)
        self.form.standardButtonBox.clicked.connect(self.clicked)

    def changeRebarsListWidget(self, index):
        max_index = self.form.rebars_listWidget.count() - 1
        if index == max_index:
            self.form.next_button.setText("Finish")
        else:
            self.form.next_button.setText("Next")
        self.form.rebars_stackedWidget.setCurrentIndex(index)

    def stirrupsLeftCoverChanged(self):
        # Set right/top/bottom cover equal to left cover
        if self.stirrups_widget.stirrups_allCoversEqual.isChecked():
            left_cover = self.stirrups_widget.stirrups_leftCover.text()
            self.stirrups_widget.stirrups_rightCover.setText(left_cover)
            self.stirrups_widget.stirrups_topCover.setText(left_cover)
            self.stirrups_widget.stirrups_bottomCover.setText(left_cover)

    def stirrupsAllCoversEqualClicked(self):
        if self.stirrups_widget.stirrups_allCoversEqual.isChecked():
            # Disable fields for right/top/bottom cover
            self.stirrups_widget.stirrups_rightCover.setEnabled(False)
            self.stirrups_widget.stirrups_topCover.setEnabled(False)
            self.stirrups_widget.stirrups_bottomCover.setEnabled(False)
            # Set right/top/bottom cover equal to left cover
            self.stirrupsLeftCoverChanged()
        else:
            # Enable fields for right/top/bottom cover
            self.stirrups_widget.stirrups_rightCover.setEnabled(True)
            self.stirrups_widget.stirrups_topCover.setEnabled(True)
            self.stirrups_widget.stirrups_bottomCover.setEnabled(True)

    def stirrupsNumberRadioClicked(self):
        """This function enable stirrups_number field and disable
        stirrups_spacing field in UI when stirrups_number_radio button is
        clicked."""
        self.stirrups_widget.stirrups_spacing.setEnabled(False)
        self.stirrups_widget.stirrups_number.setEnabled(True)

    def stirrupsSpacingRadioClicked(self):
        """This function enable stirrups_spacing field and disable
        stirrups_number field in UI when stirrups_spacing_radio button is
        clicked."""
        self.stirrups_widget.stirrups_number.setEnabled(False)
        self.stirrups_widget.stirrups_spacing.setEnabled(True)

    def runRebarDistribution(self):
        offset_of_stirrups = self.stirrups_widget.stirrups_offset.text()
        offset_of_stirrups = FreeCAD.Units.Quantity(offset_of_stirrups).Value
        from RebarDistribution import runRebarDistribution

        runRebarDistribution(self, offset_of_stirrups)

    def removeRebarDistribution(self):
        self.CustomSpacing = None
        if self.RebarGroup:
            for Stirrup in self.RebarGroup.ReinforcementGroups[0].Stirrups:
                Stirrup.CustomSpacing = ""
        FreeCAD.ActiveDocument.recompute()

    def numberDiameterOffsetEditButtonClicked(self, button):
        if (
            button
            == self.top_reinforcement_widget.numberDiameterOffsetEditButton
        ):
            number_diameter_offset = (
                self.top_reinforcement_widget.numberDiameterOffset.toPlainText()
            )
        else:
            number_diameter_offset = (
                self.bottom_reinforcement_widget.numberDiameterOffset.toPlainText()
            )

        number_diameter_offset_tuple = ast.literal_eval(number_diameter_offset)
        runNumberDiameterOffsetDialog(self, number_diameter_offset_tuple)
        if (
            button
            == self.top_reinforcement_widget.numberDiameterOffsetEditButton
        ):
            self.top_reinforcement_widget.numberDiameterOffset.setPlainText(
                str(self.NumberDiameterOffsetTuple)
            )
            self.top_reinforcement_widget.layers.setValue(
                len(self.NumberDiameterOffsetTuple)
            )
            rebar_type = self.getRebarType(
                self.NumberDiameterOffsetTuple,
                ast.literal_eval(
                    self.top_reinforcement_widget.rebarType.toPlainText()
                ),
            )
            self.top_reinforcement_widget.rebarType.setPlainText(
                str(rebar_type)
            )
            self.top_reinforcement_widget.hookOrientation.setPlainText(
                str(
                    self.getHookOrientation(
                        self.NumberDiameterOffsetTuple,
                        rebar_type,
                        ast.literal_eval(
                            self.top_reinforcement_widget.hookOrientation.toPlainText()
                        ),
                    )
                )
            )
            self.top_reinforcement_widget.hookExtension.setPlainText(
                str(
                    self.getHookExtension(
                        self.NumberDiameterOffsetTuple,
                        rebar_type,
                        ast.literal_eval(
                            self.top_reinforcement_widget.hookExtension.toPlainText()
                        ),
                    )
                )
            )
            self.top_reinforcement_widget.LRebarRounding.setPlainText(
                str(
                    self.getLRebarRounding(
                        self.NumberDiameterOffsetTuple,
                        rebar_type,
                        ast.literal_eval(
                            self.top_reinforcement_widget.LRebarRounding.toPlainText()
                        ),
                    )
                )
            )
            self.top_reinforcement_widget.layerSpacing.setText(
                str(
                    self.getLayerSpacing(
                        self.NumberDiameterOffsetTuple,
                        ast.literal_eval(
                            self.top_reinforcement_widget.layerSpacing.text()
                        ),
                    )
                )
            )
        else:
            self.bottom_reinforcement_widget.numberDiameterOffset.setPlainText(
                str(self.NumberDiameterOffsetTuple)
            )
            self.bottom_reinforcement_widget.layers.setValue(
                len(self.NumberDiameterOffsetTuple)
            )
            rebar_type = self.getRebarType(
                self.NumberDiameterOffsetTuple,
                ast.literal_eval(
                    self.bottom_reinforcement_widget.rebarType.toPlainText()
                ),
            )
            self.bottom_reinforcement_widget.rebarType.setPlainText(
                str(rebar_type)
            )
            self.bottom_reinforcement_widget.hookOrientation.setPlainText(
                str(
                    self.getHookOrientation(
                        self.NumberDiameterOffsetTuple,
                        rebar_type,
                        ast.literal_eval(
                            self.bottom_reinforcement_widget.hookOrientation.toPlainText()
                        ),
                    )
                )
            )
            self.bottom_reinforcement_widget.hookExtension.setPlainText(
                str(
                    self.getHookExtension(
                        self.NumberDiameterOffsetTuple,
                        rebar_type,
                        ast.literal_eval(
                            self.bottom_reinforcement_widget.hookExtension.toPlainText()
                        ),
                    )
                )
            )
            self.bottom_reinforcement_widget.LRebarRounding.setPlainText(
                str(
                    self.getLRebarRounding(
                        self.NumberDiameterOffsetTuple,
                        rebar_type,
                        ast.literal_eval(
                            self.bottom_reinforcement_widget.LRebarRounding.toPlainText()
                        ),
                    )
                )
            )
            self.bottom_reinforcement_widget.layerSpacing.setText(
                str(
                    self.getLayerSpacing(
                        self.NumberDiameterOffsetTuple,
                        ast.literal_eval(
                            self.bottom_reinforcement_widget.layerSpacing.text()
                        ),
                    )
                )
            )

    @staticmethod
    def getRebarType(number_diameter_offset_tuple, rebar_type_tuple):
        layers = len(number_diameter_offset_tuple)
        rebar_type_list = []
        for layer in range(1, layers + 1):
            rebar_type_list.append([])
            for i in range(
                0, len(number_diameter_offset_tuple[layer - 1].split("+"))
            ):
                if len(rebar_type_tuple) >= layer:
                    if len(rebar_type_tuple[layer - 1]) > i:
                        rebar_type_list[-1].append(
                            rebar_type_tuple[layer - 1][i]
                        )
                    else:
                        rebar_type_list[-1].append("StraightRebar")
                else:
                    rebar_type_list[-1].append("StraightRebar")
            rebar_type_list[-1] = tuple(rebar_type_list[-1])
        return tuple(rebar_type_list)

    @staticmethod
    def getHookOrientation(
        number_diameter_offset_tuple,
        rebar_type_tuple,
        hook_orientation_tuple,
    ):
        layers = len(number_diameter_offset_tuple)
        hook_orientation_list = []
        for layer in range(1, layers + 1):
            hook_orientation_list.append([])
            for i in range(
                0, len(number_diameter_offset_tuple[layer - 1].split("+"))
            ):
                if len(hook_orientation_tuple) >= layer:
                    if len(hook_orientation_tuple[layer - 1]) > i:
                        if rebar_type_tuple[layer - 1][i] == "StraightRebar":
                            hook_orientation_list[-1].append(None)
                        else:
                            if hook_orientation_tuple[layer - 1][i] is None:
                                hook_orientation_list[-1].append("Front Inside")
                            else:
                                hook_orientation_list[-1].append(
                                    hook_orientation_tuple[layer - 1][i]
                                )
                    else:
                        if rebar_type_tuple[layer - 1][i] == "StraightRebar":
                            hook_orientation_list[-1].append(None)
                        else:
                            hook_orientation_list[-1].append("Front Inside")
                else:
                    if rebar_type_tuple[layer - 1][i] == "StraightRebar":
                        hook_orientation_list[-1].append(None)
                    else:
                        hook_orientation_list[-1].append("Front Inside")
            hook_orientation_list[-1] = tuple(hook_orientation_list[-1])
        return tuple(hook_orientation_list)

    @staticmethod
    def getHookExtension(
        number_diameter_offset_tuple,
        rebar_type_tuple,
        hook_extension_tuple,
    ):
        layers = len(number_diameter_offset_tuple)
        hook_extension_list = []
        for layer in range(1, layers + 1):
            hook_extension_list.append([])
            for i in range(
                0, len(number_diameter_offset_tuple[layer - 1].split("+"))
            ):
                if len(hook_extension_tuple) >= layer:
                    if len(hook_extension_tuple[layer - 1]) > i:
                        if rebar_type_tuple[layer - 1][i] == "StraightRebar":
                            hook_extension_list[-1].append(None)
                        else:
                            if hook_extension_tuple[layer - 1][i] is None:
                                hook_extension_list[-1].append(40.0)
                            else:
                                hook_extension_list[-1].append(
                                    hook_extension_tuple[layer - 1][i]
                                )
                    else:
                        if rebar_type_tuple[layer - 1][i] == "StraightRebar":
                            hook_extension_list[-1].append(None)
                        else:
                            hook_extension_list[-1].append(40.0)
                else:
                    if rebar_type_tuple[layer - 1][i] == "StraightRebar":
                        hook_extension_list[-1].append(None)
                    else:
                        hook_extension_list[-1].append(40.0)
            hook_extension_list[-1] = tuple(hook_extension_list[-1])
        return tuple(hook_extension_list)

    @staticmethod
    def getLRebarRounding(
        number_diameter_offset_tuple, rebar_type_tuple, rounding_tuple
    ):
        layers = len(number_diameter_offset_tuple)
        rounding_list = []
        for layer in range(1, layers + 1):
            rounding_list.append([])
            for i in range(
                0, len(number_diameter_offset_tuple[layer - 1].split("+"))
            ):
                if len(rounding_tuple) >= layer:
                    if len(rounding_tuple[layer - 1]) > i:
                        if rebar_type_tuple[layer - 1][i] == "StraightRebar":
                            rounding_list[-1].append(None)
                        else:
                            if rounding_tuple[layer - 1][i] is None:
                                rounding_list[-1].append(2)
                            else:
                                rounding_list[-1].append(
                                    rounding_tuple[layer - 1][i]
                                )
                    else:
                        if rebar_type_tuple[layer - 1][i] == "StraightRebar":
                            rounding_list[-1].append(None)
                        else:
                            rounding_list[-1].append(2)
                else:
                    if rebar_type_tuple[layer - 1][i] == "StraightRebar":
                        rounding_list[-1].append(None)
                    else:
                        rounding_list[-1].append(2)
            rounding_list[-1] = tuple(rounding_list[-1])
        return tuple(rounding_list)

    @staticmethod
    def getLayerSpacing(number_diameter_offset_tuple, layer_spacing_tuple):
        layers = len(number_diameter_offset_tuple)
        layer_spacing_list = []
        for layer in range(1, layers + 1):
            if len(layer_spacing_tuple) >= layer:
                layer_spacing_list.append(layer_spacing_tuple[layer - 1])
            else:
                layer_spacing_list.append(30.0)
        return tuple(layer_spacing_list)

    def rebarTypeEditButtonClicked(self, button):
        if button == self.top_reinforcement_widget.rebarTypeEditButton:
            rebar_type = self.top_reinforcement_widget.rebarType.toPlainText()
        else:
            rebar_type = (
                self.bottom_reinforcement_widget.rebarType.toPlainText()
            )
        rebar_type_tuple = ast.literal_eval(rebar_type)
        runRebarTypeEditDialog(self, rebar_type_tuple)
        if button == self.top_reinforcement_widget.rebarTypeEditButton:
            self.top_reinforcement_widget.rebarType.setPlainText(
                str(self.RebarTypeTuple)
            )
            self.top_reinforcement_widget.hookOrientation.setPlainText(
                str(
                    self.getHookOrientation(
                        ast.literal_eval(
                            self.top_reinforcement_widget.numberDiameterOffset.toPlainText()
                        ),
                        self.RebarTypeTuple,
                        ast.literal_eval(
                            self.top_reinforcement_widget.hookOrientation.toPlainText()
                        ),
                    )
                )
            )
            self.top_reinforcement_widget.hookExtension.setPlainText(
                str(
                    self.getHookExtension(
                        ast.literal_eval(
                            self.top_reinforcement_widget.numberDiameterOffset.toPlainText()
                        ),
                        self.RebarTypeTuple,
                        ast.literal_eval(
                            self.top_reinforcement_widget.hookExtension.toPlainText()
                        ),
                    )
                )
            )
            self.top_reinforcement_widget.LRebarRounding.setPlainText(
                str(
                    self.getLRebarRounding(
                        ast.literal_eval(
                            self.top_reinforcement_widget.numberDiameterOffset.toPlainText()
                        ),
                        self.RebarTypeTuple,
                        ast.literal_eval(
                            self.top_reinforcement_widget.LRebarRounding.toPlainText()
                        ),
                    )
                )
            )
        else:
            self.bottom_reinforcement_widget.rebarType.setPlainText(
                str(self.RebarTypeTuple)
            )
            self.bottom_reinforcement_widget.hookOrientation.setPlainText(
                str(
                    self.getHookOrientation(
                        ast.literal_eval(
                            self.bottom_reinforcement_widget.numberDiameterOffset.toPlainText()
                        ),
                        self.RebarTypeTuple,
                        ast.literal_eval(
                            self.bottom_reinforcement_widget.hookOrientation.toPlainText()
                        ),
                    )
                )
            )
            self.bottom_reinforcement_widget.hookExtension.setPlainText(
                str(
                    self.getHookExtension(
                        ast.literal_eval(
                            self.bottom_reinforcement_widget.numberDiameterOffset.toPlainText()
                        ),
                        self.RebarTypeTuple,
                        ast.literal_eval(
                            self.bottom_reinforcement_widget.hookExtension.toPlainText()
                        ),
                    )
                )
            )
            self.bottom_reinforcement_widget.LRebarRounding.setPlainText(
                str(
                    self.getLRebarRounding(
                        ast.literal_eval(
                            self.bottom_reinforcement_widget.numberDiameterOffset.toPlainText()
                        ),
                        self.RebarTypeTuple,
                        ast.literal_eval(
                            self.bottom_reinforcement_widget.LRebarRounding.toPlainText()
                        ),
                    )
                )
            )

    def hookOrientationEditButtonClicked(self, button):
        if button == self.top_reinforcement_widget.hookOrientationEditButton:
            hook_orientation = (
                self.top_reinforcement_widget.hookOrientation.toPlainText()
            )
        else:
            hook_orientation = (
                self.bottom_reinforcement_widget.hookOrientation.toPlainText()
            )
        hook_orientation_tuple = ast.literal_eval(hook_orientation)
        runHookOrientationEditDialog(self, hook_orientation_tuple)
        if button == self.top_reinforcement_widget.hookOrientationEditButton:
            self.top_reinforcement_widget.hookOrientation.setPlainText(
                str(self.HookOrientationTuple)
            )
        else:
            self.bottom_reinforcement_widget.hookOrientation.setPlainText(
                str(self.HookOrientationTuple)
            )

    def hookExtensionEditButtonClicked(self, button):
        if button == self.top_reinforcement_widget.hookExtensionEditButton:
            hook_extension = (
                self.top_reinforcement_widget.hookExtension.toPlainText()
            )
        else:
            hook_extension = (
                self.bottom_reinforcement_widget.hookExtension.toPlainText()
            )
        hook_extension_tuple = ast.literal_eval(hook_extension)
        runHookExtensionEditDialog(self, hook_extension_tuple)
        if button == self.top_reinforcement_widget.hookExtensionEditButton:
            self.top_reinforcement_widget.hookExtension.setPlainText(
                str(self.HookExtensionTuple)
            )
        else:
            self.bottom_reinforcement_widget.hookExtension.setPlainText(
                str(self.HookExtensionTuple)
            )

    def LRebarRoundingEditButtonClicked(self, button):
        if button == self.top_reinforcement_widget.LRebarRoundingEditButton:
            rounding = (
                self.top_reinforcement_widget.LRebarRounding.toPlainText()
            )
        else:
            rounding = (
                self.bottom_reinforcement_widget.LRebarRounding.toPlainText()
            )
        rounding_tuple = ast.literal_eval(rounding)
        runRoundingEditDialog(self, rounding_tuple)
        if button == self.top_reinforcement_widget.LRebarRoundingEditButton:
            self.top_reinforcement_widget.LRebarRounding.setPlainText(
                str(self.RoundingTuple)
            )
        else:
            self.bottom_reinforcement_widget.LRebarRounding.setPlainText(
                str(self.RoundingTuple)
            )

    def layerSpacingEditButtonClicked(self, button):
        if button == self.top_reinforcement_widget.layerSpacingEditButton:
            layer_spacing = self.top_reinforcement_widget.layerSpacing.text()
        else:
            layer_spacing = self.bottom_reinforcement_widget.layerSpacing.text()
        layer_spacing_tuple = ast.literal_eval(layer_spacing)
        runLayerSpacingEditDialog(self, layer_spacing_tuple)
        if button == self.top_reinforcement_widget.layerSpacingEditButton:
            self.top_reinforcement_widget.layerSpacing.setText(
                str(self.LayerSpacingTuple)
            )
        else:
            self.bottom_reinforcement_widget.layerSpacing.setText(
                str(self.LayerSpacingTuple)
            )

    def shearNumberDiameterOffsetEditButtonClicked(self, button):
        if (
            button
            == self.left_reinforcement_widget.numberDiameterOffsetEditButton
        ):
            number_diameter_offset_string = (
                self.left_reinforcement_widget.numberDiameterOffset.text()
            )
        else:
            number_diameter_offset_string = (
                self.right_reinforcement_widget.numberDiameterOffset.text()
            )

        ShearRebars_NumberDiameterOffset.runNumberDiameterOffsetDialog(
            self, number_diameter_offset_string
        )
        if (
            button
            == self.left_reinforcement_widget.numberDiameterOffsetEditButton
        ):
            self.left_reinforcement_widget.numberDiameterOffset.setText(
                self.NumberDiameterOffsetString
            )
            if not self.NumberDiameterOffsetString:
                self.left_reinforcement_widget.rebarType.setText("")
                self.left_reinforcement_widget.rebarTypeEditButton.setEnabled(
                    False
                )
                self.left_reinforcement_widget.hookOrientation.setText("")
                self.left_reinforcement_widget.hookOrientationEditButton.setEnabled(
                    False
                )
                self.left_reinforcement_widget.hookExtension.setText("")
                self.left_reinforcement_widget.hookExtensionEditButton.setEnabled(
                    False
                )
                self.left_reinforcement_widget.LRebarRounding.setText("")
                self.left_reinforcement_widget.LRebarRoundingEditButton.setEnabled(
                    False
                )
            else:
                if self.left_reinforcement_widget.rebarType.text():
                    rebar_type = ast.literal_eval(
                        self.left_reinforcement_widget.rebarType.text()
                    )
                else:
                    rebar_type = ()
                self.left_reinforcement_widget.rebarType.setText(
                    str(
                        self.getShearRebarType(
                            self.NumberDiameterOffsetString, rebar_type
                        )
                    )
                )
                self.left_reinforcement_widget.rebarTypeEditButton.setEnabled(
                    True
                )
                if self.left_reinforcement_widget.hookOrientation.text():
                    self.left_reinforcement_widget.hookOrientation.setText(
                        str(
                            self.getShearHookOrientation(
                                self.NumberDiameterOffsetString,
                                rebar_type,
                                ast.literal_eval(
                                    self.left_reinforcement_widget.hookOrientation.text()
                                ),
                            )
                        )
                    )
                else:
                    self.left_reinforcement_widget.hookOrientation.setText(
                        str(
                            self.getShearHookOrientation(
                                self.NumberDiameterOffsetString, rebar_type, ()
                            )
                        )
                    )
                self.left_reinforcement_widget.hookOrientationEditButton.setEnabled(
                    True
                )
                if self.left_reinforcement_widget.hookExtension.text():
                    self.left_reinforcement_widget.hookExtension.setText(
                        str(
                            self.getShearHookExtension(
                                self.NumberDiameterOffsetString,
                                rebar_type,
                                ast.literal_eval(
                                    self.left_reinforcement_widget.hookExtension.text()
                                ),
                            )
                        )
                    )
                else:
                    self.left_reinforcement_widget.hookExtension.setText(
                        str(
                            self.getShearHookExtension(
                                self.NumberDiameterOffsetString, rebar_type, ()
                            )
                        )
                    )
                self.left_reinforcement_widget.hookExtensionEditButton.setEnabled(
                    True
                )
                if self.left_reinforcement_widget.LRebarRounding.text():
                    self.left_reinforcement_widget.LRebarRounding.setText(
                        str(
                            self.getShearLRebarRounding(
                                self.NumberDiameterOffsetString,
                                rebar_type,
                                ast.literal_eval(
                                    self.left_reinforcement_widget.LRebarRounding.text()
                                ),
                            )
                        )
                    )
                else:
                    self.left_reinforcement_widget.LRebarRounding.setText(
                        str(
                            self.getShearLRebarRounding(
                                self.NumberDiameterOffsetString, rebar_type, ()
                            )
                        )
                    )
                self.left_reinforcement_widget.LRebarRoundingEditButton.setEnabled(
                    True
                )
        else:
            self.right_reinforcement_widget.numberDiameterOffset.setText(
                self.NumberDiameterOffsetString
            )
            if not self.NumberDiameterOffsetString:
                self.right_reinforcement_widget.rebarType.setText("")
                self.right_reinforcement_widget.rebarTypeEditButton.setEnabled(
                    False
                )
                self.right_reinforcement_widget.hookOrientation.setText("")
                self.right_reinforcement_widget.hookOrientationEditButton.setEnabled(
                    False
                )
                self.right_reinforcement_widget.hookExtension.setText("")
                self.right_reinforcement_widget.hookExtensionEditButton.setEnabled(
                    False
                )
                self.right_reinforcement_widget.LRebarRounding.setText("")
                self.right_reinforcement_widget.LRebarRoundingEditButton.setEnabled(
                    False
                )
            else:
                if self.right_reinforcement_widget.rebarType.text():
                    rebar_type = ast.literal_eval(
                        self.right_reinforcement_widget.rebarType.text()
                    )
                else:
                    rebar_type = ()
                self.right_reinforcement_widget.rebarType.setText(
                    str(
                        self.getShearRebarType(
                            self.NumberDiameterOffsetString, rebar_type
                        )
                    )
                )
                self.right_reinforcement_widget.rebarTypeEditButton.setEnabled(
                    True
                )
                if self.right_reinforcement_widget.hookOrientation.text():
                    self.right_reinforcement_widget.hookOrientation.setText(
                        str(
                            self.getShearHookOrientation(
                                self.NumberDiameterOffsetString,
                                rebar_type,
                                ast.literal_eval(
                                    self.right_reinforcement_widget.hookOrientation.text()
                                ),
                            )
                        )
                    )
                else:
                    self.right_reinforcement_widget.hookOrientation.setText(
                        str(
                            self.getShearHookOrientation(
                                self.NumberDiameterOffsetString, rebar_type, ()
                            )
                        )
                    )
                self.right_reinforcement_widget.hookOrientationEditButton.setEnabled(
                    True
                )
                if self.right_reinforcement_widget.hookExtension.text():
                    self.right_reinforcement_widget.hookExtension.setText(
                        str(
                            self.getShearHookExtension(
                                self.NumberDiameterOffsetString,
                                rebar_type,
                                ast.literal_eval(
                                    self.right_reinforcement_widget.hookExtension.text()
                                ),
                            )
                        )
                    )
                else:
                    self.right_reinforcement_widget.hookExtension.setText(
                        str(
                            self.getShearHookExtension(
                                self.NumberDiameterOffsetString, rebar_type, ()
                            )
                        )
                    )
                self.right_reinforcement_widget.hookExtensionEditButton.setEnabled(
                    True
                )
                if self.right_reinforcement_widget.LRebarRounding.text():
                    self.right_reinforcement_widget.LRebarRounding.setText(
                        str(
                            self.getShearLRebarRounding(
                                self.NumberDiameterOffsetString,
                                rebar_type,
                                ast.literal_eval(
                                    self.right_reinforcement_widget.LRebarRounding.text()
                                ),
                            )
                        )
                    )
                else:
                    self.right_reinforcement_widget.LRebarRounding.setText(
                        str(
                            self.getShearLRebarRounding(
                                self.NumberDiameterOffsetString, rebar_type, ()
                            )
                        )
                    )
                self.right_reinforcement_widget.LRebarRoundingEditButton.setEnabled(
                    True
                )

    def shearRebarTypeEditButtonClicked(self, button):
        if button == self.left_reinforcement_widget.rebarTypeEditButton:
            rebar_type = self.left_reinforcement_widget.rebarType.text()
        else:
            rebar_type = self.right_reinforcement_widget.rebarType.text()
        rebar_type_tuple = ast.literal_eval(rebar_type)
        ShearRebarTypeEditDialog.runRebarTypeEditDialog(self, rebar_type_tuple)
        if button == self.left_reinforcement_widget.rebarTypeEditButton:
            self.left_reinforcement_widget.rebarType.setText(
                str(self.RebarTypeTuple)
            )
            self.left_reinforcement_widget.hookOrientation.setText(
                str(
                    self.getShearHookOrientation(
                        self.left_reinforcement_widget.numberDiameterOffset.text(),
                        self.RebarTypeTuple,
                        ast.literal_eval(
                            self.left_reinforcement_widget.hookOrientation.text()
                        ),
                    )
                )
            )
            self.left_reinforcement_widget.hookExtension.setText(
                str(
                    self.getShearHookExtension(
                        self.left_reinforcement_widget.numberDiameterOffset.text(),
                        self.RebarTypeTuple,
                        ast.literal_eval(
                            self.left_reinforcement_widget.hookExtension.text()
                        ),
                    )
                )
            )
            self.left_reinforcement_widget.LRebarRounding.setText(
                str(
                    self.getShearLRebarRounding(
                        self.left_reinforcement_widget.numberDiameterOffset.text(),
                        self.RebarTypeTuple,
                        ast.literal_eval(
                            self.left_reinforcement_widget.LRebarRounding.text()
                        ),
                    )
                )
            )
        else:
            self.right_reinforcement_widget.rebarType.setText(
                str(self.RebarTypeTuple)
            )
            self.right_reinforcement_widget.hookOrientation.setText(
                str(
                    self.getShearHookOrientation(
                        self.right_reinforcement_widget.numberDiameterOffset.text(),
                        self.RebarTypeTuple,
                        ast.literal_eval(
                            self.right_reinforcement_widget.hookOrientation.text()
                        ),
                    )
                )
            )
            self.right_reinforcement_widget.hookExtension.setText(
                str(
                    self.getShearHookExtension(
                        self.right_reinforcement_widget.numberDiameterOffset.text(),
                        self.RebarTypeTuple,
                        ast.literal_eval(
                            self.right_reinforcement_widget.hookExtension.text()
                        ),
                    )
                )
            )
            self.right_reinforcement_widget.LRebarRounding.setText(
                str(
                    self.getShearLRebarRounding(
                        self.right_reinforcement_widget.numberDiameterOffset.text(),
                        self.RebarTypeTuple,
                        ast.literal_eval(
                            self.right_reinforcement_widget.LRebarRounding.text()
                        ),
                    )
                )
            )

    def shearHookOrientationEditButtonClicked(self, button):
        if button == self.left_reinforcement_widget.hookOrientationEditButton:
            hook_orientation = (
                self.left_reinforcement_widget.hookOrientation.text()
            )
        else:
            hook_orientation = (
                self.right_reinforcement_widget.hookOrientation.text()
            )
        hook_orientation_tuple = ast.literal_eval(hook_orientation)
        ShearRebars_HookOrientationEditDialog.runHookOrientationEditDialog(
            self, hook_orientation_tuple
        )
        if button == self.left_reinforcement_widget.hookOrientationEditButton:
            self.left_reinforcement_widget.hookOrientation.setText(
                str(self.HookOrientationTuple)
            )
        else:
            self.right_reinforcement_widget.hookOrientation.setText(
                str(self.HookOrientationTuple)
            )

    def shearHookExtensionEditButtonClicked(self, button):
        if button == self.left_reinforcement_widget.hookExtensionEditButton:
            hook_extension = self.left_reinforcement_widget.hookExtension.text()
        else:
            hook_extension = (
                self.right_reinforcement_widget.hookExtension.text()
            )
        hook_extension_tuple = ast.literal_eval(hook_extension)
        ShearRebars_HookExtensionEditDialog.runHookExtensionEditDialog(
            self, hook_extension_tuple
        )
        if button == self.left_reinforcement_widget.hookExtensionEditButton:
            self.left_reinforcement_widget.hookExtension.setText(
                str(self.HookExtensionTuple)
            )
        else:
            self.right_reinforcement_widget.hookExtension.setText(
                str(self.HookExtensionTuple)
            )

    def shearLRebarRoundingEditButtonClicked(self, button):
        if button == self.left_reinforcement_widget.LRebarRoundingEditButton:
            rounding = self.left_reinforcement_widget.LRebarRounding.text()
        else:
            rounding = self.right_reinforcement_widget.LRebarRounding.text()
        rounding_tuple = ast.literal_eval(rounding)
        ShearRebars_RoundingEditDialog.runRoundingEditDialog(
            self, rounding_tuple
        )
        if button == self.left_reinforcement_widget.LRebarRoundingEditButton:
            self.left_reinforcement_widget.LRebarRounding.setText(
                str(self.RoundingTuple)
            )
        else:
            self.right_reinforcement_widget.LRebarRounding.setText(
                str(self.RoundingTuple)
            )

    def getShearRebarType(
        self, number_diameter_offset_string, rebar_type_tuple
    ):
        sets = len(number_diameter_offset_string.split("+"))
        rebar_type_list = []
        for i in range(0, sets):
            if len(rebar_type_tuple) > i:
                rebar_type_list.append(rebar_type_tuple[i])
            else:
                rebar_type_list.append("StraightRebar")
        return tuple(rebar_type_list)

    def getShearHookOrientation(
        self,
        number_diameter_offset_string,
        rebar_type_tuple,
        hook_orientation_tuple,
    ):
        sets = len(number_diameter_offset_string.split("+"))
        hook_orientation_list = []
        for i in range(0, sets):
            if len(hook_orientation_tuple) > i:
                if rebar_type_tuple[i] == "StraightRebar":
                    hook_orientation_list.append(None)
                else:
                    if hook_orientation_tuple[i] is None:
                        hook_orientation_list.append("Front Inside")
                    else:
                        hook_orientation_list.append(hook_orientation_tuple[i])
            else:
                hook_orientation_list.append(None)
        return tuple(hook_orientation_list)

    def getShearHookExtension(
        self,
        number_diameter_offset_string,
        rebar_type_tuple,
        hook_extension_tuple,
    ):
        sets = len(number_diameter_offset_string.split("+"))
        hook_extension_list = []
        for i in range(0, sets):
            if len(hook_extension_tuple) > i:
                if rebar_type_tuple[i] == "StraightRebar":
                    hook_extension_list.append(None)
                else:
                    if hook_extension_tuple[i] is None:
                        hook_extension_list.append(40.0)
                    else:
                        hook_extension_list.append(hook_extension_tuple[i])
            else:
                hook_extension_list.append(None)
        return tuple(hook_extension_list)

    def getShearLRebarRounding(
        self, number_diameter_offset_string, rebar_type_tuple, rounding_tuple
    ):
        sets = len(number_diameter_offset_string.split("+"))
        rounding_list = []
        for i in range(0, sets):
            if len(rounding_tuple) > i:
                if rebar_type_tuple[i] == "StraightRebar":
                    rounding_list.append(None)
                else:
                    if rounding_tuple[i] is None:
                        rounding_list.append(2)
                    else:
                        rounding_list.append(rounding_tuple[i])
            else:
                rounding_list.append(None)
        return tuple(rounding_list)

    def nextButtonClicked(self):
        if self.form.next_button.text() == "Finish":
            self.accept()
        index = self.form.rebars_listWidget.currentRow()
        index += 1
        max_index = self.form.rebars_listWidget.count() - 1
        self.form.rebars_listWidget.setCurrentRow(min(index, max_index))

    def backButtonClicked(self):
        index = self.form.rebars_listWidget.currentRow()
        index -= 1
        self.form.rebars_listWidget.setCurrentRow(max(index, 0))

    def clicked(self, button):
        """This function is executed when 'Apply' button is clicked from UI."""
        if self.form.standardButtonBox.buttonRole(button) in (
            QtWidgets.QDialogButtonBox.AcceptRole,
            QtWidgets.QDialogButtonBox.ApplyRole,
        ):
            self.accept(button)

        elif (
            self.form.standardButtonBox.buttonRole(button)
            == QtWidgets.QDialogButtonBox.ResetRole
        ):
            self.reset()
        elif (
            self.form.standardButtonBox.buttonRole(button)
            == QtWidgets.QDialogButtonBox.RejectRole
        ):
            self.form.close()

    def accept(self, button=None):
        """This function is executed when 'OK' button is clicked from UI. It
        execute a function to create column reinforcement."""
        self.stirrups_configuration = (
            self.form.stirrups_configuration.currentText()
        )
        self.getStirrupsData()
        self.getTopReinforcementData()
        self.getBottomReinforcementData()
        self.getLeftReinforcementData()
        self.getRightReinforcementData()
        if not self.RebarGroup:
            if self.stirrups_configuration == "Two Legged Stirrups":
                RebarGroup = TwoLeggedBeam.makeReinforcement(
                    self.stirrups_l_cover,
                    self.stirrups_r_cover,
                    self.stirrups_t_cover,
                    self.stirrups_b_cover,
                    self.stirrups_offset,
                    self.stirrups_bent_angle,
                    self.stirrups_extension_factor,
                    self.stirrups_diameter,
                    self.stirrups_number_spacing_check,
                    self.stirrups_number_spacing_value,
                    self.top_number_diameter_offset,
                    self.top_rebar_type,
                    self.top_layer_spacing,
                    self.bottom_number_diameter_offset,
                    self.bottom_rebar_type,
                    self.bottom_layer_spacing,
                    self.left_number_diameter_offset,
                    self.left_rebar_type,
                    self.left_rebar_spacing,
                    self.right_number_diameter_offset,
                    self.right_rebar_type,
                    self.right_rebar_spacing,
                    self.top_lrebar_rounding,
                    self.top_hook_extension,
                    self.top_hook_orientation,
                    self.bottom_lrebar_rounding,
                    self.bottom_hook_extension,
                    self.bottom_hook_orientation,
                    self.left_lrebar_rounding,
                    self.left_hook_extension,
                    self.left_hook_orientation,
                    self.right_lrebar_rounding,
                    self.right_hook_extension,
                    self.right_hook_orientation,
                    self.SelectedObj,
                    self.FaceName,
                )
        else:
            if self.stirrups_configuration == "Two Legged Stirrups":
                RebarGroup = TwoLeggedBeam.editReinforcement(
                    self.RebarGroup,
                    self.stirrups_l_cover,
                    self.stirrups_r_cover,
                    self.stirrups_t_cover,
                    self.stirrups_b_cover,
                    self.stirrups_offset,
                    self.stirrups_bent_angle,
                    self.stirrups_extension_factor,
                    self.stirrups_diameter,
                    self.stirrups_number_spacing_check,
                    self.stirrups_number_spacing_value,
                    self.top_number_diameter_offset,
                    self.top_rebar_type,
                    self.top_layer_spacing,
                    self.bottom_number_diameter_offset,
                    self.bottom_rebar_type,
                    self.bottom_layer_spacing,
                    self.left_number_diameter_offset,
                    self.left_rebar_type,
                    self.left_rebar_spacing,
                    self.right_number_diameter_offset,
                    self.right_rebar_type,
                    self.right_rebar_spacing,
                    self.top_lrebar_rounding,
                    self.top_hook_extension,
                    self.top_hook_orientation,
                    self.bottom_lrebar_rounding,
                    self.bottom_hook_extension,
                    self.bottom_hook_orientation,
                    self.left_lrebar_rounding,
                    self.left_hook_extension,
                    self.left_hook_orientation,
                    self.right_lrebar_rounding,
                    self.right_hook_extension,
                    self.right_hook_orientation,
                    self.SelectedObj,
                    self.FaceName,
                )
        if self.CustomSpacing:
            if RebarGroup:
                for Stirrup in RebarGroup.ReinforcementGroups[0].Stirrups:
                    Stirrup.CustomSpacing = self.CustomSpacing
                FreeCAD.ActiveDocument.recompute()
        self.RebarGroup = RebarGroup
        if (
            self.form.standardButtonBox.buttonRole(button)
            != QtWidgets.QDialogButtonBox.ApplyRole
        ):
            self.form.close()

    def getStirrupsData(self):
        """This function is used to get data related to stirrups from UI."""
        self.stirrups_l_cover = self.stirrups_widget.stirrups_leftCover.text()
        self.stirrups_l_cover = FreeCAD.Units.Quantity(
            self.stirrups_l_cover
        ).Value
        self.stirrups_r_cover = self.stirrups_widget.stirrups_rightCover.text()
        self.stirrups_r_cover = FreeCAD.Units.Quantity(
            self.stirrups_r_cover
        ).Value
        self.stirrups_t_cover = self.stirrups_widget.stirrups_topCover.text()
        self.stirrups_t_cover = FreeCAD.Units.Quantity(
            self.stirrups_t_cover
        ).Value
        self.stirrups_b_cover = self.stirrups_widget.stirrups_bottomCover.text()
        self.stirrups_b_cover = FreeCAD.Units.Quantity(
            self.stirrups_b_cover
        ).Value
        self.stirrups_offset = self.stirrups_widget.stirrups_offset.text()
        self.stirrups_offset = FreeCAD.Units.Quantity(
            self.stirrups_offset
        ).Value
        self.stirrups_diameter = self.stirrups_widget.stirrups_diameter.text()
        self.stirrups_diameter = FreeCAD.Units.Quantity(
            self.stirrups_diameter
        ).Value
        self.stirrups_bent_angle = int(
            self.stirrups_widget.stirrups_bentAngle.currentText()
        )
        self.stirrups_extension_factor = (
            self.stirrups_widget.stirrups_extensionFactor.value()
        )
        self.stirrups_number_check = (
            self.stirrups_widget.stirrups_number_radio.isChecked()
        )
        if self.stirrups_number_check:
            self.stirrups_number_spacing_check = True
            self.stirrups_number_spacing_value = (
                self.stirrups_widget.stirrups_number.value()
            )
        else:
            self.stirrups_number_spacing_check = False
            self.stirrups_number_spacing_value = (
                self.stirrups_widget.stirrups_spacing.text()
            )
            self.stirrups_number_spacing_value = FreeCAD.Units.Quantity(
                self.stirrups_number_spacing_value
            ).Value

    def getTopReinforcementData(self):
        """This function is used to get data related to top reinforcement rebars
        from UI."""
        self.top_number_diameter_offset = ast.literal_eval(
            self.top_reinforcement_widget.numberDiameterOffset.toPlainText()
        )
        self.top_rebar_type = ast.literal_eval(
            self.top_reinforcement_widget.rebarType.toPlainText()
        )
        self.top_hook_orientation = ast.literal_eval(
            self.top_reinforcement_widget.hookOrientation.toPlainText()
        )
        self.top_hook_extension = ast.literal_eval(
            self.top_reinforcement_widget.hookExtension.toPlainText()
        )
        self.top_lrebar_rounding = ast.literal_eval(
            self.top_reinforcement_widget.LRebarRounding.toPlainText()
        )
        self.top_layer_spacing = ast.literal_eval(
            self.top_reinforcement_widget.layerSpacing.text()
        )

    def getBottomReinforcementData(self):
        """This function is used to get data related to bottom reinforcement
        rebars from UI."""
        self.bottom_number_diameter_offset = ast.literal_eval(
            self.bottom_reinforcement_widget.numberDiameterOffset.toPlainText()
        )
        self.bottom_rebar_type = ast.literal_eval(
            self.bottom_reinforcement_widget.rebarType.toPlainText()
        )
        self.bottom_hook_orientation = ast.literal_eval(
            self.bottom_reinforcement_widget.hookOrientation.toPlainText()
        )
        self.bottom_hook_extension = ast.literal_eval(
            self.bottom_reinforcement_widget.hookExtension.toPlainText()
        )
        self.bottom_lrebar_rounding = ast.literal_eval(
            self.bottom_reinforcement_widget.LRebarRounding.toPlainText()
        )
        self.bottom_layer_spacing = ast.literal_eval(
            self.bottom_reinforcement_widget.layerSpacing.text()
        )

    def getLeftReinforcementData(self):
        """This function is used to get data related to left reinforcement
        rebars from UI."""
        self.left_number_diameter_offset = (
            self.left_reinforcement_widget.numberDiameterOffset.text()
        )
        if self.left_reinforcement_widget.rebarType.text():
            self.left_rebar_type = ast.literal_eval(
                self.left_reinforcement_widget.rebarType.text()
            )
        else:
            self.left_rebar_type = ()
        if self.left_reinforcement_widget.hookOrientation.text():
            self.left_hook_orientation = ast.literal_eval(
                self.left_reinforcement_widget.hookOrientation.text()
            )
        else:
            self.left_hook_orientation = ()
        if self.left_reinforcement_widget.hookExtension.text():
            self.left_hook_extension = ast.literal_eval(
                self.left_reinforcement_widget.hookExtension.text()
            )
        else:
            self.left_hook_extension = ()
        if self.left_reinforcement_widget.LRebarRounding.text():
            self.left_lrebar_rounding = ast.literal_eval(
                self.left_reinforcement_widget.LRebarRounding.text()
            )
        else:
            self.left_lrebar_rounding = ()
        self.left_rebar_spacing = (
            self.left_reinforcement_widget.rebarSpacing.text()
        )
        self.left_rebar_spacing = FreeCAD.Units.Quantity(
            self.left_rebar_spacing
        ).Value

    def getRightReinforcementData(self):
        """This function is used to get data related to right reinforcement
        rebars from UI."""
        self.right_number_diameter_offset = (
            self.right_reinforcement_widget.numberDiameterOffset.text()
        )
        if self.right_reinforcement_widget.rebarType.text():
            self.right_rebar_type = ast.literal_eval(
                self.right_reinforcement_widget.rebarType.text()
            )
        else:
            self.right_rebar_type = ()
        if self.right_reinforcement_widget.hookOrientation.text():
            self.right_hook_orientation = ast.literal_eval(
                self.right_reinforcement_widget.hookOrientation.text()
            )
        else:
            self.right_hook_orientation = ()
        if self.right_reinforcement_widget.hookExtension.text():
            self.right_hook_extension = ast.literal_eval(
                self.right_reinforcement_widget.hookExtension.text()
            )
        else:
            self.right_hook_extension = ()
        if self.right_reinforcement_widget.LRebarRounding.text():
            self.right_lrebar_rounding = ast.literal_eval(
                self.right_reinforcement_widget.LRebarRounding.text()
            )
        else:
            self.right_lrebar_rounding = ()
        self.right_rebar_spacing = (
            self.right_reinforcement_widget.rebarSpacing.text()
        )
        self.right_rebar_spacing = FreeCAD.Units.Quantity(
            self.right_rebar_spacing
        ).Value

    def reset(self):
        if not self.RebarGroup:
            self.setDefaultValues()
        else:
            setStirrupsData(self, None)
            setTopReinforcementData(self, None)
            setBottomReinforcementData(self, None)
            setShearRebarsData(self, None)


def editDialog(vobj):
    # Check if all rebar groups deleted or not
    if len(vobj.Object.ReinforcementGroups) == 0:
        showWarning("Nothing to edit. You have deleted all rebar groups.")
        return
    for rebar_group in vobj.Object.ReinforcementGroups:
        # Check if stirrups group exists
        if hasattr(rebar_group, "Stirrups"):
            # Check if Stirrups exists
            if len(rebar_group.Stirrups) > 0:
                stirrups_group = rebar_group
                break
            else:
                showWarning(
                    "You have deleted stirrups. Please recreate the "
                    "BeamReinforcement."
                )
                return
        else:
            showWarning(
                "You have deleted stirrups group. Please recreate the "
                "BeamReinforcement."
            )
            return
    obj = _BeamReinforcementDialog(vobj.Object)
    obj.setupUi()
    obj.form.stirrups_configuration.setCurrentIndex(
        obj.form.stirrups_configuration.findText(
            str(stirrups_group.StirrupsConfiguration)
        )
    )
    setStirrupsData(obj, vobj)
    setTopReinforcementData(obj, vobj)
    setBottomReinforcementData(obj, vobj)
    setShearRebarsData(obj, vobj)
    obj.form.exec_()


def setStirrupsData(obj, vobj):
    if vobj:
        for rebar_group in vobj.Object.ReinforcementGroups:
            if hasattr(rebar_group, "Stirrups"):
                Stirrups = rebar_group
                break
    else:
        for rebar_group in obj.RebarGroup.ReinforcementGroups:
            if hasattr(rebar_group, "Stirrups"):
                Stirrups = rebar_group
                break
    Stirrup = Stirrups.Stirrups[0]
    if not (
        str(Stirrup.LeftCover)
        == str(Stirrup.RightCover)
        == str(Stirrup.TopCover)
        == str(Stirrup.BottomCover)
    ):
        obj.stirrups_widget.stirrups_allCoversEqual.setChecked(False)
        obj.stirrupsAllCoversEqualClicked()
        obj.stirrups_widget.stirrups_rightCover.setEnabled(True)
        obj.stirrups_widget.stirrups_topCover.setEnabled(True)
        obj.stirrups_widget.stirrups_bottomCover.setEnabled(True)
    obj.stirrups_widget.stirrups_leftCover.setText(str(Stirrup.LeftCover))
    obj.stirrups_widget.stirrups_rightCover.setText(str(Stirrup.RightCover))
    obj.stirrups_widget.stirrups_topCover.setText(str(Stirrup.TopCover))
    obj.stirrups_widget.stirrups_bottomCover.setText(str(Stirrup.BottomCover))
    obj.stirrups_widget.stirrups_offset.setText(str(Stirrup.FrontCover))
    obj.stirrups_widget.stirrups_diameter.setText(str(Stirrup.Diameter))
    obj.stirrups_widget.stirrups_bentAngle.setCurrentIndex(
        obj.stirrups_widget.stirrups_bentAngle.findText(str(Stirrup.BentAngle))
    )
    obj.stirrups_widget.stirrups_extensionFactor.setValue(Stirrup.BentFactor)
    if Stirrup.AmountCheck:
        obj.stirrups_widget.stirrups_number_radio.setChecked(True)
        obj.stirrups_widget.stirrups_spacing_radio.setChecked(False)
        obj.stirrups_widget.stirrups_number.setEnabled(True)
        obj.stirrups_widget.stirrups_spacing.setEnabled(False)
        obj.stirrups_widget.stirrups_number.setValue(Stirrup.Amount)
    else:
        obj.stirrups_widget.stirrups_number_radio.setChecked(False)
        obj.stirrups_widget.stirrups_spacing_radio.setChecked(True)
        obj.stirrups_widget.stirrups_number.setEnabled(False)
        obj.stirrups_widget.stirrups_spacing.setEnabled(True)
        obj.stirrups_widget.stirrups_spacing.setText(str(Stirrup.TrueSpacing))


def setTopReinforcementData(obj, vobj):
    if vobj:
        for rebar_group in vobj.Object.ReinforcementGroups:
            if hasattr(rebar_group, "TopRebars"):
                TopReinforcementGroup = rebar_group
                break
    else:
        for rebar_group in obj.RebarGroup.ReinforcementGroups:
            if hasattr(rebar_group, "TopRebars"):
                TopReinforcementGroup = rebar_group
                break
    obj.top_reinforcement_widget.numberDiameterOffset.setPlainText(
        str(tuple(TopReinforcementGroup.NumberDiameterOffset))
    )
    obj.top_reinforcement_widget.rebarType.setPlainText(
        str(TopReinforcementGroup.RebarType)
    )
    obj.top_reinforcement_widget.hookOrientation.setPlainText(
        str(TopReinforcementGroup.HookOrientation)
    )
    obj.top_reinforcement_widget.hookExtension.setPlainText(
        str(TopReinforcementGroup.HookExtension)
    )
    obj.top_reinforcement_widget.LRebarRounding.setPlainText(
        str(TopReinforcementGroup.LRebarRounding)
    )
    obj.top_reinforcement_widget.layers.setValue(
        len(ast.literal_eval(TopReinforcementGroup.RebarType))
    )
    obj.top_reinforcement_widget.layerSpacing.setText(
        str(tuple(TopReinforcementGroup.LayerSpacing))
    )


def setBottomReinforcementData(obj, vobj):
    if vobj:
        for rebar_group in vobj.Object.ReinforcementGroups:
            if hasattr(rebar_group, "BottomRebars"):
                BottomReinforcementGroup = rebar_group
                break
    else:
        for rebar_group in obj.RebarGroup.ReinforcementGroups:
            if hasattr(rebar_group, "BottomRebars"):
                BottomReinforcementGroup = rebar_group
                break
    obj.bottom_reinforcement_widget.numberDiameterOffset.setPlainText(
        str(tuple(BottomReinforcementGroup.NumberDiameterOffset))
    )
    obj.bottom_reinforcement_widget.rebarType.setPlainText(
        str(BottomReinforcementGroup.RebarType)
    )
    obj.bottom_reinforcement_widget.hookOrientation.setPlainText(
        str(BottomReinforcementGroup.HookOrientation)
    )
    obj.bottom_reinforcement_widget.hookExtension.setPlainText(
        str(BottomReinforcementGroup.HookExtension)
    )
    obj.bottom_reinforcement_widget.LRebarRounding.setPlainText(
        str(BottomReinforcementGroup.LRebarRounding)
    )
    obj.bottom_reinforcement_widget.layers.setValue(
        len(ast.literal_eval(BottomReinforcementGroup.RebarType))
    )
    obj.bottom_reinforcement_widget.layerSpacing.setText(
        str(tuple(BottomReinforcementGroup.LayerSpacing))
    )


def setShearRebarsData(obj, vobj):
    LeftRebarsGroup = None
    RightRebarsGroup = None
    if vobj:
        for rebar_group in vobj.Object.ReinforcementGroups:
            if hasattr(rebar_group, "ShearReinforcementGroups"):
                for shear_rebars_group in rebar_group.ShearReinforcementGroups:
                    if hasattr(shear_rebars_group, "LeftRebars"):
                        LeftRebarsGroup = shear_rebars_group
                    elif hasattr(shear_rebars_group, "RightRebars"):
                        RightRebarsGroup = shear_rebars_group
                break
    else:
        for rebar_group in obj.RebarGroup.ReinforcementGroups:
            if hasattr(rebar_group, "ShearReinforcementGroups"):
                for shear_rebars_group in rebar_group.ShearReinforcementGroups:
                    if hasattr(shear_rebars_group, "LeftRebars"):
                        LeftRebarsGroup = shear_rebars_group
                    elif hasattr(shear_rebars_group, "RightRebars"):
                        RightRebarsGroup = shear_rebars_group
                break
    if not LeftRebarsGroup:
        obj.left_reinforcement_widget.numberDiameterOffset.setText("")
        obj.left_reinforcement_widget.rebarType.setText("")
        obj.left_reinforcement_widget.hookOrientation.setText("")
        obj.left_reinforcement_widget.hookExtension.setText("")
        obj.left_reinforcement_widget.LRebarRounding.setText("")
        obj.left_reinforcement_widget.rebarSpacing.setText("")
    else:
        obj.left_reinforcement_widget.numberDiameterOffset.setText(
            str(LeftRebarsGroup.NumberDiameterOffset)
        )
        obj.left_reinforcement_widget.rebarType.setText(
            str(LeftRebarsGroup.RebarType)
        )
        obj.left_reinforcement_widget.hookOrientation.setText(
            str(
                tuple(
                    [
                        None if not orientation else orientation
                        for orientation in LeftRebarsGroup.HookOrientation
                    ]
                )
            )
        )
        obj.left_reinforcement_widget.hookExtension.setText(
            str(
                tuple(
                    [
                        None if not extension else extension
                        for extension in LeftRebarsGroup.HookExtension
                    ]
                )
            )
        )
        obj.left_reinforcement_widget.LRebarRounding.setText(
            str(
                tuple(
                    [
                        None if not rounding else rounding
                        for rounding in LeftRebarsGroup.LRebarRounding
                    ]
                )
            )
        )
        obj.left_reinforcement_widget.rebarSpacing.setText(
            str(LeftRebarsGroup.RebarSpacing)
        )
        obj.left_reinforcement_widget.rebarTypeEditButton.setEnabled(True)
        obj.left_reinforcement_widget.hookOrientationEditButton.setEnabled(True)
        obj.left_reinforcement_widget.hookExtensionEditButton.setEnabled(True)
        obj.left_reinforcement_widget.LRebarRoundingEditButton.setEnabled(True)
    if not RightRebarsGroup:
        obj.right_reinforcement_widget.numberDiameterOffset.setText("")
        obj.right_reinforcement_widget.rebarType.setText("")
        obj.right_reinforcement_widget.hookOrientation.setText("")
        obj.right_reinforcement_widget.hookExtension.setText("")
        obj.right_reinforcement_widget.LRebarRounding.setText("")
        obj.right_reinforcement_widget.rebarSpacing.setText("")
    else:
        obj.right_reinforcement_widget.numberDiameterOffset.setText(
            str(RightRebarsGroup.NumberDiameterOffset)
        )
        obj.right_reinforcement_widget.rebarType.setText(
            str(RightRebarsGroup.RebarType)
        )
        obj.right_reinforcement_widget.hookOrientation.setText(
            str(
                tuple(
                    [
                        None if not orientation else orientation
                        for orientation in RightRebarsGroup.HookOrientation
                    ]
                )
            )
        )
        obj.right_reinforcement_widget.hookExtension.setText(
            str(
                tuple(
                    [
                        None if not extension else extension
                        for extension in RightRebarsGroup.HookExtension
                    ]
                )
            )
        )
        obj.right_reinforcement_widget.LRebarRounding.setText(
            str(
                tuple(
                    [
                        None if not rounding else rounding
                        for rounding in RightRebarsGroup.LRebarRounding
                    ]
                )
            )
        )
        obj.right_reinforcement_widget.rebarSpacing.setText(
            str(RightRebarsGroup.RebarSpacing)
        )
        obj.right_reinforcement_widget.rebarTypeEditButton.setEnabled(True)
        obj.right_reinforcement_widget.hookOrientationEditButton.setEnabled(
            True
        )
        obj.right_reinforcement_widget.hookExtensionEditButton.setEnabled(True)
        obj.right_reinforcement_widget.LRebarRoundingEditButton.setEnabled(True)


def CommandBeamReinforcement():
    """This function is used to invoke dialog box for beam reinforcement."""
    selected_obj = check_selected_face()
    if selected_obj:
        dialog = _BeamReinforcementDialog()
        dialog.setupUi()
        dialog.form.exec_()
