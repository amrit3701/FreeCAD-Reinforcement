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

__title__ = "Number Diameter Dialog"
__author__ = "Suraj"
__url__ = "https://www.freecadweb.org"

from pathlib import Path

import FreeCAD
import FreeCADGui
from PySide.QtCore import QCoreApplication

from Rebarfunc import gettupleOfNumberDiameter


class _NumberDiameterDialog:
    def __init__(self, rebars_widget):
        """This function set initial data in Rebar Number Dialog dialog box."""
        self.rebars_widget = rebars_widget
        self.form = FreeCADGui.PySideUic.loadUi(
            str(Path(__file__).with_suffix(".ui"))
        )
        self.form.setWindowTitle(
            QCoreApplication.translate(
                "RebarAddon", "Rebar Number Diameter", None
            )
        )

    def setupUi(self):
        """This function is used to set values in ui."""
        # Set values of number and diameter from rebars_widget
        self.NumberDiameter = self.rebars_widget.numberDiameter.text()
        number_diameter_list = gettupleOfNumberDiameter(self.NumberDiameter)
        number_diameter_list.extend(
            [(0, 0) for _ in range(3 - len(number_diameter_list))]
        )
        self.form.number1.setValue(number_diameter_list[0][0])
        self.form.diameter1.setText(str(number_diameter_list[0][1]) + " mm")
        self.form.number2.setValue(number_diameter_list[1][0])
        self.form.diameter2.setText(str(number_diameter_list[1][1]) + " mm")
        self.form.number3.setValue(number_diameter_list[2][0])
        self.form.diameter3.setText(str(number_diameter_list[2][1]) + " mm")
        self.form.numberDiameter.setText(self.NumberDiameter)
        self.connectSignalSlots()

    def connectSignalSlots(self):
        """This function is used to connect different slots in UI to appropriate
        functions."""
        self.form.number1.valueChanged.connect(self.setNumberDiameterString)
        self.form.diameter1.textChanged.connect(self.setNumberDiameterString)
        self.form.number2.valueChanged.connect(self.setNumberDiameterString)
        self.form.diameter2.textChanged.connect(self.setNumberDiameterString)
        self.form.number3.valueChanged.connect(self.setNumberDiameterString)
        self.form.diameter3.textChanged.connect(self.setNumberDiameterString)
        self.form.buttonBox.accepted.connect(self.accept)
        self.form.buttonBox.rejected.connect(lambda: self.form.close())

    def accept(self):
        """This function is executed when 'OK' button is clicked from ui. It
        sets value of Number#Diameter in rebars_widget."""
        self.NumberDiameter = self.form.numberDiameter.text()
        self.rebars_widget.numberDiameter.setText(self.NumberDiameter)
        self.form.close()

    def setNumberDiameterString(self):
        """This function is used to obtain Number#Diameter string from sets of
        number and diameter. And set it in ui."""
        number1 = self.form.number1.value()
        diameter1 = self.form.diameter1.text()
        diameter1 = FreeCAD.Units.Quantity(diameter1).Value
        number2 = self.form.number2.value()
        diameter2 = self.form.diameter2.text()
        diameter2 = FreeCAD.Units.Quantity(diameter2).Value
        number3 = self.form.number3.value()
        diameter3 = self.form.diameter3.text()
        diameter3 = FreeCAD.Units.Quantity(diameter3).Value
        self.NumberDiameter = (
            str(number1)
            + "#"
            + str(diameter1)
            + "mm+"
            + str(number2)
            + "#"
            + str(diameter2)
            + "mm+"
            + str(number3)
            + "#"
            + str(diameter3)
            + "mm"
        )
        self.form.numberDiameter.setText(self.NumberDiameter)


def runNumberDiameterDialog(rebars_widget):
    dialog = _NumberDiameterDialog(rebars_widget)
    dialog.setupUi()
    dialog.form.exec_()
