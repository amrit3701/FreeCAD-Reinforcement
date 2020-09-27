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

__title__ = "BOM - Edit SVG Configuration Gui"
__author__ = "Suraj"
__url__ = "https://www.freecadweb.org"


import os
from PySide2 import QtWidgets

import FreeCAD
import FreeCADGui


class _EditSVGConfigurationDialog:
    """This is a class for dialog box of editing Bill Of Material SVG
    configuration."""

    def __init__(
        self,
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
        """This function set initial data in SVG Configuration edit dialog box.
        """
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
            os.path.splitext(__file__)[0] + ".ui"
        )
        self.form.setWindowTitle(
            QtWidgets.QApplication.translate(
                "RebarAddon", "BOM - Edit SVG Configurations", None
            )
        )

    def setupUi(self):
        """This function is used to setup ui by calling appropriate functions.
        """
        self.setDefaultValues()
        self.connectSignalSlots()

    def setDefaultValues(self):
        """This function is used to set default values in ui."""
        if self.form.fontFamily.findText(self.font_family) == -1:
            self.form.fontFamily.setCurrentIndex(0)
        else:
            self.form.fontFamily.setCurrentIndex(
                self.form.fontFamily.findText(self.font_family)
            )
        self.form.fontSize.setValue(self.font_size)
        self.form.columnWidth.setText(str(self.column_width))
        self.form.rowHeight.setText(str(self.row_height))
        self.form.bomLeftOffset.setText(str(self.bom_left_offset))
        self.form.bomTopOffset.setText(str(self.bom_top_offset))
        self.form.bomMinRightOffset.setText(str(self.bom_min_right_offset))
        self.form.bomMinBottomOffset.setText(str(self.bom_min_bottom_offset))
        self.form.bomMaxWidth.setText(str(self.bom_table_svg_max_width))
        self.form.bomMaxHeight.setText(str(self.bom_table_svg_max_height))
        self.form.templateFile.setText(str(self.template_file))

    def connectSignalSlots(self):
        """This function is used to connect different slots in UI to appropriate
        functions."""
        self.form.chooseTemplateFile.clicked.connect(
            self.choose_template_clicked
        )
        self.form.buttonBox.accepted.connect(self.accept)
        self.form.buttonBox.rejected.connect(lambda: self.form.close())

    def choose_template_clicked(self):
        """This function is executed when Choose button clicked in ui to execute
        QFileDialog to select svg template file."""
        path = FreeCAD.ConfigGet("UserAppData")
        template_file, Filter = QtWidgets.QFileDialog.getOpenFileName(
            None, "Choose template for Bill of Material", path, "*.svg"
        )
        if template_file:
            self.form.templateFile.setText(str(template_file))

    def accept(self):
        """This function is executed when 'OK' button is clicked from UI."""
        self.font_family = self.form.fontFamily.currentText()
        self.font_size = self.form.fontSize.value()
        self.column_width = FreeCAD.Units.Quantity(
            self.form.columnWidth.text()
        ).Value
        self.row_height = FreeCAD.Units.Quantity(
            self.form.rowHeight.text()
        ).Value
        self.bom_left_offset = FreeCAD.Units.Quantity(
            self.form.bomLeftOffset.text()
        ).Value
        self.bom_top_offset = FreeCAD.Units.Quantity(
            self.form.bomTopOffset.text()
        ).Value
        self.bom_min_right_offset = FreeCAD.Units.Quantity(
            self.form.bomMinRightOffset.text()
        ).Value
        self.bom_min_bottom_offset = FreeCAD.Units.Quantity(
            self.form.bomMinBottomOffset.text()
        ).Value
        self.bom_table_svg_max_width = FreeCAD.Units.Quantity(
            self.form.bomMaxWidth.text()
        ).Value
        self.bom_table_svg_max_height = FreeCAD.Units.Quantity(
            self.form.bomMaxHeight.text()
        ).Value
        self.template_file = self.form.templateFile.text()
        self.form.close()


def runEditSVGConfigurationDialog(parent_dialog):
    """This function is used to invoke dialog box for editing svg configuration
    for bill of material. It is also responsive for returning data to parent
    dialog box."""
    dialog = _EditSVGConfigurationDialog(
        parent_dialog.font_family,
        parent_dialog.font_size,
        parent_dialog.column_width,
        parent_dialog.row_height,
        parent_dialog.bom_left_offset,
        parent_dialog.bom_top_offset,
        parent_dialog.bom_min_right_offset,
        parent_dialog.bom_min_bottom_offset,
        parent_dialog.bom_table_svg_max_width,
        parent_dialog.bom_table_svg_max_height,
        parent_dialog.template_file,
    )
    dialog.setupUi()
    dialog.form.exec_()
    parent_dialog.font_family = dialog.font_family
    parent_dialog.font_size = dialog.font_size
    parent_dialog.column_width = dialog.column_width
    parent_dialog.row_height = dialog.row_height
    parent_dialog.bom_left_offset = dialog.bom_left_offset
    parent_dialog.bom_top_offset = dialog.bom_top_offset
    parent_dialog.bom_min_right_offset = dialog.bom_min_right_offset
    parent_dialog.bom_min_bottom_offset = dialog.bom_min_bottom_offset
    parent_dialog.bom_table_svg_max_width = dialog.bom_table_svg_max_width
    parent_dialog.bom_table_svg_max_height = dialog.bom_table_svg_max_height
    parent_dialog.template_file = dialog.template_file
