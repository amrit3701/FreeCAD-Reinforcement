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

__title__ = "Reinforcement Workbench"
__author__ = "Suraj"
__url__ = "https://www.freecadweb.org"


from pathlib import Path
import FreeCADGui
import RebarTools

wb_icon_path = str(
    Path(RebarTools.__file__).parent.absolute() / "icons" / "Reinforcement.svg"
)


class ReinforcementWorkbench(FreeCADGui.Workbench):
    global wb_icon_path
    MenuText = "Reinforcement"
    ToolTip = "Create Building Reinforcement"
    Icon = wb_icon_path

    def Initialize(self):
        """This function is executed when FreeCAD starts"""
        import RebarTools

        self.rebar_commands = RebarTools.RebarCommands
        self.appendToolbar("RebarCommands", self.rebar_commands)

    def Activated(self):
        """This function is executed when the workbench is activated"""
        return

    def Deactivated(self):
        """This function is executed when the workbench is deactivated"""
        return

    def ContextMenu(self, recipient):
        """This is executed whenever the user right-clicks on screen"""
        # "recipient" will be either "view" or "tree"
        self.appendContextMenu("RebarCommands", self.rebar_commands)

    def GetClassName(self):
        # this function is mandatory if this is a full python workbench
        return "Gui::PythonWorkbench"


FreeCADGui.addWorkbench(ReinforcementWorkbench())
