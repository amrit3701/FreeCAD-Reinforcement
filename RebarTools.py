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

__title__ = "RebarCommands"
__author__ = "Amritpal Singh"
__url__ = "https://www.freecadweb.org"

import os

import FreeCADGui
from PySide.QtCore import QT_TRANSLATE_NOOP


class StraightRebarTool:
    @staticmethod
    def GetResources():
        return {
            "Pixmap": os.path.split(os.path.abspath(__file__))[0]
            + "/icons/dropdown_list/StraightRebar.svg",
            "MenuText": QT_TRANSLATE_NOOP(
                "Arch_Rebar_Straight", "Straight Rebar"
            ),
            "ToolTip": QT_TRANSLATE_NOOP(
                "Arch_Rebar_Straight",
                "Creates a Straight bar reinforcement from the selected face of"
                " the Structural element.",
            ),
        }

    @staticmethod
    def IsActive():
        return True if FreeCADGui.activeDocument() else False

    @staticmethod
    def Activated():
        import StraightRebar

        # Call to CommandStraightRebar() function
        StraightRebar.CommandStraightRebar()


class UShapeRebarTool:
    @staticmethod
    def GetResources():
        return {
            "Pixmap": os.path.split(os.path.abspath(__file__))[0]
            + "/icons/dropdown_list/UShapeRebar.svg",
            "MenuText": QT_TRANSLATE_NOOP("Arch_Rebar_UShape", "U-Shape Rebar"),
            "ToolTip": QT_TRANSLATE_NOOP(
                "Arch_Rebar_UShape",
                "Creates a U-Shape bar reinforcement from the selected face of "
                "the Structural element.",
            ),
        }

    @staticmethod
    def IsActive():
        return True if FreeCADGui.activeDocument() else False

    @staticmethod
    def Activated():
        import UShapeRebar

        # Call to CommandUShapeRebar() function
        UShapeRebar.CommandUShapeRebar()


class LShapeRebarTool:
    @staticmethod
    def GetResources():
        return {
            "Pixmap": os.path.split(os.path.abspath(__file__))[0]
            + "/icons/dropdown_list/LShapeRebar.svg",
            "MenuText": QT_TRANSLATE_NOOP("Arch_Rebar_LShape", "L-Shape Rebar"),
            "ToolTip": QT_TRANSLATE_NOOP(
                "Arch_Rebar_LShape",
                "Creates a L-Shape bar reinforcement from the selected face of "
                "the Structural element.",
            ),
        }

    @staticmethod
    def IsActive():
        return True if FreeCADGui.activeDocument() else False

    @staticmethod
    def Activated():
        import LShapeRebar

        # Call to CommandUShapeRebar() function
        LShapeRebar.CommandLShapeRebar()


class StirrupTool:
    @staticmethod
    def GetResources():
        return {
            "Pixmap": os.path.split(os.path.abspath(__file__))[0]
            + "/icons/dropdown_list/StirrupRebar.svg",
            "MenuText": QT_TRANSLATE_NOOP("Arch_Rebar_Stirrup", "Stirrup"),
            "ToolTip": QT_TRANSLATE_NOOP(
                "Arch_Rebar_Stirrup",
                "Creates a Stirrup bar reinforcement from the selected face of "
                "the Structural element.",
            ),
        }

    @staticmethod
    def IsActive():
        return True if FreeCADGui.activeDocument() else False

    @staticmethod
    def Activated():
        import Stirrup

        # Call to CommandStirrup() function
        Stirrup.CommandStirrup()


class BentShapeRebarTool:
    @staticmethod
    def GetResources():
        return {
            "Pixmap": os.path.split(os.path.abspath(__file__))[0]
            + "/icons/dropdown_list/BentShapeRebar.svg",
            "MenuText": QT_TRANSLATE_NOOP(
                "Arch_Rebar_BentShape", "Bent-Shape Rebar"
            ),
            "ToolTip": QT_TRANSLATE_NOOP(
                "Arch_Rebar_BentShape",
                "Creates a BentShape bar reinforcement from the selected face "
                "of the Structural element.",
            ),
        }

    @staticmethod
    def IsActive():
        return True if FreeCADGui.activeDocument() else False

    @staticmethod
    def Activated():
        import BentShapeRebar

        # Call to CommandBentShapeRebar() function
        BentShapeRebar.CommandBentShapeRebar()


class HelicalRebarTool:
    @staticmethod
    def GetResources():
        return {
            "Pixmap": os.path.split(os.path.abspath(__file__))[0]
            + "/icons/dropdown_list/HelixShapeRebar.svg",
            "MenuText": QT_TRANSLATE_NOOP(
                "Arch_Rebar_Helical", "Helical Rebar"
            ),
            "ToolTip": QT_TRANSLATE_NOOP(
                "Arch_Rebar_Helical",
                "Creates a Helical bar reinforcement from the selected face of "
                "the Structural element.",
            ),
        }

    @staticmethod
    def IsActive():
        return True if FreeCADGui.activeDocument() else False

    @staticmethod
    def Activated():
        import HelicalRebar

        # Call to CommandHelicalRebar() function
        HelicalRebar.CommandHelicalRebar()


class ColumnReinforcementTool:
    @staticmethod
    def GetResources():
        return {
            "Pixmap": os.path.split(os.path.abspath(__file__))[0]
            + "/icons/dropdown_list/Column.svg",
            "MenuText": QT_TRANSLATE_NOOP(
                "Arch_Column_Reinforcement", "Column Reinforcement"
            ),
            "ToolTip": QT_TRANSLATE_NOOP(
                "Arch_Column_Reinforcement",
                "Creates a Column Reinforcement from the selected face of the "
                "Structural element.",
            ),
        }

    @staticmethod
    def IsActive():
        return True if FreeCADGui.activeDocument() else False

    @staticmethod
    def Activated():
        from ColumnReinforcement import MainColumnReinforcement

        # Call to CommandColumnReinforcement() function
        MainColumnReinforcement.CommandColumnReinforcement()


class BeamReinforcementTool:
    @staticmethod
    def GetResources():
        return {
            "Pixmap": os.path.split(os.path.abspath(__file__))[0]
            + "/icons/dropdown_list/Beam.svg",
            "MenuText": QT_TRANSLATE_NOOP(
                "Arch_Beam_Reinforcement", "Beam Reinforcement"
            ),
            "ToolTip": QT_TRANSLATE_NOOP(
                "Arch_Beam_Reinforcement",
                "Creates a Beam Reinforcement from the selected face of the "
                "Structural element.",
            ),
        }

    @staticmethod
    def IsActive():
        return True if FreeCADGui.activeDocument() else False

    @staticmethod
    def Activated():
        from BeamReinforcement import MainBeamReinforcement

        # Call to CommandBeamReinforcement() function
        MainBeamReinforcement.CommandBeamReinforcement()


class BillOfMaterialTool:
    @staticmethod
    def GetResources():
        return {
            "Pixmap": os.path.split(os.path.abspath(__file__))[0]
            + "/icons/dropdown_list/BOM.svg",
            "MenuText": QT_TRANSLATE_NOOP(
                "Arch_Rebar_BOM", "Rebar Bill Of Material"
            ),
            "ToolTip": QT_TRANSLATE_NOOP(
                "Arch_Rebar_BOM", "Generate Rebars Bill Of Material",
            ),
        }

    @staticmethod
    def IsActive():
        return True if FreeCADGui.activeDocument() else False

    @staticmethod
    def Activated():
        from BillOfMaterial import MainBillOfMaterial

        # Call to CommandBillOfMaterial() function
        MainBillOfMaterial.CommandBillOfMaterial()


class RebarShapeCutListTool:
    @staticmethod
    def GetResources():
        return {
            "Pixmap": os.path.split(os.path.abspath(__file__))[0]
            + "/icons/dropdown_list/RebarShapeCutList.svg",
            "MenuText": QT_TRANSLATE_NOOP(
                "Reinforcement_Bar_Shape_Cut_List", "Rebar Shape Cut List"
            ),
            "ToolTip": QT_TRANSLATE_NOOP(
                "Reinforcement_Bar_Shape_Cut_List",
                "Generate Rebar Shape Cut List",
            ),
        }

    @staticmethod
    def IsActive():
        return True if FreeCADGui.activeDocument() else False

    @staticmethod
    def Activated():
        from RebarShapeCutList import MainRebarShapeCutList

        # Call to CommandRebarShapeCutList() function
        MainRebarShapeCutList.CommandRebarShapeCutList()


class BarBendingScheduleTool:
    @staticmethod
    def GetResources():
        return {
            "Pixmap": os.path.split(os.path.abspath(__file__))[0]
            + "/icons/dropdown_list/BarBendingSchedule.svg",
            "MenuText": QT_TRANSLATE_NOOP(
                "Reinforcement_Bar_Bending_Schedule", "Bar Bending " "Schedule"
            ),
            "ToolTip": QT_TRANSLATE_NOOP(
                "Reinforcement_Bar_Bending_Schedule",
                "Generate Bar Bending Schedule",
            ),
        }

    @staticmethod
    def IsActive():
        return True if FreeCADGui.activeDocument() else False

    @staticmethod
    def Activated():
        from BarBendingSchedule import MainBarBendingSchedule

        # Call to CommandBarBendingSchedule() function
        MainBarBendingSchedule.CommandBarBendingSchedule()


def updateLocale():
    FreeCADGui.addLanguagePath(
        os.path.join(os.path.dirname(__file__), "translations")
    )
    FreeCADGui.updateLocale()


FreeCADGui.addCommand("Arch_Rebar_Straight", StraightRebarTool())
FreeCADGui.addCommand("Arch_Rebar_UShape", UShapeRebarTool())
FreeCADGui.addCommand("Arch_Rebar_LShape", LShapeRebarTool())
FreeCADGui.addCommand("Arch_Rebar_Stirrup", StirrupTool())
FreeCADGui.addCommand("Arch_Rebar_BentShape", BentShapeRebarTool())
FreeCADGui.addCommand("Arch_Rebar_Helical", HelicalRebarTool())
FreeCADGui.addCommand("Arch_Column_Reinforcement", ColumnReinforcementTool())
FreeCADGui.addCommand("Arch_Beam_Reinforcement", BeamReinforcementTool())
FreeCADGui.addCommand("Arch_Rebar_BOM", BillOfMaterialTool())
FreeCADGui.addCommand(
    "Reinforcement_Bar_Shape_Cut_List", RebarShapeCutListTool()
)
FreeCADGui.addCommand(
    "Reinforcement_Bar_Bending_Schedule", BarBendingScheduleTool()
)


# List of all rebar commands
RebarCommands = [
    "Arch_Rebar_Straight",
    "Arch_Rebar_UShape",
    "Arch_Rebar_LShape",
    "Arch_Rebar_Stirrup",
    "Arch_Rebar_BentShape",
    "Arch_Rebar_Helical",
    "Arch_Column_Reinforcement",
    "Arch_Beam_Reinforcement",
    "Arch_Rebar_BOM",
    "Reinforcement_Bar_Shape_Cut_List",
    "Reinforcement_Bar_Bending_Schedule",
]
