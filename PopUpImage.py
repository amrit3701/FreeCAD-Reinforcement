# -*- coding: utf-8 -*-
# ***************************************************************************
# *                                                                         *
# *   Copyright (c) 2017 - Amritpal Singh <amrit3701@gmail.com>             *
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

__title__ = "PopUpImage"
__author__ = "Amritpal Singh"
__url__ = "https://www.freecadweb.org"


from PySide import QtCore
from PySide import QtGui
from PySide import QtSvg
import FreeCADGui
import os

class PopUpImage(QtGui.QDialog):
   def __init__(self, img):
        QtGui.QDialog.__init__(self)
        self.image = QtSvg.QSvgWidget(img)
        self.setWindowTitle(QtGui.QApplication.translate("RebarTool", "Detailed description", None))
        self.verticalLayout = QtGui.QVBoxLayout(self)
        self.verticalLayout.addWidget(self.image)

def showPopUpImageDialog(img):
   """ showPopUpImageDialog(image): This function will show a given image in a pop-up
   dialog box."""
    ui = PopUpImage(img)
    ui.exec_()
