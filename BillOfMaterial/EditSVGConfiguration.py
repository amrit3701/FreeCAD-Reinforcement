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
from PySide2 import QtCore, QtGui, QtWidgets

import FreeCAD
import FreeCADGui


class _EditSVGConfigurationDialog:
    """This is a class for dialog box of editing Bill Of Material SVG
    configuration."""

    def __init__(
        self,
        svg_project_info,
        svg_company_info,
        svg_company_logo,
        svg_company_logo_width,
        svg_company_logo_height,
        svg_footer,
        font_size,
        column_width,
        row_height,
        bom_left_offset,
        bom_right_offset,
        bom_top_offset,
        bom_bottom_offset,
        available_svg_sizes,
        svg_size,
    ):
        """This function set initial data in SVG Configuration edit dialog box.
        """
        self.svg_project_info = svg_project_info
        self.svg_company_info = svg_company_info
        self.svg_company_logo = svg_company_logo
        self.tmp_svg_company_logo = svg_company_logo
        self.svg_company_logo_width = svg_company_logo_width
        self.svg_company_logo_height = svg_company_logo_height
        self.svg_footer = svg_footer
        self.font_size = font_size
        self.column_width = column_width
        self.row_height = row_height
        self.bom_left_offset = bom_left_offset
        self.bom_right_offset = bom_right_offset
        self.bom_top_offset = bom_top_offset
        self.bom_bottom_offset = bom_bottom_offset
        self.available_svg_sizes = available_svg_sizes
        self.svg_size = svg_size
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
        self.addDropdownMenuItems()
        self.setDefaultValues()
        self.connectSignalSlots()

    def addDropdownMenuItems(self):
        """This function add dropdown items to each Gui::PrefComboBox."""
        svg_size_list = ["Fit BOM"]
        svg_size_list.extend(self.available_svg_sizes.keys())
        self.form.predefinedSVGSize.addItems(svg_size_list)
        for i, size in enumerate(self.available_svg_sizes):
            self.form.predefinedSVGSize.setItemData(
                i + 1,
                "size: " + self.available_svg_sizes[size],
                QtCore.Qt.ItemDataRole.ToolTipRole,
            )

    def setDefaultValues(self):
        """This function is used to set default values in ui."""
        self.form.projectInfo.setPlainText(self.svg_project_info)
        self.form.companyInfo.setPlainText(self.svg_company_info)
        if self.svg_company_logo:
            self.form.companyLogoImage.setPixmap(
                QtGui.QPixmap(str(self.svg_company_logo)).scaled(
                    120,
                    120,
                    QtCore.Qt.KeepAspectRatio,
                    QtCore.Qt.SmoothTransformation,
                )
            )
        self.form.logoWidth.setText(str(self.svg_company_logo_width))
        self.form.logoHeight.setText(str(self.svg_company_logo_height))
        self.form.svgFooter.setText(self.svg_footer)
        self.form.fontSize.setValue(self.font_size)
        self.form.columnWidth.setText(str(self.column_width))
        self.form.rowHeight.setText(str(self.row_height))
        self.form.bomLeftOffset.setText(str(self.bom_left_offset))
        self.form.bomRightOffset.setText(str(self.bom_right_offset))
        self.form.bomTopOffset.setText(str(self.bom_top_offset))
        self.form.bomBottomOffset.setText(str(self.bom_bottom_offset))

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

    def connectSignalSlots(self):
        """This function is used to connect different slots in UI to appropriate
        functions."""
        self.form.clearCompanyLogo.clicked.connect(self.clear_logo_clicked)
        self.form.editCompanyLogo.clicked.connect(self.edit_logo_clicked)
        self.form.predefinedSVGSizeRadio.clicked.connect(
            self.predefined_svg_size_radio_clicked
        )
        self.form.customSVGSizeRadio.clicked.connect(
            self.custom_svg_size_radio_clicked
        )
        self.form.buttonBox.accepted.connect(self.accept)
        self.form.buttonBox.rejected.connect(lambda: self.form.close())

    def clear_logo_clicked(self):
        """This function is executed when Clear button clicked in ui to clear
        svg company logo."""
        self.tmp_svg_company_logo = ""
        self.form.companyLogoImage.clear()

    def edit_logo_clicked(self):
        """This function is executed when Edit button clicked in ui to execute
        QFileDialog to select company logo image."""
        path = FreeCAD.ConfigGet("UserAppData")
        logo_file, Filter = QtWidgets.QFileDialog.getOpenFileName(
            None, "Choose company logo image", path, "*png *jpeg *jpg *ico *bmp"
        )
        if logo_file:
            self.tmp_svg_company_logo = logo_file
            self.form.companyLogoImage.setPixmap(
                QtGui.QPixmap(str(self.tmp_svg_company_logo)).scaled(
                    120,
                    120,
                    QtCore.Qt.KeepAspectRatio,
                    QtCore.Qt.SmoothTransformation,
                )
            )

    def predefined_svg_size_radio_clicked(self):
        """This function is executed when Predefined svg size radio button is
        clicked in ui."""
        self.form.predefinedSVGSize.setEnabled(True)
        self.form.customSVGSizeWidget.setEnabled(False)

    def custom_svg_size_radio_clicked(self):
        """This function is executed when Custom svg size radio button is
        clicked in ui."""
        self.form.predefinedSVGSize.setEnabled(False)
        self.form.customSVGSizeWidget.setEnabled(True)

    def accept(self):
        """This function is executed when 'OK' button is clicked from UI."""
        self.svg_project_info = self.form.projectInfo.toPlainText()
        self.svg_company_info = self.form.companyInfo.toPlainText()
        self.svg_company_logo = self.tmp_svg_company_logo
        self.svg_company_logo_width = FreeCAD.Units.Quantity(
            self.form.logoWidth.text()
        ).Value
        self.svg_company_logo_height = FreeCAD.Units.Quantity(
            self.form.logoHeight.text()
        ).Value
        self.svg_footer = self.form.svgFooter.text()
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
        self.bom_right_offset = FreeCAD.Units.Quantity(
            self.form.bomRightOffset.text()
        ).Value
        self.bom_top_offset = FreeCAD.Units.Quantity(
            self.form.bomTopOffset.text()
        ).Value
        self.bom_bottom_offset = FreeCAD.Units.Quantity(
            self.form.bomBottomOffset.text()
        ).Value
        self.svg_size = self.getSVGSize()
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


def runEditSVGConfigurationDialog(parent_dialog):
    """This function is used to invoke dialog box for editing svg configuration
    for bill of material. It is also responsive for returning data to parent
    dialog box."""
    dialog = _EditSVGConfigurationDialog(
        parent_dialog.svg_project_info,
        parent_dialog.svg_company_info,
        parent_dialog.svg_company_logo,
        parent_dialog.svg_company_logo_width,
        parent_dialog.svg_company_logo_height,
        parent_dialog.svg_footer,
        parent_dialog.font_size,
        parent_dialog.column_width,
        parent_dialog.row_height,
        parent_dialog.bom_left_offset,
        parent_dialog.bom_right_offset,
        parent_dialog.bom_top_offset,
        parent_dialog.bom_bottom_offset,
        parent_dialog.available_svg_sizes,
        parent_dialog.svg_size,
    )
    dialog.setupUi()
    dialog.form.exec_()
    parent_dialog.svg_project_info = dialog.svg_project_info
    parent_dialog.svg_company_info = dialog.svg_company_info
    parent_dialog.svg_company_logo = dialog.svg_company_logo
    parent_dialog.svg_company_logo_width = dialog.svg_company_logo_width
    parent_dialog.svg_company_logo_height = dialog.svg_company_logo_height
    parent_dialog.svg_footer = dialog.svg_footer
    parent_dialog.font_size = dialog.font_size
    parent_dialog.column_width = dialog.column_width
    parent_dialog.row_height = dialog.row_height
    parent_dialog.bom_left_offset = dialog.bom_left_offset
    parent_dialog.bom_right_offset = dialog.bom_right_offset
    parent_dialog.bom_top_offset = dialog.bom_top_offset
    parent_dialog.bom_bottom_offset = dialog.bom_bottom_offset
    parent_dialog.available_svg_sizes = dialog.available_svg_sizes
    parent_dialog.svg_size = dialog.svg_size
