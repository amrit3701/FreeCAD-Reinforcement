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

__title__ = "Hook Extension Edit Dialog"
__author__ = "Suraj"
__url__ = "https://www.freecadweb.org"

from pathlib import Path

import FreeCAD
import FreeCADGui
from PySide import QtGui
from PySide.QtCore import QCoreApplication


class _HookExtensionEditDialog:
    def __init__(self, hook_extension_tuple):
        self.HookExtensionTuple = hook_extension_tuple
        self.Layers = []
        self.HookExtensionInputFieldList = []
        self.form = FreeCADGui.PySideUic.loadUi(
            str(Path(__file__).with_suffix(".ui"))
        )
        self.form.setWindowTitle(
            QCoreApplication.translate(
                "Arch", "Hook Extension Edit Dialog", None
            )
        )

    def setupUi(self):
        """This function is used to set values in ui."""
        self.connectSignalSlots()
        layers_count = len(self.HookExtensionTuple)
        sets_count_list = [len(x) for x in self.HookExtensionTuple]
        for layer in range(1, layers_count + 1):
            self.addLayer()
            for i in range(0, sets_count_list[layer - 1]):
                self.addSet()
                if self.HookExtensionTuple[layer - 1][i] is None:
                    self.HookExtensionInputFieldList[layer - 1][i].setText(
                        FreeCAD.Units.Quantity(
                            40.0, FreeCAD.Units.Length
                        ).UserString
                    )
                    self.HookExtensionInputFieldList[layer - 1][i].setEnabled(
                        False
                    )
                else:
                    self.HookExtensionInputFieldList[layer - 1][i].setText(
                        FreeCAD.Units.Quantity(
                            self.HookExtensionTuple[layer - 1][i],
                            FreeCAD.Units.Length,
                        ).UserString
                    )
                    self.HookExtensionInputFieldList[layer - 1][i].setEnabled(
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
        layer_label = QtGui.QLabel("Layer" + str(layer) + ":")
        layer_label.setFont(QtGui.QFont("Sans", weight=QtGui.QFont.Bold))
        layout.insertWidget(index, layer_label)
        self.Layers.append(layer_label)
        self.HookExtensionInputFieldList.append([])

    def addSet(self):
        layer = len(self.Layers)
        sets = len(self.HookExtensionInputFieldList[layer - 1])
        # Create horizontal layout and its components
        h_layout = QtGui.QHBoxLayout()
        set_label = QtGui.QLabel("Set " + str(sets + 1))
        set_label.setSizePolicy(
            QtGui.QSizePolicy(
                QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed
            )
        )
        ui = FreeCADGui.UiLoader()
        hook_extension = ui.createWidget("Gui::InputField")
        hook_extension.setProperty("unit", "mm")
        hook_extension.setProperty("minimum", 10)
        hook_extension.setText(
            FreeCAD.Units.Quantity(40.0, FreeCAD.Units.Length).UserString
        )
        h_layout.addWidget(set_label)
        h_layout.addWidget(hook_extension)
        v_layout = self.form.verticalLayout
        index = v_layout.indexOf(self.form.buttonBox)
        v_layout.insertLayout(index, h_layout)
        self.HookExtensionInputFieldList[layer - 1].append(hook_extension)

    def accept(self):
        """This function is executed when 'OK' button is clicked from ui."""
        layers = len(self.Layers)
        hook_extension_list = []
        for layer in range(1, layers + 1):
            hook_extension_list.append(self.getHookExtensionTuple(layer))
        self.HookExtensionTuple = tuple(hook_extension_list)
        self.form.close()

    def getHookExtensionTuple(self, layer):
        sets = len(self.HookExtensionInputFieldList[layer - 1])
        hook_extension_list = []
        for i in range(0, sets):
            if self.HookExtensionInputFieldList[layer - 1][i].isEnabled():
                hook_extension = self.HookExtensionInputFieldList[layer - 1][
                    i
                ].text()
                hook_extension = FreeCAD.Units.Quantity(hook_extension).Value
                hook_extension_list.append(hook_extension)
            else:
                hook_extension_list.append(None)
        return tuple(hook_extension_list)


def runHookExtensionEditDialog(self, hook_extension_tuple):
    dialog = _HookExtensionEditDialog(hook_extension_tuple)
    dialog.setupUi()
    dialog.form.exec_()
    self.HookExtensionTuple = dialog.HookExtensionTuple
