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

import os
import ast
from PySide2 import QtWidgets, QtGui

import FreeCAD
import FreeCADGui

from Rebarfunc import check_selected_face
from BeamReinforcement.NumberDiameterOffset import runNumberDiameterOffsetDialog
from BeamReinforcement.RebarTypeEditDialog import runRebarTypeEditDialog
from BeamReinforcement.HookOrientationEditDialog import (
    runHookOrientationEditDialog,
)
from BeamReinforcement.HookExtensionEditDialog import runHookExtensionEditDialog
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
        self.CustomSpacing = None
        if not RebarGroup:
            # If beam reinforcement is not created yet, then get SelectedObj
            # from FreeCAD Gui selection
            selected_obj = FreeCADGui.Selection.getSelectionEx()[0]
            self.SelectedObj = selected_obj.Object
            self.FaceName = selected_obj.SubElementNames[0]

        # Load ui from file MainBeamReinforcement.ui
        self.form = FreeCADGui.PySideUic.loadUi(
            os.path.splitext(__file__)[0] + ".ui"
        )
        self.form.setWindowTitle(
            QtWidgets.QApplication.translate(
                "RebarAddon", "Beam Reinforcement Dialog Box", None
            )
        )
        self.RebarGroup = RebarGroup

    def setupUi(self):
        """This function is used to add components to ui."""
        # Add items into rebars_listWidget
        self.form.rebars_listWidget.addItem("Stirrups")
        self.form.rebars_listWidget.addItem("Top Reinforcement")
        self.form.rebars_listWidget.addItem("Bottom Reinforcement")
        self.form.rebars_listWidget.addItem("Left Reinforcement")
        self.form.rebars_listWidget.addItem("Right Reinforcement")
        self.form.rebars_listWidget.setCurrentRow(0)
        # Load and add widgets into stacked widget
        self.stirrups_widget = FreeCADGui.PySideUic.loadUi(
            os.path.split(os.path.abspath(__file__))[0] + "/Stirrups.ui"
        )
        self.form.rebars_stackedWidget.addWidget(self.stirrups_widget)
        self.top_reinforcement_widget = FreeCADGui.PySideUic.loadUi(
            os.path.split(os.path.abspath(__file__))[0]
            + "/TopBottomReinforcement.ui"
        )
        self.form.rebars_stackedWidget.addWidget(self.top_reinforcement_widget)
        self.bottom_reinforcement_widget = FreeCADGui.PySideUic.loadUi(
            os.path.split(os.path.abspath(__file__))[0]
            + "/TopBottomReinforcement.ui"
        )
        self.form.rebars_stackedWidget.addWidget(
            self.bottom_reinforcement_widget
        )
        self.left_reinforcement_widget = FreeCADGui.PySideUic.loadUi(
            os.path.split(os.path.abspath(__file__))[0]
            + "/LeftRightReinforcement.ui"
        )
        self.form.rebars_stackedWidget.addWidget(self.left_reinforcement_widget)
        self.right_reinforcement_widget = FreeCADGui.PySideUic.loadUi(
            os.path.split(os.path.abspath(__file__))[0]
            + "/LeftRightReinforcement.ui"
        )
        self.form.rebars_stackedWidget.addWidget(
            self.right_reinforcement_widget
        )
        # Add dropdown menu items
        self.addDropdownMenuItems()
        # Add image of Two Legged Stirrup
        self.stirrups_widget.stirrups_configurationImage.setPixmap(
            QtGui.QPixmap(
                os.path.split(os.path.split(os.path.abspath(__file__))[0])[0]
                + "/icons/Beam_TwoLeggedStirrups.png"
            )
        )
        self.top_reinforcement_widget.stirrups_configurationImage.setPixmap(
            QtGui.QPixmap(
                os.path.split(os.path.split(os.path.abspath(__file__))[0])[0]
                + "/icons/Beam_TwoLeggedStirrups.png"
            )
        )
        self.bottom_reinforcement_widget.stirrups_configurationImage.setPixmap(
            QtGui.QPixmap(
                os.path.split(os.path.split(os.path.abspath(__file__))[0])[0]
                + "/icons/Beam_TwoLeggedStirrups.png"
            )
        )
        self.left_reinforcement_widget.stirrups_configurationImage.setPixmap(
            QtGui.QPixmap(
                os.path.split(os.path.split(os.path.abspath(__file__))[0])[0]
                + "/icons/Beam_TwoLeggedStirrups.png"
            )
        )
        self.right_reinforcement_widget.stirrups_configurationImage.setPixmap(
            QtGui.QPixmap(
                os.path.split(os.path.split(os.path.abspath(__file__))[0])[0]
                + "/icons/Beam_TwoLeggedStirrups.png"
            )
        )
        # Set Stirrups data Widget in Scroll Area
        self.stirrups_widget.stirrups_scrollArea.setWidget(
            self.stirrups_widget.stirrups_dataWidget
        )
        # Connect signals and slots
        self.connectSignalSlots()

    def addDropdownMenuItems(self):
        """This function add dropdown items to each Gui::PrefComboBox."""
        self.stirrups_widget.stirrups_configuration.addItems(
            ["Two Legged Stirrups"]
        )
        self.top_reinforcement_widget.stirrups_configuration.addItems(
            ["Two Legged Stirrups"]
        )
        self.bottom_reinforcement_widget.stirrups_configuration.addItems(
            ["Two Legged Stirrups"]
        )
        self.left_reinforcement_widget.stirrups_configuration.addItems(
            ["Two Legged Stirrups"]
        )
        self.right_reinforcement_widget.stirrups_configuration.addItems(
            ["Two Legged Stirrups"]
        )
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
        self.form.next_button.clicked.connect(self.nextButtonCilcked)
        self.form.back_button.clicked.connect(self.backButtonCilcked)
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
        left_cover = self.stirrups_widget.stirrups_leftCover.text()
        self.stirrups_widget.stirrups_rightCover.setText(left_cover)
        self.stirrups_widget.stirrups_topCover.setText(left_cover)
        self.stirrups_widget.stirrups_bottomCover.setText(left_cover)

    def stirrupsAllCoversEqualClicked(self):
        if self.stirrups_widget.stirrups_allCoversEqual.isChecked():
            # Diable fields for right/top/bottom cover
            self.stirrups_widget.stirrups_rightCover.setEnabled(False)
            self.stirrups_widget.stirrups_topCover.setEnabled(False)
            self.stirrups_widget.stirrups_bottomCover.setEnabled(False)
            # Set right/top/bottom cover equal to left cover
            self.stirrupsLeftCoverChanged()
            self.stirrups_widget.stirrups_leftCover.textChanged.connect(
                self.stirrupsLeftCoverChanged
            )
        else:
            self.stirrups_widget.stirrups_rightCover.setEnabled(True)
            self.stirrups_widget.stirrups_topCover.setEnabled(True)
            self.stirrups_widget.stirrups_bottomCover.setEnabled(True)
            self.stirrups_widget.stirrups_leftCover.textChanged.disconnect(
                self.stirrupsLeftCoverChanged
            )

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
            for Stirrup in self.RebarGroup.RebarGroups[0].Stirrups:
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

    def getRebarType(self, number_diameter_offset_tuple, rebar_type_tuple):
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

    def getHookOrientation(
        self,
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
                            if hook_orientation_tuple[layer - 1][i] == None:
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

    def getHookExtension(
        self,
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
                            if hook_extension_tuple[layer - 1][i] == None:
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

    def getLRebarRounding(
        self, number_diameter_offset_tuple, rebar_type_tuple, rounding_tuple
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
                            if rounding_tuple[layer - 1][i] == None:
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

    def getLayerSpacing(
        self, number_diameter_offset_tuple, layer_spacing_tuple
    ):
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
            rebar_type = ast.literal_eval(
                self.left_reinforcement_widget.rebarType.text()
            )
            self.left_reinforcement_widget.rebarType.setText(
                str(
                    self.getShearRebarType(
                        self.NumberDiameterOffsetString, rebar_type
                    )
                )
            )
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
            self.right_reinforcement_widget.numberDiameterOffset.setText(
                self.NumberDiameterOffsetString
            )
            rebar_type = ast.literal_eval(
                self.right_reinforcement_widget.rebarType.text()
            )
            self.right_reinforcement_widget.rebarType.setText(
                str(
                    self.getShearRebarType(
                        self.NumberDiameterOffsetString, rebar_type
                    )
                )
            )
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
                    if hook_orientation_tuple[i] == None:
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
                    if hook_extension_tuple[i] == None:
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
                    if rounding_tuple[i] == None:
                        rounding_list.append(2)
                    else:
                        rounding_list.append(rounding_tuple[i])
            else:
                rounding_list.append(None)
        return tuple(rounding_list)

    def nextButtonCilcked(self):
        if self.form.next_button.text() == "Finish":
            self.accept()
        index = self.form.rebars_listWidget.currentRow()
        index += 1
        max_index = self.form.rebars_listWidget.count() - 1
        if index <= max_index:
            self.form.rebars_listWidget.setCurrentRow(index)

    def backButtonCilcked(self):
        index = self.form.rebars_listWidget.currentRow()
        index -= 1
        if index >= 0:
            self.form.rebars_listWidget.setCurrentRow(index)

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
            self.stirrups_widget.stirrups_configuration.currentText()
        )
        if not self.RebarGroup:
            if self.stirrups_configuration == "Two Legged Stirrups":
                self.getStirrupsData()
                self.getTopReinforcementData()
                self.getBottomReinforcementData()
                self.getLeftReinforcementData()
                self.getRightReinforcementData()
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
        if self.CustomSpacing:
            if RebarGroup:
                for Stirrup in RebarGroup.RebarGroups[0].Stirrups:
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
        self.left_rebar_type = ast.literal_eval(
            self.left_reinforcement_widget.rebarType.text()
        )
        self.left_hook_orientation = ast.literal_eval(
            self.left_reinforcement_widget.hookOrientation.text()
        )
        self.left_hook_extension = ast.literal_eval(
            self.left_reinforcement_widget.hookExtension.text()
        )
        self.left_lrebar_rounding = ast.literal_eval(
            self.left_reinforcement_widget.LRebarRounding.text()
        )
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
        self.right_rebar_type = ast.literal_eval(
            self.right_reinforcement_widget.rebarType.text()
        )
        self.right_hook_orientation = ast.literal_eval(
            self.right_reinforcement_widget.hookOrientation.text()
        )
        self.right_hook_extension = ast.literal_eval(
            self.right_reinforcement_widget.hookExtension.text()
        )
        self.right_lrebar_rounding = ast.literal_eval(
            self.right_reinforcement_widget.LRebarRounding.text()
        )
        self.right_rebar_spacing = (
            self.right_reinforcement_widget.rebarSpacing.text()
        )
        self.right_rebar_spacing = FreeCAD.Units.Quantity(
            self.right_rebar_spacing
        ).Value

    def reset(self):
        print("WIP")


def CommandBeamReinforcement():
    """This function is used to invoke dialog box for beam reinforcement."""
    selected_obj = check_selected_face()
    if selected_obj:
        dialog = _BeamReinforcementDialog()
        dialog.setupUi()
        dialog.form.exec_()
