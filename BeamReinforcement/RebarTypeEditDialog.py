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

from pathlib import Path

import FreeCADGui
from PySide import QtGui
from PySide.QtCore import QCoreApplication


class _RebarTypeEditDialog:
    def __init__(self, rebar_type_tuple):
        self.RebarTypeTuple = rebar_type_tuple
        self.Layers = []
        self.RebarTypeComboBoxList = []
        self.form = FreeCADGui.PySideUic.loadUi(
            str(Path(__file__).with_suffix(".ui"))
        )
        self.form.setWindowTitle(
            QCoreApplication.translate(
                "Arch", "Rebar Type Edit Dialog", None
            )
        )

    def setupUi(self):
        """This function is used to set values in ui."""
        self.connectSignalSlots()
        layers_count = len(self.RebarTypeTuple)
        sets_count_list = [len(x) for x in self.RebarTypeTuple]
        for layer in range(1, layers_count + 1):
            self.addLayer()
            for i in range(0, sets_count_list[layer - 1]):
                self.addSet()
                self.RebarTypeComboBoxList[layer - 1][i].setCurrentIndex(
                    self.RebarTypeComboBoxList[layer - 1][i].findText(
                        self.RebarTypeTuple[layer - 1][i]
                    )
                )

    def connectSignalSlots(self):
        """This function is used to connect different slots in UI to appropriate
        functions."""
        self.form.buttonBox.accepted.connect(self.accept)
        self.form.buttonBox.rejected.connect(lambda: self.form.close())

    def addLayer(self):
        layer = len(self.Layers) + 1
        layout = self.form.verticalLayout
        index = layout.indexOf(self.form.buttonBox)
        # Create Layer label
        layer_label = QtGui.QLabel("Layer" + str(layer) + ":")
        layer_label.setFont(QtGui.QFont("Sans", weight=QtGui.QFont.Bold))
        layout.insertWidget(index, layer_label)
        self.Layers.append(layer_label)
        self.RebarTypeComboBoxList.append([])

    def addSet(self):
        layer = len(self.Layers)
        sets = len(self.RebarTypeComboBoxList[layer - 1])
        # Create horizontal layout and its components
        h_layout = QtGui.QHBoxLayout()
        set_label = QtGui.QLabel("Set " + str(sets + 1))
        set_label.setSizePolicy(
            QtGui.QSizePolicy(
                QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed
            )
        )
        ui = FreeCADGui.UiLoader()
        rebar_type = ui.createWidget("Gui::PrefComboBox")
        rebar_type.addItems(["StraightRebar", "LShapeRebar"])
        h_layout.addWidget(set_label)
        h_layout.addWidget(rebar_type)
        v_layout = self.form.verticalLayout
        index = v_layout.indexOf(self.form.buttonBox)
        v_layout.insertLayout(index, h_layout)
        self.RebarTypeComboBoxList[layer - 1].append(rebar_type)

    def accept(self):
        """This function is executed when 'OK' button is clicked from ui."""
        layers = len(self.Layers)
        rebar_type_list = []
        for layer in range(1, layers + 1):
            rebar_type_list.append(self.getRebarTypeTuple(layer))
        self.RebarTypeTuple = tuple(rebar_type_list)
        self.form.close()

    def getRebarTypeTuple(self, layer):
        sets = len(self.RebarTypeComboBoxList[layer - 1])
        rebar_type_list = []
        for i in range(0, sets):
            rebar_type_list.append(
                self.RebarTypeComboBoxList[layer - 1][i].currentText()
            )
        return tuple(rebar_type_list)


def runRebarTypeEditDialog(self, rebar_type_tuple):
    dialog = _RebarTypeEditDialog(rebar_type_tuple)
    dialog.setupUi()
    dialog.form.exec_()
    self.RebarTypeTuple = dialog.RebarTypeTuple
