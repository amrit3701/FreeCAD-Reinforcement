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

__title__ = "Footing Reinforcement"
__author__ = "Shiv Charan"
__url__ = "https://www.freecadweb.org"

from pathlib import Path
from PySide2 import QtWidgets

import FreeCAD
import FreeCADGui

from ColumnReinforcement.RebarNumberDiameter import runNumberDiameterDialog
from Rebarfunc import check_selected_face
from FootingReinforcement.FootingReinforcement import (
    makeFootingReinforcement,
    editFootingReinforcement,
)
from RebarData import ReinforcementHelpLinks


class _FootingReinforcementDialog:
    def __init__(self, FootingReinforcementGroup=None):
        """This function set initial data in Footing Reinforcement dialog box."""
        # Load ui from file MainFootingbReinforcement.ui
        if not FootingReinforcementGroup:
            selected_obj = FreeCADGui.Selection.getSelectionEx()[0]
            self.SelectedObj = selected_obj.Object
            self.FaceName = selected_obj.SubElementNames[0]
        else:
            self.SelectedObj = FootingReinforcementGroup.Structure
            self.FaceName = FootingReinforcementGroup.Facename

        self.form = FreeCADGui.PySideUic.loadUi(
            str(Path(__file__).with_suffix(".ui").absolute())
        )
        self.form.setWindowTitle(
            QtWidgets.QApplication.translate(
                "RebarWorkbench", "Footing Reinforcement", None
            )
        )
        self.FootingReinforcementGroup = FootingReinforcementGroup

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

        # for Columns
        self.columns_widget = FreeCADGui.PySideUic.loadUi(
            str(Path(__file__).parent.absolute() / "Columns.ui")
        )
        self.form.rebars_stackedWidget.addWidget(self.columns_widget)
        # Load and add widgets into stacked widget
        self.ties_widget = FreeCADGui.PySideUic.loadUi(
            str(Path(__file__).parent.absolute() / "Ties.ui")
        )
        self.form.rebars_stackedWidget.addWidget(self.ties_widget)
        self.main_rebars_widget = FreeCADGui.PySideUic.loadUi(
            str(Path(__file__).parent.absolute() / "MainRebars.ui")
        )
        self.form.rebars_stackedWidget.addWidget(self.main_rebars_widget)
        self.sec_xdir_rebars_widget = FreeCADGui.PySideUic.loadUi(
            str(Path(__file__).parent.absolute() / "SecXDirRebars.ui")
        )
        self.form.rebars_stackedWidget.addWidget(self.sec_xdir_rebars_widget)
        self.sec_ydir_rebars_widget = FreeCADGui.PySideUic.loadUi(
            str(Path(__file__).parent.absolute() / "SecYDirRebars.ui")
        )
        self.form.rebars_stackedWidget.addWidget(self.sec_ydir_rebars_widget)

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
        self.parallel_rebars_widget.parallel_rounding.setValue(2)
        self.parallel_rebars_widget.parallel_diameter.setText("8 mm")
        self.parallel_rebars_widget.parallel_amount_radio.setChecked(True)
        self.parallel_rebars_widget.parallel_spacing_radio.setChecked(False)
        self.parallel_rebars_widget.parallel_amount.setValue(10)
        self.parallel_rebars_widget.parallel_spacing.setText("50 mm")

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
        self.cross_rebars_widget.cross_rounding.setValue(2)
        self.cross_rebars_widget.cross_diameter.setText("8 mm")
        self.cross_rebars_widget.cross_amount_radio.setChecked(True)
        self.cross_rebars_widget.cross_spacing_radio.setChecked(False)
        self.cross_rebars_widget.cross_amount.setValue(10)
        self.cross_rebars_widget.cross_spacing.setText("50 mm")

        # For Column

        self.columns_widget.columns_frontSpacing.setText("50.00 mm")
        self.columns_widget.columns_leftSpacing.setText("50.00 mm")
        self.columns_widget.columns_rightSpacing.setText("50.00 mm")
        self.columns_widget.columns_rearSpacing.setText("50.00 mm")
        self.columns_widget.column_length.setText("200.00 mm")
        self.columns_widget.column_width.setText("200.00 mm")
        self.columns_widget.column_xdir_amountRadio.setChecked(True)
        self.columns_widget.column_xdir_spacingRadio.setChecked(False)
        self.columns_widget.column_xdir_amount.setValue(1)
        self.columns_widget.column_xdir_spacing.setText("400.00 mm")
        self.columns_widget.column_ydir_amountRadio.setChecked(True)
        self.columns_widget.column_ydir_spacingRadio.setChecked(False)
        self.columns_widget.column_ydir_amount.setValue(1)
        self.columns_widget.column_ydir_spacing.setText("400.00 mm")
        self.columns_widget.column_secRebarCheck.setChecked(False)
        self.columnSecRebarCheckClicked()

        # Set Ties data
        self.ties_widget.ties_bottomCover.setText("40.00 mm")
        self.ties_widget.ties_topCover.setText("40.00 mm")
        self.ties_widget.ties_diameter.setText("8.00 mm")
        self.ties_widget.ties_bentAngle.setCurrentIndex(
            self.ties_widget.ties_bentAngle.findText("135")
        )
        self.ties_widget.ties_extensionFactor.setValue(2)
        self.ties_widget.ties_number_radio.setChecked(True)
        self.ties_widget.ties_spacing_radio.setChecked(False)
        self.ties_widget.ties_number.setEnabled(True)
        self.ties_widget.ties_spacing.setEnabled(False)
        self.ties_widget.ties_number.setValue(5)
        self.ties_widget.ties_spacing.setText("50.00 mm")
        # Set Main Rebars data
        self.main_rebars_widget.main_rebars_type.setCurrentIndex(
            self.main_rebars_widget.main_rebars_type.findText("StraightRebar")
        )
        self.main_rebars_widget.main_rebars_hookOrientation.setCurrentIndex(
            self.main_rebars_widget.main_rebars_hookOrientation.findText(
                "Bottom Outside"
            )
        )
        self.main_rebars_widget.main_rebars_hookExtendAlong.setCurrentIndex(
            self.main_rebars_widget.main_rebars_hookExtendAlong.findText(
                "x-axis"
            )
        )
        self.main_rebars_widget.main_rebars_hookExtension.setText("40.00 mm")
        self.main_rebars_widget.main_rebars_rounding.setValue(2)
        self.main_rebars_widget.main_rebars_topOffset.setText("400.00 mm")
        self.main_rebars_widget.main_rebars_diameter.setText("20.00 mm")
        # Set Secondary Xdir Rebars Data
        self.sec_xdir_rebars_widget.xdir_rebars_type.setCurrentIndex(
            self.sec_xdir_rebars_widget.xdir_rebars_type.findText(
                "StraightRebar"
            )
        )
        self.sec_xdir_rebars_widget.xdir_rebars_hookOrientation.setCurrentIndex(
            self.sec_xdir_rebars_widget.xdir_rebars_hookOrientation.findText(
                "Bottom Outside"
            )
        )
        self.sec_xdir_rebars_widget.xdir_rebars_hookExtension.setText(
            "40.00 mm"
        )
        self.sec_xdir_rebars_widget.xdir_rebars_rounding.setValue(1)
        self.sec_xdir_rebars_widget.xdir_rebars_topOffset.setText("400.00 mm")
        self.sec_xdir_rebars_widget.numberDiameter.setText("1#8mm+1#8mm+1#8mm")
        # Set Secondary Ydir Rebars Data
        self.sec_ydir_rebars_widget.ydir_rebars_type.setCurrentIndex(
            self.sec_ydir_rebars_widget.ydir_rebars_type.findText(
                "StraightRebar"
            )
        )
        self.sec_ydir_rebars_widget.ydir_rebars_hookOrientation.setCurrentIndex(
            self.sec_ydir_rebars_widget.ydir_rebars_hookOrientation.findText(
                "Bottom Outside"
            )
        )
        self.sec_ydir_rebars_widget.ydir_rebars_hookExtension.setText(
            "40.00 mm"
        )
        self.sec_ydir_rebars_widget.ydir_rebars_rounding.setValue(1)
        self.sec_ydir_rebars_widget.ydir_rebars_topOffset.setText("400.00 mm")
        self.sec_ydir_rebars_widget.numberDiameter.setText("1#8mm+1#8mm+1#8mm")

    def addDropdownMenuItems(self):
        """This function add dropdown items to each Gui::PrefComboBox."""
        self.form.footingReinforcement_configuration.addItems(
            ["FootingReinforcement"]
        )
        self.parallel_rebars_widget.meshCoverAlongValue.addItems(
            ["Bottom", "Top", "Both"]
        )
        self.parallel_rebars_widget.parallel_rebars_type.addItems(
            ["StraightRebar", "LShapeRebar", "UShapeRebar"]
        )
        self.cross_rebars_widget.cross_rebars_type.addItems(
            ["StraightRebar", "LShapeRebar", "UShapeRebar"]
        )
        self.parallel_rebars_widget.parallel_l_shapeHookOrientation.addItems(
            ["Left", "Right", "Alternate"]
        )
        self.cross_rebars_widget.cross_l_shapeHookOrientation.addItems(
            ["Left", "Right", "Alternate"]
        )

        # For columns
        # Add bent angle of ties
        self.ties_widget.ties_bentAngle.addItems(["90", "135"])
        # Add rebar_type to all rebars widgets
        self.main_rebars_widget.main_rebars_type.addItems(
            ["StraightRebar", "LShapeRebar"]
        )
        self.sec_xdir_rebars_widget.xdir_rebars_type.addItems(
            ["StraightRebar", "LShapeRebar"]
        )
        self.sec_ydir_rebars_widget.ydir_rebars_type.addItems(
            ["StraightRebar", "LShapeRebar"]
        )
        # Add hook_orientation to all rebars widgets
        hook_orientation_list = [
            "Top Inside",
            "Top Outside",
            "Top Left",
            "Top Right",
            "Bottom Inside",
            "Bottom Outside",
            "Bottom Left",
            "Bottom Right",
        ]
        self.main_rebars_widget.main_rebars_hookOrientation.addItems(
            hook_orientation_list
        )
        self.sec_xdir_rebars_widget.xdir_rebars_hookOrientation.addItems(
            hook_orientation_list
        )
        self.sec_ydir_rebars_widget.ydir_rebars_hookOrientation.addItems(
            hook_orientation_list
        )
        # Add hook_extend_along_list to main rebars widgets
        hook_extend_along_list = ["x-axis", "y-axis"]
        self.main_rebars_widget.main_rebars_hookExtendAlong.addItems(
            hook_extend_along_list
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

        self.form.next_button.clicked.connect(self.nextButtonClicked)
        self.form.back_button.clicked.connect(self.backButtonClicked)
        self.form.standardButtonBox.clicked.connect(self.clicked)

        # for column
        self.columns_widget.column_secRebarCheck.clicked.connect(
            self.columnSecRebarCheckClicked
        )
        self.columns_widget.column_xdir_amountRadio.clicked.connect(
            self.columnXdirAmountRadioClicked
        )
        self.columns_widget.column_xdir_spacingRadio.clicked.connect(
            self.columnXdirSpacingRadioClicked
        )
        self.columns_widget.column_ydir_amountRadio.clicked.connect(
            self.columnYdirAmountRadioClicked
        )
        self.columns_widget.column_ydir_spacingRadio.clicked.connect(
            self.columnYdirSpacingRadioClicked
        )
        self.ties_widget.ties_number_radio.clicked.connect(
            self.tiesNumberRadioClicked
        )
        self.ties_widget.ties_spacing_radio.clicked.connect(
            self.tiesSpacingRadioClicked
        )
        self.main_rebars_widget.main_rebars_type.currentIndexChanged.connect(
            self.changeMainRebarsType
        )
        self.sec_xdir_rebars_widget.xdir_rebars_type.currentIndexChanged.connect(
            self.changeXDirRebarsType
        )
        self.sec_ydir_rebars_widget.ydir_rebars_type.currentIndexChanged.connect(
            self.changeYDirRebarsType
        )
        self.sec_xdir_rebars_widget.xdir_rebars_editNumberDiameter.clicked.connect(
            lambda: runNumberDiameterDialog(self.sec_xdir_rebars_widget)
        )
        self.sec_ydir_rebars_widget.ydir_rebars_editNumberDiameter.clicked.connect(
            lambda: runNumberDiameterDialog(self.sec_ydir_rebars_widget)
        )

    def reset(self):
        """Reset fields values"""
        if not self.FootingReinforcementGroup:
            self.setDefaultValues()
        else:
            setParallelRebarsData(self, self.FootingReinforcementGroup)
            setCrossRebarsData(self, self.FootingReinforcementGroup)
            setColumnsData(self, self.FootingReinforcementGroup)
            setTiesData(self, self.FootingReinforcementGroup)
            setMainRebarsData(self, self.FootingReinforcementGroup)
            setSecRebarsData(self, self.FootingReinforcementGroup)

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
        self.parallel_rebars_widget.parallel_rounding.hide()

        self.parallel_rebars_widget.parallel_l_shapeHookOrientationLabel.hide()
        self.parallel_rebars_widget.parallel_roundingLabel.hide()

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

    def changeCrossRebarType(self):
        """Handle change in cross rebar type"""
        self.cross_rebars_type = (
            self.cross_rebars_widget.cross_rebars_type.currentText()
        )
        self.cross_rebars_widget.cross_l_shapeHookOrientation.hide()
        self.cross_rebars_widget.cross_rounding.hide()

        self.cross_rebars_widget.cross_l_shapeHookOrientationLabel.hide()
        self.cross_rebars_widget.cross_roundingLabel.hide()

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

    # signal for columns
    def columnXdirAmountRadioClicked(self):
        self.columns_widget.column_xdir_amount.setEnabled(True)
        self.columns_widget.column_xdir_spacing.setEnabled(False)

    def columnXdirSpacingRadioClicked(self):
        self.columns_widget.column_xdir_amount.setEnabled(False)
        self.columns_widget.column_xdir_spacing.setEnabled(True)

    def columnYdirAmountRadioClicked(self):
        self.columns_widget.column_ydir_amount.setEnabled(True)
        self.columns_widget.column_ydir_spacing.setEnabled(False)

    def columnYdirSpacingRadioClicked(self):
        self.columns_widget.column_ydir_amount.setEnabled(False)
        self.columns_widget.column_ydir_spacing.setEnabled(True)

    def columnSecRebarCheckClicked(self):
        if self.columns_widget.column_secRebarCheck.isChecked():
            self.sec_xdir_rebars_widget.setEnabled(True)
            self.sec_ydir_rebars_widget.setEnabled(True)
        else:
            self.sec_xdir_rebars_widget.setEnabled(False)
            self.sec_ydir_rebars_widget.setEnabled(False)

    def tiesNumberRadioClicked(self):
        """This function enable ties_number field and disable ties_spacing field
        in UI when ties_number_radio button is clicked."""
        self.ties_widget.ties_spacing.setEnabled(False)
        self.ties_widget.ties_number.setEnabled(True)

    def tiesSpacingRadioClicked(self):
        """This function enable ties_spacing field and disable ties_number field
        in UI when ties_spacing_radio button is clicked."""
        self.ties_widget.ties_number.setEnabled(False)
        self.ties_widget.ties_spacing.setEnabled(True)

    def changeMainRebarsType(self):
        """This function is used to update UI according to selected main rebars
        type."""
        self.main_rebars_type = (
            self.main_rebars_widget.main_rebars_type.currentText()
        )
        if self.main_rebars_type == "LShapeRebar":
            self.main_rebars_widget.main_rebars_hookOrientation.setEnabled(True)
            self.main_rebars_widget.main_rebars_hookExtendAlong.setEnabled(True)
            self.main_rebars_widget.main_rebars_hookExtension.setEnabled(True)
            self.main_rebars_widget.main_rebars_rounding.setEnabled(True)
        else:
            self.main_rebars_widget.main_rebars_hookOrientation.setEnabled(
                False
            )
            self.main_rebars_widget.main_rebars_hookExtendAlong.setEnabled(
                False
            )
            self.main_rebars_widget.main_rebars_hookExtension.setEnabled(False)
            self.main_rebars_widget.main_rebars_rounding.setEnabled(False)

    def changeXDirRebarsType(self):
        """This function is used to update UI according to selected xdir rebars
        type."""
        self.xdir_rebars_type = (
            self.sec_xdir_rebars_widget.xdir_rebars_type.currentText()
        )
        if self.xdir_rebars_type == "LShapeRebar":
            self.sec_xdir_rebars_widget.xdir_rebars_hookOrientation.setEnabled(
                True
            )
            self.sec_xdir_rebars_widget.xdir_rebars_hookExtension.setEnabled(
                True
            )
            self.sec_xdir_rebars_widget.xdir_rebars_rounding.setEnabled(True)
        else:
            self.sec_xdir_rebars_widget.xdir_rebars_hookOrientation.setEnabled(
                False
            )
            self.sec_xdir_rebars_widget.xdir_rebars_hookExtension.setEnabled(
                False
            )
            self.sec_xdir_rebars_widget.xdir_rebars_rounding.setEnabled(False)

    def changeYDirRebarsType(self):
        """This function is used to update UI according to selected ydir rebars
        type."""
        self.ydir_rebars_type = (
            self.sec_ydir_rebars_widget.ydir_rebars_type.currentText()
        )
        if self.ydir_rebars_type == "LShapeRebar":
            self.sec_ydir_rebars_widget.ydir_rebars_hookOrientation.setEnabled(
                True
            )
            self.sec_ydir_rebars_widget.ydir_rebars_hookExtension.setEnabled(
                True
            )
            self.sec_ydir_rebars_widget.ydir_rebars_rounding.setEnabled(True)
        else:
            self.sec_ydir_rebars_widget.ydir_rebars_hookOrientation.setEnabled(
                False
            )
            self.sec_ydir_rebars_widget.ydir_rebars_hookExtension.setEnabled(
                False
            )
            self.sec_ydir_rebars_widget.ydir_rebars_rounding.setEnabled(False)

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

            webbrowser.open(
                ReinforcementHelpLinks.footing_reinforcement_help_link
            )

    def accept(self, button=None):
        """This function is executed when 'OK' button is clicked from UI. It
        execute a function to create Footing reinforcement."""
        self.getParallelRebarsData()
        self.getCrossRebarsData()
        self.getColumnsData()
        self.getTiesData()
        self.getMainRebarsData()
        self.getSecondaryRebarsData()
        if not self.FootingReinforcementGroup:
            FootingReinforcementGroup = makeFootingReinforcement(
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
                column_front_spacing=self.column_front_spacing,
                column_left_spacing=self.column_left_spacing,
                column_right_spacing=self.column_right_spacing,
                column_rear_spacing=self.column_rear_spacing,
                tie_top_cover=self.tie_top_cover,
                tie_bottom_cover=self.tie_bottom_cover,
                tie_bent_angle=self.tie_bent_angle,
                tie_extension_factor=self.tie_extension_factor,
                tie_diameter=self.tie_diameter,
                tie_number_spacing_check=self.tie_number_spacing_check,
                tie_number_spacing_value=self.tie_number_spacing_value,
                column_main_rebar_diameter=self.column_main_rebar_diameter,
                column_main_rebars_t_offset=self.column_main_rebars_t_offset,
                cross_amount_spacing_value=self.cross_amount_spacing_value,
                column_width=self.column_width,
                column_length=self.column_length,
                xdir_column_amount_spacing_check=self.xdir_column_amount_spacing_check,
                xdir_column_amount_spacing_value=self.xdir_column_amount_spacing_value,
                ydir_column_amount_spacing_check=self.ydir_column_amount_spacing_check,
                ydir_column_amount_spacing_value=self.ydir_column_amount_spacing_value,
                parallel_rounding=self.parallel_rounding,
                parallel_l_shape_hook_orintation=self.parallel_l_shape_hook_orintation,
                cross_rounding=self.cross_rounding,
                cross_l_shape_hook_orintation=self.cross_l_shape_hook_orintation,
                column_main_rebars_type=self.column_main_rebars_type,
                column_main_hook_orientation=self.column_main_hook_orientation,
                column_main_hook_extend_along=self.column_main_hook_extend_along,
                column_l_main_rebar_rounding=self.column_l_main_rebar_rounding,
                column_main_hook_extension=self.column_main_hook_extension,
                column_sec_rebar_check=self.column_sec_rebar_check,
                column_sec_rebars_t_offset=self.column_sec_rebars_t_offset,
                column_sec_rebars_number_diameter=self.column_sec_rebars_number_diameter,
                column_sec_rebars_type=self.column_sec_rebars_type,
                column_sec_hook_orientation=self.column_sec_hook_orientation,
                column_l_sec_rebar_rounding=self.column_l_sec_rebar_rounding,
                column_sec_hook_extension=self.column_sec_hook_extension,
                mesh_cover_along=self.mesh_cover_along,
                structure=self.SelectedObj,
                facename=self.FaceName,
            )
        else:
            FootingReinforcementGroup = editFootingReinforcement(
                self.FootingReinforcementGroup,
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
                column_front_spacing=self.column_front_spacing,
                column_left_spacing=self.column_left_spacing,
                column_right_spacing=self.column_right_spacing,
                column_rear_spacing=self.column_rear_spacing,
                tie_top_cover=self.tie_top_cover,
                tie_bottom_cover=self.tie_bottom_cover,
                tie_bent_angle=self.tie_bent_angle,
                tie_extension_factor=self.tie_extension_factor,
                tie_diameter=self.tie_diameter,
                tie_number_spacing_check=self.tie_number_spacing_check,
                tie_number_spacing_value=self.tie_number_spacing_value,
                column_main_rebar_diameter=self.column_main_rebar_diameter,
                column_main_rebars_t_offset=self.column_main_rebars_t_offset,
                cross_amount_spacing_value=self.cross_amount_spacing_value,
                column_width=self.column_width,
                column_length=self.column_length,
                xdir_column_amount_spacing_check=self.xdir_column_amount_spacing_check,
                xdir_column_amount_spacing_value=self.xdir_column_amount_spacing_value,
                ydir_column_amount_spacing_check=self.ydir_column_amount_spacing_check,
                ydir_column_amount_spacing_value=self.ydir_column_amount_spacing_value,
                parallel_rounding=self.parallel_rounding,
                parallel_l_shape_hook_orintation=self.parallel_l_shape_hook_orintation,
                cross_rounding=self.cross_rounding,
                cross_l_shape_hook_orintation=self.cross_l_shape_hook_orintation,
                column_main_rebars_type=self.column_main_rebars_type,
                column_main_hook_orientation=self.column_main_hook_orientation,
                column_main_hook_extend_along=self.column_main_hook_extend_along,
                column_l_main_rebar_rounding=self.column_l_main_rebar_rounding,
                column_main_hook_extension=self.column_main_hook_extension,
                column_sec_rebar_check=self.column_sec_rebar_check,
                column_sec_rebars_t_offset=self.column_sec_rebars_t_offset,
                column_sec_rebars_number_diameter=self.column_sec_rebars_number_diameter,
                column_sec_rebars_type=self.column_sec_rebars_type,
                column_sec_hook_orientation=self.column_sec_hook_orientation,
                column_l_sec_rebar_rounding=self.column_l_sec_rebar_rounding,
                column_sec_hook_extension=self.column_sec_hook_extension,
                mesh_cover_along=self.mesh_cover_along,
                structure=self.SelectedObj,
                facename=self.FaceName,
            )

        self.FootingReinforcementGroup = FootingReinforcementGroup
        if (
            self.form.standardButtonBox.buttonRole(button)
            != QtWidgets.QDialogButtonBox.ApplyRole
        ):
            self.form.close()

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
        self.cross_l_shape_hook_orintation = (
            self.cross_rebars_widget.cross_l_shapeHookOrientation.currentText()
        )

    # get data from column
    def getColumnsData(self):
        """This function is used to get data related to columns from UI."""
        self.column_front_spacing = FreeCAD.Units.Quantity(
            self.columns_widget.columns_frontSpacing.text()
        ).Value
        self.column_left_spacing = FreeCAD.Units.Quantity(
            self.columns_widget.columns_leftSpacing.text()
        ).Value
        self.column_right_spacing = FreeCAD.Units.Quantity(
            self.columns_widget.columns_rightSpacing.text()
        ).Value
        self.column_rear_spacing = FreeCAD.Units.Quantity(
            self.columns_widget.columns_rearSpacing.text()
        ).Value
        self.column_width = FreeCAD.Units.Quantity(
            self.columns_widget.column_length.text()
        ).Value
        self.column_length = FreeCAD.Units.Quantity(
            self.columns_widget.column_width.text()
        ).Value

        self.xdir_column_amount_spacing_check = (
            self.columns_widget.column_xdir_amountRadio.isChecked()
        )
        if self.xdir_column_amount_spacing_check:
            self.xdir_column_amount_spacing_value = (
                self.columns_widget.column_xdir_amount.value()
            )
        else:
            self.xdir_column_amount_spacing_value = FreeCAD.Units.Quantity(
                self.columns_widget.column_xdir_spacing.text()
            ).Value

        self.ydir_column_amount_spacing_check = (
            self.columns_widget.column_ydir_amountRadio.isChecked()
        )
        if self.ydir_column_amount_spacing_check:
            self.ydir_column_amount_spacing_value = (
                self.columns_widget.column_ydir_amount.value()
            )
        else:
            self.ydir_column_amount_spacing_value = FreeCAD.Units.Quantity(
                self.columns_widget.column_ydir_spacing.text()
            ).Value

        self.column_sec_rebar_check = (
            self.columns_widget.column_secRebarCheck.isChecked()
        )

    def getTiesData(self):
        """This function is used to get data related to ties from UI."""
        # Get Ties data from UI
        self.tie_bottom_cover = self.ties_widget.ties_bottomCover.text()
        self.tie_bottom_cover = FreeCAD.Units.Quantity(
            self.tie_bottom_cover
        ).Value
        self.tie_top_cover = self.ties_widget.ties_topCover.text()
        self.tie_top_cover = FreeCAD.Units.Quantity(self.tie_top_cover).Value
        self.tie_diameter = self.ties_widget.ties_diameter.text()
        self.tie_diameter = FreeCAD.Units.Quantity(self.tie_diameter).Value
        self.tie_bent_angle = int(self.ties_widget.ties_bentAngle.currentText())
        self.tie_extension_factor = (
            self.ties_widget.ties_extensionFactor.value()
        )
        self.ties_number_check = self.ties_widget.ties_number_radio.isChecked()
        if self.ties_number_check:
            self.tie_number_spacing_check = True
            self.tie_number_spacing_value = self.ties_widget.ties_number.value()
        else:
            self.tie_number_spacing_check = False
            self.tie_number_spacing_value = self.ties_widget.ties_spacing.text()
            self.tie_number_spacing_value = FreeCAD.Units.Quantity(
                self.tie_number_spacing_value
            ).Value

    def getMainRebarsData(self):
        """This function is used to get data related to main rebars from UI."""
        self.column_main_rebars_type = (
            self.main_rebars_widget.main_rebars_type.currentText()
        )
        self.column_main_hook_orientation = (
            self.main_rebars_widget.main_rebars_hookOrientation.currentText()
        )
        self.column_main_hook_extend_along = (
            self.main_rebars_widget.main_rebars_hookExtendAlong.currentText()
        )
        self.column_main_hook_extension = (
            self.main_rebars_widget.main_rebars_hookExtension.text()
        )
        self.column_main_hook_extension = FreeCAD.Units.Quantity(
            self.column_main_hook_extension
        ).Value
        self.column_l_main_rebar_rounding = (
            self.main_rebars_widget.main_rebars_rounding.value()
        )
        self.column_main_rebars_t_offset = (
            self.main_rebars_widget.main_rebars_topOffset.text()
        )
        self.column_main_rebars_t_offset = FreeCAD.Units.Quantity(
            self.column_main_rebars_t_offset
        ).Value
        self.column_main_rebar_diameter = (
            self.main_rebars_widget.main_rebars_diameter.text()
        )
        self.column_main_rebar_diameter = FreeCAD.Units.Quantity(
            self.column_main_rebar_diameter
        ).Value

    def getXDirRebarsData(self):
        """This function is used to get data related to xdir rebars from UI."""
        self.xdir_rebars_type = (
            self.sec_xdir_rebars_widget.xdir_rebars_type.currentText()
        )
        self.xdir_rebars_hook_orientation = (
            self.sec_xdir_rebars_widget.xdir_rebars_hookOrientation.currentText()
        )
        self.xdir_rebars_hook_extension = (
            self.sec_xdir_rebars_widget.xdir_rebars_hookExtension.text()
        )
        self.xdir_rebars_hook_extension = FreeCAD.Units.Quantity(
            self.xdir_rebars_hook_extension
        ).Value
        self.xdir_rebars_rounding = (
            self.sec_xdir_rebars_widget.xdir_rebars_rounding.value()
        )
        self.xdir_rebars_t_offset = (
            self.sec_xdir_rebars_widget.xdir_rebars_topOffset.text()
        )
        self.xdir_rebars_t_offset = FreeCAD.Units.Quantity(
            self.xdir_rebars_t_offset
        ).Value
        self.xdir_rebars_number_diameter = (
            self.sec_xdir_rebars_widget.numberDiameter.text()
        )

    def getSecondaryRebarsData(self):
        """This function is used to get data related to secondary rebars."""
        self.getXDirRebarsData()
        self.getYDirRebarsData()
        self.column_sec_rebars_t_offset = (
            self.xdir_rebars_t_offset,
            self.ydir_rebars_t_offset,
        )
        self.column_sec_rebars_number_diameter = (
            self.xdir_rebars_number_diameter,
            self.ydir_rebars_number_diameter,
        )
        self.column_sec_rebars_type = (
            self.xdir_rebars_type,
            self.ydir_rebars_type,
        )
        self.column_sec_hook_orientation = (
            self.xdir_rebars_hook_orientation,
            self.ydir_rebars_hook_orientation,
        )
        self.column_sec_hook_extension = (
            self.xdir_rebars_hook_extension,
            self.ydir_rebars_hook_extension,
        )
        self.column_l_sec_rebar_rounding = (
            self.xdir_rebars_rounding,
            self.ydir_rebars_rounding,
        )

    def getYDirRebarsData(self):
        """This function is used to get data related to ydir rebars from UI."""
        self.ydir_rebars_type = (
            self.sec_ydir_rebars_widget.ydir_rebars_type.currentText()
        )
        self.ydir_rebars_hook_orientation = (
            self.sec_ydir_rebars_widget.ydir_rebars_hookOrientation.currentText()
        )
        self.ydir_rebars_hook_extension = (
            self.sec_ydir_rebars_widget.ydir_rebars_hookExtension.text()
        )
        self.ydir_rebars_hook_extension = FreeCAD.Units.Quantity(
            self.ydir_rebars_hook_extension
        ).Value
        self.ydir_rebars_rounding = (
            self.sec_ydir_rebars_widget.ydir_rebars_rounding.value()
        )
        self.ydir_rebars_t_offset = (
            self.sec_ydir_rebars_widget.ydir_rebars_topOffset.text()
        )
        self.ydir_rebars_t_offset = FreeCAD.Units.Quantity(
            self.ydir_rebars_t_offset
        ).Value
        self.ydir_rebars_number_diameter = (
            self.sec_ydir_rebars_widget.numberDiameter.text()
        )


def editDialog(vobj):
    """Edit Footing Reinforcement"""
    obj = _FootingReinforcementDialog(vobj.Object)
    obj.setupUi()
    setParallelRebarsData(obj, vobj.Object)
    setCrossRebarsData(obj, vobj.Object)
    setColumnsData(obj, vobj.Object)
    setTiesData(obj, vobj.Object)
    setMainRebarsData(obj, vobj.Object)
    setSecRebarsData(obj, vobj.Object)
    obj.form.exec_()


def setParallelRebarsData(obj, FootingReinforcementGroup):
    """Set values for parallel rebars of base of footing reinforcement"""
    if not FootingReinforcementGroup:
        return
    obj.parallel_rebars_widget.meshCoverAlongValue.setCurrentIndex(
        obj.parallel_rebars_widget.meshCoverAlongValue.findText(
            FootingReinforcementGroup.MeshCoverAlong
        )
    )
    obj.parallel_rebars_widget.parallel_l_shapeHookOrientation.setCurrentIndex(
        obj.parallel_rebars_widget.parallel_l_shapeHookOrientation.findText(
            FootingReinforcementGroup.ParallelLShapeHookOrintation
        )
    )
    obj.parallel_rebars_widget.parallel_rebars_type.setCurrentIndex(
        obj.parallel_rebars_widget.parallel_rebars_type.findText(
            FootingReinforcementGroup.ParallelRebarType
        )
    )
    obj.changeParallelRebarType()
    obj.parallel_rebars_widget.parallel_frontCover.setText(
        FootingReinforcementGroup.ParallelFrontCover.UserString
    )
    obj.parallel_rebars_widget.parallel_l_sideCover.setText(
        FootingReinforcementGroup.ParallelLeftCover.UserString
    )
    obj.parallel_rebars_widget.parallel_r_sideCover.setText(
        FootingReinforcementGroup.ParallelRightCover.UserString
    )
    obj.parallel_rebars_widget.parallel_bottomCover.setText(
        FootingReinforcementGroup.ParallelBottomCover.UserString
    )
    obj.parallel_rebars_widget.parallel_topCover.setText(
        FootingReinforcementGroup.ParallelTopCover.UserString
    )
    obj.parallel_rebars_widget.parallel_rearCover.setText(
        FootingReinforcementGroup.ParallelRearCover.UserString
    )
    obj.parallel_rebars_widget.parallel_rounding.setValue(
        FootingReinforcementGroup.ParallelRounding
    )
    obj.parallel_rebars_widget.parallel_diameter.setText(
        FootingReinforcementGroup.ParallelDiameter.UserString
    )
    obj.parallel_rebars_widget.parallel_amount_radio.setChecked(
        FootingReinforcementGroup.ParallelAmountSpacingCheck
    )
    if FootingReinforcementGroup.ParallelAmountSpacingCheck:
        obj.parallelAmountRadioClicked()
    else:
        obj.parallelSpacingRadioClicked()
    obj.parallel_rebars_widget.parallel_spacing_radio.setChecked(
        not FootingReinforcementGroup.ParallelAmountSpacingCheck
    )
    obj.parallel_rebars_widget.parallel_amount.setValue(
        FootingReinforcementGroup.ParallelAmountValue
    )
    obj.parallel_rebars_widget.parallel_spacing.setText(
        FootingReinforcementGroup.ParallelSpacingValue.UserString
    )


def setCrossRebarsData(obj, FootingReinforcementGroup):
    """Set values for cross rebars of base of footing reinforcement"""
    if not FootingReinforcementGroup:
        return

    obj.cross_rebars_widget.cross_l_shapeHookOrientation.setCurrentIndex(
        obj.cross_rebars_widget.cross_l_shapeHookOrientation.findText(
            FootingReinforcementGroup.CrossLShapeHookOrintation
        )
    )
    obj.cross_rebars_widget.cross_rebars_type.setCurrentIndex(
        obj.cross_rebars_widget.cross_rebars_type.findText(
            FootingReinforcementGroup.CrossRebarType
        )
    )
    obj.changeCrossRebarType()
    obj.cross_rebars_widget.cross_frontCover.setText(
        FootingReinforcementGroup.CrossFrontCover.UserString
    )
    obj.cross_rebars_widget.cross_l_sideCover.setText(
        FootingReinforcementGroup.CrossLeftCover.UserString
    )
    obj.cross_rebars_widget.cross_r_sideCover.setText(
        FootingReinforcementGroup.CrossRightCover.UserString
    )
    obj.cross_rebars_widget.cross_bottomCover.setText(
        FootingReinforcementGroup.CrossBottomCover.UserString
    )
    obj.cross_rebars_widget.cross_topCover.setText(
        FootingReinforcementGroup.CrossTopCover.UserString
    )
    obj.cross_rebars_widget.cross_rearCover.setText(
        FootingReinforcementGroup.CrossRearCover.UserString
    )
    obj.cross_rebars_widget.cross_rounding.setValue(
        FootingReinforcementGroup.CrossRounding
    )
    obj.cross_rebars_widget.cross_diameter.setText(
        FootingReinforcementGroup.CrossDiameter.UserString
    )
    obj.cross_rebars_widget.cross_amount_radio.setChecked(
        FootingReinforcementGroup.CrossAmountSpacingCheck
    )
    obj.cross_rebars_widget.cross_spacing_radio.setChecked(
        not FootingReinforcementGroup.CrossAmountSpacingCheck
    )
    if FootingReinforcementGroup.CrossAmountSpacingCheck:
        obj.crossAmountRadioClicked()
    else:
        obj.crossSpacingRadioClicked()
    obj.cross_rebars_widget.cross_amount.setValue(
        FootingReinforcementGroup.CrossAmountValue
    )
    obj.cross_rebars_widget.cross_spacing.setText(
        FootingReinforcementGroup.CrossSpacingValue.UserString
    )


def setColumnsData(obj, FootingReinforcementGroup):
    """Set values for columns of footing reinforcement"""
    obj.columns_widget.columns_frontSpacing.setText(
        FootingReinforcementGroup.ColumnFrontSpacing.UserString
    )
    obj.columns_widget.columns_leftSpacing.setText(
        FootingReinforcementGroup.ColumnLeftSpacing.UserString
    )
    obj.columns_widget.columns_rightSpacing.setText(
        FootingReinforcementGroup.ColumnRightSpacing.UserString
    )
    obj.columns_widget.columns_rearSpacing.setText(
        FootingReinforcementGroup.ColumnRearSpacing.UserString
    )
    obj.columns_widget.column_length.setText(
        FootingReinforcementGroup.ColumnWidth.UserString
    )
    obj.columns_widget.column_width.setText(
        FootingReinforcementGroup.ColumnLength.UserString
    )
    obj.columns_widget.column_xdir_amountRadio.setChecked(
        FootingReinforcementGroup.XDirColumnNumberSpacingCheck
    )
    obj.columns_widget.column_xdir_spacingRadio.setChecked(
        not FootingReinforcementGroup.XDirColumnNumberSpacingCheck
    )
    if FootingReinforcementGroup.XDirColumnNumberSpacingCheck:
        obj.columnXdirAmountRadioClicked()
    else:
        obj.columnXdirSpacingRadioClicked()
    obj.columns_widget.column_xdir_amount.setValue(
        FootingReinforcementGroup.XDirColumnAmountValue
    )
    obj.columns_widget.column_xdir_spacing.setText(
        FootingReinforcementGroup.XDirColumnSpacingValue.UserString
    )
    obj.columns_widget.column_ydir_amountRadio.setChecked(
        FootingReinforcementGroup.YDirColumnNumberSpacingCheck
    )
    obj.columns_widget.column_ydir_spacingRadio.setChecked(
        not FootingReinforcementGroup.YDirColumnNumberSpacingCheck
    )
    if FootingReinforcementGroup.YDirColumnNumberSpacingCheck:
        obj.columnYdirAmountRadioClicked()
    else:
        obj.columnYdirSpacingRadioClicked()
    obj.columns_widget.column_ydir_amount.setValue(
        FootingReinforcementGroup.YDirColumnAmountValue
    )
    obj.columns_widget.column_ydir_spacing.setText(
        FootingReinforcementGroup.YDirColumnSpacingValue.UserString
    )
    obj.columns_widget.column_secRebarCheck.setChecked(
        FootingReinforcementGroup.ColumnSecRebarsCheck
    )
    obj.columnSecRebarCheckClicked()


def setTiesData(obj, FootingReinforcementGroup):
    """Set values for Ties of columns of  footing reinforcement"""
    obj.ties_widget.ties_bottomCover.setText(
        FootingReinforcementGroup.TieBottomCover.UserString
    )
    obj.ties_widget.ties_topCover.setText(
        FootingReinforcementGroup.TieTopCover.UserString
    )
    obj.ties_widget.ties_diameter.setText(
        FootingReinforcementGroup.TieDiameter.UserString
    )
    obj.ties_widget.ties_bentAngle.setCurrentIndex(
        obj.ties_widget.ties_bentAngle.findText(
            str(FootingReinforcementGroup.TieBentAngle)
        )
    )
    obj.ties_widget.ties_extensionFactor.setValue(
        FootingReinforcementGroup.TieExtensionFactor
    )
    obj.ties_widget.ties_number_radio.setChecked(
        FootingReinforcementGroup.TieNumberSpacingCheck
    )
    obj.ties_widget.ties_spacing_radio.setChecked(
        not FootingReinforcementGroup.TieNumberSpacingCheck
    )
    if FootingReinforcementGroup.TieNumberSpacingCheck:
        obj.tiesNumberRadioClicked()
    else:
        obj.tiesSpacingRadioClicked()
    # obj.ties_widget.ties_number.setEnabled(True)
    # obj.ties_widget.ties_spacing.setEnabled(False)
    obj.ties_widget.ties_number.setValue(
        FootingReinforcementGroup.TieAmountValue
    )
    obj.ties_widget.ties_spacing.setText(
        FootingReinforcementGroup.TieSpacingValue.UserString
    )


def setMainRebarsData(obj, FootingReinforcementGroup):
    """Set values for Main Rebars of columns of  footing reinforcement"""
    obj.main_rebars_widget.main_rebars_type.setCurrentIndex(
        obj.main_rebars_widget.main_rebars_type.findText(
            FootingReinforcementGroup.ColumnMainRebarType
        )
    )
    obj.main_rebars_widget.main_rebars_hookOrientation.setCurrentIndex(
        obj.main_rebars_widget.main_rebars_hookOrientation.findText(
            FootingReinforcementGroup.ColumnMainHookOrientation
        )
    )
    obj.main_rebars_widget.main_rebars_hookExtendAlong.setCurrentIndex(
        obj.main_rebars_widget.main_rebars_hookExtendAlong.findText(
            FootingReinforcementGroup.ColumnMainHookExtendAlong
        )
    )
    obj.main_rebars_widget.main_rebars_hookExtension.setText(
        FootingReinforcementGroup.ColumnMainHookExtension.UserString
    )
    obj.main_rebars_widget.main_rebars_rounding.setValue(
        FootingReinforcementGroup.ColumnMainLRebarRounding
    )
    obj.main_rebars_widget.main_rebars_topOffset.setText(
        FootingReinforcementGroup.ColumnMainRebarsTopOffset.UserString
    )
    obj.main_rebars_widget.main_rebars_diameter.setText(
        FootingReinforcementGroup.ColumnMainRebarsDiameter.UserString
    )


def setSecRebarsData(obj, FootingReinforcementGroup):
    """Set values for Secondary Rebars of columns of  footing reinforcement"""
    # set secondry xdir values
    obj.sec_xdir_rebars_widget.xdir_rebars_type.setCurrentIndex(
        obj.sec_xdir_rebars_widget.xdir_rebars_type.findText(
            FootingReinforcementGroup.ColumnSecRebarsType[0]
        )
    )
    obj.sec_xdir_rebars_widget.xdir_rebars_hookOrientation.setCurrentIndex(
        obj.sec_xdir_rebars_widget.xdir_rebars_hookOrientation.findText(
            FootingReinforcementGroup.ColumnSecHookOrientation[0]
        )
    )
    obj.sec_xdir_rebars_widget.xdir_rebars_hookExtension.setText(
        str(FootingReinforcementGroup.ColumnSecHookExtension[0])
    )
    obj.sec_xdir_rebars_widget.xdir_rebars_rounding.setValue(
        FootingReinforcementGroup.ColumnSecLRebarRounding[0]
    )
    obj.sec_xdir_rebars_widget.xdir_rebars_topOffset.setText(
        str(FootingReinforcementGroup.ColumnSecRebarsTopOffset[0])
    )
    obj.sec_xdir_rebars_widget.numberDiameter.setText(
        FootingReinforcementGroup.ColumnSecRebarsNumberDiameter[0]
    )

    # set secondry ydir values
    obj.sec_ydir_rebars_widget.ydir_rebars_type.setCurrentIndex(
        obj.sec_ydir_rebars_widget.ydir_rebars_type.findText(
            FootingReinforcementGroup.ColumnSecRebarsType[1]
        )
    )
    obj.sec_ydir_rebars_widget.ydir_rebars_hookOrientation.setCurrentIndex(
        obj.sec_ydir_rebars_widget.ydir_rebars_hookOrientation.findText(
            FootingReinforcementGroup.ColumnSecHookOrientation[1]
        )
    )
    obj.sec_ydir_rebars_widget.ydir_rebars_hookExtension.setText(
        str(FootingReinforcementGroup.ColumnSecHookExtension[1])
    )
    obj.sec_ydir_rebars_widget.ydir_rebars_rounding.setValue(
        FootingReinforcementGroup.ColumnSecLRebarRounding[1]
    )
    obj.sec_ydir_rebars_widget.ydir_rebars_topOffset.setText(
        str(FootingReinforcementGroup.ColumnSecRebarsTopOffset[1])
    )
    obj.sec_ydir_rebars_widget.numberDiameter.setText(
        FootingReinforcementGroup.ColumnSecRebarsNumberDiameter[1]
    )


def CommandFootingReinforcement():
    """This function is used to invoke dialog box for Footing Reinforcement."""
    selected_obj = check_selected_face()
    if selected_obj:
        dialog = _FootingReinforcementDialog()
        dialog.setupUi()
        dialog.form.exec_()
