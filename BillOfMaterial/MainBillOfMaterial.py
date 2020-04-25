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


import os
from PySide2 import QtCore, QtWidgets

import FreeCAD
import FreeCADGui

from .UnitLineEdit import UnitLineEdit
from .BillOfMaterial_Spreadsheet import makeBillOfMaterial
from .BillOfMaterial_SVG import makeBillOfMaterialSVG
from .config import *


class _BillOfMaterialDialog:
    """This is a class for Bill Of Material dialog box."""

    def __init__(
        self,
        column_headers,
        column_units,
        rebar_length_type,
        available_svg_sizes,
        svg_size,
    ):
        """This function set initial data in Bill of Material dialog box."""
        self.column_headers_data = column_headers
        self.column_units = column_units
        self.rebar_length_type = rebar_length_type
        self.allowed_rebar_length_types = ["RealLength", "LengthWithSharpEdges"]
        self.available_svg_sizes = available_svg_sizes
        self.svg_size = svg_size
        self.form = FreeCADGui.PySideUic.loadUi(
            os.path.splitext(__file__)[0] + ".ui"
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

        # Set SVG size in ui
        if self.svg_size in self.available_svg_sizes.values():
            self.form.predefinedSVGSize.setCurrentIndex(
                self.form.predefinedSVGSize.findText(
                    list(self.available_svg_sizes.keys())[
                        list(self.available_svg_sizes.values()).index(
                            self.svg_size
                        )
                    ]
                )
            )
            self.form.predefinedSVGSizeRadio.setChecked(True)
            self.form.customSVGSizeRadio.setChecked(False)
            self.predefined_svg_size_radio_clicked()
        else:
            try:
                svg_width = float(self.svg_size.split("x")[0].strip())
                svg_height = float(self.svg_size.split("x")[1].strip())
                self.form.svgWidth.setText(str(svg_width) + "mm")
                self.form.svgHeight.setText(str(svg_height) + "mm")
                self.form.predefinedSVGSizeRadio.setChecked(False)
                self.form.customSVGSizeRadio.setChecked(True)
                self.custom_svg_size_radio_clicked()
            except:
                self.form.predefinedSVGSize.setCurrentIndex(
                    self.form.predefinedSVGSize.findText("Fit BOM")
                )
                self.form.predefinedSVGSizeRadio.setChecked(True)
                self.form.customSVGSizeRadio.setChecked(False)
                self.predefined_svg_size_radio_clicked()

        # Connect signal and slots in ui
        self.connectSignalSlots()

    def connectSignalSlots(self):
        """This function is used to connect different slots in UI to appropriate
        functions."""
        self.form.buttonBox.accepted.connect(self.accept)
        self.form.buttonBox.rejected.connect(lambda: self.form.close())
        self.form.predefinedSVGSizeRadio.clicked.connect(
            self.predefined_svg_size_radio_clicked
        )
        self.form.customSVGSizeRadio.clicked.connect(
            self.custom_svg_size_radio_clicked
        )

    def addUnitsInputFields(self):
        """This function add input fields for units of data."""
        main_layout = self.form.verticalLayout
        column_units_layouts = []
        for column, unit in reversed(self.column_units.items()):
            column_name = QtWidgets.QLabel(column + " unit")
            column_name.setMinimumWidth(160)
            column_unit = UnitLineEdit(unit)
            h_layout = QtWidgets.QHBoxLayout()
            h_layout.setSpacing(60)
            h_layout.addWidget(column_name)
            h_layout.addWidget(column_unit)
            main_layout.insertLayout(1, h_layout)
            column_units_layouts.insert(0, h_layout)
        self.column_units_layouts = column_units_layouts

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
            column_name.setMinimumWidth(120)
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

        svg_size_list = ["Fit BOM"]
        svg_size_list.extend(self.available_svg_sizes.keys())
        self.form.predefinedSVGSize.addItems(svg_size_list)
        for i, size in enumerate(self.available_svg_sizes):
            self.form.predefinedSVGSize.setItemData(
                i + 1,
                "size: " + self.available_svg_sizes[size],
                QtCore.Qt.ItemDataRole.ToolTipRole,
            )

    def predefined_svg_size_radio_clicked(self):
        self.form.predefinedSVGSize.setEnabled(True)
        self.form.customSVGSizeWidget.setEnabled(False)

    def custom_svg_size_radio_clicked(self):
        self.form.predefinedSVGSize.setEnabled(False)
        self.form.customSVGSizeWidget.setEnabled(True)

    def accept(self):
        """This function is executed when 'OK' button is clicked from UI. It
        execute a function to generate rebars bill of material."""
        # Validate entered units
        units_valid_flag = True
        for unit_h_layout in self.column_units_layouts:
            unit_field = unit_h_layout.itemAt(1).widget()
            if not unit_field.isValidUnit():
                unit_text = unit_field.text()
                unit_field.setText(unit_text + " (Invalid Unit)")
                units_valid_flag = False
        if not units_valid_flag:
            return

        column_units = self.getColumnUnits()
        column_headers = self.getColumnConfigData()
        rebar_length_type = self.form.rebarLengthType.currentText()
        create_spreadsheet = self.form.createSpreadsheet.isChecked()
        if create_spreadsheet:
            makeBillOfMaterial(
                column_headers=column_headers,
                column_units=column_units,
                rebar_length_type=rebar_length_type,
            )
        export_svg = self.form.exportSVG.isChecked()
        if export_svg:
            svg_size = self.getSVGSize()
            svg_string = makeBillOfMaterialSVG(
                column_headers=column_headers,
                column_units=column_units,
                rebar_length_type=rebar_length_type,
                svg_size=svg_size,
            )
            self.saveSVG(svg_string)
        self.form.close()

    def getSVGSize(self):
        """This function is used to get svg size from ui."""
        predefined_svg_size_check = self.form.predefinedSVGSizeRadio.isChecked()
        custom_svg_size_check = self.form.customSVGSizeRadio.isChecked()

        if predefined_svg_size_check:
            svg_sheet = self.form.predefinedSVGSize.currentText()
            if svg_sheet in self.available_svg_sizes:
                svg_size = self.available_svg_sizes[
                    self.form.predefinedSVGSize.currentText()
                ]
                return svg_size
            else:
                return ""
        elif custom_svg_size_check:
            svg_width = self.form.svgWidth.text()
            svg_width = FreeCAD.Units.Quantity(svg_width).Value
            svg_height = self.form.svgHeight.text()
            svg_height = FreeCAD.Units.Quantity(svg_height).Value
            svg_size = str(svg_width) + "x" + str(svg_height)
            return svg_size

    def saveSVG(self, svg_string):
        """This function save svg output in file chosen from a file dialog box.
        """
        import FreeCAD

        path = FreeCAD.ConfigGet("UserAppData")
        svg_filename, Filter = QtWidgets.QFileDialog.getSaveFileName(
            None, "Export svg output", path, "*.svg"
        )
        if not svg_filename:
            FreeCAD.Console.PrintError("SVG output not saved: Empty filename\n")
            return

        try:
            with open(svg_filename, "w") as svg_file:
                svg_file.write(svg_string)

        except:
            FreeCAD.Console.PrintError(
                "Error writing svg to file " + svg_filename + "\n"
            )

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
        data as key and values are tuple of column_header and sequnce number.
        e.g. {
                "Member": ("Member", 1),
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


def CommandBillOfMaterial(
    column_headers=COLUMN_HEADERS,
    column_units=COLUMN_UNITS,
    rebar_length_type=REBAR_LENGTH_TYPE,
    available_svg_sizes=AVAILABLE_SVG_SIZES,
    svg_size=SVG_SIZE,
):
    """This function is used to invoke dialog box for rebars bill of
    material."""
    dialog = _BillOfMaterialDialog(
        column_headers,
        column_units,
        rebar_length_type,
        available_svg_sizes,
        svg_size,
    )
    dialog.setupUi()
    dialog.form.exec_()
