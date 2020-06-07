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

import os
from PySide2 import QtWidgets

import FreeCAD
import FreeCADGui


class _HookExtensionEditDialog:
    def __init__(self, hook_extension_tuple):
        self.HookExtensionTuple = hook_extension_tuple
        self.HookExtensionInputFieldList = []
        self.form = FreeCADGui.PySideUic.loadUi(
            os.path.splitext(__file__)[0] + ".ui"
        )
        self.form.setWindowTitle(
            QtWidgets.QApplication.translate(
                "Arch", "Hook Extension Edit Dialog", None
            )
        )

    def setupUi(self):
        """This function is used to set values in ui."""
        self.connectSignalSlots()
        sets = len(self.HookExtensionTuple)
        for i in range(0, sets):
            self.addSet()
            if self.HookExtensionTuple[i] is None:
                self.HookExtensionInputFieldList[i].setText("40 mm")
                self.HookExtensionInputFieldList[i].setEnabled(False)
            else:
                self.HookExtensionInputFieldList[i].setText(
                    str(self.HookExtensionTuple[i])
                )
                self.HookExtensionInputFieldList[i].setEnabled(True)

    def connectSignalSlots(self):
        """This function is used to connect different slots in UI to appropriate
        functions."""
        self.form.buttonBox.accepted.connect(self.accept)
        self.form.buttonBox.rejected.connect(lambda: self.form.close())

    def addSet(self):
        sets = len(self.HookExtensionInputFieldList)
        # Create Hook Extension Combo Box
        ui = FreeCADGui.UiLoader()
        hook_extension = ui.createWidget("Gui::InputField")
        hook_extension.setProperty("unit", "mm")
        hook_extension.setProperty("minimum", 10)
        hook_extension.setText("40 mm")
        form_layout = self.form.formLayout
        index = sets
        form_layout.insertRow(index, "Set " + str(sets + 1), hook_extension)
        self.HookExtensionInputFieldList.append(hook_extension)

    def accept(self):
        """This function is executed when 'OK' button is clicked from ui."""
        sets = len(self.HookExtensionInputFieldList)
        hook_extension_list = []
        for i in range(0, sets):
            if self.HookExtensionInputFieldList[i].isEnabled():
                hook_extension = self.HookExtensionInputFieldList[i].text()
                hook_extension = FreeCAD.Units.Quantity(hook_extension).Value
                hook_extension_list.append(hook_extension)
            else:
                hook_extension_list.append(None)
        self.HookExtensionTuple = tuple(hook_extension_list)
        self.form.close()


def runHookExtensionEditDialog(self, hook_extension_tuple):
    dialog = _HookExtensionEditDialog(hook_extension_tuple)
    dialog.setupUi()
    dialog.form.exec_()
    self.HookExtensionTuple = dialog.HookExtensionTuple
