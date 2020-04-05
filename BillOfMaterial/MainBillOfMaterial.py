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
from PySide2 import QtWidgets

import FreeCADGui

from .BillOfMaterial import makeBillOfMaterial
from .config import *


class _BillOfMaterialDialog:
    def __init__(self, column_headers, rebar_length_type):
        self.column_headers_data = column_headers
        self.rebar_length_type = rebar_length_type
        self.allowed_rebar_length_types = ["RealLength", "LengthWithSharpEdges"]
        self.form = FreeCADGui.PySideUic.loadUi(
            os.path.splitext(__file__)[0] + ".ui"
        )
        self.form.setWindowTitle(
            QtWidgets.QApplication.translate(
                "RebarAddon", "Rebars Bill Of Material", None
            )
        )

    def setupUi(self):
        self.connectSignalSlots()
        self.addColumnHeaders()
        self.addDropdownMenuItems()
        self.form.rebarLengthType.setCurrentIndex(
            self.form.rebarLengthType.findText(self.rebar_length_type)
        )

    def connectSignalSlots(self):
        self.form.buttonBox.accepted.connect(self.accept)
        self.form.buttonBox.rejected.connect(lambda: self.form.close())

    def addDropdownMenuItems(self):
        self.form.rebarLengthType.addItems(self.allowed_rebar_length_types)

    def addColumnHeaders(self):
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
            show_hide_checkbox.setText("hide")
            if column_header_tuple[1] == 0:
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

    def accept(self):
        column_headers = self.getColumnConfigData()
        rebar_length_type = self.form.rebarLengthType.currentText()
        makeBillOfMaterial(
            column_headers=column_headers, rebar_length_type=rebar_length_type
        )
        self.form.close()

    def getColumnConfigData(self):
        column_header_list_widget = self.form.columnHeaderListWidget
        column_headers_config = {}
        items = []
        current_column = 1
        for index in range(column_header_list_widget.count()):
            row_widget_item = column_header_list_widget.item(index)
            row_widget = column_header_list_widget.itemWidget(row_widget_item)
            h_layout = row_widget.layout()
            show_hide_checkbox = h_layout.itemAt(0).widget()
            if show_hide_checkbox.isChecked():
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
    column_headers=COLUMN_HEADERS, rebar_length_type=REBAR_LENGTH_TYPE
):
    dialog = _BillOfMaterialDialog(column_headers, rebar_length_type)
    dialog.setupUi()
    dialog.form.exec_()
