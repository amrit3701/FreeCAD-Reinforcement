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

__title__ = "Bar Bending Schedule Gui"
__author__ = "Suraj"
__url__ = "https://www.freecadweb.org"


import os
from typing import Optional, Dict, Tuple, Literal

import Draft
import FreeCAD
import FreeCADGui
import importSVG
from PySide2 import QtGui, QtWidgets

from BillOfMaterial.BOMPreferences import BOMPreferences
from BillOfMaterial.BOMfunc import getReinforcementRebarObjects
from BillOfMaterial.UnitLineEdit import UnitLineEdit
from .BBSfunc import getBarBendingSchedule


class _BarBendingScheduleDialog:
    """This is a class for Bar Bending Schedule dialog box."""

    def __init__(
        self,
        column_headers: Optional[Dict[str, Tuple[str, int]]],
        column_units: Optional[Dict[str, str]],
        rebar_length_type: Optional[
            Literal["RealLength", "LengthWithSharpEdges"]
        ],
        reinforcement_group_by: Optional[Literal["Mark", "Host"]],
        font_family: Optional[str],
        font_size: float,
        column_width: float,
        row_height: float,
        rebar_shape_column_header: str,
        rebar_shape_stirrup_extended_edge_offset: float,
        rebar_shape_color_style: str,
        rebar_shape_stroke_width: float,
        rebar_shape_include_dimensions: bool,
        rebar_shape_dimension_font_size: float,
        rebar_shape_edge_dimension_units: str,
        rebar_shape_edge_dimension_precision: int,
        include_edge_dimension_units_in_dimension_label: bool,
        rebar_shape_bent_angle_dimension_exclude_list: Tuple[float, ...],
        helical_rebar_dimension_label_format: str,
    ):
        """This function set initial data in Bar Bending Schedule dialog box."""
        self.column_headers_data = column_headers
        self.column_units = column_units
        self.rebar_length_type = rebar_length_type
        self.allowed_rebar_length_types = ["RealLength", "LengthWithSharpEdges"]
        self.reinforcement_group_by = reinforcement_group_by
        self.allowed_reinforcement_group_by = ["Mark", "Host"]
        self.font_family = font_family
        self.font_size = font_size
        self.column_width = column_width
        self.row_height = row_height
        self.rebar_shape_column_header = rebar_shape_column_header
        self.rebar_shape_stirrup_extended_edge_offset = (
            rebar_shape_stirrup_extended_edge_offset
        )
        self.rebar_shape_color_style = rebar_shape_color_style
        self.rebar_shape_stroke_width = rebar_shape_stroke_width
        self.rebar_shape_include_dimensions = rebar_shape_include_dimensions
        self.rebar_shape_dimension_font_size = rebar_shape_dimension_font_size
        self.rebar_shape_edge_dimension_units = rebar_shape_edge_dimension_units
        self.rebar_shape_edge_dimension_precision = (
            rebar_shape_edge_dimension_precision
        )
        self.include_edge_dimension_units_in_dimension_label = (
            include_edge_dimension_units_in_dimension_label
        )
        self.rebar_shape_bent_angle_dimension_exclude_list = (
            rebar_shape_bent_angle_dimension_exclude_list
        )
        self.helical_rebar_dimension_label_format = (
            helical_rebar_dimension_label_format
        )
        self.form = FreeCADGui.PySideUic.loadUi(
            os.path.splitext(__file__)[0] + ".ui"
        )
        self.form.setWindowTitle(
            QtWidgets.QApplication.translate(
                "ReinforcementWorkbench", "Bar Bending Schedule", None
            )
        )

    def setupUi(self):
        """This function is used to add components to ui."""
        self.addUnitsInputFields()
        self.addColumnHeaders()
        self.addDropdownMenuItems()

        # Set rebar length type in ui
        self.form.rebarLengthType.setCurrentIndex(
            self.form.rebarLengthType.findText(self.rebar_length_type)
        )
        # Set reinforcement group by in ui
        self.form.reinforcementGroupBy.setCurrentIndex(
            self.form.reinforcementGroupBy.findText(self.reinforcement_group_by)
        )

        # Set initial data
        if self.form.fontFamily.findText(self.font_family) == -1:
            self.form.fontFamily.setCurrentIndex(0)
        else:
            self.form.fontFamily.setCurrentIndex(
                self.form.fontFamily.findText(self.font_family)
            )
        self.form.fontSize.setValue(self.font_size)
        self.form.columnWidth.setText(str(self.column_width))
        self.form.rowHeight.setText(str(self.row_height))

        self.form.rebarShapeColumnHeader.setText(self.rebar_shape_column_header)
        self.form.stirrupExtendedEdgeOffset.setText(
            str(self.rebar_shape_stirrup_extended_edge_offset)
        )
        self.form.rebarsStrokeWidth.setText(str(self.rebar_shape_stroke_width))
        if self.rebar_shape_color_style == "shape color":
            self.form.shapeColorRadio.setChecked(True)
            self.form.customColorRadio.setChecked(False)
            self.form.rebarsColor.setEnabled(False)
        else:
            self.form.shapeColorRadio.setChecked(False)
            self.form.customColorRadio.setChecked(True)
            self.form.rebarsColor.setEnabled(True)
            color_rgba = importSVG.getcolor(self.rebar_shape_color_style)
            color = QtGui.QColor()
            color.setRgb(
                color_rgba[0], color_rgba[1], color_rgba[2], color_rgba[3]
            )
            self.form.rebarsColor.setProperty("color", color)
        self.form.includeDimensions.setChecked(
            self.rebar_shape_include_dimensions
        )
        self.form.includeUnitsInDimensionLabel.setChecked(
            self.include_edge_dimension_units_in_dimension_label
        )
        self.form.dimensionFontSize.setValue(
            self.rebar_shape_dimension_font_size
        )
        self.form.rebarEdgeDimensionPrecision.setValue(
            self.rebar_shape_edge_dimension_precision
        )
        self.form.bentAngleDimensionExcludeList.setText(
            ", ".join(
                map(str, self.rebar_shape_bent_angle_dimension_exclude_list)
            )
        )
        self.form.helicalRebarDimensionLabelFormat.setText(
            self.helical_rebar_dimension_label_format
        )

        # Connect signal and slots in ui
        self.connectSignalSlots()

    def addUnitsInputFields(self):
        """This function add input fields for units of data."""
        main_layout = self.form.verticalLayout
        column_units_layouts = []
        for column, unit in reversed(list(self.column_units.items())):
            column_name = QtWidgets.QLabel(column + " unit")
            column_name.setMinimumWidth(250)
            column_unit = UnitLineEdit(unit)
            h_layout = QtWidgets.QHBoxLayout()
            h_layout.addWidget(column_name)
            h_layout.addWidget(column_unit)
            main_layout.insertLayout(2, h_layout)
            column_units_layouts.insert(0, h_layout)
        self.column_units_layouts = column_units_layouts
        rebar_edge_dimension_layout = self.form.rebarEdgeDimensionUnitsHLayout
        self.rebar_edge_dimension_units_widget = UnitLineEdit(
            self.rebar_shape_edge_dimension_units
        )
        rebar_edge_dimension_layout.addWidget(
            self.rebar_edge_dimension_units_widget
        )

    def addColumnHeaders(self):
        """This function add column headers data as each row of items in list
        view."""
        column_header_list_widget = self.form.columnHeaderListWidget

        ui = FreeCADGui.UiLoader()
        sorted_column_header_data = dict(
            sorted(self.column_headers_data.items(), key=lambda x: x[1][1])
        )
        for (
            column_header,
            column_header_tuple,
        ) in sorted_column_header_data.items():
            row_widget = QtWidgets.QWidget()
            row_widget_item = QtWidgets.QListWidgetItem()

            show_hide_checkbox = ui.createWidget("Gui::PrefCheckBox")
            if column_header_tuple[1] != 0:
                show_hide_checkbox.setChecked(True)
            column_name = QtWidgets.QLabel(column_header)
            column_name.setMinimumWidth(220)
            spreadsheet_column_header = ui.createWidget("Gui::PrefLineEdit")
            spreadsheet_column_header.setText(column_header_tuple[0])

            h_layout = QtWidgets.QHBoxLayout()
            h_layout.addWidget(show_hide_checkbox)
            h_layout.addWidget(column_name)
            h_layout.addWidget(spreadsheet_column_header)

            row_widget.setLayout(h_layout)
            row_widget_item.setSizeHint(row_widget.sizeHint())

            column_header_list_widget.addItem(row_widget_item)
            column_header_list_widget.setItemWidget(row_widget_item, row_widget)

    def addDropdownMenuItems(self):
        """This function add dropdown items to each Gui::PrefComboBox."""
        self.form.rebarLengthType.addItems(self.allowed_rebar_length_types)
        self.form.reinforcementGroupBy.addItems(
            self.allowed_reinforcement_group_by
        )

    def connectSignalSlots(self):
        """This function is used to connect different slots in UI to appropriate
        functions."""
        self.form.chooseSVGOutputFile.clicked.connect(
            self.choose_svg_output_file_clicked
        )
        self.form.buttonBox.accepted.connect(self.accept)
        self.form.buttonBox.rejected.connect(lambda: self.form.close())

    def choose_svg_output_file_clicked(self):
        """This function is executed when Choose button clicked in ui to execute
        QFileDialog to select svg output file."""
        path = FreeCAD.ConfigGet("UserAppData")
        output_file, Filter = QtWidgets.QFileDialog.getSaveFileName(
            None, "Choose output file for Bar Bending Schedule", path, "*.svg"
        )
        if output_file:
            self.form.svgOutputFile.setText(
                os.path.splitext(str(output_file))[0] + ".svg"
            )

    def accept(self):
        """This function is executed when 'OK' button is clicked from UI. It
        execute a function to generate bar bending schedule."""
        # Validate entered units
        units_valid_flag = True
        for unit_h_layout in self.column_units_layouts:
            unit_field = unit_h_layout.itemAt(1).widget()
            if not unit_field.isValidUnit():
                unit_text = unit_field.text()
                unit_field.setText(
                    unit_text
                    + (
                        " (Invalid Unit)"
                        if " (Invalid Unit)" not in unit_text
                        else ""
                    )
                )
                units_valid_flag = False
        if not self.rebar_edge_dimension_units_widget.isValidUnit():
            unit_text = self.rebar_edge_dimension_units_widget.text()
            self.rebar_edge_dimension_units_widget.setText(
                unit_text
                + (
                    " (Invalid Unit)"
                    if " (Invalid Unit)" not in unit_text
                    else ""
                )
            )
            units_valid_flag = False
        if not units_valid_flag:
            return

        # Check if output file is selected or not
        output_file = self.form.svgOutputFile.text()
        if not output_file:
            self.form.svgOutputFile.setStyleSheet("border: 1px solid red;")
            return

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

        rebar_length_type = self.form.rebarLengthType.currentText()
        reinforcement_group_by = self.form.reinforcementGroupBy.currentText()
        column_units = self.getColumnUnits()
        column_headers = self.getColumnConfigData()
        font_family = self.form.fontFamily.currentText()
        font_size = self.form.fontSize.value()
        column_width = FreeCAD.Units.Quantity(
            self.form.columnWidth.text()
        ).Value
        row_height = FreeCAD.Units.Quantity(self.form.rowHeight.text()).Value
        rebar_shape_column_header = self.form.rebarShapeColumnHeader.text()
        stirrup_extended_edge_offset = FreeCAD.Units.Quantity(
            self.form.stirrupExtendedEdgeOffset.text()
        ).Value
        rebars_stroke_width = FreeCAD.Units.Quantity(
            self.form.rebarsStrokeWidth.text()
        ).Value
        if self.form.shapeColorRadio.isChecked():
            rebars_color_style = "shape color"
        else:
            color_rgb_tuple = self.form.rebarsColor.property("color").getRgb()
            rebars_color_style = Draft.getrgb(
                [
                    color_rgb_tuple[0] / 255,
                    color_rgb_tuple[1] / 255,
                    color_rgb_tuple[2] / 255,
                    color_rgb_tuple[3] / 255,
                ]
            )
        include_dimensions = self.form.includeDimensions.isChecked()
        include_units_in_dimension_label = (
            self.form.includeUnitsInDimensionLabel.isChecked()
        )
        rebar_shape_dimension_font_size = self.form.dimensionFontSize.value()
        rebar_edge_dimension_units = FreeCAD.Units.Quantity(
            self.rebar_edge_dimension_units_widget.text()
        ).Value
        rebar_edge_dimension_precision = (
            self.form.rebarEdgeDimensionPrecision.value()
        )
        bent_angle_dimension_exclude_list_str = (
            self.form.bentAngleDimensionExcludeList.text()
        )
        bent_angle_dimension_exclude_list = []
        for angle in bent_angle_dimension_exclude_list_str.split(","):
            try:
                bent_angle_dimension_exclude_list.append(float(angle.strip()))
            except ValueError:
                pass
        helical_rebar_dimension_label_format = (
            self.form.helicalRebarDimensionLabelFormat.text()
        )

        output_file = self.form.svgOutputFile.text()
        getBarBendingSchedule(
            reinforcement_objs,
            column_headers=column_headers,
            column_units=column_units,
            rebar_length_type=rebar_length_type,
            reinforcement_group_by=reinforcement_group_by,
            font_family=font_family,
            font_size=font_size,
            column_width=column_width,
            row_height=row_height,
            rebar_shape_column_header=rebar_shape_column_header,
            rebar_shape_stirrup_extended_edge_offset=(
                stirrup_extended_edge_offset
            ),
            rebar_shape_color_style=rebars_color_style,
            rebar_shape_stroke_width=rebars_stroke_width,
            rebar_shape_include_dimensions=include_dimensions,
            rebar_shape_dimension_font_size=rebar_shape_dimension_font_size,
            rebar_shape_edge_dimension_units=rebar_edge_dimension_units,
            rebar_shape_edge_dimension_precision=rebar_edge_dimension_precision,
            include_edge_dimension_units_in_dimension_label=(
                include_units_in_dimension_label
            ),
            rebar_shape_bent_angle_dimension_exclude_list=(
                bent_angle_dimension_exclude_list
            ),
            helical_rebar_dimension_label_format=(
                helical_rebar_dimension_label_format
            ),
            output_file=output_file,
        )

        self.form.close()

    def getColumnUnits(self):
        """This function get units data from UI and return a dictionary with
        column name as key and its corresponding unit as value."""
        column_units = {}
        for unit_h_layout in self.column_units_layouts:
            column_name = (
                unit_h_layout.itemAt(0).widget().text().split(" unit")[0]
            )
            units = unit_h_layout.itemAt(1).widget().text()
            column_units[column_name] = units
        return column_units

    def getColumnConfigData(self):
        """This function get data from UI and return a dictionary with column
        data as key and values are tuple of column_header and sequence number.
        e.g. {
                "Host": ("Member", 1),
                "Mark": ("Mark", 2),
                ...,
            }
        """
        column_header_list_widget = self.form.columnHeaderListWidget
        column_headers_config = {}
        current_column = 1
        for index in range(column_header_list_widget.count()):
            row_widget_item = column_header_list_widget.item(index)
            row_widget = column_header_list_widget.itemWidget(row_widget_item)
            h_layout = row_widget.layout()
            show_hide_checkbox = h_layout.itemAt(0).widget()
            if not show_hide_checkbox.isChecked():
                sequence = 0
            else:
                sequence = current_column
                current_column += 1
            column_name = h_layout.itemAt(1).widget().text()
            spreadsheet_column_header = h_layout.itemAt(2).widget().text()
            column_headers_config[column_name] = (
                spreadsheet_column_header,
                sequence,
            )
        return column_headers_config


def CommandBarBendingSchedule(
    column_headers: Optional[Dict[str, Tuple[str, int]]] = None,
    column_units: Optional[Dict[str, str]] = None,
    rebar_length_type: Optional[
        Literal["RealLength", "LengthWithSharpEdges"]
    ] = None,
    reinforcement_group_by: Optional[Literal["Mark", "Host"]] = None,
    font_family: Optional[str] = None,
    font_size: float = 5,
    column_width: float = 60,
    row_height: float = 30,
    rebar_shape_column_header: str = "Rebar Shape (mm)",
    rebar_shape_stirrup_extended_edge_offset: float = 2,
    rebar_shape_color_style: str = "shape color",
    rebar_shape_stroke_width: float = 0.35,
    rebar_shape_include_dimensions: bool = True,
    rebar_shape_dimension_font_size: float = 3,
    rebar_shape_edge_dimension_units: str = "mm",
    rebar_shape_edge_dimension_precision: int = 0,
    include_edge_dimension_units_in_dimension_label: bool = False,
    rebar_shape_bent_angle_dimension_exclude_list: Tuple[float, ...] = (
        45,
        90,
        180,
    ),
    helical_rebar_dimension_label_format: str = "%L,r=%R,pitch=%P",
):
    """This function is used to invoke dialog box for bar bending schedule."""
    bom_preferences = BOMPreferences()
    if not column_headers:
        column_headers = bom_preferences.getColumnHeaders()
    if not column_units:
        column_units = bom_preferences.getColumnUnits()
    if not rebar_length_type:
        rebar_length_type = bom_preferences.getRebarLengthType()
    if not reinforcement_group_by:
        reinforcement_group_by = bom_preferences.getReinforcementGroupBy()

    svg_pref = bom_preferences.getSVGPrefGroup()
    if not font_family:
        font_family = svg_pref.GetString("FontFamily")
    if not font_size:
        font_size = svg_pref.GetFloat("FontSize")
    if not column_width:
        column_width = svg_pref.GetFloat("ColumnWidth")
    if not row_height:
        row_height = svg_pref.GetFloat("RowHeight")

    dialog = _BarBendingScheduleDialog(
        column_headers,
        column_units,
        rebar_length_type,
        reinforcement_group_by,
        font_family,
        font_size,
        column_width,
        row_height,
        rebar_shape_column_header,
        rebar_shape_stirrup_extended_edge_offset,
        rebar_shape_color_style,
        rebar_shape_stroke_width,
        rebar_shape_include_dimensions,
        rebar_shape_dimension_font_size,
        rebar_shape_edge_dimension_units,
        rebar_shape_edge_dimension_precision,
        include_edge_dimension_units_in_dimension_label,
        rebar_shape_bent_angle_dimension_exclude_list,
        helical_rebar_dimension_label_format,
    )
    dialog.setupUi()
    dialog.form.exec_()
