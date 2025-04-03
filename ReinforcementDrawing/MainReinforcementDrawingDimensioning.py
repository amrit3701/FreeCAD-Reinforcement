# -*- coding: utf-8 -*-
# ***************************************************************************
# *                                                                         *
# *   Copyright (c) 2020 - Suraj <dadralj18@gmail.com>                      *
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

__title__ = "Reinforcement Drawing Dimensioning Gui"
__author__ = "Suraj"
__url__ = "https://www.freecadweb.org"

from pathlib import Path
from typing import List, Tuple, Optional

import FreeCAD
import FreeCADGui
from PySide import QtGui
from PySide.QtCore import QCoreApplication

from BillOfMaterial.BOMfunc import getReinforcementRebarObjects
from Rebarfunc import showWarning
from .config import (
    REBARS_STROKE_WIDTH,
    REBARS_COLOR_STYLE,
    REBARS_COLOR,
    STRUCTURE_STROKE_WIDTH,
    STRUCTURE_COLOR_STYLE,
    STRUCTURE_COLOR,
    DRAWING_LEFT_OFFSET,
    DRAWING_TOP_OFFSET,
    DRAWING_MIN_RIGHT_OFFSET,
    DRAWING_MIN_BOTTOM_OFFSET,
    DRAWING_MAX_WIDTH,
    DRAWING_MAX_HEIGHT,
    TEMPLATE_FILE,
    DIMENSION_LABEL_FORMAT,
    DIMENSION_FONT_FAMILY,
    DIMENSION_FONT_SIZE,
    DIMENSION_STROKE_WIDTH,
    DIMENSION_LINE_STYLE,
    DIMENSION_LINE_COLOR,
    DIMENSION_TEXT_COLOR,
    DIMENSION_SINGLE_REBAR_LINE_START_SYMBOL,
    DIMENSION_SINGLE_REBAR_LINE_END_SYMBOL,
    DIMENSION_MULTI_REBAR_LINE_START_SYMBOL,
    DIMENSION_MULTI_REBAR_LINE_END_SYMBOL,
    DIMENSION_LINE_MID_POINT_SYMBOL,
    DIMENSION_LEFT_OFFSET,
    DIMENSION_RIGHT_OFFSET,
    DIMENSION_TOP_OFFSET,
    DIMENSION_BOTTOM_OFFSET,
    DIMENSION_LEFT_OFFSET_INCREMENT,
    DIMENSION_RIGHT_OFFSET_INCREMENT,
    DIMENSION_TOP_OFFSET_INCREMENT,
    DIMENSION_BOTTOM_OFFSET_INCREMENT,
    DIMENSION_SINGLE_REBAR_OUTER_DIM,
    DIMENSION_MULTI_REBAR_OUTER_DIM,
    DIMENSION_SINGLE_REBAR_TEXT_POSITION_TYPE,
    DIMENSION_MULTI_REBAR_TEXT_POSITION_TYPE,
)


# TODO: Use(Uncomment) typing.Literal for minimum python3.8


class _ReinforcementDrawingDimensioningDialog:
    """This is a class for Reinforcement Drawing Dimensioning dialog box."""

    def __init__(
        self,
        # views: List[Literal["Front", "Rear", "Left", "Right", "Top", "Bottom"]],
        views: List[str],
        rebars_stroke_width: float,
        # rebars_color_style: Literal["Automatic", "Custom"],
        rebars_color_style: str,
        rebars_color: Tuple[float, float, float],
        structure_stroke_width: float,
        # structure_color_style: Literal["Automatic", "Custom", "None"],
        structure_color_style: str,
        structure_color: Tuple[float, float, float],
        drawing_left_offset: float,
        drawing_top_offset: float,
        drawing_min_right_offset: float,
        drawing_min_bottom_offset: float,
        drawing_max_width: float,
        drawing_max_height: float,
        template_file: str,
        perform_dimensioning: bool,
        dimension_rebars_filter_list: Optional[List],
        dimension_label_format: str,
        dimension_font_family: str,
        dimension_font_size: float,
        dimension_stroke_width: float,
        # dimension_line_style: Literal[
        #     "Continuous",
        #     "Dash",
        #     "Dot",
        #     "DashDot",
        #     "DashDotDot",
        # ],
        dimension_line_style: str,
        dimension_line_color: Tuple[float, float, float],
        dimension_text_color: Tuple[float, float, float],
        # dimension_single_rebar_line_start_symbol: Literal[
        #     "FilledArrow",
        #     "Tick",
        #     "Dot",
        #     "None",
        # ],
        dimension_single_rebar_line_start_symbol: str,
        # dimension_single_rebar_line_end_symbol: Literal[
        #     "FilledArrow",
        #     "Tick",
        #     "Dot",
        #     "None",
        # ],
        dimension_single_rebar_line_end_symbol: str,
        # dimension_multi_rebar_line_start_symbol: Literal[
        #     "FilledArrow",
        #     "Tick",
        #     "Dot",
        #     "None",
        # ],
        dimension_multi_rebar_line_start_symbol: str,
        # dimension_multi_rebar_line_end_symbol: Literal[
        #     "FilledArrow",
        #     "Tick",
        #     "Dot",
        #     "None",
        # ],
        dimension_multi_rebar_line_end_symbol: str,
        # dimension_line_mid_point_symbol: Literal[
        #     "Tick",
        #     "Dot",
        #     "None",
        # ],
        dimension_line_mid_point_symbol: str,
        dimension_left_offset: float,
        dimension_right_offset: float,
        dimension_top_offset: float,
        dimension_bottom_offset: float,
        dimension_left_offset_increment: float,
        dimension_right_offset_increment: float,
        dimension_top_offset_increment: float,
        dimension_bottom_offset_increment: float,
        dimension_single_rebar_outer_dim: bool,
        dimension_multi_rebar_outer_dim: bool,
        # dimension_single_rebar_text_position_type: Literal[
        #     "MidOfLine",
        #     "StartOfLine",
        #     "EndOfLine",
        # ],
        dimension_single_rebar_text_position_type: str,
        # dimension_multi_rebar_text_position_type: Literal[
        #     "MidOfLine",
        #     "StartOfLine",
        #     "EndOfLine",
        # ],
        dimension_multi_rebar_text_position_type: str,
    ):
        """This function set initial data in Reinforcement Drawing Dimensioning
        dialog box."""
        self.views = views
        self.rebars_stroke_width = rebars_stroke_width
        self.rebars_color_style = rebars_color_style
        self.rebars_color = rebars_color
        self.structure_stroke_width = structure_stroke_width
        self.structure_color_style = structure_color_style
        self.structure_color = structure_color
        self.drawing_left_offset = drawing_left_offset
        self.drawing_top_offset = drawing_top_offset
        self.drawing_min_right_offset = drawing_min_right_offset
        self.drawing_min_bottom_offset = drawing_min_bottom_offset
        self.drawing_max_width = drawing_max_width
        self.drawing_max_height = drawing_max_height
        self.template_file = template_file
        self.perform_dimensioning = perform_dimensioning
        self.dimension_rebars_filter_list = dimension_rebars_filter_list
        self.dimension_label_format = dimension_label_format
        self.dimension_font_family = dimension_font_family
        self.dimension_font_size = dimension_font_size
        self.dimension_stroke_width = dimension_stroke_width
        self.dimension_line_style = dimension_line_style
        self.dimension_line_color = dimension_line_color
        self.dimension_text_color = dimension_text_color
        self.dimension_single_rebar_line_start_symbol = (
            dimension_single_rebar_line_start_symbol
        )
        self.dimension_single_rebar_line_end_symbol = (
            dimension_single_rebar_line_end_symbol
        )
        self.dimension_multi_rebar_line_start_symbol = (
            dimension_multi_rebar_line_start_symbol
        )
        self.dimension_multi_rebar_line_end_symbol = (
            dimension_multi_rebar_line_end_symbol
        )
        self.dimension_line_mid_point_symbol = dimension_line_mid_point_symbol
        self.dimension_left_offset = dimension_left_offset
        self.dimension_right_offset = dimension_right_offset
        self.dimension_top_offset = dimension_top_offset
        self.dimension_bottom_offset = dimension_bottom_offset
        self.dimension_left_offset_increment = dimension_left_offset_increment
        self.dimension_right_offset_increment = dimension_right_offset_increment
        self.dimension_top_offset_increment = dimension_top_offset_increment
        self.dimension_bottom_offset_increment = (
            dimension_bottom_offset_increment
        )
        self.dimension_single_rebar_outer_dim = dimension_single_rebar_outer_dim
        self.dimension_multi_rebar_outer_dim = dimension_multi_rebar_outer_dim
        self.dimension_single_rebar_text_position_type = (
            dimension_single_rebar_text_position_type
        )
        self.dimension_multi_rebar_text_position_type = (
            dimension_multi_rebar_text_position_type
        )
        # Load ui from file ReinforcementDrawingDimensioning_Main.ui
        self.form = FreeCADGui.PySideUic.loadUi(
            str(
                Path(__file__).parent.absolute()
                / "ReinforcementDrawingDimensioning_Main.ui"
            )
        )
        self.form.setWindowTitle(
            QCoreApplication.translate(
                "ReinforcementWorkbench",
                "Reinforcement Drawing Dimensioning",
                None,
            )
        )

    def setupUi(self):
        """This function is used to add components to ui."""
        # Load and add widgets into stacked widget
        self.shapes_data_widget = FreeCADGui.PySideUic.loadUi(
            str(
                Path(__file__).parent.absolute()
                / "ReinforcementDrawingDimensioning_Shapes.ui"
            )
        )
        self.form.reinforcement_drawing_stacked_widget.addWidget(
            self.shapes_data_widget
        )
        self.drawing_widget = FreeCADGui.PySideUic.loadUi(
            str(
                Path(__file__).parent.absolute()
                / "ReinforcementDrawingDimensioning_Drawing.ui"
            )
        )
        self.form.reinforcement_drawing_stacked_widget.addWidget(
            self.drawing_widget
        )
        self.dimension_labels_lines_widget = FreeCADGui.PySideUic.loadUi(
            str(
                Path(__file__).parent.absolute()
                / "ReinforcementDrawingDimensioning_Dimensions1.ui"
            )
        )
        self.form.reinforcement_drawing_stacked_widget.addWidget(
            self.dimension_labels_lines_widget
        )
        self.dimension_single_multi_rebars_widget = FreeCADGui.PySideUic.loadUi(
            str(
                Path(__file__).parent.absolute()
                / "ReinforcementDrawingDimensioning_Dimensions2.ui"
            )
        )
        self.form.reinforcement_drawing_stacked_widget.addWidget(
            self.dimension_single_multi_rebars_widget
        )
        self.dimension_offsets_increments_widget = FreeCADGui.PySideUic.loadUi(
            str(
                Path(__file__).parent.absolute()
                / "ReinforcementDrawingDimensioning_Dimensions3.ui"
            )
        )
        self.form.reinforcement_drawing_stacked_widget.addWidget(
            self.dimension_offsets_increments_widget
        )
        # Set default values in UI
        self.setDefaultValues()
        # Connect signals and slots
        self.connectSignalSlots()

    def setDefaultValues(self):
        """This function is used to set default values in UI."""
        self.setDefaultShapesData()
        self.setDefaultDrawingData()
        self.setDefaultDimensionLabelsLinesData()
        self.setDefaultSingleMultiRebarsData()
        self.setDefaultOffsetsIncrementsData()

    def setDefaultShapesData(self):
        """This function is used to set default values in "Shapes - Rebars &
        Structure" stacked widget in UI."""
        form = self.shapes_data_widget
        form.rebars_stroke_width.setText(
            FreeCAD.Units.Quantity(
                self.rebars_stroke_width, FreeCAD.Units.Length
            ).UserString
        )
        if self.rebars_color_style == "Automatic":
            form.rebars_shape_color_radio.setChecked(True)
            form.rebars_custom_color_radio.setChecked(False)
            form.rebars_color.setEnabled(False)
        else:
            form.rebars_shape_color_radio.setChecked(False)
            form.rebars_custom_color_radio.setChecked(True)
            form.rebars_color.setEnabled(True)
        color = QtGui.QColor()
        color.setRgbF(
            self.rebars_color[0], self.rebars_color[1], self.rebars_color[2]
        )
        form.rebars_color.setProperty("color", color)
        form.structure_stroke_width.setText(
            FreeCAD.Units.Quantity(
                self.structure_stroke_width, FreeCAD.Units.Length
            ).UserString
        )
        if self.structure_color_style == "Automatic":
            form.structure_shape_color_radio.setChecked(True)
            form.structure_color_none.setChecked(False)
            form.structure_custom_color_radio.setChecked(False)
            form.structure_color.setEnabled(False)
        elif self.structure_color_style == "Custom":
            form.structure_shape_color_radio.setChecked(False)
            form.structure_color_none.setChecked(False)
            form.structure_custom_color_radio.setChecked(True)
            form.structure_color.setEnabled(True)
        else:
            form.structure_shape_color_radio.setChecked(False)
            form.structure_color_none.setChecked(True)
            form.structure_custom_color_radio.setChecked(False)
            form.structure_color.setEnabled(False)
        color = QtGui.QColor()
        color.setRgbF(
            self.structure_color[0],
            self.structure_color[1],
            self.structure_color[2],
        )
        form.structure_color.setProperty("color", color)

    def setDefaultDrawingData(self):
        """This function is used to set default values in "Drawing - Views &
        Options" stacked widget in UI."""
        form = self.drawing_widget
        form.front_view_check_box.setChecked("Front" in self.views)
        form.rear_view_check_box.setChecked("Rear" in self.views)
        form.left_view_check_box.setChecked("Left" in self.views)
        form.right_view_check_box.setChecked("Right" in self.views)
        form.top_view_check_box.setChecked("Top" in self.views)
        form.bottom_view_check_box.setChecked("Bottom" in self.views)
        if self.perform_dimensioning:
            form.perform_dimensioning_radio_button.setChecked(True)
            form.perform_no_dimensioning_radio_button.setChecked(False)
        else:
            form.perform_dimensioning_radio_button.setChecked(False)
            form.perform_no_dimensioning_radio_button.setChecked(True)
        form.drawing_left_offset.setText(f"{self.drawing_left_offset} mm")
        form.drawing_top_offset.setText(f"{self.drawing_top_offset} mm")
        form.drawing_min_right_offset.setText(
            f"{self.drawing_min_right_offset} mm"
        )
        form.drawing_min_bottom_offset.setText(
            f"{self.drawing_min_bottom_offset} mm"
        )
        form.drawing_max_width.setText(f"{self.drawing_max_width} mm")
        form.drawing_max_height.setText(f"{self.drawing_max_height} mm")
        form.template_file.setText(self.template_file)

    def setDefaultDimensionLabelsLinesData(self):
        """This function is used to set default values in "Dimensions - Labels &
        Lines" stacked widget in UI."""
        form = self.dimension_labels_lines_widget
        form.dimension_label_format.setText(self.dimension_label_format)
        if (
            form.dimension_font_family.findText(self.dimension_font_family)
            == -1
        ):
            form.dimension_font_family.setCurrentIndex(0)
        else:
            form.dimension_font_family.setCurrentIndex(
                form.dimension_font_family.findText(self.dimension_font_family)
            )
        form.dimension_font_size.setValue(self.dimension_font_size)
        color = QtGui.QColor()
        color.setRgbF(
            self.dimension_text_color[0],
            self.dimension_text_color[1],
            self.dimension_text_color[2],
        )
        form.dimension_text_color.setProperty("color", color)
        form.dimension_stroke_width.setText(
            FreeCAD.Units.Quantity(
                self.dimension_stroke_width, FreeCAD.Units.Length
            ).UserString
        )
        if form.dimension_line_style.findText(self.dimension_line_style) == -1:
            form.dimension_line_style.setCurrentIndex(0)
        else:
            form.dimension_line_style.setCurrentIndex(
                form.dimension_line_style.findText(self.dimension_line_style)
            )
        color = QtGui.QColor()
        color.setRgbF(
            self.dimension_line_color[0],
            self.dimension_line_color[1],
            self.dimension_line_color[2],
        )
        form.dimension_line_color.setProperty("color", color)
        if (
            form.dimension_line_mid_point_symbol.findText(
                self.dimension_line_mid_point_symbol
            )
            == -1
        ):
            form.dimension_line_mid_point_symbol.setCurrentIndex(0)
        else:
            form.dimension_line_mid_point_symbol.setCurrentIndex(
                form.dimension_line_mid_point_symbol.findText(
                    self.dimension_line_mid_point_symbol
                )
            )

    def setDefaultSingleMultiRebarsData(self):
        """This function is used to set default values in "Dimensions - Single &
        Multi Rebars" stacked widget in UI."""
        form = self.dimension_single_multi_rebars_widget
        if (
            form.single_rebar_dimension_line_start_symbol.findText(
                self.dimension_single_rebar_line_start_symbol
            )
            == -1
        ):
            form.single_rebar_dimension_line_start_symbol.setCurrentIndex(0)
        else:
            form.single_rebar_dimension_line_start_symbol.setCurrentIndex(
                form.single_rebar_dimension_line_start_symbol.findText(
                    self.dimension_single_rebar_line_start_symbol
                )
            )
        if (
            form.single_rebar_dimension_line_end_symbol.findText(
                self.dimension_single_rebar_line_end_symbol
            )
            == -1
        ):
            form.single_rebar_dimension_line_end_symbol.setCurrentIndex(0)
        else:
            form.single_rebar_dimension_line_end_symbol.setCurrentIndex(
                form.single_rebar_dimension_line_end_symbol.findText(
                    self.dimension_single_rebar_line_end_symbol
                )
            )
        if (
            form.single_rebar_text_position_type.findText(
                self.dimension_single_rebar_text_position_type
            )
            == -1
        ):
            form.single_rebar_text_position_type.setCurrentIndex(0)
        else:
            form.single_rebar_text_position_type.setCurrentIndex(
                form.single_rebar_text_position_type.findText(
                    self.dimension_single_rebar_text_position_type
                )
            )
        form.single_rebar_outer_dimension.setChecked(
            self.dimension_single_rebar_outer_dim
        )
        if (
            form.multi_rebar_dimension_line_start_symbol.findText(
                self.dimension_multi_rebar_line_start_symbol
            )
            == -1
        ):
            form.multi_rebar_dimension_line_start_symbol.setCurrentIndex(0)
        else:
            form.multi_rebar_dimension_line_start_symbol.setCurrentIndex(
                form.multi_rebar_dimension_line_start_symbol.findText(
                    self.dimension_multi_rebar_line_start_symbol
                )
            )
        if (
            form.multi_rebar_dimension_line_end_symbol.findText(
                self.dimension_multi_rebar_line_end_symbol
            )
            == -1
        ):
            form.multi_rebar_dimension_line_end_symbol.setCurrentIndex(0)
        else:
            form.multi_rebar_dimension_line_end_symbol.setCurrentIndex(
                form.multi_rebar_dimension_line_end_symbol.findText(
                    self.dimension_multi_rebar_line_end_symbol
                )
            )
        if (
            form.multi_rebar_text_position_type.findText(
                self.dimension_multi_rebar_text_position_type
            )
            == -1
        ):
            form.multi_rebar_text_position_type.setCurrentIndex(0)
        else:
            form.multi_rebar_text_position_type.setCurrentIndex(
                form.multi_rebar_text_position_type.findText(
                    self.dimension_multi_rebar_text_position_type
                )
            )
        form.multi_rebar_outer_dimension.setChecked(
            self.dimension_multi_rebar_outer_dim
        )

    def setDefaultOffsetsIncrementsData(self):
        """This function is used to set default values in "Dimensions - Offsets
        & Increments" stacked widget in UI."""
        form = self.dimension_offsets_increments_widget
        form.dimension_left_offset.setText(f"{self.dimension_left_offset} mm")
        form.dimension_right_offset.setText(f"{self.dimension_right_offset} mm")
        form.dimension_top_offset.setText(f"{self.dimension_top_offset} mm")
        form.dimension_bottom_offset.setText(
            f"{self.dimension_bottom_offset} mm"
        )
        form.dimension_left_offset_increment.setText(
            f"{self.dimension_left_offset_increment} mm"
        )
        form.dimension_right_offset_increment.setText(
            f"{self.dimension_right_offset_increment} mm"
        )
        form.dimension_top_offset_increment.setText(
            f"{self.dimension_top_offset_increment} mm"
        )
        form.dimension_bottom_offset_increment.setText(
            f"{self.dimension_bottom_offset_increment} mm"
        )

    def connectSignalSlots(self):
        """This function is used to connect different slots in UI to appropriate
        functions."""
        self.form.reinforcement_drawing_list_widget.currentRowChanged.connect(
            self.changeRebarsListWidget
        )
        self.drawing_widget.choose_template_file.clicked.connect(
            self.chooseTemplateFileClicked
        )
        self.form.next_button.clicked.connect(self.nextButtonClicked)
        self.form.back_button.clicked.connect(self.backButtonClicked)
        self.form.standard_button_box.clicked.connect(self.clicked)

    def changeRebarsListWidget(self, index):
        max_index = self.form.reinforcement_drawing_list_widget.count() - 1
        if index == max_index:
            self.form.next_button.setText("Finish")
        else:
            self.form.next_button.setText("Next")
        self.form.reinforcement_drawing_stacked_widget.setCurrentIndex(index)

    def chooseTemplateFileClicked(self):
        """This function is executed when Choose Template button is clicked
        in ui to execute QFileDialog to select template file."""
        path = FreeCAD.ConfigGet("UserAppData")
        template_file, _filter = QtGui.QFileDialog.getOpenFileName(
            None, "Choose template for Drawing", path, "*.svg"
        )
        if template_file:
            self.drawing_widget.template_file.setText(str(template_file))

    def nextButtonClicked(self):
        """This function is executed when 'Next' button is clicked from UI."""
        if self.form.next_button.text() == "Finish":
            self.accept()
        else:
            index = self.form.reinforcement_drawing_list_widget.currentRow()
            index += 1
            max_index = self.form.reinforcement_drawing_list_widget.count() - 1
            if index <= max_index:
                self.form.reinforcement_drawing_list_widget.setCurrentRow(index)

    def backButtonClicked(self):
        """This function is executed when 'Back' button is clicked from UI."""
        index = self.form.reinforcement_drawing_list_widget.currentRow()
        index -= 1
        if index >= 0:
            self.form.reinforcement_drawing_list_widget.setCurrentRow(index)

    def clicked(self, button):
        """This function is executed when 'Apply' button is clicked from UI."""
        if (
            self.form.standard_button_box.buttonRole(button)
            == QtGui.QDialogButtonBox.AcceptRole
        ):
            self.accept()
        elif (
            self.form.standard_button_box.buttonRole(button)
            == QtGui.QDialogButtonBox.ResetRole
        ):
            self.setDefaultValues()
        elif (
            self.form.standard_button_box.buttonRole(button)
            == QtGui.QDialogButtonBox.RejectRole
        ):
            self.form.close()

    def accept(self):
        """This function is executed when 'OK' button is clicked from UI. It
        execute a function to reinforcement drawing and dimensioning."""
        # Check if template file is selected or not
        template_file = self.drawing_widget.template_file.text()
        if not template_file:
            self.drawing_widget.template_file.setStyleSheet(
                "border: 1px solid red;"
            )
            showWarning(
                'Choose template for drawing under: "Drawing - Views & Options"'
            )
            return
        # Get drawing data
        form = self.shapes_data_widget
        rebars_stroke_width = FreeCAD.Units.Quantity(
            form.rebars_stroke_width.text()
        ).Value
        if form.rebars_shape_color_radio.isChecked():
            rebars_color_style = "Automatic"
        else:
            rebars_color_style = "Custom"
        rebars_color = form.rebars_color.property("color").getRgbF()
        structure_stroke_width = FreeCAD.Units.Quantity(
            form.structure_stroke_width.text()
        ).Value
        if form.structure_shape_color_radio.isChecked():
            structure_color_style = "Automatic"
        elif form.structure_custom_color_radio.isChecked():
            structure_color_style = "Custom"
        else:
            structure_color_style = "None"
        structure_color = form.structure_color.property("color").getRgbF()
        form = self.drawing_widget
        views = []
        if form.front_view_check_box.isChecked():
            views.append("Front")
        if form.rear_view_check_box.isChecked():
            views.append("Rear")
        if form.left_view_check_box.isChecked():
            views.append("Left")
        if form.right_view_check_box.isChecked():
            views.append("Right")
        if form.top_view_check_box.isChecked():
            views.append("Top")
        if form.bottom_view_check_box.isChecked():
            views.append("Bottom")
        drawing_left_offset = FreeCAD.Units.Quantity(
            form.drawing_left_offset.text()
        ).Value
        drawing_top_offset = FreeCAD.Units.Quantity(
            form.drawing_top_offset.text()
        ).Value
        drawing_min_right_offset = FreeCAD.Units.Quantity(
            form.drawing_min_right_offset.text()
        ).Value
        drawing_min_bottom_offset = FreeCAD.Units.Quantity(
            form.drawing_min_bottom_offset.text()
        ).Value
        drawing_max_width = FreeCAD.Units.Quantity(
            form.drawing_max_width.text()
        ).Value
        drawing_max_height = FreeCAD.Units.Quantity(
            form.drawing_max_height.text()
        ).Value

        # Get dimensioning data
        form = self.dimension_labels_lines_widget
        perform_dimensioning = (
            self.drawing_widget.perform_dimensioning_radio_button.isChecked()
        )
        dimension_label_format = form.dimension_label_format.text()
        dimension_font_family = form.dimension_font_family.currentText()
        dimension_font_size = form.dimension_font_size.value()
        dimension_text_color = form.dimension_text_color.property(
            "color"
        ).getRgbF()
        dimension_stroke_width = FreeCAD.Units.Quantity(
            form.dimension_stroke_width.text()
        ).Value
        dimension_line_style = form.dimension_line_style.currentText()
        dimension_line_color = form.dimension_line_color.property(
            "color"
        ).getRgbF()
        dimension_line_mid_point_symbol = (
            form.dimension_line_mid_point_symbol.currentText()
        )
        form = self.dimension_single_multi_rebars_widget
        dimension_single_rebar_line_start_symbol = (
            form.single_rebar_dimension_line_start_symbol.currentText()
        )
        dimension_single_rebar_line_end_symbol = (
            form.single_rebar_dimension_line_end_symbol.currentText()
        )
        dimension_single_rebar_text_position_type = (
            form.single_rebar_text_position_type.currentText()
        )
        dimension_single_rebar_outer_dim = (
            form.single_rebar_outer_dimension.isChecked()
        )
        dimension_multi_rebar_line_start_symbol = (
            form.multi_rebar_dimension_line_start_symbol.currentText()
        )
        dimension_multi_rebar_line_end_symbol = (
            form.multi_rebar_dimension_line_end_symbol.currentText()
        )
        dimension_multi_rebar_text_position_type = (
            form.multi_rebar_text_position_type.currentText()
        )
        dimension_multi_rebar_outer_dim = (
            form.multi_rebar_outer_dimension.isChecked()
        )
        form = self.dimension_offsets_increments_widget
        dimension_left_offset = FreeCAD.Units.Quantity(
            form.dimension_left_offset.text()
        ).Value
        dimension_right_offset = FreeCAD.Units.Quantity(
            form.dimension_right_offset.text()
        ).Value
        dimension_top_offset = FreeCAD.Units.Quantity(
            form.dimension_top_offset.text()
        ).Value
        dimension_bottom_offset = FreeCAD.Units.Quantity(
            form.dimension_bottom_offset.text()
        ).Value
        dimension_left_offset_increment = FreeCAD.Units.Quantity(
            form.dimension_left_offset_increment.text()
        ).Value
        dimension_right_offset_increment = FreeCAD.Units.Quantity(
            form.dimension_right_offset_increment.text()
        ).Value
        dimension_top_offset_increment = FreeCAD.Units.Quantity(
            form.dimension_top_offset_increment.text()
        ).Value
        dimension_bottom_offset_increment = FreeCAD.Units.Quantity(
            form.dimension_bottom_offset_increment.text()
        ).Value

        # Get selected objects list
        selected_objects = [
            selection.Object
            for selection in FreeCADGui.Selection.getSelectionEx()
        ]
        reinforcement_objs = getReinforcementRebarObjects(selected_objects)
        if not reinforcement_objs:
            reinforcement_objs = getReinforcementRebarObjects(
                FreeCAD.ActiveDocument.Objects
            )

        def getFreeCADObjectsList(
            objects: list,
            # ) -> Union[Literal["None"], str]:
        ) -> str:
            return (
                "None"
                if not objects
                else "["
                + ",".join(
                    ["FreeCAD.ActiveDocument." + obj.Name for obj in objects]
                )
                + "]"
            )

        rebars_list = getFreeCADObjectsList(reinforcement_objs)
        FreeCADGui.addModule("ReinforcementDrawing.make_reinforcement_drawing")
        for view in views:
            FreeCADGui.doCommand(
                "ReinforcementDrawing.make_reinforcement_drawing."
                "makeStructuresReinforcementDrawing(structure_list=None, "
                f"rebars_list={rebars_list}, "
                f'view="{view}", '
                f"rebars_stroke_width={rebars_stroke_width}, "
                f'rebars_color_style="{rebars_color_style}", '
                f"rebars_color={rebars_color}, "
                f"structure_stroke_width={structure_stroke_width}, "
                f'structure_color_style="{structure_color_style}", '
                f"structure_color={structure_color}, "
                f"drawing_left_offset={drawing_left_offset}, "
                f"drawing_top_offset={drawing_top_offset}, "
                f"drawing_min_right_offset={drawing_min_right_offset}, "
                f"drawing_min_bottom_offset={drawing_min_bottom_offset}, "
                f"drawing_max_width={drawing_max_width}, "
                f"drawing_max_height={drawing_max_height}, "
                f'template_file=r"{template_file}", '
                f"perform_dimensioning={perform_dimensioning}, "
                "dimension_rebars_filter_list=None, "
                f'dimension_label_format="{dimension_label_format}",  '
                f'dimension_font_family="{dimension_font_family}", '
                f"dimension_font_size={dimension_font_size}, "
                f"dimension_stroke_width={dimension_stroke_width}, "
                f'dimension_line_style="{dimension_line_style}",'
                f" dimension_line_color={dimension_line_color}, "
                f"dimension_text_color={dimension_text_color}, "
                'dimension_single_rebar_line_start_symbol="'
                f'{dimension_single_rebar_line_start_symbol}", '
                'dimension_single_rebar_line_end_symbol="'
                f'{dimension_single_rebar_line_end_symbol}", '
                'dimension_multi_rebar_line_start_symbol="'
                f'{dimension_multi_rebar_line_start_symbol}", '
                'dimension_multi_rebar_line_end_symbol="'
                f'{dimension_multi_rebar_line_end_symbol}", '
                'dimension_line_mid_point_symbol="'
                f'{dimension_line_mid_point_symbol}", '
                f"dimension_left_offset={dimension_left_offset}, "
                f"dimension_right_offset={dimension_right_offset}, "
                f"dimension_top_offset={dimension_top_offset}, "
                f"dimension_bottom_offset={dimension_bottom_offset}, "
                "dimension_left_offset_increment="
                f"{dimension_left_offset_increment}, "
                "dimension_right_offset_increment="
                f"{dimension_right_offset_increment}, "
                "dimension_top_offset_increment="
                f"{dimension_top_offset_increment}, "
                "dimension_bottom_offset_increment="
                f"{dimension_bottom_offset_increment}, "
                "dimension_single_rebar_outer_dim="
                f"{dimension_single_rebar_outer_dim}, "
                "dimension_multi_rebar_outer_dim="
                f"{dimension_multi_rebar_outer_dim}, "
                "dimension_single_rebar_text_position_type="
                f'"{dimension_single_rebar_text_position_type}", '
                "dimension_multi_rebar_text_position_type="
                f'"{dimension_multi_rebar_text_position_type}")'
            )
        self.form.close()


def CommandReinforcementDrawingDimensioning(
    view="Front",
    rebars_stroke_width=REBARS_STROKE_WIDTH,
    rebars_color_style=REBARS_COLOR_STYLE,
    rebars_color=REBARS_COLOR,
    structure_stroke_width=STRUCTURE_STROKE_WIDTH,
    structure_color_style=STRUCTURE_COLOR_STYLE,
    structure_color=STRUCTURE_COLOR,
    drawing_left_offset=DRAWING_LEFT_OFFSET,
    drawing_top_offset=DRAWING_TOP_OFFSET,
    drawing_min_right_offset=DRAWING_MIN_RIGHT_OFFSET,
    drawing_min_bottom_offset=DRAWING_MIN_BOTTOM_OFFSET,
    drawing_max_width=DRAWING_MAX_WIDTH,
    drawing_max_height=DRAWING_MAX_HEIGHT,
    template_file=TEMPLATE_FILE,
    perform_dimensioning=True,
    dimension_rebars_filter_list=None,
    dimension_label_format=DIMENSION_LABEL_FORMAT,
    dimension_font_family=DIMENSION_FONT_FAMILY,
    dimension_font_size=DIMENSION_FONT_SIZE,
    dimension_stroke_width=DIMENSION_STROKE_WIDTH,
    dimension_line_style=DIMENSION_LINE_STYLE,
    dimension_line_color=DIMENSION_LINE_COLOR,
    dimension_text_color=DIMENSION_TEXT_COLOR,
    dimension_single_rebar_line_start_symbol=(
        DIMENSION_SINGLE_REBAR_LINE_START_SYMBOL
    ),
    dimension_single_rebar_line_end_symbol=(
        DIMENSION_SINGLE_REBAR_LINE_END_SYMBOL
    ),
    dimension_multi_rebar_line_start_symbol=(
        DIMENSION_MULTI_REBAR_LINE_START_SYMBOL
    ),
    dimension_multi_rebar_line_end_symbol=(
        DIMENSION_MULTI_REBAR_LINE_END_SYMBOL
    ),
    dimension_line_mid_point_symbol=DIMENSION_LINE_MID_POINT_SYMBOL,
    dimension_left_offset=DIMENSION_LEFT_OFFSET,
    dimension_right_offset=DIMENSION_RIGHT_OFFSET,
    dimension_top_offset=DIMENSION_TOP_OFFSET,
    dimension_bottom_offset=DIMENSION_BOTTOM_OFFSET,
    dimension_left_offset_increment=DIMENSION_LEFT_OFFSET_INCREMENT,
    dimension_right_offset_increment=DIMENSION_RIGHT_OFFSET_INCREMENT,
    dimension_top_offset_increment=DIMENSION_TOP_OFFSET_INCREMENT,
    dimension_bottom_offset_increment=DIMENSION_BOTTOM_OFFSET_INCREMENT,
    dimension_single_rebar_outer_dim=DIMENSION_SINGLE_REBAR_OUTER_DIM,
    dimension_multi_rebar_outer_dim=DIMENSION_MULTI_REBAR_OUTER_DIM,
    dimension_single_rebar_text_position_type=(
        DIMENSION_SINGLE_REBAR_TEXT_POSITION_TYPE
    ),
    dimension_multi_rebar_text_position_type=(
        DIMENSION_MULTI_REBAR_TEXT_POSITION_TYPE
    ),
):
    dialog = _ReinforcementDrawingDimensioningDialog(
        [view],
        rebars_stroke_width,
        rebars_color_style,
        rebars_color,
        structure_stroke_width,
        structure_color_style,
        structure_color,
        drawing_left_offset,
        drawing_top_offset,
        drawing_min_right_offset,
        drawing_min_bottom_offset,
        drawing_max_width,
        drawing_max_height,
        template_file,
        perform_dimensioning,
        dimension_rebars_filter_list,
        dimension_label_format,
        dimension_font_family,
        dimension_font_size,
        dimension_stroke_width,
        dimension_line_style,
        dimension_line_color,
        dimension_text_color,
        dimension_single_rebar_line_start_symbol,
        dimension_single_rebar_line_end_symbol,
        dimension_multi_rebar_line_start_symbol,
        dimension_multi_rebar_line_end_symbol,
        dimension_line_mid_point_symbol,
        dimension_left_offset,
        dimension_right_offset,
        dimension_top_offset,
        dimension_bottom_offset,
        dimension_left_offset_increment,
        dimension_right_offset_increment,
        dimension_top_offset_increment,
        dimension_bottom_offset_increment,
        dimension_single_rebar_outer_dim,
        dimension_multi_rebar_outer_dim,
        dimension_single_rebar_text_position_type,
        dimension_multi_rebar_text_position_type,
    )
    dialog.setupUi()
    dialog.form.exec_()
