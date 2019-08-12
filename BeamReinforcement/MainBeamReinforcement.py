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

__title__ = "Beam Reinforcement"
__author__ = "Suraj"
__url__ = "https://www.freecadweb.org"

import os
from PySide2 import QtWidgets

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
                "RebarAddon", "Beam Reinforcement", None
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
        # Set Stirrups data Widget in Scroll Area
        self.stirrups_widget.stirrups_scrollArea.setWidget(
            self.stirrups_widget.stirrups_dataWidget
        )
        # Connect signals and slots
        self.connectSignalSlots()

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
        import ast

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

    def rebarTypeEditButtonClicked(self, button):
        if button == self.top_reinforcement_widget.rebarTypeEditButton:
            rebar_type = self.top_reinforcement_widget.rebarType.toPlainText()
        else:
            rebar_type = (
                self.bottom_reinforcement_widget.rebarType.toPlainText()
            )
        import ast

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
        import ast

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
        import ast

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
        import ast

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
        print("WIP")
        if (
            self.form.standardButtonBox.buttonRole(button)
            != QtWidgets.QDialogButtonBox.ApplyRole
        ):
            self.form.close()

    def reset(self):
        print("WIP")


def CommandBeamReinforcement():
    """This function is used to invoke dialog box for beam reinforcement."""
    selected_obj = check_selected_face()
    if selected_obj:
        dialog = _BeamReinforcementDialog()
        dialog.setupUi()
        dialog.form.exec_()
