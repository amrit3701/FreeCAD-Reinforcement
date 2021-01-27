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

from pathlib import Path

import FreeCADGui
from PySide2 import QtWidgets


class _RoundingEditDialog:
    def __init__(self, rounding_tuple):
        self.RoundingTuple = rounding_tuple
        self.RoundingSpinBoxList = []
        self.form = FreeCADGui.PySideUic.loadUi(
            str(Path(__file__).with_suffix(".ui"))
        )
        self.form.setWindowTitle(
            QtWidgets.QApplication.translate(
                "Arch", "Rounding Edit Dialog", None
            )
        )

    def setupUi(self):
        """This function is used to set values in ui."""
        self.connectSignalSlots()
        sets = len(self.RoundingTuple)
        for i in range(0, sets):
            self.addSet()
            if self.RoundingTuple[i] is None:
                self.RoundingSpinBoxList[i].setValue(2)
                self.RoundingSpinBoxList[i].setEnabled(False)
            else:
                self.RoundingSpinBoxList[i].setValue(self.RoundingTuple[i])
                self.RoundingSpinBoxList[i].setEnabled(True)

    def connectSignalSlots(self):
        """This function is used to connect different slots in UI to appropriate
        functions."""
        self.form.buttonBox.accepted.connect(self.accept)
        self.form.buttonBox.rejected.connect(lambda: self.form.close())

    def addSet(self):
        sets = len(self.RoundingSpinBoxList)
        # Create Rounding Combo Box
        ui = FreeCADGui.UiLoader()
        rounding = ui.createWidget("Gui::PrefSpinBox")
        rounding.setValue(2)
        form_layout = self.form.formLayout
        index = sets
        form_layout.insertRow(index, "Set " + str(sets + 1), rounding)
        self.RoundingSpinBoxList.append(rounding)

    def accept(self):
        """This function is executed when 'OK' button is clicked from ui."""
        sets = len(self.RoundingSpinBoxList)
        rounding_list = []
        for i in range(0, sets):
            if self.RoundingSpinBoxList[i].isEnabled():
                rounding_list.append(self.RoundingSpinBoxList[i].value())
            else:
                rounding_list.append(None)
        self.RoundingTuple = tuple(rounding_list)
        self.form.close()


def runRoundingEditDialog(self, rounding_tuple):
    dialog = _RoundingEditDialog(rounding_tuple)
    dialog.setupUi()
    dialog.form.exec_()
    self.RoundingTuple = dialog.RoundingTuple
