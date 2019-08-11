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
from PySide2 import QtWidgets, QtCore, QtGui

import FreeCADGui


class _RebarTypeEditDialog:
    def __init__(self, rebar_type_tuple):
        self.RebarTypeTuple = rebar_type_tuple
        self.Layers = []
        self.SetsDict = {}
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
        print("WIP")
        self.connectSignalSlots()
        layers_count = len(self.RebarTypeTuple)
        sets_count_list = [len(x) for x in self.RebarTypeTuple]
        for layer in range(1, layers_count + 1):
            self.addLayer()
            for i in range(0, sets_count_list[layer - 1]):
                self.addSet()

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
        layer_label = QtWidgets.QLabel("Layer" + str(layer) + ":")
        layer_label.setFont(QtGui.QFont("Sans", weight=QtGui.QFont.Bold))
        layout.insertWidget(index, layer_label)
        self.Layers.append(layer_label)
        self.SetsDict["layer" + str(layer)] = []
        print("WIP")

    def addSet(self):
        layer = len(self.Layers)
        sets = len(self.SetsDict["layer" + str(layer)])
        self.SetsDict["layer" + str(layer)].append([])
        # Create horizontal layout and its components
        h_layout = QtWidgets.QHBoxLayout()
        set_label = QtWidgets.QLabel("Set " + str(sets + 1))
        set_label.setSizePolicy(
            QtWidgets.QSizePolicy(
                QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed
            )
        )
        ui = FreeCADGui.UiLoader()
        rebar_type = ui.createWidget("Gui::PrefComboBox")
        h_layout.addWidget(set_label)
        h_layout.addWidget(rebar_type)
        v_layout = self.form.verticalLayout
        index = v_layout.indexOf(self.form.buttonBox)
        v_layout.insertLayout(index, h_layout)
        self.SetsDict["layer" + str(layer)][-1].append(set_label)
        self.SetsDict["layer" + str(layer)][-1].append(rebar_type)
        print("WIP")

    def accept(self):
        """This function is executed when 'OK' button is clicked from ui."""
        print("WIP")
        self.form.close()


def runRebarTypeEditDialog(self, number_diameter_offset, rebar_type_tuple):
    if isinstance(number_diameter_offset, str):
        number_diameter_offset = (number_diameter_offset,)

    layers = len(number_diameter_offset)
    rebar_type_list = []
    for layer in range(1, layers + 1):
        rebar_type_list.append([])
        for i in range(0, len(number_diameter_offset[layer - 1].split("+"))):
            if len(rebar_type_tuple) >= layer:
                if len(rebar_type_tuple[layer - 1]) > i:
                    rebar_type_list[-1].append(rebar_type_tuple[layer - 1][i])
                else:
                    rebar_type_list[-1].append("StraightRebar")
            else:
                rebar_type_list[-1].append("StraightRebar")
        rebar_type_list[-1] = tuple(rebar_type_list[-1])

    dialog = _RebarTypeEditDialog(tuple(rebar_type_list))
    dialog.setupUi()
    dialog.form.exec_()
    self.RebarTypeTuple = dialog.RebarTypeTuple
