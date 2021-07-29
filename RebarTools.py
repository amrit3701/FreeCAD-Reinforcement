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

from pathlib import Path

import FreeCADGui
from PySide.QtCore import QT_TRANSLATE_NOOP


class StraightRebarTool:
    @staticmethod
    def GetResources():
        return {
            "Pixmap": str(
                Path(__file__).parent
                / "icons"
                / "dropdown_list"
                / "StraightRebar.svg"
            ),
            "MenuText": QT_TRANSLATE_NOOP(
                "Reinforcement_StraightRebar", "Straight Rebar"
            ),
            "ToolTip": QT_TRANSLATE_NOOP(
                "Reinforcement_StraightRebar",
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
            "Pixmap": str(
                Path(__file__).parent
                / "icons"
                / "dropdown_list"
                / "UShapeRebar.svg"
            ),
            "MenuText": QT_TRANSLATE_NOOP(
                "Reinforcement_UShapeRebar", "U-Shape Rebar"
            ),
            "ToolTip": QT_TRANSLATE_NOOP(
                "Reinforcement_UShapeRebar",
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
            "Pixmap": str(
                Path(__file__).parent
                / "icons"
                / "dropdown_list"
                / "LShapeRebar.svg"
            ),
            "MenuText": QT_TRANSLATE_NOOP(
                "Reinforcement_LShapeRebar", "L-Shape Rebar"
            ),
            "ToolTip": QT_TRANSLATE_NOOP(
                "Reinforcement_LShapeRebar",
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
            "Pixmap": str(
                Path(__file__).parent
                / "icons"
                / "dropdown_list"
                / "StirrupRebar.svg"
            ),
            "MenuText": QT_TRANSLATE_NOOP(
                "Reinforcement_StirrupRebar", "Stirrup"
            ),
            "ToolTip": QT_TRANSLATE_NOOP(
                "Reinforcement_StirrupRebar",
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
            "Pixmap": str(
                Path(__file__).parent
                / "icons"
                / "dropdown_list"
                / "BentShapeRebar.svg"
            ),
            "MenuText": QT_TRANSLATE_NOOP(
                "Reinforcement_BentShapeRebar", "Bent-Shape Rebar"
            ),
            "ToolTip": QT_TRANSLATE_NOOP(
                "Reinforcement_BentShapeRebar",
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
            "Pixmap": str(
                Path(__file__).parent
                / "icons"
                / "dropdown_list"
                / "HelixShapeRebar.svg"
            ),
            "MenuText": QT_TRANSLATE_NOOP(
                "Reinforcement_HelicalRebar", "Helical Rebar"
            ),
            "ToolTip": QT_TRANSLATE_NOOP(
                "Reinforcement_HelicalRebar",
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
            "Pixmap": str(
                Path(__file__).parent / "icons" / "dropdown_list" / "Column.svg"
            ),
            "MenuText": QT_TRANSLATE_NOOP(
                "Reinforcement_ColumnRebars", "Column Reinforcement"
            ),
            "ToolTip": QT_TRANSLATE_NOOP(
                "Reinforcement_ColumnRebars",
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
            "Pixmap": str(
                Path(__file__).parent / "icons" / "dropdown_list" / "Beam.svg"
            ),
            "MenuText": QT_TRANSLATE_NOOP(
                "Reinforcement_BeamRebars", "Beam Reinforcement"
            ),
            "ToolTip": QT_TRANSLATE_NOOP(
                "Reinforcement_BeamRebars",
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


class SlabReinforcementTool:
    @staticmethod
    def GetResources():
        return {
            "Pixmap": str(
                Path(__file__).parent / "icons" / "SlabReinforcement.svg"
            ),
            "MenuText": QT_TRANSLATE_NOOP(
                "Reinforcement_SlabRebars", "Slab Reinforcement"
            ),
            "ToolTip": QT_TRANSLATE_NOOP(
                "Reinforcement_SlabRebars",
                "Creates a Slab Reinforcement from the selected face of the "
                "Structural element.",
            ),
        }

    @staticmethod
    def IsActive():
        return True if FreeCADGui.activeDocument() else False

    @staticmethod
    def Activated():
        from SlabReinforcement import MainSlabReinforcement

        # Call to CommandSlabReinforcement() function
        MainSlabReinforcement.CommandSlabReinforcement()


class BillOfMaterialTool:
    @staticmethod
    def GetResources():
        return {
            "Pixmap": str(
                Path(__file__).parent / "icons" / "dropdown_list" / "BOM.svg"
            ),
            "MenuText": QT_TRANSLATE_NOOP(
                "Reinforcement_BillOfMaterial", "Rebar Bill Of Material"
            ),
            "ToolTip": QT_TRANSLATE_NOOP(
                "Reinforcement_BillOfMaterial",
                "Generate Rebars Bill Of Material",
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
            "Pixmap": str(
                Path(__file__).parent
                / "icons"
                / "dropdown_list"
                / "RebarShapeCutList.svg"
            ),
            "MenuText": QT_TRANSLATE_NOOP(
                "Reinforcement_BarShapeCutList", "Rebar Shape Cut List"
            ),
            "ToolTip": QT_TRANSLATE_NOOP(
                "Reinforcement_BarShapeCutList",
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
            "Pixmap": str(
                Path(__file__).parent
                / "icons"
                / "dropdown_list"
                / "BarBendingSchedule.svg"
            ),
            "MenuText": QT_TRANSLATE_NOOP(
                "Reinforcement_BarBendingSchedule", "Bar Bending Schedule"
            ),
            "ToolTip": QT_TRANSLATE_NOOP(
                "Reinforcement_BarBendingSchedule",
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


class ReinforcementDrawingDimensioningTool:
    @staticmethod
    def GetResources():
        return {
            "Pixmap": str(
                Path(__file__).parent
                / "icons"
                / "dropdown_list"
                / "DrawingDimensioning.svg"
            ),
            "MenuText": QT_TRANSLATE_NOOP(
                "Reinforcement_DrawingDimensioning",
                "Reinforcement Drawing Dimensioning",
            ),
            "ToolTip": QT_TRANSLATE_NOOP(
                "Reinforcement_DrawingDimensioning",
                "Generate Reinforcement Drawing Dimensioning",
            ),
        }

    @staticmethod
    def IsActive():
        return True if FreeCADGui.activeDocument() else False

    @staticmethod
    def Activated():
        from ReinforcementDrawing.MainReinforcementDrawingDimensioning import (
            CommandReinforcementDrawingDimensioning,
        )

        CommandReinforcementDrawingDimensioning()


def updateLocale():
    FreeCADGui.addLanguagePath(str(Path(__file__).parent / "translations"))
    FreeCADGui.updateLocale()


FreeCADGui.addCommand("Reinforcement_StraightRebar", StraightRebarTool())
FreeCADGui.addCommand("Reinforcement_UShapeRebar", UShapeRebarTool())
FreeCADGui.addCommand("Reinforcement_LShapeRebar", LShapeRebarTool())
FreeCADGui.addCommand("Reinforcement_StirrupRebar", StirrupTool())
FreeCADGui.addCommand("Reinforcement_BentShapeRebar", BentShapeRebarTool())
FreeCADGui.addCommand("Reinforcement_HelicalRebar", HelicalRebarTool())
FreeCADGui.addCommand("Reinforcement_ColumnRebars", ColumnReinforcementTool())
FreeCADGui.addCommand("Reinforcement_BeamRebars", BeamReinforcementTool())
FreeCADGui.addCommand("Reinforcement_SlabRebars", SlabReinforcementTool())
FreeCADGui.addCommand("Reinforcement_BillOfMaterial", BillOfMaterialTool())
FreeCADGui.addCommand("Reinforcement_BarShapeCutList", RebarShapeCutListTool())
FreeCADGui.addCommand(
    "Reinforcement_BarBendingSchedule", BarBendingScheduleTool()
)
FreeCADGui.addCommand(
    "Reinforcement_DrawingDimensioning", ReinforcementDrawingDimensioningTool()
)


# List of all rebar commands
RebarCommands = [
    "Reinforcement_StraightRebar",
    "Reinforcement_UShapeRebar",
    "Reinforcement_LShapeRebar",
    "Reinforcement_StirrupRebar",
    "Reinforcement_BentShapeRebar",
    "Reinforcement_HelicalRebar",
    "Reinforcement_ColumnRebars",
    "Reinforcement_BeamRebars",
    "Reinforcement_SlabRebars",
]

# Initialize "Arch_Rebar" command
if "Arch_Rebar" not in FreeCADGui.listCommands():
    from ArchRebar import _CommandRebar

    FreeCADGui.addCommand("Arch_Rebar", _CommandRebar())

# List of all rebar commands to show in Reinforcement workbench tool bar
ReinforcementCommands = [
    "Reinforcement_StraightRebar",
    "Reinforcement_UShapeRebar",
    "Reinforcement_LShapeRebar",
    "Reinforcement_StirrupRebar",
    "Reinforcement_BentShapeRebar",
    "Reinforcement_HelicalRebar",
    "Reinforcement_ColumnRebars",
    "Reinforcement_BeamRebars",
    "Reinforcement_SlabRebars",
    "Arch_Rebar",
    "Reinforcement_BillOfMaterial",
    "Reinforcement_BarShapeCutList",
    "Reinforcement_BarBendingSchedule",
    "Reinforcement_DrawingDimensioning",
]
