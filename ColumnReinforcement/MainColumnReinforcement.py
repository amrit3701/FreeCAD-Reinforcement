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

__title__ = "Column Reinforcement"
__author__ = "Suraj"
__url__ = "https://www.freecadweb.org"

from pathlib import Path
from PySide2 import QtGui, QtWidgets

import FreeCAD
import FreeCADGui

from Rebarfunc import check_selected_face, showWarning
from ColumnReinforcement.SingleTieMultipleRebars import (
    makeSingleTieMultipleRebars,
    editSingleTieMultipleRebars,
)
from ColumnReinforcement.RebarNumberDiameter import runNumberDiameterDialog
from ColumnReinforcement import CircularColumn
from ColumnReinforcement.TwoTiesSixRebars import (
    makeTwoTiesSixRebars,
    editTwoTiesSixRebars,
)


class _ColumnReinforcementDialog:
    def __init__(self, RebarGroup=None):
        """This function set initial data in Column Reinforcement dialog box."""
        self.column_type = "RectangularColumn"
        if not RebarGroup:
            # If column reinforcement is not created yet, then get SelectedObj
            # from FreeCAD Gui selection
            selected_obj = FreeCADGui.Selection.getSelectionEx()[0]
            self.SelectedObj = selected_obj.Object
            self.FaceName = selected_obj.SubElementNames[0]
            self.CustomSpacing = None
        else:
            # If column reinforcement is already created, then get selectedObj
            # from data stored in created Tie
            for rebar_group in RebarGroup.RebarGroups:
                if RebarGroup.ColumnType == "RectangularColumn":
                    if hasattr(rebar_group, "Ties"):
                        Tie = rebar_group.Ties[0]
                        self.FaceName = Tie.Base.Support[0][1][0]
                        self.SelectedObj = Tie.Base.Support[0][0]
                        self.CustomSpacing = Tie.CustomSpacing
                        break
                else:
                    if hasattr(rebar_group, "HelicalRebars"):
                        helical_rebar = rebar_group.HelicalRebars[0]
                        self.FaceName = helical_rebar.Base.Support[0][1][0]
                        self.SelectedObj = helical_rebar.Base.Support[0][0]
                        self.CustomSpacing = helical_rebar.CustomSpacing
                        break
        # Load ui from file MainColumnReinforcement.ui
        self.form = FreeCADGui.PySideUic.loadUi(
            str(Path(__file__).with_suffix(".ui").absolute())
        )
        self.form.setWindowTitle(
            QtWidgets.QApplication.translate(
                "RebarAddon", "Column Reinforcement", None
            )
        )
        self.RebarGroup = RebarGroup

    def setupUi(self):
        """This function is used to add components to ui."""
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
        self.circular_column_widget = FreeCADGui.PySideUic.loadUi(
            str(Path(__file__).parent.absolute() / "CircularColumn.ui")
        )
        self.form.rebars_stackedWidget.addWidget(self.circular_column_widget)
        # Add dropdown menu items
        self.addDropdownMenuItems()
        # Add image of Single Tie
        self.form.image.setPixmap(
            QtGui.QPixmap(
                str(
                    Path(__file__).parent.parent.absolute()
                    / "icons"
                    / "Column_SingleTieMultipleRebars.png"
                )
            )
        )
        if self.RebarGroup:
            self.form.ties_configuration.setEnabled(False)
        # Set default values in UI
        self.setDefaultValues()
        # Connect signals and slots
        self.connectSignalSlots()

    def setDefaultValues(self):
        # Set default values in UI
        # Set Ties data
        self.form.ties_configuration.setCurrentIndex(
            self.form.ties_configuration.findText("SingleTie")
        )
        self.ties_widget.ties_leftCover.setText(FreeCAD.Units.Quantity(40.00, "mm").UserString)
        self.ties_widget.ties_rightCover.setText(FreeCAD.Units.Quantity(40.00, "mm").UserString)
        self.ties_widget.ties_topCover.setText(FreeCAD.Units.Quantity(40.00, "mm").UserString)
        self.ties_widget.ties_bottomCover.setText(FreeCAD.Units.Quantity(40.00, "mm").UserString)
        self.ties_widget.ties_allCoversEqual.setChecked(True)
        self.tiesAllCoversEqualClicked()
        self.ties_widget.ties_offset.setText(FreeCAD.Units.Quantity(100.00, "mm").UserString)
        self.ties_widget.ties_diameter.setText(FreeCAD.Units.Quantity(8.00, "mm").UserString)
        self.ties_widget.ties_bentAngle.setCurrentIndex(
            self.ties_widget.ties_bentAngle.findText("135")
        )
        self.ties_widget.ties_extensionFactor.setValue(2)
        self.ties_widget.ties_number_radio.setChecked(True)
        self.ties_widget.ties_spacing_radio.setChecked(False)
        self.ties_widget.ties_number.setEnabled(True)
        self.ties_widget.ties_spacing.setEnabled(False)
        self.ties_widget.ties_number.setValue(5)
        self.ties_widget.ties_spacing.setText(FreeCAD.Units.Quantity(100.00, "mm").UserString)
        # Set Main Rebars data
        self.main_rebars_widget.main_rebars_type.setCurrentIndex(
            self.main_rebars_widget.main_rebars_type.findText("StraightRebar")
        )
        self.main_rebars_widget.main_rebars_hookOrientation.setCurrentIndex(
            self.main_rebars_widget.main_rebars_hookOrientation.findText(
                "Top Inside"
            )
        )
        self.main_rebars_widget.main_rebars_hookExtendAlong.setCurrentIndex(
            self.main_rebars_widget.main_rebars_hookExtendAlong.findText(
                "x-axis"
            )
        )
        self.main_rebars_widget.main_rebars_hookExtension.setText(FreeCAD.Units.Quantity(40.00, "mm").UserString)
        self.main_rebars_widget.main_rebars_rounding.setValue(2)
        self.main_rebars_widget.main_rebars_topOffset.setText(FreeCAD.Units.Quantity(0.00, "mm").UserString)
        self.main_rebars_widget.main_rebars_bottomOffset.setText(FreeCAD.Units.Quantity(0.00, "mm").UserString)
        self.main_rebars_widget.main_rebars_diameter.setText(FreeCAD.Units.Quantity(20.00, "mm").UserString)
        # Set Secondary Xdir Rebars Data
        self.sec_xdir_rebars_widget.xdir_rebars_type.setCurrentIndex(
            self.sec_xdir_rebars_widget.xdir_rebars_type.findText(
                "StraightRebar"
            )
        )
        self.sec_xdir_rebars_widget.xdir_rebars_hookOrientation.setCurrentIndex(
            self.sec_xdir_rebars_widget.xdir_rebars_hookOrientation.findText(
                "Top Inside"
            )
        )
        self.sec_xdir_rebars_widget.xdir_rebars_hookExtension.setText(
            FreeCAD.Units.Quantity(40.00, "mm").UserString
        )
        self.sec_xdir_rebars_widget.xdir_rebars_rounding.setValue(1)
        self.sec_xdir_rebars_widget.xdir_rebars_topOffset.setText(FreeCAD.Units.Quantity(0.00, "mm").UserString)
        self.sec_xdir_rebars_widget.xdir_rebars_bottomOffset.setText(FreeCAD.Units.Quantity(0.00, "mm").UserString)
        self.sec_xdir_rebars_widget.numberDiameter.setText(
            "2#20mm+1#16mm+2#20mm"
        )
        # Set Secondary Ydir Rebars Data
        self.sec_ydir_rebars_widget.ydir_rebars_type.setCurrentIndex(
            self.sec_ydir_rebars_widget.ydir_rebars_type.findText(
                "StraightRebar"
            )
        )
        self.sec_ydir_rebars_widget.ydir_rebars_hookOrientation.setCurrentIndex(
            self.sec_ydir_rebars_widget.ydir_rebars_hookOrientation.findText(
                "Top Inside"
            )
        )
        self.sec_ydir_rebars_widget.ydir_rebars_hookExtension.setText(
            FreeCAD.Units.Quantity(40.00, "mm").UserString
        )
        self.sec_ydir_rebars_widget.ydir_rebars_rounding.setValue(1)
        self.sec_ydir_rebars_widget.ydir_rebars_topOffset.setText(FreeCAD.Units.Quantity(0.00, "mm").UserString)
        self.sec_ydir_rebars_widget.ydir_rebars_bottomOffset.setText(FreeCAD.Units.Quantity(0.00, "mm").UserString)
        self.sec_ydir_rebars_widget.numberDiameter.setText(
            "1#20mm+1#16mm+1#20mm"
        )
        # Set circular column data
        self.circular_column_widget.sideCover.setText(FreeCAD.Units.Quantity(20.00, "mm").UserString)
        self.circular_column_widget.helical_rebars_topOffset.setText(FreeCAD.Units.Quantity(40.00, "mm").UserString)
        self.circular_column_widget.helical_rebars_bottomOffset.setText(
            FreeCAD.Units.Quantity(40.00, "mm").UserString
        )
        self.circular_column_widget.pitch.setText(FreeCAD.Units.Quantity(50.00, "mm").UserString)
        self.circular_column_widget.helical_rebars_diameter.setText(FreeCAD.Units.Quantity(8.00, "mm").UserString)
        self.circular_column_widget.main_rebars_topOffset.setText(FreeCAD.Units.Quantity(20.00, "mm").UserString)
        self.circular_column_widget.main_rebars_bottomOffset.setText(FreeCAD.Units.Quantity(20.00, "mm").UserString)
        self.circular_column_widget.main_rebars_diameter.setText(FreeCAD.Units.Quantity(16.00, "mm").UserString)
        self.circular_column_widget.main_rebars_number_radio.setChecked(True)
        self.circular_column_widget.main_rebars_angle_radio.setChecked(False)
        self.circular_column_widget.main_rebars_number.setEnabled(True)
        self.circular_column_widget.main_rebars_angle.setEnabled(False)
        self.circular_column_widget.main_rebars_number.setValue(6)
        self.circular_column_widget.main_rebars_angle.setValue(60)

    def addDropdownMenuItems(self):
        """This function add dropdown items to each Gui::PrefComboBox."""
        # Add ties configurations
        self.form.ties_configuration.addItems(["SingleTie", "TwoTiesSixRebars"])
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
        self.form.rectangular_column_radio.clicked.connect(
            self.rectangularColumnRadioClicked
        )
        self.form.circular_column_radio.clicked.connect(
            self.circularColumnRadioClicked
        )
        self.form.rebars_listWidget.currentRowChanged.connect(
            self.changeRebarsListWidget
        )
        self.form.ties_configuration.currentIndexChanged.connect(
            self.changeTiesConfiguration
        )
        self.ties_widget.ties_leftCover.textChanged.connect(
            self.tiesLeftCoverChanged
        )
        self.ties_widget.ties_allCoversEqual.clicked.connect(
            self.tiesAllCoversEqualClicked
        )
        self.ties_widget.ties_number_radio.clicked.connect(
            self.tiesNumberRadioClicked
        )
        self.ties_widget.ties_spacing_radio.clicked.connect(
            self.tiesSpacingRadioClicked
        )
        self.ties_widget.ties_customSpacing.clicked.connect(
            self.runRebarDistribution
        )
        self.ties_widget.ties_removeCustomSpacing.clicked.connect(
            self.removeRebarDistribution
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
        self.circular_column_widget.main_rebars_number_radio.clicked.connect(
            self.mainRebarsNumberRadioClicked
        )
        self.circular_column_widget.main_rebars_angle_radio.clicked.connect(
            self.mainRebarsAngleRadioClicked
        )
        self.form.next_button.clicked.connect(self.nextButtonClicked)
        self.form.back_button.clicked.connect(self.backButtonClicked)
        self.form.standardButtonBox.clicked.connect(self.clicked)

    def reset(self):
        if not self.RebarGroup:
            self.setDefaultValues()
        else:
            if self.column_type == "RectangularColumn":
                setTiesData(self, None)
                setMainRebarsData(self, None)
                if self.ties_configuration == "SingleTie":
                    setXDirRebarsData(self, None)
                    setYDirRebarsData(self, None)
            else:
                setCircularColumnReinforcementData(self, None)

    def circularColumnRadioClicked(self):
        self.column_type = "CircularColumn"
        self.form.rebars_listWidget.hide()
        self.form.ties_configuration.hide()
        self.form.ties_sequenceLabel.hide()
        self.form.ties_sequenceListWidget.hide()
        self.form.rebars_stackedWidget.setCurrentIndex(4)
        self.form.back_button.hide()
        self.form.image.setPixmap(
            QtGui.QPixmap(
                str(
                    Path(__file__).parent.parent.absolute()
                    / "icons"
                    / "CircularColumnReinforcement.png"
                )
            )
        )
        self.form.next_button.setText("Finish")

    def rectangularColumnRadioClicked(self):
        self.column_type = "RectangularColumn"
        self.form.rebars_listWidget.show()
        self.form.ties_configuration.show()
        self.form.ties_sequenceLabel.show()
        self.form.ties_sequenceListWidget.show()
        self.form.rebars_stackedWidget.setCurrentIndex(
            self.form.rebars_listWidget.currentRow()
        )
        self.form.back_button.show()
        self.changeTiesConfiguration()
        self.form.next_button.setText("Next")

    def changeRebarsListWidget(self, index):
        max_index = self.form.rebars_listWidget.count() - 1
        if index == max_index:
            self.form.next_button.setText("Finish")
        else:
            self.form.next_button.setText("Next")
        self.form.rebars_stackedWidget.setCurrentIndex(index)

    def changeTiesConfiguration(self):
        """This function is used to find selected ties configuration from UI
        and update UI accordingly."""
        self.ties_configuration = self.form.ties_configuration.currentText()
        if self.ties_configuration == "SingleTie":
            self.form.image.setPixmap(
                QtGui.QPixmap(
                    str(
                        Path(__file__).parent.parent.absolute()
                        / "icons"
                        / "Column_SingleTieMultipleRebars.png"
                    )
                )
            )
            self.sec_xdir_rebars_widget.setEnabled(True)
            self.sec_ydir_rebars_widget.setEnabled(True)
            self.form.ties_sequenceLabel.setEnabled(False)
            self.form.ties_sequenceListWidget.setEnabled(False)
        elif self.ties_configuration == "TwoTiesSixRebars":
            self.form.image.setPixmap(
                QtGui.QPixmap(
                    str(
                        Path(__file__).parent.parent.absolute()
                        / "icons"
                        / "Column_TwoTiesSixRebars.png"
                    )
                )
            )
            self.sec_xdir_rebars_widget.setEnabled(False)
            self.sec_ydir_rebars_widget.setEnabled(False)
            self.form.ties_sequenceLabel.setEnabled(True)
            self.form.ties_sequenceListWidget.setEnabled(True)

    def tiesLeftCoverChanged(self):
        if self.ties_widget.ties_allCoversEqual.isChecked():
            # Set right/top/bottom cover equal to left cover
            left_cover = self.ties_widget.ties_leftCover.text()
            self.ties_widget.ties_rightCover.setText(left_cover)
            self.ties_widget.ties_topCover.setText(left_cover)
            self.ties_widget.ties_bottomCover.setText(left_cover)

    def tiesAllCoversEqualClicked(self):
        if self.ties_widget.ties_allCoversEqual.isChecked():
            # Disable fields for right/top/bottom cover
            self.ties_widget.ties_rightCover.setEnabled(False)
            self.ties_widget.ties_topCover.setEnabled(False)
            self.ties_widget.ties_bottomCover.setEnabled(False)
            # Set right/top/bottom cover equal to left cover
            self.tiesLeftCoverChanged()
        else:
            # Enable fields for right/top/bottom cover
            self.ties_widget.ties_rightCover.setEnabled(True)
            self.ties_widget.ties_topCover.setEnabled(True)
            self.ties_widget.ties_bottomCover.setEnabled(True)

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

    def runRebarDistribution(self):
        offset_of_ties = self.ties_widget.ties_offset.text()
        offset_of_ties = FreeCAD.Units.Quantity(offset_of_ties).Value
        from RebarDistribution import runRebarDistribution

        runRebarDistribution(self, offset_of_ties)

    def removeRebarDistribution(self):
        self.CustomSpacing = None
        if self.RebarGroup:
            for Tie in self.RebarGroup.RebarGroups[0].Ties:
                Tie.CustomSpacing = ""
        FreeCAD.ActiveDocument.recompute()

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

    def mainRebarsNumberRadioClicked(self):
        self.circular_column_widget.main_rebars_number.setEnabled(True)
        self.circular_column_widget.main_rebars_angle.setEnabled(False)

    def mainRebarsAngleRadioClicked(self):
        self.circular_column_widget.main_rebars_number.setEnabled(False)
        self.circular_column_widget.main_rebars_angle.setEnabled(True)

    def nextButtonClicked(self):
        if self.form.next_button.text() == "Finish":
            self.accept()
        index = self.form.rebars_listWidget.currentRow()
        index += 1
        max_index = self.form.rebars_listWidget.count() - 1
        if index <= max_index:
            self.form.rebars_listWidget.setCurrentRow(index)

    def backButtonClicked(self):
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
        self.ties_configuration = self.form.ties_configuration.currentText()
        if not self.RebarGroup:
            if self.column_type == "RectangularColumn":
                if self.ties_configuration == "SingleTie":
                    self.getTiesData()
                    self.getMainRebarsData()
                    self.getXDirRebarsData()
                    self.getYDirRebarsData()
                    RebarGroup = makeSingleTieMultipleRebars(
                        self.ties_l_cover,
                        self.ties_r_cover,
                        self.ties_t_cover,
                        self.ties_b_cover,
                        self.ties_offset,
                        self.ties_bent_angle,
                        self.ties_extension_factor,
                        self.ties_diameter,
                        self.ties_number_spacing_check,
                        self.ties_number_spacing_value,
                        self.main_rebars_diameter,
                        self.main_rebars_t_offset,
                        self.main_rebars_b_offset,
                        self.main_rebars_type,
                        self.main_rebars_hook_orientation,
                        self.main_rebars_hook_extend_along,
                        self.main_rebars_rounding,
                        self.main_rebars_hook_extension,
                        (self.xdir_rebars_t_offset, self.ydir_rebars_t_offset),
                        (self.xdir_rebars_b_offset, self.ydir_rebars_b_offset),
                        (
                            self.xdir_rebars_number_diameter,
                            self.ydir_rebars_number_diameter,
                        ),
                        (self.xdir_rebars_type, self.ydir_rebars_type),
                        (
                            self.xdir_rebars_hook_orientation,
                            self.ydir_rebars_hook_orientation,
                        ),
                        (self.xdir_rebars_rounding, self.ydir_rebars_rounding),
                        (
                            self.xdir_rebars_hook_extension,
                            self.ydir_rebars_hook_extension,
                        ),
                        self.SelectedObj,
                        self.FaceName,
                    )
                elif self.ties_configuration == "TwoTiesSixRebars":
                    self.getTiesData()
                    self.getMainRebarsData()
                    RebarGroup = makeTwoTiesSixRebars(
                        self.ties_l_cover,
                        self.ties_r_cover,
                        self.ties_t_cover,
                        self.ties_b_cover,
                        self.ties_offset,
                        self.ties_bent_angle,
                        self.ties_extension_factor,
                        self.ties_diameter,
                        self.ties_number_spacing_check,
                        self.ties_number_spacing_value,
                        self.main_rebars_diameter,
                        self.main_rebars_t_offset,
                        self.main_rebars_b_offset,
                        self.main_rebars_type,
                        self.main_rebars_hook_orientation,
                        self.main_rebars_hook_extend_along,
                        self.main_rebars_rounding,
                        self.main_rebars_hook_extension,
                        self.ties_sequence,
                        self.SelectedObj,
                        self.FaceName,
                    )
            else:
                self.getCircularColumnReinforcementData()
                RebarGroup = CircularColumn.makeReinforcement(
                    self.cir_h_rebar_s_cover,
                    self.cir_h_rebar_t_offset,
                    self.cir_h_rebar_b_offset,
                    self.cir_h_rebar_pitch,
                    self.cir_h_rebar_diameter,
                    self.cir_m_rebar_t_offset,
                    self.cir_m_rebar_b_offset,
                    self.cir_m_rebar_diameter,
                    self.cir_number_angle_check,
                    self.cir_number_angle_value,
                    self.SelectedObj,
                    self.FaceName,
                ).rebar_group
        else:
            if self.column_type == "RectangularColumn":
                if self.ties_configuration == "SingleTie":
                    self.getTiesData()
                    self.getMainRebarsData()
                    self.getXDirRebarsData()
                    self.getYDirRebarsData()
                    RebarGroup = editSingleTieMultipleRebars(
                        self.RebarGroup,
                        self.ties_l_cover,
                        self.ties_r_cover,
                        self.ties_t_cover,
                        self.ties_b_cover,
                        self.ties_offset,
                        self.ties_bent_angle,
                        self.ties_extension_factor,
                        self.ties_diameter,
                        self.ties_number_spacing_check,
                        self.ties_number_spacing_value,
                        self.main_rebars_diameter,
                        self.main_rebars_t_offset,
                        self.main_rebars_b_offset,
                        self.main_rebars_type,
                        self.main_rebars_hook_orientation,
                        self.main_rebars_hook_extend_along,
                        self.main_rebars_rounding,
                        self.main_rebars_hook_extension,
                        (self.xdir_rebars_t_offset, self.ydir_rebars_t_offset),
                        (self.xdir_rebars_b_offset, self.ydir_rebars_b_offset),
                        (
                            self.xdir_rebars_number_diameter,
                            self.ydir_rebars_number_diameter,
                        ),
                        (self.xdir_rebars_type, self.ydir_rebars_type),
                        (
                            self.xdir_rebars_hook_orientation,
                            self.ydir_rebars_hook_orientation,
                        ),
                        (self.xdir_rebars_rounding, self.ydir_rebars_rounding),
                        (
                            self.xdir_rebars_hook_extension,
                            self.ydir_rebars_hook_extension,
                        ),
                        self.SelectedObj,
                        self.FaceName,
                    )
                elif self.ties_configuration == "TwoTiesSixRebars":
                    self.getTiesData()
                    self.getMainRebarsData()
                    RebarGroup = editTwoTiesSixRebars(
                        self.RebarGroup,
                        self.ties_l_cover,
                        self.ties_r_cover,
                        self.ties_t_cover,
                        self.ties_b_cover,
                        self.ties_offset,
                        self.ties_bent_angle,
                        self.ties_extension_factor,
                        self.ties_diameter,
                        self.ties_number_spacing_check,
                        self.ties_number_spacing_value,
                        self.main_rebars_diameter,
                        self.main_rebars_t_offset,
                        self.main_rebars_b_offset,
                        self.main_rebars_type,
                        self.main_rebars_hook_orientation,
                        self.main_rebars_hook_extend_along,
                        self.main_rebars_rounding,
                        self.main_rebars_hook_extension,
                        self.ties_sequence,
                        self.SelectedObj,
                        self.FaceName,
                    )
            else:
                self.getCircularColumnReinforcementData()
                RebarGroup = CircularColumn.editReinforcement(
                    self.RebarGroup,
                    self.cir_h_rebar_s_cover,
                    self.cir_h_rebar_t_offset,
                    self.cir_h_rebar_b_offset,
                    self.cir_h_rebar_pitch,
                    self.cir_h_rebar_diameter,
                    self.cir_m_rebar_t_offset,
                    self.cir_m_rebar_b_offset,
                    self.cir_m_rebar_diameter,
                    self.cir_number_angle_check,
                    self.cir_number_angle_value,
                    self.SelectedObj,
                    self.FaceName,
                )
        if self.CustomSpacing:
            if RebarGroup:
                for Tie in RebarGroup.RebarGroups[0].Ties:
                    Tie.CustomSpacing = self.CustomSpacing
                FreeCAD.ActiveDocument.recompute()
        self.RebarGroup = RebarGroup
        if (
            self.form.standardButtonBox.buttonRole(button)
            != QtWidgets.QDialogButtonBox.ApplyRole
        ):
            self.form.close()

    def getTiesData(self):
        """This function is used to get data related to ties from UI."""
        # Get Ties data from UI
        self.ties_l_cover = self.ties_widget.ties_leftCover.text()
        self.ties_l_cover = FreeCAD.Units.Quantity(self.ties_l_cover).Value
        self.ties_r_cover = self.ties_widget.ties_rightCover.text()
        self.ties_r_cover = FreeCAD.Units.Quantity(self.ties_r_cover).Value
        self.ties_t_cover = self.ties_widget.ties_topCover.text()
        self.ties_t_cover = FreeCAD.Units.Quantity(self.ties_t_cover).Value
        self.ties_b_cover = self.ties_widget.ties_bottomCover.text()
        self.ties_b_cover = FreeCAD.Units.Quantity(self.ties_b_cover).Value
        self.ties_offset = self.ties_widget.ties_offset.text()
        self.ties_offset = FreeCAD.Units.Quantity(self.ties_offset).Value
        self.ties_diameter = self.ties_widget.ties_diameter.text()
        self.ties_diameter = FreeCAD.Units.Quantity(self.ties_diameter).Value
        self.ties_bent_angle = int(
            self.ties_widget.ties_bentAngle.currentText()
        )
        self.ties_extension_factor = (
            self.ties_widget.ties_extensionFactor.value()
        )
        self.ties_number_check = self.ties_widget.ties_number_radio.isChecked()
        if self.ties_number_check:
            self.ties_number_spacing_check = True
            self.ties_number_spacing_value = (
                self.ties_widget.ties_number.value()
            )
        else:
            self.ties_number_spacing_check = False
            self.ties_number_spacing_value = (
                self.ties_widget.ties_spacing.text()
            )
            self.ties_number_spacing_value = FreeCAD.Units.Quantity(
                self.ties_number_spacing_value
            ).Value
        if self.ties_configuration == "TwoTiesSixRebars":
            item1 = self.form.ties_sequenceListWidget.item(0).text()
            item2 = self.form.ties_sequenceListWidget.item(1).text()
            self.ties_sequence = (item1, item2)

    def getMainRebarsData(self):
        """This function is used to get data related to main rebars from UI."""
        self.main_rebars_type = (
            self.main_rebars_widget.main_rebars_type.currentText()
        )
        self.main_rebars_hook_orientation = (
            self.main_rebars_widget.main_rebars_hookOrientation.currentText()
        )
        self.main_rebars_hook_extend_along = (
            self.main_rebars_widget.main_rebars_hookExtendAlong.currentText()
        )
        self.main_rebars_hook_extension = (
            self.main_rebars_widget.main_rebars_hookExtension.text()
        )
        self.main_rebars_hook_extension = FreeCAD.Units.Quantity(
            self.main_rebars_hook_extension
        ).Value
        self.main_rebars_rounding = (
            self.main_rebars_widget.main_rebars_rounding.value()
        )
        self.main_rebars_t_offset = (
            self.main_rebars_widget.main_rebars_topOffset.text()
        )
        self.main_rebars_t_offset = FreeCAD.Units.Quantity(
            self.main_rebars_t_offset
        ).Value
        self.main_rebars_b_offset = (
            self.main_rebars_widget.main_rebars_bottomOffset.text()
        )
        self.main_rebars_b_offset = FreeCAD.Units.Quantity(
            self.main_rebars_b_offset
        ).Value
        self.main_rebars_diameter = (
            self.main_rebars_widget.main_rebars_diameter.text()
        )
        self.main_rebars_diameter = FreeCAD.Units.Quantity(
            self.main_rebars_diameter
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
        self.xdir_rebars_b_offset = (
            self.sec_xdir_rebars_widget.xdir_rebars_bottomOffset.text()
        )
        self.xdir_rebars_b_offset = FreeCAD.Units.Quantity(
            self.xdir_rebars_b_offset
        ).Value
        self.xdir_rebars_number_diameter = (
            self.sec_xdir_rebars_widget.numberDiameter.text()
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
        self.ydir_rebars_b_offset = (
            self.sec_ydir_rebars_widget.ydir_rebars_bottomOffset.text()
        )
        self.ydir_rebars_b_offset = FreeCAD.Units.Quantity(
            self.ydir_rebars_b_offset
        ).Value
        self.ydir_rebars_number_diameter = (
            self.sec_ydir_rebars_widget.numberDiameter.text()
        )

    def getCircularColumnReinforcementData(self):
        self.cir_h_rebar_s_cover = self.circular_column_widget.sideCover.text()
        self.cir_h_rebar_s_cover = FreeCAD.Units.Quantity(
            self.cir_h_rebar_s_cover
        ).Value
        self.cir_h_rebar_t_offset = (
            self.circular_column_widget.helical_rebars_topOffset.text()
        )
        self.cir_h_rebar_t_offset = FreeCAD.Units.Quantity(
            self.cir_h_rebar_t_offset
        ).Value
        self.cir_h_rebar_b_offset = (
            self.circular_column_widget.helical_rebars_bottomOffset.text()
        )
        self.cir_h_rebar_b_offset = FreeCAD.Units.Quantity(
            self.cir_h_rebar_b_offset
        ).Value
        self.cir_h_rebar_pitch = self.circular_column_widget.pitch.text()
        self.cir_h_rebar_pitch = FreeCAD.Units.Quantity(
            self.cir_h_rebar_pitch
        ).Value
        self.cir_h_rebar_diameter = (
            self.circular_column_widget.helical_rebars_diameter.text()
        )
        self.cir_h_rebar_diameter = FreeCAD.Units.Quantity(
            self.cir_h_rebar_diameter
        ).Value
        self.cir_m_rebar_t_offset = (
            self.circular_column_widget.main_rebars_topOffset.text()
        )
        self.cir_m_rebar_t_offset = FreeCAD.Units.Quantity(
            self.cir_m_rebar_t_offset
        ).Value
        self.cir_m_rebar_b_offset = (
            self.circular_column_widget.main_rebars_bottomOffset.text()
        )
        self.cir_m_rebar_b_offset = FreeCAD.Units.Quantity(
            self.cir_m_rebar_b_offset
        ).Value
        self.cir_m_rebar_diameter = (
            self.circular_column_widget.main_rebars_diameter.text()
        )
        self.cir_m_rebar_diameter = FreeCAD.Units.Quantity(
            self.cir_m_rebar_diameter
        ).Value
        self.cir_number_check = (
            self.circular_column_widget.main_rebars_number_radio.isChecked()
        )
        if self.cir_number_check:
            self.cir_number_angle_check = True
            self.cir_number_angle_value = (
                self.circular_column_widget.main_rebars_number.value()
            )
        else:
            self.cir_number_angle_check = False
            self.cir_number_angle_value = (
                self.circular_column_widget.main_rebars_angle.value()
            )


def editDialog(vobj):
    # Check if all rebar groups deleted or not
    if len(vobj.Object.RebarGroups) == 0:
        showWarning("Nothing to edit. You have deleted all rebar groups.")
        return
    ties_group = None
    for i, rebar_group in enumerate(vobj.Object.RebarGroups):
        if vobj.Object.ColumnType == "RectangularColumn":
            # Check if ties group exists
            if hasattr(rebar_group, "Ties"):
                # Check if ties exists
                if len(rebar_group.Ties) > 0:
                    ties_group = rebar_group
                    break
                else:
                    showWarning(
                        "You have deleted ties. Please recreate the "
                        "ColumnReinforcement."
                    )
                    return
            elif i == len(vobj.Object.RebarGroups) - 1:
                showWarning(
                    "You have deleted ties group. Please recreate the "
                    "ColumnReinforcement."
                )
                return
        else:
            # Check if HelicalRebars group exists
            if hasattr(rebar_group, "HelicalRebars"):
                # Check if helical_rebar exists
                if len(rebar_group.HelicalRebars) > 0:
                    break
                else:
                    showWarning(
                        "You have deleted helical rebars. Please recreate the "
                        "ColumnReinforcement."
                    )
                    return
            elif i == len(vobj.Object.RebarGroups) - 1:
                showWarning(
                    "You have deleted HelicalRebars group. Please recreate the "
                    "ColumnReinforcement."
                )
                return
    obj = _ColumnReinforcementDialog(vobj.Object)
    obj.setupUi()
    if ties_group:
        obj.form.rectangular_column_radio.setChecked(True)
        obj.rectangularColumnRadioClicked()
        obj.form.ties_configuration.setCurrentIndex(
            obj.form.ties_configuration.findText(
                str(ties_group.TiesConfiguration)
            )
        )
        setTiesData(obj, vobj)
        obj.main_rebars_widget.setEnabled(False)
        obj.sec_xdir_rebars_widget.setEnabled(False)
        obj.sec_ydir_rebars_widget.setEnabled(False)
        for i, rebar_group in enumerate(vobj.Object.RebarGroups):
            if hasattr(rebar_group, "MainRebars"):
                if len(rebar_group.MainRebars) > 0:
                    setMainRebarsData(obj, vobj)
                    obj.main_rebars_widget.setEnabled(True)
            elif hasattr(rebar_group, "SecondaryRebars"):
                if len(rebar_group.SecondaryRebars) > 0:
                    for sec_rebar in rebar_group.SecondaryRebars:
                        if hasattr(sec_rebar, "XDirRebars"):
                            if len(sec_rebar.XDirRebars) > 0:
                                setXDirRebarsData(obj, vobj)
                                obj.sec_xdir_rebars_widget.setEnabled(True)
                        elif hasattr(sec_rebar, "YDirRebars"):
                            if len(sec_rebar.YDirRebars) > 0:
                                setYDirRebarsData(obj, vobj)
                                obj.sec_ydir_rebars_widget.setEnabled(True)
    else:
        obj.form.circular_column_radio.setChecked(True)
        obj.circularColumnRadioClicked()
        setCircularColumnReinforcementData(obj, vobj)

    obj.form.exec_()


def setTiesData(obj, vobj):
    if vobj:
        for rebar_group in vobj.Object.RebarGroups:
            if hasattr(rebar_group, "Ties"):
                Ties = rebar_group
                break
    else:
        for rebar_group in obj.RebarGroup.RebarGroups:
            if hasattr(rebar_group, "Ties"):
                Ties = rebar_group
                break

    if not (
        str(Ties.LeftCover)
        == str(Ties.RightCover)
        == str(Ties.TopCover)
        == str(Ties.BottomCover)
    ):
        obj.ties_widget.ties_allCoversEqual.setChecked(False)
        obj.tiesAllCoversEqualClicked()
        obj.ties_widget.ties_rightCover.setEnabled(True)
        obj.ties_widget.ties_topCover.setEnabled(True)
        obj.ties_widget.ties_bottomCover.setEnabled(True)
    obj.ties_widget.ties_leftCover.setText(str(Ties.LeftCover))
    obj.ties_widget.ties_rightCover.setText(str(Ties.RightCover))
    obj.ties_widget.ties_topCover.setText(str(Ties.TopCover))
    obj.ties_widget.ties_bottomCover.setText(str(Ties.BottomCover))
    Tie = Ties.Ties[0]
    obj.ties_widget.ties_offset.setText(str(Ties.Ties[0].FrontCover))
    if Ties.TiesConfiguration == "TwoTiesSixRebars":
        if Ties.TiesSequence[0] == "Tie2" and Ties.TiesSequence[1] == "Tie1":
            obj.ties_widget.ties_offset.setText(str(Ties.Ties[1].FrontCover))
    obj.ties_widget.ties_diameter.setText(str(Tie.Diameter))
    obj.ties_widget.ties_bentAngle.setCurrentIndex(
        obj.ties_widget.ties_bentAngle.findText(str(Tie.BentAngle))
    )
    obj.ties_widget.ties_extensionFactor.setValue(Tie.BentFactor)
    if Tie.AmountCheck:
        obj.ties_widget.ties_number.setValue(Tie.Amount)
    else:
        obj.ties_widget.ties_number_radio.setChecked(False)
        obj.ties_widget.ties_spacing_radio.setChecked(True)
        obj.ties_widget.ties_number.setEnabled(False)
        obj.ties_widget.ties_spacing.setEnabled(True)
        obj.ties_widget.ties_spacing.setText(str(Tie.TrueSpacing))
    if Ties.TiesConfiguration == "TwoTiesSixRebars":
        item1 = Ties.TiesSequence[0]
        item2 = Ties.TiesSequence[1]
        obj.form.ties_sequenceListWidget.item(0).setText(item1)
        obj.form.ties_sequenceListWidget.item(1).setText(item2)


def setMainRebarsData(obj, vobj):
    if vobj:
        for rebar_group in vobj.Object.RebarGroups:
            if hasattr(rebar_group, "MainRebars"):
                MainRebars = rebar_group
                break
    else:
        for rebar_group in obj.RebarGroup.RebarGroups:
            if hasattr(rebar_group, "MainRebars"):
                MainRebars = rebar_group
                break
    obj.main_rebars_widget.main_rebars_type.setCurrentIndex(
        obj.main_rebars_widget.main_rebars_type.findText(
            str(MainRebars.RebarType)
        )
    )
    obj.main_rebars_widget.main_rebars_hookOrientation.setCurrentIndex(
        obj.main_rebars_widget.main_rebars_hookOrientation.findText(
            str(MainRebars.HookOrientation)
        )
    )
    obj.main_rebars_widget.main_rebars_hookExtendAlong.setCurrentIndex(
        obj.main_rebars_widget.main_rebars_hookExtendAlong.findText(
            str(MainRebars.HookExtendAlong)
        )
    )
    obj.main_rebars_widget.main_rebars_hookExtension.setText(
        str(MainRebars.HookExtension)
    )
    obj.main_rebars_widget.main_rebars_rounding.setValue(
        MainRebars.MainRebars[0].Rounding
    )
    obj.main_rebars_widget.main_rebars_topOffset.setText(
        str(MainRebars.TopOffset)
    )
    obj.main_rebars_widget.main_rebars_bottomOffset.setText(
        str(MainRebars.BottomOffset)
    )
    obj.main_rebars_widget.main_rebars_diameter.setText(
        str(MainRebars.MainRebars[0].Diameter)
    )


def setXDirRebarsData(obj, vobj):
    if vobj:
        for rebar_group in vobj.Object.RebarGroups:
            if hasattr(rebar_group, "SecondaryRebars"):
                for sec_rebar in rebar_group.SecondaryRebars:
                    if hasattr(sec_rebar, "XDirRebars"):
                        XDirRebarsGroup = sec_rebar
                        break
    else:
        for rebar_group in obj.RebarGroup.RebarGroups:
            if hasattr(rebar_group, "SecondaryRebars"):
                for sec_rebar in rebar_group.SecondaryRebars:
                    if hasattr(sec_rebar, "XDirRebars"):
                        XDirRebarsGroup = sec_rebar
                        break
    obj.sec_xdir_rebars_widget.xdir_rebars_type.setCurrentIndex(
        obj.sec_xdir_rebars_widget.xdir_rebars_type.findText(
            str(XDirRebarsGroup.RebarType)
        )
    )
    obj.sec_xdir_rebars_widget.xdir_rebars_hookOrientation.setCurrentIndex(
        obj.sec_xdir_rebars_widget.xdir_rebars_hookOrientation.findText(
            str(XDirRebarsGroup.HookOrientation)
        )
    )
    obj.sec_xdir_rebars_widget.xdir_rebars_hookExtension.setText(
        str(XDirRebarsGroup.HookExtension)
    )
    obj.sec_xdir_rebars_widget.xdir_rebars_rounding.setValue(
        XDirRebarsGroup.XDirRebars[0].Rounding
    )
    obj.sec_xdir_rebars_widget.xdir_rebars_topOffset.setText(
        str(XDirRebarsGroup.TopOffset)
    )
    obj.sec_xdir_rebars_widget.xdir_rebars_bottomOffset.setText(
        str(XDirRebarsGroup.BottomOffset)
    )
    obj.sec_xdir_rebars_widget.numberDiameter.setText(
        str(XDirRebarsGroup.NumberDiameter)
    )


def setYDirRebarsData(obj, vobj):
    if vobj:
        for rebar_group in vobj.Object.RebarGroups:
            if hasattr(rebar_group, "SecondaryRebars"):
                for sec_rebar in rebar_group.SecondaryRebars:
                    if hasattr(sec_rebar, "YDirRebars"):
                        YDirRebarsGroup = sec_rebar
                        break
    else:
        for rebar_group in obj.RebarGroup.RebarGroups:
            if hasattr(rebar_group, "SecondaryRebars"):
                for sec_rebar in rebar_group.SecondaryRebars:
                    if hasattr(sec_rebar, "YDirRebars"):
                        YDirRebarsGroup = sec_rebar
                        break
    obj.sec_ydir_rebars_widget.ydir_rebars_type.setCurrentIndex(
        obj.sec_ydir_rebars_widget.ydir_rebars_type.findText(
            str(YDirRebarsGroup.RebarType)
        )
    )
    obj.sec_ydir_rebars_widget.ydir_rebars_hookOrientation.setCurrentIndex(
        obj.sec_ydir_rebars_widget.ydir_rebars_hookOrientation.findText(
            str(YDirRebarsGroup.HookOrientation)
        )
    )
    obj.sec_ydir_rebars_widget.ydir_rebars_hookExtension.setText(
        str(YDirRebarsGroup.HookExtension)
    )
    obj.sec_ydir_rebars_widget.ydir_rebars_rounding.setValue(
        YDirRebarsGroup.YDirRebars[0].Rounding
    )
    obj.sec_ydir_rebars_widget.ydir_rebars_topOffset.setText(
        str(YDirRebarsGroup.TopOffset)
    )
    obj.sec_ydir_rebars_widget.ydir_rebars_bottomOffset.setText(
        str(YDirRebarsGroup.BottomOffset)
    )
    obj.sec_ydir_rebars_widget.numberDiameter.setText(
        str(YDirRebarsGroup.NumberDiameter)
    )


def setCircularColumnReinforcementData(obj, vobj):
    if vobj:
        for rebar_group in vobj.Object.RebarGroups:
            if hasattr(rebar_group, "HelicalRebars"):
                helical_rebar_group = rebar_group
                break
    else:
        for rebar_group in obj.RebarGroup.RebarGroups:
            if hasattr(rebar_group, "HelicalRebars"):
                helical_rebar_group = rebar_group
                break
    helical_rebar = helical_rebar_group.HelicalRebars[0]
    obj.circular_column_widget.sideCover.setText(str(helical_rebar.SideCover))
    obj.circular_column_widget.helical_rebars_topOffset.setText(
        str(helical_rebar.TopCover)
    )
    obj.circular_column_widget.helical_rebars_bottomOffset.setText(
        str(helical_rebar.BottomCover)
    )
    obj.circular_column_widget.pitch.setText(str(helical_rebar.Pitch))
    obj.circular_column_widget.helical_rebars_diameter.setText(
        str(helical_rebar.Diameter)
    )
    if vobj:
        for rebar_group in vobj.Object.RebarGroups:
            if hasattr(rebar_group, "MainRebars"):
                main_rebars_group = rebar_group
                break
    else:
        for rebar_group in obj.RebarGroup.RebarGroups:
            if hasattr(rebar_group, "MainRebars"):
                main_rebars_group = rebar_group
                break
    obj.circular_column_widget.main_rebars_topOffset.setText(
        str(main_rebars_group.TopOffset)
    )
    obj.circular_column_widget.main_rebars_bottomOffset.setText(
        str(main_rebars_group.BottomOffset)
    )
    obj.circular_column_widget.main_rebars_diameter.setText(
        str(main_rebars_group.Diameter)
    )
    obj.circular_column_widget.main_rebars_number.setValue(
        main_rebars_group.Number
    )
    obj.circular_column_widget.main_rebars_angle.setValue(
        main_rebars_group.Angle
    )
    if not main_rebars_group.NumberAngleCheck:
        obj.circular_column_widget.main_rebars_angle_radio.setChecked(True)
        obj.mainRebarsAngleRadioClicked()


def CommandColumnReinforcement():
    """This function is used to invoke dialog box for column reinforcement."""
    selected_obj = check_selected_face()
    if selected_obj:
        dialog = _ColumnReinforcementDialog()
        dialog.setupUi()
        dialog.form.exec_()
