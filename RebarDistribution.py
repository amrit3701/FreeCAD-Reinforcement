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

__title__ = "DialogDistribution"
__author__ = "Amritpal Singh"
__url__ = "https://www.freecadweb.org"

from PySide import QtGui
from Rebarfunc import getFaceNumber
import FreeCAD
import FreeCADGui
import ArchCommands
import os
import math


class _RebarDistributionDialog:
    def __init__(self, frontCover, size):
        self.FrontCover = frontCover
        self.ExpandingLength = size
        self.form = FreeCADGui.PySideUic.loadUi(
            os.path.splitext(__file__)[0] + ".ui"
        )
        self.form.setWindowTitle(
            QtGui.QApplication.translate("Arch", "Rebar Distribution", None)
        )
        self.form.image.setPixmap(
            QtGui.QPixmap(
                os.path.split(os.path.abspath(__file__))[0]
                + "/icons/RebarDistribution.svg"
            )
        )

    def accept(self):
        amount1 = self.form.amount1.value()
        spacing1 = self.form.spacing1.text()
        spacing1 = FreeCAD.Units.Quantity(spacing1).Value
        amount2 = self.form.amount2.value()
        spacing2 = self.form.spacing2.text()
        spacing2 = FreeCAD.Units.Quantity(spacing2).Value
        amount3 = self.form.amount3.value()
        spacing3 = self.form.spacing3.text()
        spacing3 = FreeCAD.Units.Quantity(spacing3).Value
        self.CustomSpacing = getCustomSpacingString(
            amount1,
            spacing1,
            amount2,
            spacing2,
            amount3,
            spacing3,
            self.FrontCover,
            self.ExpandingLength,
        )

    def setupUi(self, CustomSpacing):
        # Connect Signals and Slots
        self.form.buttonBox.accepted.connect(self.accept)
        self.form.buttonBox.rejected.connect(lambda: self.form.close())
        if CustomSpacing:
            spacingList = getupleOfCustomSpacing(CustomSpacing)
            if len(spacingList) >= 1:
                self.form.amount1.setValue(spacingList[0][0])
                self.form.spacing1.setText(f"{spacingList[0][1]} mm")
            else:
                self.form.amount1.setValue(0)
                self.form.spacing1.setText("0 mm")

            if len(spacingList) >= 2:
                self.form.amount2.setValue(spacingList[1][0])
                self.form.spacing2.setText(f"{spacingList[1][1]} mm")
            else:
                self.form.amount2.setValue(0)
                self.form.spacing2.setText("0 mm")

            if len(spacingList) == 3:
                self.form.amount3.setValue(spacingList[2][0])
                self.form.spacing3.setText(f"{spacingList[2][1]} mm")
            else:
                self.form.amount3.setValue(0)
                self.form.spacing3.setText("0 mm")


def getCustomSpacingString(
    amount1, spacing1, amount2, spacing2, amount3, spacing3, frontCover, size
):
    seg1_area = amount1 * spacing1 - spacing1 / 2
    seg3_area = amount3 * spacing3 - spacing3 / 2
    seg2_area = size - seg1_area - seg3_area - 2 * frontCover
    if seg2_area < 0:
        FreeCAD.Console.PrintError(
            "Sum of length of segment 1 and segment 2 is greater than length of"
            " rebar expands.\n"
        )
        return
    if spacing1 and spacing2 and spacing3 and amount1 and amount2 and amount3:
        pass
    else:
        if spacing1 and spacing2 and spacing3:
            amount2 = math.ceil(seg2_area / spacing2)
            spacing2 = seg2_area / amount2
        elif amount1 and amount2 and amount3:
            spacing2 = math.floor(seg2_area / amount2)
    CustomSpacing = (
        str(amount1)
        + "@"
        + str(spacing1)
        + "+"
        + str(int(amount2))
        + "@"
        + str(spacing2)
        + "+"
        + str(amount3)
        + "@"
        + str(spacing3)
    )
    return CustomSpacing


def getupleOfCustomSpacing(span_string):
    """gettupleOfCustomSpacing(span_string): This function take input
    in specific syntax and return output in the form of list. For eg.
    Input: "3@100+2@200+3@100"
    Output: [(3, 100), (2, 200), (3, 100)]"""

    span_st = span_string.strip()
    span_sp = span_st.split("+")
    index = 0
    spacinglist = []
    while index < len(span_sp):
        # Find "@" recursively in span_sp array.
        in_sp = span_sp[index].split("@")
        spacinglist.append((int(in_sp[0]), float(in_sp[1])))
        index += 1
    return spacinglist


def runRebarDistribution(self, frontCover=None):
    if frontCover is None:
        frontCover = self.form.frontCover.text()
        frontCover = FreeCAD.Units.Quantity(frontCover).Value
    face = self.SelectedObj.Shape.Faces[getFaceNumber(self.FaceName) - 1]
    size = (
        ArchCommands.projectToVector(
            self.SelectedObj.Shape.copy(), face.normalAt(0, 0)
        )
    ).Length
    dialog = _RebarDistributionDialog(frontCover, size)
    dialog.setupUi(self.CustomSpacing)
    dialog.form.exec_()
    try:
        self.CustomSpacing = dialog.CustomSpacing
    except AttributeError:
        pass


def removeRebarDistribution(self):
    self.CustomSpacing = ""
    self.Rebar.CustomSpacing = ""
    FreeCAD.ActiveDocument.recompute()
