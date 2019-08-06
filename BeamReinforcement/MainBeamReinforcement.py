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

__title__ = "Beam Reinforcement"
__author__ = "Suraj"
__url__ = "https://www.freecadweb.org"

import os
from PySide2 import QtWidgets

import FreeCAD
import FreeCADGui

from Rebarfunc import check_selected_face

class _BeamReinforcementDialog:
    def __init__(self, RebarGroup=None):
        """This function set initial data in Beam Reinforcement dialog box."""
        self.CustomSpacing = None
        if not RebarGroup:
            # If beam reinforcement is not created yet, then get SelectedObj
            # from FreeCAD Gui selection
            selected_obj = FreeCADGui.Selection.getSelectionEx()[0]
            self.SelectedObj = selected_obj.Object
            self.FaceName = selected_obj.SubElementNames[0]

        # Load ui from file MainBeamReinforcement.ui
        self.form = FreeCADGui.PySideUic.loadUi(
            os.path.splitext(__file__)[0] + ".ui"
        )
        self.form.setWindowTitle(
            QtWidgets.QApplication.translate(
                "RebarAddon", "Beam Reinforcement", None
            )
        )
        self.RebarGroup = RebarGroup

    def setupUi(self):
        """This function is used to add components to ui."""
        # Add items into rebars_listWidget
        self.form.rebars_listWidget.addItem("Stirrups")
        self.form.rebars_listWidget.addItem("Top Reinforcement")
        self.form.rebars_listWidget.addItem("Bottom Reinforcement")
        self.form.rebars_listWidget.addItem("Left Reinforcement")
        self.form.rebars_listWidget.addItem("Right Reinforcement")
        self.form.rebars_listWidget.setCurrentRow(0)

def CommandBeamReinforcement():
    """This function is used to invoke dialog box for beam reinforcement."""
    selected_obj = check_selected_face()
    if selected_obj:
        dialog = _BeamReinforcementDialog()
        dialog.setupUi()
        dialog.form.exec_()
