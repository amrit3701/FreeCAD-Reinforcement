# -*- coding: utf-8 -*-
# ***************************************************************************
# *                                                                         *
# *   Copyright (c) 2020 - Suraj <dadralj18@gmail.com>                      *
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

__title__ = "Unit QLineEdit Widget"
__author__ = "Suraj"
__url__ = "https://www.freecadweb.org"


from PySide2 import QtWidgets
import FreeCAD


class UnitLineEdit(QtWidgets.QLineEdit):
    def __init__(self, contents="", parent=None):
        super().__init__(contents, parent)
        self.textEdited.connect(self.unitEdited)

    def unitEdited(self):
        if self.isValidUnit():
            self.setStyleSheet("color: black;")
        else:
            self.setStyleSheet("color: red;")

    def isValidUnit(self):
        try:
            FreeCAD.Units.Quantity(self.text())
            return True
        except ValueError:
            return False
