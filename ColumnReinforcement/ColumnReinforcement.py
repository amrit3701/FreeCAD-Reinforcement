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

__title__ = "Column Reinforcement"
__author__ = "Suraj"
__url__ = "https://www.freecadweb.org"

from RebarDistribution import runRebarDistribution, removeRebarDistribution
from Rebarfunc import getSelectedFace
from PySide import QtGui
import FreeCADGui
import os


class _ColumnTaskPanel:
    def __init__(self, Rebar=None):
        self.customSpacing = None
        if not Rebar:
            selected_obj = FreeCADGui.Selection.getSelectionEx()[0]
            self.SelectedObj = selected_obj.Object
            self.FaceName = selected_obj.SubElementNames[0]
        else:
            self.FaceName = Rebar.Base.Support[0][1][0]
            self.SelectedObj = Rebar.Base.Support[0][0]
        self.form = FreeCADGui.PySideUic.loadUi(os.path.splitext(__file__)[0] + ".ui")
        self.form.setWindowTitle(
            QtGui.QApplication.translate("RebarAddon", "Column Reinforcement", None)
        )
        self.form.image.setPixmap(
            QtGui.QPixmap(
                os.path.split(os.path.split(os.path.abspath(__file__))[0])[0]
                + "/icons/Column_CustomConfiguration.png"
            )
        )
        self.addDropdownMenuItems()
        self.connectSignalSlots()
        self.form.mainRebarOrientationWidget.hide()
        self.form.x_dirRebarOrientationWidget.hide()
        self.form.y_dirRebarOrientationWidget.hide()

    def addDropdownMenuItems(self):
        """ This function add dropdown items to each Gui::PrefComboBox."""
        self.form.columnConfiguration.addItems(
            ["Custom Configuration", "SingleTieFourRebars"]
        )
        self.form.bentAngle.addItems(["90", "135"])
        self.form.mainRebarType.addItems(["StraightRebar", "LShapeRebar"])
        self.form.x_dirRebarType.addItems(["StraightRebar", "LShapeRebar"])
        self.form.y_dirRebarType.addItems(["StraightRebar", "LShapeRebar"])
        hook_orientation_list = [
            "Top Inside",
            "Top Outside",
            "Top Left",
            "Top Right",
            "Bottom Inside",
            "Bottom Outside",
            "Bottom Left",
            "Bottom Right",
        ]
        self.form.mainRebarHookOrientation.addItems(hook_orientation_list)
        self.form.x_dirRebarHookOrientation.addItems(hook_orientation_list)
        self.form.y_dirRebarHookOrientation.addItems(hook_orientation_list)
        hook_extend_along_list = ["x-axis", "y-axis"]
        self.form.mainRebarHookExtendAlong.addItems(hook_extend_along_list)
        self.form.x_dirRebarHookExtendAlong.addItems(hook_extend_along_list)
        self.form.y_dirRebarHookExtendAlong.addItems(hook_extend_along_list)

    def connectSignalSlots(self):
        """ This function is used to connect different slots in UI to appropriate functions."""
        self.form.columnConfiguration.currentIndexChanged.connect(
            self.changeColumnConfiguration
        )
        self.form.number_radio.clicked.connect(self.number_radio_clicked)
        self.form.spacing_radio.clicked.connect(self.spacing_radio_clicked)
        self.form.mainRebarType.currentIndexChanged.connect(self.getMainRebarType)
        self.form.x_dirRebarType.currentIndexChanged.connect(self.getXDirRebarType)
        self.form.y_dirRebarType.currentIndexChanged.connect(self.getYDirRebarType)
        self.form.mainRebarHookExtendAlong.currentIndexChanged.connect(
            self.getHookExtendAlong
        )
        self.form.x_dirRebarHookExtendAlong.currentIndexChanged.connect(
            self.getHookExtendAlong
        )
        self.form.y_dirRebarHookExtendAlong.currentIndexChanged.connect(
            self.getHookExtendAlong
        )
        self.form.customSpacing.clicked.connect(lambda: runRebarDistribution(self))
        self.form.removeCustomSpacing.clicked.connect(
            lambda: removeRebarDistribution(self)
        )
        self.form.PickSelectedFace.clicked.connect(lambda: getSelectedFace(self))

    def getStandardButtons(self):
        """ This function add standard buttons to tool bar."""
        return (
            int(QtGui.QDialogButtonBox.Ok)
            | int(QtGui.QDialogButtonBox.Apply)
            | int(QtGui.QDialogButtonBox.Cancel)
            | int(QtGui.QDialogButtonBox.Help)
            | int(QtGui.QDialogButtonBox.Reset)
        )

    def changeColumnConfiguration(self):
        """ This function is used to find selected column configuration from UI and update UI accordingly."""
        column_configuration = self.form.columnConfiguration.currentText()
        if column_configuration == "Custom Configuration":
            self.form.image.setPixmap(
                QtGui.QPixmap(
                    os.path.split(os.path.split(os.path.abspath(__file__))[0])[0]
                    + "/icons/Column_CustomConfiguration.png"
                )
            )
            self.showXdirRebarsWidget()
            self.showYdirRebarsWidget()
        elif column_configuration == "SingleTieFourRebars":
            self.form.image.setPixmap(
                QtGui.QPixmap(
                    os.path.split(os.path.split(os.path.abspath(__file__))[0])[0]
                    + "/icons/Column_SingleTieFourRebars.png"
                )
            )
            self.hideXdirRebarsWidget()
            self.hideYdirRebarsWidget()

    def number_radio_clicked(self):
        """ This function enable number field and disable spacing field in UI when number radio button is clicked."""
        self.form.spacing.setEnabled(False)
        self.form.number.setEnabled(True)

    def spacing_radio_clicked(self):
        """ This function enable spacing field and disable number field in UI when spacing radio button is clicked."""
        self.form.number.setEnabled(False)
        self.form.spacing.setEnabled(True)

    def getMainRebarType(self):
        """ This function is used to find Main Rebars Type and update UI accordingly."""
        main_rebar_type = self.form.mainRebarType.currentText()
        if main_rebar_type == "LShapeRebar":
            self.form.mainRebarOrientationWidget.show()
        else:
            self.form.mainRebarOrientationWidget.hide()

    def getXDirRebarType(self):
        """ This function is used to find Rebar Type of rebars placed along X-Direction and update UI accordingly."""
        xdir_rebar_type = self.form.x_dirRebarType.currentText()
        if xdir_rebar_type == "LShapeRebar":
            self.form.x_dirRebarOrientationWidget.show()
        else:
            self.form.x_dirRebarOrientationWidget.hide()

    def getYDirRebarType(self):
        """ This function is used to find Rebar Type of rebars placed along Y-Direction and update UI accordingly."""
        ydir_rebar_type = self.form.y_dirRebarType.currentText()
        if ydir_rebar_type == "LShapeRebar":
            self.form.y_dirRebarOrientationWidget.show()
        else:
            self.form.y_dirRebarOrientationWidget.hide()

    def getHookExtendAlong(self):
        """ This function is used to find HookExtendAlong value from UI."""
        main_hook_extend_along = self.form.mainRebarHookExtendAlong.currentText()
        xdir_hook_extend_along = self.form.x_dirRebarHookExtendAlong.currentText()
        ydir_hook_extend_along = self.form.y_dirRebarHookExtendAlong.currentText()

    def hideXdirRebarsWidget(self):
        """ This function hide widget related to Rebars placed along X-Direction."""
        self.form.x_dirRebarsWidget.hide()

    def hideYdirRebarsWidget(self):
        """ This function hide widget related to Rebars placed along Y-Direction."""
        self.form.y_dirRebarsWidget.hide()

    def showXdirRebarsWidget(self):
        """ This function show widget related to Rebars placed along X-Direction."""
        self.form.x_dirRebarsWidget.show()

    def showYdirRebarsWidget(self):
        """ This function show widget related to Rebars placed along Y-Direction."""
        self.form.y_dirRebarsWidget.show()
