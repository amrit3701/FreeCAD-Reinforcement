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

__title__ = "Number Diameter Offset Dialog"
__author__ = "Suraj"
__url__ = "https://www.freecadweb.org"


import os
from PySide2 import QtWidgets

import FreeCADGui


class _NumberDiameterOffsetDialog:
    def __init__(self, number_diameter_offset_tuple):
        self.NumberDiameterOffsetTuple = number_diameter_offset_tuple
        self.form = FreeCADGui.PySideUic.loadUi(
            os.path.splitext(__file__)[0] + ".ui"
        )
        self.form.setWindowTitle(
            QtWidgets.QApplication.translate(
                "Arch", "Rebar Number Diameter Offset", None
            )
        )

    def setupUi(self):
        """This function is used to set values in ui."""
        self.form.scrollArea.setWidget(self.form.dataWidget)
        self.connectSignalSlots()
        print("WIP")

    def connectSignalSlots(self):
        """This function is used to connect different slots in UI to appropriate
        functions."""
        self.form.buttonBox.accepted.connect(self.accept)
        self.form.buttonBox.rejected.connect(lambda: self.form.close())

    def accept(self):
        """This function is executed when 'OK' button is clicked from ui."""
        print("WIP")
        self.form.close()


def runNumberDiameterOffsetDialog(self, number_diameter_offset):
    if isinstance(number_diameter_offset, str):
        number_diameter_offset = (number_diameter_offset,)
    dialog = _NumberDiameterOffsetDialog(number_diameter_offset)
    dialog.setupUi()
    dialog.form.exec_()
    self.NumberDiameterOffsetTuple = dialog.NumberDiameterOffsetTuple
    print("WIP")
