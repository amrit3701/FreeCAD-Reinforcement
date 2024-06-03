# -*- coding: utf-8 -*-
# ***************************************************************************
# *                                                                         *
# *   Copyright (c) 2019 - Shiv Charan <shivcharanmt@gmail.com>                      *
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

__title__ = "Slab Reinforcement"
__author__ = "Shiv Charan"
__url__ = "https://www.freecadweb.org"

from pathlib import Path
from PySide2 import QtWidgets

import FreeCAD
import FreeCADGui

from Rebarfunc import (
    check_selected_face,
    facenormalDirection,
    showWarning
)
from SlabReinforcement.SlabReinforcement import (
    makeSlabReinforcement,
    editSlabReinforcement,
)
from RebarData import ReinforcementHelpLinks


class _SlabReinforcementDialog:
    def __init__(self, SlabReinforcementGroup=None):
        """This function set initial data in Slab Reinforcement dialog box."""
        # Load ui from file MainSlabReinforcement.ui
        if not SlabReinforcementGroup:
            selected_obj = FreeCADGui.Selection.getSelectionEx()[0]
            self.SelectedObj = selected_obj.Object
            self.FaceName = selected_obj.SubElementNames[0]
        else:
            self.SelectedObj = SlabReinforcementGroup.Structure
            self.FaceName = SlabReinforcementGroup.Facename

        self.form = FreeCADGui.PySideUic.loadUi(
            str(Path(__file__).with_suffix(".ui").absolute())
        )
        self.form.setWindowTitle(
            QtWidgets.QApplication.translate(
                "RebarWorkbench", "Slab Reinforcement", None
            )
        )
        self.SlabReinforcementGroup = SlabReinforcementGroup

    def setupUi(self):
        """This function is used to add components to ui."""
        # Load and add widgets into stacked widget
        self.parallel_rebars_widget = FreeCADGui.PySideUic.loadUi(
            str(Path(__file__).parent.absolute() / "ParallelRebars.ui")
        )
        self.form.rebars_stackedWidget.addWidget(self.parallel_rebars_widget)

        self.cross_rebars_widget = FreeCADGui.PySideUic.loadUi(
            str(Path(__file__).parent.absolute() / "CrossRebars.ui")
        )
        self.form.rebars_stackedWidget.addWidget(self.cross_rebars_widget)

        # Add dropdown menu items
        self.addDropdownMenuItems()
        self.setDefaultValues()
        # # Connect signals and slots
        self.connectSignalSlots()

    def setDefaultValues(self):
        self.form.rebars_listWidget.setCurrentRow(0)
        self.parallel_rebars_widget.meshCoverAlongValue.setCurrentIndex(
            self.parallel_rebars_widget.meshCoverAlongValue.findText("Bottom")
        )
        self.parallel_rebars_widget.parallel_l_shapeHookOrientation.setCurrentIndex(
            self.parallel_rebars_widget.parallel_l_shapeHookOrientation.findText(
                "Left"
            )
        )
        self.parallel_rebars_widget.parallel_rebars_type.setCurrentIndex(
            self.parallel_rebars_widget.parallel_rebars_type.findText(
                "StraightRebar"
            )
        )
        self.changeParallelRebarType()
        self.parallel_rebars_widget.parallel_frontCover.setText("20 mm")
        self.parallel_rebars_widget.parallel_l_sideCover.setText("10 mm")
        self.parallel_rebars_widget.parallel_r_sideCover.setText("10 mm")
        self.parallel_rebars_widget.parallel_bottomCover.setText("20 mm")
        self.parallel_rebars_widget.parallel_topCover.setText("20 mm")
        self.parallel_rebars_widget.parallel_rearCover.setText("20 mm")
        self.parallel_rebars_widget.parallel_bentLength.setText("50 mm")
        self.parallel_rebars_widget.parallel_bentAngle.setValue(135)
        self.parallel_rebars_widget.parallel_rounding.setValue(2)
        self.parallel_rebars_widget.parallel_diameter.setText("8 mm")
        self.parallel_rebars_widget.parallel_amount_radio.setChecked(True)
        self.parallel_rebars_widget.parallel_spacing_radio.setChecked(False)
        self.parallel_rebars_widget.parallel_amount.setValue(3)
        self.parallel_rebars_widget.parallel_spacing.setText("50 mm")
        self.parallel_rebars_widget.parallel_distribution_rebar_check.setChecked(
            False
        )

        self.cross_rebars_widget.cross_l_shapeHookOrientation.setCurrentIndex(
            self.cross_rebars_widget.cross_l_shapeHookOrientation.findText(
                "Left"
            )
        )
        self.cross_rebars_widget.cross_rebars_type.setCurrentIndex(
            self.cross_rebars_widget.cross_rebars_type.findText("StraightRebar")
        )
        self.changeCrossRebarType()
        self.cross_rebars_widget.cross_frontCover.setText("20 mm")
        self.cross_rebars_widget.cross_l_sideCover.setText("10 mm")
        self.cross_rebars_widget.cross_r_sideCover.setText("10 mm")
        self.cross_rebars_widget.cross_bottomCover.setText("20 mm")
        self.cross_rebars_widget.cross_topCover.setText("20 mm")
        self.cross_rebars_widget.cross_rearCover.setText("20 mm")
        self.cross_rebars_widget.cross_bentLength.setText("50 mm")
        self.cross_rebars_widget.cross_bentAngle.setValue(135)
        self.cross_rebars_widget.cross_rounding.setValue(2)
        self.cross_rebars_widget.cross_diameter.setText("8 mm")
        self.cross_rebars_widget.cross_amount_radio.setChecked(True)
        self.cross_rebars_widget.cross_spacing_radio.setChecked(False)
        self.cross_rebars_widget.cross_amount.setValue(3)
        self.cross_rebars_widget.cross_spacing.setText("50 mm")
        self.cross_rebars_widget.cross_distribution_rebar_check.setChecked(
            False
        )
        self.cross_rebars_widget.cross_distribution_diameter.setText("8 mm")
        self.cross_rebars_widget.cross_distributionAmountRadio.setChecked(True)
        self.cross_rebars_widget.cross_distribution_amount.setValue(3)
        self.cross_rebars_widget.cross_distribution_spacing.setText("20 mm")

        self.parallel_rebars_widget.parallel_distribution_diameter.setText(
            "8 mm"
        )
        self.parallel_rebars_widget.parallel_distributionAmountRadio.setChecked(
            True
        )
        self.parallel_rebars_widget.parallel_distribution_amount.setValue(3)
        self.parallel_rebars_widget.parallel_distribution_spacing.setText(
            "20 mm"
        )

    def addDropdownMenuItems(self):
        """This function add dropdown items to each Gui::PrefComboBox."""
        self.form.slabReinforcement_configuration.addItems(
            ["SlabReinforcement"]
        )
        self.parallel_rebars_widget.meshCoverAlongValue.addItems(
            ["Bottom", "Top"]
        )
        self.parallel_rebars_widget.parallel_rebars_type.addItems(
            ["StraightRebar", "LShapeRebar", "UShapeRebar", "BentShapeRebar"]
        )
        self.cross_rebars_widget.cross_rebars_type.addItems(
            ["StraightRebar", "LShapeRebar", "UShapeRebar", "BentShapeRebar"]
        )
        self.parallel_rebars_widget.parallel_l_shapeHookOrientation.addItems(
            ["Left", "Right", "Alternate"]
        )
        self.cross_rebars_widget.cross_l_shapeHookOrientation.addItems(
            ["Left", "Right", "Alternate"]
        )

    def connectSignalSlots(self):
        """This function is used to connect different slots in UI to appropriate
        functions."""

        self.form.rebars_listWidget.currentRowChanged.connect(
            self.changeRebarsListWidget
        )
        self.cross_rebars_widget.cross_rebars_type.currentIndexChanged.connect(
            self.changeCrossRebarType
        )
        self.parallel_rebars_widget.parallel_rebars_type.currentIndexChanged.connect(
            self.changeParallelRebarType
        )
        self.parallel_rebars_widget.parallel_amount_radio.clicked.connect(
            self.parallelAmountRadioClicked
        )
        self.parallel_rebars_widget.parallel_spacing_radio.clicked.connect(
            self.parallelSpacingRadioClicked
        )
        self.cross_rebars_widget.cross_amount_radio.clicked.connect(
            self.crossAmountRadioClicked
        )
        self.cross_rebars_widget.cross_spacing_radio.clicked.connect(
            self.crossSpacingRadioClicked
        )
        self.parallel_rebars_widget.parallel_distributionAmountRadio.clicked.connect(
            self.parallelDistributionAmountRadio
        )
        self.parallel_rebars_widget.parallel_distributionSpacingRadio.clicked.connect(
            self.parallelDistributionSpacingRadio
        )
        self.cross_rebars_widget.cross_distributionAmountRadio.clicked.connect(
            self.crossDistributionAmountRadio
        )
        self.cross_rebars_widget.cross_distributionSpacingRadio.clicked.connect(
            self.crossDistributionSpacingRadio
        )
        self.cross_rebars_widget.cross_distribution_rebar_check.clicked.connect(
            self.crossDistributionRebarCheckClicked
        )
        self.parallel_rebars_widget.parallel_distribution_rebar_check.clicked.connect(
            self.parallelDistributionRebarCheckClicked
        )

        self.form.next_button.clicked.connect(self.nextButtonClicked)
        self.form.back_button.clicked.connect(self.backButtonClicked)
        self.form.standardButtonBox.clicked.connect(self.clicked)

    def reset(self):
        """Reset fields values"""
        if not self.SlabReinforcementGroup:
            self.setDefaultValues()
        else:
            setParallelRebarsData(self, self.SlabReinforcementGroup)
            setCrossRebarsData(self, self.SlabReinforcementGroup)

    def changeRebarsListWidget(self, index):
        """Handle change in rebar list widget"""
        max_index = self.form.rebars_listWidget.count() - 1
        if index == max_index:
            self.form.next_button.setText("Finish")
        else:
            self.form.next_button.setText("Next")
        self.form.rebars_stackedWidget.setCurrentIndex(index)

    def changeParallelRebarType(self):
        """Handle change in parallel rebar type"""
        self.parallel_rebars_type = (
            self.parallel_rebars_widget.parallel_rebars_type.currentText()
        )
        self.parallel_rebars_widget.parallel_l_shapeHookOrientation.hide()
        self.parallel_rebars_widget.parallel_bentLength.hide()
        self.parallel_rebars_widget.parallel_bentAngle.hide()
        self.parallel_rebars_widget.parallel_rounding.hide()
        self.parallel_rebars_widget.parallel_distribution_rebar_check.hide()

        self.parallel_rebars_widget.parallel_l_shapeHookOrientationLabel.hide()
        self.parallel_rebars_widget.parallel_bentLengthLabel.hide()
        self.parallel_rebars_widget.parallel_bentAngleLabel.hide()
        self.parallel_rebars_widget.parallel_roundingLabel.hide()

        self.parallel_rebars_widget.parallel_distribution_diameterLabel.hide()
        self.parallel_rebars_widget.parallel_distribution_amountLabel.hide()
        self.parallel_rebars_widget.parallel_distribution_spacingLabel.hide()
        self.parallel_rebars_widget.distributionValuesHeading.hide()
        self.parallel_rebars_widget.parallel_distribution_diameter.hide()
        self.parallel_rebars_widget.parallel_distributionAmountRadio.hide()
        self.parallel_rebars_widget.parallel_distributionSpacingRadio.hide()
        self.parallel_rebars_widget.parallel_distribution_amount.hide()
        self.parallel_rebars_widget.parallel_distribution_spacing.hide()
        self.parallel_rebars_widget.parallel_distribution_rebar_check.setChecked(
            False
        )
        if self.parallel_rebars_type == "StraightRebar":
            pass
        elif self.parallel_rebars_type == "LShapeRebar":
            self.parallel_rebars_widget.parallel_l_shapeHookOrientation.show()
            self.parallel_rebars_widget.parallel_l_shapeHookOrientationLabel.show()
            self.parallel_rebars_widget.parallel_rounding.show()
            self.parallel_rebars_widget.parallel_roundingLabel.show()

        elif self.parallel_rebars_type == "UShapeRebar":
            self.parallel_rebars_widget.parallel_rounding.show()
            self.parallel_rebars_widget.parallel_roundingLabel.show()

        elif self.parallel_rebars_type == "BentShapeRebar":
            self.parallel_rebars_widget.parallel_bentLength.show()
            self.parallel_rebars_widget.parallel_bentAngle.show()
            self.parallel_rebars_widget.parallel_rounding.show()
            self.parallel_rebars_widget.parallel_distribution_rebar_check.show()
            self.parallel_rebars_widget.parallel_bentLengthLabel.show()
            self.parallel_rebars_widget.parallel_bentAngleLabel.show()
            self.parallel_rebars_widget.parallel_roundingLabel.show()

    def changeCrossRebarType(self):
        """Handle change in cross rebar type"""
        self.cross_rebars_type = (
            self.cross_rebars_widget.cross_rebars_type.currentText()
        )
        self.cross_rebars_widget.cross_l_shapeHookOrientation.hide()
        self.cross_rebars_widget.cross_bentLength.hide()
        self.cross_rebars_widget.cross_bentAngle.hide()
        self.cross_rebars_widget.cross_rounding.hide()
        self.cross_rebars_widget.cross_distribution_rebar_check.hide()

        self.cross_rebars_widget.cross_l_shapeHookOrientationLabel.hide()
        self.cross_rebars_widget.cross_bentLengthLabel.hide()
        self.cross_rebars_widget.cross_bentAngleLabel.hide()
        self.cross_rebars_widget.cross_roundingLabel.hide()

        self.cross_rebars_widget.cross_distribution_diameterLabel.hide()
        self.cross_rebars_widget.cross_distribution_amountLabel.hide()
        self.cross_rebars_widget.cross_distribution_spacingLabel.hide()
        self.cross_rebars_widget.distributionValuesHeading.hide()
        self.cross_rebars_widget.cross_distribution_diameter.hide()
        self.cross_rebars_widget.cross_distributionAmountRadio.hide()
        self.cross_rebars_widget.cross_distributionSpacingRadio.hide()
        self.cross_rebars_widget.cross_distribution_amount.hide()
        self.cross_rebars_widget.cross_distribution_spacing.hide()
        self.cross_rebars_widget.cross_distribution_rebar_check.setChecked(
            False
        )
        if self.cross_rebars_type == "StraightRebar":
            pass
        elif self.cross_rebars_type == "LShapeRebar":
            self.cross_rebars_widget.cross_l_shapeHookOrientation.show()
            self.cross_rebars_widget.cross_l_shapeHookOrientationLabel.show()
            self.cross_rebars_widget.cross_rounding.show()
            self.cross_rebars_widget.cross_roundingLabel.show()

        elif self.cross_rebars_type == "UShapeRebar":
            self.cross_rebars_widget.cross_rounding.show()
            self.cross_rebars_widget.cross_roundingLabel.show()

        elif self.cross_rebars_type == "BentShapeRebar":
            self.cross_rebars_widget.cross_bentLength.show()
            self.cross_rebars_widget.cross_bentAngle.show()
            self.cross_rebars_widget.cross_rounding.show()
            self.cross_rebars_widget.cross_distribution_rebar_check.show()
            self.cross_rebars_widget.cross_bentLengthLabel.show()
            self.cross_rebars_widget.cross_bentAngleLabel.show()
            self.cross_rebars_widget.cross_roundingLabel.show()

    def parallelAmountRadioClicked(self):
        """Handle parallel rebar amount radio click event"""
        self.parallel_rebars_widget.parallel_spacing.setEnabled(False)
        self.parallel_rebars_widget.parallel_amount.setEnabled(True)

    def crossAmountRadioClicked(self):
        """Handle cross rebar amount radio click event"""
        self.cross_rebars_widget.cross_spacing.setEnabled(False)
        self.cross_rebars_widget.cross_amount.setEnabled(True)

    def parallelSpacingRadioClicked(self):
        """Handle parallel rebar spacing radio click event"""
        self.parallel_rebars_widget.parallel_spacing.setEnabled(True)
        self.parallel_rebars_widget.parallel_amount.setEnabled(False)

    def crossSpacingRadioClicked(self):
        """Handle cross rebar spacing radio click event"""
        self.cross_rebars_widget.cross_spacing.setEnabled(True)
        self.cross_rebars_widget.cross_amount.setEnabled(False)

    def parallelDistributionAmountRadio(self):
        """Handle parallel distribution rebar amount radio click event"""
        self.parallel_rebars_widget.parallel_distribution_amount.setEnabled(
            True
        )
        self.parallel_rebars_widget.parallel_distribution_spacing.setEnabled(
            False
        )

    def parallelDistributionSpacingRadio(self):
        """Handle parallel distribution rebar spacing radio click event"""
        self.parallel_rebars_widget.parallel_distribution_amount.setEnabled(
            False
        )
        self.parallel_rebars_widget.parallel_distribution_spacing.setEnabled(
            True
        )

    def crossDistributionAmountRadio(self):
        """Handle cross distribution rebar amount radio click event"""
        self.cross_rebars_widget.cross_distribution_amount.setEnabled(True)
        self.cross_rebars_widget.cross_distribution_spacing.setEnabled(False)

    def crossDistributionSpacingRadio(self):
        """Handle cross distribution rebar spacing radio click event"""
        self.cross_rebars_widget.cross_distribution_amount.setEnabled(False)
        self.cross_rebars_widget.cross_distribution_spacing.setEnabled(True)

    def parallelDistributionRebarCheckClicked(self):
        """Handle parallel distribution rebar checkbox click event"""
        if (
            self.parallel_rebars_widget.parallel_distribution_rebar_check.isChecked()
        ):
            self.parallel_rebars_widget.distributionValuesHeading.show()
            self.parallel_rebars_widget.parallel_distribution_diameterLabel.show()
            self.parallel_rebars_widget.parallel_distribution_amountLabel.show()
            self.parallel_rebars_widget.parallel_distribution_spacingLabel.show()
            self.parallel_rebars_widget.parallel_distribution_diameter.show()
            self.parallel_rebars_widget.parallel_distributionAmountRadio.show()
            self.parallel_rebars_widget.parallel_distributionSpacingRadio.show()
            self.parallel_rebars_widget.parallel_distribution_amount.show()
            self.parallel_rebars_widget.parallel_distribution_spacing.show()
        else:
            self.parallel_rebars_widget.parallel_distribution_diameterLabel.hide()
            self.parallel_rebars_widget.parallel_distribution_amountLabel.hide()
            self.parallel_rebars_widget.parallel_distribution_spacingLabel.hide()
            self.parallel_rebars_widget.distributionValuesHeading.hide()
            self.parallel_rebars_widget.parallel_distribution_diameter.hide()
            self.parallel_rebars_widget.parallel_distributionAmountRadio.hide()
            self.parallel_rebars_widget.parallel_distributionSpacingRadio.hide()
            self.parallel_rebars_widget.parallel_distribution_amount.hide()
            self.parallel_rebars_widget.parallel_distribution_spacing.hide()

    def crossDistributionRebarCheckClicked(self):
        """Handle cross distribution rebar checkbox click event"""
        if self.cross_rebars_widget.cross_distribution_rebar_check.isChecked():
            self.cross_rebars_widget.cross_distribution_diameterLabel.show()
            self.cross_rebars_widget.cross_distribution_amountLabel.show()
            self.cross_rebars_widget.cross_distribution_spacingLabel.show()
            self.cross_rebars_widget.distributionValuesHeading.show()
            self.cross_rebars_widget.cross_distribution_diameter.show()
            self.cross_rebars_widget.cross_distributionAmountRadio.show()
            self.cross_rebars_widget.cross_distributionSpacingRadio.show()
            self.cross_rebars_widget.cross_distribution_amount.show()
            self.cross_rebars_widget.cross_distribution_spacing.show()
        else:
            self.cross_rebars_widget.cross_distribution_diameterLabel.hide()
            self.cross_rebars_widget.cross_distribution_amountLabel.hide()
            self.cross_rebars_widget.cross_distribution_spacingLabel.hide()
            self.cross_rebars_widget.distributionValuesHeading.hide()
            self.cross_rebars_widget.cross_distribution_diameter.hide()
            self.cross_rebars_widget.cross_distributionAmountRadio.hide()
            self.cross_rebars_widget.cross_distributionSpacingRadio.hide()
            self.cross_rebars_widget.cross_distribution_amount.hide()
            self.cross_rebars_widget.cross_distribution_spacing.hide()

    def nextButtonClicked(self):
        """Handle next button click event"""
        if self.form.next_button.text() == "Finish":
            self.accept()
        index = self.form.rebars_listWidget.currentRow()
        index += 1
        max_index = self.form.rebars_listWidget.count() - 1
        if index <= max_index:
            self.form.rebars_listWidget.setCurrentRow(index)

    def backButtonClicked(self):
        """Handle back button click event"""
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
        elif (
            self.form.standardButtonBox.buttonRole(button)
            == QtWidgets.QDialogButtonBox.HelpRole
        ):
            import webbrowser

            webbrowser.open(ReinforcementHelpLinks.slab_reinforcement_help_link)

    def accept(self, button=None):
        """This function is executed when 'OK' button is clicked from UI. It
        execute a function to create slab reinforcement."""
        self.getParallelRebarsData()
        self.getParallelDistributionRebarsData()
        self.getCrossRebarsData()
        self.getCrossDistributionRebarsData()
        if not self.SlabReinforcementGroup:
            SlabReinforcementGroup = makeSlabReinforcement(
                parallel_rebar_type=self.parallel_rebars_type,
                parallel_front_cover=self.parallel_front_cover,
                parallel_rear_cover=self.parallel_rear_cover,
                parallel_left_cover=self.parallel_left_cover,
                parallel_right_cover=self.parallel_right_cover,
                parallel_top_cover=self.parallel_top_cover,
                parallel_bottom_cover=self.parallel_bottom_cover,
                parallel_diameter=self.parallel_diameter,
                parallel_amount_spacing_check=self.parallel_amount_spacing_check,
                parallel_amount_spacing_value=self.parallel_amount_spacing_value,
                cross_rebar_type=self.cross_rebars_type,
                cross_front_cover=self.cross_front_cover,
                cross_rear_cover=self.cross_rear_cover,
                cross_left_cover=self.cross_left_cover,
                cross_right_cover=self.cross_right_cover,
                cross_top_cover=self.cross_top_cover,
                cross_bottom_cover=self.cross_bottom_cover,
                cross_diameter=self.cross_diameter,
                cross_amount_spacing_check=self.cross_amount_spacing_check,
                cross_amount_spacing_value=self.cross_amount_spacing_value,
                cross_rounding=self.cross_rounding,
                cross_bent_bar_length=self.cross_bent_bar_length,
                cross_bent_bar_angle=self.cross_bent_bar_angle,
                cross_l_shape_hook_orintation=self.cross_l_shape_hook_orintation,
                cross_distribution_rebars_check=self.cross_distribution_rebars_check,
                cross_distribution_rebars_diameter=self.cross_distribution_rebars_diameter,
                cross_distribution_rebars_amount_spacing_check=(
                    self.cross_distribution_rebars_amount_spacing_check
                ),
                cross_distribution_rebars_amount_spacing_value=(
                    self.cross_distribution_rebars_amount_spacing_value
                ),
                parallel_rounding=self.parallel_rounding,
                parallel_bent_bar_length=self.parallel_bent_bar_length,
                parallel_bent_bar_angle=self.parallel_bent_bar_angle,
                parallel_l_shape_hook_orintation=self.parallel_l_shape_hook_orintation,
                parallel_distribution_rebars_check=self.parallel_distribution_rebars_check,
                parallel_distribution_rebars_diameter=self.parallel_distribution_rebars_diameter,
                parallel_distribution_rebars_amount_spacing_check=(
                    self.parallel_distribution_rebars_amount_spacing_check
                ),
                parallel_distribution_rebars_amount_spacing_value=(
                    self.parallel_distribution_rebars_amount_spacing_value
                ),
                mesh_cover_along=self.mesh_cover_along,
                structure=self.SelectedObj,
                facename=self.FaceName,
            )
        else:
            SlabReinforcementGroup = editSlabReinforcement(
                self.SlabReinforcementGroup,
                parallel_rebar_type=self.parallel_rebars_type,
                parallel_front_cover=self.parallel_front_cover,
                parallel_rear_cover=self.parallel_rear_cover,
                parallel_left_cover=self.parallel_left_cover,
                parallel_right_cover=self.parallel_right_cover,
                parallel_top_cover=self.parallel_top_cover,
                parallel_bottom_cover=self.parallel_bottom_cover,
                parallel_diameter=self.parallel_diameter,
                parallel_amount_spacing_check=self.parallel_amount_spacing_check,
                parallel_amount_spacing_value=self.parallel_amount_spacing_value,
                cross_rebar_type=self.cross_rebars_type,
                cross_front_cover=self.cross_front_cover,
                cross_rear_cover=self.cross_rear_cover,
                cross_left_cover=self.cross_left_cover,
                cross_right_cover=self.cross_right_cover,
                cross_top_cover=self.cross_top_cover,
                cross_bottom_cover=self.cross_bottom_cover,
                cross_diameter=self.cross_diameter,
                cross_amount_spacing_check=self.cross_amount_spacing_check,
                cross_amount_spacing_value=self.cross_amount_spacing_value,
                cross_rounding=self.cross_rounding,
                cross_bent_bar_length=self.cross_bent_bar_length,
                cross_bent_bar_angle=self.cross_bent_bar_angle,
                cross_l_shape_hook_orintation=self.cross_l_shape_hook_orintation,
                cross_distribution_rebars_check=self.cross_distribution_rebars_check,
                cross_distribution_rebars_diameter=self.cross_distribution_rebars_diameter,
                cross_distribution_rebars_amount_spacing_check=(
                    self.cross_distribution_rebars_amount_spacing_check
                ),
                cross_distribution_rebars_amount_spacing_value=(
                    self.cross_distribution_rebars_amount_spacing_value
                ),
                parallel_rounding=self.parallel_rounding,
                parallel_bent_bar_length=self.parallel_bent_bar_length,
                parallel_bent_bar_angle=self.parallel_bent_bar_angle,
                parallel_l_shape_hook_orintation=self.parallel_l_shape_hook_orintation,
                parallel_distribution_rebars_check=self.parallel_distribution_rebars_check,
                parallel_distribution_rebars_diameter=self.parallel_distribution_rebars_diameter,
                parallel_distribution_rebars_amount_spacing_check=(
                    self.parallel_distribution_rebars_amount_spacing_check
                ),
                parallel_distribution_rebars_amount_spacing_value=(
                    self.parallel_distribution_rebars_amount_spacing_value
                ),
                mesh_cover_along=self.mesh_cover_along,
                structure=self.SelectedObj,
                facename=self.FaceName,
            )
        self.SlabReinforcementGroup = SlabReinforcementGroup
        if (
            self.form.standardButtonBox.buttonRole(button)
            != QtWidgets.QDialogButtonBox.ApplyRole
        ):
            self.form.close()

    def getParallelDistributionRebarsData(self):
        """Get parallel distribution rebars data"""
        self.parallel_distribution_rebars_check = (
            self.parallel_rebars_widget.parallel_distribution_rebar_check.isChecked()
        )
        # if self.parallel_distribution_rebars_check:
        self.parallel_distribution_rebars_diameter = (
            self.parallel_rebars_widget.parallel_distribution_diameter.text()
        )
        self.parallel_distribution_rebars_diameter = FreeCAD.Units.Quantity(
            self.parallel_distribution_rebars_diameter
        ).Value
        self.parallel_distribution_rebars_amount_spacing_check = (
            self.parallel_rebars_widget.parallel_distributionAmountRadio.isChecked()
        )
        if self.parallel_distribution_rebars_amount_spacing_check:
            self.parallel_distribution_rebars_amount_spacing_value = (
                self.parallel_rebars_widget.parallel_distribution_amount.value()
            )
        else:
            self.parallel_distribution_rebars_amount_spacing_value = (
                self.parallel_rebars_widget.parallel_distribution_spacing.text()
            )
            self.parallel_distribution_rebars_amount_spacing_value = (
                FreeCAD.Units.Quantity(
                    self.parallel_distribution_rebars_amount_spacing_value
                ).Value
            )

    def getCrossDistributionRebarsData(self):
        """Get cross distribution rebars data"""
        self.cross_distribution_rebars_check = (
            self.cross_rebars_widget.cross_distribution_rebar_check.isChecked()
        )
        # if self.cross_distribution_rebars_check:
        self.cross_distribution_rebars_diameter = (
            self.cross_rebars_widget.cross_distribution_diameter.text()
        )
        self.cross_distribution_rebars_diameter = FreeCAD.Units.Quantity(
            self.cross_distribution_rebars_diameter
        ).Value
        self.cross_distribution_rebars_amount_spacing_check = (
            self.cross_rebars_widget.cross_distributionAmountRadio.isChecked()
        )
        if self.cross_distribution_rebars_amount_spacing_check:
            self.cross_distribution_rebars_amount_spacing_value = (
                self.cross_rebars_widget.cross_distribution_amount.value()
            )
        else:
            self.cross_distribution_rebars_amount_spacing_value = (
                self.cross_rebars_widget.cross_distribution_spacing.text()
            )
            self.cross_distribution_rebars_amount_spacing_value = (
                FreeCAD.Units.Quantity(
                    self.cross_distribution_rebars_amount_spacing_value
                ).Value
            )

    def getParallelRebarsData(self):
        """Get parallel rebars data"""
        self.mesh_cover_along = (
            self.parallel_rebars_widget.meshCoverAlongValue.currentText()
        )
        self.parallel_front_cover = (
            self.parallel_rebars_widget.parallel_frontCover.text()
        )
        self.parallel_front_cover = FreeCAD.Units.Quantity(
            self.parallel_front_cover
        ).Value
        self.parallel_rear_cover = (
            self.parallel_rebars_widget.parallel_rearCover.text()
        )
        self.parallel_rear_cover = FreeCAD.Units.Quantity(
            self.parallel_rear_cover
        ).Value
        self.parallel_left_cover = (
            self.parallel_rebars_widget.parallel_l_sideCover.text()
        )
        self.parallel_left_cover = FreeCAD.Units.Quantity(
            self.parallel_left_cover
        ).Value
        self.parallel_right_cover = (
            self.parallel_rebars_widget.parallel_r_sideCover.text()
        )
        self.parallel_right_cover = FreeCAD.Units.Quantity(
            self.parallel_right_cover
        ).Value
        self.parallel_top_cover = (
            self.parallel_rebars_widget.parallel_topCover.text()
        )
        self.parallel_top_cover = FreeCAD.Units.Quantity(
            self.parallel_top_cover
        ).Value
        self.parallel_bottom_cover = (
            self.parallel_rebars_widget.parallel_bottomCover.text()
        )
        self.parallel_bottom_cover = FreeCAD.Units.Quantity(
            self.parallel_bottom_cover
        ).Value
        self.parallel_diameter = (
            self.parallel_rebars_widget.parallel_diameter.text()
        )
        self.parallel_diameter = FreeCAD.Units.Quantity(
            self.parallel_diameter
        ).Value
        self.parallel_amount_spacing_check = (
            self.parallel_rebars_widget.parallel_amount_radio.isChecked()
        )
        if self.parallel_amount_spacing_check:
            self.parallel_amount_spacing_value = (
                self.parallel_rebars_widget.parallel_amount.value()
            )
        else:
            self.parallel_amount_spacing_value = (
                self.parallel_rebars_widget.parallel_spacing.text()
            )
            self.parallel_amount_spacing_value = FreeCAD.Units.Quantity(
                self.parallel_amount_spacing_value
            ).Value

        self.parallel_rounding = (
            self.parallel_rebars_widget.parallel_rounding.value()
        )
        self.parallel_bent_bar_length = (
            self.parallel_rebars_widget.parallel_bentLength.text()
        )
        self.parallel_bent_bar_length = FreeCAD.Units.Quantity(
            self.parallel_bent_bar_length
        ).Value
        self.parallel_bent_bar_angle = (
            self.parallel_rebars_widget.parallel_bentAngle.value()
        )
        self.parallel_l_shape_hook_orintation = (
            self.parallel_rebars_widget.parallel_l_shapeHookOrientation.currentText()
        )

    def getCrossRebarsData(self):
        """Get cross rebars data"""
        self.cross_front_cover = (
            self.cross_rebars_widget.cross_frontCover.text()
        )
        self.cross_front_cover = FreeCAD.Units.Quantity(
            self.cross_front_cover
        ).Value
        self.cross_rear_cover = self.cross_rebars_widget.cross_rearCover.text()
        self.cross_rear_cover = FreeCAD.Units.Quantity(
            self.cross_rear_cover
        ).Value
        self.cross_left_cover = (
            self.cross_rebars_widget.cross_l_sideCover.text()
        )
        self.cross_left_cover = FreeCAD.Units.Quantity(
            self.cross_left_cover
        ).Value
        self.cross_right_cover = (
            self.cross_rebars_widget.cross_r_sideCover.text()
        )
        self.cross_right_cover = FreeCAD.Units.Quantity(
            self.cross_right_cover
        ).Value
        self.cross_top_cover = self.cross_rebars_widget.cross_topCover.text()
        self.cross_top_cover = FreeCAD.Units.Quantity(
            self.cross_top_cover
        ).Value
        self.cross_bottom_cover = (
            self.cross_rebars_widget.cross_bottomCover.text()
        )
        self.cross_bottom_cover = FreeCAD.Units.Quantity(
            self.cross_bottom_cover
        ).Value
        self.cross_diameter = self.cross_rebars_widget.cross_diameter.text()
        self.cross_diameter = FreeCAD.Units.Quantity(self.cross_diameter).Value
        self.cross_amount_spacing_check = (
            self.cross_rebars_widget.cross_amount_radio.isChecked()
        )
        self.cross_amount_spacing_check = (
            self.cross_rebars_widget.cross_amount_radio.isChecked()
        )
        if self.cross_amount_spacing_check:
            self.cross_amount_spacing_value = (
                self.cross_rebars_widget.cross_amount.value()
            )
        else:
            self.cross_amount_spacing_value = (
                self.cross_rebars_widget.cross_spacing.text()
            )
            self.cross_amount_spacing_value = FreeCAD.Units.Quantity(
                self.cross_amount_spacing_value
            ).Value
        self.cross_rounding = self.cross_rebars_widget.cross_rounding.value()
        self.cross_bent_bar_length = (
            self.cross_rebars_widget.cross_bentLength.text()
        )
        self.cross_bent_bar_length = FreeCAD.Units.Quantity(
            self.cross_bent_bar_length
        ).Value
        self.cross_bent_bar_angle = (
            self.cross_rebars_widget.cross_bentAngle.value()
        )
        self.cross_distribution_rebars_check = (
            self.cross_rebars_widget.cross_distribution_rebar_check.isChecked()
        )
        self.cross_l_shape_hook_orintation = (
            self.cross_rebars_widget.cross_l_shapeHookOrientation.currentText()
        )


def editDialog(vobj):
    """Edit Slab Reinforcement"""
    obj = _SlabReinforcementDialog(vobj.Object)
    obj.setupUi()
    setParallelRebarsData(obj, vobj.Object)
    setCrossRebarsData(obj, vobj.Object)
    obj.form.exec_()


def setParallelRebarsData(obj, SlabReinforcementGroup):
    """Set values for parallel rebars of slab reinforcement"""
    if not SlabReinforcementGroup:
        return
    obj.parallel_rebars_widget.meshCoverAlongValue.setCurrentIndex(
        obj.parallel_rebars_widget.meshCoverAlongValue.findText(
            SlabReinforcementGroup.MeshCoverAlong
        )
    )
    obj.parallel_rebars_widget.parallel_l_shapeHookOrientation.setCurrentIndex(
        obj.parallel_rebars_widget.parallel_l_shapeHookOrientation.findText(
            SlabReinforcementGroup.ParallelLShapeHookOrintation
        )
    )
    obj.parallel_rebars_widget.parallel_rebars_type.setCurrentIndex(
        obj.parallel_rebars_widget.parallel_rebars_type.findText(
            SlabReinforcementGroup.ParallelRebarType
        )
    )
    obj.changeParallelRebarType()
    obj.parallel_rebars_widget.parallel_frontCover.setText(
        SlabReinforcementGroup.ParallelFrontCover.UserString
    )
    obj.parallel_rebars_widget.parallel_l_sideCover.setText(
        SlabReinforcementGroup.ParallelLeftCover.UserString
    )
    obj.parallel_rebars_widget.parallel_r_sideCover.setText(
        SlabReinforcementGroup.ParallelRightCover.UserString
    )
    obj.parallel_rebars_widget.parallel_bottomCover.setText(
        SlabReinforcementGroup.ParallelBottomCover.UserString
    )
    obj.parallel_rebars_widget.parallel_topCover.setText(
        SlabReinforcementGroup.ParallelTopCover.UserString
    )
    obj.parallel_rebars_widget.parallel_rearCover.setText(
        SlabReinforcementGroup.ParallelRearCover.UserString
    )
    obj.parallel_rebars_widget.parallel_bentLength.setText(
        SlabReinforcementGroup.ParallelBentBarLength.UserString
    )
    obj.parallel_rebars_widget.parallel_bentAngle.setValue(
        SlabReinforcementGroup.ParallelBentBarAngle
    )
    obj.parallel_rebars_widget.parallel_rounding.setValue(
        SlabReinforcementGroup.ParallelRounding
    )
    obj.parallel_rebars_widget.parallel_diameter.setText(
        SlabReinforcementGroup.ParallelDiameter.UserString
    )
    obj.parallel_rebars_widget.parallel_amount_radio.setChecked(
        SlabReinforcementGroup.ParallelAmountSpacingCheck
    )
    if SlabReinforcementGroup.ParallelAmountSpacingCheck:
        obj.parallelAmountRadioClicked()
    else:
        obj.parallelSpacingRadioClicked()
    obj.parallel_rebars_widget.parallel_spacing_radio.setChecked(
        not SlabReinforcementGroup.ParallelAmountSpacingCheck
    )
    obj.parallel_rebars_widget.parallel_amount.setValue(
        SlabReinforcementGroup.ParallelAmountValue
    )
    obj.parallel_rebars_widget.parallel_spacing.setText(
        SlabReinforcementGroup.ParallelSpacingValue.UserString
    )
    obj.parallel_rebars_widget.parallel_distribution_rebar_check.setChecked(
        SlabReinforcementGroup.ParallelDistributionRebarsCheck
    )
    obj.parallelDistributionRebarCheckClicked()
    obj.parallel_rebars_widget.parallel_distribution_diameter.setText(
        SlabReinforcementGroup.ParallelDistributionRebarsDiameter.UserString
    )
    obj.parallel_rebars_widget.parallel_distributionAmountRadio.setChecked(
        SlabReinforcementGroup.ParallelDistributionRebarsAmountSpacingCheck
    )
    obj.parallel_rebars_widget.parallel_distributionSpacingRadio.setChecked(
        not SlabReinforcementGroup.ParallelDistributionRebarsAmountSpacingCheck
    )
    if SlabReinforcementGroup.ParallelDistributionRebarsAmountSpacingCheck:
        obj.parallelDistributionAmountRadio()
    else:
        obj.parallelDistributionSpacingRadio()
    obj.parallel_rebars_widget.parallel_distribution_amount.setValue(
        SlabReinforcementGroup.ParallelDistributionRebarsAmount
    )
    obj.parallel_rebars_widget.parallel_distribution_spacing.setText(
        SlabReinforcementGroup.ParallelDistributionRebarsSpacing.UserString
    )


def setCrossRebarsData(obj, SlabReinforcementGroup):
    """Set values for cross rebars of slab reinforcement"""
    if not SlabReinforcementGroup:
        return

    obj.cross_rebars_widget.cross_l_shapeHookOrientation.setCurrentIndex(
        obj.cross_rebars_widget.cross_l_shapeHookOrientation.findText(
            SlabReinforcementGroup.CrossLShapeHookOrintation
        )
    )
    obj.cross_rebars_widget.cross_rebars_type.setCurrentIndex(
        obj.cross_rebars_widget.cross_rebars_type.findText(
            SlabReinforcementGroup.CrossRebarType
        )
    )
    obj.changeCrossRebarType()
    obj.cross_rebars_widget.cross_frontCover.setText(
        SlabReinforcementGroup.CrossFrontCover.UserString
    )
    obj.cross_rebars_widget.cross_l_sideCover.setText(
        SlabReinforcementGroup.CrossLeftCover.UserString
    )
    obj.cross_rebars_widget.cross_r_sideCover.setText(
        SlabReinforcementGroup.CrossRightCover.UserString
    )
    obj.cross_rebars_widget.cross_bottomCover.setText(
        SlabReinforcementGroup.CrossBottomCover.UserString
    )
    obj.cross_rebars_widget.cross_topCover.setText(
        SlabReinforcementGroup.CrossTopCover.UserString
    )
    obj.cross_rebars_widget.cross_rearCover.setText(
        SlabReinforcementGroup.CrossRearCover.UserString
    )
    obj.cross_rebars_widget.cross_bentLength.setText(
        SlabReinforcementGroup.CrossBentBarLength.UserString
    )
    obj.cross_rebars_widget.cross_bentAngle.setValue(
        SlabReinforcementGroup.CrossBentBarAngle
    )
    obj.cross_rebars_widget.cross_rounding.setValue(
        SlabReinforcementGroup.CrossRounding
    )
    obj.cross_rebars_widget.cross_diameter.setText(
        SlabReinforcementGroup.CrossDiameter.UserString
    )
    obj.cross_rebars_widget.cross_amount_radio.setChecked(
        SlabReinforcementGroup.CrossAmountSpacingCheck
    )
    obj.cross_rebars_widget.cross_spacing_radio.setChecked(
        not SlabReinforcementGroup.CrossAmountSpacingCheck
    )
    if SlabReinforcementGroup.CrossAmountSpacingCheck:
        obj.crossAmountRadioClicked()
    else:
        obj.crossSpacingRadioClicked()
    obj.cross_rebars_widget.cross_amount.setValue(
        SlabReinforcementGroup.CrossAmountValue
    )
    obj.cross_rebars_widget.cross_spacing.setText(
        SlabReinforcementGroup.CrossSpacingValue.UserString
    )
    obj.cross_rebars_widget.cross_distribution_rebar_check.setChecked(
        SlabReinforcementGroup.CrossDistributionRebarsCheck
    )
    obj.crossDistributionRebarCheckClicked()
    obj.cross_rebars_widget.cross_distribution_diameter.setText(
        SlabReinforcementGroup.CrossDistributionRebarsDiameter.UserString
    )
    obj.cross_rebars_widget.cross_distributionAmountRadio.setChecked(
        SlabReinforcementGroup.CrossDistributionRebarsAmountSpacingCheck
    )
    obj.cross_rebars_widget.cross_distributionSpacingRadio.setChecked(
        not SlabReinforcementGroup.CrossDistributionRebarsAmountSpacingCheck
    )
    if SlabReinforcementGroup.CrossDistributionRebarsAmountSpacingCheck:
        obj.crossDistributionAmountRadio()
    else:
        obj.crossDistributionSpacingRadio()
    obj.cross_rebars_widget.cross_distribution_amount.setValue(
        SlabReinforcementGroup.CrossDistributionRebarsAmount
    )
    obj.cross_rebars_widget.cross_distribution_spacing.setText(
        SlabReinforcementGroup.CrossDistributionRebarsSpacing.UserString
    )


def CommandSlabReinforcement():
    """This function is used to invoke dialog box for slab reinforcement."""
    selected_obj = check_selected_face()
    if selected_obj:
        # check if selected face is horizontal. If so, later execution will fail with error
        normal = facenormalDirection()
        is_horizontal = FreeCAD.Vector(0, 0, 1).getAngle(normal) < 0.01
        if is_horizontal:  
            showWarning("Error: Select a vertical slab surface!")
            return
        dialog = _SlabReinforcementDialog()
        dialog.setupUi()
        dialog.form.exec_()
