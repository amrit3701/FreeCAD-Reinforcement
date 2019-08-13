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

__title__ = "Number Diameter Offset Edit Dialog"
__author__ = "Suraj"
__url__ = "https://www.freecadweb.org"


import os
from PySide2 import QtWidgets

import FreeCAD
import FreeCADGui

from Rebarfunc import gettupleOfNumberDiameterOffset


class _NumberDiameterOffsetDialog:
    def __init__(self, number_diameter_offset_string):
        self.NumberDiameterOffsetString = number_diameter_offset_string
        self.SetsDict = {}
        self.form = FreeCADGui.PySideUic.loadUi(
            os.path.splitext(__file__)[0] + ".ui"
        )
        self.form.setWindowTitle(
            QtWidgets.QApplication.translate(
                "Arch", "Rebar Number Diameter Offset Edit Dialog", None
            )
        )

    def setupUi(self):
        """This function is used to set values in ui."""
        self.connectSignalSlots()
        number_diameter_offset_tuple = gettupleOfNumberDiameterOffset(
            self.NumberDiameterOffsetString
        )
        sets = len(number_diameter_offset_tuple)
        for i in range(0, sets):
            self.addSetButtonClicked()
            _, number, diameter, offset, _ = self.SetsDict["set" + str(i + 1)]
            number.setValue(number_diameter_offset_tuple[i][0])
            diameter.setText(str(number_diameter_offset_tuple[i][1]) + "mm")
            offset.setText(str(number_diameter_offset_tuple[i][2]) + "mm")

    def connectSignalSlots(self):
        """This function is used to connect different slots in UI to appropriate
        functions."""
        self.form.addSetButton.clicked.connect(self.addSetButtonClicked)
        self.form.removeSetButton.clicked.connect(self.removeSetButtonClicked)
        self.form.buttonBox.accepted.connect(self.accept)
        self.form.buttonBox.rejected.connect(lambda: self.form.close())

    def addSetButtonClicked(self):
        sets = len(self.SetsDict)
        sets += 1
        self.SetsDict["set" + str(sets)] = []
        # Create horizontal layout and its components
        h_layout = QtWidgets.QHBoxLayout()
        set_label = QtWidgets.QLabel("Set " + str(sets))
        set_label.setSizePolicy(
            QtWidgets.QSizePolicy(
                QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed
            )
        )
        ui = FreeCADGui.UiLoader()
        number = ui.createWidget("Gui::PrefSpinBox")
        number.setSizePolicy(
            QtWidgets.QSizePolicy(
                QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed
            )
        )
        number.setMinimum(1)
        diameter = ui.createWidget("Gui::InputField")
        diameter.setSizePolicy(
            QtWidgets.QSizePolicy(
                QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed
            )
        )
        diameter.setProperty("unit", "mm")
        diameter.setText("16 mm")
        offset = ui.createWidget("Gui::InputField")
        offset.setSizePolicy(
            QtWidgets.QSizePolicy(
                QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed
            )
        )
        offset.setProperty("unit", "mm")
        offset.setText("20 mm")
        h_layout.addWidget(set_label)
        h_layout.addWidget(number)
        h_layout.addWidget(diameter)
        h_layout.addWidget(offset)
        v_layout = self.form.verticalLayout
        index = v_layout.indexOf(self.form.addSetButton)
        v_layout.insertLayout(index, h_layout)
        self.SetsDict["set" + str(sets)].append(set_label)
        self.SetsDict["set" + str(sets)].append(number)
        self.SetsDict["set" + str(sets)].append(diameter)
        self.SetsDict["set" + str(sets)].append(offset)
        self.SetsDict["set" + str(sets)].append(h_layout)
        if sets == 2:
            self.form.removeSetButton.setEnabled(True)

    def removeSetButtonClicked(self):
        sets = len(self.SetsDict)
        h_layout = self.SetsDict["set" + str(sets)][4]
        for i in reversed(range(0, len(self.SetsDict["set" + str(sets)]) - 1)):
            h_layout.removeWidget(self.SetsDict["set" + str(sets)][i])
            self.SetsDict["set" + str(sets)][i].deleteLater()
            del self.SetsDict["set" + str(sets)][i]
        self.form.verticalLayout.removeItem(h_layout)
        h_layout.deleteLater()
        del self.SetsDict["set" + str(sets)]
        sets -= 1
        if sets == 1:
            self.form.removeSetButton.setEnabled(False)

    def accept(self):
        """This function is executed when 'OK' button is clicked from ui."""
        sets = len(self.SetsDict)
        number_diameter_offset_string = ""
        for i in range(1, sets + 1):
            number = self.SetsDict["set" + str(i)][1].value()
            diameter = self.SetsDict["set" + str(i)][2].text()
            diameter = FreeCAD.Units.Quantity(diameter).Value
            offset = self.SetsDict["set" + str(i)][3].text()
            offset = FreeCAD.Units.Quantity(offset).Value
            number_diameter_offset_string += (
                str(number) + "#" + str(diameter) + "mm@" + str(offset) + "mm"
            )
            if i != sets:
                number_diameter_offset_string += "+"
        self.NumberDiameterOffsetString = number_diameter_offset_string
        self.form.close()


def runNumberDiameterOffsetDialog(self, number_diameter_offset_string):
    dialog = _NumberDiameterOffsetDialog(number_diameter_offset_string)
    dialog.setupUi()
    dialog.form.exec_()
    self.NumberDiameterOffsetString = dialog.NumberDiameterOffsetString
