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

__title__ = "Rounding Edit Dialog"
__author__ = "Suraj"
__url__ = "https://www.freecadweb.org"

import os
from PySide2 import QtWidgets, QtGui

import FreeCAD
import FreeCADGui


class _RoundingEditDialog:
    def __init__(self, rounding_tuple):
        self.RoundingTuple = rounding_tuple
        self.Layers = []
        self.RoundingSpinBoxList = []
        self.form = FreeCADGui.PySideUic.loadUi(
            os.path.splitext(__file__)[0] + ".ui"
        )
        self.form.setWindowTitle(
            QtWidgets.QApplication.translate(
                "Arch", "Rounding Edit Dialog", None
            )
        )

    def setupUi(self):
        """This function is used to set values in ui."""
        self.connectSignalSlots()
        layers_count = len(self.RoundingTuple)
        sets_count_list = [len(x) for x in self.RoundingTuple]
        for layer in range(1, layers_count + 1):
            self.addLayer()
            for i in range(0, sets_count_list[layer - 1]):
                self.addSet()
                if self.RoundingTuple[layer - 1][i] == None:
                    self.RoundingSpinBoxList[layer - 1][i].setValue(2)
                    self.RoundingSpinBoxList[layer - 1][i].setEnabled(False)
                else:
                    self.RoundingSpinBoxList[layer - 1][i].setValue(
                        self.RoundingTuple[layer - 1][i]
                    )
                    self.RoundingSpinBoxList[layer - 1][i].setEnabled(True)

    def connectSignalSlots(self):
        """This function is used to connect different slots in UI to appropriate
        functions."""
        self.form.buttonBox.accepted.connect(self.accept)
        self.form.buttonBox.rejected.connect(lambda: self.form.close())

    def addLayer(self):
        layer = len(self.Layers) + 1
        layout = self.form.verticalLayout
        index = layout.indexOf(self.form.buttonBox)
        # Create Layer label
        layer_label = QtWidgets.QLabel("Layer" + str(layer) + ":")
        layer_label.setFont(QtGui.QFont("Sans", weight=QtGui.QFont.Bold))
        layout.insertWidget(index, layer_label)
        self.Layers.append(layer_label)
        self.RoundingSpinBoxList.append([])

    def addSet(self):
        layer = len(self.Layers)
        sets = len(self.RoundingSpinBoxList[layer - 1])
        # Create horizontal layout and its components
        h_layout = QtWidgets.QHBoxLayout()
        set_label = QtWidgets.QLabel("Set " + str(sets + 1))
        set_label.setSizePolicy(
            QtWidgets.QSizePolicy(
                QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed
            )
        )
        ui = FreeCADGui.UiLoader()
        rounding = ui.createWidget("Gui::PrefSpinBox")
        rounding.setValue(4)
        h_layout.addWidget(set_label)
        h_layout.addWidget(rounding)
        v_layout = self.form.verticalLayout
        index = v_layout.indexOf(self.form.buttonBox)
        v_layout.insertLayout(index, h_layout)
        self.RoundingSpinBoxList[layer - 1].append(rounding)

    def accept(self):
        """This function is executed when 'OK' button is clicked from ui."""
        layers = len(self.Layers)
        rounding_list = []
        for layer in range(1, layers + 1):
            rounding_list.append(self.getRoundingTuple(layer))
        self.RoundingTuple = tuple(rounding_list)
        self.form.close()

    def getRoundingTuple(self, layer):
        sets = len(self.RoundingSpinBoxList[layer - 1])
        rounding_list = []
        for i in range(0, sets):
            if self.RoundingSpinBoxList[layer - 1][i].isEnabled():
                rounding = self.RoundingSpinBoxList[layer - 1][i].value()
                rounding_list.append(rounding)
            else:
                rounding_list.append(None)
        return tuple(rounding_list)


def runRoundingEditDialog(self, rounding_tuple):
    dialog = _RoundingEditDialog(rounding_tuple)
    dialog.setupUi()
    dialog.form.exec_()
    self.RoundingTuple = dialog.RoundingTuple
