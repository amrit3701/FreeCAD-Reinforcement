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

__title__ = "Bill Of Material Gui"
__author__ = "Suraj"
__url__ = "https://www.freecadweb.org"

from collections import OrderedDict
from pathlib import Path
from typing import OrderedDict as OrderedDictType, Literal

import FreeCAD
import FreeCADGui
from PySide2 import QtWidgets

from .BOMPreferences import BOMPreferences
from .BOMfunc import getReinforcementRebarObjects
from .BillOfMaterial_SVG import makeBillOfMaterialSVG
from .BillOfMaterial_Spreadsheet import makeBillOfMaterial
from .UnitLineEdit import UnitLineEdit
from .config import COLUMN_HEADERS


class _BillOfMaterialDialog:
    """This is a class for Bill Of Material dialog box."""

    def __init__(
        self,
        column_headers,
        column_units,
        rebar_length_type,
        reinforcement_group_by,
        font_family,
        font_size,
        column_width,
        row_height,
        bom_left_offset,
        bom_top_offset,
        bom_min_right_offset,
        bom_min_bottom_offset,
        bom_table_svg_max_width,
        bom_table_svg_max_height,
        template_file,
    ):
        """This function set initial data in Bill of Material dialog box."""
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
        self.bom_left_offset = bom_left_offset
        self.bom_top_offset = bom_top_offset
        self.bom_min_right_offset = bom_min_right_offset
        self.bom_min_bottom_offset = bom_min_bottom_offset
        self.bom_table_svg_max_width = bom_table_svg_max_width
        self.bom_table_svg_max_height = bom_table_svg_max_height
        self.template_file = template_file
        self.form = FreeCADGui.PySideUic.loadUi(
            str(Path(__file__).with_suffix(".ui"))
        )
        self.form.setWindowTitle(
            QtWidgets.QApplication.translate(
                "RebarAddon", "Rebars Bill Of Material", None
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

        # Connect signal and slots in ui
        self.connectSignalSlots()

    def addUnitsInputFields(self):
        """This function add input fields for units of data."""
        main_layout = self.form.verticalLayout
        column_units_layouts = []
        for column, unit in reversed(list(self.column_units.items())):
            column_name = QtWidgets.QLabel(column + " unit")
            column_name.setMinimumWidth(200)
            column_unit = UnitLineEdit(unit)
            h_layout = QtWidgets.QHBoxLayout()
            h_layout.setSpacing(60)
            h_layout.addWidget(column_name)
            h_layout.addWidget(column_unit)
            main_layout.insertLayout(2, h_layout)
            column_units_layouts.insert(0, h_layout)
        self.column_units_layouts = column_units_layouts

    def addColumnHeaders(self):
        """This function add column headers data as each row of items in list
        view."""
        column_header_list_widget = self.form.columnHeaderListWidget

        ui = FreeCADGui.UiLoader()
        for (
            column_header,
            column_header_disp,
        ) in self.column_headers_data.items():
            row_widget = QtWidgets.QWidget()
            row_widget_item = QtWidgets.QListWidgetItem()

            show_hide_checkbox = ui.createWidget("Gui::PrefCheckBox")
            show_hide_checkbox.setChecked(True)
            column_name = QtWidgets.QLabel(column_header)
            column_name.setMinimumWidth(160)
            column_header_disp_widget = ui.createWidget("Gui::PrefLineEdit")
            column_header_disp_widget.setText(column_header_disp)

            h_layout = QtWidgets.QHBoxLayout()
            h_layout.addWidget(show_hide_checkbox)
            h_layout.addWidget(column_name)
            h_layout.addWidget(column_header_disp_widget)

            row_widget.setLayout(h_layout)
            row_widget_item.setSizeHint(row_widget.sizeHint())

            column_header_list_widget.addItem(row_widget_item)
            column_header_list_widget.setItemWidget(row_widget_item, row_widget)

        # Add hidden columns in UI
        for column_header, column_header_disp in COLUMN_HEADERS.items():
            if column_header not in self.column_headers_data:
                row_widget = QtWidgets.QWidget()
                row_widget_item = QtWidgets.QListWidgetItem()

                show_hide_checkbox = ui.createWidget("Gui::PrefCheckBox")
                show_hide_checkbox.setChecked(False)
                column_name = QtWidgets.QLabel(column_header)
                column_name.setMinimumWidth(160)
                column_header_disp_widget = ui.createWidget("Gui::PrefLineEdit")
                column_header_disp_widget.setText(column_header_disp)

                h_layout = QtWidgets.QHBoxLayout()
                h_layout.addWidget(show_hide_checkbox)
                h_layout.addWidget(column_name)
                h_layout.addWidget(column_header_disp_widget)

                row_widget.setLayout(h_layout)
                row_widget_item.setSizeHint(row_widget.sizeHint())

                column_header_list_widget.addItem(row_widget_item)
                column_header_list_widget.setItemWidget(
                    row_widget_item, row_widget
                )

    def addDropdownMenuItems(self):
        """This function add dropdown items to each Gui::PrefComboBox."""
        self.form.rebarLengthType.addItems(self.allowed_rebar_length_types)
        self.form.reinforcementGroupBy.addItems(
            self.allowed_reinforcement_group_by
        )

    def connectSignalSlots(self):
        """This function is used to connect different slots in UI to appropriate
        functions."""
        from .EditSVGConfiguration import runEditSVGConfigurationDialog

        self.form.editSVGConfigButton.clicked.connect(
            lambda: runEditSVGConfigurationDialog(self)
        )
        self.form.createSVG.stateChanged.connect(
            self.create_svg_checkbox_clicked
        )
        self.form.chooseSVGOutputFile.clicked.connect(
            self.choose_svg_output_file_clicked
        )
        self.form.buttonBox.accepted.connect(self.accept)
        self.form.buttonBox.rejected.connect(lambda: self.form.close())

    def create_svg_checkbox_clicked(self):
        """This function is executed when Create SVG button is checked/unchecked
        in ui."""
        if self.form.createSVG.isChecked():
            self.form.editSVGConfigButton.setEnabled(True)
            self.form.svgOutputFileWidget.setEnabled(True)
        else:
            self.form.editSVGConfigButton.setEnabled(False)
            self.form.svgOutputFileWidget.setEnabled(False)

    def choose_svg_output_file_clicked(self):
        """This function is executed when Choose button clicked in ui to execute
        QFileDialog to select svg output file."""
        path = FreeCAD.ConfigGet("UserAppData")
        output_file, file_filter = QtWidgets.QFileDialog.getSaveFileName(
            None, "Choose output file for Bill of Material", path, "*.svg"
        )
        if output_file:
            self.form.svgOutputFile.setText(
                str(Path(output_file).with_suffix(".svg"))
            )

    def accept(self):
        """This function is executed when 'OK' button is clicked from UI. It
        execute a function to generate rebars bill of material."""
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
        if not units_valid_flag:
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

        column_units = self.getColumnUnits()
        column_headers = self.getColumnConfigData()
        rebar_length_type = self.form.rebarLengthType.currentText()
        reinforcement_group_by = self.form.reinforcementGroupBy.currentText()
        create_spreadsheet = self.form.createSpreadsheet.isChecked()

        if create_spreadsheet:
            makeBillOfMaterial(
                column_headers=column_headers,
                column_units=column_units,
                rebar_length_type=rebar_length_type,
                rebar_objects=reinforcement_objs,
                reinforcement_group_by=reinforcement_group_by,
            )
        create_svg = self.form.createSVG.isChecked()

        if create_svg:
            output_file = self.form.svgOutputFile.text()
            makeBillOfMaterialSVG(
                column_headers=column_headers,
                column_units=column_units,
                rebar_length_type=rebar_length_type,
                font_family=self.font_family,
                font_size=self.font_size,
                column_width=self.column_width,
                row_height=self.row_height,
                bom_left_offset=self.bom_left_offset,
                bom_top_offset=self.bom_top_offset,
                bom_min_right_offset=self.bom_min_right_offset,
                bom_min_bottom_offset=self.bom_min_bottom_offset,
                bom_table_svg_max_width=self.bom_table_svg_max_width,
                bom_table_svg_max_height=self.bom_table_svg_max_height,
                template_file=self.template_file,
                output_file=output_file,
                rebar_objects=reinforcement_objs,
                reinforcement_group_by=reinforcement_group_by,
            )

        if self.form.savePreferences.isChecked():
            BOMPreferences(
                conf_column_units=column_units,
                conf_column_headers=column_headers,
                conf_rebar_length_type=rebar_length_type,
                conf_reinforcement_group_by=reinforcement_group_by,
                conf_column_width=self.column_width,
                conf_row_height=self.row_height,
                conf_font_family=self.font_family,
                conf_font_size=self.font_size,
                conf_bom_svg_left_offset=self.bom_left_offset,
                conf_bom_svg_top_offset=self.bom_top_offset,
                conf_bom_svg_min_right_offset=self.bom_min_right_offset,
                conf_bom_svg_min_bottom_offset=self.bom_min_bottom_offset,
                overwrite=True,
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

    def getColumnConfigData(
        self,
    ) -> OrderedDictType[
        Literal[
            "Host",
            "Mark",
            "RebarsCount",
            "Diameter",
            "RebarLength",
            "RebarsTotalLength",
        ],
        str,
    ]:
        """This function get data from UI and return an ordered dictionary with
        column data as key and column display header as value.
        e.g. {
                "Host": "Member",
                "Mark": "Mark",
                ...,
            }
        """
        column_header_list_widget = self.form.columnHeaderListWidget
        columns = []
        current_column = 1
        for index in range(column_header_list_widget.count()):
            row_widget_item = column_header_list_widget.item(index)
            row_widget = column_header_list_widget.itemWidget(row_widget_item)
            h_layout = row_widget.layout()
            show_hide_checkbox = h_layout.itemAt(0).widget()
            if show_hide_checkbox.isChecked():
                column_name = h_layout.itemAt(1).widget().text()
                disp_column_header = h_layout.itemAt(2).widget().text()
                columns.append(
                    (column_name, disp_column_header, current_column)
                )
                current_column += 1
        column_headers_config = OrderedDict()
        for column in sorted(columns, key=lambda x: x[2]):
            column_headers_config[column[0]] = column[1]
        return column_headers_config


def CommandBillOfMaterial(
    column_headers=None,
    column_units=None,
    rebar_length_type=None,
    reinforcement_group_by=None,
    font_family=None,
    font_size=None,
    column_width=None,
    row_height=None,
    bom_left_offset=None,
    bom_top_offset=None,
    bom_min_right_offset=None,
    bom_min_bottom_offset=None,
    bom_table_svg_max_width=None,
    bom_table_svg_max_height=None,
    template_file=None,
):
    """This function is used to invoke dialog box for rebars bill of material"""
    bom_preferences = BOMPreferences()
    column_headers = column_headers or bom_preferences.getColumnHeaders()
    column_units = column_units or bom_preferences.getColumnUnits()
    rebar_length_type = (
        rebar_length_type or bom_preferences.getRebarLengthType()
    )
    reinforcement_group_by = (
        reinforcement_group_by or bom_preferences.getReinforcementGroupBy()
    )

    svg_pref = bom_preferences.getSVGPrefGroup()
    font_family = font_family or svg_pref.GetString("FontFamily")
    font_size = font_size or svg_pref.GetFloat("FontSize")
    column_width = column_width or svg_pref.GetFloat("ColumnWidth")
    row_height = row_height or svg_pref.GetFloat("RowHeight")
    if bom_left_offset is None:
        bom_left_offset = svg_pref.GetFloat("LeftOffset")
    if bom_top_offset is None:
        bom_top_offset = svg_pref.GetFloat("TopOffset")
    if bom_min_right_offset is None:
        bom_min_right_offset = svg_pref.GetFloat("MinRightOffset")
    if bom_min_bottom_offset is None:
        bom_min_bottom_offset = svg_pref.GetFloat("MinBottomOffset")
    bom_table_svg_max_width = bom_table_svg_max_width or svg_pref.GetFloat(
        "MaxWidth"
    )
    bom_table_svg_max_height = bom_table_svg_max_height or svg_pref.GetFloat(
        "MaxHeight"
    )
    if template_file is None:
        template_file = svg_pref.GetString("TemplateFile")

    dialog = _BillOfMaterialDialog(
        column_headers,
        column_units,
        rebar_length_type,
        reinforcement_group_by,
        font_family,
        font_size,
        column_width,
        row_height,
        bom_left_offset,
        bom_top_offset,
        bom_min_right_offset,
        bom_min_bottom_offset,
        bom_table_svg_max_width,
        bom_table_svg_max_height,
        template_file,
    )
    dialog.setupUi()
    dialog.form.exec_()
