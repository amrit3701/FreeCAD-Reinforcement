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

__title__ = "Hook Orientation Edit Dialog"
__author__ = "Suraj"
__url__ = "https://www.freecadweb.org"

import os
from PySide2 import QtWidgets, QtGui

import FreeCADGui


class _HookOrientationEditDialog:
    def __init__(self, hook_orientation_tuple):
        self.HookOrientationTuple = hook_orientation_tuple
        self.Layers = []
        self.HookOrientationComboBoxList = []
        self.form = FreeCADGui.PySideUic.loadUi(
            os.path.splitext(__file__)[0] + ".ui"
        )
        self.form.setWindowTitle(
            QtWidgets.QApplication.translate(
                "Arch", "Hook Orientation Edit Dialog", None
            )
        )

    def setupUi(self):
        """This function is used to set values in ui."""
        self.connectSignalSlots()
        layers_count = len(self.HookOrientationTuple)
        sets_count_list = [len(x) for x in self.HookOrientationTuple]
        for layer in range(1, layers_count + 1):
            self.addLayer()
            for i in range(0, sets_count_list[layer - 1]):
                self.addSet()
                if self.HookOrientationTuple[layer - 1][i] == None:
                    self.HookOrientationComboBoxList[layer - 1][
                        i
                    ].setCurrentIndex(
                        self.HookOrientationComboBoxList[layer - 1][i].findText(
                            "Front Inside"
                        )
                    )
                    self.HookOrientationComboBoxList[layer - 1][i].setEnabled(
                        False
                    )
                else:
                    self.HookOrientationComboBoxList[layer - 1][
                        i
                    ].setCurrentIndex(
                        self.HookOrientationComboBoxList[layer - 1][i].findText(
                            self.HookOrientationTuple[layer - 1][i]
                        )
                    )
                    self.HookOrientationComboBoxList[layer - 1][i].setEnabled(
                        True
                    )

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
        self.HookOrientationComboBoxList.append([])

    def addSet(self):
        layer = len(self.Layers)
        sets = len(self.HookOrientationComboBoxList[layer - 1])
        # Create horizontal layout and its components
        h_layout = QtWidgets.QHBoxLayout()
        set_label = QtWidgets.QLabel("Set " + str(sets + 1))
        set_label.setSizePolicy(
            QtWidgets.QSizePolicy(
                QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed
            )
        )
        ui = FreeCADGui.UiLoader()
        hook_orientation = ui.createWidget("Gui::PrefComboBox")
        hook_orientation.addItems(
            ["Front Inside", "Front Outside", "Rear Inside", "Rear Outside"]
        )
        h_layout.addWidget(set_label)
        h_layout.addWidget(hook_orientation)
        v_layout = self.form.verticalLayout
        index = v_layout.indexOf(self.form.buttonBox)
        v_layout.insertLayout(index, h_layout)
        self.HookOrientationComboBoxList[layer - 1].append(hook_orientation)

    def accept(self):
        """This function is executed when 'OK' button is clicked from ui."""
        layers = len(self.Layers)
        hook_orientation_list = []
        for layer in range(1, layers + 1):
            hook_orientation_list.append(self.getHookOrientationTuple(layer))
        self.HookOrientationTuple = tuple(hook_orientation_list)
        self.form.close()

    def getHookOrientationTuple(self, layer):
        sets = len(self.HookOrientationComboBoxList[layer - 1])
        hook_orientation_list = []
        for i in range(0, sets):
            if self.HookOrientationComboBoxList[layer - 1][i].isEnabled():
                hook_orientation_list.append(
                    self.HookOrientationComboBoxList[layer - 1][i].currentText()
                )
            else:
                hook_orientation_list.append(None)
        return tuple(hook_orientation_list)


def runHookOrientationEditDialog(self, hook_orientation_tuple):
    dialog = _HookOrientationEditDialog(hook_orientation_tuple)
    dialog.setupUi()
    dialog.form.exec_()
    self.HookOrientationTuple = dialog.HookOrientationTuple
