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

__title__ = "Rebar Shape Cut List Gui"
__author__ = "Suraj"
__url__ = "https://www.freecadweb.org"

import os
from typing import Tuple, Union, List

import Draft
import FreeCAD
import FreeCADGui
import importSVG
from PySide2 import QtGui, QtWidgets

from BillOfMaterial.BOMfunc import getReinforcementRebarObjects
from BillOfMaterial.UnitLineEdit import UnitLineEdit
from RebarShapeCutList.RebarShapeCutListfunc import (
    getRebarShapeCutList,
    getBaseRebarsList,
)


class _RebarShapeCutListDialog:
    """A Rebar Shape Cut List dialog box"""

    def __init__(
        self,
        stirrup_extended_edge_offset: float,
        rebars_stroke_width: float,
        rebars_color_style: str,
        row_height: float,
        width: float,
        side_padding: float,
        horizontal_rebar_shape: bool,
        include_mark: bool,
        include_dimensions: bool,
        include_units_in_dimension_label: bool,
        rebar_edge_dimension_units: str,
        rebar_edge_dimension_precision: int,
        dimension_font_family: str,
        dimension_font_size: float,
        bent_angle_dimension_exclude_list: Tuple[float, ...],
        helical_rebar_dimension_label_format: str,
    ):
        """This function set initial data in Rebar Shape Cut List dialog box."""
        self.stirrup_extended_edge_offset = stirrup_extended_edge_offset
        self.rebars_stroke_width = rebars_stroke_width
        self.rebars_color_style = rebars_color_style
        self.row_height = row_height
        self.width = width
        self.side_padding = side_padding
        self.horizontal_rebar_shape = horizontal_rebar_shape
        self.include_mark = include_mark
        self.include_dimensions = include_dimensions
        self.include_units_in_dimension_label = include_units_in_dimension_label
        self.rebar_edge_dimension_units = rebar_edge_dimension_units
        self.rebar_edge_dimension_precision = rebar_edge_dimension_precision
        self.dimension_font_family = dimension_font_family
        self.dimension_font_size = dimension_font_size
        self.bent_angle_dimension_exclude_list = (
            bent_angle_dimension_exclude_list
        )
        self.helical_rebar_dimension_label_format = (
            helical_rebar_dimension_label_format
        )
        self.form = FreeCADGui.PySideUic.loadUi(
            os.path.splitext(__file__)[0] + ".ui"
        )
        self.form.setWindowTitle(
            QtWidgets.QApplication.translate(
                "ReinforcementWorkbench", "Rebar Shape Cut List", None
            )
        )

    def setupUi(self):
        """This function is used to add components to ui."""
        self.addUnitsInputFields()
        self.form.stirrupExtendedEdgeOffset.setText(
            str(self.stirrup_extended_edge_offset)
        )
        self.form.rebarsStrokeWidth.setText(str(self.rebars_stroke_width))
        if self.rebars_color_style == "shape color":
            self.form.shapeColorRadio.setChecked(True)
            self.form.customColorRadio.setChecked(False)
            self.form.rebarsColor.setEnabled(False)
        else:
            self.form.shapeColorRadio.setChecked(False)
            self.form.customColorRadio.setChecked(True)
            self.form.rebarsColor.setEnabled(True)
            color_rgba = importSVG.getcolor(self.rebars_color_style)
            color = QtGui.QColor()
            color.setRgb(
                color_rgba[0], color_rgba[1], color_rgba[2], color_rgba[3]
            )
            self.form.rebarsColor.setProperty("color", color)
        self.form.rowHeight.setText(str(self.row_height))
        self.form.columnWidth.setText(str(self.width))
        self.form.sidePadding.setText(str(self.side_padding))
        self.form.horizontalRebarShape.setChecked(self.horizontal_rebar_shape)
        self.form.includeMark.setChecked(self.include_mark)
        self.form.includeDimensions.setChecked(self.include_dimensions)
        self.form.dimensionDataWidget.setEnabled(self.include_dimensions)
        self.form.includeUnitsInDimensionLabel.setChecked(
            self.include_units_in_dimension_label
        )
        self.form.rebarEdgeDimensionPrecision.setValue(
            self.rebar_edge_dimension_precision
        )
        if (
            self.form.dimensionFontFamily.findText(self.dimension_font_family)
            == -1
        ):
            self.form.dimensionFontFamily.setCurrentIndex(0)
        else:
            self.form.dimensionFontFamily.setCurrentIndex(
                self.form.dimensionFontFamily.findText(
                    self.dimension_font_family
                )
            )
        self.form.dimensionFontSize.setValue(self.dimension_font_size)
        self.form.bentAngleDimensionExcludeList.setText(
            ", ".join(map(str, self.bent_angle_dimension_exclude_list))
        )
        self.form.helicalRebarDimensionLabelFormat.setText(
            self.helical_rebar_dimension_label_format
        )

        self.connectSignalSlots()

    def addUnitsInputFields(self):
        """This function add input fields for units of data."""
        rebar_edge_dimension_layout = self.form.rebarEdgeDimensionUnitsHLayout
        self.rebar_edge_dimension_units_widget = UnitLineEdit(
            self.rebar_edge_dimension_units
        )
        rebar_edge_dimension_layout.addWidget(
            self.rebar_edge_dimension_units_widget
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
            None, "Choose output file for Bill of Material", path, "*.svg"
        )
        if output_file:
            self.form.svgOutputFile.setText(
                os.path.splitext(str(output_file))[0] + ".svg"
            )

    def accept(self):
        """This function is executed when 'OK' button is clicked from UI. It
        execute a function to generate rebar shape cut list."""
        # Validate entered units
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
        base_rebars_list = getBaseRebarsList(reinforcement_objs)

        self.stirrup_extended_edge_offset = FreeCAD.Units.Quantity(
            self.form.stirrupExtendedEdgeOffset.text()
        ).Value
        self.rebars_stroke_width = FreeCAD.Units.Quantity(
            self.form.rebarsStrokeWidth.text()
        ).Value
        if self.form.shapeColorRadio.isChecked():
            self.rebars_color_style = "shape color"
        else:
            self.rebars_color_style = Draft.getrgb(
                self.form.rebarsColor.property("color").getRgb()
            )
        self.row_height = FreeCAD.Units.Quantity(
            self.form.rowHeight.text()
        ).Value
        self.width = FreeCAD.Units.Quantity(self.form.columnWidth.text()).Value
        self.side_padding = FreeCAD.Units.Quantity(
            self.form.sidePadding.text()
        ).Value
        self.horizontal_rebar_shape = self.form.horizontalRebarShape.isChecked()
        self.include_mark = self.form.includeMark.isChecked()
        self.include_dimensions = self.form.includeDimensions.isChecked()
        self.include_units_in_dimension_label = (
            self.form.includeUnitsInDimensionLabel.isChecked()
        )
        self.rebar_edge_dimension_units = FreeCAD.Units.Quantity(
            self.rebar_edge_dimension_units_widget.text()
        ).Value
        self.rebar_edge_dimension_precision = (
            self.form.rebarEdgeDimensionPrecision.value()
        )
        self.dimension_font_family = self.form.dimensionFontFamily.currentText()
        self.dimension_font_size = self.form.dimensionFontSize.value()
        bent_angle_dimension_exclude_list_str = (
            self.form.bentAngleDimensionExcludeList.text()
        )
        self.bent_angle_dimension_exclude_list = []
        for angle in bent_angle_dimension_exclude_list_str.split(","):
            try:
                self.bent_angle_dimension_exclude_list.append(
                    float(angle.strip())
                )
            except ValueError:
                pass
        self.helical_rebar_dimension_label_format = (
            self.form.helicalRebarDimensionLabelFormat.text()
        )

        getRebarShapeCutList(
            base_rebars_list=base_rebars_list,
            include_mark=self.include_mark,
            stirrup_extended_edge_offset=self.stirrup_extended_edge_offset,
            rebars_stroke_width=self.rebars_stroke_width,
            rebars_color_style=self.rebars_color_style,
            include_dimensions=self.include_dimensions,
            rebar_edge_dimension_units=self.rebar_edge_dimension_units,
            rebar_edge_dimension_precision=self.rebar_edge_dimension_precision,
            include_units_in_dimension_label=(
                self.include_units_in_dimension_label
            ),
            bent_angle_dimension_exclude_list=(
                self.bent_angle_dimension_exclude_list
            ),
            dimension_font_family=self.dimension_font_family,
            dimension_font_size=self.dimension_font_size,
            helical_rebar_dimension_label_format=(
                self.helical_rebar_dimension_label_format
            ),
            row_height=self.row_height,
            width=self.width,
            side_padding=self.side_padding,
            horizontal_rebar_shape=self.horizontal_rebar_shape,
            output_file=output_file,
        )

        self.form.close()


def CommandRebarShapeCutList(
    stirrup_extended_edge_offset: float = 2,
    rebars_stroke_width: float = 0.35,
    rebars_color_style: str = "shape color",
    row_height: float = 40,
    width: float = 60,
    side_padding: float = 1,
    horizontal_rebar_shape: bool = True,
    include_mark: bool = True,
    include_dimensions: bool = True,
    include_units_in_dimension_label: bool = False,
    rebar_edge_dimension_units: str = "mm",
    rebar_edge_dimension_precision: int = 0,
    dimension_font_family: str = "DejaVu Sans",
    dimension_font_size: float = 2,
    bent_angle_dimension_exclude_list: Union[Tuple[float, ...], List[float]] = (
        45,
        90,
        180,
    ),
    helical_rebar_dimension_label_format: str = "%L,r=%R,pitch=%P",
):
    """This function is used to invoke dialog box for rebar shape cut list"""
    dialog = _RebarShapeCutListDialog(
        stirrup_extended_edge_offset,
        rebars_stroke_width,
        rebars_color_style,
        row_height,
        width,
        side_padding,
        horizontal_rebar_shape,
        include_mark,
        include_dimensions,
        include_units_in_dimension_label,
        rebar_edge_dimension_units,
        rebar_edge_dimension_precision,
        dimension_font_family,
        dimension_font_size,
        bent_angle_dimension_exclude_list,
        helical_rebar_dimension_label_format,
    )
    dialog.setupUi()
    dialog.form.exec_()
