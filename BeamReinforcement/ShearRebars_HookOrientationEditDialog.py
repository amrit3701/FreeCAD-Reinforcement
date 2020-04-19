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
from PySide2 import QtWidgets

import FreeCADGui


class _HookOrientationEditDialog:
    def __init__(self, hook_orientation_tuple):
        self.HookOrientationTuple = hook_orientation_tuple
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
        sets = len(self.HookOrientationTuple)
        for i in range(0, sets):
            self.addSet()
            if self.HookOrientationTuple[i] is None:
                self.HookOrientationComboBoxList[i].setCurrentIndex(
                    self.HookOrientationComboBoxList[i].findText("Front Inside")
                )
                self.HookOrientationComboBoxList[i].setEnabled(False)
            else:
                self.HookOrientationComboBoxList[i].setCurrentIndex(
                    self.HookOrientationComboBoxList[i].findText(
                        self.HookOrientationTuple[i]
                    )
                )
                self.HookOrientationComboBoxList[i].setEnabled(True)

    def connectSignalSlots(self):
        """This function is used to connect different slots in UI to appropriate
        functions."""
        self.form.buttonBox.accepted.connect(self.accept)
        self.form.buttonBox.rejected.connect(lambda: self.form.close())

    def addSet(self):
        sets = len(self.HookOrientationComboBoxList)
        # Create Hook Orientation Combo Box
        ui = FreeCADGui.UiLoader()
        hook_orientation = ui.createWidget("Gui::PrefComboBox")
        hook_orientation.addItems(
            ["Front Inside", "Front Outside", "Rear Inside", "Rear Outside"]
        )
        form_layout = self.form.formLayout
        index = sets
        form_layout.insertRow(index, "Set " + str(sets + 1), hook_orientation)
        self.HookOrientationComboBoxList.append(hook_orientation)

    def accept(self):
        """This function is executed when 'OK' button is clicked from ui."""
        sets = len(self.HookOrientationComboBoxList)
        hook_orientation_list = []
        for i in range(0, sets):
            if self.HookOrientationComboBoxList[i].isEnabled():
                hook_orientation_list.append(
                    self.HookOrientationComboBoxList[i].currentText()
                )
            else:
                hook_orientation_list.append(None)
        self.HookOrientationTuple = tuple(hook_orientation_list)
        self.form.close()


def runHookOrientationEditDialog(self, hook_orientation_tuple):
    dialog = _HookOrientationEditDialog(hook_orientation_tuple)
    dialog.setupUi()
    dialog.form.exec_()
    self.HookOrientationTuple = dialog.HookOrientationTuple
