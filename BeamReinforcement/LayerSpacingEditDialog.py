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

__title__ = "Layer Spacing Edit Dialog"
__author__ = "Suraj"
__url__ = "https://www.freecadweb.org"

import os
from PySide2 import QtWidgets

import FreeCAD
import FreeCADGui


class _LayerSpacingEditDialog:
    def __init__(self, layer_spacing_tuple):
        self.LayerSpacingTuple = layer_spacing_tuple
        self.Layers = 0
        self.LayerSpacingInputFieldList = []
        self.form = FreeCADGui.PySideUic.loadUi(
            os.path.splitext(__file__)[0] + ".ui"
        )
        self.form.setWindowTitle(
            QtWidgets.QApplication.translate(
                "Arch", "Layer Spacing Edit Dialog", None
            )
        )

    def setupUi(self):
        """This function is used to set values in ui."""
        self.connectSignalSlots()
        layers_count = len(self.LayerSpacingTuple)
        for layer in range(1, layers_count + 1):
            self.addLayer()
            self.LayerSpacingInputFieldList[layer - 1].setText(
                str(self.LayerSpacingTuple[layer - 1])
            )

    def connectSignalSlots(self):
        """This function is used to connect different slots in UI to appropriate
        functions."""
        self.form.buttonBox.accepted.connect(self.accept)
        self.form.buttonBox.rejected.connect(lambda: self.form.close())

    def addLayer(self):
        layer = self.Layers + 1
        # Create Layer Spacing Input Field
        ui = FreeCADGui.UiLoader()
        layer_spacing = ui.createWidget("Gui::InputField")
        layer_spacing.setProperty("unit", "mm")
        layer_spacing.setText("30 mm")
        self.LayerSpacingInputFieldList.append(layer_spacing)

        layout = self.form.formLayout
        index = layer - 1
        layout.insertRow(index, "Layer" + str(layer), layer_spacing)
        self.Layers += 1

    def accept(self):
        """This function is executed when 'OK' button is clicked from ui."""
        layers = self.Layers
        layer_spacing_list = []
        for layer in range(1, layers + 1):
            layer_spacing = self.LayerSpacingInputFieldList[layer - 1].text()
            layer_spacing_list.append(
                FreeCAD.Units.Quantity(layer_spacing).Value
            )
        self.LayerSpacingTuple = tuple(layer_spacing_list)
        self.form.close()


def runLayerSpacingEditDialog(self, layer_spacing_tuple):
    dialog = _LayerSpacingEditDialog(layer_spacing_tuple)
    dialog.setupUi()
    dialog.form.exec_()
    self.LayerSpacingTuple = dialog.LayerSpacingTuple
