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

__title__ = "Rebar Type Edit Dialog"
__author__ = "Suraj"
__url__ = "https://www.freecadweb.org"

import os
from PySide2 import QtWidgets

import FreeCADGui


class _RebarTypeEditDialog:
    def __init__(self, rebar_type_tuple):
        self.RebarTypeTuple = rebar_type_tuple
        self.RebarTypeComboBoxList = []
        self.form = FreeCADGui.PySideUic.loadUi(
            os.path.splitext(__file__)[0] + ".ui"
        )
        self.form.setWindowTitle(
            QtWidgets.QApplication.translate(
                "Arch", "Rebar Type Edit Dialog", None
            )
        )

    def setupUi(self):
        """This function is used to set values in ui."""
        self.connectSignalSlots()
        sets = len(self.RebarTypeTuple)
        for i in range(0, sets):
            self.addSet()
            self.RebarTypeComboBoxList[i].setCurrentIndex(
                self.RebarTypeComboBoxList[i].findText(self.RebarTypeTuple[i])
            )

    def connectSignalSlots(self):
        """This function is used to connect different slots in UI to appropriate
        functions."""
        self.form.buttonBox.accepted.connect(self.accept)
        self.form.buttonBox.rejected.connect(lambda: self.form.close())

    def addSet(self):
        sets = len(self.RebarTypeComboBoxList)
        # Create Rebar Type Combo Box
        ui = FreeCADGui.UiLoader()
        rebar_type = ui.createWidget("Gui::PrefComboBox")
        rebar_type.addItems(["StraightRebar", "LShapeRebar"])
        form_layout = self.form.formLayout
        index = sets
        form_layout.insertRow(index, "Set " + str(sets + 1), rebar_type)
        self.RebarTypeComboBoxList.append(rebar_type)

    def accept(self):
        """This function is executed when 'OK' button is clicked from ui."""
        sets = len(self.RebarTypeComboBoxList)
        rebar_type_list = []
        for i in range(0, sets):
            rebar_type_list.append(self.RebarTypeComboBoxList[i].currentText())
        self.RebarTypeTuple = tuple(rebar_type_list)
        self.form.close()


def runRebarTypeEditDialog(self, rebar_type_tuple):
    dialog = _RebarTypeEditDialog(rebar_type_tuple)
    dialog.setupUi()
    dialog.form.exec_()
    self.RebarTypeTuple = dialog.RebarTypeTuple
